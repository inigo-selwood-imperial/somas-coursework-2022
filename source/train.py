import sys
import os; os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
import random
import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf

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

        new_statistics = _train(training_peasant, peasants, epochs=steps_per_epoch)
        if statistics is None:
            statistics = new_statistics
        else:
            new_statistics["episode"] = (new_statistics["episode"] 
                    + proportion * steps_per_epoch)
            statistics = pd.concat([statistics, new_statistics])
    
    _plot(statistics)
    training_peasant.save("resources/weights/intelligent-unrewarded")


def train_cooperative():
    pass

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
    else:
        raise ValueError(f"invalid train argument: {sys.argv[1]}")
