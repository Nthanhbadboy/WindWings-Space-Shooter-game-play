"""APK finite emission boundary models, not observed hits or Unity schedules."""
import math
from tools.verify.enemy_damage_model import f32

def div(a,b):
    if b==0:
        return math.nan if a==0 else math.copysign(math.inf,a)
    return f32(a/b)

def basic(number,id_bullet,*,get_position,spacing,delta,start_y,directions,demo,layer_bullet,emit):
    if id_bullet==-1:return
    dx,dy=map(f32,spacing);delta=f32(delta);start_y=f32(start_y)
    hx=f32(dx*f32(.5)) if number%2==0 else 0.
    ha=f32(delta*f32(.5)) if number%2==0 else 0.
    first=0
    def z():return f32(get_position()[2]+f32(.1)) if demo else f32(layer_bullet)
    if number%2!=0 or hx==0:
        x=get_position()[0];y=f32(start_y+get_position()[1]);zz=z()
        emit(dict(position=[x,y,zz],angle=0.));first=1
    if number<2:return
    for j in range(first,first+math.trunc(number/2)):
        for k in range(2):
            if directions is None:raise ValueError('null directions')
            if k>=len(directions):raise IndexError('directions bounds')
            d=directions[k];px=get_position()[0];py=get_position()[1];zz=z()
            # Actual instruction grouping, not algebraic simplification/FMA.
            xx=f32(f32(f32(hx*f32(d))+f32(dx*f32(d*j)))+px)
            yy=f32(f32(start_y+f32(dy*f32(j)))+py)
            angle=f32(f32(ha*f32(d))+f32(delta*f32(d*j)))
            emit(dict(position=[xx,yy,zz],angle=angle))

def circle(number,*,get_position,arc,start_angle,emit):
    if number<1:return
    step=div(f32(arc),f32(number))
    for i in range(number):
        # Native makes earlier redundant position calls, then reads a fresh vector
        # immediately before invoking the terminal helper.
        emit(dict(position=list(get_position()),angle=f32(f32(step*f32(i))+f32(start_angle))))

class Iterator23:
    def __init__(self):self.state=0;self.index=0
    def step(self,*,child_count,get_rate,emit,wait):
        if self.state not in (0,1):return False
        if self.state==0:self.index=0
        else:self.index+=1
        self.state=-1
        if self.index>=child_count():return False
        emit(self.index)
        rate=get_rate()  # before the second, live childCount read
        duration=div(f32(rate),f32(child_count()))
        wait(duration);self.state=1;return True

class Iterator13:
    def __init__(self):self.state=0;self.index=0;self.interval=None
    def step(self,*,number,get_rate,emit_pair,wait):
        if self.state not in (0,1):return False
        if self.state==0:self.index=0;self.interval=min(div(f32(get_rate()),f32(number)),f32(.05))
        else:self.index+=1
        self.state=-1
        if self.index>=number:return False
        emit_pair(self.index);wait(self.interval);self.state=1;return True
