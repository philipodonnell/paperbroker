import arrow
from ...assets import asset_factory
from ...quotes import quote_factory
from .QuoteAdapter import QuoteAdapter
from googlefinance import getQuotes

"""
    Get current prices from Google Finance
"""
class GoogleFinanceQuoteAdapter(QuoteAdapter):

    def get_quote(self, asset):

        asset = asset_factory(asset)
        google_quotes = getQuotes(asset.symbol)

        if google_quotes is None or len(google_quotes) == 0:
            raise Exception("GoogleFinanceAdapter.get_quote: No quote found for {}".format(asset.symbol))

        last_trade = google_quotes[0].get('LastTradeWithCurrency', None)
        if last_trade is None or last_trade == '':
            raise Exception("GoogleFinanceAdapter.get_quote: No quote found for {}".format(asset.symbol))

        return quote_factory(quote_date=arrow.now().format('YYYY-MM-DD'), asset=asset, price=last_trade)

    def get_expiration_dates(self, underlying_asset=None):
        raise NotImplementedError("GoogleFinanceQuoteAdapter.get_option_quotes: Options quotes are not supported.")

    def get_options(self, underlying_asset=None, expiration_date=None):
        raise NotImplementedError("GoogleFinanceQuoteAdapter.get_options: Options quotes are not supported.")


