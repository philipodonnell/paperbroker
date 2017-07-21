import arrow

class QuoteAdapter:

    def __init__(self, current_date=None):
        self.set_current_date(current_date)

    def set_current_date(self, current_date):
        self._current_date = arrow.get(current_date).format('YYYY-MM-DD') if current_date is not None else None

    def get_current_date(self):
        return self._current_date if self._current_date else None

    @property
    def current_date(self):
        return self.get_current_date()

    def get_quote(self, asset):
        raise NotImplementedError("QuoteAdapter.get_quote: You should subclass this and create an adapter.")

    def get_options(self, underlying_asset=None, expiration_date=None):
        raise NotImplementedError("QuoteAdapter.get_options: You should subclass this and create an adapter.")

    def get_expiration_dates(self, underlying_asset=None):
        raise NotImplementedError("QuoteAdapter.get_expiration_dates: You should subclass this and create an adapter.")

