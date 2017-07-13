import unittest
import arrow
from .TestDataQuoteAdapter import TestDataQuoteAdapter
from ..PaperBroker import PaperBroker
from ..accounts import Account
from ..logic.maintenance_margin import get_maintenance_margin
from ..positions import Position
from ..assets import Asset, Option, Call, Put


class TestMaintenanceMargins(unittest.TestCase):

    #    def __init__(self):

    #        super(TestGetQuotes, self).__init__()

    def setUp(self):
        self.quote_adapter = TestDataQuoteAdapter()
        pass

    def test_get_maintenance_margin(self):
        self.quote_adapter.current_date = '2017-01-27'
        positions = [
            Position(asset=Asset('AAL'), quantity=100),
            Position(asset=Call(underlying='AAL', strike=5, expiration_date=arrow.now()),
                     quantity=-2),
            Position(asset=Call(underlying='AAL', strike=10, expiration_date=arrow.now()),
                     quantity=3),
            Position(asset=Call(underlying='AAL', strike=15, expiration_date=arrow.now()),
                     quantity=-4),
            Position(asset=Call(underlying='AAL', strike=25, expiration_date=arrow.now()),
                     quantity=2)
        ]

        assert get_maintenance_margin(positions=positions, quote_adapter=self.quote_adapter) == 2500


if __name__ == '__main__':
    unittest.main()