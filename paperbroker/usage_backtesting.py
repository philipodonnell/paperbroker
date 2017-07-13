import paperbroker
from paperbroker import PaperBroker


# Creating a PaperBroker defaults to:
# - uses the local filesystem temp folder to store acounts
# - quotes from Google Finance (equities only)
# - estimates all transaction prices at the midpoint
# - you can change any of these by writing your own adapters, see paperbroker/adapters
broker = PaperBroker()

# Because this is a demo, lets switch over to the test data quote adapter
# The test adapter is pre-loaded with GOOG options prices from 1/27-1/28 2017
# Note the the code is exactly the same as using the default GoogleFinance, except there is no current_date field
# We'll use GOOG's chains as of 2017-01-27, just before the Jan 17 options expirations
from paperbroker.tests.TestDataQuoteAdapter import TestDataQuoteAdapter
broker = PaperBroker(quote_adapter = TestDataQuoteAdapter(current_date='2017-01-27'))

# This is how we get basic quotes
# We can nrmaget any quotes supported by GoogleFinance
quote = broker.get_quote('GOOG')

print(quote.price)
# >> 988.8

# Get the expiration dates that GoogleFinance has for GOOG
expiration_dates = broker.get_expiration_dates('GOOG')
print(expiration_dates)
# >> ['2017-01-27', '2017-02-03', '2017-02-10', ...]

# Get all of the options that we have for the Feb 3, 2017 weeklies
quotes = broker.get_options('GOOG', '2017-02-03')
print(len(quotes), quotes)
# >> [<paperbroker.quotes.OptionQuote object at 0x000000B85006E6A0>,...]

# Get the ATM call implied volatility and delta
call_quotes = [q for q in quotes if q.asset.option_type == 'call']
atm_call_quote = sorted(call_quotes, key=lambda q:abs(quote.price - q.asset.strike))[0]
print(atm_call_quote.asset.symbol, atm_call_quote.bid, atm_call_quote.ask, atm_call_quote.delta, atm_call_quote.iv)
# >> GOOG170203C00830000 7.3 8.2 0.4828381241141011 0.18149839437648937

# Create an account so we can buy this call
account = broker.open_account()
account.cash = 20000 # give ourselves some cash

# Create a market order to buy-to-open this option
from paperbroker.orders import Order
order = Order()
order.add_leg(asset=atm_call_quote.asset, quantity=1, order_type='bto')

# simulation is not required, but its recommended to see what state you'll be in afterwards
simulated_account = broker.simulate_order(account, order)
print(simulated_account.cash, simulated_account.maintenance_margin)

# Enter the order. Note that nothing about the account has changed.
# PaperBroker will not fill orders until you call broker.fill_orders()
broker.enter_order(account, order)
print(account.cash, account.maintenance_margin)

# while we're here, lets also sell one of these on the 1/27 expiration and buy some stock for a covered call
covered_call_order = Order()
covered_call_order.add_leg(asset='GOOG', quantity=100, order_type='bto')
covered_call_order.add_leg(asset='GOOG170127C00830000', quantity=-1, order_type='sto')

# again we'll simulate. Note that both the previous (unfilled) bto call order
# and this order are both considered during the simulation
simulated_account = broker.simulate_order(account, covered_call_order)
print(simulated_account.cash, simulated_account.maintenance_margin)

# and finally enter the covered call order
broker.enter_order(account, covered_call_order)

# force the broker to fill all the outstanding orders
# you will have to do this manually once you have all the orders for a given day entered
broker.fill_orders()
print(account.cash, account.maintenance_margin)

# Since this is a demo, manually roll the date forward
# When using the default GoogleFinance adapter this is unneccessary since
# the quotes are always current
broker.quote_adapter.current_date = '2017-01-28'


