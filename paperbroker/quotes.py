import arrow
from .assets import asset_factory, Option

def quote_factory(quote_date, asset, price = None, estimator=None):
    asset = asset_factory(asset)
    if isinstance(asset, Option):
        return OptionQuote(quote_date, asset, price, estimator)
    else:
        return Quote(quote_date, asset, price, estimator)


class Quote(object):

    def __init__(self, quote_date, asset, price = None, estimator=None):
        self.estimator = estimator
        self.asset = asset_factory(asset)
        self.quote_date = quote_date
        self.bid = None
        self.ask = None
        self.bid_size = None
        self.ask_size = None
        self.fixed_price = price

    def fix_price(self, price:float=None, estimator=None, quantity=1):
        if price is not None:
            self.fixed_price = float(price)
        self.fixed_price = self.get_price(estimator=estimator, quantity=quantity)

    def is_fixed_price(self):
        return self.fixed_price is not None

    def get_price(self, estimator=None, quantity=1):
        """
            Get the current estimated quote price (if fixed) or generate a new price
        :param estimator: optional if price is fixed, otherwise must have a method with .estimate(quote, quantity)
        :param quantity: optional if price is fixed, passed to .estimate(quote, quantity)
        :return: a float price that the security could expect to trade at based on the quantity
        """

        estimator = estimator or self.estimator

        if self.fixed_price is None:
            if estimator is None:
                raise Exception("Quote.get_price(): `estimator` must have a method with .estimate(quote, quantity)")
            return estimator.estimate(self, quantity)

        return self.fixed_price

    def is_priceable(self, estimator=None, quantity=1):
        """
            Shortcut to determine if the price is possible or not
        :param estimator:
        :param quantity:
        :return:
        """
        if self.fixed_price is not None: return True
        try:
            return self.get_price(estimator, quantity) is not None
        except Exception as e:
            return False




class OptionQuote(Quote):
    def __init__(self, quote_date, asset, price = None, estimator=None):
        super(OptionQuote, self).__init__(quote_date, asset, price, estimator)
        if not isinstance(self.asset, Option):
            raise Exception("OptionQuote(Quote): Must pass an option to create an option quote");
        self.quote_type = 'option'
        self.delta = None
        self.iv = None
        self.gamma = None
        self.vega = None
        self.theta = None
        self.intrinsic_value = None
        self.extrinsic_value = None
        self.days_to_expiration = (arrow.get(quote_date) - arrow.get(asset.expiration_date)).days



