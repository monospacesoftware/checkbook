import re

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
