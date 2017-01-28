from decimal import Decimal
from cost_basis.transaction import Transaction
from cost_basis.account import Account

class AverageAccount(Account):
    def __init__(self, *args, **kwargs):
        # Python2 compatability
        super(AverageAccount, self).__init__(*args, **kwargs)
    # just a convenience function: it's fine to append transactions to the list
    @property
    def account_type(self):
        return "AverageCostBasis"
    def check_and_make_buy_lot_number(self, lot_number):
        if lot_number is not None:
            raise Exception("Specifying lot numbers is explicitly disallowed for AverageAccount")
        else:
            return lot_number

    def realized_gains(self, out_quantity, to_quantity, to_units, lot_number, date=None):
        # Just running this for the exception generation
        self.check_and_make_buy_lot_number(lot_number)
        current_average_cost = self.__cost_basis_avg_method(date)/self.volume(date)
        sell_cost = to_quantity/out_quantity
        return (sell_cost-float(current_average_cost))*out_quantity
    def cost_basis(self, date=None):
        return self.__cost_basis_avg_method(date)
    def __cost_basis_avg_method(self, date=None):
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
        transactions_filtered = self.filter_transactions_by_date(date)
        cost_basis = self.__cost_basis_avg_method(date)
        price = Transaction.float2decimal(price,2)
        return price*self.volume()-cost_basis
