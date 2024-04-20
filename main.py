from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.get("/connect/{game_id}")
def connect(game_id: int):
    return