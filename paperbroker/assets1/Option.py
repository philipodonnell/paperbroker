import arrow
from .Asset import Asset
from . import asset_factory

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


