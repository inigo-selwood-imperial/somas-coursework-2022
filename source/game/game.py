import numpy as np
import pandas as pd

from game.cohort import Cohort
from game.state import State
from game.action import Action

from game.actors.monster import Monster


class Game:

    def __init__(self, 
            peasants: list, 
            reward_scheme: str = "uniform", 
            experience_factor: float = 0.75,
            round_limit: int = -1,
            monster_base_level: int = 10,
            monster_level_factor: int = 1.1):
        
        self.monster_base_level = monster_base_level
        self.monster_level_factor = monster_level_factor

        self.reward_scheme = reward_scheme
        self.experience_factor = experience_factor

        self.round_limit = round_limit
        self.round = 0
        self.turn = 0

        self.cohort = Cohort(peasants)
        self.monster = self.spawn_monster()
        self.action = Action(0, 0)

        self.combatants = []
        self.abstainers = []
    
    def distribute_experience(self, peasants: list, experience: float):

        # Rewards all peasants equally
        if self.reward_scheme == "uniform":
            peasant_count = len(peasants)
            for peasant in peasants:
                peasant.grant_experience(experience / peasant_count)
        
        # Rewards all combatants equally
        elif self.reward_scheme == "combatant-uniform":
            combatants = list(set(self.combatants).union(set(peasants)))
            combatant_count = len(combatants)
            for peasant in combatants:
                peasant.grant_experience(experience / combatant_count)

        else:
            raise ValueError(f"invalid reward scheme: {self.reward_scheme}")
    
    def end_turn(self) -> tuple:
        """ Ends the current turn """

        # Consider all peasants combatants if none fought
        if not self.combatants:
            self.combatants = self.cohort.peasants
            self.abstainers = []

        # Track how much damage was dealt
        damage_dealt = self.action.attack 
        monster_killed = self.monster.health - self.action.attack <= 0
        if monster_killed:
            damage_dealt = self.monster.health

        # Track how much damage was avoided
        damage_avoided = 0
        if not monster_killed:
            damage_avoided = self.action.defence
            if self.monster.attack - self.action.defence <= 0:
                damage_avoided = self.monster.attack
        
        # Deal damage to the monster
        self.monster.health -= self.action.attack
        self.monster.health = max(self.monster.health, 0)
        
        # Give some health back to those who didn't fight
        for peasant in self.abstainers:
            peasant.health += 1

        # Deal damage to peasants, track survivors
        death_count = 0
        damage_taken = 0
        survivors = [peasant for peasant in self.abstainers]
        if self.monster.health > 0:
            damage_taken = max(0, self.monster.attack - self.action.defence)

            combatant_count = len(self.combatants)
            for peasant in self.combatants:
                peasant.health -= damage_taken / combatant_count

                if peasant.health > 0:
                    survivors.append(peasant)
                else:
                    death_count += 1
        
        # If the monster died, nobody takes damage
        else:
            survivors = self.cohort.peasants
            
        # Evaluate and distribute experience reward
        experience = damage_dealt / self.monster.base_health
        experience += damage_avoided / self.monster.attack
        experience *= self.monster.level * self.experience_factor
        self.distribute_experience(survivors, experience)
    
        # Start a new round, if the game hasn't finished
        pit_escaped = self.round_limit != -1 and self.round + 1 >= self.round_limit
        finished = pit_escaped or not survivors

        survivor_staminas = [peasant.stamina for peasant in survivors]
        survivor_healths = [peasant.health for peasant in survivors]

        def average(values: list) -> float:
            return sum(values) / len(values) if values else 0
        
        # Display some round information
        status = {
            "round": self.round,
            "turn": self.turn,
            
            "cohort-size": len(self.cohort.peasants),

            "combatants": len(self.combatants),
            "abstainers": len(self.abstainers),

            "monster-level": self.monster.level,
            "monster-health": self.monster.health,

            "experience-gained": experience,

            "damage-dealt": damage_dealt,
            "damage-avoided": damage_avoided,
            "damage-taken": damage_taken,
            "experience-gained": experience,

            "stamina-mean": average(survivor_staminas),
            "health-mean": average(survivor_healths),
        }

        if not finished:
            self.action = Action(0, 0)
            self.cohort = Cohort(survivors)

            self.combatants = []
            self.abstainers = []

            self.turn += 1

            if monster_killed:
                self.monster = self.spawn_monster()
                self.round += 1
        
        return finished, status
    
    def run(self) -> pd.DataFrame:
        keys = []
        statistics = []
        
        while True:
            finished, turn_statistics = self.step()

            if turn_statistics:
                values = list(turn_statistics.values())
                statistics.append(values)
                if finished:
                    keys = list(turn_statistics.keys())
            
            if finished:
                break
        
        dataframe = pd.DataFrame(statistics, columns=keys)
        return dataframe
    
    def spawn_monster(self) -> Monster:
        level = self.monster_base_level \
                    * (self.round + 1) \
                    * self.monster_level_factor
        health = level * np.random.uniform(0.25, 0.75)
        attack = level - health
        return Monster(health, attack)

    def state(self) -> State:
        return State(self.monster, 
                self.cohort, 
                self.action, 
                self.combatants, 
                self.abstainers,
                self.round,
                self.turn)

    def step(self) -> tuple:

        # Fetch a random peasant
        peasant, cohort_spanned = self.cohort.iterate()

        # Get their action
        action = peasant.action(self.state())

        self.action.attack += action.attack
        self.action.defence += action.defence
        peasant.stamina -= action.attack + action.defence

        # Keep track of combatants
        if action.attack or action.defence:
            self.combatants.append(peasant)
        else:
            self.abstainers.append(peasant)

        return self.end_turn() if cohort_spanned else (False, None)