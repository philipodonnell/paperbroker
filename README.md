# paperbroker
A python3 open source simulated brokerage for paper trading, algorithms and backtesting. Trade stocks, bonds, options and many other securities via adapters.

## What is paperbroker?
I made paperbroker to help me learn to trade options

## Work In Progress!!
This is a work in progress. Contributions are welcome!

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
broker = PaperBroker()

quote = broker.get_quote('GOOG')

print(quote.price) 
# >> 988.8
```


## Credits
Special thanks to the folks at https://www.reddit.com/r/options

