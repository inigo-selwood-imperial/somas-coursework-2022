import yaml

import numpy as np
import pandas as pd

from game.cohort import Cohort
from game.state import State
from game.action import Action

from game.actors.monster import Monster
from game.actors.peasant import Peasant


class Game:

    def __init__(self, 
            peasants: list, 
            reward_scheme: str = "uniform", 
            experience_factor: float = 0.9,
            round_limit: int = 100,
            monster_base_level: int = 10,
            monster_level_factor: int = 1.05,
            reward_weights: tuple = [1] * 7):
        
        self.monster_base_level = monster_base_level
        self.monster_level_factor = monster_level_factor

        self.reward_scheme = reward_scheme
        self.experience_factor = experience_factor
        self.weights = reward_weights

        self.round_limit = round_limit
        self.round = 0
        self.turn = 0

        self.cohort = Cohort(peasants)
        self.monster = self.spawn_monster()
        self.action = Action(0, 0)

        self.combatants = []
        self.abstainers = []

        self.lifetimes = []
        self.rewards = {}
    
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
        
        elif self.reward_scheme == "socially-conscious":
            pass

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
                    self.lifetimes.append(self.round)
        
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
            return sum(values) / len(values) if values else self.round
        
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
            "lifetime-mean": average(self.lifetimes) if self.lifetimes else self.round,
        }

        # print(yaml.dump(status))

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
    
    def evaluate_reward(self, peasant: Peasant, action: Action) -> float:
        group_attack = self.action.attack
        group_defence = self.action.defence

        combined_attack = group_attack + action.attack
        combined_defence = group_defence + action.defence

        potential_attack = min(peasant.stamina, peasant.attack)
        potential_defence = min(peasant.stamina, peasant.defence)

        # True if the peasant's actions killed the monster or saved the group
        # Note that killing the monster also saves the group
        killed_monster = (self.action.attack < self.monster.health 
                and combined_attack >= self.monster.health)
        saved_group = (killed_monster
                or (self.monster.attack > self.action.defence 
                    and combined_defence >= self.monster.attack))
        
        # True if the monster is already dead, or the group already saved
        monster_killed = group_attack >= self.monster.health
        group_saved = monster_killed or self.monster.attack <= group_defence

        # True if the player is capable of killing the monster
        monster_killable = not monster_killed and (self.monster.health <= 
                self.action.attack + potential_attack)
        group_saveable = not group_saved and (self.monster.attack <= 
                self.action.defence + potential_defence)

        acted = action.attack or action.defence

        group_size = len(self.cohort.peasants)

        position = len(self.combatants) + len(self.abstainers)
        completion_percentage = group_size / position if position else 0
        
        # True if the monster is stronger than the peasant by a margin
        health_low = self.monster.health * 0.5 >= peasant.health
        stamina_low = self.monster.attack * 0.5 >= peasant.stamina

        # Rewarded attributes
        weak = health_low or stamina_low
        heroic = killed_monster or saved_group
        early = acted and completion_percentage < 1 / group_size
        brave = acted and (health_low or stamina_low) 
        generous = (not monster_killed 
                and not group_saved 
                and (action.attack + action.defence) >= 0.5 * peasant.stamina)
    
        # Penalized attributes
        selfish = ((not monster_killed and monster_killable)
                or (not group_saved and group_saveable))
        foolish = ((action.attack and monster_killed)
                or (action.defence and group_saved))

        criteria = [
            weak,
            heroic,
            early,
            brave,
            generous,

            -int(selfish),
            -int(foolish),
        ]
        
        # Weight attributes and sum result
        assert len(self.weights) == len(criteria), "weight dimensions invalid"
        pairs = zip(criteria, self.weights)
        weighted_criteria = [weight * criteria for (weight, criteria) in pairs]
        
        return sum(weighted_criteria)

    def step(self) -> tuple:

        # Fetch a random peasant
        peasant, cohort_spanned = self.cohort.iterate()

        # Get their action
        action = peasant.action(self.state())

        # Evaluate experience reward
        reward = self.evaluate_reward(peasant, action)
        self.rewards[peasant.id] = reward

        self.action.attack += action.attack
        self.action.defence += action.defence
        peasant.stamina -= action.attack + action.defence

        # Keep track of combatants
        if action.attack or action.defence:
            self.combatants.append(peasant)
        else:
            self.abstainers.append(peasant)

        return self.end_turn() if cohort_spanned else (False, None)