import sys

from engine import *
import scenes


if __name__ == "__main__":
    engine = Engine()
    engine.register(scenes.MainMenu, "main-menu")

    engine.start(sys.argv[1:], "main-menu")