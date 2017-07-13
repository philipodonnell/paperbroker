###############################
#
# Greeks for european-style options
#
###############################

import ivolat3

def get_option_greeks(option_type, strike, underlying_price, days_to_expiration, price, dividend = 0.0):

    out = {
        "iv": None,
        "delta": None,
        "vega": None,
        "theta": None,
        "rho": None,
        "gamma": None,
        "vanna": None,
        "charm": None,
        "speed": None,
        "zomma": None,
        "color": None,
        "veta": None,
        "vomma": None,
        "ultima": None,
        "dual_delta": None,
    }

    if option_type is None or (option_type != 'put' and option_type != 'call') : return out
    if strike is None: return out
    if underlying_price is None: return out
    if days_to_expiration is None or days_to_expiration <= 0: return out
    if price is None: return out
    if dividend is None: dividend = 0.0

    # stock price
    s = underlying_price
    # option strike price
    k = strike
    # risk-free interest rate
    r = days_to_expiration / 365 * 0.02 # (2% treasury rate)
    # drift rate (dividend)
    q = dividend
    # time remaining until expiration (in years)
    t = days_to_expiration / 365.0
    # call option price
    p = price

    # annual volatility of stock price
    # sigma = 0.2

    # call opition implied volatility
    sigma = ivolat3.ivolat_call(s, k, r, q, t, p) if option_type == 'call' else ivolat3.ivolat_put(s, k, r, q, t, p)

    if sigma != sigma:
        # means sigma is not a number
        # but everything else needs it so bail
        #we were unable to calculate implied volatility which is the base of all the other calculations
        # no iv means no greeks
        return out

    out['iv'] = sigma

    out['delta'] = ivolat3.delta_call(s, k, r, q, t, sigma) if \
        option_type == 'call' else ivolat3.delta_put(s, k, r, q, t, sigma)

    out['vega'] = ivolat3.vega(s, k, r, q, t, sigma)

    out['theta'] = (ivolat3.theta_call(s, k, r, q, t, sigma) if
                    option_type == 'call' else ivolat3.theta_put(s, k, r, q, t, sigma)) / 365

    out['rho'] = ivolat3.rho_call(s, k, r, q, t, sigma) if \
        option_type == 'call' else ivolat3.rho_put(s, k, r, q, t, sigma)

    out['gamma'] = ivolat3.gamma(s, k, r, q, t, sigma)
    out['vanna'] = ivolat3.vanna(s, k, r, q, t, sigma)
    out['charm'] = (ivolat3.charm_call(s, k, r, q, t, sigma) if \
        option_type == 'call' else ivolat3.charm_put(s, k, r, q, t, sigma)) / 365
    out['speed'] = ivolat3.speed(s, k, r, q, t, sigma) / 365
    out['zomma'] = ivolat3.zomma(s, k, r, q, t, sigma) / 365
    out['color'] = ivolat3.color(s, k, r, q, t, sigma) / (365)
    out['veta'] = ivolat3.DvegaDtime(s, k, r, q, t, sigma) / (100 * 365)
    out['vomma'] = ivolat3.vomma(s, k, r, q, t, sigma)
    out['ultima'] = ivolat3.ultima(s, k, r, q, t, sigma) / 365

    out['dual_delta'] = ivolat3.dualdelta_call(s, k, r, q, t, sigma) if option_type == 'call' else ivolat3.dualdelta_put(
        s, k, r, q, t, sigma)

    return out

