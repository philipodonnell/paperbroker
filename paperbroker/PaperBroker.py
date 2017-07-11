from .adapters.quotes import QuoteAdapter
from .adapters.quotes import GoogleFinanceQuoteAdapter

from .adapters.accounts import AccountAdapter
from .adapters.accounts import LocalFileSystemAccountAdapter

from .adapters.markets import MarketAdapter
from .adapters.markets.PaperMarketAdapter import PaperMarketAdapter

from .accounts import Account
from .orders import Order
from .estimators import Estimator



class PaperBroker():

    def __init__(self, quote_adapter:QuoteAdapter=None, book_adapter:AccountAdapter=None, market_adapter:MarketAdapter=None):
        self.quote_adapter = quote_adapter if quote_adapter is not None else GoogleFinanceQuoteAdapter()
        self.book_adapter = book_adapter if book_adapter is not None else LocalFileSystemAccountAdapter()
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
        self.book_adapter.put_account(account)
        return account

    def get_account(self, account_id:str=None):
        return self.book_adapter.get_account(account_id=account_id)

    def enter_order(self, account: Account, order: Order, estimator:Estimator=None):
        return self.market_adapter.enter_order(account=account, order=order, estimator=estimator)





