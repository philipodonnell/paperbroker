import arrow
from ...assets import asset_factory
from ...quotes import quote_factory


class QuoteAdapter:
    def get_quote(self, asset):
        raise NotImplementedError("QuoteAdapter.get_quote: You should subclass this and create an adapter.")

    def get_option_quotes(self, underlying_asset, params:dict=None):
        raise NotImplementedError("QuoteAdapter.get_option_quotes: You should subclass this and create an adapter.")

