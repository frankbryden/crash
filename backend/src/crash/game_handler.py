import numpy as np
import time
from typing import Tuple, Dict
from fastapi import WebSocket
from threading import Lock

from crash.player import PlayingPlayer, Player
from crash.records import Cashout, CashoutMessage


class GameHandler:

    def __init__(
        self,
        name: str = "New Lobby",
        average: float = 30,
        standard_deviation: float = 10,
        minimum_time: float = 3,
        starting_multiplicator: float = 0.75,
        multiplicator_coef: float = 0.1,
    ):
        self.name = name
        self.average = average
        self.std = standard_deviation
        self.min_time = minimum_time

        self.starting_multiplicator = starting_multiplicator
        self.multiplicator_coef = multiplicator_coef

        self.players: Dict[WebSocket, Player] = {}

        self.cash: Dict[WebSocket:int] = {}

        # For concurrent access
        self.mutex = Lock()

    # only for some testing
    def test_values(self) -> tuple:
        duration = max(self.min_time, np.random.normal(self.average, self.std))
        time_array = np.linspace(0, duration)
        multiplicator_array = self.starting_multiplicator + np.exp(
            self.multiplicator_coef * time_array
        )
        return duration, multiplicator_array

    def get_game(self, name: str = "New Game"):

        return Game(
            name,
            self.players,
            multiplicator_coef=self.multiplicator_coef,
            average=self.average,
            standard_deviation=self.std,
            minimum_time=self.min_time,
            game_handler_parent=self,
        )

    def join(self, ws, name):
        with self.mutex:
            self.players[ws] = Player(name, 1000)

            if ws not in self.cash:
                self.cash[ws] = 1000


class Game:
    def __init__(
        self,
        name: str,
        players: Dict[WebSocket, Player],
        multiplicator_coef: float = 0.01,
        average: float = 30,
        standard_deviation: float = 10,
        minimum_time: float = 3,
        game_handler_parent: GameHandler = None,
    ):

        self.name = name

        self.average = average
        self.std = standard_deviation
        self.min_time = minimum_time

        self.ongoing = False

        # Game begins in the waiting state
        self.waiting_initial_time = time.time()

        self.initial_time = None
        self.game_duration = None
        self.multiplicator_coef = multiplicator_coef

        self.game_handler_parent = game_handler_parent

        self.players: Dict[WebSocket, PlayingPlayer] = {
            ws: PlayingPlayer(player.name) for ws, player in players.items()
        }

    def start_game(self) -> bool:
        if not self.ongoing:
            self.game_duration = max(
                self.min_time, np.random.normal(self.average, self.std)
            )
            self.ongoing = True
            self.initial_time = time.time()
            return True
        else:
            print("Game already started.")
            return False

    def reset_game(self):
        self.ongoing = False
        self.game_duration = max(
            self.min_time, np.random.normal(self.average, self.std)
        )

    def bid(self, ws, amount):
        cash_available = self.game_handler_parent.cash[ws]
        bid_amount = min(amount, cash_available)

        # Was player not here at round start?
        if ws not in self.players:
            # Player is created and added to the round
            self.players[ws] = PlayingPlayer(self.game_handler_parent.players[ws].name)

        # Players can only bid once
        if self.players[ws].bid(bid_amount):
            self.game_handler_parent.cash[ws] -= bid_amount

    # Maybe make time an input instead and remove dependancy on time library
    def get_multiplicator(self) -> float:
        current_game_duration = time.time() - self.initial_time
        if self.game_duration < current_game_duration:
            return 0
        else:
            multiplicator = np.exp(self.multiplicator_coef * current_game_duration)
            return np.round(multiplicator, decimals=2)

    def cashout(self, ws) -> Cashout:
        if ws in self.players:
            mult = self.get_multiplicator()
            cashout = self.players[ws].cashout(mult)
            self.game_handler_parent.cash[ws] += cashout.gain
            return cashout

    def get_cash_vaults(self, current_players: dict) -> Dict[str, int]:
        cash_dict = {}
        for ws in current_players:
            if ws in self.game_handler_parent.cash:
                cash_dict[current_players[ws].name] = self.game_handler_parent.cash[ws]

        return cash_dict

    def get_bids(self, current_players: dict) -> Dict[str, int]:
        bids_dict = {}
        for ws in current_players:
            if ws in self.players:
                bids_dict[current_players[ws].name] = self.players[ws].bid_value

        return bids_dict

    def get_cashouts(self) -> Dict[str, CashoutMessage]:
        return {
            player.name: {
                "bid": player.bid_value,
                "gain": getattr(player.cashout_record, "gain", -1),
                "mult": getattr(player.cashout_record, "mult", -1),
            }
            for player in self.players.values()
        }

    # States management
    def is_waiting(self) -> bool:
        return (time.time() - self.waiting_initial_time) < 10  # 10 seconds wait for now

    def reset_waiting_time(self):
        self.waiting_initial_time = time.time()

    def is_crashed(self) -> bool:
        if self.ongoing:
            return (time.time() - self.initial_time) > self.game_duration
        else:
            return False  # Game is not crashed, it has not started


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    game_handler = GameHandler()
    durations = []
    multiplicators = []
    for i in range(10000):
        duration, multiplicator_array = game_handler.test_values()
        durations.append(duration)
        multiplicators.append(multiplicator_array[-1])

    plt.figure()
    plt.hist(durations, bins=50)
    plt.show()
    plt.figure()
    plt.yscale("log")
    plt.hist(multiplicators, bins=50)
    plt.show()
