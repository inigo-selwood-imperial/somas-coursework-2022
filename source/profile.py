import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy
import seaborn as sns

from game.game import Game
from game.actors.random_peasant import RandomPeasant

seed = 100
np.random.seed(seed)


def profile_episode(group_size: int = 10,
        base_level: int = 10,
        experience_factor: float = 0.7,
        round_limit: int = 100):
    
    peasants = [RandomPeasant(base_level) for _ in range(group_size)]
    game = Game(peasants,
            experience_factor=experience_factor,
            reward_scheme="combatant-uniform",
            round_limit=round_limit)
    results = game.run()

    figure, axes = plt.subplots(ncols=2)
    
    results.plot.line(ax=axes[0], x="turn", y=["stamina-mean", "cohort-size"])
    results.plot.line(ax=axes[1], x="turn", y=["health-mean"])

    plt.show()


def profile_experience_factor(base_level: int = 10,
        group_size: int = 10,
        round_limit: int = 100,
        games_per_step: int = 5):

    # For each value of experience_factor in the range 0.5, 1.5
    statistics = []
    for experience_factor in range(500, 1500, 25):
        experience_factor /= 1000

        lifespans = []
        stamina_correlations = []
        stamina_gradients = []
        for _ in range(5):
            peasants = [RandomPeasant(base_level) for _ in range(group_size)]
            game = Game(peasants,
                    experience_factor=experience_factor,
                    reward_scheme="combatant-uniform",
                    round_limit=round_limit)
            results = game.run()

            # Get some interesting stats
            turns = len(results)
            rounds = results["round"].max()
        
            # cohort_slope = scipy.stats.linregress(results["turn"], 
            #         results["cohort-size"]).slope

            lifespans.append(results["lifetime-mean"].iloc[-1])
        
            regression = scipy.stats.linregress(results["turn"], 
                    results["stamina-mean"])
            stamina_correlations.append(regression.rvalue)
            stamina_gradients.append(regression.slope)
        
        average_lifespan = np.mean(lifespans)
        average_correlation = np.mean(stamina_correlations)
        average_gradient = np.mean(stamina_gradients)

        results = [
            experience_factor,
            average_lifespan,
            average_correlation,
            average_gradient,
        ]
        statistics.append(results)
    
    headers = [
        "experience-factor",
        "average-lifespan",
        "stamina-correlation",
        "stamina-gradient",
    ]
    table = pd.DataFrame(statistics, columns=headers)

    def add_best_fit(x: str, y: str, name: str):
        best_fit = np.polyfit(x=table.loc[:, x], y=table.loc[:, y], deg=1)
        best_fit = np.poly1d(best_fit)(table.loc[:, x])
        table[name] = best_fit

    add_best_fit("experience-factor", 
            "average-lifespan", 
            "experience-lifetime-trend")
    add_best_fit("experience-factor", 
            "stamina-correlation", 
            "experience-stamina-correlation-trend")
    add_best_fit("experience-factor", 
            "stamina-gradient", 
            "experience-stamina-gradient-trend")

    figure, axes = plt.subplots(ncols=2)
    
    plots = [
        "average-lifespan", 
        "experience-lifetime-trend",
    ]
    table.plot.line(ax=axes[0], x="experience-factor", y=plots)
    
    plots = [
        "stamina-gradient", 
        "experience-stamina-gradient-trend",
    ]
    table.plot.line(ax=axes[1], x="experience-factor", y=plots)

    plt.show()

if __name__ == "__main__":
    assert len(sys.argv) == 2

    if sys.argv[1] == "episode":
        profile_episode()
    elif sys.argv[1] == "phi":
        profile_experience_factor()
    else:
        raise ValueError(f"invalid profile argument: {sys.argv[1]}")