


class OrderImpact():
    """
    This class is used to perform analysis the effect of an order on an account. It is used mostly by risk management
    but you can also use it for gemeral analysis

    It is initialized with these objects
    account0 - the account in the state is was before the order
    account1 - the account in the state it was after the order
    order - the order itself
    actual_commission - The amount of commission charged for the order
    actual_fill_price - The actual price that the order filled at

    """
    def __init__(self, account0 = None, account1 = None, order = None, actual_commission = None, actual_fill_price = None):
        self.account0 = account0
        self.account1 = account1
        self.order = order
        self.actual_commission = actual_commission
        self.actual_fill_price = actual_fill_price

    @property
    def change_in_cash(self):
        return self.account1.cash - self.account0.cash

    @property
    def change_in_maintenance_margin(self):
        return self.account1.maintenance_margin - self.account0.maintenance_margin



