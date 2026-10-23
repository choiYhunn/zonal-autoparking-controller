"""New portable reconstruction; no transport, GPIO, or hardware success claim.

Call tick() with monotonic seconds and immutable sensor snapshots. Returned
commands describe requested output only. A real adapter needs independent ECU
watchdogs, feedback, and physical calibration before any vehicle use.
"""
from dataclasses import dataclass
from enum import Enum, auto
import math


class State(Enum):
    SCAN_RIGHT = auto()
    FWD_AFTER = auto()
    LEFT_FWD = auto()
    RIGHT_REV = auto()
    REVERSE_TO_WALL = auto()
    DONE = auto()
    STOP = auto()


@dataclass(frozen=True)
class Config:
    right_min_cm: float = 10
    right_max_cm: float = 70
    confirm_s: float = 1
    forward_s: float = 1
    left_s: float = 2.5
    reverse_s: float = 3
    rear_wall_cm: float = 20
    rear_timeout_s: float = 10
    scan_timeout_s: float = 30  # New model guard, not a historical parameter.
    max_sensor_age_s: float = 0.5  # New model guard.

    def __post_init__(self):
        if any(not math.isfinite(v) or v <= 0 for v in vars(self).values()):
            raise ValueError("configuration values must be positive and finite")
        if not 2 <= self.right_min_cm <= self.right_max_cm <= 350:
            raise ValueError("right detection range must lie within 2..350 cm")
        if not 2 < self.rear_wall_cm <= 350:
            raise ValueError("rear threshold must lie above the sensor minimum")


@dataclass(frozen=True)
class Sample:
    cm: float | None
    measured_at: float

    def status(self, now: float, max_age: float) -> str:
        if not math.isfinite(self.measured_at) or not 0 <= now - self.measured_at <= max_age:
            return "stale-or-future"
        if self.cm is None or not math.isfinite(self.cm) or self.cm <= 0:
            return "missing"
        if self.cm == 4000:
            return "no-echo"
        if not 2 <= self.cm <= 350:
            return "invalid-range"
        return "valid"


@dataclass(frozen=True)
class Command:
    steer_deg: int = 0  # Logical coordinates: left negative, right positive.
    speed: int = 0  # Signed workshop PWM request, not measured velocity.


class Controller:
    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self.state = State.SCAN_RIGHT
        self.reason = ""
        self._entered: float | None = None
        self._last: float | None = None
        self._confirmed_since: float | None = None

    def stop(self, reason: str = "operator-stop") -> Command:
        if self.state != State.DONE:
            self.state, self.reason = State.STOP, reason
        return Command()

    def _enter(self, state: State, now: float):
        self.state, self._entered = state, now

    def command(self) -> Command:
        return {
            State.SCAN_RIGHT: Command(0, 55),
            State.FWD_AFTER: Command(0, 50),
            State.LEFT_FWD: Command(-12, 50),
            State.RIGHT_REV: Command(12, -45),
            State.REVERSE_TO_WALL: Command(0, -45),
        }.get(self.state, Command())

    def tick(self, now: float, right: Sample, rear: Sample) -> Command:
        if self.state in (State.STOP, State.DONE):
            return Command()
        if not math.isfinite(now) or (self._last is not None and now < self._last):
            return self.stop("invalid-clock")
        self._last = now
        if self._entered is None:
            self._entered = now
        elapsed = now - self._entered
        p = self.config

        if self.state == State.SCAN_RIGHT:
            status = right.status(now, p.max_sensor_age_s)
            if status not in ("valid", "no-echo"):
                return self.stop("right-sensor-" + status)
            if elapsed >= p.scan_timeout_s:
                return self.stop("scan-timeout")
            hit = status == "valid" and p.right_min_cm <= right.cm <= p.right_max_cm
            if hit:
                if self._confirmed_since is None:
                    self._confirmed_since = now
                if now - self._confirmed_since >= p.confirm_s:
                    self._enter(State.FWD_AFTER, now)
            else:
                self._confirmed_since = None
        elif self.state in (State.FWD_AFTER, State.LEFT_FWD, State.RIGHT_REV):
            duration, next_state = {
                State.FWD_AFTER: (p.forward_s, State.LEFT_FWD),
                State.LEFT_FWD: (p.left_s, State.RIGHT_REV),
                State.RIGHT_REV: (p.reverse_s, State.REVERSE_TO_WALL),
            }[self.state]
            if elapsed >= duration:
                self._enter(next_state, now)

        # Also validate the rear input on the tick that starts wall approach.
        if self.state == State.REVERSE_TO_WALL:
            status = rear.status(now, p.max_sensor_age_s)
            if status not in ("valid", "no-echo"):
                return self.stop("rear-sensor-" + status)
            if now - self._entered >= p.rear_timeout_s:
                return self.stop("rear-timeout")
            if status == "valid" and rear.cm < p.rear_wall_cm:
                self._enter(State.DONE, now)
                self.reason = "rear-threshold"
        return self.command()


@dataclass(frozen=True)
class Calibration:
    invert_steering: bool = True
    invert_zone3: bool = True  # Recorded v8 correction; post-fix hardware outcome unknown.

    def payloads(self, command: Command) -> dict[str, bytes]:
        """Pure direction/magnitude encoding; this does not transmit a CAN frame."""
        if abs(command.steer_deg) > 12 or abs(command.speed) > 255:
            raise ValueError("command exceeds workshop payload limits")
        steer = -command.steer_deg if self.invert_steering else command.steer_deg
        def encode(value: int) -> bytes:
            return bytes((int(value < 0), abs(value)))
        return {
            "ZONE1": encode(steer),
            "ZONE2": encode(command.speed),
            "ZONE3": encode(-command.speed if self.invert_zone3 else command.speed),
            "ZONE4": encode(command.speed),
        }
