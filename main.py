import json

from fastapi import FastAPI, WebSocket
import websockets
import uvicorn
from games_manager import Games_manager

app = FastAPI()
gm = Games_manager()


@app.get("/create/{user_id}")
async def create(user_id: int):
    game_id = gm.create_game(user_id)
    print(f"Game created by user {user_id} with game_id {game_id}")
    return game_id


@app.get("/get_rule/{rule_id}")
async def get_rule(rule_id: int):
    with open("test.json") as f:
        return json.loads(f.read())


@app.get("/connect/{user_id}/{game_id}")
async def connect(user_id: int, game_id: int):
    await websockets.connect(f"ws://localhost:8000/connect/{user_id}/{game_id}")


@app.get("/get_users/{game_id}")
async def get_users(game_id: int):
    return gm.get_users(game_id)


@app.get("buy/{game_id}/{player_id}")
async def buy(game_id: int, player_id: int):
    return gm.buy(game_id, player_id)


@app.get("end_turn/{game_id}/{player_id}")
async def end_turn(game_id: int, player_id: int):
    return gm.end_turn(game_id, player_id)


@app.get("roll/{game_id}/{player_id}")
async def roll(game_id: int, player_id: int):
    return gm.roll(game_id, player_id)


@app.get("sell/{game_id}/{player_id}/{field_id}")
async def sell(game_id: int, player_id: int, field_id: int):
    return gm.sell(game_id, player_id, field_id)


@app.get("pay/{game_id}/{player_id}")
async def pay(game_id: int, player_id: int):
    return gm.pay(game_id, player_id)


@app.get("upgrade/{game_id}/{player_id}/{field_id}")
async def upgrade(game_id: int, player_id: int, field_id: int):
    return gm.upgrade(game_id, player_id, field_id)


# WebSockets:

@app.websocket("/connect/{user_id}/{game_id}")
async def websocket_endpoint(ws: WebSocket, user_id: int, game_id: int):
    await ws.accept()
    gm.connect_to_game(game_id, user_id, ws)
    while True:
        data = await ws.receive_text()
        gm.send_message(game_id, data)

        await ws.send_text(f"Message text was: {data}")


uvicorn.run(app, host="localhost", port=8000)
