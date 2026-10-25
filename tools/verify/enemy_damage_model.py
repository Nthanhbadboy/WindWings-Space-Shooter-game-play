"""Finite binary32 arithmetic up to first user callback, not full receiver execution."""
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
