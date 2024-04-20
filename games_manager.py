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
        self.games[user_id] = game
        return game_id

    def connect_to_game(self, game_id: int, user_id: int, ws: WebSocket):
        if not self.is_game_consist(game_id):
            return False                
        if (self.games[game_id].add_player(Player(user_id, ws))):
            print(f"User {user_id} connected to game {game_id}")
            return True
        return False
    
    