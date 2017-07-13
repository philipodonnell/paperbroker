from .adapters.quotes import QuoteAdapter
from .adapters.quotes import GoogleFinanceQuoteAdapter

from .adapters.accounts import AccountAdapter
from .adapters.accounts import LocalFileSystemAccountAdapter

from .adapters.markets import MarketAdapter
from .adapters.markets.PaperMarketAdapter import PaperMarketAdapter

from .accounts import Account
from .orders import Order
from .estimators import Estimator
from .assets import Asset, asset_factory


class PaperBroker():

    def __init__(self, quote_adapter:QuoteAdapter=None, account_adapter:AccountAdapter=None, market_adapter:MarketAdapter=None):
        self.quote_adapter = quote_adapter if quote_adapter is not None else GoogleFinanceQuoteAdapter()
        self.account_adapter = account_adapter if account_adapter is not None else LocalFileSystemAccountAdapter()
        self.market_adapter = market_adapter if market_adapter is not None else PaperMarketAdapter(self.quote_adapter)

    def get_price(self, asset):
        quote = self.get_quote(asset)
        return quote.price if quote is not None else None

    def get_quote(self, asset):
        return self.quote_adapter.get_quote(asset)

    def get_options(self, underlying_asset=None, expiration_date=None):
        return self.quote_adapter.get_options(underlying_asset, expiration_date)

    def get_expiration_dates(self, underlying_asset=None):
        return self.quote_adapter.get_expiration_dates(underlying_asset)

    def open_account(self):
        account = Account()
        self.account_adapter.put_account(account)
        return account

    def get_account(self, account_id:str=None):
        return self.account_adapter.get_account(account_id=account_id)

    def buy_to_open(self, account: Account=None, asset:Asset=None, quantity = 1, simulate=False):
        o = Order()
        o.add_leg(asset=asset_factory(asset), quantity=abs(quantity), order_type='bto')
        return self.enter_order(account, o, simulate=simulate)

    def sell_to_open(self, account: Account=None, asset:Asset=None, quantity = 1, simulate=False):
        o = Order()
        o.add_leg(asset=asset_factory(asset), quantity=abs(quantity)*-1, order_type='sto')
        return self.enter_order(account, o, simulate=simulate)

    def buy_to_close(self, account: Account=None, asset:Asset=None, quantity = 1, simulate=False):
        o = Order()
        o.add_leg(asset=asset_factory(asset), quantity=abs(quantity), order_type='btc')
        return self.enter_order(account, o, simulate=simulate)

    def sell_to_close(self, account: Account=None, asset:Asset=None, quantity = 1, simulate=False):
        o = Order()
        o.add_leg(asset=asset_factory(asset), quantity=abs(quantity)*-1, order_type='stc')
        return self.enter_order(account, o, simulate=simulate)

    def enter_order(self, account: Account, order: Order, estimator:Estimator=None, simulate=False):

        if simulate:
            return self.market_adapter.simulate_order(account=account, order=order, estimator=estimator)

        # enter order always simulates first but only executes on simulate=False
        self.market_adapter.simulate_order(account=account, order=order, estimator=estimator)
        self.market_adapter.enter_order(account=account, order=order, estimator=estimator)
        self.account_adapter.put_account(account)
        return account


    def simulate_order(self, account: Account, order: Order, estimator:Estimator=None):
        account_after = self.market_adapter.simulate_order(account=account, order=order, estimator=estimator)

        if account_after.cash < 0:
            raise Exception('PaperBroker.simulate_order: You do not have enough cash for this order.')

        if account_after.cash < account.maintenance_margin:
            raise Exception('PaperBroker.simulate_order: You do not have enough cash to cover the margin requirement.')

        return account_after

    def close_position(self, account:Account, position=None):
        return self.close_positions(account, [position])

    def close_positions(self, account:Account, positions=None):
        if positions is None:
            positions = []

        btc = {}
        stc = {}
        assets_by_symbol = {}
        for p in positions:
            assets_by_symbol[p.asset.symbol] = p.asset
            if p.quantity > 0:
                stc[p.asset.symbol] = stc.get(p.asset.symbol, 0) + p.quantity
            else:
                btc[p.asset.symbol] = btc.get(p.asset.symbol, 0) + p.quantity

        o = Order()
        for s in stc.keys():
            o.add_leg(order_type = 'stc', asset=assets_by_symbol[s], quantity=-1*stc[s])
        for b in btc.keys():
            o.add_leg(order_type = 'btc', asset=assets_by_symbol[b], quantity=abs(btc[b]))

        self.enter_order(account, o)



