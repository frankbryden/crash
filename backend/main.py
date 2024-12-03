from fastapi import FastAPI, WebSocket
from typing import Union
from pydantic import BaseModel
import json
from threading import Thread
import time

from game_handler import GameHandler

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

game_handler = GameHandler()
game = game_handler.get_game()

# Server loop
def loop():
    while True:
        current_players = game_handler.players
        
        if len(current_players) > 0 and not game.ongoing:
            game.start_game()
            print("Game starting!")
        
        if game.is_crashed():
            game.reset_game()
            print("reseting game!")

thread = Thread(target = loop)
thread.start()

"""
ws expects json
type : join,bid,cashout,lobby,crash,state
name : player name              # only for join messages
amount : amount of money to bid # only for bid messages
state: waiting,bidding,playing  # only for state messages
"""

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    
    await manager.connect(websocket)

    # Maybe make this "while True" a "while connected"?
    while True:
        current_players = game_handler.players
        
        data = await websocket.receive_text()
        message = json.loads(data)
        
        if message["type"] == "join":
            name = message["name"]
            game_handler.join(websocket,name)

            for ws in current_players:
                await ws.send_text(f"{name} joined the lobby!")
            
        elif message["type"] == "bid":
            if not game.ongoing:
                await websocket.send_text(f"A game is not currently in progress.")
            else:
                amount = message["amount"]
                await manager.broadcast(f"{current_players[ws]} bid {amount}.")
        
        elif message["type"] == "cashout":
            if not game.ongoing:
                await websocket.send_text(f"A game is not currently in progress.")
            else:
                await manager.broadcast(f"{current_players[ws]} cashed out with a mult of {game.get_multiplicator()}!")
    
    await manager.disconnect(websocket)
