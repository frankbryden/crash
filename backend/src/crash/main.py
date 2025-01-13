from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
from contextlib import asynccontextmanager
import asyncio
from pymongo import MongoClient

from crash.game_handler import GameHandler
from crash.player import PlayingPlayer
import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
)


class ConnectionManager:
    def __init__(self):
        self.mutex = asyncio.Lock()
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self.mutex:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self.mutex:
            self.active_connections.remove(websocket)

    async def send_personal_message_lobby(self, message: dict, websocket: WebSocket):
        async with self.mutex:
            logging.info(f"[send_personal_message_lobby] sending {message}")
            await websocket.send_text(json.dumps(message))

    async def broadcast_lobby(self, message: dict):
        async with self.mutex:
            for connection in self.active_connections:
                await connection.send_text(json.dumps(message))


# Connect to Mongo, get db and the player collection
mongo_client = MongoClient("db", 27017, serverSelectionTimeoutMS=2000)
db = mongo_client.crash
players_collection = db.players

manager = ConnectionManager()

game_handler = GameHandler()
game = game_handler.get_game()

# Event from threading library to get event driven approach :D
# The event is set in the websocket handler for when a player joins
player_join_event = asyncio.Event()


async def continuously_transmit_mult(stop_event: asyncio.Event):
    while not stop_event.is_set():
        await manager.broadcast_lobby(
            {"type": "mult", "mult": game.get_multiplicator()}
        )
        await asyncio.sleep(0.02)


# Server loop
async def loop():
    while True:
        current_players = game_handler.players
        # logging.info(current_players)
        # If there is no player we wait for one to save CPU cycles
        if len(current_players) == 0:
            logging.info("Waiting for players...")
            await player_join_event.wait()

        # Start timer
        estimated_start_time = await game.start_pre_game_wait()
        await manager.broadcast_lobby(
            {
                "type": "state",
                "state": "waiting",
                "estimated_start": estimated_start_time,
            }
        )
        await game.wait_for_game_start()

        # Start the game
        await game.start_game()
        await manager.broadcast_lobby({"type": "state", "state": "playing"})

        # Send the multiplicator to be drawn until crash
        await continuously_transmit_mult(game.get_crash_event())

        # await asyncio.gather(transmitter_task, crash_task)
        await asyncio.gather(
            asyncio.shield(continuously_transmit_mult(game.get_crash_event())),
            game.wait_for_crash(),
        )

        await manager.broadcast_lobby(
            {
                "type": "state",
                "state": "crashed",
                "cash_vaults": game.get_cash_vaults(game_handler.players),
            }
        )
        # We update the player history (bids, gains and multipliers)
        game.update_players_history()
        game.reset_game()

        # Clear the event so that we can set it again
        # next time a player joins an empty lobby
        player_join_event.clear()


def run_async_loop():
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    event_loop.run_until_complete(loop())


@asynccontextmanager
async def lifespan(app: FastAPI):
    event_loop = asyncio.get_event_loop()
    asyncio.ensure_future(loop(), loop=event_loop)
    yield


app = FastAPI(lifespan=lifespan)

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

            data = await websocket.receive_text()
            logging.info(data)
            message = json.loads(data)

            if message["type"] == "join":

                # A player has joined an empty lobby
                if len(game_handler.players) == 0:
                    player_join_event.set()
                    game.reset_waiting_time()

                # Name will be google id string later
                name = message["name"]

                player_info = players_collection.find_one({"name": name})
                # Check if player is in the db
                if player_info == None:
                    # If not, we create their doc
                    cash = 1000
                    player = PlayingPlayer(name, cash=cash)
                    player_id = players_collection.insert_one(player.to_db_entry())
                    print("Player added to db with id :", player_id)
                else:
                    player = PlayingPlayer.from_db_entry(player_info)

                await game_handler.join(websocket, player)
                logging.info("Sending personal message for gift")
                await manager.send_personal_message_lobby(
                    {
                        "type": "gift",
                        "next_available_gift": player.get_gift_claim_time(),
                    },
                    websocket,
                )

                # Broadcast the lobby state to everyone
                await manager.broadcast_lobby(
                    {
                        "type": "join",
                        "target": name,
                        "lobby": [
                            player.name for player in game_handler.players.values()
                        ],
                        "cash_vaults": game.get_cash_vaults(game_handler.players),
                        "bids": game.get_bids(game_handler.players),
                        "state": "playing" if game.is_playing() else "waiting",
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
                            "target": game_handler.players[websocket].name,
                            "amount": amount,
                            "bids": game.get_bids(game_handler.players),
                            "cash_vaults": game.get_cash_vaults(game_handler.players),
                            "cashouts": game.get_cashouts(),
                        }
                    )

            elif message["type"] == "cashout":
                if not game.ongoing:
                    await manager.send_personal_message_lobby(
                        {"type": "error", "message": "Game has not started."}, websocket
                    )
                else:
                    cashout = game.cashout(websocket)
                    logging.info(cashout)
                    if cashout:
                        await manager.broadcast_lobby(
                            {
                                "type": "cashout",
                                "target": game_handler.players[websocket].name,
                                "mult": cashout.mult,
                                "gains": cashout.gain,
                                "cash_vaults": game.get_cash_vaults(
                                    game_handler.players
                                ),
                                "cashouts": game.get_cashouts(),
                            }
                        )

    except WebSocketDisconnect:

        await manager.disconnect(websocket)
        new_player_list = [player.name for player in game_handler.players.values()]
        new_player_list.remove(game_handler.players[websocket].name)
        print("new lobby list : ", new_player_list)
        await manager.broadcast_lobby(
            {
                "type": "leave",
                "target": game_handler.players[websocket].name,
                "lobby": new_player_list,
                "bids": game.get_bids(game_handler.players),
                "cash_vaults": game.get_cash_vaults(game_handler.players),
            }
        )
        # Update the information in the db
        print("Updating player in db")
        print(game_handler.players[websocket].to_db_entry())
        players_collection.update_one(
            {"name": game_handler.players[websocket].name},
            {
                "$set": {
                    "cash": game_handler.players[websocket].cash,
                    "bid_history": game_handler.players[websocket].bid_history,
                    "gain_history": game_handler.players[websocket].gain_history,
                    "mult_history": game_handler.players[websocket].mult_history,
                },
            },
        )
        del game_handler.players[websocket]  # delete the player from the lobby
