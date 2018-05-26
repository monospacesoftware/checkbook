import sys
from typing import List, Set

import yaml

from checkbook.transaction_source import Transaction, TransactionSource


class Database:

    def __init__(self):
        self.trans = self.load()

    def load(self) -> Set[Transaction]:
        trans = set()
        with open('database.yml', 'r') as yml_file:
            input = yaml.load(yml_file)
            if input:
                for entry in input:
                    tran = Transaction(date=entry['date'],
                                       desc=entry['desc'],
                                       amt=entry['amt'],
                                       cat=entry['cat'],
                                       memo=entry['memo'],
                                       acct=entry['acct'])
                    trans.add(tran)
        return trans

    def save(self) -> None:
        sorted_trans = list(self.trans)
        sorted_trans.sort(key=lambda t: str(t))
        output = []
        for tran in sorted_trans:
            entry = {'date': tran.date,
                     'desc': tran.desc,
                     'amt': tran.amt,
                     'cat': tran.cat,
                     'memo': tran.memo,
                     'acct': tran.acct}
            output.append(entry)
        with open('database.yml', 'w') as yml_file:
            yaml.dump(output, yml_file)

    def add(self, tran: Transaction) -> None:
        self.trans.add(tran)

    def __len__(self):
        return len(self.trans)

    def __iter__(self):
        return self.trans.__iter__()

    def __next__(self):
        return self.trans.__next__()

    def get_all_cats(self):
        cats = set()
        for tran in self:
            cat = tran.cat or "Uncategorized"
            cats.add(cat)
        return sorted(list(cats))
