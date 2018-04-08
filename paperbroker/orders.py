"""

    Just a few ordering classes. Again, minimal logic.

"""

from math import copysign
from .assets import Asset, asset_factory
from .quotes import Quote

class Leg(object):
    def __init__(self, asset: Asset, quantity: int, order_type: str, price: float = None):

        # automatically correct the signs of the quantity and price
        if order_type[0] == 's':
            quantity = abs(quantity) * -1
            price = (abs(price) * -1) if price is not None else None
        else:
            quantity = abs(quantity) * 1
            price = (abs(price) * 1) if price is not None else None

        self.asset = asset
        self.quantity = quantity
        self.order_type = order_type
        self.price = price


class Order(object):
    def __init__(self, legs = None, price=None, condition='market'):
        self.legs = legs if legs is not None else []
        self.status = 'open'
        self.price = 0.0
        self.condition = condition

    def duplicate(self, times=1):
        self.price *= times
        for leg in self.legs:
            leg.quantity *= times
        return self

    def buy_to_open(self, asset = None, quantity: int = None, price: float = None):
        return self.add_leg(asset=asset, quantity=quantity, price=price, order_type='bto')
    def sell_to_open(self, asset = None, quantity: int = None, price: float = None):
        return self.add_leg(asset=asset, quantity=quantity, price=price, order_type='sto')
    def buy_to_close(self, asset = None, quantity: int = None, price: float = None):
        return self.add_leg(asset=asset, quantity=quantity, price=price, order_type='btc')
    def sell_to_close(self, asset = None, quantity: int = None, price: float = None):
        return self.add_leg(asset=asset, quantity=quantity, price=price, order_type='stc')


    def add_leg(self, leg: Leg = None, asset = None, quantity: int = None, order_type: str = None,
                price: float = None):

        # if asset is a list-like object, then take the first elent in the list
        if asset and hasattr(asset, '__iter__') and not isinstance(asset, str):
            asset = asset[0] if len(asset) > 0 else None

        # if asset is a quote, replace it with the actual asset
        if asset and isinstance(asset, Quote):
            asset = asset.asset

        asset = asset_factory(asset)
        quantity = int(quantity)

        if asset is None:
            raise Exception("Order.add_leg: an asset is required")

        if leg is not None:
            if len([_.asset.symbol for _ in self.legs if _.asset == leg.asset]) > 0:
                raise Exception("Order.add_leg symbol {} already exists within this order".format(leg.asset.symbol))
            self.legs.append(leg)
            self.price = self.price + leg.price * abs(quantity) if self.price is not None and leg.price is not None else None
        else:
            if len([_.asset.symbol for _ in self.legs if _.asset == asset]) > 0:
                raise Exception("Order.addLeg symbol {} already exists within this order".format(asset.symbol))

            self.legs.append(Leg(asset=asset, quantity=quantity, order_type=order_type, price=price))
            self.price = self.price + price * abs(quantity) if self.price is not None and price is not None else None


        return self
