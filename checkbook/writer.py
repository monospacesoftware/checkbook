import re
from os import listdir
from os.path import isfile

from checkbook.chase import Chase
from checkbook.database import Database
from checkbook.psecu import Psecu
from checkbook.transaction_source import TransactionSource


class Writer:

    @classmethod
    def write_master(cls, db: Database):
        sorted_trans = list(db)
        sorted_trans.sort(key=lambda t: str(t))
        with open("master.csv", 'w') as out_file:
            out_file.write("Date,Amount,Description,Memo,Category,Account\n")
            for tran in sorted_trans:
                out_file.write(
                    f"{tran.date or ''},{tran.amt or ''},{tran.desc or ''},{tran.memo or ''},{tran.cat or ''},{tran.acct or ''}\n")

        print(f"Wrote {len(db)} transactions to checkbook.csv")

    @classmethod
    def write_summary(cls, db: Database):
        months = {}
        for tran in db:
            parts = tran.date.split("/")
            month = "/".join([parts[0], parts[2]])
            cat = tran.cat or "Uncategorized"

            cats = months.get(month)
            if not cats:
                cats = {}
                months[month] = cats

            sum = cats.get(cat)
            if not sum:
                sum = 0

            sum += tran.amt
            cats[cat] = sum

        all_cats = db.get_all_cats()
        with open("summary.csv", 'w') as out_file:
            header = all_cats.copy()
            header.insert(0, "Month")
            print(",".join(header), file=out_file)
            for month in sorted(months):
                line = [month]
                for cat in all_cats:
                    sum = months.get(month).get(cat) or 0
                    line.append("%.2f" % sum)
                print(",".join(line), file=out_file)

        print(f"Wrote {len(db)} transactions to summary.csv")





