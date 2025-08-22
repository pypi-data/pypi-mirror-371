from enum import Enum

class Direction(Enum):
    STOP    = "STOPPED"
    FORWARD = "FORWARD"
    REVERSE = "REVERSE"

class SpeedLevel(Enum):
    STOP    = "STOP"
    VERYLOW = "VERYLOW"
    LOW     = "LOW"
    MEDIUM  = "MEDIUM"
    HIGH    = "HIGH"
    
class Owner(Enum):
    FREE   = "FREE"
    CAN    = "CAN"
    WEB    = "WEB"
    PYTHON = "PYTHON"
    HOME   = "HOME"