import uuid

import numpy as np

from game.action import Action
from game.state import State


class Peasant:

    def __init__(self, 
            stamina: float, 
            health: float, 
            attack: float, 
            defence: float):
        
        self.stamina = stamina
        self.health = health
        self.attack = health
        self.defence = defence

        self.id = uuid.uuid4().hex[:10]

    def action(self, state: State) -> Action:
        raise NotImplementedError()
    
    def grant_experience(self, experience: float):
        """ Distribute the experience evenly, to achieve a ratio of 
        stamina := 2 * (attack + defence)
        where attack/defence ~= 1
        """

        if (self.attack + self.defence) * 2 < self.stamina:
            defecit = self.stamina - 2 * (self.attack + self.defence)
            delta = min(experience, defecit)
            experience -= delta

            ratio = self.attack / self.defence
            self.attack += delta * ratio
            self.defence += delta * (1 - ratio)
        
        self.stamina += experience * (2 / 3)
        self.attack += experience * (1 / 6)
        self.defence += experience * (1 / 6)