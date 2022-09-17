## Completed Features

* using coingecko Python SDK
* help list of crypto + currencies
* add default and fallback values
* print currency symbol with prices
* Performance
  * Calculate % increase/decrease from one day to another
    * Example: `crypto gains -c bitcoin 2020-01-01 2021-01-01`
  * Compare performance of one coin to another
    * Example: `crypto gains -c bitcoin -c ethereum 2020-01-01 2021-01-01`

## Future Ideas
```bash
crypto history -c bitcoin -d 10 # past 10 days of bitcoin price
crypto history -c bitcoin -d 10 --graph # add a graph
crypto history -c bitcoin -w 5 # past 5 weeks of bitcoin price
crypto history -c bitcoin -m 3 # past 3 months of bitcoin price```
```

* Multi-coin, multi-currency command support
* Visualization
  * Graph for historical data
  * Example: `crypto history -d 1 -c bitcoin --graph`
* add TTL config for caching
* add argument validation tests

v1.3
* Track historical prices on a monthly basis (e.g. Jan 1, Feb 1, Mar 1)

v1.5
* Statistical modelling
  * TBD

v2.0
* Trading bot
  * Command to "buy" or "sell" at current time
  * Track gains/losses
