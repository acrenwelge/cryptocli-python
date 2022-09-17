#! /opt/homebrew/bin/python3

import click
import json
import time
from pycoingecko import CoinGeckoAPI
from os.path import expanduser
from datetime import date, datetime
from prettytable import PrettyTable
from currency_symbols import CurrencySymbols

crypto_dir = expanduser("~") + "/.crypto"
config_file_path = crypto_dir + "/defaults.json"
settings = {}
# load configuration settings
try:
  with open(config_file_path) as f:
    settings = json.load(f)
except FileNotFoundError:
  click.echo("Config file not found... creating one now at {fp}".format(fp=config_file_path))
  with open(config_file_path,'w') as f:
    f.write("{}") # empty configuration initialization

cg = CoinGeckoAPI()

def get_resources(resource: str) -> list:
  """retrieve one of the following from cache:
  - list of supported coins
  - list of supported currencies
  if no cache file exists, create one by populating it from the API
  """
  if resource not in ['coins','currencies']:
    raise ValueError('resource must be either "coins" or "currencies"')
  cache_file = crypto_dir + '/'+resource+'.json'
  try:
    with open(cache_file) as resource:
      return json.load(resource)
  except FileNotFoundError:
    click.echo("{} cache file does not exist... creating one at {}".format(resource,cache_file))
    with open(cache_file, 'w') as file:
      if resource == "coins":
        from_api = cg.get_coins_list()
      elif resource == "currencies":
        from_api = cg.get_supported_vs_currencies()
      json.dump(sorted(from_api), file)
      return from_api

# validation callbacks
def validate_coin(ctx,param,value: str) -> str: 
  all_coins = get_resources("coins")
  for coin in all_coins:
    if value == coin['id'] or value == coin['name'] or value == coin['symbol']:
      return coin['id']
  raise click.BadParameter("{} is not a valid cryptocurrency".format(value))

def validate_currency(ctx, param, value: str) -> str:
  all_currencies = get_resources("currencies")
  for currency in all_currencies:
    if value == currency:
      return value
  raise click.BadParameter("{} is not a valid currency denomination".format(value))

@click.group()
@click.pass_context
@click.option("-c","--coin", default=settings['coin'], help="Name of the cryptocurrency", callback=validate_coin)
@click.option("-cur","--currency", default=settings['currency'], help="Name of the currency to denominate the price", callback=validate_currency)
def main(ctx, coin, currency) -> None:
  """Invoked on every command. Assigns either user supplied or default values to global context object that other commands can reference.
  """
  ctx.obj['coin'] = coin
  ctx.obj['currency'] = currency

@click.command(name="price")
@click.pass_context
@click.option("-w","--watch/--no-watch", default=False, help="Watch the price")
@click.option("-i","--interval", default=15, help="Watch interval in seconds", show_default=True)
@click.option("-s","--stop", type=int, help="Stop the program after specified minutes")
def get_price(ctx, watch: bool, interval: int, stop: int) -> None:
  """Retrieves the current price for a given coin, with options to watch at a specified interval and stop after a time.
  """
  coin = ctx.obj['coin']
  curr = ctx.obj['currency']
  if 60 / interval > 50:
    print("WARNING: your rate of API calls will exceed the limit of 50 per minute")
  num_loops = 0
  if (watch):
    click.echo('DATE / TIME' + ' '*13 + 'Price ('+curr+')')
    click.echo('-' * 40)
    while True:
      num_loops += 1
      price = cg.get_price(ids=coin, vs_currencies=curr)[coin][curr]
      click.echo(datetime.now().strftime('%d-%m-%Y %H:%M:%S') + (' '*5) + CurrencySymbols.get_symbol(curr) + str(price))
      if (stop is not None and interval * num_loops >= stop * 60):
        break
      time.sleep(interval)
  else:
    table = PrettyTable()
    table.field_names = ['Coin','Price ('+curr+')']
    obj = cg.get_price(ids=coin,vs_currencies=curr)
    price = CurrencySymbols.get_symbol(curr) + str(obj[coin][curr])
    table.add_row([coin, price])
    click.echo(table)

@click.command
@click.pass_context
def info(ctx) -> None:
  """Retrieve basic information on a cryptocurrency
  """
  coin = cg.get_coin_by_id(id=ctx.obj['coin'])
  table = PrettyTable()
  table.header = False
  # print(coin['market_data'].keys())
  table.add_row(['ID',coin['id']])
  table.add_row(['Name',coin['name']])
  table.add_row(['Symbol',coin['symbol']])
  table.add_row(['Hash algorithm',coin['hashing_algorithm']])
  table.add_row(['Genesis date',coin['genesis_date']])
  table.add_row(['Current price',CurrencySymbols.get_symbol(ctx.obj['currency'])+str(coin['market_data']['current_price'][ctx.obj['currency']])])
  table.add_row(['Max supply',coin['market_data']['max_supply']])
  table.add_row(['Circulating supply', coin['market_data']['circulating_supply']])
  table.add_row(['Market Cap', coin['market_data']['market_cap']['usd']])
  table.add_row(['Market Cap Rank', coin['market_data']['market_cap_rank']])
  click.echo(table)
  click.echo("\n" + "DESCRIPTION: " + coin['description']['en'])

@click.command
@click.argument('search_string')
def search(search_string: str) -> None:
  """Search for cryptocurrencies that match a particular string"""
  coin_list = get_resources("coins")
  coins_found = []
  table = PrettyTable()
  table.field_names = ["ID","Symbol","Name"]
  for coin in coin_list:
    if search_string in coin['id'] or search_string in coin['symbol'] or search_string in coin['name']:
        coins_found.append(coin)
  if len(coins_found) == 0:
    click.echo('Sorry, no cryptocurrencies or tokens found matching that string :(')
  else:
    for coin in coins_found:
      table.add_row([coin['id'],coin['symbol'],coin['name']])
    click.echo(table)

@click.command
@click.option("--currency-default", help="Set default currency to denominate prices (ISO 4217 code)")
@click.option("--coin-default", help="Set default cryptocurrency coin to use")
def config(currency_default: str, coin_default: str) -> None:
  """View default configuration or change configuration settings
  """
  if currency_default is None and coin_default is None:
    click.echo("No new configurations set - existing config is:")
    table = PrettyTable()
    table.header = False
    table.align = 'l'
    for field in settings.keys():
      table.add_row([field, settings[field]])
    click.echo(table)
  if currency_default is not None:
    all_currencies = get_resources('currencies')
    if currency_default not in all_currencies:
      raise click.BadParameter(currency_default + ' is not a valid currency')
    else:
      settings['currency'] = currency_default
      click.echo('Setting currency to {val}'.format(val=currency_default))
  if coin_default is not None:
    all_coins = get_resources('coins')
    found = False
    for coin in all_coins:
      if coin_default == coin['id'] or coin_default == coin['name'] or coin_default == coin['symbol']:
        settings['coin'] = coin['id'] # store the ID of the coin for use in the API, although name or symbol should also work
        click.echo('Setting coin to {val}'.format(val=coin_default))
        found = True
        break
    if not found:
      raise click.BadParameter(coin_default + ' is not a valid coin')
      
  with open(config_file_path,'w') as f:
    json.dump(settings, f)

@click.command
@click.pass_context
@click.option("--find-date", help="Date of price to lookup in format: dd-mm-yyyy")
@click.option("--days", help="Number of days of history to lookup")
def history(ctx,find_date,days) -> None:
  """Look up the price of a coin on particular date or throughout the past n days"""
  table = PrettyTable()
  table.field_names = ["Date", "Price"]
  if find_date is not None:
    data = cg.get_coin_history_by_id(ctx.obj['coin'],find_date)
    table.add_row([find_date,round(data['market_data']['current_price'][ctx.obj['currency']],2)])
  if days is not None:
    data = cg.get_coin_market_chart_by_id(ctx.obj['coin'],ctx.obj['currency'],days)
    for row in data['prices']:
      formatted_date = datetime.utcfromtimestamp(row[0]/1000).strftime("%Y-%m-%d %H:%M")
      table.add_row([formatted_date, round(row[1],2)])
  click.echo(table)

@click.group
def list():
  """View a list of supported fiat and cryptocurrencies"""
  # this is a dummy command - coins and currencies are sub-commands
  pass

@click.command
def coins():
  """View a list of supported cryptocurrencies"""
  all_coins = get_resources("coins")
  table = PrettyTable()
  table.field_names = ['ID','Symbol',"Name"]
  # table.add_rows(all_coins)
  for coin in all_coins:
    table.add_row([coin['id'],coin['symbol'],coin['name']])
  click.echo(table)

@click.command
def currencies():
  """View a list of supported currencies to denominate prices in"""
  all_currencies = get_resources("currencies")
  table = PrettyTable()
  table.add_column('Currency',all_currencies)
  click.echo(table)

@click.command
@click.pass_context
@click.option("-sd","--start-date",type=click.DateTime(),required=True)
@click.option("-ed","--end-date",type=click.DateTime(),default=datetime.today())
def gains(ctx, start_date: date, end_date: date):
  """Print the price gain (or loss) between start_date and end_date.
  Both dates must be in ISO format (yyyy-mm-dd).
  If no end date is given, today's date is assumed
  """
  if end_date < start_date:
    raise click.BadParameter('Start date must come before end date')
  if end_date > datetime.today() or start_date > datetime.today():
    raise click.BadParameter('Dates cannot be in the future')
  start_data = cg.get_coin_history_by_id(ctx.obj['coin'],start_date.strftime('%d-%m-%Y'))
  start_price = start_data['market_data']['current_price'][ctx.obj['currency']]
  end_data = cg.get_coin_history_by_id(ctx.obj['coin'],end_date.strftime('%d-%m-%Y'))
  end_price = end_data['market_data']['current_price'][ctx.obj['currency']]
  percent_change = (end_price - start_price) / start_price * 100
  word = 'increased' if percent_change > 0 else 'decreased'
  click.echo("{coin} {txt} by {num:.2f}% from {sym}{begin:,.2f} to {sym}{end:,.2f}"
    .format(coin=ctx.obj['coin'],txt=word,sym=CurrencySymbols.get_symbol(ctx.obj['currency']),
    num=percent_change,begin=start_price,end=end_price))

main.add_command(get_price)
main.add_command(info)
main.add_command(search)
main.add_command(config)
list.add_command(coins)
list.add_command(currencies)
main.add_command(list)
main.add_command(history)
main.add_command(gains)

if __name__ == '__main__':
  main(obj={})