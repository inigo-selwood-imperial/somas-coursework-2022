from engine import Object, Window


class Label(Object):

    def __init__(self):
        super().__init__()

        self.text = ""
    
    def size(self) -> list:
        lines = self.text.count("\n")
        if self.text and self.text[-1] == "\n":
            lines -= 1
        
        columns = 0
        for token in self.text.split("\n"):
            columns = max(len(token), columns)
        
        return [columns, lines]
    
    def draw(self, window: Window):
        window.print(self.text, self.position)