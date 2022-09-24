import click
from prettytable import PrettyTable
from pycoingecko import CoinGeckoAPI
from currency_symbols import CurrencySymbols

cg = CoinGeckoAPI()

@click.command
@click.pass_context
def get_info(ctx) -> None:
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