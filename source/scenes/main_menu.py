from engine import Engine, Scene, Window


class MainMenu(Scene):

    def __init__(self, name: str, engine: Engine):
        super().__init__(name, engine)

    def draw(self, window: Window) -> None:
        window.print("hello world")