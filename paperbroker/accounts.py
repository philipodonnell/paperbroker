import random
import string

from .positions import PositionGroup

def account_factory(account):
    if isinstance(account, Account):
        return account
    return Account(account_id=account)


class Account():

    def __init__(self, positions=None, account_id:str=None):
        self.account_id = account_id if account_id is not None else 'account' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        self.capital_used = 0.0
        self.starting_cash = 0.0
        self.portfolio_value = 0.0
        self.pnl = 0.0
        self.returns = 0.0
        self.cash = 0.0
        self.positions = positions if positions is not None else []
        self.start_date = None
        self.positions_value = 0.0
        self.bid_ask_spread_estimator = None



