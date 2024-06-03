import random


class Trade:
    def __init__(self, player_id1, player_id2, money1, money2, fields):
        self.player_id1 = player_id1
        self.player_id2 = player_id2
        self.money1 = money1
        self.money2 = money2
        self.fields = fields
        self.trade_id = self.generate_trade_id()

    def get_player_id1(self):
        return self.player_id1

    def get_player_id2(self):
        return self.player_id2

    def get_money1(self):
        return self.money1

    def get_money2(self):
        return self.money2

    def get_fields(self):
        return self.fields

    def get_trade_id(self):
        return self.trade_id
    
    def generate_trade_id(self):
        res = '1'
        for i in range(7):
            res += str(random.randint(0, 9))
        return res
