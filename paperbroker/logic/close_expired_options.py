import arrow
from ..accounts import Account
from ..assets import Option, Call, Put, Asset
from ..adapters.quotes.QuoteAdapter import QuoteAdapter
from ..orders import Order, Leg
from ..positions import Position

from .group_into_basic_strategies import create_asset_strategies
from ..adapters.markets import MarketAdapter

from copy import copy
from math import copysign


def drain_asset(positions, asset, quantity):
    """
        Iterate through the positions and decrease the quantity until you have drained all the positions
    """
    remaining_quantity = quantity

    # get a list of positions that are opposite to the quantity we are draining
    positions = [_ for _ in positions if _.asset == asset and copysign(1,_.quantity) == copysign(1, quantity * -1)]
    for position in positions:

        if abs(remaining_quantity) <= abs(position.quantity):
            # there are enough quantity in this position to complete it
            position.quantity += remaining_quantity
            remaining_quantity = 0
            return remaining_quantity

        if abs(remaining_quantity) > abs(position.quantity):
            # we are going to have some left over
            remaining_quantity += position.quantity
            position.quantity = 0

    return remaining_quantity

def close_expired_options(account:Account, quote_adapter:QuoteAdapter, market_adapter:MarketAdapter):
    """
    Process an account's positions and handle the process of closing any expired options
    :param account:
    :return:
    """

    # the effect of an options expiration can be thought of as an option transaction that was forced to take place
    # at exactly its intrinsic value, along with its resulting position
    # we simulate this by processing an order to make that happen
    starting_account = copy(account)

    # no positions, bail
    if len(account.positions) == 0:
        return

    # get one quote so we can see what day it is
    current_date = quote_adapter.get_quote(asset=account.positions[0].asset.underlying if isinstance(account.positions[0].asset, Option) else account.positions[0].asset ).quote_date

    # get a list of all the options that are expired
    expired = [_ for _ in account.positions
               if isinstance(_.asset, Option)
               and arrow.get(_.asset.expiration_date).format('YYYY-MM-DD') < arrow.get(current_date).format('YYYY-MM-DD')]

    # no expirations, bail
    if len(expired) == 0:
        return

    # get a unique list of underlyings
    underlyings = list(set([_.asset.underlying.symbol for _ in expired]))

    # iterate through them
    for underlying in underlyings:

        # get a current quote
        underlying_quote = quote_adapter.get_quote(underlying)

        # get the positions in or of this underlying
        positions_in_underlying = [_ for _ in account.positions if (isinstance(_.asset, Option) and _.asset.underlying == underlying) or (_.asset == underlying)]

        # make a list of the positions of expiring options in this underlying
        expired_positions = [_ for _ in account.positions
                   if isinstance(_.asset, Option)
                   and arrow.get(_.asset.expiration_date).format('YYYY-MM-DD') <
                    arrow.get(current_date).format('YYYY-MM-DD')
                   ]

        # record the amount of long and short equity we have open to work with
        long_equity = sum([_.quantity for _ in positions_in_underlying
                           if not isinstance(_.asset, Option)
                           and _.quantity > 0
                            ])
        short_equity = sum([_.quantity for _ in positions_in_underlying
                            if not isinstance(_.asset, Option)
                            and _.quantity < 0
                            ])

        # start entering orders for the expired options
        for position in expired_positions:

            # figure out if the option is ITM
            is_itm = position.asset.get_intrinsic_value(underlying_price=underlying_quote.price) > 0

            if not is_itm:
                # if the option is not in the money, it expired worthless, force it to dissapear
                pass
            else:
                # the option is in the money, so we need to handle it

                if position.asset.option_type == 'call' and position.quantity > 0:
                    # long calls expire by buying the stock at the strike price and
                    #   adding the option cost basis to the stock cost basis
                    account.cash -= position.asset.strike * position.quantity * 100
                    account.positions.append(Position(asset=underlying,
                                                      quantity=abs(position.quantity) * 100,
                                                      cost_basis=position.asset.strike + abs(position.cost_basis)))

                elif position.asset.option_type == 'call' and position.quantity < 0:
                    # short calls expire by being forced to surrender the stock and get the strike price
                    # we'll handle this by putting in a fixed price sell-to-close order for the underlying
                    # if for some reason the order doesn't fill (like there is no stock available)

                    # two things can happen here. Either you have enough shares to surrender and so you surrender them
                    # or you don't have enough shares and you're forced to buy them to surrender

                    # iterate through each quantity to make the code simpler
                    for x in range(abs(position.quantity)):
                        if long_equity > 100:
                            # there is stock available to surrender
                            # drain 100 shares
                            drain_asset(positions=account.positions, asset=position.asset.underlying, quantity=-100)
                            long_equity -= 100
                        else:
                            # there is not enough stock, so subtract enough cash to buy the shares
                            account.cash -= underlying_quote.price * 100
                            # then sell them back at the strike
                            account.cash += position.asset.strike * 100

                elif position.asset.option_type == 'put' and position.quantity > 0:
                    # long puts expire by you gaining short shares and cash at the strike
                    #   adding the option cost basis to the stock cost basis
                    account.cash += position.asset.strike * abs(position.quantity) * 100
                    account.positions.append(Position(asset=underlying,
                                                      quantity= -1 * abs(position.quantity) * 100,
                                                      cost_basis=position.asset.strike - abs(position.cost_basis)))

                elif position.asset.option_type == 'put' and position.quantity < 0:
                    # short puts expire by you being forced to liquidate a short but you  shares strike price in cash
                    # iterate through each quantity to make the code simpler

                    for x in range(abs(position.quantity)):
                        if short_equity < -100:
                            # we have short equity to give up
                            # drain 100 shares
                            drain_asset(positions=account.positions, asset=position.asset.underlying, quantity=100)
                            account.cash -= underlying_quote.price * 100
                            short_equity += 100
                        else:
                            # there is not enough short available, so you get to buy some shares, so take the cash
                            account.cash -= underlying_quote.price * 100
                            # and give it back
                            account.cash += position.asset.strike * 100


            position.quantity = 0

    account.positions = [_ for _ in account.positions if _.quantity != 0]
    return account