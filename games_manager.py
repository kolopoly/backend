from fastapi import FastAPI, WebSocket
from game import Game
from player import Player
import random


class Games_manager:
    games = {}

    def is_game_consist(self, game_id: int):
        return game_id in self.games

    def generate_random_id(self):
        x = random.randint(1000, 9999)
        while x in self.games:
            x = random.randint(1000, 9999)
        return x

    def create_game(self, user_id: int):
        game_id = self.generate_random_id()
        game = Game(game_id, user_id)
        self.games[game_id] = game
        return game_id

    def connect_to_game(self, game_id: int, user_id: int, ws: WebSocket):
        print(game_id)
        print(self.games)

        if not self.is_game_consist(game_id):
            return False
        if (self.games[game_id].add_player(Player(user_id, ws))):
            print(f"User {user_id} connected to game {game_id}")
            return True
        return False

    def get_users(self, game_id: int):
        if not self.is_game_consist(game_id):
            return []
        return self.games[game_id].get_users()

    def buy(self, game_id: int, player_id: int):
        if not self.is_game_consist(game_id):
            return False
        return self.games[game_id].buy(player_id)

    def end_turn(self, game_id: int, player_id: int):
        if not self.is_game_consist(game_id):
            return False
        return self.games[game_id].end_turn(player_id)

    def roll(self, game_id: int, player_id: int):
        if not self.is_game_consist(game_id):
            return False
        return self.games[game_id].roll_dice(player_id)

    def sell(self, game_id: int, player_id: int, field_id: int):
        if not self.is_game_consist(game_id):
            return False
        return self.games[game_id].sell(player_id, field_id)

    def pay(self, game_id: int, player_id: int):
        if not self.is_game_consist(game_id):
            return False
        return self.games[game_id].pay(player_id)

    def upgrade(self, game_id: int, player_id: int, field_id: int):
        if not self.is_game_consist(game_id):
            return False
        return self.games[game_id].upgrade(player_id, field_id)
