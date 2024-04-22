class Field:
    id = None
    name = None
    street_id = None
    owner = None

    buy_price = None
    sell_price = None
    house_price = None
    hotel_price = None

    fees = []
    field_level = 0

    def __init__(self, id, name, street_id, buy_price, sell_price, house_price, hotel_price, fees):
        self.id = id
        self.name = name
        self.street_id = street_id
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.house_price = house_price
        self.hotel_price = hotel_price
        self.fees = fees

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_owner(self):
        return self.owner

    def set_owner(self, owner):
        self.owner = owner

    def get_buy_price(self):
        return self.buy_price

    def get_sell_price(self):
        return self.sell_price

    def get_house_price(self):
        return self.house_price

    def get_hotel_price(self):
        return self.hotel_price

    def get_street_id(self):
        return self.street_id

    def upgrade_by_building(self, money):
        if self.field_level == 0 or self.field_level == len(self.fees):
            return False, money
        if money < self.house_price:
            return False, money
        self.field_level += 1
        return True, money - self.house_price

    def upgrade_by_street(self):
        if self.field_level != 0:
            return False
        self.field_level += 1
        return True

    def downgrade(self):
        if self.field_level == 0:
            return False, self.sell_price
        self.field_level -= 1
        return True, self.house_price

    def downgrade_by_street(self):
        if self.field_level != 1:
            return False
        self.field_level -= 1
        return True

    def get_fee(self):
        return self.fees[self.field_level]

    def get_fees(self):
        return self.fees

    def get_field_level(self):
        return self.field_level

    def get_price(self):
        return self.buy_price
