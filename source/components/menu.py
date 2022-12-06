import curses

from engine import Node, Event, Window


class Menu(Node):

    def __init__(self, name: str, engine):
        super().__init__(name, engine)

        self.options = []
        self.index = 0
        self.focused = True
        self.width = 0
        self.title = None
    
    def add_option(self, text: str):
        self.options.append(text)
        self.width = max(self.width, len(text))
    
    def set_title(self, title: str):
        self.title = title
        self.width = max(self.width, len(title))
    
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
            padding = " " * (self.width - len(option))
            highlight = index == self.index

            window.print(f" {option}{padding} ", 
                    (2, index + 1), 
                    highlight=highlight)
            
            window.draw_box((self.width + 6, len(self.options) + 2))

            if self.title:
                window.print(f" {self.title} ", (2, 0))