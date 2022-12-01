from __future__ import annotations

import uuid

from .event import Event


class Node:

    def __init__(self):
        self._children = {}
        self._callbacks = {}
    
    def _exit(self):
        """ Exits children, then self """

        for child in self.children:
            child._exit()
        self.exit()
    
    def _input(self, event: Event):
        """ Propagates input to children, then self """

        for child in self.children:
            child._input(event)
        self.input(event)
    
    def add_child(node_type: type, name: str = None, **arguments):
        """ Adds a child """

        if name:
            if name in self.children:
                message = f"node '{self.name}' already has child '{name}'"
                raise Exception(message)
        else:
            name = uuid.uuid4().hex()[:10]

        node = node_type(**arguments)
        self.children[name] = node

        log.debug(f"added node '{name}' to '{self.name}'")
    
    def connect(signal: str, callback: callable):
        """ Connects a callback to one of this node's signals """

        if signal not in self._callbacks:
            raise Exception(f"'{signal}' not registered in '{self.name}'")
        self._callbacks[signal].append(callback)

        name = callback.__name__
        log.debug(f"connected '{name}' to '{signal}' in '{self.name}'")
    
    def emit(signal: str, **arguments):
        """ Emits a signal to connected nodes """

        if signal not in self._callbacks:
            raise Exception(f"'{signal}' not registered in '{self.name}'")
        for callback in self._callbacks[signal]:
            callback(**arguments)
        
        log.debug(f"'{self.name}' emitted '{signal}'")

    def get_node(path: str) -> Node | None:
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
    
    def register(signal: str):
        """ Registers a signal """

        if signal in self._signals:
            raise Exception(f"signal '{signal}' already registered")
        self._callbacks[signal] = []

        log.debug(f"'{self.name}' registered '{signal}'")
    
    def remove_child(name: str):
        """ Removes a child """

        if name not in self.children:
            raise Exception(f"node '{self.name}' has no child '{name}'")
        
        child._exit()
        del self.children[name]

        log.debug(f"'{self.name}' removed child '{name}'")

    def enter(self):
        pass

    def exit(self):
        pass

    def input(event: Event):
        pass