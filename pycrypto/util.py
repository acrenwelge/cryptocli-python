import json
import click
from os.path import expanduser
from pycoingecko import CoinGeckoAPI
from prettytable import PrettyTable
cg = CoinGeckoAPI()

crypto_dir = expanduser("~") + "/.crypto"
config_file_path = crypto_dir + "/defaults.json"
settings = {"coin": "btc", "currency": "usd"} #fallback values

def load_config_settings():
  try:
    with open(config_file_path) as f:
      global settings
      settings = json.load(f)
  except FileNotFoundError:
    click.echo("Config file not found... creating one now at {fp}".format(fp=config_file_path))
    with open(config_file_path,'w') as f:
      json.dump(settings, f) # store current config
  return settings

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