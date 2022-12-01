from engine import Scene, Window


class MainMenu(Scene):

    def __init__(self):
        pass
    
    def draw(self, window: Window):
        window.print("hello world")