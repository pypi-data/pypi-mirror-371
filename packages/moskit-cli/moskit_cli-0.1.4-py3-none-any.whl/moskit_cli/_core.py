# moskit/_core.py
import json
from urllib import request
from .enums import Direction, SpeedLevel, Owner

class _MoskitClient:
    def __init__(self, base_url: str, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = float(timeout)
        self._headers = {"Content-Type": "application/json", "X-Caller": "PYTHON"}

    def _post(self, path: str, payload: dict) -> bool:
        try:
            data = json.dumps(payload).encode("utf-8")
            req = request.Request(self.base_url + path, data=data, headers=self._headers, method="POST")
            with request.urlopen(req, timeout=self.timeout) as resp:
                return 200 <= resp.getcode() < 300
        except Exception:
            return False

    def _get_state(self, motor_id: int):
        url = f"{self.base_url}/api/status?motor_id={int(motor_id)}"
        req = request.Request(url, headers={"Accept": "application/json", **self._headers}, method="GET")
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                if 200 <= resp.getcode() < 300:
                    body = resp.read().decode("utf-8", "ignore")
                    return json.loads(body or "{}")
        except Exception:
            return None
        return None

    @staticmethod
    def _val(x):
        return getattr(x, "value", x)

    def home(self, motor_id: int):
        return self._post("/api/home", {"motor_id": int(motor_id)})

    def driveToPosition(self, motor_id: int, position: int, speed_level: SpeedLevel):
        payload = {"motor_id": int(motor_id), "position": int(position), "speedLevel": self._val(speed_level)}
        return self._post("/api/driveToPosition", payload)

    def driveVelocity(self, motor_id: int, speed_level: SpeedLevel, direction: Direction = Direction.STOPPED, scale: float = 1.0):
        payload = {"motor_id": int(motor_id), "dir": self._val(direction), "speedLevel": self._val(speed_level), "speedScale": float(scale)}
        return self._post("/api/driveVelocity", payload)

    def getVelocity(self, motor_id: int):
        st = self._get_state(motor_id)
        return int(st["velocity"]) if st and "velocity" in st and st["velocity"] is not None else None

    def getPosition(self, motor_id: int):
        st = self._get_state(motor_id)
        return int(st["position"]) if st and "position" in st and st["position"] is not None else None

    def getIsMoving(self, motor_id: int):
        st = self._get_state(motor_id)
        return bool(st["isMoving"]) if st and "isMoving" in st else None

    def getEndStopLockL(self, motor_id: int):
        st = self._get_state(motor_id)
        return bool(st["rEndstopLock"]) if st and "rEndstopLock" in st else None

    def getEndStopLockR(self, motor_id: int):
        st = self._get_state(motor_id)
        return bool(st["fEndstopLock"]) if st and "fEndstopLock" in st else None

    def getOwner(self, motor_id: int):
        st = self._get_state(motor_id)
        if not st or "owner" not in st or st["owner"] is None:
            return None
        name = str(st["owner"]).upper()
        try:
            return Owner[name]
        except Exception:
            return None
