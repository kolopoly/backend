import random
import json
from field import Field
from trade import Trade


def roll_dice():
    return random.randint(1, 6)


class Game:

    def __init__(self, game_id, host_id, rules_json, rule_id):
        self.round = 0
        self.rule_id = rule_id
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
        self.active_trade = None
        self.prison_field_id = -1
        self.find_prison()
        self.active_special_action = False

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
        if self.active_player_counter == 3 and self.prison_field_id != -1:
            self.players[player_id].change_prison_state()
            self.players_positions[player_id] = self.prison_field_id
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
        counter = 0
        while not self.players_still_in_game[self.get_active_player_id()]:
            self.active_player_pos = (self.active_player_pos + 1) % len(self.players_order)
            counter += 1
            if counter > len(self.players_order):
                return True
        self.active_player_counter = 0
        self.clean_all_actions_values()
        self.clean_all_completed_actions_values()
        return True

    def clean_all_actions_values(self):
        for key in self.actions:
            self.actions[key] = 0

    def clean_all_completed_actions_values(self):
        self.completed_actions = {"buy": False, "end_turn": False, "roll": False, "ready_to_pay": False}
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
        if self.check_street_ownership_and_mortgage_state(player_id, self.fields[field_id].get_color()):
            self.upgrade_street(self.fields[field_id].get_color())
        return True

    def check_street_ownership(self, player_id, street_id):
        for field in self.fields:
            if field.get_color() == street_id and field.get_owner() != player_id:
                return False
        return True

    def check_street_ownership_and_mortgage_state(self, player_id, street_id):
        if not self.check_street_ownership(player_id, street_id):
            return False
        for field in self.fields:
            if field.get_color() == street_id and field.get_is_mortgaged():
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
        if self.fields[field_id].get_is_mortgaged():
            return False
        street_ownership = self.check_street_ownership(player_id, self.fields[field_id].get_color())
        if not street_ownership:
            return self.mortgage_field(player_id, field_id)
        else:
            if self.fields[field_id].get_field_level() <= 1 and \
                    self.get_max_field_level(self.fields[field_id].get_color()) > self.fields[field_id].get_field_level():
                return False
            keep_ownership, money = self.fields[field_id].downgrade()
            self.players[player_id].set_money(self.players[player_id].get_money() + money)
            if self.fields[field_id].get_field_level() == 0:
                self.downgrade_street(self.fields[field_id].get_color())
            return True

    def get_max_field_level(self, street_id):
        max_level = 0
        for field in self.fields:
            if field.get_color() == street_id and field.get_field_level() > max_level:
                max_level = field.get_field_level()
        return max_level

    def contract_trade_fields(self, player1_id, player2_id, fields_ids, money1, money2):
        for field_id in fields_ids:
            if self.fields[field_id].get_owner() == player1_id:
                self.fields[field_id].set_owner(player2_id)
            else:
                self.fields[field_id].set_owner(player1_id)
        self.players[player1_id].add_money(money2 - money1)
        self.players[player2_id].add_money(money1 - money2)

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

    def unmortgage_field(self, player_id, field_id):
        self.check_ids([player_id], [field_id])
        if not self.check_action_unmortgage(player_id, field_id):
            return False
        self.fields[field_id].unmortgage()
        self.players[player_id].set_money(self.players[player_id].get_money() - self.fields[field_id].get_buy_back_price())
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
            self.sell_all_property_for_good(customer_id)
            if self.players[customer_id].get_money() < rent:
                self.players[owner_id].set_money(self.players[owner_id].get_money() +
                                                 self.players[customer_id].get_money())
            else:
                self.players[owner_id].set_money(self.players[owner_id].get_money() +
                                                 rent)
            self.players[customer_id].set_money(0)
            self.set_player_inactive(customer_id)
        else:
            self.players[customer_id].set_money(self.players[customer_id].get_money() - rent)
            self.players[owner_id].set_money(self.players[owner_id].get_money() + rent)
        self.completed_actions["ready_to_pay"] = False
        return True

    def set_player_inactive(self, player_id):
        self.players_still_in_game[player_id] = False

    def sell_all_property_for_good(self, player_id):
        for field in self.fields:
            if field.get_owner() == player_id:
                while self.check_action_sell_field(player_id, field.get_id()):
                    self.sell_field(player_id, field.get_id())
        for field in self.fields:
            if field.get_owner() == player_id:
                while self.check_action_sell_field(player_id, field.get_id()):
                    self.sell_field(player_id, field.get_id())
                field.set_owner(None)

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
                        "surrender": self.check_action_surrender(player_id), "action_answer_trade": False,
                        "action_trade": True}

    def generate_trade_actions(self):
        return {"buy": False, "end_turn": False,
                "roll": False, "sell": [[False, i] for i in range(len(self.fields))],
                "pay": False, "upgrade": [[False, i] for i in range(len(self.fields))],
                "surrender": False, "action_answer_trade": True,
                "action_trade": False}
      
    def get_trade(self):
        trade = {}
        if self.active_trade is not None:
            trade["player_id1"] = self.active_trade.get_player_id1()
            trade["player_id2"] = self.active_trade.get_player_id2()
            trade["money1"] = self.active_trade.get_money1()
            trade["money2"] = self.active_trade.get_money2()
            trade["fields"] = self.active_trade.get_fields()
            trade["trade_id"] = self.active_trade.get_trade_id()

        return trade

    async def send_game_state(self):
        if not self.is_started:
            game_state = {"players": {player_id: self.players[player_id].get_id()
                                      for player_id in self.players}, "rule_id": self.rule_id}
        else:
            if self.active_trade is None:
                await self.update_actions(self.get_active_player_id())
                actions = self.actions
            else:
                actions = self.generate_trade_actions()

            game_state = {"players": {player_id: self.players[player_id].get_id()
                                      for player_id in self.players_order}, "rule_id": self.rule_id,
                          "players_still_in_game": self.players_still_in_game,
                          "players_positions": self.players_positions,
                          "players_money": {player_id: self.players[player_id].get_money()
                                            for player_id in self.players_order},
                          "fields_owners_with_levels": {field.get_id(): (field.get_owner(), field.get_field_level())
                                                        for field in self.fields}, "round": self.round,
                          "last_rolls": self.last_rolls, "active_player": self.get_active_player_id(),
                          "actions": actions, "game_over": (self.get_number_of_players_still_in_game() <= 1),
                          "trade": self.get_trade()}

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
        if self.players[player_id].is_must_pay():
            return False
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
        if self.check_action_roll(player_id):
            return False
        if self.check_action_must_pay(player_id):
            return False
        if self.get_active_player_id() != player_id:
            return False
        if self.active_player_counter == 0:
            return False
        return True

    def check_action_sell(self, player_id):
        fields_of_player = []
        for field in self.fields:
            if field.get_owner() == player_id and \
                    self.check_action_sell_field(player_id, field.get_id()):
                fields_of_player.append([True, field.get_id()])
            else:
                fields_of_player.append([False, field.get_id()])
        return fields_of_player

    def check_action_sell_field(self, player_id, field_id):
        if self.fields[field_id].get_owner() != player_id:
            return False
        if self.fields[self.players_positions[player_id]].get_type() != "street":
            return False
        if self.fields[field_id].get_field_level() <= 1 and \
                self.get_max_field_level(self.fields[field_id].get_color()) > self.fields[field_id].get_field_level():
            return False
        if self.fields[field_id].get_is_mortgaged():
            return False
        return True
    
    def check_action_must_pay(self, player_id):
        if self.players[player_id].is_must_pay():
            return True
        if self.fields[self.players_positions[player_id]].get_is_mortgaged():
            return False
        if self.fields[self.players_positions[player_id]].get_owner() is None:
            return False
        if self.fields[self.players_positions[player_id]].get_owner() == player_id:
            return False
        if not self.completed_actions["ready_to_pay"]:
            return False
        return True

    def check_action_pay(self, player_id):
        if self.players[player_id].is_in_prison():
            return True
        if self.players[player_id].is_must_pay():
            return True
        if self.fields[self.players_positions[player_id]].get_is_mortgaged():
            return False
        if self.fields[self.players_positions[player_id]].get_owner() is None:
            return False
        if self.fields[self.players_positions[player_id]].get_owner() == player_id:
            return False
        if not self.completed_actions["ready_to_pay"]:
            return False
        return True

    def check_action_upgrade(self, player_id):
        fields_of_player = []
        for field in self.fields:
            if self.check_action_upgrade_field(player_id, field.get_id()) or \
                    self.check_action_unmortgage(player_id, field.get_id()):
                fields_of_player.append([True, field.get_id()])
            else:
                fields_of_player.append([False, field.get_id()])
        return fields_of_player

    def check_action_unmortgage(self, player_id, field_id):
        if player_id != self.get_active_player_id():
            return False
        if self.fields[field_id].get_owner() != player_id:
            return False
        if not self.fields[field_id].get_is_mortgaged():
            return False
        if self.players[player_id].get_money() < self.fields[field_id].get_buy_back_price():
            return False
        return True

    def check_action_upgrade_field(self, player_id, field_id):
        if self.fields[field_id].get_owner() != player_id:
            return False
        if self.fields[field_id].get_is_mortgaged():
            return False
        if self.players[player_id].get_money() < self.fields[field_id].get_house_price():
            return False
        if self.fields[field_id].get_field_level() == len(self.fields[field_id].get_fees()) - 1:
            return False
        if not self.check_street_ownership(player_id, self.fields[field_id].get_color()):
            return False
        return True

    def check_action_roll(self, player_id):
        if self.get_active_player_id() != player_id:
            return False
        if self.check_action_must_pay(player_id):
            return False
        if self.completed_actions.get("roll", 0) == 1:
            if self.last_rolls[0] != self.last_rolls[1]:
                return False
            if self.active_player_counter >= 3 and self.prison_field_id != -1:
                return False
            self.completed_actions["roll"] = 0
        return True

    def check_action_surrender(self, player_id):
        if self.players_order[self.active_player_pos] != player_id:
            return False
        # if self.check_action_pay(player_id):
        #     return False
        return True

    def get_possible_actions(self, player_id):
        if self.get_active_player_id() != player_id:
            return []
        return self.actions_list

    def get_number_of_players_still_in_game(self):
        counter = 0
        for player in self.players_still_in_game:
            if self.players_still_in_game[player]:
                counter += 1
        return counter

    def surrender(self, player_id):
        if player_id != self.get_active_player_id():
            return False
        if self.get_number_of_players_still_in_game() <= 1:
            return False
        self.sell_all_property_for_good(player_id)
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
        if not self.roll_process(player_id):
            return False
        self.update_player_mortgage_counters(player_id)
        return True

    def roll_process(self, player_id):
        dice1 = roll_dice()
        dice2 = roll_dice()
        self.last_rolls = [dice1, dice2]
        self.completed_actions["roll"] = 1
        self.completed_actions["ready_to_pay"] = True
        previous_position = self.players_positions[player_id]
        if self.players[player_id].is_in_prison():
            if dice1 == dice2:
                self.players[player_id].change_prison_state()                
            else:
                self.players[player_id].number_of_turns_in_prison += 1
                if self.players[player_id].number_of_turns_in_prison == 3:
                    self.players[player_id].set_must_pay(True)
                self.active_player_counter = 1
                return True
        result = self.update_position(player_id, dice1, dice2)
        if result and previous_position + dice1 + dice2 > len(self.fields):
            self.players[player_id].add_money(self.bonus_for_circle)
        return True

    def sell(self, player_id, field_id):
        if player_id != self.get_active_player_id():
            return False
        self.sell_field(player_id, field_id)
        return False

    def get_field_by_player_id(self, player_id):
        return self.fields[self.players_positions[player_id]]

    def pay(self, player_id):
        if player_id != self.get_active_player_id():
            return False
        if self.players[player_id].is_in_prison():
            return self.pay_prison(player_id)
        return self.pay_rent(player_id,
                             self.fields[self.players_positions[player_id]].get_owner(),
                             self.players_positions[player_id])

    def pay_prison(self, player_id):
        if player_id != self.get_active_player_id():
            return False
        if not self.players[player_id].is_in_prison():
            return False
        cost = self.get_field_by_player_id(player_id).get_escape_price()
        if self.players[player_id].get_money() < cost:
            return False
        self.players[player_id].set_money(self.players[player_id].get_money() - cost)
        self.players[player_id].change_prison_state()
        if self.players[player_id].is_must_pay():
            self.players[player_id].set_must_pay(False)
        return True

    def upgrade(self, player_id, field_id):
        if player_id != self.get_active_player_id():
            return False
        if self.fields[field_id].get_is_mortgaged():
            return self.unmortgage_field(player_id, field_id)
        else:
            return self.upgrade_field(player_id, field_id)

    def mortgage_field(self, player_id, field_id):
        if player_id != self.get_active_player_id():
            return False
        if self.fields[field_id].get_owner() != player_id:
            return False
        if self.get_max_field_level(self.fields[field_id].get_color()) > 1:
            return False
        if self.fields[field_id].get_is_mortgaged():
            return False
        self.fields[field_id].mortgage()
        self.players[player_id].set_money(
            self.players[player_id].get_money()
            + self.fields[field_id].get_mortgage_price()
        )
        return True

    def update_player_mortgage_counters(self, player_id):
        for field in self.fields:
            if field.get_owner() == player_id and field.get_is_mortgaged():
                field.decrease_mortgage_turns_counter()
        return True

    def request_trade(self, player1_id, player2_id, money1, money2, fields_ids):
        if player1_id != self.get_active_player_id():
            return False
        self.check_ids([player1_id, player2_id], fields_ids)
        for field_id in fields_ids:
            if self.fields[field_id].get_owner() != player1_id and self.fields[field_id].get_owner() != player2_id:
                return False
            if self.fields[field_id].get_field_level() > 1:
                return False
        if self.players[player1_id].get_money() < money1:
            return False
        if self.players[player2_id].get_money() < money2:
            return False

        self.active_trade = Trade(player1_id, player2_id, money1, money2, fields_ids)
        self.old_active_player_pos = self.active_player_pos
        self.active_player_pos = self.players_order.index(player2_id)
        return True

    def answer_trade(self, player_id, trade_id, answer):
        if self.active_trade is None:
            return "self.active_trade is None:"
        if player_id != self.active_trade.get_player_id2():
            return "player_id != self.active_trade.get_player_id2():"
        if trade_id != self.active_trade.get_trade_id():
            return "self.active_trade.get_trade_id():"
        if answer:
            self.contract_trade_fields(self.active_trade.get_player_id1(), self.active_trade.get_player_id2(),
                                       self.active_trade.get_fields(), self.active_trade.get_money1(),
                                       self.active_trade.get_money2())
        self.active_trade = None
        self.active_player_pos = self.old_active_player_pos
        return True
    
    def find_prison(self):
        for field in self.fields:
            if field.get_type() == "prison":
                self.prison_field_id = field.get_id()
                return
            
    def parse_special_action_result(self, player_id, chosen_variant: str = None):
        if self.fields[self.players_positions[player_id]].get_type() != "special":
            return False
        self.active_special_action = False
        card_dict = json.loads(self.fields[self.players_positions[player_id]].get_card())
        if card_dict["type"] == 1:
            self.players[player_id].add_money(card_dict["change_balance"])

        elif card_dict["type"] == 2:
            if self.fields[self.players_positions[player_id]].get_type() == "special" \
                    and card_dict["move_to_id"] != self.players_positions[player_id]:
                self.active_special_action = True
            self.players_positions[player_id] = card_dict["move_to_id"]

        elif card_dict["type"] == 3:
            if self.fields[self.players_positions[player_id]].get_type() == "special" and card_dict["move_for"] != 0:
                self.active_special_action = True
            self.players_positions[player_id] = (self.players_positions[player_id] +
                                                 card_dict["move_for"]) % len(self.fields)

        elif card_dict["type"] == 4:
            if card_dict["answers"][card_dict["correct_answer"]] == chosen_variant:
                self.players[player_id].add_money(card_dict["balance_add"])
            else:
                self.players[player_id].add_money(card_dict["balance_subtract"])

        return True
