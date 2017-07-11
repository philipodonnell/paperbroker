from ..orders import Order
from ..accounts import Account
from ..assets import Option
from ..positions import Position
from ..adapters.quotes import QuoteAdapter
from ..estimators import Estimator
from copy import deepcopy
from math import copysign


def fill_order(account: Account = None, order: Order = None, quote_adapter:QuoteAdapter=None, estimator:Estimator=None):
    if account is None:
        raise Exception("logic.fill_order: must provide an account.")

    if order is None or len(order.legs) == 0:
        raise Exception("logic.fill_order: Orders must have one or more than one leg.")

    if quote_adapter is None:
        raise Exception("logic.fill_order: must provide a quote_adapter")

    if estimator is None:
        estimator = Estimator()

    # figure out the best expected price the order would fill at
    leg_prices = {}
    order_price = 0.0
    for leg in order.legs:
        leg_prices[leg] = estimator.estimate(quote_adapter.get_quote(leg.asset)) * copysign(1, leg.quantity)
        order_price += leg_prices[leg] * abs(leg.quantity)

    if order.condition == 'market' or (order.condition == 'limit' and order.price < order_price):

        for leg in order.legs:

            cost_basis = leg_prices[leg]

            if leg.order_type[0].lower() == 'b' and (leg.quantity < 0 or cost_basis < 0):
                raise Exception(
                    "logic.fill_order: BTO or BTC legs must be positive quantity and positive price")

            if leg.order_type[0].lower() == 's' and (leg.quantity > 0 or cost_basis > 0):
                raise Exception(
                    "logic.fill_order: STO or STC legs must be negative quantity and negative price")

            if isinstance(leg.asset, Option):
                account.cash -= abs(cost_basis * leg.quantity) * copysign(1, leg.quantity) * 100
            else:
                account.cash -= abs(cost_basis * leg.quantity) * copysign(1, leg.quantity)

            # if the leg is opening, then create a position for each leg
            if leg.order_type.lower() in ['bto', 'sto']:

                account.positions.append(Position(leg.asset, leg.quantity, cost_basis))

            elif leg.order_type.lower() in ['btc', 'stc']:

                closable_positions = [position for position in account.positions if
                                      position.asset == leg.asset and copysign(1, position.quantity) == (
                                          copysign(1, leg.quantity) * -1)]

                if len(closable_positions) == 0:
                    raise Exception("logic.fill_order: There are no available positions to close.")

                # add up the quantities available
                quantity_available_to_close = sum([position.quantity for position in closable_positions])

                if abs(quantity_available_to_close) < abs(leg.quantity):
                    raise Exception("logic.fill_order: There are not enough open positions to close.")

                # iterate through the positions and reduce the quantity by the leg quantity
                quantity_to_close_remaining = abs(leg.quantity)
                for position in closable_positions:
                    if quantity_to_close_remaining > 0:
                        quantity_can_close = abs(position.quantity)
                        quantity_to_close = min(quantity_to_close_remaining, quantity_can_close)
                        position.quantity += copysign(1, position.quantity) * -1 * quantity_to_close
                        quantity_to_close_remaining -= quantity_to_close

    # filter out any positions that are completely closed
    account.positions = [position for position in account.positions if position.quantity != 0]

    order.status = 'filled'

    return account

