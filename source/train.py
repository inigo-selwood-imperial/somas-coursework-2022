import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import scipy

from learning.experience_buffer import ExperienceBuffer

from game.game import Game
from game.actors.random_peasant import RandomPeasant
from game.actors.ddpg_peasant import DDPGPeasant


if __name__ == "__main__":

    training_peasant = DDPGPeasant(10)

    rewards = []
    for _ in range(100):

        peasants = [RandomPeasant(10) for _ in range(9)]
        peasants.append(training_peasant)

        game = Game(peasants)
        results = game.run()

        reward = training_peasant.reward_total
        rewards.append(reward)

        average_reward = np.mean(rewards[-40:])
        print(f"{average_reward:.3}")