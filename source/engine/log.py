import datetime
import os


class Log:

    def __enter__(self):
        root = os.path.abspath(__file__)
        for _ in range(2):
            root = os.path.dirname(root)
        
        log_base = os.path.join(root, "logs")
        if not os.path.exists(log_base):
            os.mkdir(log_base)
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        path = os.path.join(log_base, f"log-{timestamp}.txt")

        self.file = None
        self.file = open(path, "w")

        return self
    
    def __exit__(self, type, value, traceback):
        if self.file:
            self.file.close()
        
    def _print(self, level: str, value: any):
        timestamp = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
        self.file.write(f"[{timestamp}] {level} {value}\n")
        
    def alert(self, value: any):
        self._print("ALERT", value)
        
    def debug(self, value: any):
        self._print("DEBUG", value)
        
    def error(self, value: any):
        self._print("ERROR", value)
        
    def fatal(self, value: any):
        self._print("FATAL", value)