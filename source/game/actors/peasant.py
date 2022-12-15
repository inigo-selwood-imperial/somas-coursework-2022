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

        # Try to maintain stamina to fully attack/defend
        stamina_boost = 0
        if self.stamina < self.attack + self.defence:
            defecit = (self.attack + self.defence) - self.stamina
            stamina_boost = min(defecit, experience)
        
        # Distribute the remaining experience randomly between attack/defence
        experience_left = experience - stamina_boost
        attack_boost = experience_left * np.random.uniform()
        defence_boost = experience_left - attack_boost

        self.stamina += stamina_boost
        self.attack += attack_boost
        self.defence += defence_boost