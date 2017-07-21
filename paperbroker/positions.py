"""

    Objects representing positions. Simple right now.

"""

from .quotes import Quote
from .assets import asset_factory, Option
from math import copysign

class Position(object):
    """
    A Position represents an asset that you are long/short. Each Position object can
    represent one or more quantities of the asset along with a common cost basis

    Positions can also have an associated quote, which gives it the ability to calculate
    more things.

    The functions with 'total' in their name mean that the result will be in total dollar amounts taking
    into account the multiplier (100 for optiosn, 1 for equities), the quantity, and the cost basis,
    so not in per asset amounts but in total dollar impact to cash.
    """

    def __init__(self, asset, quantity: int, cost_basis: float=0.0, quote=None, position_id=None, open_date=None):
        self.id = position_id or ('position' + str(id(self)))
        self.open_date = open_date
        self.asset = asset_factory(asset)
        self.quantity = quantity
        self.cost_basis = cost_basis
        self.quote = quote
        self.multiplier = 100 if isinstance(self.asset, Option) else 1

    @property
    def total_cost_basis(self):
        """
        :return: The total $ cost basis of the position
        """
        return (self.cost_basis * abs(self.quantity)) * self.multiplier

    @property
    def total_close_cost(self):
        """
        :return: The cost to liquidate the position. Negative means you gain by liquidating
        """
        if self.quote is not None and self.quote.is_priceable():
            return self.quote.price * self.quantity * self.multiplier * -1
        else:
            return 0.0

    @property
    def close_cost(self):
        """
        :return: The cost to liquidate the position. Negative means you gain by liquidating
        """
        if self.quote is not None and self.quote.is_priceable():
            return self.quote.price * copysign(1, self.quantity) * -1
        else:
            return 0.0

    @property
    def total_profit(self):
        """
        :return: The total $ profit you have unrealized in this position. Positive means you have profits, negative is losses
        """
        return self.total_close_cost - self.total_cost_basis


    @property
    def profit(self):
        """
        :return: The total $ profit you have unrealized in this position. Positive means you have profits, negative is losses
        """
        return self.close_cost - self.cost_basis

    @property
    def strike(self): return self.asset.strike if isinstance(self.asset, Option) else None

    @property
    def expiration_date(self): return self.asset.expiration_date if isinstance(self.asset, Option) else None

    @property
    def underlying(self): return self.asset.underlying if isinstance(self.asset, Option) else None

    @property
    def option_type(self): return self.asset.option_type if isinstance(self.asset, Option) else None

    @property
    def symbol(self): return self.asset.symbol
    @property
    def asset_type(self): return self.asset.asset_type


    @property
    def delta(self): return (self.quote.delta * self.quantity * self.multiplier) if isinstance(self.asset, Option) else (1 * self.quantity * self.multiplier)
    @property
    def gamma(self): return (self.quote.gamma * self.quantity * self.multiplier) if isinstance(self.asset, Option) else (0.0)
    @property
    def theta(self): return (self.quote.theta * self.quantity * self.multiplier) if isinstance(self.asset, Option) else (0.0)
    @property
    def vega(self): return (self.quote.vega * self.quantity * self.multiplier) if isinstance(self.asset, Option) else (0.0)
    @property
    def rho(self): return (self.quote.rho * self.quantity * self.multiplier) if isinstance(self.asset, Option) else (0.0)
    @property
    def iv(self): return (self.quote.iv * self.quantity * self.multiplier) if isinstance(self.asset, Option) else (0.0)

    @property
    def total_price(self): return (self.quote.price * self.quantity * self.multiplier) if isinstance(self.asset, Option) and self.quote is not None else (0.0)

    @property
    def days_to_expiration(self): return self.quote.days_to_expiration if isinstance(self.asset, Option) and self.quote is not None else None
