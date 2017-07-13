"""

    Specialized classes for assets. Anything that can be represented by a symbol.
    Overrides the == to make it easier
    Use asset_factory() if you don't know if an object is a string or an asset
    Logic within the asset classes is kept to a minimum to make it easier
      to learn from the code. Most is in /paperbroker/logic/

"""
import arrow


def asset_factory(symbol=None):
    """
        Create the appropriate asset based on the symbol.
    :param symbol: Case-insensitive symbol for the asset being created
    :return: An object that's a subclass of Asset or None
    """

    if symbol is None:
        return None

    if isinstance(symbol, Asset):
        return symbol

    symbol = symbol.upper()

    if len(symbol) > 8:
        if 'P0' in symbol:
            return Put(symbol)
        elif 'C0' in symbol:
            return Call(symbol)
        else:
            return Option(symbol)
    else:
        return Asset(symbol)

"""
Asset: Assets are always identified by a symbol which uniquely identifies the asset and a type.
"""
class Asset():

    def __init__(self, symbol: str=None, asset_type: str=None):
        self.symbol = symbol.upper()
        self.asset_type = asset_type
        return

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.symbol == other.symbol
        if isinstance(other, str):
            return self.symbol == other.upper()
        return False

    def __ne__(self, other):
        """Define a non-equality test"""
        return not self.__eq__(other)



"""
    Base class for any option derivative
"""
class Option(Asset):

    def __init__(self, symbol:str = None, underlying=None, option_type:str = None, strike:float = None, expiration_date = None):

        if symbol is not None:

            # if a symbol is provided, then we create the asset based on the symbol

            r = symbol[::-1]

            self.strike = float(r[0:8][::-1]) / 1000
            self.option_type = 'call' if r[8] == 'C' else 'put'
            self.expiration_date = arrow.get(r[9:15][::-1], 'YYMMDD').format('YYYY-MM-DD')
            self.underlying = asset_factory(r[15:][::-1])

        else:

            # if not then we piece it together with the data we have

            underlying = asset_factory(underlying)

            if underlying is None:
                raise Exception('Option(Asset): An underlying is required')

            if option_type is None or option_type not in ['call', 'put']:
                raise Exception('Option(Asset): option_type is required and must be `call` or `put`')

            if strike is None or strike <= 0.0:
                raise Exception('Option(Asset): strike is required and must be > 0.0')

            if expiration_date is None:
                raise Exception('Option(Asset): expiration_date is required')

            # parse the date real quick to check on it
            try:
                expiration_date = arrow.get(expiration_date).format('YYMMDD')
            except Exception as e:
                raise Exception('Option(Asset): expiration_date is invalid')

            # build the symbol
            symbol = (underlying.symbol + expiration_date + option_type[0] + str(int(round(strike, 2) * 1000)).zfill(8)).upper()

            self.underlying = underlying
            self.option_type = option_type
            self.strike = float(strike)
            self.expiration_date = arrow.get(expiration_date, 'YYMMDD').format('YYYY-MM-DD')

        super(Option, self).__init__(symbol, self.option_type)

    def get_extrinsic_value(self, underlying_price=None, price=None):
        return (abs(price) - self.get_intrinsic_value(underlying_price=underlying_price)) if price is not None else None

    def get_intrinsic_value(self, underlying_price=None):

        if self.strike is None:
            return None

        if underlying_price is None:
            return None

        if self.option_type == 'call':
            return max(underlying_price - self.strike, 0)
        if self.option_type == 'put':
            return max(self.strike - underlying_price, 0)

        return None



class Put(Option):
    def __init__(self, symbol: str = None, underlying = None,
                 underlying_symbol: str = None, strike: float = None, expiration_date=None):
        super(Put, self).__init__(symbol=symbol, option_type='put', underlying = underlying, strike=strike, expiration_date=expiration_date)

class Call(Option):
    def __init__(self, symbol: str = None, underlying = None,
                 underlying_symbol: str = None, strike: float = None, expiration_date=None):
        super(Call, self).__init__(symbol=symbol, option_type='call', underlying = underlying, strike=strike, expiration_date=expiration_date)

