"""Finite native-order coin pickup fixtures, not Unity physics/save/runtime approval.

Coin handlers only: other item dispatch branches remain in decoded source contract.
Per-call stage/tech/coin/device fields stable after initialization. Random motion,
wallet persistence and a complete Unity scheduler are not fabricated here.
"""
import math
from dataclasses import dataclass
from tools.verify.enemy_damage_model import f32
COIN_KIND={70001:1,70002:2,70011:1,70012:2}


def int32(v):
    if not -(1<<31)<=v<(1<<31):raise ValueError('outside fixture int32 conversion domain')
    return v


def wrap32(v):return (v+(1<<31))%(1<<32)-(1<<31)


def currency_delta(kind,stage,tech,coins,device_percent=0.0):
    if kind not in (1,2):raise ValueError('coin handler fixture only')
    for v in (stage,tech,coins):int32(v)
    stage_group=f32(int32(math.trunc(f32(f32(int32(stage+10))/f32(10)))))
    base=f32(stage_group*f32(1.5 if kind==1 else 3))
    level_minus14=int32(tech-14)
    lab=f32(f32(f32(level_minus14)/f32(3))+f32(1)) if level_minus14>=1 else f32(1)
    money=f32(coins);thresholds=[f32(lab*f32(x)) for x in (5500,4300,3300,2500)]
    stage_selected=stage
    # FCMP threshold,balance: MI means THRESHOLD < BALANCE, not the reverse.
    w22=0 if thresholds[0]<money else stage
    if thresholds[0]<money:
        amount=f32(1 if kind==1 else 2);band='above5500'
    else:
        amount=f32(min(base,f32(16 if kind==1 else 23))+f32(2.5 if kind==1 else 12))
        w23=0 if thresholds[1]<money else w22
        if thresholds[1]<money:
            amount=f32(amount*f32(.25)) if kind==1 else f32(amount/f32(6));band='4300to5500'
        elif thresholds[2]<money:
            amount=f32(amount/f32(3)) if kind==1 else f32(amount*f32(.25));stage_selected=w22;band='3300to4300'
        else:
            if thresholds[3]<money:amount=f32(amount*f32(.5));band='2500to3300'
            else:band='atMost2500'
            stage_selected=w23
    amount=f32(amount*f32(f32(device_percent)+f32(1)))
    if stage_selected<=40:amount=f32(amount*f32(.86))
    if not math.isfinite(amount):raise ValueError('finite fixture only')
    return dict(delta=int32(math.trunc(amount)),untruncated=amount,band=band,lab_factor=lab,thresholds=thresholds)


@dataclass
class Currency:
    coin_count: int = 0
    device_percent: float = 0.0


def collect_coin(kind,state,*,get_stage,get_tech,post):
    stage=get_stage();tech=get_tech()
    result=currency_delta(kind,stage,tech,state.coin_count,state.device_percent)
    state.coin_count=wrap32(state.coin_count+result['delta'])
    post(48,None)  # EventID.AddCoin, no payload; store BEFORE synchronous post
    return result


def bind_coin_callbacks(callbacks,small,large):
    callbacks[1]=small;callbacks[2]=large  # direct STR assignments in Controller.Start


def coin_item_collected(item,*,get_index,get_callback,play_sound):
    index=get_index(item)
    if index not in COIN_KIND:raise ValueError('outside coin-only fixture, not an APK rejection')
    callback=get_callback(COIN_KIND[index])
    if callback is not None:callback(item)
    play_sound()


def on_collect_event(payload,*,is_exact_gameobject,get_tag,item_collected):
    if not is_exact_gameobject(payload):raise ValueError('native null/type failure')
    if get_tag(payload)=='Item':item_collected(payload)
    # No Pool call in OnCollectItem receiver.


def trigger_enter(get_gameobject,tag,*,active_hit_enemy,invisible,item_collected,pool,non_item=lambda:None):
    if tag=='Item':
        item_collected(get_gameobject())
        pool(get_gameobject())  # live getter again AFTER callback/event dispatch
    elif active_hit_enemy and not invisible:non_item()


def apply_device_coin_bonus(state,player_index,*,get_devices,get_device,get_stat_value2):
    devices=get_devices(player_index)  # failure here leaves previous percent unchanged
    state.device_percent=f32(0)
    if devices is None:raise ValueError('native null device array')
    for instance_id in devices:
        if instance_id==-1:continue
        device=get_device(instance_id)
        if device is None:raise ValueError('native null device')
        if 5000<=device['id']<=5999:
            before=state.device_percent
            value=f32(get_stat_value2(device))
            state.device_percent=f32(before+f32(value/f32(100)))


def stat_value2(device,stat_rows,percent_by_levels2):
    """Native Device_Get_Data.GetStatValue2; rows are supplied configuration, not guesses."""
    category=math.trunc(device['id']/1000)
    rank=device['rank'];row=stat_rows[category+4]
    if rank<0 or rank>=len(row):raise IndexError('native array bound')
    first=f32(row[rank])
    if first==0:return f32(0)
    if category-1<0 or category-1>=len(percent_by_levels2):raise IndexError('native array bound')
    return f32(f32(row[rank])+f32(f32(percent_by_levels2[category-1])*f32(int32(device['lv']+1))))


def stage_index(company_name,fixed_stage,map_current_test,is_branch,stage_branch,stage_current):
    if company_name=='Test' and fixed_stage:return map_current_test
    return stage_branch if is_branch else stage_current


def tech_lab_level(game_mode,scene_name,get_saved):
    if game_mode==4 and scene_name=='Game':return 0
    return get_saved()


def droid_pickup_suffix(distance,is_force,*,collect_to,get_gameobject,post,pool,reset_target=lambda:None):
    """Reached suffix only, AFTER Update/CollectItems target/scan eligibility checks."""
    distance=f32(distance)
    if not math.isfinite(distance):raise ValueError('finite fixture only')
    if distance<5 and not is_force:
        collect_to();return 'force-to-player'
    if distance<.5:
        post(2,get_gameobject())
        pool(get_gameobject())
        reset_target()  # Update resets target=player; CollectItems does not
        return 'collected'
    return 'move-or-continue'
