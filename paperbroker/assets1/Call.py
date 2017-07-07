from .Option import Option
class Call(Option):
    def __init__(self, symbol: str = None, underlying = None,
                 underlying_symbol: str = None, strike: float = None, expiration_date=None):
        super(Call, self).__init__(symbol=symbol, option_type='call', underlying = underlying, strike=strike, expiration_date=expiration_date)
