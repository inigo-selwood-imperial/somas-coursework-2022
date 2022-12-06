import time

from .event import Event
from .log import debug as log_debug, event as log_event
from .node import Node
from .timer import Timer
from .window import Window


class Engine:

    def __init__(self):
        self._scenes = {}
        self._scene = None

        self._running = False

        self.window = None
    
    def load(self, name: str):
        if name not in self._scenes:
            message = f"scene '{name}' not registered"
            log_error(message)
            raise Exception(f"scene '{name}' not registered")
        
        # Quit old scene, if applicable
        if self._scene:
            log_debug(f"quitting scene '{self._scene.name}'")
            self._scene._exit()
            self._scene = None
        
        # Load new scene
        log_debug(f"loading scene '{name}'")
        self._scene = self._scenes[name](name, self)
        self._scene._engine = self
        self._scene.name = name
        self._scene.enter()
    
    def quit(self):

        # Quit current scene, if applicable
        if self._scene:
            log_debug(f"quitting scene '{self._scene.name}'")
            self._scene._exit()
            self._scene = None
        
        self._running = False

    def start(self, arguments: list, root: str):

        timer = Timer()
        frame_period = 1 / 24
        timer.start(frame_period)

        with Window() as self.window:

            self._running = True

            self.load(root)
            
            while self._running:
                
                self.window.clear()
                self._scene._draw(self.window)

                if self.window.updates_available:
                    self.window.update()

                while event := self.window.poll():
                    log_event(event)
                    if event.type == "quit":
                        self.quit()
                        break
                    else:
                        self._scene._input(event)

                if not timer.finished():
                    time.sleep(timer.delta())
                    timer.start(frame_period)
    
    def register(self, scene_type: Node, name: str):
        if name in self._scenes:
            raise Exception(f"scene '{name}' already registered")
        self._scenes[name] = scene_type
        