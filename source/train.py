import os; os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
# import scipy

from learning.experience_buffer import ExperienceBuffer

from game.game import Game
from game.actors.random_peasant import RandomPeasant
from game.actors.ddpg_peasant import DDPGPeasant


if __name__ == "__main__":

    training_peasant = DDPGPeasant(10)

    seed = 100
    np.random.seed(seed)
    tf.random.set_seed(seed)

    rewards = []
    lifespans = []

    statistics = []
    for episode in range(100):

        peasants = [RandomPeasant(10) for _ in range(9)]
        peasants.append(training_peasant)
        training_peasant.reset()

        game = Game(peasants, experience_factor=0.9, round_limit=100, monster_level_factor=1.05)
        results = game.run()

        reward = training_peasant.reward_total
        lifespan = training_peasant.previous_round

        rewards.append(reward)
        lifespans.append(lifespan)

        average_reward = np.mean(rewards[-40:])
        network_lifespan = np.mean(lifespans[-40:])
        average_lifespan = results["lifetime-mean"].iloc[-1]

        print(f"{episode}: {average_reward:.3}, {network_lifespan:.3}, {average_lifespan:.3}")
        statistics.append([episode, average_reward, network_lifespan, average_lifespan])

    statistics = pd.DataFrame(statistics, columns=["episode", "average-reward", "network-lifespan", "average-lifespan"])
    statistics.plot(x="episode", y=["average-reward", "network-lifespan", "average-lifespan"])
    plt.show()