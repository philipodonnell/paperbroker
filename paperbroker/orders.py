"""

    Just a few ordering classes. Again, minimal logic.

"""

from .assets import Asset, asset_factory

class Leg(object):
    def __init__(self, asset: Asset, quantity: int, order_type: str, price: float = None):
        self.asset = asset
        self.quantity = quantity
        self.order_type = order_type
        self.price = price

class Order(object):
    def __init__(self, legs = None, price=None, condition='market'):
        self.legs = legs if legs is not None else []
        self.status = 'open'
        self.price = 0.0
        self.total_price = 0.0
        self.condition = condition


    def add_leg(self, leg: Leg = None, asset = None, quantity: int = None, order_type: str = None,
                price: float = None):

        asset = asset_factory(asset)
        quantity = int(quantity)
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



