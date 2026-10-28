"""APK-bound callback registration and gold/FX control fixtures, not Unity playback.

Valid Action delegates, non-null reached dependencies, finite binary32 arithmetic,
positive start HP and in-range int32 operations only. These checks are MODEL domain,
not validation claimed in native. Random/engine calls are supplied live hooks.
"""
import math,struct
from dataclasses import dataclass
from tools.verify.enemy_damage_model import f32


def combine(old,new):
    if old is None:return new
    if new is None:return old
    def invoke(*args):
        old(*args)
        new(*args)
    return invoke


def start_skeleton(get_receiver,on_hit,cancel_effect,*,unity_present=lambda obj:obj is not None):
    if unity_present(get_receiver()):
        receiver=get_receiver()  # native GetComponent called again, not cached first result
        if receiver is None:raise ValueError('native null failure after second GetComponent')
        receiver.hit_callback=on_hit  # assignment, NOT Combine
    cancel_effect()  # runs even if first Unity object check was false


def start_drop_gold(receiver,on_damage):
    if receiver is None:raise ValueError('native null failure')
    receiver.hit_damage_callback=combine(receiver.hit_damage_callback,on_damage)


def start_test_enemy(receiver,on_first_hit):
    if receiver is None:raise ValueError('native null failure')
    receiver.hit_callback=combine(receiver.hit_callback,on_first_hit)


@dataclass
class TestTimer:
    started: bool = False
    time_start: float = 0.0


def test_first_hit(timer,clock):
    if not timer.started:
        timer.started=True
        timer.time_start=f32(clock())


def skeleton_hit(get_slot_names,set_black,hit_color,is_invoking,cancel_invoke,invoke):
    i=0
    while i<len(get_slot_names()):
        set_black(get_slot_names()[i],hit_color)
        i+=1
    if is_invoking('CancelEffect'):cancel_invoke('CancelEffect')
    invoke('CancelEffect',f32(.01))


def skeleton_cancel(get_slot_names,set_black):
    i=0
    while i<len(get_slot_names()):
        set_black(get_slot_names()[i],(0.,0.,0.,1.))
        i+=1


def i32(value):
    if not -(1<<31)<=value<(1<<31):raise ValueError('outside bounded int32 fixture')
    return value


@dataclass
class DropGold:
    burst_coins: int = 28
    total_p: int = 10
    i_plus: int = 1


def drop_gold(state,_damage,*,get_current,get_start,get_parent,post):
    # _damage intentionally UNUSED by the native callback.
    current=f32(get_current());start=f32(get_start())
    if not math.isfinite(current) or not math.isfinite(start) or start<=0:
        raise ValueError('outside finite positive-start fixture')
    percent=f32(f32(current/start)*f32(100))
    if not math.isfinite(percent):raise ValueError('outside finite fixture')
    lost=i32(100-i32(math.trunc(percent)))
    threshold=i32(state.i_plus*state.total_p)
    if lost>threshold:
        state.i_plus=i32(state.i_plus+1)  # ONE increment/event, never a catch-up while loop
        coins=state.burst_coins  # read before GetTransform helper
        parent=get_parent()
        post(6,{'burstCoins':coins,'parent':parent})
    elif lost<state.total_p:state.i_plus=1
    return lost


def gold_plan(coins):
    # Division by5 is the spawn-budget grouping, NOT proof of collected currency value.
    coins=i32(coins)
    q=max(math.trunc(coins/5),0)
    r=i32(coins-5*q);pieces=i32(q+r)
    radius=f32(.15 if pieces==1 else .75 if pieces<4 else struct.unpack('<f',bytes.fromhex('6766e63f'))[0] if pieces==4 else 2.4)
    normal=(q<2 or r!=0)
    ones=r if normal else 5
    fives=q if normal else q-1
    return {'id70001_count':max(ones,0),'id70002_count':max(fives,0),'radius':radius,'pre_split_pieces':pieces}


def on_burst_golds(payload,*,get_position,burst_out):
    # Native cast/null failure is not a silent no-op.
    if not isinstance(payload,dict) or 'burstCoins' not in payload or 'parent' not in payload:
        raise ValueError('native null/cast failure fixture')
    plan=gold_plan(payload['burstCoins'])
    for item,count in ((70001,plan['id70001_count']),(70002,plan['id70002_count'])):
        for _ in range(count):
            center=get_position(payload['parent'])  # live transform reread for EVERY item
            burst_out(item,center,plan['radius'])
    return plan


def ellipse_target(center,radius,*,random_float,random_int):
    r=f32(radius)
    if not r>0 or not math.isfinite(r):raise ValueError('positive finite radius fixture')
    x=f32(random_float(-r,r))
    square=f32(r*r)
    factor=f32(f32(math.sqrt(square))/r)  # eccentricity=0, preserve native sqrt/div rounding
    cap=f32(factor*f32(math.sqrt(f32(square-f32(x*x)))))
    minimum=f32(0 if r>1 else f32(r*.5))
    y=f32(random_float(minimum,cap))  # forwards even minimum>cap, just like callsite
    sign=random_int(0,5)
    return (f32(f32(center[0])+x),f32(f32(center[1])+(-y if sign<2 else y)))


def burst_out(item,center,radius,*,random_float,random_int,get_item_z,pool_get,get_iitem,activate):
    target=ellipse_target(center,radius,random_float=random_float,random_int=random_int)
    obj=pool_get(item,(target[0],target[1],get_item_z()))
    if obj is None:raise ValueError('native null pooled object')
    component=get_iitem(obj)
    if component is None:raise ValueError('native null IItem')
    component((f32(center[0]),f32(center[1])),target)  # IItem.BurstOut slot0
    activate(obj,True)  # explicit activation happens AFTER interface dispatch
