from ...orders import Order
from ...accounts import Account
from ...assets import Option, asset_factory, Asset
from ...positions import Position
from ...adapters.quotes import QuoteAdapter
from ...estimators import Estimator
from copy import deepcopy
from math import copysign

from .MarketAdapter import MarketAdapter

from ...logic.fill_order import fill_order
from ...logic.close_expired_options import close_expired_options

class PendingOrder():
    def __init__(self, order: Order = None, account: Account = None, estimator: Estimator=None):
        self.order = order
        self.account = account
        self.estimator = estimator


class PaperMarketAdapter(MarketAdapter):

    def __init__(self, quote_adapter:QuoteAdapter, estimator: Estimator = None):
        self.pending_orders = []
        self.quote_adapter = quote_adapter
        self.estimator = estimator if estimator is not None else Estimator()

    def expire_options(self, account:Account, quote_adapter:QuoteAdapter):
        close_expired_options(account=account, quote_adapter=quote_adapter, market_adapter=self)

    # fill any open orders that the broker knows about
    # # if it is possible to fill the order
    # and then cancel everything that was left
    def fill_pending_orders(self, cancel_on_failure = True):
        for pending_order in self.pending_orders:
            try:

                #actually fill the order
                fill_order(account=pending_order.account,
                        order = pending_order.order,
                        quote_adapter=self.quote_adapter,
                        estimator=pending_order.estimator)

                pending_order.order.status = 'filled'

            except Exception as e:
                pending_order.order.status = 'failed'
                print("Order failed to execute")
                print(e)
                pass

        self.pending_orders = [_ for _ in self.pending_orders if _.order.status != 'filled']

        if cancel_on_failure:
            self.pending_orders = []

    def simulate_order(self, account: Account, order: Order, estimator:Estimator=None):
        estimator = estimator if estimator is not None else self.estimator

        # since we are simulating the order, make a copy of the account and the order
        # we'll force the order against the account and check the values at the end
        account_copy = deepcopy(account)
        order_copy = deepcopy(order)

        # force fill copies of any open orders against copies of this account
        for pending_order in [_ for _ in self.pending_orders if _.account == account]:
            account_copy = fill_order(account=account_copy, order=deepcopy(pending_order.order), estimator=estimator, quote_adapter=self.quote_adapter)

        # now fill this order against a copy of the account
        fill_order(account=account_copy, order=order_copy, estimator=estimator, quote_adapter=self.quote_adapter)

        return account_copy


    def enter_order(self, account: Account, order: Order, estimator:Estimator=None, auto_fill=True):
        estimator = estimator if estimator is not None else self.estimator
        self.pending_orders.append(PendingOrder(account=account, order=order, estimator=estimator))
        if auto_fill:
            self.fill_pending_orders()
        return account


