import time
import curses
import signal
import sys

from .event import *
from .log import debug as log_debug


class Window:
    REFRESH_FREQUENCY = 3 # /Hz
    REFRESH_PERIOD    = 1 / REFRESH_FREQUENCY # /s

    def __enter__(self):
        """ Create a curses context for the window """

        log_debug("initializing curses")
        self.handle = curses.initscr()

        # Turn off key echo, make input immediate, and disable cursor
        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)

        # Enable use of colour
        if not curses.has_colors():
            raise Exception("terminal does not support colour")
        curses.start_color()
        curses.use_default_colors()

        # Enable use of function/arrow keys, and disable input buffering
        self.handle.keypad(True)
        self.handle.nodelay(True)

        # Register a quit handler flag
        self.queue_quit = False
        def handle_quit(signal, frame):
            self.queue_quit = True
        signal.signal(signal.SIGINT, handle_quit)

        self.blocking = False
        self.size = self.get_size()
        self.last_ticks = time.time()

        self.updates_available = False

        return self

    def __exit__(self, type, value, traceback):
        """ Break down the curses context """
        log_debug("quitting curses")

        # Re-enable input buffering and turn off extended key sets
        self.handle.nodelay(False)
        self.handle.keypad(False)

        # Re-enable cursor, buffer input until line-break, and enable key echo
        curses.curs_set(True)
        curses.nocbreak()
        curses.echo()

        curses.endwin()

    def clear(self):
        """ Clears the window """
        self.handle.clear()

    def get_size(self) -> tuple:
        """ Gets the size of the terminal """

        height, width = self.handle.getmaxyx()
        return (width, height)
    
    def print(self, value: any, position: tuple = None):
        """ Prints a value, optionally specifiying the position and colour """

        if position:
            x, y = position
            width, height = self.size
            if x < 0 or x >= width or y < 0 or y >= height:
                return
            self.handle.addstr(y, x, f"{value}")
        else:
            self.handle.addstr(f"{value}")
        
        self.updates_available = True

    def poll(self, blocking: bool = False) -> str | None:
        """ Poll the window for events """

        # Quit events
        if self.queue_quit:
            self.queue_quit = False
            return QuitEvent()

        # Refresh window every so often
        new_ticks = time.time()
        tick_delta = new_ticks - self.last_ticks
        if tick_delta > Window.REFRESH_PERIOD:
            self.last_ticks = new_ticks

            # Window resize events
            self.handle.refresh()
            newsize = self.get_size()
            if self.size != newsize:
                self.size = newsize
                return WindowResizeEvent(self.size)
        
        # Set input blocking
        if blocking != self.blocking:
            self.handle.nodelay(not blocking)
            self.blocking = blocking
        
        # Scan for new key inputs
        try:
            return KeyEvent(self.handle.getch())
        except:
            pass
    
        # On default
        return None
    
    def update(self):
        """ Updates the screen """
        self.handle.refresh()
        self.updates_available = False
