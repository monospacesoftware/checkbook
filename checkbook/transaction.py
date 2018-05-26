class Transaction:

    def __init__(self,
                 date: str,
                 desc: str,
                 amt: float,
                 cat: str = None,
                 memo: str = None,
                 acct: str = None):
        self.date = date
        self.desc = desc
        self.amt = amt
        self.cat = cat
        self.memo = memo
        self.acct = acct

    def __str__(self):
        return "\t".join([  # self.type or '',
            self.date or '',
            str(self.amt or ''),
            self.desc or '',
            self.cat or '',
            self.memo or '',
            self.acct or '',
        ])
        # return f"{self.type or ''}{\t{self.date or ''}\t{self.amt or ''}\t{self.desc or ''}\t{self.cat or ''}"

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return False
        return self.date == other.date and self.desc == other.desc and self.amt == other.amt

    def __hash__(self):
        return hash((self.date, self.amt, self.desc))



