from copy import deepcopy, copy

from .assets import *
from .quotes import Quote

class PositionGroup(object):

    """
        A position group represents a set of positions that you would like to treat as a distinct set
    """

    def __init__(self, positions=None):
        positions = positions or []
        self._positions = positions if isinstance(positions, list) else [positions]
        self._positions_index = 0

    def __iter__(self, positions):
        return self

    def __next__(self):

        try:
            result = self._positions[self._positions_index]
        except IndexError:
            self._positions_index = 0
            raise StopIteration

        self._positions_index += 1
        return result

    def append(self, positions):
        return PositionGroup(copy(self._positions) + (positions if isinstance(positions, list) else [positions]))

    def get_total_profit(self):
        return self.get_total_price() - self.get_total_cost_basis()

    def get_total_price(self):

        total_price = 0.0

        for position in self._positions:

            if position.quote is None:
                raise Exception("PositionGroup.get_total_price: A quote is required.")

            if isinstance(position.asset, Option):
                total_price += position.quote.price * position.quantity * 100
            else:
                total_price += position.quote.price * position.quantity * 1

        return total_price

    def get_total_cost_basis(self):

        total_cost_basis = 0.0

        for position in self._positions:

            if isinstance(position.asset, Option):
                total_cost_basis += position.cost_basis * abs(position.quantity) * 100
            else:
                total_cost_basis += position.cost_basis * abs(position.quantity) * 1

        return total_cost_basis






class Position(object):
    """
    A Position represents an asset that you are long/short. Each Position object can
    represent one or more quantities of the asset along with a common cost basis

    Positions can also have an associated quote, which gives it the ability to calculate
    more things
    """
    def __init__(self, asset: Asset, quantity: int, cost_basis: float=0.0, quote:Quote=None):
        self.asset = asset
        self.quantity = quantity
        self.cost_basis = cost_basis
        self.quote = quote



