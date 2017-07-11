import arrow

from ..assets import Asset, Option
from ..adapters.quotes.QuoteAdapter import QuoteAdapter
from .group_into_basic_strategies import *

"""
Special thanks to /u/EdKaim for the outline of this process:
https://www.reddit.com/r/options/comments/6iivnu/generic_method_of_calculating_margin_requirements/dj7msph/
"""

def get_maintenance_margin(strategies=None, positions=None, quote_adapter:QuoteAdapter=None):

    if positions is None: positions = list()
    if strategies is None: strategies = group_into_basic_strategies(positions)

    #start the calculation off
    total_margin_requirement = 0.0

    for strategy in strategies:

        if strategy.strategy_type == 'asset' \
                and strategy.direction == 'long':
            # no margin requirements for lond anything
            total_margin_requirement += 0

        elif strategy.strategy_type == 'covered':
            # no margin requirements for covered strategies
            total_margin_requirement += 0

        elif strategy.strategy_type == 'spread' \
                and strategy.spread_type == 'debit':
            # no margin requirements for debti spreads
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
            raise Exception("Margins on naked puts are not yet supported")

        elif strategy.strategy_type == 'asset' \
                and strategy.direction=='short' \
                and isinstance(strategy.asset, Call):
            # naked option, calculate using the formula
            current_call_price = quote_adapter.get_quote(strategy.asset).price
            current_underlying_price = quote_adapter.get_quote(strategy.asset.underlying).price

            total_margin_requirement += max(

                ((0.20 * current_underlying_price) - (
                    strategy.asset.strike - current_underlying_price) + current_call_price) * 100,

                ((0.10 * current_underlying_price) + current_call_price) * 100

            )

        else:
            raise Exception('A strategy was provided that we do not know how to calculate the maintenance margin for')

    return total_margin_requirement

if __name__ == "__main__":
    from broker import Position

    """
    Long 100 shares
    Short 2 calls at 5
    Long 3 calls at 10
    Short 4 calls at 15
    Long 2 calls at 25
    """

    positions = [
        Position(asset = Underlying(symbol='AAL'), quantity=100),
        Position(asset=Option(underlying_symbol = 'AAL', option_type='call', strike = 5, expiration_date=arrow.now()), quantity = -2),
        Position(asset=Option(underlying_symbol = 'AAL', option_type='call', strike=10, expiration_date=arrow.now()), quantity=3),
        Position(asset=Option(underlying_symbol = 'AAL', option_type='call', strike=15, expiration_date=arrow.now()), quantity=-4),
        Position(asset=Option(underlying_symbol = 'AAL', option_type='call', strike=25, expiration_date=arrow.now()), quantity=2)
    ]

    assert calculate_maintenance_margin(positions) == 2500


    # symbol,recorded_date,option_type,expires_at,strike,delta,bid,ask,days_to_expiration,iv,gamma,vega,theta
    # AAL161104C00027000,2016-11-01,call,2016-11-04,27.00,0.92014870,12.7500,14.6500,3,3.51480688,0.01159739,0.54062215,-0.31674485
    # midpoint = 13.70


    #symbol, recorded_date, option_type, expires_at, strike, delta, bid, ask, days_to_expiration, iv, gamma, vega, theta
    #AAL161104C00027500, 2016 - 11 - 01, call, 2016 - 11 - 04, 27.50, 0.93740130, 11.2000, 14.8000, 3, 2.99024114, 0.01130652, 0.44840183, -0.22352224
    # midpoint = 13.00



    #symbol, recorded_date, option_type, expires_at, strike, delta, bid, ask, days_to_expiration, iv, gamma, vega, theta
    #AAL161104C00027000, 2016 - 11 - 02, call, 2016 - 11 - 04, 27.00, 0.00000000, 11.8000, 13.8000, 2, 0.00000000, 0.00000000, 0.00000000, 0.00000000
    # midpoint = 12.80


    #symbol, recorded_date, option_type, expires_at, strike, delta, bid, ask, days_to_expiration, iv, gamma, vega, theta
    #AAL161104C00027500, 2016 - 11 - 02, call, 2016 - 11 - 04, 27.50, 0.00000000, 10.5500, 14.4000, 2, 0.00000000, 0.00000000, 0.00000000, 0.00000000
    # midpoint = 12.48



