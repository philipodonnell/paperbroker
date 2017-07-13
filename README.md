# paperbroker
A python3 open source simulated brokerage for paper trading, algorithms and backtesting. Trade stocks, bonds, options and many other securities via adapters.

## Features
When I was learning to trade options I needed a free API-driven broker simulation that understood options so that I could paper trade my strategies. I built `paperbroker` to meet that need and I hope it will help you too.

- Specialized classes for different kinds of assets (including option greeks)
- Brokerage business logic in dedicated modules
- Automatically handles option expirations
- Interchangable, extensible, transaction pricing estimators
- 4 days of real option pricing data included for development and testing

Contributors and contributions are welcome! My hope is that this codebase will grow beyond my original use case to help many more people learn about options trading and investment. More is coming very soon, including:

- Margins on naked calls and puts (help!)
- Commission handling
- Additional data sources
- Built-in paper trading UI
- Free hosted version to expermient with

If you are interested in contributing, please contact me on reddit @ /u/philipwithpostral or open an issue with suggestions or corrections.

This is a work in progress and under active development. It is not suited for production use. USE AT YOUR OWN RISK! If you find bugs, please open an issue!

## Goals
- Provide a complete reference implementation for the essential functions of a small retail-facing brokerage operation.
- Enable algorithm developers and novice traders a complete brokerage-in-a-box experience without risking any capital.
- Educate and inform newcomers about how a brokerage operation works, manages positions, fills orders and calculates margins.

## Installing paperbroker
Install paperbroker directly from git. I recommend and test on windows 10 and ubuntu.
```
pip install git+https://github.com/philipodonnell#egg=paperbroker
```

## Usage Examples

```python
from paperbroker import PaperBroker
from paperbroker.orders import Order


# Creating a PaperBroker defaults to:
# - uses the local filesystem temp folder to store acounts
# - quotes from Google Finance (equities only)
# - estimates all transaction prices at the midpoint
# - you can change any of these by writing your own adapters, see paperbroker/adapters
broker = PaperBroker()

# Create an account so we can buy stuff
account = broker.open_account()
account.cash = 100000 # give ourselves some cash!!

# This is how we get basic quotes
# We can get any quotes supported by GoogleFinance
quote = broker.get_quote('GOOG')
print(quote.price)
# >> 943.83

# Get the expiration dates that GoogleFinance has for GOOG
expiration_dates = broker.get_expiration_dates('GOOG')
print(expiration_dates)
# >> ['2018-01-19']

# Get all of the options that we have for the next chain
quotes = broker.get_options('GOOG', expiration_dates[0])
print(len(quotes), quotes)
# >> 118 [<paperbroker.quotes.OptionQuote object at 0x0000008C13F41FD0>, ..]

# Get the 50 delta call implied volatility and strike
call_quotes = [q for q in quotes if q.asset.option_type == 'call' and q.has_greeks()]
fifty_delta_call_quote = sorted(call_quotes, key=lambda q:abs(0.5 - abs(q.delta)))[0]
print(fifty_delta_call_quote.asset.symbol, fifty_delta_call_quote.bid, fifty_delta_call_quote.ask, fifty_delta_call_quote.asset.strike, fifty_delta_call_quote.iv)
# >> GOOG180119C00960000 51.0 52.6 960.0 0.20861707425282885

# Create a market order to buy-to-open this option
# straightforward orders have shortcuts
broker.buy_to_open(account=account, asset=fifty_delta_call_quote.asset, quantity=1)
print(account.cash, account.maintenance_margin, len(account.positions))
# >> 94820.0 0.0 1

# while we're here, lets also sell an ATM call on the same expiration and buy some stock for a covered call
atm_call_quote = sorted(call_quotes, key=lambda q:abs(quote.price - q.asset.strike))[0]
print(atm_call_quote.asset.symbol, atm_call_quote.bid, atm_call_quote.ask, atm_call_quote.asset.strike, atm_call_quote.iv)
# >> GOOG180119C00940000 61.1 63.0 940.0 0.21215993354358822

# covered calls require custom orders (for now, help at /paperbroker/orders.py)
covered_call_order = Order()
covered_call_order.add_leg(asset='GOOG', quantity=100, order_type='bto')
covered_call_order.add_leg(asset=atm_call_quote.asset.symbol, quantity=-1, order_type='sto')

# simulation is not required, but its recommended to see what state you'll be in afterwards
# for more complex orders
simulated_account = broker.simulate_order(account, covered_call_order)
print(account.cash, account.maintenance_margin, len(account.positions))
# >> 94820.0 0.0 1

# enter the covered call order
broker.enter_order(account, covered_call_order)
print(account.cash, account.maintenance_margin, len(account.positions))
# >> 6642.0 0.0 3

# now imagine a little time has passed and we need some cash. That covered call is holding a lot of capital!
# let sell the stock part
# notice afterwards that our cash is higher but out maintenance margin has increased by a few thousand dollars
# this is because the short call was covered by the stock so it had no margin requirement
# we sold the stock so now its covered by the ATM long call and treated as a vertical spread
broker.sell_to_close(account, 'GOOG', -100)
print(account.cash, account.maintenance_margin, len(account.positions))
# >> 101025.0 2000.0 2

# Lets sell the atm long call as well
# we'll need to find it in the position list
long_call_position = [_ for _ in account.positions if _.asset == fifty_delta_call_quote.asset][0]

# there is a shortcut to close existing positions by passing them to the broker directly
# the maintenance margin is null because we don't have an implementation for naked call margin yet
# check out paperbroker/logic/maintenance_margin.py if you can help
broker.close_position(account, long_call_position)
print(account.cash, account.maintenance_margin, len(account.positions))
# >> 106205.0 None 1


# and finally liquidate everything and back to normal
broker.close_positions(account, account.positions)
print(account.cash, account.maintenance_margin, len(account.positions))
# >> 100000.0 0.0 0

```


## Credits
Special thanks to the folks at https://www.reddit.com/r/options

