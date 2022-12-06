from engine import Node, Window
from components import Menu


class MainMenu(Node):

    def __init__(self, name: str, engine):
        super().__init__(name, engine)
    
    def enter(self):
        menu = self.add_child(Menu, "menu")
        menu.set_title("main menu")
        
        menu.add_option("play")
        menu.add_option("settings")
        menu.add_option("quit")

        menu.connect("selected", self.option_selected)
    
    def option_selected(self, option: str):
        if option == "quit":
            self.get_engine().quit()