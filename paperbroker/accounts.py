"""

    Brokerage Accounts.
    Keeps track of positions.
    Read and Save with a /paperbroker/adapters/accounts/AccountAdapter

"""

import random
import string

def account_factory(account):
    if isinstance(account, Account):
        return account
    return Account(account_id=account)


class Account():

    def __init__(self, positions=None, account_id:str=None):
        self.account_id = account_id if account_id is not None else 'account' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        self.cash = 10000
        self.maintenance_margin = 0.0
        self.positions = positions if positions is not None else []



