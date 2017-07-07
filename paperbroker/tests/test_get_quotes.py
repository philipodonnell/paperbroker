import unittest

from .TestDataQuoteAdapter import TestDataQuoteAdapter
from ..PaperBroker import PaperBroker

"""
    A selection of data is included below for easy reference to prevent needing to
      open the file for math. Note that prices are as recorded @ approx 11am EST.

        Test data sample:

        Underlying quote of AAL was

        symbol  recorded_date  bid       ask
        AAL     2017-01-27     47.3500   47.3700
        AAL     2017-01-28     46.9000   47.0000

        Sample options prices

        symbol              recorded_date  bid      ask
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


"""

class TestGetQuotes(unittest.TestCase):

    #    def __init__(self):

    #        super(TestGetQuotes, self).__init__()

    def setUp(self):
        self.quote_adapter = TestDataQuoteAdapter()
        pass

    def test_get_underlying_quote(self):
        self.quote_adapter.recorded_date = '2017-01-27'
        broker = PaperBroker(quote_adapter=self.quote_adapter)
        quote = broker.get_quote('AAL')

        self.assertIsNotNone(quote)
        self.assertAlmostEqual(quote.bid, 47.35, places=2)
        self.assertAlmostEqual(quote.ask, 47.37, places=2)
        self.assertAlmostEqual(quote.price, 47.36, places=2)


    def test_get_underlying_quote_on_different_date(self):
        self.quote_adapter.recorded_date = '2017-01-28'
        broker = PaperBroker(quote_adapter=self.quote_adapter)
        quote = broker.get_quote('AAL')

        self.assertIsNotNone(quote)
        self.assertAlmostEqual(quote.bid, 46.90, places=2)
        self.assertAlmostEqual(quote.ask, 47.00, places=2)
        self.assertAlmostEqual(quote.price, 46.95, places=2)


    def test_get_option_quote(self):
        self.quote_adapter.recorded_date = '2017-01-27'
        broker = PaperBroker(quote_adapter=self.quote_adapter)
        quote = broker.get_quote('AAL170203P00045500')

        self.assertIsNotNone(quote)
        self.assertAlmostEqual(quote.bid, 0.24, places=2)
        self.assertAlmostEqual(quote.ask, 0.27, places=2)
        self.assertAlmostEqual(quote.price, 0.255, places=3)

    def test_get_option_quotes(self):
        pass



if __name__ == '__main__':
    unittest.main()