class Event:
    
    def __init__(self, type_name: str):
        self.type = type_name


class KeyEvent(Event):

    def __init__(self, scancode: int):
        super().__init__("key")
        self.scancode = scancode
        self.keycode = keycode
    
    def __str__(self) -> str:
        return f"key pressed: {self.keycode}"


class QuitEvent(Event):

    def __init__(self):
        super().__init__("quit")
    
    def __str__(self) -> str:
        return "quit requested"


class WindowResizeEvent(Event):

    def __init__(self, size: list):
        super().__init__("window-resize")
        self.size = size
    
    def __str__(self) -> str:
        width, height = self.size
        return f"window resized: [{width}, {height}]"