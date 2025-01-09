import pytest
from typing import Callable

from fastapi.testclient import TestClient
from fastapi import WebSocket

from crash.main import app
from crash.player import PlayingPlayer

from pymongo import MongoClient

client = TestClient(app)


@pytest.fixture
def name() -> str:
    return "Franku"


@pytest.fixture
def websocket_connection() -> Callable[[], WebSocket]:
    return lambda: client.websocket_connect("/ws")


def join_message(name: str) -> dict:
    return {"type": "join", "name": name}


def get_obj_attributes(object) -> list[str]:
    return [
        attribute
        for attribute in dir(object)
        if not attribute.startswith("__") and not callable(getattr(object, attribute))
    ]


def test_pass():
    pass


@pytest.fixture()
def players_collection():

    print("setup")
    # Get db using mongo client
    mongo_client = MongoClient("db", 27017, serverSelectionTimeoutMS=2000)
    db = mongo_client.crash

    # Get a players collection just for tests
    collection = db.test_players

    yield collection

    print("teardown")
    db.drop_collection("test_players")


def test_db(name: str, players_collection):

    # Assume player is not in db (wipe at every test)
    assert players_collection.find_one({"name": name}) == None

    # Starting cash and player creation
    cash = 1000
    player = PlayingPlayer(name, cash=cash)

    # Insert player in the db
    player_id = players_collection.insert_one(player.to_db_entry())

    # Now we find the player on the db
    player_info = players_collection.find_one({"name": name, "cash": cash})

    # Load that player information
    player_from_db = PlayingPlayer(name)
    player_from_db = player_from_db.from_db_entry(player_info)

    # Get the attribute of that new objects and compare them
    attributes = get_obj_attributes(player)

    for attribute in attributes:
        assert getattr(player, attribute) == getattr(player_from_db, attribute)


"""
def test_join(name: str, websocket_connection: WebSocket):
    with websocket_connection() as websocket:
        # Send a message
        websocket.send_json(join_message(name))

        # Receive a response
        data = websocket.receive_json()

        # Assertions
        assert data["type"] == "join"
        assert data["target"] == name


def test_two_players(name: str, websocket_connection: WebSocket):
    name1 = name + "1"
    name2 = name + "2"
    with websocket_connection() as websocket:
        with websocket_connection() as websocket2:
            # Send a messages
            websocket.send_json(join_message(name1))
            # Discard initial response (tested in test_join)
            websocket.receive_json()

            websocket2.send_json(join_message(name2))
            

            # Receive a response
            # Should get lobby message triggered by 2nd connection
            data = websocket.receive_json()

            # Assertions
            assert data["type"] == "join"
            assert data["target"] == name2
            assert data["lobby"] == [name1, name2]
"""
