import unittest

from ..adapters.quotes import GoogleFinanceQuoteAdapter

class TestGoogleFinanceAdapter(unittest.TestCase):

    #    def __init__(self):

    #        super(TestGetQuotes, self).__init__()

    def test_get_quote(self):
        quote_adapter = GoogleFinanceQuoteAdapter()
        quote = quote_adapter.get_quote('GOOG')
        self.assertGreater(quote.price, 0)



if __name__ == '__main__':
    unittest.main()