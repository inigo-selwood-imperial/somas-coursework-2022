from engine import Node, Window
from components import Menu


class MainMenu(Node):
    
    def enter(self):
        menu = self.add_child(Menu, "menu")
        menu.options = [
            "play",
            "settings",
            "quit",
        ]