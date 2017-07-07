"""
Just a syntax sugar thing
"""
"""

AssetBase: Assets are always identified by a symbol which uniquely identifies the asset and a type.

"""

class AssetBase:
    def __init__(self, symbol: str=None, asset_type:str=None):
        self.symbol = symbol.upper()
        self.asset_type = asset_type
        return

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.symbol == other.symbol
        if isinstance(other, str):
            return self.symbol == other.upper()
        return False

    def __ne__(self, other):
        """Define a non-equality test"""
        return not self.__eq__(other)



class Asset(AssetBase):

    def __init__(self, symbol: str=None, asset_type: str=None):
        super(Asset, self).__init__(symbol, asset_type)
        return

