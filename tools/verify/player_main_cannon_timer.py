"""Bounded ship1 timer branch model; not Unity, bullet delivery or DPS."""
import math
import struct
from dataclasses import dataclass, replace


def f32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]


@dataclass(frozen=True)
class Timer:
    deadline: float = 0.0
    extra_deadline: float = 0.0
    turn: int = 0


def step(state, now, interval, extra_delay, extra_count):
    """One reached MainCannonShoot invocation, stable Time.time, finite nonnegative domain.

    Success means entry to emitter section, NOT a successfully emitted/hitting bullet.
    Caller gameplay gates, Unity calls/failures and multiple Time.time reads are omitted.
    Input validation here is model-only, not a native validation claim.
    """
    if not isinstance(extra_count, int) or isinstance(extra_count, bool) or not 0 <= extra_count < 2**31 - 1:
        raise ValueError('model requires bounded nonnegative extra count')
    if not 0 <= state.turn <= extra_count:
        raise ValueError('model requires normalized counter')
    values = [now, interval, extra_delay, state.deadline, state.extra_deadline]
    if any(not math.isfinite(v) or v < 0 for v in values):
        raise ValueError('finite nonnegative model domain only')
    now, interval, extra_delay, deadline, extra_deadline = map(f32, values)
    normalized = Timer(deadline, extra_deadline, state.turn)
    if now < deadline:
        return normalized, False
    if extra_count >= 1:
        if now < extra_deadline:
            return normalized, False
        extra_deadline = f32(now + extra_delay)
        turn = state.turn + 1
        if turn <= extra_count:
            return Timer(deadline, extra_deadline, turn), True
        return Timer(f32(now + interval), extra_deadline, 0), True
    return replace(normalized, deadline=f32(now + interval)), True
