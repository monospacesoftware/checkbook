import html
from typing import List

from checkbook.transaction import Transaction
from checkbook.transaction_source import TransactionSource


class Chase(TransactionSource):

    chase_tran_types = {'Sale': 'withdrawal',
                        'Payment': 'deposit',
                        'Refund': 'deposit',
                        'Return': 'deposit'}

    def parse_line(self, cols: List[str]) -> Transaction:
        tran_type = self.chase_tran_types.get(cols[0].strip())
        if not tran_type:
            raise ValueError(f"Unrecognized transaction type '{cols[0]}': {cols}")

        date = cols[1].strip()
        if not date:
            raise ValueError(f"Missing date: {cols}")

        amt_col = 4
        if len(cols) > 5 and cols[5]:
            found_amt = False
            for i in reversed(range(3, len(cols))):
                if cols[i]:
                    amt_col = i
                    break

        amt = cols[amt_col].strip()
        if not amt:
            raise ValueError(f"Missing amount: {cols}")

        try:
            amt = float(amt)
        except Exception as e:
            raise ValueError(f"Invalid amount '{amt}': {cols}")

        if tran_type == 'withdrawal' and amt >= 0:
            raise ValueError(f"Invalid withdrawal: expecting negative amount but got '{amt}': {cols}")

        if tran_type == 'deposit' and amt <= 0:
            raise ValueError(f"Invalid deposit: expecting positive amount but got '{amt}': {cols}")

        desc = " ".join(map(lambda s: s.strip(), cols[3:amt_col]))
        if not desc:
            raise ValueError(f"Missing description: {cols}")

        desc = html.unescape(desc)
        desc = desc.strip()

        return Transaction(date=date,
                           amt=amt,
                           desc=desc)
