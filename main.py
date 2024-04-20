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

@app.get("/connect/{user_id}/{game_id}")
async def connect(user_id: int, game_id: int):    
    await websockets.connect(f"ws://localhost:8000/connect/{user_id}/{game_id}")    
    
@app.get("/get_users/{game_id}")
async def get_users(game_id: int):
    return gm.get_users(game_id)

@app.websocket("/connect/{user_id}/{game_id}")
async def websocket_endpoint(ws: WebSocket, user_id: int, game_id: int):
    await ws.accept()        
    gm.connect_to_game(game_id, user_id, ws)
    while True:
        data = await ws.receive_text()
        gm.send_message(game_id, data)
        
        await ws.send_text(f"Message text was: {data}")        

uvicorn.run(app, host="localhost", port=8000)