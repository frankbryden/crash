import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocket
from crash.main import app
from typing import Callable

client = TestClient(app)


@pytest.fixture
def name() -> str:
    return "Franku"


@pytest.fixture
def websocket_connection() -> Callable[[], WebSocket]:
    return lambda: client.websocket_connect("/ws")


def join_message(name: str) -> dict:
    return {"type": "join", "name": name}


def test_pass():
    pass


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
