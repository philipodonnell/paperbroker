import arrow
from ..assets import asset_factory
from ..quotes import quote_factory


class QuoteAdapter:
    def get_quote(self, asset, quote_date=None, estimator=None):
        """
            The only method on adapters. Pass in a symbol or Asset and get a quote.
            The default is to raise a NotImplemented exception
        :param asset:
        :param quote_date:
        :return: a Quote object
        """
        # something like this
        # asset = asset_factory(asset)
        # quote = quote_factory(quote_date, asset, estimator=estimator)
        # return quote
        raise NotImplementedError("QuoteAdapter.get_quote: You should subclass this and create an adapter.")
