from .event import Event
from .engine import Engine
from .window import Window


class Scene:

    def __init__(self, name: str, engine: Engine):
        self._name = name
        self._engine = engine

    def draw(self, window: Window) -> None:
        """ Called before the window refreshes """
        pass

    def get_engine() -> Engine:
        """ Fetches the game engine object """
        return self._engine

    def enter(self) -> None:
        """ Called when the scene is added to the tree """
        pass

    def exit(self) -> None:
        """ Called when a scene is freed """
        pass

    def input(self, event: Event) -> None:
        """ Called when an event occurs """
        pass