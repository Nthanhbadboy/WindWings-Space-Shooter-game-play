"""APK-order receiver fixtures, not Unity, subscriber bindings, clocks or measured DPS.

Dependencies are live/non-null, ability counts/coefficients stable during a call,
random/Time reads supplied by caller. Hooks represent reached calls, NOT evidence
that a particular scenario registers them. Hook exceptions deliberately propagate.
Finite binary32 intermediates and in-range truncations only; native infinity selects
and FCVTZS saturation remain in preserved native anchors, not emulated here.
"""
import math
from dataclasses import dataclass, field
from tools.verify.enemy_damage_model import HpRef, Receiver, calculate_with_callbacks
from tools.verify.player_main_cannon_timer import f32


@dataclass
class Damager:
    damage: float
    kill_event: object = None


@dataclass
class Enemy:
    data: HpRef
    receiver: Receiver = field(default_factory=Receiver)
    can_attack: bool = True
    health_exists: bool = True
    invisible: bool = False
    can_move: bool = True


def enemy_take_damage(enemy, damager, *, ignore=False, on_hit=lambda: None,
                      destroy=lambda: None, stun=lambda _: None, burn=lambda *_: None,
                      level=lambda _: 0, coefficient=lambda _: 0.0,
                      stun_present=True, random_int=lambda: 0, random_float=lambda: 0.0):
    """Wrapper + controller; destroy hook dispatches selected base/override body.

    UpdateHpBar is recorded at its native position; UI rendering not emulated.
    No artificial HP hook is inserted there. Caller can supply a concrete destroy
    dispatch fixture, including delayed implementations that return before pooling.
    """
    trace = [('display_on_hit', None)]; on_hit()
    if enemy.data.hp <= 0 or not enemy.can_attack:
        return trace
    if damager is not None and enemy.health_exists:
        calculate_with_callbacks(enemy.receiver, enemy.data, damager.damage, ignore, trace)
    else:
        trace.append(('log_error', None))  # NOT an early controller return
    trace.append(('update_hp_bar', None))
    if enemy.data.hp > 0:
        trace.append(('survive', None))
        if stun_present and level(31) >= 1:
            chance = f32(f32(coefficient(31)) * f32(level(31)))
            if chance > 0 and chance >= random_int():
                trace.append(('stun', 3.0)); stun(3.0)
        if level(34) >= 1:
            chance = f32(f32(coefficient(34)) * f32(level(34)))
            if chance >= 100 or chance >= f32(random_float()):
                if damager is None:
                    raise ValueError('native null-dereference path: burn requires Damager')
                copied = Damager(damager.damage, damager.kill_event)
                trace.append(('burn', (copied.damage, f32(0.4), 6.0)))
                burn(copied, f32(0.4), 6.0)
    else:
        enemy.can_move = False; enemy.invisible = True
        trace.append(('disable_collider', True))
        trace.append(('destroy_dispatch', 0)); destroy()
        if damager is None:
            raise ValueError('native null-dereference path after destroy')
        callback = damager.kill_event  # loaded AFTER complete destroy dispatch returns
        if callback is not None:
            trace.append(('kill_event', None)); callback()
    return trace


def base_enemy_destroy_zero(*, on_dead=None, on_destroyed=None, burst=lambda: None,
                            destroyed=lambda: None, pool=lambda: None):
    """Base Enemy_Destroy.Destroy(0), normal-return dependencies; NOT overrides.

    on_destroyed is a getter: on_dead may change that field before its native reload.
    Pool clears onDead in native body; caller owns that mutable field if needed.
    """
    trace = []
    if on_dead is not None:
        trace.append('on_dead'); on_dead()
    callback = on_destroyed() if on_destroyed is not None else None
    if callback is not None:
        trace.append('on_destroyed'); callback()
        trace.append('burst_items'); burst()
        trace.append('destroyed_effects'); destroyed()
        trace += ['event_19_enemy_die', 'event_79_pool_enemy']
    trace.append('pool'); pool()
    trace.append('event_79_pool_enemy')
    return trace


def finite(value):
    value = f32(value)
    if not math.isfinite(value):
        raise ValueError('finite binary32 model domain only')
    return value


def trunc(value):
    value = finite(value)
    if not -(2**31) <= value < 2**31:
        raise ValueError('in-range FCVTZS model domain only')
    return int(value)


def player_damage_amount(damage, device, armor, abi9, abi10):
    """Ordered FMUL/FSUB, armor, FCVTZS, reductions, FCVTZS (not one truncation)."""
    damage, device, armor, abi9, abi10 = map(finite, (damage, device, armor, abi9, abi10))
    reduced = finite(damage - finite(damage * device))
    factor = (finite(100 / finite(100 + armor)) if armor >= 0 else
              finite(2 - finite(100 / finite(100 - armor))))
    first = trunc(finite(reduced * factor))
    multiplier = max(finite(finite(1 - abi9) - abi10), 0.0)
    final = trunc(finite(finite(first) * multiplier))
    return first, final


@dataclass
class Player:
    hp: float = 100.0  # represents shared Player_Health.CurrentHealth static cell
    start_hp: float = 100.0
    armor: float = 0.0
    device: float = 0.0
    invisible: bool = False
    victory: bool = False
    invincible: bool = False
    attack_invisible: bool = False
    immune_deadline: float = 0.0
    shield: bool = False
    destroy_shield: object = None
    clear_deadline: float = 0.0
    is_alive: bool = True
    pvp_life: int = 0
    reborn_now: int = 0
    mode: int = 1
    on_extra_life: object = None


def player_take_damage(player, damager, *, ignore=False, clock=lambda: 0.0,
                       immune_time=lambda: 0.0, level=lambda _: 0,
                       coefficient=lambda _: 0.0, random_float=lambda: 100.0,
                       heal_start_hp=lambda: 100.0, heal=lambda _: None,
                       miss=lambda: None, ability35=lambda: None,
                       post=lambda *_: None, set_invisible=lambda: None,
                       death_effect=lambda: None, on_die=lambda: None,
                       cleanup=lambda: None):
    """Player_Health.TakeDamage, including death/extra-life; stable stats fixture.

    post(event,payload) is synchronous and may mutate shared player.hp. The first
    event payload is the value BOXED before dispatch, not a mutable HP reference.
    Missing on_die models native null failure (after isAlive=false), not a no-op.
    """
    t = []
    if player.hp <= 0 or player.invisible or damager is None or player.victory:
        return t
    if player.invincible and not ignore:
        if level(30) >= 1 and f32(random_float()) <= f32(f32(coefficient(30)) * f32(level(30))):
            amount = finite(finite(finite(coefficient('30_amount') / 100) * f32(level(30))) * finite(heal_start_hp()))
            t.append(('heal_interface', amount)); heal(amount)
        return t
    if player.attack_invisible:
        return t
    # This seemingly reversed branch is in the APK: expired deadline skips this hit.
    if f32(player.immune_deadline) < finite(clock()):
        player.immune_deadline = finite(finite(clock()) + finite(immune_time()))
        t.append(('immune_deadline_store', player.immune_deadline)); return t
    if level(8) >= 1:
        chance = finite(finite(coefficient(8)) * f32(level(8)))
        if player.start_hp == 0:
            raise ValueError('finite ratio model requires nonzero start_hp')
        if finite(player.hp / player.start_hp) < f32(0.3):
            chance = finite(chance + finite(finite(coefficient(22)) * f32(level(22))))
        chance = min(chance, 90.0)
        if chance > f32(random_float()):
            t.append(('miss', None)); miss(); return t
    if player.shield:
        callback = player.destroy_shield
        player.shield = False; t.append(('shield_clear', None))
        if callback is not None:
            t.append(('destroy_shield', None)); callback()
        return t
    if level(28) >= 1 and f32(player.clear_deadline) < finite(clock()):
        player.clear_deadline = finite(finite(clock()) + 1.0)
        t.append(('clear_effect_99005', None))
    if level(35) >= 1:
        t.append(('ability35_virtual', True)); ability35()
    a9 = finite(finite(coefficient(9)) * f32(level(9)))
    a10 = finite(finite(coefficient(10)) * f32(level(10)))
    first, final = player_damage_amount(damager.damage, player.device, player.armor, a9, a10)
    player.hp = max(finite(finite(player.hp) - finite(final)), 0.0)
    t += [('truncations', (first, final)), ('hp_store', player.hp)]
    payload = player.hp
    t.append(('event', 21)); post(21, payload)
    t.append(('event', 39)); post(39, None)
    if player.hp > 0:
        t.append(('set_attack_invisible', None)); set_invisible(); return t
    t.append(('death_effect_91005_audio58', None)); death_effect()
    player.pvp_life -= 1; t.append(('pvp_life', player.pvp_life))
    extra = player.mode == 6 and player.pvp_life >= 1
    if not extra and level(16) >= 1 and level(16) > player.reborn_now:
        player.reborn_now += 1; extra = True
        t.append(('reborn_now', player.reborn_now))
    if extra:
        callback = player.on_extra_life
        if callback is not None:
            t.append(('extra_life_callback', None)); callback()
        return t  # no isAlive=false, on_die, cleanup or event18 in this branch
    player.is_alive = False; t.append(('is_alive_store', False))
    if on_die is None:
        raise ValueError('native null onDie invocation path')
    t.append(('on_die', None)); on_die()
    t.append(('cleanup', None)); cleanup()
    t.append(('event', 18)); post(18, None)  # actual payload Transform; identity omitted
    return t


def immune_interval(tech_level):
    """Player_Get_Datas.TimeToImmuneOneHit, tech index0, not immunity duration."""
    if tech_level < 1:return f32(3.4028234663852886e38)
    if tech_level <= 3:return 50.0
    if tech_level <= 5:return 45.0
    if tech_level == 6:return 40.0
    if tech_level <= 8:return 35.0
    if tech_level == 9:return 30.0
    return 25.0


def delayed_enemy_destroy(start_callback, condition_getter, base_destroy):
    """Two MoveNext phases; scheduler owns WaitUntil polling/resumption.

    Serialized delayTime/default2 is NOT used by this native implementation.
    condition_getter fetches the current Func<bool> each poll, not a cached delegate.
    """
    if start_callback is not None:start_callback()
    def predicate():
        callback=condition_getter()
        if callback is None:raise ValueError('native null condition invocation path')
        return callback()
    yield ('wait_until',predicate)
    base_destroy()


def mb_die_effect(activate_effect, hide_body, burst, destroyed, post):
    """MB death's 4 source states; exactly 3 waits, no base Pool tail."""
    activate_effect();yield ('wait',1.0)
    hide_body();yield ('wait',1.0)
    burst();yield ('wait',1.0)
    destroyed();post(19);post(79)


def death_blast(ability_level, chance_per_level, random_float, amount_getter, query,
                layer_mask, *, collider_live=lambda _: True, object_live=lambda _: True,
                layer=lambda _: 0, get_health=lambda c: True, get_damageable=lambda c: c,
                take_damage=lambda *_: None):
    """Enemy_Destroy.Destroyed ability32 branch, ordered collider list, NO dedup.

    query(radius,mask) supplies Physics overlap results; engine spatial query omitted.
    get_health only requires a non-null IHealth; native does NOT invoke IsAlive here.
    amount is get_abi32Amount(), NOT the incoming damage or observed HP loss.
    """
    if ability_level < 1:return []
    chance=finite(finite(chance_per_level)*f32(ability_level))
    if chance < 100 and chance < f32(random_float()):return []
    amount=finite(amount_getter());hits=[]
    for collider in query(3.0,layer_mask):
        if not collider_live(collider) or not object_live(collider):continue
        mask=layer_mask & 0xffffffff
        if mask != (mask | (1 << (layer(collider)&31))):continue
        health=get_health(collider);receiver=get_damageable(collider)
        if health is None or receiver is None:continue
        receiver=get_damageable(collider)  # native rereads getter before dispatch
        request=Damager(amount,None)
        take_damage(receiver,request,False);hits.append((receiver,request))
    return hits
