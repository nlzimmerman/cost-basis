from decimal import Decimal
from cost_basis.account import Account
from cost_basis.transaction import Transaction

class SpecIDAccount(Account):
    def __init__(self, *args, **kwargs):
        # Python2 compatability
        super(SpecIDAccount, self).__init__(*args, **kwargs)

    @property
    def account_type(self):
        return "SpecID"
    def check_and_make_buy_lot_number(self, lot_number):
        if lot_number is None:
            if len(self.transactions)==0:
                lot_number = 0
            else:
                lot_number = max(x.lot_number for x in self.transactions)+1
        else:
            # Check to make sure that this lot number hasn't been used before. Only necessary if you specified it
            if any((x.lot_number==lot_number and x.buy_quantity>0) for x in self.transactions):
                raise Exception("This lot number has already been used")
        return lot_number

    def realized_gains(self, out_quantity, to_quantity, to_units, lot_number, date=None):
        if lot_number is None:
            raise Exception("You must specify a lot number when selling!")
        transactions_filtered = list(self.filter_transactions_by_date(date))
        lot_volume = sum(x.buy_quantity for x in transactions_filtered if x.lot_number==lot_number)
        out_quantity = Transaction.float2decimal(out_quantity, self.sigfigs)
        to_quantity = Transaction.float2decimal(to_quantity, 2)
        if lot_volume<out_quantity:
            raise Exception("Can't sell more shares ({}) than are in the lot ({})!".format(out_quantity, lot_volume))
        [lot_cost] = [x.sell_quantity/x.buy_quantity for x in transactions_filtered if x.lot_number==lot_number and x.buy_quantity>0]
        sell_cost = to_quantity/out_quantity
        return (float(sell_cost)-float(lot_cost))*float(out_quantity)


    def unrealized_capital_gains(self, price, date=None):
        transactions_filtered = list(self.filter_transactions_by_date(date))
        # The unrealized capital gains are the shares remaining (i.e. not sold) in each lot,
        # times the price gain, summed over each lot
        lot_numbers = {x.lot_number for x in transactions_filtered}
        running_total = 0
        for lot_number in lot_numbers:
            # DRY this up; I copy/pasted this from a different function!
            lot_volume = sum(x.buy_quantity for x in transactions_filtered if x.lot_number==lot_number)
            [lot_cost] = [Transaction.float2decimal(x.sell_quantity/x.buy_quantity, 2) for x in transactions_filtered if x.lot_number==lot_number and x.buy_quantity>0]
            lot_gains = lot_volume * (Transaction.float2decimal(price,2)-lot_cost)
            running_total += lot_gains
        return running_total

    def cost_basis(self, date=None):
        # DRY this up (somehow, hm.)
        transactions_filtered = list(self.filter_transactions_by_date(date))
        lot_numbers = {x.lot_number for x in transactions_filtered}
        running_total = 0
        for lot_number in lot_numers:
            lot_volume = sum(x.buy_quantity for x in transactions_filtered if x.lot_number==lot_number)
            [lot_cost] = [Transaction.float2decimal(x.sell_quantity/x.buy_quantity, 2) for x in transactions_filtered if x.lot_number==lot_number and x.buy_quantity>0]
            running_total += lot_cost
        return running_total
