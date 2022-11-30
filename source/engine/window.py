import time
import curses
import signal
import sys

from .event import *


class Window:
    REFRESH_FREQUENCY = 3 # /Hz
    REFRESH_PERIOD    = 1 / REFRESH_FREQUENCY # /s

    _pairs   = {}

    def __enter__(self):
        """ Create a curses context for the window """

        self._handle = curses.initscr()

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
        self._handle.keypad(True)
        self._handle.nodelay(True)

        # Register a quit handler flag
        self._queue_quit = False
        def handle_quit(signal, frame):
            self._queue_quit = True
        signal.signal(signal.SIGINT, handle_quit)

        self._blocking = False
        self._size = self.get_size()
        self._last_ticks = time.time()

        return self

    def __exit__(self, type, value, traceback):
        """ Break down the curses context """

        # Re-enable input buffering and turn off extended key sets
        self._handle.nodelay(False)
        self._handle.keypad(False)

        # Re-enable cursor, buffer input until line-break, and enable key echo
        curses.curs_set(True)
        curses.nocbreak()
        curses.echo()

        curses.endwin()
    
    @staticmethod
    def _get_colour_pair(foreground: int, background: int) -> int:
        """ Fetches (or creates) a curses colour pair """
        
        # Check the colour is valid
        def colour_valid(colour: int) -> bool:
            return (colour >= 0 and colour < 8) or colour == -1
        if not colour_valid(foreground) or not colour_valid(background):
            raise ValueError("invalid colour code")
        
        # If the pair isn't already defined, create one
        hash = foreground << 8 | background
        if not hash in Window._pairs:
            index = len(Window._pairs) + 1
            if index > curses.COLOR_PAIRS:
                raise Exception("out of colour pair space")
            
            curses.init_pair(index, foreground, background)
            Window._pairs[hash] = index
        
        return Window._pairs[hash]
    
    def draw_box(self, size: tuple, origin: tuple = (0, 0)):
        x, y = origin
        width, height = size

        border_horizontal = "─" * (width - 2)
        self.print(border_horizontal, (x + 1, y))
        self.print(border_horizontal, (x + 1, y + height - 1))

        for row in range(1, height - 1):
            self.print("│", (x, y + row))
            self.print("│", (x + width - 1, y + row))
        
        self.print("╭", (x, y))
        self.print("╰", (x, y + height - 1))
        self.print("╮", (x + width - 1, y))
        self.print("╯", (x + width - 1, y + height - 1))

    def clear(self):
        self._handle.clear()

    def get_size(self) -> tuple:
        """ Gets the size of the terminal """

        height, width = self._handle.getmaxyx()
        return (width, height)
    
    def print(self, 
            value: any, 
            position: tuple = None, 
            foreground: int = -1, 
            background: int = -1):
        """ Prints a value, optionally specifiying the position and colour """
        
        colour_index = Window._get_colour_pair(foreground, background)
        if colour_index is None:
            return
        attributes = curses.color_pair(colour_index)

        if position:
            x, y = position
            width, height = self._size
            if x < 0 or x >= width or y < 0 or y >= height:
                return
            self._handle.addstr(y, x, f"{value}", attributes)
        else:
            self._handle.addstr(f"{value}", attributes)

    def poll(self, _blocking: bool = False) -> str | None:
        """ Poll the window for events """

        # Quit events
        if self._queue_quit:
            self._queue_quit = False
            return QuitEvent()

        # Refresh window every so often
        new_ticks = time.time()
        tick_delta = new_ticks - self._last_ticks
        if tick_delta > Window.REFRESH_PERIOD:
            self._last_ticks = new_ticks

            # Window resize events
            self._handle.refresh()
            new_size = self.get_size()
            if self._size != new_size:
                self._size = new_size
                return WindowResizeEvent(self._size)
        
        # Set input _blocking
        if _blocking != self._blocking:
            self._handle.nodelay(not _blocking)
            self._blocking = _blocking
        
        # Scan for new key inputs
        try:
            scancode = self._handle.getch()
            keycode = curses.keyname(scancode)
            return KeyEvent(scancode, keycode)
        except:
            pass
    
        # On default
        return None
    
    def update(self):
        self._handle.refresh()