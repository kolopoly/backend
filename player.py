from fastapi import WebSocket


class Player:
    player_id: int
    ws: WebSocket

    def __init__(self, player_id: int, ws: WebSocket):
        self.player_id = player_id
        self.ws = ws

    def get_id(self):
        return self.player_id

    def get_webSocket(self):
        return self.ws
    
    async def send_json_message(self, msg):               
        await self.ws.send_text(msg)
