import datetime
import os
import atexit


_log_file = None

def get_log_file():
    global _log_file

    def close_log_file():
        if _log_file is not None:
            _log_file.close()

    if _log_file is None:

        # Evaluate root
        root = os.path.abspath(__file__)
        for _ in range(3):
            root = os.path.dirname(root)

        # Check log folder exists
        log_base = os.path.join(root, "logs")
        if not os.path.exists(log_base):
            os.mkdir(log_base)
        
        # Evaluate log name
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        log_name = f"log-{timestamp}.txt"
        path = os.path.join(log_base, log_name)

        # Open file, and register for closing at exit
        _log_file = open(path, "w")
        atexit.register(close_log_file)
    
    return _log_file


def debug(value: any):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    get_log_file().write(f"{timestamp} (DEBUG) {value}\n")


def event(value: any):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    get_log_file().write(f"{timestamp} (EVENT) {value}\n")
