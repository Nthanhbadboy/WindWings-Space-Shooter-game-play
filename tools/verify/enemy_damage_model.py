"""Finite binary32 enemy arithmetic plus mutable native-order callback receiver."""
import math
from tools.verify.player_main_cannon_timer import f32


def calculate(hp, damage, armor, no_damage=False, ignore_invincible=False):
    # Validation belongs only to this bounded model, not the APK.
    if any(not math.isfinite(v) for v in (hp, damage, armor)):
        raise ValueError('finite model inputs only')
    hp, damage, armor = map(f32, (hp, damage, armor))
    if (no_damage and not ignore_invincible) or hp <= 0:
        return dict(hp=hp, accepted=False, pre_callback_loss=0.0)
    if armor >= 0:
        factor = f32(100.0 / f32(100.0 + armor))
    else:
        factor = f32(2.0 - f32(100.0 / f32(100.0 - armor)))
    adjusted = f32(factor * damage)
    after = max(f32(hp - adjusted), 0.0)
    return dict(hp=after, accepted=True, armor_factor=factor,
                pre_callback_loss=f32(hp - after))


# Mutable references deliberately preserve native callback/re-entrancy semantics.
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class HpRef:
    hp: float


@dataclass
class Receiver:
    armor: float = 0.0
    no_damage: bool = False
    hit_callback: Optional[Callable] = None
    hit_damage_callback: Optional[Callable] = None


def calculate_with_callbacks(receiver, hp_ref, damage, ignore_invincible=False, trace=None):
    """Reached Enemy_Health.CalculateDamage; hooks are fixture inputs, not APK bindings.

    hp_ref and receiver are captured objects; replacing an outer controller's data
    during a callback does not redirect the ref argument or receiver of this call.
    Finite arithmetic domain is inherited from calculate(). Exceptions propagate.
    """
    trace = [] if trace is None else trace
    before = f32(hp_ref.hp)
    result = calculate(before, damage, receiver.armor, receiver.no_damage, ignore_invincible)
    if not result['accepted']:
        return trace
    hp_ref.hp = result['hp']; trace.append(('hp_store', hp_ref.hp))
    callback = receiver.hit_callback
    if callback is not None:
        trace.append(('hit_callback', None)); callback()
    callback = receiver.hit_damage_callback  # native reload AFTER first callback
    if callback is not None:
        loss = f32(before - hp_ref.hp)  # native ref argument, not controller.data reload
        if loss > 0:
            trace.append(('hit_damage_callback', loss)); callback(loss)
    return trace
