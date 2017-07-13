import arrow
from ...assets import asset_factory, Option
from ...quotes import OptionQuote, Quote
from .QuoteAdapter import QuoteAdapter
from googlefinance import getQuotes



"""
    Get current prices from Google Finance
"""
class GoogleFinanceQuoteAdapter(QuoteAdapter):

    def get_quote(self, asset):

        asset = asset_factory(asset)

        if isinstance(asset, Option):

            options = self.get_options(asset.underlying, asset.expiration_date)
            matches = [_ for _ in options if _.asset == asset]
            if len(matches) == 0:
                raise Exception("GoogleFinanceAdapter.get_quote: No quote found for {}".format(asset.symbol))
            return matches[0]

        else:

            google_quotes = getQuotes(asset.symbol)

            if google_quotes is None or len(google_quotes) == 0:
                raise Exception("GoogleFinanceAdapter.get_quote: No quote found for {}".format(asset.symbol))

            last_trade = google_quotes[0].get('LastTradeWithCurrency', None)
            if last_trade is None or last_trade == '' or last_trade == '-':
                raise Exception("GoogleFinanceAdapter.get_quote: No quote found for {}".format(asset.symbol))

            return Quote(quote_date=arrow.now().format('YYYY-MM-DD'), asset=asset, bid=float(last_trade)-0.01, ask=float(last_trade)+0.01)

    def get_expiration_dates(self, underlying_asset=None):
        oc = OptionChain('NASDAQ:' + asset_factory(underlying_asset).symbol)
        return list(set([asset_factory(_['s']).expiration_date for _ in (oc.calls + oc.puts)]))

    def get_options(self, underlying_asset=None, expiration_date=None):
        oc = OptionChain('NASDAQ:' + asset_factory(underlying_asset).symbol)
        underlying_quote = self.get_quote(underlying_asset)

        out = []
        for option in (oc.calls + oc.puts):
            if arrow.get(expiration_date).format('YYMMDD') in option['s']:
                quote = OptionQuote(quote_date=arrow.now().format('YYYY-MM-DD'),
                                asset=option['s'],
                                bid=float(option['b']) if option['b'] != '-' else None,
                                ask=float(option['a']) if option['a'] != '-' else None,
                                underlying_price = underlying_quote.price)
                out.append(quote)

        return out





# the code below is from https://github.com/makmac213/python-google-option-chain


import requests


OPTION_CHAIN_URL = 'https://www.google.com/finance/option_chain'


class OptionChain(object):

    def __init__(self, q):
        """
        Usage:
        from optionchain import OptionChain
        oc = OptionChain('NASDAQ:AAPL')
        # oc.calls
        # oc.puts
        """

        params = {
            'q': q,
            'output': 'json'
        }

        data = self._get_content(OPTION_CHAIN_URL, params)

        # get first calls and puts
        calls = data['calls']
        puts = data['puts']

        for (ctr, exp) in enumerate(data['expirations']):
            # we already got the first put and call
            # skip first
            if ctr:
                params['expd'] = exp['d']
                params['expm'] = exp['m']
                params['expy'] = exp['y']

                new_data = self._get_content(OPTION_CHAIN_URL, params)

                if new_data.get('calls') is not None:
                    calls += new_data.get('calls')

                if new_data.get('puts') is not None:
                    puts += new_data.get('puts')

        self.calls = calls
        self.puts = puts

    def _get_content(self, url, params):
        response = requests.get(url, params=params)
        if response.status_code == 200:
            content_json = response.content
            data = json_decode(content_json)

            return data

import json
import token, tokenize

from io import StringIO



# using below solution fixes the json output from google
# http://stackoverflow.com/questions/4033633/handling-lazy-json-in-python-expecting-property-name
def fixLazyJson (in_text):
    tokengen = tokenize.generate_tokens(StringIO(in_text.decode('ascii')).readline)

    result = []
    for tokid, tokval, _, _, _ in tokengen:
        # fix unquoted strings
        if (tokid == token.NAME):
            if tokval not in ['true', 'false', 'null', '-Infinity', 'Infinity', 'NaN']:
                tokid = token.STRING
                tokval = u'"%s"' % tokval

        # fix single-quoted strings
        elif (tokid == token.STRING):
            if tokval.startswith ("'"):
                tokval = u'"%s"' % tokval[1:-1].replace ('"', '\\"')

        # remove invalid commas
        elif (tokid == token.OP) and ((tokval == '}') or (tokval == ']')):
            if (len(result) > 0) and (result[-1][1] == ','):
                result.pop()

        # fix single-quoted strings
        elif (tokid == token.STRING):
            if tokval.startswith ("'"):
                tokval = u'"%s"' % tokval[1:-1].replace ('"', '\\"')

        result.append((tokid, tokval))

    return tokenize.untokenize(result)


def json_decode(json_string):
    try:
        ret = json.loads(json_string)
    except:
        json_string = fixLazyJson(json_string)
        ret = json.loads(json_string)
    return ret