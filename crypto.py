#! /opt/homebrew/bin/python3

from gc import callbacks
import click
import json
import time
from locale import currency
from pycoingecko import CoinGeckoAPI
from os.path import exists, expanduser
from datetime import date, datetime

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

# retrieve one of the following from cache:
# - list of coins
# - list of currencies
# if no cache file exists, create one by populating it from the API
def get_resources(resource):
  if resource != 'coins' and resource != 'currencies':
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

def validate_coin(ctx,param,value):
  all_coins = get_resources("coins")
  for coin in all_coins:
    if value == coin['id'] or value == coin['name'] or value == coin['symbol']:
      return coin['id']
  raise click.BadParameter("{} is not a valid cryptocurrency".format(value))

def validate_currency(ctx, param, value):
  all_currencies = get_resources("currencies")
  for currency in all_currencies:
    if value == currency:
      return value
  raise click.BadParameter("{} is not a valid currency denomination".format(value))

@click.group()
@click.pass_context
@click.option("--coin", default='bitcoin', help="Name of the cryptocurrency", callback=validate_coin)
@click.option("--currency", default='usd', help="Name of the currency to denominate the price", callback=validate_currency)
def main(ctx, coin, currency):
    ctx.obj['coin'] = coin
    ctx.obj['currency'] = currency

@click.command(name="price")
@click.pass_context
@click.option("--watch/--no-watch", default=False, help="Watch the price")
@click.option("--interval", default=15, help="Watch interval in seconds", show_default=True)
@click.option("--stop", type=int, help="Stop the program after specified minutes")
def get_price(ctx, watch, interval, stop):
  num_loops = 0
  if (watch):
    while True:
      num_loops += 1
      click.echo(cg.get_price(ids=ctx.obj['coin'],vs_currencies=ctx.obj['currency']))
      if (stop is not None and interval * num_loops >= stop * 60):
        break
      time.sleep(interval)
  else:
    click.echo(cg.get_price(ids=ctx.obj['coin'],vs_currencies=ctx.obj['currency']))

@click.command(name="info")
@click.pass_context
def info(ctx):
  click.echo(cg.get_coin_by_id(id=ctx.obj['coin']))

@click.command
@click.argument('look_for')
def search(look_for):
  coin_list = get_resources("coins")
  coins_found = []
  for coin in coin_list:
    if look_for in coin['id'] or look_for in coin['symbol'] or look_for in coin['name']:
        coins_found.append(coin)
  if len(coins_found) == 0:
    click.echo('Sorry, no cryptocurrencies or tokens found matching that string :(')
  else:
    for coin in coins_found:
      click.echo(coin)

@click.command
@click.option("--currency-default",help="Provide the default currency to denominate prices (ISO 4217 code)")
@click.option("--coin-default",help="Provide the default cryptocurrency coin to use")
### TODO: validate set configuration values against coin / currency list
def config(currency_default,coin_default):
  if currency_default is None and coin_default is None:
    click.echo("No new configurations set - existing config is:")
    click.echo(settings)
  if currency_default is not None:
    settings['currency'] = currency_default
    click.echo('Setting currency to {val}'.format(val=currency_default))
  if coin_default is not None:
    settings['coin'] = coin_default
    click.echo('Setting coin to {val}'.format(val=coin_default))
  with open(config_file_path,'w') as f:
    json.dump(settings, f)

@click.command
@click.pass_context
@click.option("--date", help="Date of price to lookup in format: dd-mm-yyyy")
@click.option("--days", help="Number of days of history to lookup")
def history(ctx,date,days):
  if (date is not None):
    click.echo(cg.get_coin_history_by_id(ctx.obj['coin'],date))
  if (days is not None):
    click.echo(cg.get_coin_market_chart_by_id(ctx.obj['coin'],ctx.obj['currency'],days))

@click.group
def list():
  # this is a dummy command - coins and currencies are sub-commands
  pass

@click.command
def coins():
  all_coins = get_resources("coins")
  for coin in all_coins:
    click.echo(coin['id'] + ' - ' + coin['symbol'])

@click.command
def currencies():
  all_currencies = get_resources("currencies")
  for i in range(0,len(all_currencies)):
    click.echo(all_currencies[i])

@click.command
@click.pass_context
@click.argument("start_date")
@click.argument("end_date")
def gains(ctx, start_date, end_date):
  start_data = cg.get_coin_history_by_id(ctx.obj['coin'],start_date)
  start_price = start_data['market_data']['current_price'][ctx.obj['currency']]
  end_data = cg.get_coin_history_by_id(ctx.obj['coin'],end_date)
  end_price = end_data['market_data']['current_price'][ctx.obj['currency']]
  percent_change = (end_price - start_price) / start_price * 100
  word = 'increased' if percent_change > 0 else 'decreased'
  click.echo("{coin} {txt} by {num:.2f}%".format(coin=ctx.obj['coin'],txt=word,num=percent_change))

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