from abc import ABC


class Message(ABC):
    def __init__(self, src=None, payload=None, dest=None, stamp=None):
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


class BroadcastMessageSync(Message):
    def __init__(self, src, payload, stamp):
        super().__init__(src=src, payload=payload, stamp=stamp)


class DestinatedMessageSync(Message):
    def __init__(self, src, payload, dest, stamp):
        super().__init__(src=src, payload=payload, dest=dest, stamp=stamp)


class MessageReceivedSync(Message):
    def __init__(self, src, dest, stamp):
        super().__init__(src=src, dest=dest, stamp=stamp)


class UpdateAnnuaire(Message):
    def __init__(self, annuaire):
        self.annuaire = annuaire


class AddAnnuaire(Message):
    def __init__(self, pid):
        self.pid = pid


class Numerotation(Message):
    def __init__(self, pid):
        self.pid = pid


class NumerotationBack(Message):
    def __init__(self, pid):
        self.pid = pid


class Leader(Message):
    def __init__(self, pid):
        self.pid = pid
