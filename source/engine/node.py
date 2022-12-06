from __future__ import annotations

import uuid

from .event import Event
from .log import debug as log_debug, event as log_event


class Node:

    def __init__(self):
        self.name = None

        self.engine = None
        self.children = {}
        self.callbacks = {}
        self.signals = {}

    def _draw(self, window: Window):
        for child in self.children.values():
            child._draw(window)
        self.draw(window)
    
    def _exit(self):
        """ Exits children, then self """

        for child in self.children.values():
            child._exit()
        self.exit()
    
    def _input(self, event: Event):
        """ Propagates input to children, then self """

        for child in self.children.values():
            child._input(event)
        self.input(event)
    
    def add_child(self, node_type: type, name: str = None, **arguments) -> Node:
        """ Adds a child """

        log_debug(f"adding node '{name}' to '{self.name}'")

        if name:
            if name in self.children:
                message = f"node '{self.name}' already has child '{name}'"
                raise Exception(message)
        else:
            name = uuid.uuid4().hex[:10]

        node = node_type(**arguments)
        node.engine = self.engine
        node.name = name
        node.enter()
        self.children[name] = node

        return node
    
    def connect(self, signal: str, callback: callable):
        """ Connects a callback to one of this node's signals """

        name = callback.__name__
        log_debug(f"connected '{name}' to '{signal}' in '{self.name}'")

        if signal not in self.callbacks:
            raise Exception(f"'{signal}' not registered in '{self.name}'")
        self.callbacks[signal].append(callback)
    
    def emit(self, signal: str, **arguments):
        """ Emits a signal to connected nodes """
        
        log_event(f"'{self.name}' emitted '{signal}' ({arguments})")

        if signal not in self.callbacks:
            raise Exception(f"'{signal}' not registered in '{self.name}'")
        for callback in self.callbacks[signal]:
            callback(**arguments)

    def draw(self, window: Window):
        pass

    def enter(self):
        pass

    def exit(self):
        pass

    def get_node(self, path: str) -> Node | None:
        """ Gets a child node """

        # Get head token
        tokens = path.split(".")
        head = tokens[0]
        if head not in self.children:
            raise Exception(f"node '{self.name}' has no child '{head}'")
        
        # Propagate, or return
        if len(tokens) == 1:
            return self.children[name]
        else:
            return self.children[name].get_node(".".join(tokens[1:]))
    
    def getengine(self):
        return self.engine

    def input(self, event: Event):
        pass
    
    def register(self, signal: str):
        """ Registers a signal """

        log_debug(f"'{self.name}' registered '{signal}'")

        if signal in self.signals:
            raise Exception(f"signal '{signal}' already registered")
        self.callbacks[signal] = []

    
    def remove_child(self, name: str):
        """ Removes a child """

        log_debug(f"'{self.name}' removing child '{name}'")

        if name not in self.children:
            raise Exception(f"node '{self.name}' has no child '{name}'")
        
        child._exit()
        del self.children[name]