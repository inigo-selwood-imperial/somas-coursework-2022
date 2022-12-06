from .node import Node


class Object(Node):

    def __init__(self):
        self.position = (0, 0)
        self.size = 