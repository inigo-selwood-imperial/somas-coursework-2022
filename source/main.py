import time

from engine import Engine, Log

import scenes


if __name__ == "__main__":
    engine = Engine()
    engine.register(scenes.MainMenu, "main-menu")

    engine.start("main-menu")