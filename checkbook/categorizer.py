import re
import sys
from typing import List, Tuple

from checkbook.database import Database
from checkbook.rule import Rule
from checkbook.transaction import Transaction


class Categorizer:

    desc_re = re.compile("(?:(starts|ends|contains|equals|matches) )?(.*)", re.IGNORECASE)
    amt_re = re.compile("(?:(lt|le|gt|ge|eq|ne) )?(.*)", re.IGNORECASE)
    rules = None

    @classmethod
    def get_rules(cls):
        if not cls.rules:
            cls.rules = cls.load_rules()
        return cls.rules

    @classmethod
    def load_rules(cls) -> List[Rule]:
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
                        raise ValueError(f"Rule {count} in {category} is missing desc")

                    desc_match = cls.desc_re.match(desc)
                    if not desc_match:
                        raise ValueError(f"Rule {desc} in {category} is does not fit expected format")

                    desc_oper = desc_match.group(1) or 'starts'
                    desc = desc_match.group(2)

                    amt = rule_dict.get('amt') or "0"

                    amt_match = cls.amt_re.match(amt)
                    if not desc_match:
                        raise ValueError(f"Rule {count} in {category} is has invalid amount '{amt}'")

                    amt_oper = amt_match.group(1) or 'ge'
                    amt = amt_match.group(2)

                    try:
                        amt = abs(float(amt))
                    except:
                        raise ValueError(f"Rule {count} in {category} is has invalid amount '{amt}'")

                    rule = Rule(desc=desc,
                                desc_oper=desc_oper,
                                amt=amt,
                                amt_oper=amt_oper,
                                cat=category)

                    if not rule.desc:
                        raise ValueError(f"Rule {count} in {category} is missing desc")

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
                        raise ValueError(f"Unrecognized desc_oper '{rule.desc_oper}'. Values are starts, ends, contains, equals, matches")

                    rule.desc_re = re.compile(re_str, re.IGNORECASE)
                    if not rule.desc_re:
                        raise ValueError(f"Invalid regular expression: {re_str}.")

                    rules.append(rule)

            print(f"Loaded {len(rules)} rules from rules.yml")
            return rules

    @classmethod
    def process_db(cls, db: Database):
        for tran in db:
            cat = cls.find_category(tran)
            if not cat:
                print(f"Uncategorized: {tran}")
                continue
            if cat == tran.cat:
                continue

            if tran.cat and tran.cat != cat:
                print(f"Recategorized from '{tran.cat}' to '{cat}': {tran}")
            #elif not tran.cat:
            #    print(f"Categorized as '{cat}': {tran}")

            tran.cat = cat

    @classmethod
    def find_category(cls, tran: Transaction) -> str:
        abs_amt = abs(tran.amt)

        for rule in cls.get_rules():
            amt_match = False if abs_amt else True
            if abs_amt:
                if rule.amt_oper == 'eq':
                    amt_match = abs_amt == rule.amt
                elif rule.amt_oper == 'lt':
                    amt_match = abs_amt < rule.amt
                elif rule.amt_oper == 'le':
                    amt_match = abs_amt <= rule.amt
                elif rule.amt_oper == 'gt':
                    amt_match = abs_amt > rule.amt
                elif rule.amt_oper == 'ge':
                    amt_match = abs_amt >= rule.amt
                elif rule.amt_oper == 'ne':
                    amt_match = abs_amt != rule.amt
                else:
                    raise ValueError(f"Unrecognized amt_oper: {rule.amt_oper}. Values are eq, lt, le, gt, te, ne.")

            if not amt_match:
                continue

            if rule.desc_re.match(tran.desc):
                return rule.cat

        if tran.amt > 0:
            return 'Deposit'

