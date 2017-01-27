from decimal import Decimal
from cost_basis.transaction import Transaction

class Account(object):
    def __init__(self, units, initial_balance=0, sigfigs=3):
        self.units = units
        self.inital_balance = initial_balance
        self.transactions = list()
        self.sigfigs=sigfigs
    # just a convenience function: it's fine to append transactions to the list
    def sort_transactions(self):
        self.transactions.sort(key = lambda x: x.date)
    def buy(self, date, in_quantity, from_quantity, from_units="USD"):
        self.transactions.append(
            Transaction(
                date,
                Transaction.float2decimal(in_quantity,  self.sigfigs),
                Transaction.float2decimal(from_quantity, 2),
                self.units,
                from_units
            )
        )
    def sell(self, date, out_quantity, to_quantity, to_units="USD"):
        current_average_cost = self.cost_basis_avg_method()/self.volume()
        sell_cost = to_quantity/out_quantity
        #print(sell_cost)
        self.transactions.append(
            Transaction(
                date,
                -1*Transaction.float2decimal(out_quantity, self.sigfigs),
                -1*Transaction.float2decimal(to_quantity, self.sigfigs),
                self.units,
                to_units
            )
        )
        return (sell_cost-float(current_average_cost))*out_quantity
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
    def cost_basis_avg_method(self, date=None):
        # cost basis, by the average cost method, is the average price you _paid_ for all shares, ever
        # times the number of shares you currently have
        # converting to a list because we're going to have to traverse more than once.
        transactions_filtered = list(self.filter_transactions_by_date(date))
        total_paid = sum(x.sell_quantity for x in transactions_filtered if x.sell_quantity > 0)
        total_bought = sum(x.buy_quantity for x in transactions_filtered if x.sell_quantity > 0)
        average_price_paid = total_paid/total_bought
        # print(average_price_paid)
        total_held = self.volume(date)
        return total_held*average_price_paid

    def unrealized_capital_gains(self, price, date=None):
        #transactions_filtered = self.filter_transactions_by_date(date)
        cost_basis = self.cost_basis_avg_method(date)
        price = Transaction.float2decimal(price,2)
        return price*self.volume()-cost_basis
