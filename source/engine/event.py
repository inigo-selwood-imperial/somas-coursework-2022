class Event:
    TYPE_KEY    = 1
    TYPE_QUIT   = 2
    TYPE_RESIZE = 3

    def __init__(self, type: int):
        self.type = type


class QuitEvent(Event):

    def __init__(self):
        super().__init__(Event.TYPE_QUIT)

    def __str__(self) -> str:
        return "quit requested"


class KeyEvent(Event):

    def __init__(self, scancode: int, keycode: str):
        super().__init__(Event.TYPE_KEY)
        self.scancode = scancode
        self.keycode = keycode
    
    def __str__(self) -> str:
        return f"key pressed: {self.keycode} ({self.scancode})"


class WindowResizeEvent(Event):

    def __init__(self, size: tuple):
        super().__init__(Event.TYPE_RESIZE)
        self.size = size
    
    def __str__(self) -> str:
        width, height = self.size
        return f"window resized: [{width}:{height}]"