from fastapi import WebSocket


class Player:
    player_id: int
    ws: WebSocket
    player_money: int

    def __init__(self, player_id: int, ws: WebSocket, player_money: int = 1500):
        self.player_id = player_id
        self.ws = ws
        self.player_money = player_money


    def get_id(self):
        return self.player_id

    def get_webSocket(self):
        return self.ws

    def get_money(self):
        return self.player_money

    def set_money(self, money):
        self.player_money = money
    
    async def send_json_message(self, msg):               
        await self.ws.send_text(msg)
