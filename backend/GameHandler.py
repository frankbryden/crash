import numpy as np
import time

class Game:
    def __init__(self,name : str,duration : float,starting_multiplicator : float = 0.75,multiplicator_coef : float = 0.01):
        self.name = name
        self.duration = duration
        self.game_started = False
        self.initial_time = None

        self.starting_multiplicator = starting_multiplicator
        self.multiplicator_coef = multiplicator_coef
        
    def start_game(self):
        if not self.game_started: 
            self.game_started = True
            self.initial_time = time.time()
        else:
            print("Game already started.")

    # Maybe make time an input instead and remove dependancy on time library
    def get_multiplicator(self) -> float:
        if not self.game_started:
            print("The game has not started yet.")
            return 0
        current_game_duration = (time.time() - self.initial_time)
        if self.duration < current_game_duration:
            print("Too late, you lose!")
            return 0
        else :
            multiplicator = self.starting_multiplicator + np.exp( self.multiplicator_coef * current_game_duration)
            print(f"The game has been going on for {current_game_duration}. Your multiplicator : {multiplicator}")
            return multiplicator


class GameHandler:
    
    def __init__(self, name : str = "New Lobby", average : float = 30,standard_deviation : float = 10,
                 minimum_time : float = 3, starting_multiplicator : float = 0.75,multiplicator_coef : float = 0.01):
        self.name = name
        self.average = average
        self.std = standard_deviation
        self.min_time = minimum_time

        self.starting_multiplicator = starting_multiplicator
        self.multiplicator_coef = multiplicator_coef
    
    # only for some testing
    def test_values(self) -> tuple: 
        duration = max(self.min_time,np.random.normal(self.average,self.std))
        time_array = np.linspace(0,duration)
        multiplicator_array = self.starting_multiplicator + np.exp( self.multiplicator_coef * time_array)
        return duration,multiplicator_array

    def get_game(self,name : str = "New Game")-> Game:
        game_total_duration = max(self.min_time,np.random.normal(self.average,self.std)) 
        return Game(name ,duration = game_total_duration,
                    starting_multiplicator = self.starting_multiplicator,
                    multiplicator_coef = self.multiplicator_coef)


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    game_handler = GameHandler()
    durations = []
    multiplicators = []
    for i in range(10000):
        duration,multiplicator_array = game_handler.test_values()
        durations.append(duration)
        multiplicators.append(multiplicator_array[-1])
    
    plt.figure()
    plt.hist(durations,bins = 50)
    plt.show()
    plt.figure()
    plt.yscale("log")
    plt.hist(multiplicators,bins = 50)
    plt.show()
