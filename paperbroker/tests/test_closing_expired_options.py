import unittest

from ..assets import *
from ..positions import Position
from .TestDataQuoteAdapter import TestDataQuoteAdapter
from ..PaperBroker import PaperBroker
from ..accounts import Account

#from ..adapters.markets.PaperMarketAdapter import

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

class TestClosingExpiredOptions(unittest.TestCase):

    def setUp(self):
        self.quote_adapter = TestDataQuoteAdapter()
        pass

    def test_will_not_close_if_not_expired(self):
        self.quote_adapter.recorded_date = '2017-01-27'
        broker = PaperBroker(quote_adapter=self.quote_adapter)
        account = Account([
            Position(asset='AAL170127P00048000', quantity=-1, cost_basis=(0.65 + 0.74)/2)
        ])
        broker.market_adapter.expire_options(account, broker.quote_adapter)

        self.assertTrue(len(account.positions) == 1)
        self.assertTrue(account.positions[0].asset == 'AAL170127P00048000')
        self.assertTrue(account.positions[0].quantity == -1)

    def test_otm_long_call(self):
        """
        symbol  recorded_date  bid       ask
        AAL     2017-01-27     47.3500   47.3700
        AAL     2017-01-28     46.9000   47.0000
        """
        self.quote_adapter.recorded_date = '2017-01-28'
        broker = PaperBroker(quote_adapter=self.quote_adapter)
        account = Account([
            Position(asset='AAL170127C00048000', quantity=1, cost_basis=0.08)
        ])
        account.cash = 10000
        broker.market_adapter.expire_options(account, broker.quote_adapter)

        self.assertTrue(len(account.positions) == 0)
        self.assertTrue(account.cash==10000)

    def test_itm_long_call(self):
        """
        symbol  recorded_date  bid       ask
        AAL     2017-01-27     47.3500   47.3700
        AAL     2017-01-28     46.9000   47.0000
        """
        self.quote_adapter.recorded_date = '2017-01-28'
        broker = PaperBroker(quote_adapter=self.quote_adapter)
        account = Account([
            Position(asset='AAL170127C00046000', quantity=1, cost_basis=(1.30 + 1.46) / 2)
        ])
        account.cash = 10000
        broker.market_adapter.expire_options(account, broker.quote_adapter)

        self.assertTrue(len(account.positions) == 1)
        self.assertEqual(account.positions[0].asset, 'AAL')
        self.assertEqual(account.positions[0].quantity, 100)
        self.assertTrue(account.cash==10000 - 46 * 100)


    def test_otm_long_put(self):
        """
        symbol  recorded_date  bid       ask
        AAL     2017-01-27     47.3500   47.3700
        AAL     2017-01-28     46.9000   47.0000
        """
        self.quote_adapter.recorded_date = '2017-01-28'
        broker = PaperBroker(quote_adapter=self.quote_adapter)
        account = Account([
            Position(asset='AAL170127P00046000', quantity=1, cost_basis=0.05)
        ])
        account.cash = 10000
        broker.market_adapter.expire_options(account, broker.quote_adapter)

        self.assertTrue(len(account.positions) == 0)
        self.assertTrue(account.cash==10000)


    def test_itm_long_put(self):
        """
        symbol  recorded_date  bid       ask
        AAL     2017-01-27     47.3500   47.3700
        AAL     2017-01-28     46.9000   47.0000
        """
        self.quote_adapter.recorded_date = '2017-01-28'
        broker = PaperBroker(quote_adapter=self.quote_adapter)
        account = Account([
            Position(asset='AAL170127P00048000', quantity=1, cost_basis=(0.65 + 0.74) / 2)
        ])
        account.cash = 10000
        broker.market_adapter.expire_options(account, broker.quote_adapter)

        self.assertTrue(len(account.positions) == 1)
        self.assertEqual(account.positions[0].asset, 'AAL')
        self.assertEqual(account.positions[0].quantity, -100)
        self.assertTrue(account.cash==10000 + 48 * 100)


    def test_otm_short_naked_call(self):
        """
        symbol  recorded_date  bid       ask
        AAL     2017-01-27     47.3500   47.3700
        AAL     2017-01-28     46.9000   47.0000
        """
        self.quote_adapter.recorded_date = '2017-01-28'
        broker = PaperBroker(quote_adapter=self.quote_adapter)
        account = Account([
            Position(asset='AAL170127C00048000', quantity=-1, cost_basis=0.08)
        ])
        account.cash = 10000
        broker.market_adapter.expire_options(account, broker.quote_adapter)

        self.assertTrue(len(account.positions) == 0)
        self.assertTrue(account.cash==10000)


    def test_itm_short_naked_call(self):
        """
        symbol  recorded_date  bid       ask
        AAL     2017-01-27     47.3500   47.3700
        AAL     2017-01-28     46.9000   47.0000
        """
        self.quote_adapter.recorded_date = '2017-01-28'
        broker = PaperBroker(quote_adapter=self.quote_adapter)
        account = Account([
            Position(asset='AAL170127C00046000', quantity=-1, cost_basis=(1.30 + 1.46) / 2)
        ])
        account.cash = 10000
        broker.market_adapter.expire_options(account, broker.quote_adapter)

        self.assertTrue(len(account.positions) == 0)
        #self.assertNotIsInstance(account.positions[0].asset, Option)
        #self.assertEqual(account.positions[0].quantity, -100)
        self.assertTrue(account.cash==10000 - (46.95 - 46) * 100)


    def test_otm_short_naked_put(self):
        """
        symbol  recorded_date  bid       ask
        AAL     2017-01-27     47.3500   47.3700
        AAL     2017-01-28     46.9000   47.0000
        """
        self.quote_adapter.recorded_date = '2017-01-28'
        broker = PaperBroker(quote_adapter=self.quote_adapter)
        account = Account([
            Position(asset='AAL170127P00046000', quantity=-1, cost_basis=0.05)
        ])
        account.cash = 10000
        broker.market_adapter.expire_options(account, broker.quote_adapter)

        self.assertTrue(len(account.positions) == 0)
        self.assertTrue(account.cash==10000)


    def test_itm_short_naked_put(self):
        """
        symbol  recorded_date  bid       ask
        AAL     2017-01-27     47.3500   47.3700
        AAL     2017-01-28     46.9000   47.0000
        """
        self.quote_adapter.recorded_date = '2017-01-28'
        broker = PaperBroker(quote_adapter=self.quote_adapter)
        account = Account([
            Position(asset='AAL170127P00048000', quantity=-1, cost_basis=(0.65 + 0.74) / 2)
        ])
        account.cash = 10000
        broker.market_adapter.expire_options(account, broker.quote_adapter)

        self.assertTrue(len(account.positions) == 0)
        self.assertTrue(account.cash==10000 + (48-46.95) * 100)



    def test_otm_short_covered_call(self):
        """
        symbol  recorded_date  bid       ask
        AAL     2017-01-27     47.3500   47.3700
        AAL     2017-01-28     46.9000   47.0000
        """
        self.quote_adapter.recorded_date = '2017-01-28'
        broker = PaperBroker(quote_adapter=self.quote_adapter)
        account = Account([
            Position(asset='AAL170127C00048000', quantity=-1, cost_basis=0.08),
            Position(asset='AAL', quantity=102, cost_basis=47.36)
        ])
        account.cash = 10000
        broker.market_adapter.expire_options(account, broker.quote_adapter)

        self.assertTrue(len(account.positions) == 1)
        self.assertEqual(account.positions[0].quantity, 102)
        self.assertTrue(account.cash==10000)


    def test_itm_short_covered_call(self):
        """
        symbol  recorded_date  bid       ask
        AAL     2017-01-27     47.3500   47.3700
        AAL     2017-01-28     46.9000   47.0000
        """
        self.quote_adapter.recorded_date = '2017-01-28'
        broker = PaperBroker(quote_adapter=self.quote_adapter)
        account = Account([
            Position(asset='AAL170127C00046000', quantity=-1, cost_basis=(1.30 + 1.46) / 2),
            Position(asset='AAL', quantity=102, cost_basis=47.36)
        ])
        account.cash = 10000
        broker.market_adapter.expire_options(account, broker.quote_adapter)

        self.assertTrue(len(account.positions) == 1)
        self.assertEqual(account.positions[0].quantity, 2)
        self.assertTrue(account.cash==10000)

    def test_otm_short_covered_put(self):
        """
        symbol  recorded_date  bid       ask
        AAL     2017-01-27     47.3500   47.3700
        AAL     2017-01-28     46.9000   47.0000
        """
        self.quote_adapter.recorded_date = '2017-01-28'
        broker = PaperBroker(quote_adapter=self.quote_adapter)
        account = Account([
            Position(asset='AAL170127P00046000', quantity=-1, cost_basis=0.05),
            Position(asset='AAL', quantity=-102, cost_basis=47.36)
        ])
        account.cash = 10000
        broker.market_adapter.expire_options(account, broker.quote_adapter)

        self.assertTrue(len(account.positions) == 1)
        self.assertEqual(account.positions[0].asset, 'AAL')
        self.assertEqual(account.positions[0].quantity, -102)
        self.assertTrue(account.cash==10000)


    def test_itm_short_covered_put(self):
        """
        symbol  recorded_date  bid       ask
        AAL     2017-01-27     47.3500   47.3700
        AAL     2017-01-28     46.9000   47.0000
        """
        self.quote_adapter.recorded_date = '2017-01-28'
        broker = PaperBroker(quote_adapter=self.quote_adapter)
        account = Account([
            Position(asset='AAL170127P00048000', quantity=-1, cost_basis=(0.65 + 0.74) / 2),
            Position(asset='AAL', quantity=-102, cost_basis=47.36)
        ])
        account.cash = 10000
        broker.market_adapter.expire_options(account, broker.quote_adapter)

        self.assertTrue(len(account.positions) == 1)
        self.assertEqual(account.positions[0].asset, 'AAL')
        self.assertEqual(account.positions[0].quantity, -2)
        self.assertTrue(account.cash==10000 - 46.95*100)




if __name__ == '__main__':
    unittest.main()