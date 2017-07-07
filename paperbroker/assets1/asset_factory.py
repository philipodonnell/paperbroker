from .Asset import Asset
from .Put import Put
from .Call import Call

def asset_factory(symbol=None):
    """
        Create the appropriate asset based on the symbol.
    :param symbol: Case-insensitive symbol for the asset being created
    :return: An object that's a subclass of Asset or None
    """

    if symbol is None:
        return None

    if isinstance(symbol, Asset):
        return symbol

    symbol = symbol.upper()

    if len(symbol) > 8:
        if 'P0' in symbol:
            return Put(symbol)
        elif 'C0' in symbol:
            return Call(symbol)
        else:
            return Asset(symbol)
    else:
        return Asset(symbol)


