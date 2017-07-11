import unittest

from .TestDataQuoteAdapter import TestDataQuoteAdapter
from ..PaperBroker import PaperBroker
from ..accounts import Account


class TestBookAdapterFunctionality(unittest.TestCase):

    #    def __init__(self):

    #        super(TestGetQuotes, self).__init__()

    def setUp(self):
        pass

    def test_get_create_new_account(self):
        broker = PaperBroker()
        account = broker.open_account()
        self.assertIsNotNone(account)

        broker = PaperBroker()
        account = broker.get_account(account_id=account.account_id)
        self.assertIsNotNone(account)
        self.assertIsInstance(account, Account)



if __name__ == '__main__':
    unittest.main()