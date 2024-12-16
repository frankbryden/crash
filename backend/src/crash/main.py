from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Union
import json
from threading import Thread, Event, Lock
import asyncio
import time

from crash.game_handler import GameHandler
from crash.utils import run_async_in_thread

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.mutex = Lock()
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        with self.mutex:
            self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        with self.mutex:
            self.active_connections.remove(websocket)

    async def send_personal_message_lobby(self, message: dict, websocket: WebSocket):
        with self.mutex:
            await websocket.send_text(json.dumps(message))

    async def broadcast_lobby(self, message: dict):
        with self.mutex:
            for connection in self.active_connections:
                await connection.send_text(json.dumps(message))


manager = ConnectionManager()

game_handler = GameHandler()
game = game_handler.get_game()

# Event from threading library to get event driven approach :D
# The event is set in the websocket handler for when a player joins
player_join_event = Event()


async def continuously_transmit_mult(stop_event: Event):
    while True:
        await manager.broadcast_lobby(
            {"type": "mult", "mult": game.get_multiplicator()}
        )
        time.sleep(0.02)
        if stop_event.is_set():
            return


# Server loop
async def loop():
    while True:
        current_players = game_handler.players
        # print(current_players)
        # If there is no player we wait for one to save CPU cycles
        if len(current_players) == 0:
            print("Waiting for players...")
            player_join_event.wait()

        # Start timer
        await manager.broadcast_lobby({"type": "state", "state": "waiting"})
        game.blocking_pre_game_wait()

        # Start the game
        game.start_game()
        await manager.broadcast_lobby({"type": "state", "state": "playing"})

        # Send the multiplicator to be drawn
        sender = Thread(
            target=run_async_in_thread,
            args=(lambda: continuously_transmit_mult(game.get_crash_event()),),
        )
        sender.start()

        # Play until crash
        game.wait_for_crash()
        await manager.broadcast_lobby({"type": "state", "state": "crashed"})
        game.reset_game()

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
            print(data)
            message = json.loads(data)

            if message["type"] == "join":

                # A player has joined an empty lobby
                if len(current_players) == 0:
                    player_join_event.set()
                    game.reset_waiting_time()

                name = message["name"]
                game_handler.join(websocket, name)

                # Broadcast the lobby state to everyone
                await manager.broadcast_lobby(
                    {
                        "type": "join",
                        "target": name,
                        "lobby": [player.name for player in current_players.values()],
                        "cash_vaults": game.get_cash_vaults(current_players),
                        "bids": game.get_bids(current_players),
                        "state": "waiting" if game.is_waiting() else "playing",
                    }
                )

            elif message["type"] == "bid":
                if game.ongoing or game.is_crashed():
                    await manager.send_personal_message_lobby(
                        {"type": "error", "message": "Game is already going."},
                        websocket,
                    )
                else:
                    amount = message["amount"]
                    game.bid(websocket, amount)

                    # TODO: find a way to avoid recomputing the whole dicts each time a player makes a bid
                    await manager.broadcast_lobby(
                        {
                            "type": "bid",
                            "target": current_players[websocket].name,
                            "amount": amount,
                            "bids": game.get_bids(current_players),
                            "cash_vaults": game.get_cash_vaults(current_players),
                        }
                    )

            elif message["type"] == "cashout":
                if not game.ongoing:
                    await manager.send_personal_message_lobby(
                        {"type": "error", "message": "Game has not started."}, websocket
                    )
                else:
                    cashout = game.cashout(websocket)

                    if cashout:
                        await manager.broadcast_lobby(
                            {
                                "type": "cashout",
                                "target": current_players[websocket].name,
                                "mult": cashout.mult,
                                "gains": cashout.gain,
                                "cash_vaults": game.get_cash_vaults(current_players),
                                "cashouts": game.get_cashouts(),
                            }
                        )

    except WebSocketDisconnect:

        manager.disconnect(websocket)
        new_player_list = list(current_players.values())
        new_player_list.remove(current_players[websocket])
        await manager.broadcast_lobby(
            {
                "type": "leave",
                "target": current_players[websocket],
                "lobby": new_player_list,
                "bids": game.get_bids(current_players),
                "cash_vaults": game.get_cash_vaults(current_players),
            }
        )
        del game_handler.players[websocket]  # delete the player from the lobby
