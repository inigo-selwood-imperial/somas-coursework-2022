import numpy as np

from game.actors.peasant import Peasant

from game.action import Action
from game.state import State


class RandomPeasant(Peasant):

    def __init__(self, level: float):
        stamina = level * np.random.uniform(0.25, 0.75)
        health = level - stamina

        attack = level * np.random.uniform(0.25, 0.75)
        defence = level - attack
    
        super().__init__(stamina, health, attack, defence)

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
