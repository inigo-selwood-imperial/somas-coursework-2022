import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy


from game.game import Game
from game.actors.random_peasant import RandomPeasant


def profile(base_level: int = 10,
        group_size: int = 10,
        round_limit: int = 100,
        games_per_step: int = 5):

    # For each value of experience_factor in the range 0.5, 1.5
    rows = []
    for experience_factor in range(500, 1500, 100):
        experience_factor /= 1000

        columns = []
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
        
            cohort_slope = scipy.stats.linregress(results["turn"], 
                    results["cohort-size"]).slope
            
            level_regression = scipy.stats.linregress(results["turn"], 
                    results["level-mean"])
            level_slope = level_regression.slope
            level_correlation = level_regression.rvalue

            columns.append([
                experience_factor,
                turns,
                rounds,
                cohort_slope,
                level_slope,
                level_correlation,
            ])
        
        transpose = np.transpose(columns)
        rows.append(np.average(row) for row in transpose)
    
    table = pd.DataFrame(rows, columns=["phi", "turns", "rounds", "cohort-slope", "level-slope", "level-correlation"])
    print(table)
    
    figure, axes = plt.subplots(ncols=3)
    table.plot.line(ax=axes[0], x="phi", y=["turns", "rounds"])
    table.plot.line(ax=axes[1], x="phi", y=["cohort-slope", "level-slope"])
    table.plot.scatter(ax=axes[2], x="phi", y="level-correlation")
    plt.show()

if __name__ == "__main__":
    profile()