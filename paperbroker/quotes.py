import arrow
from .assets import asset_factory, Option

def quote_factory(quote_date, asset, price = None, estimator=None):
    asset = asset_factory(asset)
    if isinstance(asset, Option):
        return OptionQuote(quote_date, asset, price, estimator)
    else:
        return Quote(quote_date, asset, price, estimator)


class Quote(object):

    def __init__(self, quote_date, asset, price=None, bid=0.0, ask=0.0, bid_size=0, ask_size=0):
        self.asset = asset_factory(asset)
        self.quote_date = quote_date
        self.bid = 0.0
        self.ask = 0.0
        self.bid_size = 0
        self.ask_size = None
        self.price = price

        if self.price is None and bid + ask != 0.0:
            self.price = ((bid + ask) / 2)

    def is_priceable(self, estimator=None, quantity=1):
        return self.price is not None





class OptionQuote(Quote):
    def __init__(self, quote_date, asset, price=None, bid=0.0, ask=0.0, bid_size=0, ask_size=0, delta=None, iv=None, gamma=None, vega=None, theta=None):
        super(OptionQuote, self).__init__(quote_date=quote_date, asset=asset, price=price, bid=bid, ask=ask, bid_size=bid_size, ask_size=ask_size)
        if not isinstance(self.asset, Option):
            raise Exception("OptionQuote(Quote): Must pass an option to create an option quote");
        self.quote_type = 'option'
        self.delta = delta
        self.iv = iv
        self.gamma = gamma
        self.vega = vega
        self.theta = theta
        self.days_to_expiration = (arrow.get(quote_date) - arrow.get(asset.expiration_date)).days

    def get_intrinsic_value(self, underlying_price = None):
        return self.asset.get_intrinsic_value(underlying_price=underlying_price)

    def get_extrinsic_value(self, underlying_price=None):
        return self.asset.get_extrinsic_value(underlying_price=underlying_price, price=self.price)


