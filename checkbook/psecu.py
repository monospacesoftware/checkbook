import re
from typing import List

from checkbook.transaction import Transaction
from checkbook.transaction_source import TransactionSource


class Psecu(TransactionSource):

    def parse_line(self, cols: List[str]) -> Transaction:
        date = cols[0].strip()
        if not date:
            raise ValueError(f"Missing date: {cols}")

        desc = cols[1].strip()
        if not desc:
            raise ValueError(f"Missing description: {cols}")

        type_re = re.compile('(?:(Withdrawal|Deposit) )?(.*)').match(desc)
        if not type_re:
            raise ValueError(f"Unexpected description format {desc}: {cols}")

        tran_type = type_re.group(1).lower() if type_re.group(1) else None
        desc = type_re.group(2)

        amt = cols[2].strip()
        if not amt:
            #raise ValueError(f"Missing amount: {cols}")
            #print(f"Skipping due to missing amount: {cols}")
            return None

        try:
            amt = float(amt)
        except:
            raise ValueError(f"Invalid amount '{amt}': {cols}")
        
        if tran_type == 'withdrawal' and amt >= 0:
            raise ValueError(f"Invalid withdrawal: expecting negative amount but got '{amt}': {cols}")

        if tran_type == 'deposit' and amt <= 0:
            raise ValueError(f"Invalid deposit: expecting positive amount but got '{amt}': {cols}")

        desc = desc.rstrip().lstrip()

        return Transaction(date=date,
                           amt=amt,
                           desc=desc)
