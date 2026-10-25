"""Normal SetBarrels configuration, explicit input fields (not prefab defaults).
Floating instructions are separate f32 operations; no fused multiply-add.
"""
import math
from tools.verify.enemy_damage_model import f32
# delta rate, delta speed, speed cap, optional rate floor, spread (step,base,cap)
CONFIG={1:(-.0035,1.1,42,None,(3,5,15)),3:(-.001,1.15,38,None,None),5:(-.00689,.5,45,None,(3,5,15)),7:(0,0,45,None,(3,5,15)),9:(-.0035,.4,45,None,(3,5,15)),11:(-.005,1.5,42,None,(2,3,6)),13:(-.003,.5,42,None,None),14:(-.005,.1,42,.036,(2,3,6)),16:(-.01,.2,42,.06,(6,30,60)),17:(0,0,42,None,(2,3,6)),18:(-.001,1.15,38,None,None),19:(-.03,None,None,.02,None),20:(-.0035,1.1,42,None,(1,1,5)),21:(-.005,.1,42,.2,None),22:(-.005,1.5,42,None,(2,3,6)),23:(-.005,1.5,42,None,(2,3,6)),24:(-.005,1.5,42,None,None)}
COMPRESSED={1,3,11,16,17,18,20,22,23,24}

def count_index(i,first,second,length):
    if i in COMPRESSED:
        n=second-2
        idx=(0 if n < -5 else min(math.trunc(n/2)+2,length-1)) if first>2 else (0 if second<0 else min(second,length-1))
    elif i in (13,21):idx=min(max(first,0),length-1)
    else:idx=max(first-1,0)
    if idx<0 or idx>=length:raise IndexError('native array/list bounds')
    return idx

def configure(i,*,level,start_rate,start_speed):
    dr,ds,cap,floor,spread=CONFIG[i]
    rate=f32(f32(start_rate)+f32(f32(level)*f32(dr)))
    if floor is not None:rate=max(rate,f32(floor))
    out={'shotRate':rate}
    if ds is not None:out['btlSpeed']=min(f32(f32(start_speed)+f32(f32(level)*f32(ds))),f32(cap))
    if spread:
        step,base,limit=spread
        out['angleDelta']=min(f32(f32(f32(math.trunc(level/10))*f32(step))+f32(base)),f32(limit))
    return out
