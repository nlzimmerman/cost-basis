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
            return datetime.datetime.strptime(d, '%Y-%M-%d')
    @staticmethod
    def float2decimal(f, sigfigs=2):
        return Decimal('{1:0.{0}f}'.format(sigfigs, f))

class SpecIDAccount(object):
    def __init__(self, units, initial_balance=0, sigfigs=3):
        self.units = units
        self.inital_balance = initial_balance
        self.transactions = list()
        self.sigfigs=sigfigs

    def buy(self, date, in_quantity, from_quantity, from_units="USD", lot_number=None):
        if lot_number is None:
            if len(self.transactions)==0:
                lot_number = 0
            else:
                lot_number = max(x.lot_number for x in self.transactions)+1
        else:
            # Check to make sure that this lot number hasn't been used before. Only necessary if you specified it
            if any((x.lot_number==lot_number and x.buy_quantity>0) for x in self.transactions):
                raise Exception("This lot number has already been used")
        self.transactions.append(
            Transaction(
                date,
                Transaction.float2decimal(in_quantity, self.sigfigs),
                Transaction.float2decimal(from_quantity, 2),
                self.units,
                from_units,
                lot_number
            )
        )

    def sell(self, date, out_quantity, to_quantity, to_units="USD", lot_number=None):
        # lot_number is not optional here!
        # First, let's see if this lot has enough shares left in it.
        if lot_number is None:
            raise Exception("You must specify a lot number when selling!")
        lot_volume = sum(x.buy_quantity for x in self.transactions if x.lot_number==lot_number)
        out_quantity = Transaction.float2decimal(out_quantity, self.sigfigs)
        to_quantity = Transaction.float2decimal(to_quantity, 2)
        if lot_volume<out_quantity:
            raise Exception("Can't sell more shares ({}) than are in the lot ({})!".format(out_quantity, lot_volume))
        [lot_cost] = [x.sell_quantity/x.buy_quantity for x in self.transactions if x.lot_number==lot_number and x.buy_quantity>0]
        sell_cost = to_quantity/out_quantity
        self.transactions.append(
            Transaction(
                date,
                -1*Transaction.float2decimal(out_quantity, self.sigfigs),
                -1*Transaction.float2decimal(to_quantity, 2),
                self.units,
                to_units,
                lot_number
            )
        )
        return (float(sell_cost)-float(lot_cost))*float(out_quantity)
    def sell_all(self, date, to_quantity):
        sell_price = Transaction.float2decimal(to_quantity, 2)/self.volume()
        # DRY this up too, probably
        lot_numbers = {x.lot_number for x in self.transactions}
        output = list()
        for lot in lot_numbers:
            lot_volume = sum(x.buy_quantity for x in self.transactions if x.lot_number==lot)
            if lot_volume > 0:
                output.append(self.sell(date, lot_volume, lot_volume*sell_price, lot_number=lot))
        return output

    def filter_transactions_by_date(self, date):
        if date is None:
            return self.transactions
        else:
            d = Transaction.parse_date(date)
            transactions_filtered = (x for x in self.transactions if x.date <= d)
            return transactions_filtered
    def money_in(self, date=None):
        transactions_filtered = self.filter_transactions_by_date(date)
        return sum(x.sell_quantity for x in transactions_filtered if x.sell_quantity>0)

    def money_out(self, date=None):
        transactions_filtered = self.filter_transactions_by_date(date)
        return sum(-1*x.sell_quantity for x in transactions_filtered if x.sell_quantity<0)

    def volume(self, date=None):
        # NB: Python has a weird (and kind of bad) feature that we are exploiting here, namely that
        # sum([]) = 0
        # where that 0 is an int
        transactions_filtered = self.filter_transactions_by_date(date)
        return sum(x.buy_quantity for x in transactions_filtered)
    def cost(self, date = None):
        if len(self.transactions)>0 and not all(x.sell_units == self.transactions[0].sell_units for x in self.transactions):
            raise Exception("Transactions don't all have the same sell_units, so we don't know how to calculate the cost basis yet.")
        transactions_filtered = self.filter_transactions_by_date(date)
        return sum(x.sell_quantity for x in transactions_filtered)

    def unrealized_capital_gains(self, price, date=None):
        transactions_filtered = list(self.filter_transactions_by_date(date))
        # The unrealized capital gains are the shares remaining (i.e. not sold) in each lot,
        # times the price gain, summed over each lot
        lot_numbers = {x.lot_number for x in self.transactions}
        running_total = 0
        for lot_number in lot_numbers:
            # DRY this up; I copy/pasted this from a different function!
            lot_volume = sum(x.buy_quantity for x in self.transactions if x.lot_number==lot_number)
            [lot_cost] = [x.sell_quantity/x.buy_quantity for x in self.transactions if x.lot_number==lot_number and x.buy_quantity>0]
            lot_gains = lot_volume * (Transaction.float2decimal(price,2)-lot_cost)
            running_total += lot_gains
        return running_total