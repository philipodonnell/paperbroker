import arrow
from ...assets import asset_factory
from ...quotes import quote_factory
from .QuoteAdapter import QuoteAdapter
from googlefinance import getQuotes

"""
    Get current prices from Google Finance
"""
class GoogleFinanceQuoteAdapter(QuoteAdapter):

    def get_quote(self, asset, quote_date=None, estimator=None):
        # quote_date is ignored for this adapter

        asset = asset_factory(asset)
        google_quotes = getQuotes(asset.symbol)

        if google_quotes is None or len(google_quotes) == 0:
            raise Exception("GoogleFinanceAdapter.get_quote: No quote found for {}".format(asset.symbol))

        last_trade = google_quotes[0].get('LastTradeWithCurrency', None)
        if last_trade is None or last_trade == '':
            raise Exception("GoogleFinanceAdapter.get_quote: No quote found for {}".format(asset.symbol))

        return quote_factory(quote_date=arrow.now().format('YYYY-MM-DD'), asset=asset, estimator=estimator)


