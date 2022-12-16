import numpy as np

from game.actors.peasant import Peasant

from game.action import Action
from game.state import State


class RandomPeasant(Peasant):

    def __init__(self, level: float):
        super().__init__(0, 0, 0, 0)
        self.level = level
        self.reset()

    def action(self, state: State) -> Action:
        attack = 0
        defence = 0

        # Attack/defend with a random amount of stamina, half of the time
        if np.random.uniform() > 0.5:
            attack = self.attack * np.random.uniform()
        if np.random.uniform() > 0.5:
            defence = self.defence * np.random.uniform()
        
        # Cap the amount of stamina needed for both actions; do some floating
        # point underflow prevention
        stamina_needed = (attack + defence) * 1.01
        if stamina_needed > self.stamina:
            attack = attack * (self.stamina / stamina_needed)
            defence = defence * (self.stamina / stamina_needed)

        return Action(attack, defence)

    def reset(self):
        self.stamina = self.level * np.random.uniform(0.25, 0.75)
        self.health = self.level - self.stamina

        self.attack = self.level * np.random.uniform(0.25, 0.75)
        self.defence = self.level - self.attack