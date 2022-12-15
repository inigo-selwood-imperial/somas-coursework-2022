from game.game import Game
from game.actors.random_peasant import RandomPeasant


if __name__ == "__main__":

    peasants = [RandomPeasant(10) for _ in range(9)]
    game = Game(peasants)
    results = game.run()
    print(results)