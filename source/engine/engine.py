import time

from .event import Event
from .scene import Scene
from .timer import Timer
from .window import Window
from .log import debug as log_debug


class Engine:

    def __init__(self):
        self._scenes = {}
        self._scene = None
        self._scene_name = None

        self._running = False

        self.window = None
    
    def load(self, name: str):
        if name not in self._scenes:
            message = f"scene '{name}' not registered"
            log_error(message)
            raise Exception(f"scene '{name}' not registered")
        
        # Quit old scene, if applicable
        if self._scene:
            self._scene.exit()
            self._scene = None
            log_debug(f"quit scene '{self._scene_name}'")
        
        # Load new scene
        self._scene = self._scenes[name]()
        self._scene_name = name
        self._scene.enter()
        log_debug(f"loaded scene '{name}'")
    
    def quit(self):

        # Quit current scene, if applicable
        if self._scene:
            self._scene.exit()
            self._scene = None
            log_debug(f"quit scene '{self._scene_name}'")
        
        self._running = False

    def start(self, arguments: list, root: str):

        timer = Timer()
        frame_period = 1 / 16
        timer.start(frame_period)

        with Window() as self.window:

            self._running = True

            self.load(root)
            
            while self._running:
                
                self.window.clear()
                self._scene.draw(self.window)
                self.window.update()

                while event := self.window.poll():
                    log_debug(f"event: {event}")
                    if event.type == "quit":
                        self.quit()
                        break
                    else:
                        self._scene._input(event)

                if not timer.finished():
                    time.sleep(timer.delta())
                    timer.start(frame_period)

    
    def register(self, scene_type: Scene, name: str):
        if name in self._scenes:
            raise Exception(f"scene '{name}' already registered")

        self._scenes[name] = scene_type
        