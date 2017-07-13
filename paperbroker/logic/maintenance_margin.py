"""

    Uses the supplied positions to estimate the total cumulative margin requirement.

    Uses each basic strategy to calculate the margin of each and adds them up.

"""




import arrow

from ..assets import Asset, Option
from ..adapters.quotes.QuoteAdapter import QuoteAdapter
from .group_into_basic_strategies import *



def get_maintenance_margin(strategies=None, positions=None, quote_adapter:QuoteAdapter=None):

    if positions is None: positions = list()
    if strategies is None: strategies = group_into_basic_strategies(positions)

    #start the calculation off
    total_margin_requirement = 0.0

    for strategy in strategies:

        if strategy.strategy_type == 'asset' \
                and strategy.direction == 'long':
            # no margin requirements for long anything
            total_margin_requirement += 0

        elif strategy.strategy_type == 'asset' \
                and strategy.asset.asset_type not in ('option', 'call', 'put') \
                and strategy.direction == 'short':
            # non-option shorts have a margin requirement equal to the cost to repurchase
            total_margin_requirement += abs(strategy.quantity) * quote_adapter.get_quote(strategy.asset).price

        elif strategy.strategy_type == 'covered':
            # no margin requirements for covered strategies
            total_margin_requirement += 0

        elif strategy.strategy_type == 'spread' \
                and strategy.spread_type == 'debit':
            # no margin requirements for debit spreads
            total_margin_requirement += 0

        elif strategy.strategy_type == 'spread' \
                and strategy.spread_type == 'credit' \
                and strategy.option_type=='put':
            # credit put spreads use the width of the strikes
            total_margin_requirement += (strategy.sell_option.strike - strategy.buy_option.strike) * 100

        elif strategy.strategy_type == 'spread' \
                and strategy.spread_type == 'credit' \
                and strategy.option_type == 'call':
            # credit call spreads use the width of the strikes
            total_margin_requirement += (strategy.buy_option.strike - strategy.sell_option.strike) * 100

        elif strategy.strategy_type == 'asset' \
                and strategy.direction=='short' \
                and isinstance(strategy.asset, Put):
            # naked call can't be calculated yet, please help!
            return None

        elif strategy.strategy_type == 'asset' \
                and strategy.direction=='short' \
                and isinstance(strategy.asset, Call):
            # naked call can't be calculated yet, please help!
            return None

        else:
            raise Exception('A strategy was provided that we do not know how to calculate the maintenance margin for')

    return total_margin_requirement
