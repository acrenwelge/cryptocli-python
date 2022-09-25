import click
from prettytable import PrettyTable
from currency_symbols import CurrencySymbols
import time
from datetime import datetime
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

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