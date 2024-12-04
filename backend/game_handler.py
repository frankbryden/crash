import numpy as np
import time
from threading import Lock


class Game:
    def __init__(
        self,
        name: str,
        starting_multiplicator: float = 0.75,
        multiplicator_coef: float = 0.01,
        average: float = 30,
        standard_deviation: float = 10,
        minimum_time: float = 3,
        players: list = None,
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
        self.starting_multiplicator = starting_multiplicator
        self.multiplicator_coef = multiplicator_coef

        self.players = players or []

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

    # Maybe make time an input instead and remove dependancy on time library
    def get_multiplicator(self) -> float:
        current_game_duration = time.time() - self.initial_time
        if self.game_duration < current_game_duration:
            print("Too late, you lose!")
            return 0
        else:
            multiplicator = self.starting_multiplicator + np.exp(
                self.multiplicator_coef * current_game_duration
            )
            print(
                f"The game has been going on for {current_game_duration}. Your multiplicator : {multiplicator}"
            )
            return multiplicator

    def is_waiting(self) -> bool:
        return (time.time() - self.waiting_initial_time) > 30  # 30 seconds wait for now

    def reset_waiting_time(self):
        self.waiting_initial_time = time.time()

    def is_crashed(self) -> bool:
        if self.ongoing:
            return (time.time() - self.initial_time) > self.game_duration
        else:
            return False  # Game is not crashed, it has not started


class GameHandler:

    def __init__(
        self,
        name: str = "New Lobby",
        average: float = 30,
        standard_deviation: float = 10,
        minimum_time: float = 3,
        starting_multiplicator: float = 0.75,
        multiplicator_coef: float = 0.01,
    ):
        self.name = name
        self.average = average
        self.std = standard_deviation
        self.min_time = minimum_time

        self.starting_multiplicator = starting_multiplicator
        self.multiplicator_coef = multiplicator_coef

        self.players = {}  # ws : name

        self.mutex = Lock()

    # only for some testing
    def test_values(self) -> tuple:
        duration = max(self.min_time, np.random.normal(self.average, self.std))
        time_array = np.linspace(0, duration)
        multiplicator_array = self.starting_multiplicator + np.exp(
            self.multiplicator_coef * time_array
        )
        return duration, multiplicator_array

    def get_game(self, name: str = "New Game") -> Game:

        return Game(
            name,
            starting_multiplicator=self.starting_multiplicator,
            multiplicator_coef=self.multiplicator_coef,
            average=self.average,
            standard_deviation=self.std,
            minimum_time=self.min_time,
        )

    def join(self, ws, name):
        with self.mutex:
            self.players[ws] = name


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
