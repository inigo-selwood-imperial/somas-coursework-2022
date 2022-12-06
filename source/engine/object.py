from .node import Node


class Object(Node):

    def __init__(self):
        super().__init__()

        self.position = [0, 0]
        self.margin  = [0, 0, 0, 0]
    
    def _size(self):
        margin_top, margin_right, margin_bottom, margin_left = self.margin
        width, height = self.size()
        return [
            margin_left + margin_right + width,
            margin_top + margin_bottom + height,
        ]
    
    def size(self) -> list:
        return [0, 0]