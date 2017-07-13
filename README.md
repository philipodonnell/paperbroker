# paperbroker
A python3 open source simulated brokerage for paper trading, algorithms and backtesting. Trade stocks, bonds, options and many other securities via adapters.

## Features
When I was learning to trade options I needed a free API-driven broker simulation that understood options so that I could paper trade my strategies. I built `paperbroker` to meet that need and I hope it will help you too.

- Specialized classes for different kinds of assets (including option greeks)
- Brokerage business logic in dedicated modules
- Automatically handles option expirations
- Interchangable, extensible, transaction pricing estimators
- 4 days of real option pricing data included for development and testing

Contributors and contributions are welcome! My hope is that this codebase will grow beyond my original use case to help many more people learn about options trading and investment. More is coming very soon, including commission handling, additional data sources, and a free hosted version to expermient with. If you are interested in contributing, please contact me on reddit @ /u/philipwithpostral or open an issue with suggestions or corrections.

This is a work in progress and under active development. It is not suited for production use. USE AT YOUR OWN RISK! If you find bugs, please open an issue!

## Goals
- Provide a complete reference implementation for the essential functions of a small retail-facing brokerage operation.
- Enable algorithm developers and novice traders a complete brokerage-in-a-box experience without risking any capital.
- Educate and inform newcomers about how a brokerage operation works, manages positions, fills orders and calculates margins.

## Installing paperbroker
Install paperbroker directly from git
```
pip install git+https://github.com/philipodonnell#egg=paperbroker
```

## Usage

```python

from paperbroker import PaperBroker

# Creating a PaperBroker defaults to:
# - uses the local filesystem temp folder to store acounts
# - quotes from Google Finance (equities only)
# - estimates all transaction prices at the midpoint
# - you can change any of these by writing your own adapters, see paperbroker/adapters
broker = PaperBroker()

# This is how we get basic quotes, we can get any quotes supported by GoogleFinance
quote = broker.get_quote('GOOG')

print(quote.price)
# >> 988.8

# Lets get the expiration dates that GoogleFinance has for GOOG
expiration_dates = broker.get_expiration_dates('GOOG')



```


## Credits
Special thanks to the folks at https://www.reddit.com/r/options

