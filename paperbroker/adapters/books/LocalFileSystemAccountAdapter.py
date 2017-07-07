from ...accounts import Account, account_factory
import tempfile
import os
import pickle
from os import listdir
from os.path import isfile, join

class LocalFileSystemBookAdapter():

    def __init__(self, root=None):
        if root is None: root = tempfile.gettempdir()
        if not os.path.exists(root+"/accounts/"):
            os.makedirs(root+"/accounts/")
        self.root = root

    def get_account(self, account_id: str, current_date=None):
        return pickle.load(file=self.root + "/accounts/" + account_id + ".pickle")

    def has_account(self, account_id: str, current_date=None):
        try:
            pickle.load(file=self.root + "/accounts/" + account_id + ".pickle")
            return True
        except:
            return False

    def put_account(self, account: Account, current_date=None):
        pickle.dump(account, file=self.root + "/accounts/" + account.account_id + ".pickle")

    def get_account_ids(self, current_date=None):
        mypath = self.root + "/accounts/"
        return [f.split(".")[0] for f in listdir(mypath) if isfile(join(mypath, f))]

    def delete_account(self, account, current_date=None):
        try:
            os.remove(self.root + "/accounts/" + account_factory(account).account_id + ".pickle")
        except:
            pass

    def delete_accounts(self, accounts, current_date=None):
        [self.delete_account(account) for account in accounts]
