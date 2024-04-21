import random


class Game:
    players = {}
    is_started = False
    host_id = None
    game_id = None
    fields = []
    players_order = []
    players_positions = {}
    active_player = 0
    active_player_counter = 0
    last_rolls = []
    actions = {}
    actions_list = ["end_turn", "surrender", "next"]

    def __init__(self, game_id, host_id, json_cards):
        self.round = 0
        self.game_id = game_id
        self.host = host_id

    def add_player(self, player):  # don't we have to ask for numb of max players in room?
        if self.is_started:
            return False
        self.players[player.get_id()] = player
        return True

    def get_users(self):
        res = []
        for player in self.players:
            res.append(self.players.get(player).get_id())
        return res

    def start_game(self, json_settings):
        if self.is_started:
            return False
        self.players_order = list(self.players.keys())
        random.shuffle(self.players_order)
        self.players_positions = {player_id: 0 for player_id in self.players}
        self.is_started = True
        last_rolls = [1, 1]
        return True

    def roll_dice(self):
        return random.randint(1, 6)

    def update_position(self, player_id, dice1, dice2):
        self.check_ids([player_id], [])
        self.round += 1
        self.active_player_counter += 1
        if self.active_player_counter == 3:
            #TODO: go to jail
            self.players_positions[player_id] = 0
            pass
        else:
            self.players_positions[player_id] = (self.players_positions[player_id] + dice1 + dice2) % len(self.fields)
            #TODO: check if player passed start
            #TODO: check if player landed on field with owner

        return True

    def end_cur_turn(self, player_id):
        self.check_ids([player_id], [])
        if self.active_player != player_id:
            raise Exception("not active player tries to end turn.")
        self.active_player = (self.active_player + 1) % len(self.players)
        self.active_player_counter = 0
        self.clean_all_actions_values()
        return True

    def clean_all_actions_values(self):
        for key in self.actions:
            self.actions[key] = 0

    def get_player_position(self, player_id):
        return self.players_positions[player_id]

    def buy_field(self, player_id, field_id):
        self.check_ids([player_id], [field_id])
        if self.fields[field_id].get_owner() is not None:
            return False
        if self.players[player_id].get_money() < self.fields[field_id].get_price():
            return False
        self.players[player_id].set_money(self.players[player_id].get_money() - self.fields[field_id].get_buy_price())
        self.fields[field_id].set_owner(player_id)
        return True

    def sell_field(self, player_id, field_id):
        self.check_ids([player_id], [field_id])
        if self.fields[field_id].get_owner() != player_id:
            return False
        keep_ownership, money = self.fields[field_id].downgrade()
        if not keep_ownership:
            self.fields[field_id].set_owner(None)
        self.players[player_id].set_money(self.players[player_id].get_money() + money)
        return True

    def contract_trade_fields(self, player1_id, player2_id, fields_ids, money):
        self.check_ids([player1_id, player2_id], fields_ids)
        for field_id in fields_ids:
            if self.fields[field_id].get_owner() != player1_id:
                return False
            if self.fields[field_id].get_owner() == player2_id:
                return False
            if self.fields[field_id].get_built_houses() > 0 or self.fields[field_id].get_built_hotels() > 0:
                return False
        if self.players[player2_id].get_money() < money:
            return False
        for field_id in fields_ids:
            self.fields[field_id].set_owner(player2_id)
        self.players[player2_id].set_money(self.players[player2_id].get_money() - money)
        self.players[player1_id].set_money(self.players[player1_id].get_money() + money)
        return True

    def upgrade_field(self, player_id, field_id):
        self.check_ids([player_id], [field_id])
        if player_id != self.fields[field_id].get_owner():
            return False
        result, money = self.fields[field_id].upgrade(self.players[player_id].get_money())
        if not result:
            return False
        self.players[player_id].set_money(money)
        pass

    def pay_rent(self, customer_id, owner_id, field_id):
        self.check_ids([customer_id, owner_id], [field_id])
        if self.fields[field_id].get_owner() != owner_id:
            return False
        if customer_id == owner_id:
            return False
        rent = self.fields[field_id].get_rent()
        if self.players[customer_id].get_money() < rent:
            #TODO: bankrupt
            self.players[owner_id].set_money(self.players[owner_id].get_money() + self.players[customer_id].get_money())
            self.players[customer_id].set_money(0)
            return True
        self.players[customer_id].set_money(self.players[customer_id].get_money() - rent)
        self.players[owner_id].set_money(self.players[owner_id].get_money() + rent)
        return True

    def check_ids(self, player_ids, field_ids):
        for player_id in player_ids:
            if player_id not in self.players:
                raise Exception(f"Player {player_id} not exists.\n")
        for field_id in field_ids:
            if field_id not in self.fields:
                raise Exception(f"Field {field_id} not exists.\n")
        return True

    def get_active_player_id(self):
        return self.players_order[self.active_player]

    def send_game_state(self):
        pass

    def get_players_info(self):
        players_info = {
            "playersNumber": len(self.players),
            "playersMoney": [self.players[player_id].get_money() for player_id in self.players_order],
            "playersAvatar": [None for player_id in self.players_order],
            "playersNames": [self.players[player_id].get_name() for player_id in self.players_order],
            "currentPlayer": self.get_active_player_id(),
        }
        return players_info

    def get_possible_actions(self, player_id):
        if self.active_player != player_id:
            return []
        pass

    def buy(self, player_id):
        if (player_id != self.get_active_player_id()):
            return False
        # TODO

        return False

    def end_turn(self, player_id):
        if (player_id != self.get_active_player_id()):
            return False
        return self.end_cur_turn(player_id)

    def roll(self, player_id):
        if (player_id != self.get_active_player_id()):
            return False
        dice1 = self.roll_dice()
        dice2 = self.roll_dice()
        self.last_rolls = [dice1, dice2]
        self.update_position(player_id, dice1, dice2)
        return True

    def sell(self, player_id, field_id):
        if (player_id != self.get_active_player_id()):
            return False
        self.sell_field(player_id, field_id)
        return False

    def pay(self, player_id):
        if (player_id != self.get_active_player_id()):
            return False
        # TODO
        return False

    def upgrade(self, player_id, field_id):
        if (player_id != self.get_active_player_id()):
            return False
        # TODO
        return False





class Field:
    id = None
    name = None
    group_id = None
    owner = None

    buy_price = None
    sell_price = None
    house_price = None
    hotel_price = None

    house_rent = None
    hotel_rent = None
    built_houses = 0
    built_hotels = 0
    limit_houses = 4
    limit_hotels = 1

    def __init__(self, id, name, group_id, buy_price, sell_price, house_price, hotel_price, house_rent, hotel_rent):
        self.id = id
        self.name = name
        self.group_id = group_id
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.house_price = house_price
        self.hotel_price = hotel_price
        self.house_rent = house_rent
        self.hotel_rent = hotel_rent

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

    def get_built_houses(self):
        return self.built_houses

    def get_built_hotels(self):
        return self.built_hotels

    def build_house(self, money):
        if self.built_houses >= self.limit_houses:
            return False, money
        if money < self.house_price:
            return False, money
        self.built_houses += 1
        return True, money - self.house_price

    def build_hotel(self, money):
        if self.built_hotels >= self.limit_hotels:
            return False, money
        if self.built_houses < self.limit_houses:
            return False, money
        if money < self.hotel_price:
            return False, money
        self.built_hotels = 1
        self.built_houses = 0
        return True, money - self.hotel_price

    def upgrade(self, money):
        if self.built_hotels > 0:
            return False, money
        if self.built_houses < self.limit_houses:
            return self.build_house(money)
        if self.built_hotels < self.limit_hotels:
            return self.build_hotel(money)
        return False, money

    def downgrade(self):
        if self.built_hotels > 0:
            self.built_hotels = 0
            self.built_houses = self.limit_houses
            return True, self.hotel_price
        elif self.built_houses > 0:
            self.built_houses -= 1
            return True, self.house_price
        return False, self.sell_price

    def get_rent(self):
        return self.house_rent * self.built_houses + self.hotel_rent * self.built_hotels
