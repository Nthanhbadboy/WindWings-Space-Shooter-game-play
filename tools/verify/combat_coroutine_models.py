"""Executable control-flow reconstructions, not full Unity/IL2CPP replacements.

Calls into emitters are events, not assumed spawn/hit counts. Timing is supplied
by caller; wait/frame events mark coroutine suspension. Exception/object lifetime,
ARM FPCR, collision and helper-internal emission are outside these small models.
"""
import math
import struct


def f32(x):
    return struct.unpack('<f',struct.pack('<f',x))[0]


def divide(a,b):
    """Preserve unguarded float division, including zero denominator."""
    if b == 0:
        return math.nan if a == 0 or math.isnan(a) else math.copysign(math.inf,a*math.copysign(1,b))
    return f32(a/b)


def rank_rounds(rank):
    return 1 if rank < 3 else 2 if rank == 3 else 3


def attack10(rank):
    for i in range(rank_rounds(rank)):
        yield ('round_dispatch',i)
        yield ('wait',0.25)


def attack11(rank, now):
    duration=f32(0.4) if rank < 3 else 1.0 if rank == 3 else f32(0.6)
    end=f32(now()+duration)
    while now() < end:
        for i in range(3):
            yield ('barrel_descriptor_dispatch',i)
        yield ('wait',f32(0.04))


def sync12(has_live_pair):
    yield ('wait',f32(0.2))
    if has_live_pair():
        yield ('side_dependent_sync_dispatch',None)


def shot_all13(number, shot_rate, scale_x):
    width=divide(scale_x,float(number))
    quotient=divide(shot_rate,float(number))
    rate=f32(0.05) if math.isnan(quotient) else min(quotient,f32(0.05))
    for i in range(max(number,0)):
        for side in range(2):
            yield ('barrel_dispatch',(i,side,width))
        yield ('wait',rate)


def move14(distance_xy, move, delta_time, speed, delay_callback):
    while distance_xy() > 0.5:
        move(f32(speed*delta_time()))
        yield ('frame',None)
    yield ('wait',delay_callback)  # even delay=0 is an actual WaitForSeconds
    yield ('required_callback',None)


def attack17(child_count):
    for i in range(max(child_count,0)):
        yield ('position_dispatch',i)
        if i % 2 == 1:
            yield ('wait',f32(0.2))
    yield ('frame',None)  # terminal state2, not another projectile


def particle18():
    while True:
        yield ('set_rate_over_distance',2.0)
        yield ('wait',0.5)
        yield ('set_rate_over_distance',0.0)
        yield ('wait',1.0)


def shoot_children(child_count, emit, shot_rate, number):
    """23/24: count is called twice per emitted child; number is forwarded."""
    i=0
    while i < child_count():
        emit(i,number)
        yield ('child_helper_dispatch',(i,number))
        rate_after=shot_rate()
        count_after=child_count()
        yield ('wait',divide(rate_after,float(count_after)))
        i+=1


def control7_9(attack_step, return_step, delay, pool, ended):
    """Injected step helpers return True at arrival. State order from raw tables."""
    while not attack_step():
        yield ('frame',None)  # state1; init speed/trigger are in attack helper
    yield ('wait',f32(0.35))  # state2 resume executes optional delay
    if delay > 0:
        yield ('wait',delay)  # state3, not state0
    while not return_step():
        yield ('frame',None)  # state4
    pool()
    ended()


def clone9_cleanup(duration):
    yield ('wait',duration)
    yield ('stop_attack',None)
    yield ('wait',f32(0.34))
    yield ('pool_clone',None)


def pumpkin_window_step(now, timeout, check_at, active, active_at, deactive_at):
    """One timestamp fixture for the post-arrival branch, not a clock simulator.

    Native samples Time.time separately; this helper assumes all those samples
    equal `now`. Events denote helper calls, not damage or spawned objects.
    """
    events=[]
    if now >= timeout:
        return {'events':['optional_callback','hide'], 'active':active,
                'active_at':active_at,'deactive_at':deactive_at,'check_at':check_at}
    if now > check_at:
        events.append('find_enemy');check_at=f32(now+0.5)
    if active:
        if now > deactive_at:
            active=False;active_at=f32(now+1.0)
        events.append('laser_helper')  # even after expiry; internal Check sees inactive
    elif now > active_at:
        active=True;deactive_at=f32(now+2.0)
    events.extend(['rotate','frame'])
    return {'events':events,'active':active,'active_at':active_at,
            'deactive_at':deactive_at,'check_at':check_at}
