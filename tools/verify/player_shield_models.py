"""Reached non-null shield/reborn flag blocks, not an entire Unity controller.

No reference counting: callbacks may clear invincible during rebirth. RebornDone
preserves previous invincible on shield branches; preservation != setting true.
Particle/bone helpers preceding RebornDone's flag block are outside this fixture.
"""
from dataclasses import dataclass


@dataclass
class Shields:
    skill: bool = False
    droid101: bool = False
    droid103: bool = False
    onehit: bool = False


def shield_callback(player, lifecycle, flags, kind, active):
    if kind not in ('skill','droid101','droid103','onehit'):raise ValueError(kind)
    setattr(flags,kind,bool(active))
    aggregate=flags.skill or flags.droid101 or flags.droid103
    if kind!='onehit':player.invincible=bool(aggregate)
    lifecycle.hit_enemy_enabled=not aggregate


def reborn_done_flag_block(player,lifecycle,flags,*,restricted_cleanup=lambda:None):
    """Called after root cleared inReborning and ran particle/bone helpers.

    skill/101 branch: Player_Talent.reborning=false, cleanup may call Startup or item helpers.
    Hook models those calls only, not inferred registration or helper side effects.
    Return records whether this block writes Player_Talent.reborning, not its final live value.
    """
    if flags.skill or flags.droid101:
        lifecycle.hit_enemy_enabled=False
        restricted_cleanup()
        return {'talent_reborning_write':False}
    if not flags.onehit and not flags.droid103:
        player.invincible=False
    lifecycle.hit_enemy_enabled=not flags.droid103
    return {'talent_reborning_write':None}


@dataclass
class ZoneState:
    # Fixture keys, not UnityEngine.Object equality/destruction emulation.
    zones: set
    healing: bool = False
    heal_cor: object = None
    health_invisible: bool = False
    physics_invisible: bool = False


def set_zone_invisible(state,zone,invisible,heal,in_reborning,*,start_heal,stop_heal,display=lambda _:None):
    if invisible:
        state.zones.add(zone)
        if heal and not state.healing:
            state.healing=True
            if state.heal_cor is not None:stop_heal(state.heal_cor)
            state.heal_cor=start_heal()
    else:state.zones.discard(zone)
    if in_reborning():return  # live read after StartCoroutine/helper calls
    state.health_invisible=bool(invisible)
    state.physics_invisible=bool(invisible)
    display(not invisible)
    if not invisible and state.healing:
        state.healing=False
        if state.heal_cor is not None:stop_heal(state.heal_cor)
