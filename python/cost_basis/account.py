from decimal import Decimal
from cost_basis.transaction import Transaction
import sys
# python2 is strictly inferior to python3, but I do try to write backward-compatible
# code
# via http://stackoverflow.com/questions/35673474/using-abc-abcmeta-in-a-way-it-is-compatible-both-with-python-2-7-and-python-3-5
# I'm pretty sure this would not work correctly on Python [3.0, 3.4) but
# I'm not that worried about it
import abc
from abc import abstractmethod, abstractproperty
if sys.version_info[0] < 3:
    ABC = abc.ABCMeta('ABC', (), {})
else:
    ABC = abc.ABC



class Account(ABC):
    def __init__(self, units, initial_balance=0, sigfigs=3):
        self.units = units
        self.inital_balance = initial_balance
        self.transactions = list()
        self.sigfigs=sigfigs
    # just a convenience function: it's fine to append transactions to the list
    @abstractmethod
    def check_and_make_buy_lot_number(self, lot_number):
        pass
    @abstractmethod
    def realized_gains(self, out_quantity, to_quantity, to_units, lot_number, date=None):
        pass
    @abstractmethod
    def unrealized_capital_gains(self, price, date=None):
        pass
    @abstractmethod
    def cost_basis(self, date=None):
        pass
    @abstractproperty
    def account_type(self):
        pass
    def sort_transactions(self):
        self.transactions.sort(key = lambda x: x.date)
    def buy(self, date, in_quantity, from_quantity, from_units="USD", lot_number = None):
        lot_number = self.check_and_make_buy_lot_number(lot_number)
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
        gains = self.realized_gains(out_quantity, to_quantity, to_units, lot_number, date)
        #print(sell_cost)
        self.transactions.append(
            Transaction(
                date,
                -1*Transaction.float2decimal(out_quantity, self.sigfigs),
                -1*Transaction.float2decimal(to_quantity, self.sigfigs),
                self.units,
                to_units,
                lot_number
            )
        )
        return gains
    # Not 100% sure that this will work correctly all the time with an AverageAccount
    # I seem to recall that you shouldn't be using equality checks with None but
    # Haven't looked that up again.
    def sell_all(self, date, to_quantity):
        sell_price = Transaction.float2decimal(to_quantity, 2)/self.volume(date)
        # DRY this up too, probably
        transactions_filtered = list(self.filter_transactions_by_date(date))
        lot_numbers = {x.lot_number for x in transactions_filtered}
        output = list()
        for lot in lot_numbers:
            lot_volume = sum(x.buy_quantity for x in transactions_filtered if x.lot_number==lot)
            if lot_volume > 0:
                output.append(self.sell(date, lot_volume, lot_volume*sell_price, lot_number=lot))
        return output

    def filter_transactions_by_date(self, date):
        if date is None:
            return self.transactions
        else:
            d = Transaction.parse_date(date)
            # This is a generator, so be sure to make a list if you need to iterate more than once.
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
