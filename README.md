# ⚡️ Crypto CLI ⚡️

Ever felt the pressing need to lookup crypto data right from your shell? Now you can!

### Installation
Note: requires Python 3, [pipx](https://pypa.github.io/pipx/) recommended
```bash
pipx install cryptocli
# alias to 'crypto' command
echo "alias crypto=cryptocli" >> ~/.bashrc
source ~/.bashrc
```

### Build from source
Note: [hatch](https://hatch.pypa.io/) is the build tool
```bash
git clone https://github.com/acrenwelge/cryptocli-python.git
python -m build
pipx install dist/*.whl
```

### Usage

> Please note: there is currently a **rate limit of 50 calls / minute** for the free API being used

👀 Search for a crypto
```bash
crypto search bit
```

ℹ️ Lookup info on a cryptocurrency
```bash
crypto --coin bitcoin
```

💰 Get price info only
```bash
crypto price --coin bitcoin
```

💶 Get price info for multiple coins in multiple currencies
```bash
crypto price -c bitcoin -c ethereum -c litecoin -cur USD -cur EUR
```

📈 Get price history by day, week, or month
```bash
crypto history -c bitcoin -d 10 # past 10 days of bitcoin price
crypto history -c bitcoin -d 10 --graph # add a graph
crypto history -c bitcoin -w 5 # past 5 weeks of bitcoin price
crypto history -c bitcoin -m 3 # past 3 months of bitcoin price
```

📖 Get USD price of bitcoin on May 1, 2015
```bash
crypto price -c bitcoin --date 2015-05-01
```

⏱ Watch the price (default: refresh every 15 seconds)
```bash
crypto price -c bitcoin --watch
crypto price -c bitcoin -w -i 10 -s 1 # interval of 10 seconds, stop after 1 minute
```

％ See price gains over time
```bash
crypto gains -c bitcoin 2020-01-01 2021-01-01
```

### Config
The default coin and currency to use will be stored in `$HOME/.crypto/defaults.properties`. If this file exists, these values will be used unless overridden with command line arguments. If no file exists and no command line arguments are provided, the program reverts to bitcoin and USD defaults, respectively.

⚙️ Set default crypto and currency
```bash
crypto config -c bitcoin
crypto config -cur USD
crypto config # displays current defaults if no args set
```
> Crypto coin must be its `id`. Currency must follow [ISO 4217](https://en.wikipedia.org/wiki/ISO_4217) AND be supported by the API used.

📝 List possible coin and currency values
```bash
crypto list coins
crypto list currencies
```

### Caching
A list of coins to search will be cached in `$HOME/.crypto/coins.json` for quick searching and lookup. By default, a [TTL](https://en.wikipedia.org/wiki/Time_to_live) value of 7 days will be used.

### Complex Queries & Examples 🧐
```bash
# find the number of cryptocurrencies with the word "chain" in their name
crypto list coins | grep chain | wc -l

# store the price of bitcoin for the last year
crypto history -c bitcoin -d 365 > btc-prices-last-year.txt
```

### Built with...
* Python 3.9
* [Click](https://click.palletsprojects.com/en/8.1.x/)
* [pycoingecko](https://github.com/man-c/pycoingecko)
* [Coingecko API](https://www.coingecko.com/en/api/documentation?)
* [CurrencySymbols](https://pypi.org/project/currency-symbols/)