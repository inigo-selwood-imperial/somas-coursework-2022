from __future__ import annotations

import uuid

from .event import Event
from .log import debug as log_debug, event as log_event


class Node:

    def __init__(self):
        self.name = None

        self._engine = None
        self._children = {}
        self._callbacks = {}
        self._signals = {}

    def _draw(self, window: Window):
        for child in self._children.values():
            child._draw(window)
        self.draw(window)
    
    def _exit(self):
        """ Exits children, then self """

        for child in self._children.values():
            child._exit()
        self.exit()
    
    def _input(self, event: Event):
        """ Propagates input to children, then self """

        for child in self._children.values():
            child._input(event)
        self.input(event)
    
    def add_child(self, node_type: type, name: str = None, **arguments) -> Node:
        """ Adds a child """

        log_debug(f"adding node '{name}' to '{self.name}'")

        if name:
            if name in self._children:
                message = f"node '{self.name}' already has child '{name}'"
                raise Exception(message)
        else:
            name = uuid.uuid4().hex()[:10]

        node = node_type(**arguments)
        node._engine = self._engine
        node.name = name
        node.enter()
        self._children[name] = node

        return node
    
    def connect(self, signal: str, callback: callable):
        """ Connects a callback to one of this node's signals """

        name = callback.__name__
        log_debug(f"connected '{name}' to '{signal}' in '{self.name}'")

        if signal not in self._callbacks:
            raise Exception(f"'{signal}' not registered in '{self.name}'")
        self._callbacks[signal].append(callback)
    
    def emit(self, signal: str, **arguments):
        """ Emits a signal to connected nodes """
        
        log_event(f"'{self.name}' emitted '{signal}' ({arguments})")

        if signal not in self._callbacks:
            raise Exception(f"'{signal}' not registered in '{self.name}'")
        for callback in self._callbacks[signal]:
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
        if head not in self._children:
            raise Exception(f"node '{self.name}' has no child '{head}'")
        
        # Propagate, or return
        if len(tokens) == 1:
            return self._children[name]
        else:
            return self._children[name].get_node(".".join(tokens[1:]))
    
    def get_engine(self):
        return self._engine

    def input(self, event: Event):
        pass
    
    def register(self, signal: str):
        """ Registers a signal """

        log_debug(f"'{self.name}' registered '{signal}'")

        if signal in self._signals:
            raise Exception(f"signal '{signal}' already registered")
        self._callbacks[signal] = []

    
    def remove_child(self, name: str):
        """ Removes a child """

        log_debug(f"'{self.name}' removing child '{name}'")

        if name not in self._children:
            raise Exception(f"node '{self.name}' has no child '{name}'")
        
        child._exit()
        del self._children[name]