import numpy as np
import time
from threading import Lock


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

        self.players = {}  # ws : name

        self.cash = {}  # ws : cash

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
            multiplicator_coef=self.multiplicator_coef,
            average=self.average,
            standard_deviation=self.std,
            minimum_time=self.min_time,
            game_handler_parent=self,
        )

    def join(self, ws, name):
        with self.mutex:
            self.players[ws] = name

            if ws not in self.cash:
                self.cash[ws] = 1000


class Game:
    def __init__(
        self,
        name: str,
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

        self.bids = {}  # ws : bid

    def start_game(self):
        if not self.ongoing:
            self.game_duration = max(
                self.min_time, np.random.normal(self.average, self.std)
            )
            self.ongoing = True
            self.initial_time = time.time()
        else:
            print("Game already started.")

    def reset_game(self):
        self.ongoing = False
        self.game_duration = max(
            self.min_time, np.random.normal(self.average, self.std)
        )

    def bid(self, ws, amount):
        cash_available = self.game_handler_parent.cash[ws]
        bid_amount = min(amount, cash_available)

        # Players can only bid once
        if ws not in self.bids and bid_amount > 0:
            self.bids[ws] = bid_amount
            self.game_handler_parent.cash[ws] -= bid_amount

    # Maybe make time an input instead and remove dependancy on time library
    def get_multiplicator(self) -> float:
        current_game_duration = time.time() - self.initial_time
        if self.game_duration < current_game_duration:
            return 0
        else:
            multiplicator = np.exp(self.multiplicator_coef * current_game_duration)
            return np.round(multiplicator, decimals=2)

    def cashout(self, ws):
        if ws in self.bids:
            gain = self.get_multiplicator() * self.bids[ws]
            self.bids.pop(ws)
            self.game_handler_parent.cash[ws] += gain
            return gain

    def get_cash_vaults(self, current_players: dict) -> dict:
        cash_dict = {}
        for ws in current_players:
            if ws in self.game_handler_parent.cash:
                cash_dict[current_players[ws]] = self.game_handler_parent.cash[ws]

        return cash_dict

    def get_bids(self, current_players: dict) -> dict:
        bids_dict = {}
        for ws in current_players:
            if ws in self.bids:
                bids_dict[current_players[ws]] = self.bids[ws]

        return bids_dict

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
