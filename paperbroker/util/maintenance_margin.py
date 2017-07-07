import arrow

from assets import Underlying, Option


# positions is expected to contain Position objects representing positions
def calculate_maintenance_margin(positions=None, broker=None):
    if positions is None: positions = list()

    total_margin_requirement = 0.0

    # count the number of long/short shares
    total_long_shares = sum([p.quantity for p in positions if isinstance(p.asset, Underlying) and p.quantity > 0])
    total_short_shares = sum([p.quantity for p in positions if isinstance(p.asset, Underlying) and p.quantity < 0])

    # get the short calls/puts
    short_calls = []
    for call in [p for p in positions if
                 isinstance(p.asset, Option) and p.quantity < 0 and p.asset.option_type == 'call']:
        for x in range(0, abs(call.quantity)):
            short_calls.append(call)

    short_puts = []
    for put in [p for p in positions if
                 isinstance(p.asset, Option) and p.quantity < 0 and p.asset.option_type == 'put']:
        for x in range(0, abs(put.quantity)):
            short_puts.append(put)

    # get all the long calls/puts
    long_calls = []
    for call in [p for p in positions if
                 isinstance(p.asset, Option) and p.quantity > 0 and p.asset.option_type == 'call']:
        for x in range(0, abs(call.quantity)):
            long_calls.append(call)

    long_puts = []
    for put in [p for p in positions if
                 isinstance(p.asset, Option) and p.quantity > 0 and p.asset.option_type == 'put']:
        for x in range(0, abs(put.quantity)):
            long_puts.append(put)

    # sort by in the moneyness
    short_calls = sorted(short_calls, key = lambda k: k.asset.strike, reverse=False)
    long_calls = sorted(long_calls, key = lambda k: k.asset.strike, reverse=False)
    short_puts = sorted(short_puts, key = lambda k: k.asset.strike, reverse=True)
    long_puts = sorted(long_puts, key = lambda k: k.asset.strike, reverse=True)



    for short_call in short_calls:

        if total_long_shares >= 100:
            # if there are enough shares to cover this call, cover it and don't hit margin
            total_long_shares -= 100
            total_margin_requirement += 0
        elif len(long_calls) > 0:
            long_call = long_calls.pop(0)
            if long_call.asset.strike <= short_call.asset.strike:
                # if the long strike lower or the same as the short strike, its a debit spread, no margin hit
                total_margin_requirement += 0
            else:
                # if the long strike is higher than the short strike, its a credit spread, margin hit of strike width
                total_margin_requirement += (long_call.asset.strike - short_call.asset.strike) * 100
        else:
            raise Exception("Margins on naked calls are not yet supported")

    for short_put in short_puts:

        if total_short_shares >= 100:
            # if there are enough shares to cover this put, cover it and don't hit margin
            total_short_shares -= 100
            total_margin_requirement += 0
        elif len(long_puts) > 0:
            long_put = long_puts.pop(0)
            if long_put.asset.strike >= short_put.asset.strike:
                # if the long strike higher or the same as the short strike, its a debit spread, no margin hit
                total_margin_requirement += 0
            else:
                # if the long strike is lower than the short strike, its a credit spread, margin hit of strike width
                total_margin_requirement += (short_put.asset.strike - long_put.asset.strike) * 100
        else:
            raise Exception("Margins on naked puts are not yet supported")



    """
            # if we can't cover it with shares and there's no long calls left, its naked
            current_call_price = broker.get_spot_price(short_call.asset)
            current_underlying_price = broker.get_spot_price(short_call.underlying.asset)

            total_margin_requirement += max(
                # [(.20 x 44.66) – 8.66 + .25] x 16 x 100
                ((0.20 * current_underlying_price) - (
                short_call.asset.strike - current_underlying_price) + current_call_price) * 100,
                # [(.10 x 44.66) + .85] x 10 x 100
                ((0.10 * current_underlying_price) + current_call_price) * 100
            )

    """
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



