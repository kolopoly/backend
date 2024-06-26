import json

from fastapi import WebSocket
from game import Game
from player import Player
import random


class GamesManager:
    games = {}

    def is_game_consist(self, game_id: int):
        return game_id in self.games

    def generate_random_id(self):
        x = random.randint(1000, 9999)
        while x in self.games:
            x = random.randint(1000, 9999)
        return x

    def create_game(self, user_id: int, rule, rule_id: int):
        game_id = self.generate_random_id()
        game = Game(game_id, user_id, rule, rule_id)
        self.games[game_id] = game
        return game_id

    async def connect_to_game(self, game_id: int, user_id: int, ws: WebSocket):

        if not self.is_game_consist(game_id):
            return False
        if self.games[game_id].add_player(user_id, ws):
            print(f"User {user_id} connected to game {game_id}")
            await self.games[game_id].send_game_state()
            return True
        return False    

    def get_users(self, game_id: int):
        if not self.is_game_consist(game_id):
            return []
        return self.games[game_id].get_users()

    async def buy(self, game_id: int, player_id: int):
        if not self.is_game_consist(game_id):
            return False
        res = self.games[game_id].buy(player_id)
        await self.games[game_id].send_game_state()
        return res

    async def end_turn(self, game_id: int, player_id: int):
        if not self.is_game_consist(game_id):
            return False
        res = self.games[game_id].end_turn(player_id)
        await self.games[game_id].send_game_state()
        return res

    async def roll(self, game_id: int, player_id: int):
        if not self.is_game_consist(game_id):
            return False
        res = self.games[game_id].roll(player_id)
        await self.games[game_id].send_game_state()
        return res

    async def sell(self, game_id: int, player_id: int, field_id: int):
        if not self.is_game_consist(game_id):
            return False
        res = self.games[game_id].sell(player_id, field_id)
        await self.games[game_id].send_game_state()
        return res

    async def surrender(self, game_id: int, player_id: int):
        if not self.is_game_consist(game_id):
            return False
        res = self.games[game_id].surrender(player_id)        
        await self.games[game_id].send_game_state()
        return res

    async def pay(self, game_id: int, player_id: int):
        if not self.is_game_consist(game_id):
            return False
        res = self.games[game_id].pay(player_id)
        await self.games[game_id].send_game_state()
        return res

    # async def pay_prison(self, game_id: int, player_id: int):
    #     if not self.is_game_consist(game_id):
    #         return False
    #     res = self.games[game_id].pay_prison(player_id)
    #     await self.games[game_id].send_game_state()
    #     return res

    async def upgrade(self, game_id: int, player_id: int, field_id: int):
        if not self.is_game_consist(game_id):
            return False
        res = self.games[game_id].upgrade(player_id, field_id)
        await self.games[game_id].send_game_state()
        return res

    async def start_game(self, game_id: int, player_id: int):
        if not self.is_game_consist(game_id):
            return False
        res = self.games[game_id].start_game(player_id)
        await self.games[game_id].send_game_state()
        return res

    async def mortgage_field(self, game_id: int, player_id: int, field_id: int):
        if not self.is_game_consist(game_id):
            return False
        res = self.games[game_id].mortgage_field(player_id, field_id)
        await self.games[game_id].send_game_state()
        return res
    
    async def request_trade(self, game_id: int, player_id1: int, player_id2: int, money1: int, money2: int, fields):
        if not self.is_game_consist(game_id):
            return False
        res = self.games[game_id].request_trade(player_id1, player_id2, money1, money2, fields)
        await self.games[game_id].send_game_state()
        return res

    async def answer_special_action(self, game_id: int, player_id: int, chosen_variant: int):
        if not self.is_game_consist(game_id):
            return False
        res = self.games[game_id].request_trade(player_id1, player_id2, money1, money2, fields)
        await self.games[game_id].send_game_state()
        return res
    
    async def answer_trade(self, game_id: int, player_id: int, trade_id: str, answer: bool):
        if not self.is_game_consist(game_id):
            return False
        res = self.games[game_id].answer_trade(player_id, trade_id, answer)
        await self.games[game_id].send_game_state()
        return res
    
    def get_rule_id(self, game_id: int):
        if not self.is_game_consist(game_id):
            return 0
        return self.games[game_id].get_rule_id()
