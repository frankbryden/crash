import pytest
from fastapi.testclient import TestClient
from crash.main import app  # Replace with your actual app import

client = TestClient(app)


def test_websocket(name: str):
    with client.websocket_connect("/ws") as websocket:
        # Send a message
        websocket.send_json({"type": "join", "name": name})

        # Receive a response
        data = websocket.receive_json()

        # Assertions
        assert data["type"] == "response"
        assert data["message"] == "Hello, client!"
