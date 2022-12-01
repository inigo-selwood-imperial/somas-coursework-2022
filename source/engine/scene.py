from .node import Node
from .window import Window


class Scene(Node):

    def __init__(self):
        super().__init__()

    def _draw(self, window: Window):
        for child in self._children:
            child._draw(window)
        self.draw(window)

    def draw(self):
        pass