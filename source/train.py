import sys
import os; os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
import random
import datetime
import itertools

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as matplt
import tensorflow as tf
import scipy
import mpl_toolkits as plt_tlk

from tensorflow import keras
# import scipy

from learning.experience_buffer import ExperienceBuffer

from game.game import Game
from game.actors.random_peasant import RandomPeasant
from game.actors.ddpg_peasant import DDPGPeasant


def _plot(statistics: pd.DataFrame):    
    plots = [
        "average-reward", 
        "network-lifespan", 
        "average-lifespan"
    ]
    statistics.plot(x="episode", y=plots)
    plt.show()


def _train(training_peasant: DDPGPeasant,
        peasants: list,
        epochs: int = 100,
        verbose: bool = True,
        **arguments):

    peasants.append(training_peasant)

    rewards = []
    lifespans = []
    statistics = []
    for episode in range(epochs):
        for peasant in peasants:
            peasant.reset()

        game = Game(peasants, **arguments)
        results = game.run()

        reward = np.mean(training_peasant.rewards)
        lifespan = training_peasant.previous_round

        rewards.append(reward)
        lifespans.append(lifespan)

        average_reward = np.mean(rewards[-40:])
        network_lifespan = np.mean(lifespans[-40:])
        average_lifespan = results["lifetime-mean"].iloc[-1]

        results = [
            episode, 
            average_reward, 
            network_lifespan, 
            average_lifespan,
        ]
        statistics.append(results)

        if verbose:
            report = []
            for result in results:
                if isinstance(result, float):
                    report.append(f"{result:.3}")
                else:
                    report.append(f"{result}")
            print(", ".join(report))

    headers = [
        "episode", 
        "average-reward", 
        "network-lifespan", 
        "average-lifespan",
    ]
    statistics = pd.DataFrame(statistics, columns=headers)
    return statistics


def train_random():
    training_peasant = DDPGPeasant(10)
    peasants = [RandomPeasant(10) for _ in range(9)]
    statistics = _train(training_peasant, 
            peasants, 
            epochs=200, 
            reward_scheme="combatant-uniform")
    _plot(statistics)


def train_random_incremental(steps_per_epoch: int = 25,
        cohort_size: int = 5):
    
    training_peasant = DDPGPeasant(10, 
            weight_file="resources/weights/random-unrewarded")

    statistics = None
    for proportion in range(cohort_size - 1):

        peasants = [RandomPeasant(10) for _ in range(cohort_size - proportion)]
        for _ in range(proportion):
            intelligent_peasant = DDPGPeasant(10, 
                    weight_file="resources/weights/random-unrewarded",
                    train=False)
            peasants.append(intelligent_peasant)

        new_statistics = _train(training_peasant, 
                peasants, 
                epochs=steps_per_epoch,
                reward_scheme="combat-uniform")
        if statistics is None:
            statistics = new_statistics
        else:
            new_statistics["episode"] = (new_statistics["episode"] 
                    + proportion * steps_per_epoch)
            statistics = pd.concat([statistics, new_statistics])
    
    _plot(statistics)
    training_peasant.save("resources/weights/intelligent-unrewarded")


def profile_multivariable(steps_per_epoch: int = 10):

    statistics = []
    for weight_early in range(0, 160, 20):
        weight_early /= 100

        for weight_generous in range(0, 160, 20):
            weight_generous /= 100

            training_peasant = DDPGPeasant(10, weight_file="resources/weights/random-unrewarded")
            peasants = []
            for _ in range(4):
                peasants.append(RandomPeasant(10))

            weights = [
                1,
                -0.5,
                weight_early,
                -0.25,
                weight_generous,
                1,
                1,
            ]

            simulation = _train(training_peasant,
                    peasants,
                    epochs=steps_per_epoch,
                    reward_scheme="socially-conscious",
                    verbose=False,
                    reward_weights=weights,
                    monster_base_level=5,
                    monster_level_factor=1.05)
            lifetime = np.mean(simulation["average-lifespan"])

            print(f"{weight_early}, {weight_generous}: {lifetime:.3}")
            statistics.append([weight_early, weight_generous, lifetime])
    
    table = pd.DataFrame(statistics, 
            columns=["weight-early", "weight-generous", "lifetime"])
        
    table.to_csv("output.csv")

    figure = plt.figure()
    axes = figure.add_subplot(projection='3d')
    axes.plot_trisurf(table["weight-early"], table["weight-generous"], table["lifetime"], linewidth=2, antialiased=True)
    plt.show()


def profile_cooperation(steps_per_epoch: int = 10):

    results = []
    for index in range(7):

        statistics = []
        for weight in range(0, 160, 20):
            weight /= 100

            training_peasant = DDPGPeasant(10, weight_file="resources/weights/random-unrewarded")
            peasants = []
            for _ in range(4):
                peasants.append(RandomPeasant(10))

            weights = [1] * 7
            weights[index] = weight

            simulation = _train(training_peasant,
                    peasants,
                    epochs=steps_per_epoch,
                    reward_scheme="uniform",
                    verbose=False,
                    reward_weights=weights,
                    monster_base_level=5,
                    monster_level_factor=1.05)
            lifetime = np.mean(simulation["average-lifespan"])

            print(f"{index}, {weight}: {lifetime:.3}")
            statistics.append([weight, lifetime])
    
        table = pd.DataFrame(statistics, columns=["weight", "lifetime"])
        correlation = table["weight"].corr(table["lifetime"])
        results.append([index, correlation])

    table = pd.DataFrame(results, columns=["weight-index", "correlation"])
    print(table)
    table.plot.bar(x="weight-index", y="correlation")
    plt.show()


if __name__ == "__main__":
    assert len(sys.argv) == 2

    seed = 100
    np.random.seed(seed)
    tf.random.set_seed(seed)
    keras.utils.set_random_seed(seed)

    if sys.argv[1] == "random":
        train_random()
    elif sys.argv[1] == "incremental":
        train_random_incremental()
    elif sys.argv[1] == "cooperative":
        profile_cooperation()
    elif sys.argv[1] == "multivariable":
        profile_multivariable()
    else:
        raise ValueError(f"invalid train argument: {sys.argv[1]}")
