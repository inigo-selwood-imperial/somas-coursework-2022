import numpy as np


class State:

    def __init__(self, 
            monster, 
            cohort, 
            action,
            combatants: list, 
            abstainers: list,
            round: int,
            turn: int):

        self.combatants = []
        self.abstainers = []

        self.monster = monster
        self.cohort = cohort

        self.combatants = combatants
        self.abstainers = abstainers

        self.action = action

        self.round = round
        self.turn = turn