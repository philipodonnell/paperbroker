"""

    Objects representing positions. Simple right now.

"""

from .quotes import Quote
from .assets import asset_factory, Option


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

    def __init__(self, asset, quantity: int, cost_basis: float=0.0, quote:Quote=None):
        self.asset = asset_factory(asset)
        self.quantity = quantity
        self.cost_basis = cost_basis
        self.quote = quote

    def get_total_cost_basis(self):
        """
        :return: The total $ cost basis of the position
        """
        multiplier = 100 if isinstance(self.asset, Option) else 1
        return (self.cost_basis * abs(self.quantity)) * multiplier


    def get_total_liquidation_value(self):
        """
        :return: The total $ effect of liquidating the position. Negative means you gain by liquidating
        """
        if self.quote is not None and self.quote.is_priceable():
            multiplier = 100 if isinstance(self.asset, Option) else 1
            return self.quote.price * self.quantity * multiplier * -1
        else:
            return 0.0

    def get_total_profit(self):
        """
        :return: The total $ profit you have unrealized in this position. Positive means you have profits, negative is losses
        """
        return self.get_total_liquidation_value() - self.get_total_cost_basis()


