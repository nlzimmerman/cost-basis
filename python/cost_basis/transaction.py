import datetime
from decimal import Decimal

class Transaction(object):
    def __init__(self, date, buy_quantity, sell_quantity, buy_units, sell_units = "USD", lot_number=None):
        # convention: buy_quantity and sell_quantity are both positive when a transaction is INTO an account
        # (i.e., I buy 1 VFIAX for 200 USD), and they are both negative when a transaction is OUT OF an account
        # second convention: Transactions have dates but not times; we aren't going to tell you your cost basis on
        # a sub-daily basis. This is because I'm in the habit of dealing with mutual funds. I could regret this later,
        # but it's cool to not have to think about timezones in the meantime.
        self.date = self.parse_date(date)
        self.buy_quantity = buy_quantity
        self.sell_quantity = sell_quantity
        self.buy_units = buy_units
        self.sell_units = sell_units
        self.lot_number = lot_number

    def __repr__(self):
        if self.lot_number is None:
            return "T[{}, {}, ({})]".format(self.buy_quantity, self.sell_quantity, self.sell_quantity/self.buy_quantity)
        else:
            return "{}[{}, {}, ({})]".format(self.lot_number, self.buy_quantity, self.sell_quantity, self.sell_quantity/self.buy_quantity)
    @classmethod
    def from_exchange_rate(cls, date, sell_quantity, exchange_rate, buy_units, sell_units = None):
        if sell_units is None:
            return cls(date, sell_quantity*exchange_rate, sell_quantity, buy_units)
        else:
            return cls(date, sell_quantity*exchange_rate, sell_quantity, buy_units, sell_units)

    @staticmethod
    def parse_date(d):
        if type(d) is datetime.date:
            return d
        elif type(d) is datetime.datetime:
            return d.date()
        elif type(d) is str:
            # convention: Dates can be written as YYYY-MM-DD, but not in any other way.
            return datetime.datetime.strptime(d, '%Y-%m-%d')
    @staticmethod
    def float2decimal(f, sigfigs=2):
        return Decimal('{1:0.{0}f}'.format(sigfigs, f))
