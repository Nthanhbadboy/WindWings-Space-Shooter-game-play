"""Provisional finite native-order fixtures. Drone_Attack != legacy Droid_Attack.

No Unity tick-duration, projectile-hit or DPS promise. Configuration and source
getters are explicit inputs; callback order and live field rereads are retained.
"""
import math
from dataclasses import dataclass
from tools.verify.enemy_damage_model import f32


def max_power_points(tech,ability12,ability13):
    tier=4 if tech>5 else 3 if tech>3 else 2 if tech>1 else 1 if tech==1 else 0
    return min(tier+ability12+2*ability13,4)+6


def start_power_points(get_tech,get_ability,use_items):
    tech=get_tech()
    value=4 if tech>7 else 3 if tech==7 else 2 if tech>4 else 1 if tech>2 else 0
    if use_items is None:raise ValueError('native null array')
    if len(use_items)<4:raise IndexError('native array bounds')
    if use_items[3]:value+=3;use_items[3]=False
    # GetMaxPowerUpPoints calls tech again; consume flag before this dependency.
    tier_tech=get_tech();a=get_ability(12);b=get_ability(13)
    return min(value,max_power_points(tier_tech,a,b))


@dataclass
class PlayerLevel:
    lv:int=-1
    def get(self,get_start):
        if self.lv==-1:self.lv=get_start()
        return self.lv
    def set(self,value):self.lv=value


@dataclass
class Wing1:
    start_rate:float=f32(.12)
    start_speed:float=f32(14)
    rate:float=0
    speed:float=0
    angle:float=0
    number:int=0
    count:int=0
    time_shot:float=0
    time_barrel:float=0


def configure_wing1(s,get_level,is_super,numbers):
    s.count=0
    first=get_level();second=get_level()
    if first>2:
        n=second-2
        idx=0 if n < -5 else min(math.trunc(n/2)+2,len(numbers)-1)
    else:idx=0 if second<0 else min(second,len(numbers)-1)
    if idx<0 or idx>=len(numbers):raise IndexError('native array bounds')
    s.number=numbers[idx]
    if is_super():return
    s.rate=s.start_rate;s.speed=s.start_speed
    s.angle=min(f32(f32(math.trunc(get_level()/10))*f32(3)+f32(5)),f32(15))
    level=get_level()
    s.rate=f32(s.start_rate+f32(f32(level)*f32(-.0035)))
    s.speed=min(f32(s.start_speed+f32(f32(level)*f32(1.1))),f32(42))


def wing1_packet(s,number,*,now,is_super,attempt,table_length=10):
    if now()<s.time_shot:return False
    if now()<s.time_barrel:return False
    spacing=f32(f32(f32(s.rate+f32(-.01))*f32(.3))/f32(table_length))
    s.time_barrel=f32(now()+spacing)
    packet_size=3 if is_super() else 2
    s.count+=1
    if s.count==number:s.count=0;s.time_shot=f32(now()+s.rate)
    for index in range(packet_size):attempt(index)
    return True


@dataclass
class LegacyDroidGun:
    count_shots:int=0
    time_shot:float=0
    time_reload:float=.5
    time_rounds:float=3
    count_mags:int=6
    infinity_rounds:bool=False
    time_to_start:float=0
    time_to_shot:float=0
    time_to_reload:float=0
    time_to_rounds:float=0
    count_of_mags:int=0
    count_of_blts:int=0
    is_stunned:bool=False
    audio_clip:int=0
    mag_start:object=None
    mag_ended:object=None
    round_ended:object=None


def legacy_start_sync(s,infinity=False):
    s.time_to_shot=s.time_to_reload=s.time_to_rounds=0
    s.count_of_mags=s.count_of_blts=0
    s.infinity_rounds=infinity


def legacy_mag_end(s,now):
    s.time_to_reload=f32(now()+s.time_reload)
    if s.mag_ended is not None:s.mag_ended()
    if s.count_mags<1 or s.count_of_mags>=s.count_mags:return
    s.count_of_mags+=1
    if s.count_of_mags!=s.count_mags:return
    s.count_of_mags=0
    if not s.infinity_rounds and s.round_ended is not None:s.round_ended()
    s.time_to_rounds=f32(now()+s.time_rounds)


def legacy_auto(s,*,now,child_count,get_child,parent,shoot,audio,mag_end=None):
    end=mag_end if mag_end is not None else lambda:legacy_mag_end(s,now)
    if s.mag_start is not None:s.mag_start()
    if s.time_shot>0:
        if now()<s.time_to_shot:return
        shoot(get_child(0 if s.count_shots>=1 else s.count_of_blts))
        s.time_to_shot=f32(now()+s.time_shot);s.count_of_blts+=1
        if s.audio_clip:audio(s.audio_clip)
        target=s.count_shots if s.count_shots>=1 else child_count()
        if s.count_of_blts==target:end();s.count_of_blts=0
    else:
        if s.count_shots>=1:
            i=0;s.count_of_blts=0
            while i<s.count_shots:
                shoot(get_child(0));i+=1;s.count_of_blts+=1
        elif child_count()>0:
            i=0
            while i<child_count():shoot(get_child(i));i+=1
        else:shoot(parent)
        if s.audio_clip:audio(s.audio_clip)
        end()


def legacy_fixed(s,*,now,can_attack,run_auto):
    if now()<s.time_to_start:return
    if can_attack is not None and not can_attack():return
    if s.time_rounds>0 and now()<s.time_to_rounds:return
    if s.time_reload>0 and now()<s.time_to_reload:return
    run_auto()  # is_stunned guard belongs to Shoot, NOT these scheduler counters


@dataclass
class ProjectileDrone:
    shot_rate:float=0
    charge_rate:float=0
    shot_deadline:float=0
    charge_deadline:float=0
    number:int=1
    count:int=0


def drone_rate(base_rate,get_ability,get_amount):
    if get_ability(25)>=1:
        amount=f32(get_amount())
        points=get_ability(25)  # native helper called again, not a cached first result
        denominator=f32(amount*f32(points))
        if denominator==0:raise ValueError('outside finite fixture division domain')
        return f32(f32(base_rate)/denominator)
    return f32(base_rate)


def projectile_drone_shoot(s,*,now,get_barrels,attempt,charged=True):
    if charged and s.charge_deadline>now():return False
    if now()<s.shot_deadline:return False
    s.shot_deadline=f32(now()+s.shot_rate)
    barrels=get_barrels()
    if barrels is None:raise ValueError('native null array after deadline write')
    length=len(barrels)
    for index in range(length):
        attempt(index)  # adapter preserves GetObject/GetComponent/activation order
        if charged:
            s.count+=1
            if s.count>=s.number:
                s.count=0;s.charge_deadline=f32(now()+s.charge_rate)
        # native loop does NOT recheck new charge deadline between barrels
    return True


@dataclass
class LaserDrone:
    actived:bool=False
    time_attack:float=0
    time_charge:float=0
    time_to_active:float=0
    time_to_deactive:float=0


def laser_drone_tick(s,family,*,now,attack,fade=lambda:None,deactivate=lambda:None,is_attack=lambda:True):
    if family not in (7,9):raise ValueError('laser timing fixture only')
    if not is_attack():return 'stopped'
    if s.actived:
        if now()>s.time_to_deactive:
            s.actived=False;s.time_to_active=f32(now()+s.time_charge)
            if family==9:deactivate();return 'deactivated'
            # Family7 still calls AttackLaser ON THE EXPIRING TICK.
        attack();return 'attack'
    if now()>s.time_to_active:
        s.actived=True;s.time_to_deactive=f32(now()+s.time_attack)
        return 'activated'  # no AttackLaser on the activation tick
    if family==9:fade()
    return 'idle'


def drone_base_fixed(s,*,is_attack,now,find):
    if not is_attack():return
    if s['time_to_check']>=now():return
    s['time_to_check']=f32(now()+f32(.5))
    find()


@dataclass
class SweepDrone:
    shooting:bool=False
    phase:int=0
    rotation:float=0
    target_angle:float=0
    count:int=0
    number:int=3
    shot_rate:float=3
    turn_rate:float=0
    shot_deadline:float=0
    turn_deadline:float=0


def move_towards_angle(current,target,step):
    diff=f32(target-current)
    diff=f32(diff+f32(math.floor(f32(diff/f32(360)))*f32(-360)))
    diff=min(max(diff,f32(0)),f32(360))
    if diff>180:diff=f32(diff-f32(360))
    if -step<diff<step:return target
    adjusted=f32(current+diff)
    if abs(f32(adjusted-current))<=step:return adjusted
    return f32(current+(step if adjusted-current>=0 else -step))


def sweep_drone_tick(s,*,now,delta,set_rotation,set_fx):
    if s.turn_deadline>now() or now()<s.shot_deadline:return 'wait'
    if not s.shooting:s.shooting=True;s.phase=0;return 'started'
    s.rotation=move_towards_angle(s.rotation,s.target_angle,f32(f32(delta())*f32(20)))
    set_rotation(s.rotation)
    if s.rotation==s.target_angle:
        if s.phase==0:set_fx(True)
        s.target_angle=f32(-16 if s.phase==0 else 16 if s.phase==1 else 0)
        s.phase+=1
    if s.phase!=4:return 'sweeping'
    s.shooting=False;s.shot_deadline=f32(now()+s.shot_rate);set_fx(False)
    s.count+=1
    if s.count>=s.number:s.count=0;s.turn_deadline=f32(now()+s.turn_rate)
    return 'finished'


def drone_base_damage(source_id,rank,*,get_rank,get_level,base_values,get_ability,ability_amount):
    if rank==-1:rank=get_rank(source_id)
    level=get_level(source_id)
    index=source_id-20001
    if not 0<=index<len(base_values):raise IndexError('native baseDamage array bounds')
    base=f32(f32(f32(f32(level)*f32(.16))+f32(1))*f32(base_values[index]))
    extra=0 if rank==1 else .2 if rank==2 else .35 if rank==3 else .5 if rank==4 else .56
    ranked=f32(base*f32(f32(extra)+f32(1)))
    points=get_ability(21)
    bonus=f32(f32(f32(ability_amount())*f32(points))+f32(1))
    return f32(ranked*bonus)
