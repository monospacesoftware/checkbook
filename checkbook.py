import html
import re
from typing import List, Tuple

import sys

chase_tran_types = {'Sale': 'withdrawal',
                    'Payment': 'deposit'}

desc_re = re.compile("(?:(starts|ends|contains|equals|matches) )?(.*)", re.IGNORECASE)
amt_re = re.compile("(?:(lt|le|gt|ge|eq|ne) )?(.*)", re.IGNORECASE)

class Rule:
    def __init__(self,
                 desc:str,
                 desc_oper:str='starts',
                 amt:float=0,
                 amt_oper:str='ge',
                 cat:str=None,
                 desc_re=None):
        self.desc = desc
        self.desc_oper = desc_oper
        self.amt = amt
        self.amt_oper = amt_oper
        self.cat = cat
        self.desc_re = desc_re


class Transaction:
    def __init__(self,
                 date:str,
                 desc:str,
                 amt:float,
                 type:str=None,
                 cat:str=None,
                 memo:str=None,
                 acct:str=None):
        self.date = date
        self.desc = desc
        self.amt = amt
        self.type = type
        self.cat = cat
        self.memo = memo
        self.acct = acct

    def __repr__(self):
        return "\t".join([#self.type or '',
                          self.date or '',
                          str(self.amt or ''),
                          self.desc or '',
                          #self.cat or ''
        ])
        #return f"{self.type or ''}{\t{self.date or ''}\t{self.amt or ''}\t{self.desc or ''}\t{self.cat or ''}"


def load_rules() -> List[Rule]:
    import yaml
    with open('rules.yml') as yml_file:
        rules_by_category = yaml.load(yml_file)
        rules = []
        for category in rules_by_category.keys():
            category_rules = rules_by_category.get(category)
            count = 0
            for rule_dict in category_rules:
                count = count + 1

                desc = rule_dict.get('desc')
                if not desc:
                    print(f"Rule {count} in {category} is missing desc")
                    sys.exit(1)

                desc_match = desc_re.match(desc)
                if not desc_match:
                    print(f"Rule {desc} in {category} is does not fit expected format")
                    sys.exit(1)

                desc_oper = desc_match.group(1) or 'starts'
                desc = desc_match.group(2)

                amt = rule_dict.get('amt') or "0"

                amt_match = amt_re.match(amt)
                if not desc_match:
                    print(f"Rule {count} in {category} is has invalid amount '{amt}'")
                    sys.exit(1)

                amt_oper = amt_match.group(1) or 'ge'
                amt = amt_match.group(2)

                try:
                    amt = abs(float(amt))
                except:
                    print(f"Rule {count} in {category} is has invalid amount '{amt}'")
                    sys.exit(1)

                rule = Rule(desc=desc,
                            desc_oper=desc_oper,
                            amt=amt,
                            amt_oper=amt_oper,
                            cat=category)

                if not rule.desc:
                    print(f"Rule {count} in {category} is missing desc")
                    sys.exit(1)

                re_str = None
                if rule.desc_oper == 'starts':
                    re_str = f"{re.escape(rule.desc)}.*"
                elif rule.desc_oper == 'ends':
                    re_str = f".*{re.escape(rule.desc)}"
                elif rule.desc_oper == 'contains':
                    re_str = f".*{re.escape(rule.desc)}.*"
                elif rule.desc_oper == 'equals':
                    re_str = re.escape(re.escape(rule.desc))
                elif rule.desc_oper == 'matches':
                    re_str = rule.desc
                else:
                    print(f"Unrecognized desc_oper '{rule.desc_oper}'. Values are starts, ends, contains, equals, matches")
                    sys.exit(1)

                rule.desc_re = re.compile(re_str, re.IGNORECASE)
                if not rule.desc_re:
                    print(f"Invalid regular expression: {re_str}.")
                    sys.exit(1)

                rules.append(rule)

        print(f"Loaded {len(rules)} rules from rules.yml")
        return rules


def load_trans(file_name:str, acct_name:str, parser) -> List[Transaction]:
    import csv
    with open(file_name, newline='') as csv_file:
        trans = []
        reader = csv.reader(csv_file, quoting=0)
        next(reader) # skip header

        for cols in reader:
            tran = parser(cols)
            if not tran:
                print(f"Missing or unexpected data while loading {file_name}: {','.join(cols)}")
                sys.exit(1)

            tran.acct = acct_name
            trans.append(tran)

        print(f"Loaded {len(trans)} transactions from {file_name}")
        return trans


def parse_psecu(cols) -> Transaction:
    date = cols[0]
    if not date:
        print(f"Missing date: {cols}")
        sys.exit(1)

    desc = cols[1]
    if not desc:
        print(f"Missing description: {cols}")
        sys.exit(1)

    type_re = re.compile('(?:(Withdrawal|Deposit) )?(.*)').match(desc)
    if not type_re:
        print(f"Unexpected description format {desc}: {cols}")
        sys.exit(1)

    tran_type = type_re.group(1).lower() if type_re.group(1) else None
    desc = type_re.group(2)

    amt = cols[2]
    # if not amt:
    #     print(f"Missing amount: {cols}")
    #     sys.exit(1)

    if amt:
        try:
            amt = abs(float(amt))
        except:
            print(f"Invalid amount '{amt}': {cols}")
            sys.exit(1)

    desc = desc.rstrip().lstrip()

    return Transaction(type=tran_type,
                       date=date,
                       amt=amt,
                       desc=desc)


def load_psecu(file_name:str, acct_name:str) -> List[Transaction]:
    return load_trans(file_name, acct_name, parse_psecu)


def parse_chase(cols) -> Transaction:
    tran_type = chase_tran_types.get(cols[0])
    if not tran_type:
        print(f"Unrecognized transaction type '{cols[0]}': {cols}")
        sys.exit(1)

    date = cols[1]
    if not date:
        print(f"Missing date: {cols}")
        sys.exit(1)

    amt = cols[len(cols)-1]
    if not amt:
        print(f"Missing amount: {cols}")
        sys.exit(1)

    try:
        amt = abs(float(amt))
    except:
        print(f"Invalid amount '{amt}': {cols}")
        sys.exit(1)

    desc = " ".join(cols[3:len(cols)-1])
    if not desc:
        print(f"Missing description: {cols}")
        sys.exit(1)

    desc = html.unescape(desc)
    desc = desc.rstrip().lstrip()

    return Transaction(type=tran_type,
                       date=date,
                       amt=amt,
                       desc=desc)


def load_chase(file_name:str, acct_name:str) -> List[Transaction]:
    return load_trans(file_name, acct_name, parse_chase)


def assign_category(tran: Transaction, rules: List[Rule]) -> None:
    for rule in rules:
        amt_match = False if tran.amt else True
        if tran.amt:
            if rule.amt_oper == 'eq':
                amt_match = tran.amt == rule.amt
            elif rule.amt_oper == 'lt':
                amt_match = tran.amt < rule.amt
            elif rule.amt_oper == 'le':
                amt_match = tran.amt <= rule.amt
            elif rule.amt_oper == 'gt':
                amt_match = tran.amt > rule.amt
            elif rule.amt_oper == 'ge':
                amt_match = tran.amt >= rule.amt
            elif rule.amt_oper == 'ne':
                amt_match = tran.amt != rule.amt
            else:
                print(f"Unrecognized amt_oper: {rule.amt_oper}. Values are eq, lt, le, gt, te, ne.")
                sys.exit(1)

        if not amt_match:
            continue

        if rule.desc_re.match(tran.desc):
            tran.cat = rule.cat
            return


def process_trans(in_trans:List[Transaction], rules:List[Rule]) -> Tuple[List[Transaction], List[Transaction], List[Transaction]]:
    skipped = []
    uncat = []
    out = []
    for tran in in_trans:
        if tran.type == 'deposit':
            tran.cat = 'Deposit'

        assign_category(tran, rules)
        if tran.cat == 'SKIP':
            skipped.append(tran)
            continue

        if tran.type == 'withdrawal':
            tran.amt = tran.amt * -1

        if not tran.cat:
            uncat.append(tran)

        out.append(tran)

    return skipped, uncat, out


def print_trans(trans:List[Transaction], type:str) -> None:
    print()
    print(f"{len(trans)} {type} transactions:")
    for tran in trans:
        print(tran)


def write_ccb(trans: List[Transaction], file_name: str) -> None:
    with open(file_name, 'w') as out_file:
        out_file.write("Date,Amount,Description,Memo,Category,Account\n")
        for tran in trans:
            out_file.write(f"{tran.date or ''},{tran.amt or ''},{tran.desc or ''},{tran.memo or ''},{tran.cat or ''},{tran.acct or ''}\n")

    print()
    print(f"Wrote {len(trans)} transactions to {file_name}")
