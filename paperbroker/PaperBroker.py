from .adapters.quotes import QuoteAdapter
from .adapters.quotes import GoogleFinanceQuoteAdapter

from .adapters.accounts import AccountAdapter
from .adapters.accounts import LocalFileSystemAccountAdapter


from .accounts import Account




class PaperBroker():

    def __init__(self, quote_adapter:QuoteAdapter=None, book_adapter:AccountAdapter=None):
        self.quote_adapter = quote_adapter if quote_adapter is not None else GoogleFinanceQuoteAdapter()
        self.book_adapter = book_adapter if book_adapter is not None else LocalFileSystemAccountAdapter()

    def get_price(self, asset):
        quote = self.get_quote(asset)
        return quote.price if quote is not None else None

    def get_quote(self, asset):
        return self.quote_adapter.get_quote(asset)

    def get_option_quotes(self, underlying_asset, params:dict=None):
        return self.quote_adapter.get_option_quotes(underlying_asset=underlying_asset, params=params)

    def open_account(self):
        account = Account()
        self.book_adapter.put_account(account)
        return account

    def get_account(self, account_id:str=None):
        return self.book_adapter.get_account(account_id=account_id)




