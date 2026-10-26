"""Finite APK-native fixtures: shared HP writers and UI-only drone power.

No claim of whole-program writer absence, scene boot/event delivery, Unity timer
execution, full damage/armor receiver, save durability or int32 overflow behavior.
"""
from dataclasses import dataclass
from tools.verify.enemy_damage_model import f32


@dataclass
class SharedHP:
    start:float=2000
    current:float=0
    tech_heal:float=0
    device_heal:float=0
    device_reduction:float=0
    immune_deadline:float=0


def get_start_hp(get_points,get_ability,base=2500,step=f32(.18),abi7_amount=1):
    points=get_points(0)
    ability=get_ability(7)
    percent=f32(f32(step*f32(points))+f32(f32(abi7_amount)*f32(ability)))
    return f32(f32(base)*f32(percent+f32(1)))


def reset_hp(s):s.current=s.start


def ability_changed36(s,payload,get_start):
    if payload is None:raise ValueError('native null unbox')
    if type(payload) is not int:raise TypeError('native Int32 cast')
    if payload==7:s.start=get_start()


def recover_fraction(level,base=f32(.01)):
    if level==0:return f32(0)
    extra=.1 if level>7 else .08 if level>4 else .06 if level>2 else .03 if level==2 else 0
    return f32(base*f32(f32(extra)+f32(1)))


def immune_interval(level):
    return f32(25 if level>9 else 30 if level==9 else 35 if level>6 else 40 if level==6 else 45 if level>3 else 50 if level>=1 else float.fromhex('0x1.fffffep+127'))


def refresh64(s,*,mode,wave,get_start,get_recover,post,schedule,now,get_immune):
    if mode==1 and wave!=0:
        old_start=s.start;old_current=s.current
        new_start=get_start()
        if old_start==0:raise ValueError('outside finite fixture ratio domain; NOT a native throw claim')
        current=f32(f32(old_current/old_start)*new_start)
        s.start=new_start;s.current=current
        post(21,current)
    else:
        s.start=get_start();reset_hp(s)
    s.tech_heal=f32(get_recover()*s.start)
    schedule('AutoGainHealth',f32(5),f32(5))
    first=now();s.immune_deadline=f32(first+get_immune())
    # Native then resolves player reference. That unrelated object lookup is not simulated.


def change_devices(s,source,*,get_ids,get_device,get_stat1):
    ids=get_ids(source)
    s.device_reduction=0;s.device_heal=0
    if ids is None:raise ValueError('native null device array after reset')
    for instance in ids:
        if instance==-1:continue
        device=get_device(instance)
        if device is None:raise ValueError('native null device after partial writes')
        if 1000<=device['id']<=1999:
            old=s.device_reduction
            s.device_reduction=f32(old+f32(get_stat1(device)/f32(100)))
        elif 5000<=device['id']<=5999:
            old=s.device_heal;base=s.start
            s.device_heal=f32(old+f32(f32(base*get_stat1(device))/f32(100)))


def gain_health(s,amount,*,post,has_fx=False,fx=lambda:None):
    new=f32(s.current+amount);s.current=new if new<s.start else s.start
    if has_fx:fx()
    post(21,s.current)


def auto_gain(s,post):
    if s.current<=0:return False
    new=f32(f32(s.current+s.tech_heal)+s.device_heal)
    s.current=new if new<s.start else s.start
    post(21,s.current)
    return True


def board_power(source,*,get_level,basic,delta,index_default=20001):
    level=get_level(source)
    if basic is None or delta is None:raise ValueError('native null board array')
    i=source-index_default
    a=max(0,min(i,len(basic)-1));b=max(0,min(i,len(delta)-1))
    if not 0<=a<len(basic) or not 0<=b<len(delta):raise IndexError('native array bounds')
    power=f32(f32(basic[a])*f32(f32(f32(delta[b])*f32(level))+f32(1)))
    return dict(power=power,rounded=round(power))  # finite Int32 range: ties-to-even
