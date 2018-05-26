import re
from os import listdir
from os.path import isfile

from checkbook.chase import Chase
from checkbook.database import Database
from checkbook.psecu import Psecu
from checkbook.transaction_source import TransactionSource


class Loader:

    @classmethod
    def load_incoming(cls, db: Database):
        chase = Chase()
        psecu = Psecu()
        for path in cls.list_incoming_files():
            if re.match(".*chase.*", path, re.IGNORECASE):
                cls.load_trans(path, chase, db, "2_Amazon Credit Card")
            elif re.match(".*psecu.*", path, re.IGNORECASE):
                cls.load_trans(path, psecu, db, "1_PSECU Joint Checking")
            else:
                print(f"Skipping unrecognized file {path}")

    @classmethod
    def load_trans(cls, path: str, source: TransactionSource, db: Database, acct_name: str):
        for tran in source.load(path, acct_name):
            db.add(tran)

    @classmethod
    def list_incoming_files(cls):
        paths = []
        for file_name in listdir('incoming'):
            path = f"incoming/{file_name}"
            if not isfile(path):
                continue
            paths.append(path)
        return paths
