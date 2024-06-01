from fastapi import WebSocket


class Player:
    player_id: int
    ws: WebSocket
    player_money: int

    def __init__(self, player_id: int, ws: WebSocket, player_money: int = 1500):
        self.player_id = player_id
        self.ws = ws
        self.player_money = player_money
        self.in_prison = False
        self.number_of_turns_in_prison = 0
        self.must_pay = False

    def get_id(self):
        return self.player_id

    def get_webSocket(self):
        return self.ws

    def get_money(self):
        return self.player_money

    def set_money(self, money):
        self.player_money = money
        
    def add_money(self, money):
        self.player_money += money
        
    def is_in_prison(self):
        return self.in_prison
    
    def is_must_pay(self):
        return self.must_pay

    def set_must_pay(self, must_pay):
        self.must_pay = must_pay

    def change_prison_state(self):
        if (self.in_prison):
            self.in_prison = False
        else:
            self.in_prison = True
            self.number_of_turns_in_prison = 0

    async def send_json_message(self, msg):
        await self.ws.send_text(msg)
