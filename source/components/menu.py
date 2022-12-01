import curses

from engine import Node, Event, Window


class Menu(Node):

    def __init__(self, name: str):
        super().__init__(name)

        self.options = []
        self.index = 0
        self.focused = True
    
    def enter(self):
        self.register("selected")
    
    def input(self, event: Event):
        if event.type == "key":
            if event.scancode == curses.KEY_UP and self.index:
                self.index -= 1
            elif (event.scancode == curses.KEY_DOWN 
                    and self.index + 1 < len(self.options)):
                self.index += 1
            elif event.scancode == ord("\n"):
                self.emit("selected", option=self.options[self.index])
    
    def draw(self, window: Window):
        for index in range(len(self.options)):
            option = self.options[index]
            window.print(option, (2, index))
        
        window.print(">", (0, self.index))