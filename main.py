import json
import os

from fastapi import FastAPI, WebSocket
import websockets
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse

from gamesmanager import GamesManager

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gm = GamesManager()


@app.get("/buy/{game_id}/{player_id}")
async def buy(game_id: int, player_id: int):
    return await gm.buy(game_id, player_id)


@app.get("/connect/{user_id}/{game_id}")
async def connect(user_id: int, game_id: int):
    try :
        return await websockets.connect(f"ws://localhost:8000/connect/{user_id}/{game_id}")
    except Exception as e:
        print(e)
        return False

@app.get("/create/{user_id}/{rule_id}")
async def create(user_id: int, rule_id: int):
    try:
        with open(f"./rules/{rule_id}.json") as f:
            rule = f.read()
            rule = json.loads(rule)
        game_id = gm.create_game(user_id, rule, rule_id)
        print(f"Game created by user {user_id} with game_id {game_id}")
        return game_id
    except Exception as e:
        print(e)
        return 0


@app.get("/end_turn/{game_id}/{player_id}")
async def end_turn(game_id: int, player_id: int):
    return await gm.end_turn(game_id, player_id)


@app.get("/get_rule_by_game_id/{game_id}")
async def get_rule_by_game(game_id: int):
    rule_id = gm.get_rule_id(game_id)
    with open(f"./rules/{rule_id}.json") as f:
        return json.loads(f.read())

@app.get("/get_rule/{rule_id}")
async def get_rule(rule_id: int):
    with open(f"./rules/{rule_id}.json") as f:
        return json.loads(f.read())


@app.post("/save_rule")
async def save_rule(payload: dict):
    print(payload)
    json_files = [f for f in os.listdir("./rules") if f.endswith('.json')]
    json_files.sort(key=lambda f: int(f.split('.')[0]))
    id = int(json_files[-1].split('.')[0]) + 1
    with open(f"./rules/{id}.json", 'w') as file:
        data = json.dumps(payload)
        file.write(data)
    return id


@app.get("/get_rules")
async def get_rules():
    json_files = [f for f in os.listdir("./rules") if f.endswith('.json')]
    json_files.sort(key=lambda f: int(f.split('.')[0]))

    combined_data = []

    for filename in json_files:
        file_path = os.path.join('./rules', filename)
        with open(file_path, 'r') as file:
            data = json.load(file)
            combined_data.append(data)

    return json.dumps(combined_data)


@app.get("/get_users/{game_id}")
async def get_users(game_id: int):
    return await gm.get_users(game_id)


@app.get("/mortgage_field/{game_id}/{player_id}/{field_id}")
async def mortgage_field(game_id: int, player_id: int, field_id: int):
    return await gm.mortgage_field(game_id, player_id, field_id)


@app.get("/pay/{game_id}/{player_id}")
async def pay(game_id: int, player_id: int):
    return await gm.pay(game_id, player_id)


# @app.get("/pay_prison/{game_id}/{player_id}")
# async def pay_prison(game_id: int, player_id: int):
#     return await gm.pay_prison(game_id, player_id)


@app.get("/roll/{game_id}/{player_id}")
async def roll(game_id: int, player_id: int):
    return await gm.roll(game_id, player_id)


@app.get("/sell/{game_id}/{player_id}/{field_id}")
async def sell(game_id: int, player_id: int, field_id: int):
    return await gm.sell(game_id, player_id, field_id)


@app.get("/start_game/{game_id}/{player_id}")
async def start_game(game_id: int, player_id: int):
    return await gm.start_game(game_id, player_id)


@app.get("/surrender/{game_id}/{player_id}")
async def surrender(game_id: int, player_id: int):
    return await gm.surrender(game_id, player_id)


@app.post("/request_trade")
async def trade(playload: dict):
    print(playload)
    x = await gm.request_trade(
        int(playload['game_id']),
        int(playload['player_id1']),
        int(playload['player_id2']),
        playload['money1'],
        playload['money2'],
        playload['fields']
    )
    print(x)


@app.get("/answer_trade/{game_id}/{player_id}/{trade_id}/{answer}")
async def answer_trade(game_id: int, player_id: int, trade_id: int, answer: bool):
    x = await gm.answer_trade(game_id, player_id, str(trade_id), answer)
    print(x)


@app.get("/upgrade/{game_id}/{player_id}/{field_id}")
async def upgrade(game_id: int, player_id: int, field_id: int):
    return await gm.upgrade(game_id, player_id, field_id)


@app.get("/assets/{asset_name}")
async def assets(asset_name: str):
    path = f"./assets/{asset_name}"
    if os.path.exists(path):
        return FileResponse(path, media_type='application/octet-stream', filename=os.path.basename(path))
    else:
        return {"error": "File not found"}


# WebSockets:

@app.websocket("/connect/{user_id}/{game_id}")
async def websocket_endpoint(ws: WebSocket, user_id: int, game_id: int):
    await ws.accept()
    await gm.connect_to_game(game_id, user_id, ws)
    while True:
        try:
            data = await ws.receive_text()
            print(data)
            await ws.send_text(f"Message text was: {data}")
        except Exception as e:
            print(e)
            break        
