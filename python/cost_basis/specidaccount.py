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
    def sell_first(self,  date, out_quantity, to_quantity, to_units="USD", lot_number = None):
        if lot_number is not None:
            raise Exception("sell_first is not compatible with specifying lot_number")
        out_quantity = Transaction.float2decimal(out_quantity, self.sigfigs)
        to_quantity = Transaction.float2decimal(to_quantity, 2)
        volume_to_sell = out_quantity
        # All lot numbers registered in the account
        lot_numbers = {x.lot_number for x in self.transactions}
        while volume_to_sell > 0:
            # find the oldest lot that has anything in it. Just this once we aren't bothering filtering
            # self.transactions since we are selling the oldest lots
            positive_lots = [lot_number for lot_number in lot_numbers
                               if sum(y.buy_quantity for y in self.transactions
                                      if y.lot_number==lot_number
                                      ) > 0
                                      ]
            # Then, of those lots, we find one with the oldest buy date
            # Find the oldest buy date
            oldest_buy_date = min(x.date for x in self.transactions
                                   if x.buy_quantity > 0
                                   and x.lot_number in positive_lots
                                   )
            # Sidebar: I really should have ideally used a data structure that I didn't
            # have to search all the time — writing Scala has ruined me.
            # It's not an error to have more than one oldest lot, but if that happens
            # We select one at random
            oldest_lot = [x.lot_number for x in self.transactions
                             if x.buy_quantity>0 and x.date==oldest_buy_date
                         ][0]
            # Whew. Now, we sell either the entire lot or the out_quantity
            lot_volume = sum(x.buy_quantity for x in self.transactions
                                              if x.lot_number == oldest_lot
                                              )
            volume_this_sale = min(lot_volume, out_quantity)
            to_quantity_this_sale = to_quantity*volume_this_sale/out_quantity
            # Using super and not self to avoid trouble if I clobber the sell() method later.
            super(SpecIDAccount, self).sell(date,
                                            volume_this_sale,
                                            to_quantity_this_sale,
                                            to_units,
                                            oldest_lot
                                            )
            volume_to_sell -= volume_this_sale

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
        sell_cost = float(to_quantity)/float(out_quantity)
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
