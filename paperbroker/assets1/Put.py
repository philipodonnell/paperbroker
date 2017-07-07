from .Option import Option

class Put(Option):
    def __init__(self, symbol: str = None, underlying = None,
                 underlying_symbol: str = None, strike: float = None, expiration_date=None):
        super(Put, self).__init__(symbol=symbol, option_type='put', underlying = underlying, strike=strike, expiration_date=expiration_date)

