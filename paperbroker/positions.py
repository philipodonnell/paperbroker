"""

    Objects representing positions. Simple right now.

"""

from .quotes import Quote
from .assets import asset_factory


class Position(object):
    """
    A Position represents an asset that you are long/short. Each Position object can
    represent one or more quantities of the asset along with a common cost basis

    Positions can also have an associated quote, which gives it the ability to calculate
    more things
    """
    def __init__(self, asset, quantity: int, cost_basis: float=0.0, quote:Quote=None):
        self.asset = asset_factory(asset)
        self.quantity = quantity
        self.cost_basis = cost_basis
        self.quote = quote



