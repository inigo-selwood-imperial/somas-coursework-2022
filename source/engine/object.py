from .node import Node


class Object(Node):

    def __init__(self):
        self.position = [0, 0]
        self.size = [0, 0]
    
        self.margin  = [0, 0, 0, 0]
        self.padding = [0, 0, 0, 0]

        self.anchors = [0, 0, 0, 0]
        self.grow_mask = [0, 0]
    
    def size(self) -> list:
        return [0, 0]