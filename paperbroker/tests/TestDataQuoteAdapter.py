import arrow
from ..assets import asset_factory, Option
from ..quotes import Quote, OptionQuote
from ..adapters.quotes.QuoteAdapter import QuoteAdapter
import gzip
import os
import csv
from ..logic.ivolat3_option_greeks import get_option_greeks

"""
    An adapter that uses the included test dataset at /tests/test_data/data.csv.gz

    Data includes all quotes for the underlyings and options on the following dates:
    AAL between 2017-01-27 and 2017-01-28 (Jan expiration + earnings) and between 2017-03-24 and 2017-03-25 (March expiration)
    GOOG between 2017-01-27 and 2017-01-28 (Jan expiration) and between 2017-03-24 and 2017-03-25 (March expiration)

    Data is csv/gzip in the format [symbol],[current_date],[bid],[ask]

    A selection of data is included below for easy reference to prevent needing to
      open the file for math. Note that prices are as recorded @ approx 11am EST.

        Test data sample:

        Underlying quote of AAL was

        symbol  current_date  bid       ask
        AAL     2017-01-27     47.3500   47.3700
        AAL     2017-01-28     46.9000   47.0000

        Sample options prices

        symbol              current_date  bid      ask
        AAL170203P00045500  2017-01-27     0.2400   0.2700
        AAL170203P00045500  2017-01-28     0.2800   0.3200
        AAL170203P00046000  2017-01-27     0.3500   0.3800
        AAL170203P00046000  2017-01-28     0.4100   0.4600
        AAL170203P00046500  2017-01-27     0.4900   0.5300
        AAL170203P00046500  2017-01-28     0.5800   0.6400
        AAL170203P00047000  2017-01-27     0.6800   0.7200
        AAL170203P00047000  2017-01-28     0.7900   0.8600
        AAL170203P00047500  2017-01-27     0.9100   0.9700
        AAL170203P00047500  2017-01-28     1.0700   1.1300
        AAL170203P00048000  2017-01-27     1.1800   1.2500
        AAL170203P00048000  2017-01-28     1.3900   1.4500
        AAL170203P00048500  2017-01-27     1.5000   1.5900
        AAL170203P00048500  2017-01-28     1.7600   1.8300

    Set the date you would like quotes for by setting the self.current_date property

"""

if 'testdata_keyvalue_cache' not in globals():
    testdata_keyvalue_cache = None



class TestDataQuoteAdapter(QuoteAdapter):

    def __init__(self, current_date='2017-03-24'):
        self.current_date = arrow.get(current_date).format('YYYY-MM-DD')


    def load_testdata_cache(self):
        global testdata_keyvalue_cache
        testdata_keyvalue_cache = {}
        filename = os.path.join(os.path.dirname(__file__), 'test_data\\data.csv.gz')
        with gzip.open(filename, 'rt') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                if 'AAL' in row[0]:
                    asset = asset_factory(row[0])
                    if isinstance(asset, Option):
                        oq = OptionQuote(quote_date = row[1], asset = row[0], bid=row[2], ask=row[3])
                        if oq.price:
                            underlying = oq.asset.underlying
                            greeks = get_option_greeks(option_type=oq.asset.option_type,
                                                       underlying_price=testdata_keyvalue_cache.get(underlying.symbol + arrow.get(oq.quote_date).format('YYYY-MM-DD')).price,
                                                       days_to_expiration=oq.days_to_expiration,
                                                       strike=oq.asset.strike,
                                                       price=oq.price,
                                                       dividend=0.0)
                            greeks = greeks if greeks is not None else {}
                            oq.iv = greeks.get('iv', None)
                            oq.delta = greeks.get('delta', None)
                            oq.gamma = greeks.get('gamma', None)
                            oq.vega = greeks.get('vega', None)
                            oq.theta = greeks.get('theta', None)
                            oq.rho = greeks.get('rho', None)

                        testdata_keyvalue_cache[row[0] + row[1]] = oq

                    else:
                        testdata_keyvalue_cache[row[0] + row[1]] = Quote(quote_date=row[1], asset=row[0], bid=row[2], ask=row[3])

    def get_quote(self, asset):
        global testdata_keyvalue_cache

        asset = asset_factory(asset)

        if testdata_keyvalue_cache is None:
            self.load_testdata_cache()

        if testdata_keyvalue_cache.get(asset.symbol + arrow.get(self.current_date).format('YYYY-MM-DD'), None) is not None:
            return testdata_keyvalue_cache.get(asset.symbol + arrow.get(self.current_date).format('YYYY-MM-DD'))

        return None

    def get_options(self, underlying_asset=None, expiration_date=None):
        global testdata_keyvalue_cache

        if testdata_keyvalue_cache is None:
            self.load_testdata_cache()

        return [quote for quote in testdata_keyvalue_cache.values()
                if isinstance(quote, OptionQuote)
                and quote.quote_date == self.current_date
                and quote.asset.underlying == (underlying_asset if underlying_asset is not None else quote.asset.underlying)
                and quote.asset.expiration_date == (expiration_date if expiration_date is not None else quote.asset.expiration_date)
        ]


    def get_expiration_dates(self, underlying_asset=None):
        return sorted(list(set([quote.asset.expiration_date for quote in self.get_options(underlying_asset)])))


