import sys
from abc import abstractmethod, ABCMeta
from typing import List

from checkbook.transaction import Transaction


class TransactionSource(metaclass=ABCMeta):

    def load(self, file_name: str, acct_name: str) -> List[Transaction]:
        import csv
        with open(file_name, newline='') as csv_file:
            trans = []
            reader = csv.reader(csv_file, quoting=0)
            next(reader)  # skip header

            for cols in reader:
                tran = self.parse_line(cols)
                if not tran:
                    #print(f"Missing or unexpected data while loading {file_name}: {','.join(cols)}")
                    continue

                if acct_name and not tran.acct:
                    tran.acct = acct_name

                trans.append(tran)

            print(f"Loaded {len(trans)} transactions from {file_name}")
            return trans

    @abstractmethod
    def parse_line(self, cols: List[str]) -> Transaction:
        raise NotImplementedError()
