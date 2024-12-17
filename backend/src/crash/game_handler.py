import numpy as np
import time
from typing import Tuple, Dict
from fastapi import WebSocket
from threading import Lock, Event, Thread

from crash.player import PlayingPlayer, Player
from crash.records import Cashout, CashoutMessage
from crash.utils import sleep_and_go

GAME_WAIT_TIME_S = 10


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

    def join(self, ws, name, cash):
        with self.mutex:
            self.players[ws] = Player(name, cash)


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
        # Game will block on the waiting state until this fires
        self.start_event = Event()
        self.crash_event = Event()

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
            Thread(target=self.launch_crash_timer).start()
            return True
        else:
            print("Game already started.")
            return False

    def blocking_pre_game_wait(self):
        sleep_and_go(GAME_WAIT_TIME_S, self.start_event)
        self.start_event.wait()

    def reset_game(self):
        self.ongoing = False
        self.players = {}
        self.crash_event.clear()
        self.start_event.clear()
        self.game_duration = max(
            self.min_time, np.random.normal(self.average, self.std)
        )

    def bid(self, ws, amount):
        cash_available = self.game_handler_parent.players[ws].cash
        bid_amount = min(amount, cash_available)

        # Was player not here at round start?
        if ws not in self.players:
            # Player is created and added to the round
            self.players[ws] = PlayingPlayer(self.game_handler_parent.players[ws].name)

        # Players can only bid once
        if self.players[ws].bid(bid_amount):
            self.game_handler_parent.players[ws].cash -= bid_amount

    # Maybe make time an input instead and remove dependancy on time library
    def get_multiplicator(self) -> float:
        current_game_duration = time.time() - self.initial_time
        if self.game_duration < current_game_duration:
            return 0
        else:
            multiplicator = np.exp(self.multiplicator_coef * current_game_duration)
            return np.round(multiplicator, decimals=2)

    def cashout(self, ws) -> Cashout:
        if ws in self.players and not self.players[ws].cashout_record:
            mult = self.get_multiplicator()
            cashout = self.players[ws].cashout(mult)
            self.game_handler_parent.players[ws].cash += cashout.gain
            return cashout

    def get_cash_vaults(self, current_players: dict) -> Dict[str, int]:
        cash_dict = {}
        for ws in current_players:
            if ws in self.game_handler_parent.players:
                cash_dict[current_players[ws].name] = self.game_handler_parent.players[
                    ws
                ].cash

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
        return (
            time.time() - self.waiting_initial_time
        ) < GAME_WAIT_TIME_S  # 10 seconds wait for now

    def reset_waiting_time(self):
        self.waiting_initial_time = time.time()

    def is_crashed(self) -> bool:
        if self.ongoing:
            return (time.time() - self.initial_time) > self.game_duration
        else:
            return False  # Game is not crashed, it has not started

    def launch_crash_timer(self):
        sleep_and_go(self.game_duration, self.crash_event)

    def get_crash_event(self):
        return self.crash_event

    def wait_for_crash(self):
        self.crash_event.wait()

    def update_players_history(self):
        for ws, player in self.players.items():
            lobby_player = self.game_handler_parent.players[ws]
            cashout = player.cashout_record
            # Save history only if the player has bid
            if player.has_bid:
                lobby_player.bid_history.append(player.bid_value)
                # Checks if the player has managed to cashout before crash
                if cashout != None:
                    lobby_player.gain_history.append(cashout.gain)
                    lobby_player.mult_history.append(cashout.mult)
                else:
                    lobby_player.gain_history.append(-1 * player.bid_value)
                    lobby_player.mult_history.append(0)


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
