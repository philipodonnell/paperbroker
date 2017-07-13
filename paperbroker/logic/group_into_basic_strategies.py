"""

    This module contains functions to group an arbitrary set of positions
      into a number of strategies, each one of the following "basic" strategies

    class AssetStrategy(BasicStrategy): A strategy that involves going long or short in an asset
    class OffsetStrategy(BasicStrategy): A strategy that involves being simultaneously long and short the same asset
    class CoveredStrategy(BasicStrategy): A strategy where an asset is used to cover the risk from the sale of an option
    class SpreadStrategy(BasicStrategy): A strategy where two options with inverse risk profiles are used to create a defined risk

    This is primarily used to calculate the maintenance margin requirement, but could be useful for other reasons
    You could also inherit from these to create more specific strategies, like:
        class NakedOptionStrategy(AssetStrategy): ?
        class CreditSpreadStrategy(SpreadStrategy): ?

    usage: group_into_basic_strategies(positions:Position)

    Special thanks to /u/EdKaim for the outline of this process:
    https://www.reddit.com/r/options/comments/6iivnu/generic_method_of_calculating_margin_requirements/dj7msph/

"""



from ..assets import Asset, Option, Call, Put
from ..positions import Position

class BasicStrategy:
    def __init__(self, strategy_type=None, quantity=1):
        self.strategy_type = strategy_type if strategy_type is not None else 'basic'
        self.quantity = quantity




class AssetStrategy(BasicStrategy):
    """
        A strategy that involves going long or short in an asset
    """
    def __init__(self, asset:Asset, quantity=1):
        super(AssetStrategy, self).__init__('asset', quantity)
        self.asset = asset
        self.direction = 'short' if self.quantity < 0 else 'long'



class OffsetStrategy(BasicStrategy):
    """
        A strategy that involves being simultaneously long and short the same asset
    """
    def __init__(self, asset:Asset, quantity=1):
        super(OffsetStrategy, self).__init__('offset', quantity)
        self.asset = asset


class SpreadStrategy(BasicStrategy):
    """
        A strategy where two options with inverse risk profiles are used to create a defined risk
    """
    def __init__(self, sell_option:Option, buy_option:Option, quantity=1):
        super(SpreadStrategy, self).__init__('spread', quantity)

        if sell_option.option_type != buy_option.option_type:
            raise Exception("SpreadStrategy: option types of sell and buy must match")

        if sell_option.underlying != buy_option.underlying :
            raise Exception("SpreadStrategy: underlying types of sell and buy must match")

        if sell_option.strike == buy_option.strike :
            raise Exception("SpreadStrategy: strikes of sell and buy must be different")

        self.sell_option = sell_option
        self.buy_option = buy_option
        self.option_type = sell_option.option_type
        self.quantity = abs(quantity)

        if sell_option.option_type == 'put':
            self.spread_type = 'credit' if self.sell_option.strike > self.buy_option.strike else 'debit'
        else:
            self.spread_type = 'credit' if self.sell_option.strike < self.buy_option.strike else 'debit'



class CoveredStrategy(BasicStrategy):
    """
        A strategy where an asset is used to cover the risk from the sale of an option
    """
    def __init__(self, asset:Asset, sell_option:Option, quantity=1):
        super(CoveredStrategy, self).__init__('covered', quantity)

        if asset != sell_option.underlying:
            raise Exception("CoveredStrategy: option underlying must be the same as asset")

        self.asset = asset
        self.sell_option = sell_option
        self.quantity = abs(quantity)



def create_asset_strategies(positions, underlying):
    positions = [_ for _ in positions if
                 (isinstance(_.asset, Option) and _.asset.underlying == underlying) or (_.asset == underlying)]

    if len(positions) == 0: return []

    asset_strategies = []

    long_equity = AssetStrategy(asset=underlying, quantity=sum([_.quantity for _ in positions if not isinstance(_.asset, Option) and _.quantity > 0]))
    short_equity = AssetStrategy(asset=underlying, quantity=sum([_.quantity for _ in positions if not isinstance(_.asset, Option) and _.quantity < 0]))

    # get the short calls/puts
    short_calls = []
    for call in [p for p in positions if
                 isinstance(p.asset, Option) and p.quantity < 0 and p.asset.option_type == 'call']:
        for x in range(0, abs(call.quantity)):
            short_calls.append(AssetStrategy(asset=call.asset, quantity=-1))

    short_puts = []
    for put in [p for p in positions if
                 isinstance(p.asset, Option) and p.quantity < 0 and p.asset.option_type == 'put']:
        for x in range(0, abs(put.quantity)):
            short_puts.append(AssetStrategy(asset=put.asset, quantity=-1))

    # get all the long calls/puts
    long_calls = []
    for call in [p for p in positions if
                 isinstance(p.asset, Option) and p.quantity > 0 and p.asset.option_type == 'call']:
        for x in range(0, abs(call.quantity)):
            long_calls.append(AssetStrategy(asset=call.asset, quantity=1))

    long_puts = []
    for put in [p for p in positions if
                 isinstance(p.asset, Option) and p.quantity > 0 and p.asset.option_type == 'put']:
        for x in range(0, abs(put.quantity)):
            long_puts.append(AssetStrategy(asset=put.asset, quantity=1))

    return [] + [long_equity]+[short_equity]+long_puts+short_puts+long_calls+short_calls



def _group_into_basic_strategies_in_underlying(underlying, positions):

    positions = [_ for _ in positions if (isinstance(_.asset, Option) and _.asset.underlying == underlying) or (_.asset == underlying)]

    strategies = []

    long_equity = AssetStrategy(asset=underlying, quantity=sum([_.quantity for _ in positions if not isinstance(_.asset, Option) and _.quantity > 0]))
    short_equity = AssetStrategy(asset=underlying, quantity=sum([_.quantity for _ in positions if not isinstance(_.asset, Option) and _.quantity < 0]))

    # get the short calls/puts
    short_calls = []
    for call in [p for p in positions if
                 isinstance(p.asset, Option) and p.quantity < 0 and p.asset.option_type == 'call']:
        for x in range(0, abs(int(call.quantity))):
            short_calls.append(AssetStrategy(asset=call.asset, quantity=-1))

    short_puts = []
    for put in [p for p in positions if
                 isinstance(p.asset, Option) and p.quantity < 0 and p.asset.option_type == 'put']:
        for x in range(0, abs(int(put.quantity))):
            short_puts.append(AssetStrategy(asset=put.asset, quantity=-1))

    # get all the long calls/puts
    long_calls = []
    for call in [p for p in positions if
                 isinstance(p.asset, Option) and p.quantity > 0 and p.asset.option_type == 'call']:
        for x in range(0, abs(int(call.quantity))):
            long_calls.append(AssetStrategy(asset=call.asset, quantity=1))

    long_puts = []
    for put in [p for p in positions if
                 isinstance(p.asset, Option) and p.quantity > 0 and p.asset.option_type == 'put']:
        for x in range(0, abs(int(put.quantity))):
            long_puts.append(AssetStrategy(asset=put.asset, quantity=1))

    # sort by in the moneyness
    short_calls = sorted(short_calls, key = lambda k: k.asset.strike, reverse=False)
    long_calls = sorted(long_calls, key = lambda k: k.asset.strike, reverse=False)
    short_puts = sorted(short_puts, key = lambda k: k.asset.strike, reverse=True)
    long_puts = sorted(long_puts, key = lambda k: k.asset.strike, reverse=True)




    for short_call in short_calls:

        if long_equity.quantity >= 100:
            # if there are enough shares to cover this call, cover it and don't hit margin
            strategies.append(CoveredStrategy(asset=underlying, sell_option=short_call.asset))
            long_equity.quantity -= 100

        elif len(long_calls) > 0:
            # if there are still any long calls, use them to build spreads
            long_call = long_calls.pop(0)
            strategies.append(SpreadStrategy( buy_option=long_call.asset, sell_option=short_call.asset))

        else:
            # if not then we just have to add this one as a naked short call
            strategies.append(short_call)


    for short_put in short_puts:

        if short_equity.quantity >= 100:
            # if there are enough shares to cover this put, cover it and don't hit margin
            strategies.append(CoveredStrategy(asset=underlying, sell_option=short_put.asset))
            short_put.quantity -= 100

        elif len(long_puts) > 0:
            # if there are still any long puts, use them to build spreads
            long_put = long_puts.pop(0)
            strategies.append(SpreadStrategy( buy_option=long_put.asset, sell_option=short_put.asset))

        else:
            # if not then we just have to add this one as a naked short put
            strategies.append(short_put)


    # ok, now to close everything up
    # we can ignore the short option lists now because we're done with those
    # but we need to add everything long and also the long/short equities
    strategies += long_calls + long_puts + [long_equity] + [short_equity]

    return strategies

def group_into_basic_strategies(positions):

    # get a unique list of underlyings
    underlyings = list(set([_.asset.underlying.symbol for _ in positions if isinstance(_.asset, Option)]))

    # add all the strategies for each underlying
    strategies = []
    for underlying in underlyings:
        strategies += _group_into_basic_strategies_in_underlying(underlying=underlying, positions=positions)

    return strategies