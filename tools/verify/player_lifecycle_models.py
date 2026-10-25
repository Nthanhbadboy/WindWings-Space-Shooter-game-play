"""Finite native-order HP/extra-life fixtures; not Unity scheduler/input/visual approval.

Controller startup assigns health.onExtraLife directly (not Delegate.Combine).
Normal and PVP paths dispatch actual callbacks, but Invoke's string target and
its later execution are external scheduler inputs here; not guessed RebornDone.
"""
from dataclasses import dataclass
from tools.verify.damage_receiver_models import finite, f32


@dataclass
class Lifecycle:
    move_enabled: bool = True
    time_scale: float = 1.0
    flag_pair: tuple = (False, False)  # exact bool-pair store; no invented field names


def gain_health(player, amount, *, has_fx=False, fx=lambda: None, post=lambda *_: None):
    # Native upper clamp only: negative gain can make HP negative.
    player.hp=min(finite(finite(player.hp)+finite(amount)),finite(player.start_hp))
    if has_fx:fx()
    payload=player.hp  # loaded again after optional Particle.Play
    post(21,payload)
    return payload


def heal_hp(get_start_hp, percent, delta_time, gain):
    """Reached HealHp iterator; snapshot target, local progress starts at1, null yields.

    Return/yield control follows MoveNext: scheduler supplies each scaled deltaTime.
    Local progress, NOT current HP, controls completion. No catch-up/completion snap.
    """
    target=finite(finite(get_start_hp())*finite(percent))
    per_second=finite(finite(target/100.0)/f32(.02))
    progress=f32(1.0)
    while progress<target:
        amount=finite(per_second*finite(delta_time()))
        progress=finite(progress+amount)
        gain(amount)
        yield ('frame',None)


def zone_heal(get_start_hp,gain):
    """First wait precedes first heal; live max HP read again on each resume."""
    while True:
        yield ('wait',f32(.2))
        gain(finite(finite(get_start_hp())*f32(.01235)),True)


def no_touch(mouse_up,mouse_down,mouse_held,touch_count):
    return not mouse_up() and not mouse_down() and not mouse_held() and touch_count()==0


def normal_extra_life(player,state,*,gain,no_touch_predicate,schedule_done,start_heal,
                      prepare=lambda: None,finish_effect=lambda: None):
    """Two phases; health gain and Invincible store happen BEFORE pause/WaitUntil.

    start_heal must dispatch the separate HealHp coroutine, not instantly fill HP.
    Schedule hooks may throw or execute fixture code; those effects are not swallowed.
    """
    prepare()
    gain(1.0)
    player.invincible=True
    state.move_enabled=False
    schedule_done()
    state.time_scale=0.0;state.flag_pair=(True,True)
    yield ('wait_until',no_touch_predicate)
    finish_effect()
    state.time_scale=f32(.05)
    start_heal(.5)
    state.flag_pair=(False,False)


def pvp_extra_life(player,state,*,post,gain,schedule_done,start_heal,prepare=lambda: None):
    post(86,None)
    prepare();gain(1.0)
    player.invincible=True;state.move_enabled=False
    schedule_done();start_heal(1.0)
    # No Time.timeScale write or WaitUntil in DoExtraLifePVP.
