import arrow
from ...assets import asset_factory
from ...quotes import quote_factory


class QuoteAdapter:
    def get_quote(self, asset):
        raise NotImplementedError("QuoteAdapter.get_quote: You should subclass this and create an adapter.")

    def get_options(self, underlying_asset=None, expiration_date=None):
        raise NotImplementedError("QuoteAdapter.get_options: You should subclass this and create an adapter.")

    def get_expiration_dates(self, underlying_asset=None):
        raise NotImplementedError("QuoteAdapter.get_expiration_dates: You should subclass this and create an adapter.")

