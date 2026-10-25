"""Bounded binary32 native-layout arithmetic; affine Transform bridge is a model, not Unity."""
import math,struct
from tools.verify.ui_composition import IDENTITY,sequential_sum

def f32(v):return struct.unpack('<f',struct.pack('<f',v))[0]
def vec(v):
    if len(v)!=3 or not all(math.isfinite(n) for n in v):raise ValueError('finite Vector3 required')
    return [f32(n) for n in v]
def point(matrix,p):
    if len(matrix)!=16 or not all(math.isfinite(n) for n in matrix):raise ValueError('finite affine matrix required')
    return [f32(sequential_sum(matrix[i*4+j]*p[j] for j in range(3))+matrix[i*4+3]) for i in range(3)]
def inverse_point(matrix,p):
    if len(matrix)!=16 or matrix[12:]!=[0,0,0,1] or not all(math.isfinite(n) for n in matrix):raise ValueError('finite affine matrix required')
    rows=[[matrix[i*4+j] for j in range(3)]+[p[i]-matrix[i*4+3]] for i in range(3)]
    for i in range(3):
        pivot=max(range(i,3),key=lambda j:abs(rows[j][i]));rows[i],rows[pivot]=rows[pivot],rows[i]
        if abs(rows[i][i])<1e-12:raise ValueError('singular/ill-conditioned affine bridge not modeled')
        v=rows[i][i];rows[i]=[n/v for n in rows[i]]
        for j in range(3):
            if j!=i:
                v=rows[j][i];rows[j]=[a-v*b for a,b in zip(rows[j],rows[i])]
    return [f32(row[3]) for row in rows]

def safe_bounds(screen_height,rect,main_half_height,cached=(0.,0.)):
    top,bottom=map(f32,cached)
    if top!=0 and bottom!=0:return dict(bounds=[top,bottom],recomputed=False)
    if type(screen_height) is not int or not 0<screen_height<=0x7fffffff:raise ValueError('positive int32 Screen.height required on cache miss')
    if rect is None or len(rect)!=4 or not all(math.isfinite(n) for n in rect):raise ValueError('finite safeArea Rect required on cache miss')
    if main_half_height is None or not math.isfinite(main_half_height) or main_half_height<=0:raise ValueError('positive main-camera half height required on cache miss')
    _,y,_,height=map(f32,rect);h=f32(main_half_height);screen=f32(screen_height);diameter=f32(h+h)
    top=f32(h-f32(f32(f32(screen-f32(y+height))*diameter)/screen))
    bottom=f32(f32(f32(y*diameter)/screen)-h)
    return dict(bounds=[top,bottom],recomputed=True)

def anchor_step(anchor,local,parent,ui_half_height,ui_aspect,fixed,constants,screen_height=None,safe_rect=None,main_half_height=None,state=None,cached_safe=(0.,0.)):
    if type(anchor) is not int or not 0<=anchor<=9:raise ValueError('model accepts declared Anchor enum0..9 only')
    if type(fixed) is not bool:raise ValueError('fixed must be bool')
    if not all(math.isfinite(v) and v>0 for v in (ui_half_height,ui_aspect)):raise ValueError('positive finite camera inputs required')
    local=vec(local);world=point(parent,local);inverse_point(parent,world)
    roots=constants['roots']
    if state is None:state=dict(root=list(roots[str(anchor)]),real=[0.,0.],start=world,cached_z=local[2])
    else:state={k:list(v) if isinstance(v,list) else v for k,v in state.items()}
    height=f32(ui_half_height);aspect=f32(ui_aspect)
    if fixed:height=min(height,constants['clamp']);aspect=max(constants['min_aspect'],min(aspect,.75))
    safe=dict(bounds=list(cached_safe),recomputed=False)
    if 2<=anchor<=7:
        safe=safe_bounds(screen_height,safe_rect,main_half_height,cached_safe);state['real'][1]=safe['bounds'][0 if anchor>=5 else 1]
    if anchor in (3,6,8):state['real'][0]=f32(-f32(height*aspect))
    elif anchor in (4,7,9):state['real'][0]=f32(height*aspect)
    x=f32(state['start'][0]+f32(state['real'][0]-state['root'][0]))
    if anchor in (8,9):
        target=[x,world[1],world[2]];new_local=inverse_point(parent,target);writes=[dict(setter='position',value=target)]
    else:
        target=[x,f32(state['start'][1]+f32(state['real'][1]-state['root'][1])),f32(state['start'][2]+0.)]
        converted=inverse_point(parent,target);new_local=[converted[0],converted[1],f32(state['cached_z'])];writes=[dict(setter='position',value=target),dict(setter='localPosition',value=new_local)]
    return dict(state=state,local=new_local,world=point(parent,new_local),writes=writes,safe=safe)

def scaler_step(size,main_half_height,full,clamp,constants):
    if len(size)!=2 or not all(math.isfinite(v) for v in size) or not math.isfinite(main_half_height) or main_half_height<=0:raise ValueError('finite size and positive main-camera height required')
    h=f32(main_half_height)
    if clamp:h=min(h,constants['clamp'])
    return [f32(size[0]),f32(h+h) if full else f32(f32(h*f32(size[1]))/constants['half_h'])]
