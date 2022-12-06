from .node import Node


class Scene(Node):

    def __init__(self):
        super().__init__()

    def load(name: str):
        self.engine.load(name)
    
    def quit():
        self.engine.quit()