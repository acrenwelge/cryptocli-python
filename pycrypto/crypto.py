#! /opt/homebrew/bin/python3

import click
import json
from pycoingecko import CoinGeckoAPI
from datetime import date, datetime
from prettytable import PrettyTable
from currency_symbols import CurrencySymbols

# project imports
from . import util
from . import price
from . import info

# init
settings = util.load_config_settings()
cg = CoinGeckoAPI()

# validation callbacks
def validate_coin(ctx,param,value: str) -> str: 
  all_coins = util.get_resources("coins")
  for coin in all_coins:
    if value == coin['id'] or value == coin['name'] or value == coin['symbol']:
      return coin['id']
  raise click.BadParameter("{} is not a valid cryptocurrency".format(value))

def validate_currency(ctx, param, value: str) -> str:
  all_currencies = util.get_resources("currencies")
  for currency in all_currencies:
    if value == currency:
      return value
  raise click.BadParameter("{} is not a valid currency denomination".format(value))

# main function - entrypoint
@click.group()
@click.pass_context
@click.option("-c","--coin", default=settings['coin'], help="Name of the cryptocurrency", callback=validate_coin)
@click.option("-cur","--currency", default=settings['currency'], help="Name of the currency to denominate the price", callback=validate_currency)
def main(ctx, coin, currency) -> None:
  """Invoked on every command. Assigns either user supplied or default values to global context object that other commands can reference.
  """
  ctx.obj = {}
  ctx.obj['coin'] = coin
  ctx.obj['currency'] = currency

@click.command
@click.argument('search_string')
def search(search_string: str) -> None:
  """Search for cryptocurrencies that match a particular string"""
  coin_list = util.get_resources("coins")
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
  all_coins = util.get_resources("coins")
  table = PrettyTable()
  table.field_names = ['ID','Symbol',"Name"]
  # table.add_rows(all_coins)
  for coin in all_coins:
    table.add_row([coin['id'],coin['symbol'],coin['name']])
  click.echo(table)

@click.command
def currencies():
  """View a list of supported currencies to denominate prices in"""
  all_currencies = util.get_resources("currencies")
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

main.add_command(price.get_price)
main.add_command(info.get_info)
main.add_command(search)
main.add_command(util.config)
list.add_command(coins)
list.add_command(currencies)
main.add_command(list)
main.add_command(history)
main.add_command(gains)