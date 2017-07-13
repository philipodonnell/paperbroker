"""

    Expects an account after an order goes through but may be in an invalid state.

    For instance, an account may have negative cash, or be holding an option with an
      invalid permission level. Throws exceptions if it find an issue.

"""


def validate_account(account):

    if account.cash < 0:
        raise Exception('validate_account: You do not have enough cash for this order.')

    if account.cash < account.maintenance_margin:
        raise Exception('validate_account: You do not have enough cash to cover the margin requirement.')

    return account


