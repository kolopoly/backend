class Field:
    MORTGAGE_TURNS = 5

    def __init__(self, id, rule):
        self.type = rule["type"]
        self.color = rule["color"]
        self.id = id
        self.name = rule["name"]
        self.owner = None
        self.field_level = 0
        self.mortgage_turns_counter = 0
        if self.type == 'street':
            self.buy_price = rule["buy_price"]
            self.mortgage_price = int(rule["buy_price"] * 0.7)
            self.buy_back_price = int(self.mortgage_price * 1.1)
            self.house_price = rule["upgrade_price"]
            self.fees = rule["fees"]

        elif self.type == "start":
            self.add_to_balance = rule["add_to_balance"]
        elif self.type == "prison":
            self.escape_price = rule["escape_price"]
        self.is_mortgaged = False
    
    def get_escape_price(self):
        return self.escape_price

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
        return self.house_price

    def get_type(self):
        return self.type

    def get_mortgage_price(self):
        return self.house_price

    def get_buy_back_price(self):
        return self.buy_back_price

    def get_house_price(self):
        return self.house_price

    def get_color(self):
        return self.color

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
            return False, self.house_price
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
    
    def get_is_mortgaged(self):
        return self.is_mortgaged
    
    def mortgage(self):
        self.is_mortgaged = True
        self.start_mortgage_turns_counter()
        return self.mortgage_price

    def unmortgage(self):
        self.is_mortgaged = False
        self.reset_mortgage_turns_counter()
        return self.buy_back_price

    def start_mortgage_turns_counter(self):
        self.mortgage_turns_counter = self.MORTGAGE_TURNS

    def reset_mortgage_turns_counter(self):
        self.mortgage_turns_counter = 0

    def decrease_mortgage_turns_counter(self):
        self.mortgage_turns_counter -= 1
        if self.is_mortgage_arrears():
            self.set_owner_none()

    def set_owner_none(self):
        self.field_level = 0
        self.is_mortgaged = False
        self.set_owner(None)

    def is_mortgage_arrears(self):
        return self.is_mortgaged and self.mortgage_turns_counter == 0
