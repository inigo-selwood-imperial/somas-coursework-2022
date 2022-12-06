from .node import Node


class Scene(Node):

    def __init__(self):
        super().__init__()

    def load(name: str):
        self._engine.load(name)
    
    def quit():
        self._engine.quit()