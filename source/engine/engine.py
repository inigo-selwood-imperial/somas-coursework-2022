import time

from .event import Event
from .log import Log
from .timer import Timer
from .window import Window

class Engine:

    def __init__(self):
        self.scenes = {}
        self.scene = None

        self.log = None
        self.window = None

    def load(self, name: str):
        """ Loads a registered scene of a given name """
        
        # Stop the current scene
        if self.scene:
            self.log.debug(f"quitting scene '{self.scene._name}'")
            self.scene.exit()
            self.scene = None

        # Check the scene specified exists
        if name not in self.scenes:
            raise Exception(f"no such scene '{name}'")
        
        # Load the new scene
        self.log.debug(f"loading scene '{name}'")
        scene = self.scenes[name]
        scene.enter()
        self.scene = scene
    
    def quit(self):
        """ Stops the engine """

        # Quit the current scene (if applicable), and exit
        if self.scene:
            self.log.debug(f"quitting scene '{self.scene._name}'")
            self.scene.exit()
        
        self.log.debug("quitting")
        self.running = False

    def register(self, scene_type: type, name: str):
        """ Registers a scene with a given name """

        # Check name is unique
        if name in self.scenes:
            raise Exception(f"scene '{name}' already registered")
        
        # Create scene
        scene = scene_type(name, self)
        self.scenes[name] = scene

    def start(self, root: str):
        """ Starts the main loop """

        with Window() as window, Log() as log:
            self.window = window
            self.log = log

            # Create a timer; used to refresh window every 1/8s
            timer = Timer()
            timer_period = 1 / 8
            timer.start(timer_period)

            # Load root scene
            self.load(root)

            # Main loop
            self.running = True
            while self.running:

                # Poll events
                while event := window.poll():
                    if event.type == Event.TYPE_QUIT:
                        self.quit()
                    else:
                        self.scene.input(event)
                        self.log.debug(f"event: {event}")

                # Refresh window
                window.clear()
                self.scene.draw(window)
                window.update()

                # Cap frame rate
                if not timer.finished():
                    time.sleep(timer.delta())
                timer.start(timer_period)


