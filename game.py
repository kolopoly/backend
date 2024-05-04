import random
import json
from field import Field


def roll_dice():
    return random.randint(1, 6)


class Game:

    def __init__(self, game_id, host_id, rules_json):
        self.round = 0
        self.game_id = game_id
        self.host_id = host_id
        self.players = {}
        self.is_started = False
        self.fields = []
        self.field_ids = []
        self.players_order = []
        self.players_still_in_game = {}
        self.players_positions = {}
        self.active_player_pos = 0
        self.active_player_counter = 0
        self.last_rolls = []
        self.actions = {}
        self.completed_actions = {}
        self.actions_list = ["end_turn", "surrender", "pay"]
        self.bonus_for_circle = 100
        self.fields = self.parse_input_rules_json(rules_json)

    def parse_input_rules_json(self, json_data):
        fields_data = json_data.get('fields', [])
        fields = []
        counter = 0
        for field_data in fields_data:
            field = Field(
                id=counter,
                rule=field_data
            )
            fields.append(field)
            self.field_ids.append(counter)
            counter += 1
        return fields

    def add_player(self, player):  # don't we have to ask for numb of max players in room?
        self.players[player.get_id()] = player
        return True

    def get_users(self):
        res = []
        for player in self.players:
            res.append(self.players.get(player).get_id())
        return res

    def start_game(self, player_id):
        if player_id != self.host_id:
            return False
        if self.is_started:
            return False
        self.players_order = list(self.players.keys())
        random.shuffle(self.players_order)
        for player_id in self.players_order:
            self.players_positions[player_id] = 1
        self.players_positions = {player_id: 0 for player_id in self.players}
        self.is_started = True
        self.last_rolls = [1, 1]
        for player in self.players:
            self.players_still_in_game[player] = True
        self.clean_all_completed_actions_values()
        return True

    def update_position(self, player_id, dice1, dice2):
        self.check_ids([player_id], [])
        self.round += 1
        self.active_player_counter += 1
        if self.active_player_counter == 3:
            # TODO: go to jail
            self.players_positions[player_id] = 0
        else:
            self.players_positions[player_id] = (self.players_positions[player_id] + dice1 + dice2) % len(self.fields)
            # TODO: check if player passed start
            # TODO: check if player landed on field with owner
        return True

    def end_cur_turn(self, player_id):
        self.check_ids([player_id], [])
        if self.get_active_player_id() != player_id:
            raise Exception("not active player tries to end turn.")
        self.active_player_pos = (self.active_player_pos + 1) % len(self.players_order)
        while not self.players_still_in_game[self.get_active_player_id()]:
            self.active_player_pos = (self.active_player_pos + 1) % len(self.players_order)
        self.active_player_counter = 0
        self.clean_all_actions_values()
        self.clean_all_completed_actions_values()
        return True

    def clean_all_actions_values(self):
        for key in self.actions:
            self.actions[key] = 0

    def clean_all_completed_actions_values(self):
        self.completed_actions = {"buy": 0, "end_turn": 0, "roll": 0, "pay": False}
        # self.actions["upgrade"] = []

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
        if self.check_street_ownership(player_id, self.fields[field_id].get_color()):
            self.upgrade_street(self.fields[field_id].get_color())
        return True

    def check_street_ownership(self, player_id, street_id):
        for field in self.fields:
            if field.get_color() == street_id and field.get_owner() != player_id:
                return False
        return True

    def upgrade_street(self, street_id):
        for field in self.fields:
            if field.get_color() == street_id:
                field.upgrade_by_street()

    def downgrade_street(self, street_id):
        for field in self.fields:
            if field.get_color() == street_id:
                field.downgrade_by_street()

    def sell_field(self, player_id, field_id):
        self.check_ids([player_id], [field_id])
        if self.fields[field_id].get_owner() != player_id:
            return False
        if self.get_max_field_level(self.fields[field_id].get_color()) > self.fields[field_id].get_field_level():
            return False
        street_ownership = self.check_street_ownership(player_id, self.fields[field_id].get_color())
        keep_ownership, money = self.fields[field_id].downgrade()
        if not keep_ownership:
            self.fields[field_id].set_owner(None)
        self.players[player_id].set_money(self.players[player_id].get_money() + money)
        if street_ownership and not keep_ownership:
            self.downgrade_street(self.fields[field_id].get_color())
        return True

    def get_max_field_level(self, street_id):
        max_level = 0
        for field in self.fields:
            if field.get_color() == street_id and field.get_field_level() > max_level:
                max_level = field.get_field_level()
        return max_level

    def contract_trade_fields(self, player1_id, player2_id, fields_ids, money):
        self.check_ids([player1_id, player2_id], fields_ids)
        for field_id in fields_ids:
            if self.fields[field_id].get_owner() != player1_id:
                return False
            if self.fields[field_id].get_owner() == player2_id:
                return False
            if self.fields[field_id].get_field_level() > 1:
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
        for field in self.fields:
            if field.get_color() == self.fields[field_id].get_color() and field.get_owner() != player_id:
                return False
        result, money = self.fields[field_id].upgrade_by_building(self.players[player_id].get_money())
        if not result:
            return False
        self.players[player_id].set_money(money)
        return True

    def pay_rent(self, customer_id, owner_id, field_id):
        self.check_ids([customer_id, owner_id], [field_id])
        if self.fields[field_id].get_owner() != owner_id:
            return False
        if customer_id == owner_id:
            return False
        rent = self.fields[field_id].get_fee()
        if self.players[customer_id].get_money() < rent:
            # TODO: bankrupt
            self.recursive_sell_all(customer_id)
            if self.players[customer_id].get_money() < rent:
                self.players[owner_id].set_money(self.players[owner_id].get_money() +
                                                 self.players[customer_id].get_money())
            else:
                self.players[owner_id].set_money(self.players[owner_id].get_money() +
                                                 rent)
            self.players[customer_id].set_money(0)
            self.set_player_inactive(customer_id)
            self.completed_actions["pay"] = True
            return True

        self.players[customer_id].set_money(self.players[customer_id].get_money() - rent)
        self.players[owner_id].set_money(self.players[owner_id].get_money() + rent)
        self.completed_actions["pay"] = True
        return True

    def set_player_inactive(self, player_id):
        self.players_still_in_game[player_id] = False

    def recursive_sell_all(self, player_id):
        fields_of_player = []
        for field in self.fields:
            if field.get_owner() == player_id:
                fields_of_player.append(field.get_id())
        flag_to_continue = False
        for i in self.check_action_sell(player_id):
            if i[0]:
                flag_to_continue = True
                break

        while flag_to_continue:
            for field_id in fields_of_player:
                if self.check_action_sell_field(player_id, field_id):
                    self.sell_field(player_id, field_id)
            flag_to_continue = False
            for i in self.check_action_sell(player_id):
                if i[0]:
                    flag_to_continue = True
                    break

    def check_ids(self, player_ids, field_ids):
        for player_id in player_ids:
            if player_id not in self.players:
                raise Exception(f"Player {player_id} not exists.\n")
        for field_id in field_ids:
            if field_id >= len(self.fields):
                raise Exception(f"Field {field_id} not exists.\n")
        return True

    def get_active_player_id(self):
        return self.players_order[self.active_player_pos]

    async def update_actions(self, player_id):
        self.actions = {"buy": self.check_action_buy(player_id), "end_turn": self.check_action_end_turn(player_id),
                        "roll": self.check_action_roll(player_id), "sell": self.check_action_sell(player_id),
                        "pay": self.check_action_pay(player_id), "upgrade": self.check_action_upgrade(player_id),
                        "surrender": self.check_action_surrender(player_id)}

    async def send_game_state(self):
        if not self.is_started:
            game_state = {"players": {player_id: self.players[player_id].get_id()
                                      for player_id in self.players}}
        else:
            await self.update_actions(self.get_active_player_id())
            game_state = {"players": {player_id: self.players[player_id].get_id()
                                      for player_id in self.players_order},
                          "players_still_in_game": self.players_still_in_game,
                          "players_positions": self.players_positions,
                          "players_money": {player_id: self.players[player_id].get_money()
                                            for player_id in self.players_order},
                          "fields_owners_with_levels": {field.get_id(): (field.get_owner(), field.get_field_level())
                                                        for field in self.fields}, "round": self.round,
                          "last_rolls": self.last_rolls, "active_player": self.get_active_player_id(),
                          "actions": self.actions, "game_over": (self.get_number_of_players_still_in_game() <= 1)}

        msg = json.dumps(game_state)

        for player in self.players:
            await self.players[player].send_json_message(msg)

    def get_number_of_players_still_in_game(self):
        counter = 0
        for player in self.players_still_in_game:
            if self.players_still_in_game[player]:
                counter += 1
        return counter

    def check_action_buy(self, player_id):
        if self.fields[self.players_positions[player_id]].get_owner() is not None:
            return False
        if self.fields[self.players_positions[player_id]].get_type() != "street":
            return False
        if self.players[player_id].get_money() < self.fields[self.players_positions[player_id]].get_buy_price():
            return False
        if self.active_player_counter == 0:
            return False

        return True

    def check_action_end_turn(self, player_id):
        if self.get_active_player_id() != player_id:
            return False
        if self.active_player_counter == 0:
            return False
        # if self.completed_actions["roll"] == 0:
        #     return False
        # if self.check_if_need_to_pay(player_id):
        #     return False
        # self.completed_actions["roll"] = 0
        return True

    def check_action_sell(self, player_id):
        fields_of_player = []
        for field in self.fields:
            if field.get_owner() == player_id and self.check_action_sell_field(player_id, field.get_id()):
                fields_of_player.append([True, field.get_id()])
            else:
                fields_of_player.append([False, field.get_id()])
        return fields_of_player

    def check_action_sell_field(self, player_id, field_id):
        if self.fields[field_id].get_owner() != player_id:
            return False
        if self.fields[self.players_positions[player_id]].get_type() != "street":
            return False
        if self.get_max_field_level(self.fields[field_id].get_color()) > self.fields[field_id].get_field_level():
            return False
        return True

    def check_action_pay(self, player_id):
        if self.fields[self.players_positions[player_id]].get_owner() is None:
            return False
        if self.fields[self.players_positions[player_id]].get_owner() == player_id:
            return False
        if self.completed_actions["pay"]:
            return False
        return True

    def check_action_upgrade(self, player_id):
        fields_of_player = []
        for field in self.fields:
            if field.get_owner() == player_id and self.check_action_upgrade_field(player_id, field.get_id()):
                fields_of_player.append([True, field.get_id()])
            else:
                fields_of_player.append([False, field.get_id()])
        return fields_of_player

    def check_action_upgrade_field(self, player_id, field_id):
        if self.fields[field_id].get_owner() != player_id:
            return False
        if self.players[player_id].get_money() < self.fields[field_id].get_house_price():
            return False
        if self.fields[field_id].get_field_level() == len(self.fields[field_id].get_fees()) - 1:
            return False
        if not self.check_street_ownership(player_id, self.fields[field_id].get_color()):
            return False
        return True

    def check_if_need_to_pay(self, player_id):
        if self.fields[self.players_positions[player_id]].get_owner() is None:
            return False
        if self.fields[self.players_positions[player_id]].get_owner() == player_id:
            return False
        if self.completed_actions["pay"]:
            return False
        return True

    def check_action_roll(self, player_id):
        if self.get_active_player_id() != player_id:
            return False
        if self.check_if_need_to_pay(player_id):
            return False
        if self.completed_actions.get("roll", 0) == 1:
            if self.last_rolls[0] != self.last_rolls[1]:
                return False
            if self.active_player_counter >= 3:
                return False
            self.completed_actions["roll"] = 0
        return True

    def check_action_surrender(self, player_id):
        if self.players_order[self.active_player_pos] != player_id:
            return False
        if self.check_if_need_to_pay(player_id):
            return False
        return True

    def get_possible_actions(self, player_id):
        if self.get_active_player_id() != player_id:
            return []
        return self.actions_list

    def surrender(self, player_id):
        if player_id != self.get_active_player_id():
            return False
        self.recursive_sell_all(player_id)
        self.players[player_id].set_money(0)
        self.set_player_inactive(player_id)
        self.end_turn(player_id)
        return True

    def buy(self, player_id):
        if player_id != self.get_active_player_id():
            return False
        return self.buy_field(player_id, self.players_positions[player_id])

    def end_turn(self, player_id):
        if player_id != self.get_active_player_id():
            return False
        return self.end_cur_turn(player_id)

    def roll(self, player_id):
        if player_id != self.get_active_player_id():
            return False
        if not self.check_action_roll(player_id):
            return False
        dice1 = roll_dice()
        dice2 = roll_dice()
        self.last_rolls = [dice1, dice2]
        self.completed_actions["roll"] = 1
        self.completed_actions["pay"] = False
        previous_position = self.players_positions[player_id]
        result = self.update_position(player_id, dice1, dice2)
        if result and previous_position + dice1 + dice2 > len(self.fields):
            self.players[player_id].set_money(self.players[player_id].get_money() + self.bonus_for_circle)
        return True

    def sell(self, player_id, field_id):
        if player_id != self.get_active_player_id():
            return False
        self.sell_field(player_id, field_id)
        return False

    def pay(self, player_id):
        if player_id != self.get_active_player_id():
            return False
        return self.pay_rent(player_id,
                             self.fields[self.players_positions[player_id]].get_owner(),
                             self.players_positions[player_id])

    def upgrade(self, player_id, field_id):
        if player_id != self.get_active_player_id():
            return False
        return self.upgrade_field(player_id, field_id)

    def mortgage_field(self, player_id, field_id):
        # TODO: implement
        return True
