import numpy as np

from game.actors.peasant import Peasant


class Cohort:

    def __init__(self, peasants: list):
        self.position = 0

        self.peasants = peasants
        self.indices = list(range(len(peasants)))
        np.random.shuffle(self.indices)
    
    def iterate(self) -> tuple:
        assert self.indices

        index = self.indices[-1]
        self.indices = self.indices[:-1]

        peasant = self.peasants[index]
        done = not self.indices

        self.position += 1
        
        return peasant, done