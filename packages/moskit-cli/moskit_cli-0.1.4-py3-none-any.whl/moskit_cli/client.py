# moskit/client.py
from ._core import _MoskitClient
from .enums import Direction, SpeedLevel, Owner

class MoskitClient:
    def __init__(self, base_url: str, timeout: float = 5.0):
        self._impl = _MoskitClient(base_url, timeout)

    def home(self, motor_id: int):
        return self._impl.home(motor_id)

    def driveToPosition(self, motor_id: int, position: int, speed_level: SpeedLevel):
        return self._impl.driveToPosition(motor_id, position, speed_level)

    def driveVelocity(self, motor_id: int, speed_level: SpeedLevel, direction: Direction = Direction.STOPPED,  scale: float = 1.0):
        return self._impl.driveVelocity(motor_id, direction, speed_level, scale)

    def getVelocity(self, motor_id: int):
        return self._impl.getVelocity(motor_id)

    def getPosition(self, motor_id: int):
        return self._impl.getPosition(motor_id)

    def getIsMoving(self, motor_id: int):
        return self._impl.getIsMoving(motor_id)

    def getEndStopLockL(self, motor_id: int):
        return self._impl.getEndStopLockL(motor_id)

    def getEndStopLockR(self, motor_id: int):
        return self._impl.getEndStopLockR(motor_id)

    def getOwner(self, motor_id: int):
        return self._impl.getOwner(motor_id)