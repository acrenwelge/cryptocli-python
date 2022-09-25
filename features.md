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
* published to PyPi for installation via `pipx`

## Future Ideas
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
