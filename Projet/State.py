from enum import Enum

class State(Enum):
    NONE = None
    REQUEST = "request"
    SC = "sc"
    RELEASE = "release"