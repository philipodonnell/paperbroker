"""

    Estimation tools for determining the likely price that an asset would transact at.

    Make your own estimator by subclassing Estimator

    If you need to force orders to go through you can use the FixedPriceEstimator to force the
    market maker to fill at a specific price

"""
from math import copysign
from .quotes import Quote


class Estimator:
    """
        THe mother of all estimators, midway between the bid and ask
    """
    def estimate(self, quote:Quote, quantity = None):

        if quote.bid is not None and quote.ask is None and quote.bid > 0.0 and quote.ask > 0.0:
            return round((quote.bid + quote.ask) / 2, 2)

        if quote.price is not None:
            return round(quote.price,2)

        raise Exception('Estimator.estimate: Cannot estimate a price if the bid or ask are None or 0.0')


class MidpointEstimator(Estimator):
    """
        The default estimator if nothing else is available, just passes through to estimator base
    """

class FixedPriceEstimator(Estimator):
    """
        Used to force orders to fill at certain prices, such as for when options expire or testing
    """
    def __init__(self, price= 0.0):
        self.price = price
        return

    def estimate(self, quote: Quote, quantity=None):
        return self.price

class SlippageEstimator(Estimator):
    """
        A price estimator assuming a certain slippage within the bid-ask spread.

         `slippage` should be a float number:
            + 1.0 transaction took place at the most favorable price (buy@bid/sell@ask) (higher is better)
              0.0 transaction took place at the midpoint
            - 1.0 transaction took place at the least favorable price (buy@ask/sell@bid) (lower is worse)
    """

    def __init__(self, slippage = 0.0):
        self.slippage = slippage
        return

    def estimate(self, quote:Quote, quantity:int = None):

        # quantity is only used for direction
        quantity = copysign(1, quantity)

        if quote.bid is None or quote.ask is None or quote.bid == 0.0 or quote.ask == 0.0:
            raise Exception(
                'SlippageEstimator.estimate: Cannot estimate a price if the bid or ask are None or 0.0')

        if quantity is None or quantity == 0:
            raise Exception(
                'SlippageEstimator.estimate: Must provide a signed quantity to buy or sell.')

        spread = (quote.ask - quote.bid) / 2
        midpoint = quote.bid + spread

        if quantity > 0:
            return midpoint - spread * self.slippage
        else:
            return midpoint + spread * self.slippage

