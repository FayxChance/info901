from abc import ABC, abstractmethod

class Message(ABC):
    def __init__(self, src = None, payload = None, dest = None, stamp = None):
        self.src = src
        self.payload = payload
        self.dest = dest
        self.stamp = stamp


class Token(Message):
    def __init__(self, dest):
        super().__init__(dest=dest)

class DestinatedMessage(Message):
    def __init__(self, src, payload, dest, stamp):
        super().__init__(src=src, payload=payload, dest=dest, stamp=stamp)

class BroadcastMessage(Message):
    def __init__(self, src, payload, stamp):
        super().__init__(src=src, payload=payload, stamp=stamp)

class Synchronization(Message):
    def __init__(self, src, stamp):
        super().__init__(src=src, stamp=stamp)