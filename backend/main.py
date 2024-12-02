from fastapi import FastAPI
from typing import Union
from pydantic import BaseModel

from GameHandler import GameHandler

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


game_handler = GameHandler()
game = game_handler.get_game()


@app.post("/game/start")
async def start():
    if game.game_started:
        return {"gamestate":"Game already started"}
    else :
        game.start_game()
        return {"gamestate":"Game starting!"}

@app.put("/game/{name}")
async def play(name: str):
    if not game.game_started:
        return {"gamestate":"Game not started yet"}
    else :
        return {"name" : name , "mult" : game.get_multiplicator()}

