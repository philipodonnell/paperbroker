import unittest

from .TestDataQuoteAdapter import TestDataQuoteAdapter
from ..PaperBroker import PaperBroker
from ..orders import Order
from ..estimators import MidpointEstimator
from ..logic.fill_order import fill_order
from ..accounts import Account

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

class TestFillOrder(unittest.TestCase):

    #    def __init__(self):

    #        super(TestGetQuotes, self).__init__()

    def setUp(self):
        self.quote_adapter = TestDataQuoteAdapter()
        pass

    def test_ordering(self):
        self.quote_adapter.recorded_date = '2017-01-27'
        broker = PaperBroker(quote_adapter=self.quote_adapter)

        asset = 'AAL'

        # AAL170203P00046500  2017-01-27     0.4900   0.5300 mid: 0.51
        # AAL170203P00046500  2017-01-28     0.5800   0.6400 mid: 0.61
        # AAL170203P00047500  2017-01-27     0.9100   0.9700 mid: 0.94
        # AAL170203P00047500  2017-01-28     1.0700   1.1300 mid: 1.10

        option1 = 'AAL170203P00046500'
        option2 = 'AAL170203P00047500'

        a = Account()
        a.cash = 1000

        o = Order()
        o.add_leg(asset=option1, quantity=1, order_type='bto')
        a=fill_order(account=a, order=o, quote_adapter=self.quote_adapter, estimator=MidpointEstimator())

        self.assertAlmostEqual(a.cash, 1000 - 0.51 * 100, places=2)
        assert len(a.positions) == 1
        assert a.positions[0].asset == option1
        assert a.positions[0].quantity == 1
        assert a.positions[0].cost_basis == 0.51

        o = Order()
        o.add_leg(asset=option2, quantity=-2, order_type='sto')
        a=fill_order(account=a, order=o, quote_adapter=self.quote_adapter, estimator=MidpointEstimator())

        self.assertAlmostEqual(a.cash, 1000 - 0.51 * 100 + 0.94 * 100 * 2, places=2)
        assert len(a.positions) == 2
        assert a.positions[1].asset == option2
        assert a.positions[1].quantity == -2

        self.quote_adapter.recorded_date = '2017-01-28'

        o = Order()
        o.add_leg(asset=option2, quantity=1, order_type='btc')
        a=fill_order(account=a, order=o, quote_adapter=self.quote_adapter, estimator=MidpointEstimator())

        self.assertAlmostEqual(a.cash, 1000 - 0.51 * 100 + 0.94 * 100 * 2 - 1.10 * 100, places=2)
        assert len(a.positions) == 2
        assert a.positions[1].asset == option2
        assert a.positions[1].quantity == -1

        o = Order()
        o.add_leg(asset=option1, quantity=-1, order_type='stc')
        a=fill_order(account=a, order=o, quote_adapter=self.quote_adapter, estimator=MidpointEstimator())

        self.assertAlmostEqual(a.cash, 1000 - 0.51 * 100 + 0.94 * 100 * 2 - 1.10 * 100 + 0.61 * 100, places=2)

        assert len(a.positions) == 1
        assert a.positions[0].asset == option2
        assert a.positions[0].quantity == -1


if __name__ == '__main__':
    unittest.main()





