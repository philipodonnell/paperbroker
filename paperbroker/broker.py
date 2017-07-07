def get_price(self, estimator=None, quantity=1):
    """
        Get the current estimated quote price (if fixed) or generate a new price
    :param estimator: optional if price is fixed, otherwise must have a method with .estimate(quote, quantity)
    :param quantity: optional if price is fixed, passed to .estimate(quote, quantity)
    :return: a float price that the security could expect to trade at based on the quantity
    """

    estimator = estimator or self.estimator

    if self.fixed_price is None:
        if estimator is None:
            raise Exception("Quote.get_price(): `estimator` must have a method with .estimate(quote, quantity)")
        return estimator.estimate(self, quantity)

    return self.fixed_price




