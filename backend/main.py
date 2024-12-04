from fastapi import FastAPI, WebSocket
from typing import Union
from pydantic import BaseModel
import json
from threading import Thread, Event
import asyncio
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

    async def send_personal_message_lobby(self, message: dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(message))

    async def broadcast_lobby(self, message: dict):
        for connection in self.active_connections:
            await connection.send_text(json.dumps(message))


manager = ConnectionManager()

game_handler = GameHandler()
game = game_handler.get_game()

# Event from threading library to get event driven approach :D
# The event is set in the websocket handler for when a player joins
player_join_event = Event()


# Server loop
async def loop():
    while True:
        current_players = game_handler.players

        # If there is no player we wait for one to save CPU cycles
        if len(current_players) == 0:
            print("Waiting for players...")
            player_join_event.wait()

        if len(current_players) > 0 and not game.is_waiting() and not game.ongoing:
            game.start_game()
            await manager.broadcast_lobby({"type": "state", "state": "starting"})

        elif game.is_waiting():
            await manager.broadcast_lobby({"type": "state", "state": "waiting"})
            time.sleep(5)

        if game.is_crashed():
            game.reset_game()
            print("Resetting game!")
            # await manager.broadcast_lobby("Resetting game!")
            game.reset_waiting_time()

        # Clear the event so that we can set it again
        # next time a player joins an empty lobby
        player_join_event.clear()


def run_async_loop():
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    event_loop.run_until_complete(loop())


# thread = Thread(target = loop)
thread = Thread(target=run_async_loop, daemon=True)
thread.start()

"""
ws: expected json
type : join,bid,cashout,lobby,crash,state
name : player name              # only for join messages
amount : amount of money to bid # only for bid messages
"""
"""
ws: sent json
type : join,bid,cashout,lobby,crash,state,error
state: waiting,bidding,playing  # only for state messages
message : error message         # only for error messages
mult : multiplicator at cashout # only for cashout messages
"""


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await manager.connect(websocket)

    try:
        # Maybe make this "while True" a "while connected"?
        while True:
            current_players = game_handler.players

            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "join":
                name = message["name"]
                game_handler.join(websocket, name)
                await manager.broadcast_lobby(
                    {
                        "type": "join",
                        "target": name,
                        "lobby": list(current_players.values()),
                    }
                )
                # A player has joined
                player_join_event.set()

            elif message["type"] == "bid":
                if not game.ongoing:
                    await manager.send_personal_message_lobby(
                        {"type": "error", "message": "Game has not started."}
                    )
                else:
                    amount = message["amount"]
                    await manager.broadcast_lobby(
                        {
                            "type": "bid",
                            "target": current_players[websocket],
                            "amount": amount,
                        }
                    )

            elif message["type"] == "cashout":
                if not game.ongoing:
                    await manager.send_personal_message_lobby(
                        {"type": "error", "message": "Game has not started."}
                    )
                else:
                    await manager.broadcast_lobby(
                        {
                            "type": "cashout",
                            "target": current_players[websocket],
                            "mult": game.get_multiplicator(),
                        }
                    )
    except:
        manager.disconnect(websocket)
        new_player_list = list(current_players.values())
        new_player_list.remove(current_players[websocket])
        await manager.broadcast_lobby(
            {
                "type": "leave",
                "target": current_players[websocket],
                "lobby": new_player_list,
            }
        )
        del game_handler.players[websocket]  # delete the player from the lobby