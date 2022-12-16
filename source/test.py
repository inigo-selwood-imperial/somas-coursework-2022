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


def train_random():

    training_peasant = DDPGPeasant(10, 
            weight_file="resources/weights/intelligent-unrewarded")

    seed = 100
    keras.utils.set_random_seed(seed)

    statistics = []
    for episode in range(200):

        training_peasant.reset()
        peasants = [training_peasant]

        for _ in range(9):
            peasants.append(RandomPeasant(10))

        game = Game(peasants, 
                experience_factor=0.9, 
                round_limit=100, 
                monster_level_factor=1.05)
        results = game.run()

        reward = training_peasant.reward_total
        lifespan = training_peasant.previous_round

        rewards.append(training_peasant.reward_total)
        lifespans.append(lifespan)

        average_reward = np.mean(rewards[-40:])
        network_lifespan = np.mean(lifespans[-40:])

        print(f"{episode}: {average_reward:.3}, {network_lifespan:.3}")
        statistics.append(episode, average_reward, network_lifespan)
    
    headers = [
        "episode",
        "average-reward",
        "lifespan",
    ]
    table = pd.DataFrame(statistics, columns=headers)
    table.plot(x="episode", y=["average-reward", "lifespan"])
    plt.show()

    # name = datetime.datetime.now().strftime("resources/weights/intelligent-unrewarded")
    # training_peasant.save(name)



if __name__ == "__main__":
    train_random()