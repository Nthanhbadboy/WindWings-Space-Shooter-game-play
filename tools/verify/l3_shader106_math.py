"""Bounded CPU references for decoded Sprites/Default GLSL.
Explicit sequential binary64, mip0/raw-UNORM, clamp-to-edge. NOT GPU fidelity/render.
"""
import math
from tools.verify.ui_composition import sequential_sum

def vector(values,n):
    if len(values)!=n or any(type(v) not in (float,int) or not math.isfinite(v) for v in values):raise ValueError('finite numeric vector required')
    return [float(v) for v in values]
def dimensions(size):
    if len(size)!=2 or any(type(v) is not int or not 0<v<=2**20 for v in size):raise ValueError('bounded positive integer dimensions required')
    return size

def round_even(value):
    if type(value) not in (float,int) or not math.isfinite(value) or abs(value)>2**24:raise ValueError('finite bounded snap coordinate required')
    # Exact scalar unity_roundEven source in GLES100. GLSL300 roundEven uses the
    # same mathematical tie policy; neither path emulates GPU lowp/mediump.
    y=math.floor(value+.5)
    return float(math.floor(.5*y)*2 if y-value==.5 else y)

def columns(matrix):
    m=vector(matrix,16);return [[m[r*4+c] for r in range(4)] for c in range(4)]
def vertex(position,uv,vertex_color,material_color,renderer_color,flip,object_to_world,matrix_vp,screen,pixel_snap=False):
    p=vector(position,4);uv=vector(uv,2);flip=vector(flip,2);screen=dimensions(screen)
    if p[3]!=1:raise ValueError('source program uses implicit object position w1')
    if type(pixel_snap) is not bool:raise ValueError('explicit bool variant choice required')
    if object_to_world[12:]!=[0,0,0,1]:raise ValueError('affine object matrix required')
    o=columns(object_to_world);vp=columns(matrix_vp);x,y=p[0]*flip[0],p[1]*flip[1]
    # Preserve the staged multiply/add order of the recovered shader, not generic sum.
    u1=[y*o[1][i] for i in range(4)]
    u0=[o[0][i]*x+u1[i] for i in range(4)]
    u0=[o[2][i]*p[2]+u0[i] for i in range(4)]
    world=[u0[i]+o[3][i] for i in range(4)]
    u1=[world[1]*vp[1][i] for i in range(4)]
    u1=[vp[0][i]*world[0]+u1[i] for i in range(4)]
    u1=[vp[2][i]*world[2]+u1[i] for i in range(4)]
    original=[vp[3][i]*world[3]+u1[i] for i in range(4)];vector(original,4)
    if abs(original[3])<1e-12:raise ValueError('clip w near zero outside bounded CPU model')
    clip=list(original);snap=None
    if pixel_snap:
        half=[n*.5 for n in screen];projected=[original[i]/original[3] for i in range(2)];scaled=[projected[i]*half[i] for i in range(2)];rounded=[round_even(v) for v in scaled];clip[:2]=[original[3]*(rounded[i]/half[i]) for i in range(2)];snap=dict(ndc_before=projected,scaled=scaled,rounded=rounded)
    colors=[vector(c,4) for c in (vertex_color,material_color,renderer_color)]
    varying=[(colors[0][i]*colors[1][i])*colors[2][i] for i in range(4)];window=[(clip[i]/clip[3]+1)*screen[i]*.5 for i in range(2)]
    return dict(world=world,clip_before_snap=original,clip=clip,window=window,uv=uv,varying_color=varying,snap=snap)

def interpolate(vertices,barycentric):
    if len(vertices)!=3:raise ValueError('three source shader vertices required')
    b=vector(barycentric,3)
    if min(b)<-1e-10 or abs(sequential_sum(b)-1)>1e-9:raise ValueError('inside-triangle screen barycentrics required; no implicit coverage')
    ws=[v['clip'][3] for v in vertices]
    if any(not math.isfinite(w) or w<=1e-12 for w in ws):raise ValueError('positive finite post-clip vertex w required')
    unscaled=[b[i]/ws[i] for i in range(3)];total=sequential_sum(unscaled)
    if abs(total)<1e-12:raise ValueError('undefined varying denominator')
    p=[v/total for v in unscaled]
    def field(name,n):
        values=[vector(v[name],n) for v in vertices];return [sequential_sum(p[j]*values[j][i] for j in range(3)) for i in range(n)]
    return dict(perspective_weights=p,uv=field('uv',2),varying_color=field('varying_color',4))

def footprint(uv,size):
    uv=vector(uv,2);w,h=dimensions(size)
    if any(not -1<=v<=2 for v in uv):raise ValueError('bounded normalized UV range [-1,2] required')
    pixel=[uv[0]*w-.5,uv[1]*h-.5];base=[math.floor(v) for v in pixel];frac=[pixel[i]-base[i] for i in range(2)];taps=[]
    for dx,dy in ((0,0),(1,0),(0,1),(1,1)):
        x,y=base[0]+dx,base[1]+dy;weight=(frac[0] if dx else 1-frac[0])*(frac[1] if dy else 1-frac[1]);taps.append(dict(unclamped=[x,y],xy=[min(w-1,max(0,x)),min(h-1,max(0,y))],weight=weight))
    return dict(texel_coordinate=pixel,base=base,fraction=frac,taps=taps)

def bilinear(uv,size,pixels,wrap_u=1,wrap_v=1):
    if (wrap_u,wrap_v)!=(1,1):raise ValueError('only source Clamp1 on BOTH axes; no guessed wrap')
    f=footprint(uv,size);values=[]
    for tap in f['taps']:
        xy=tuple(tap['xy'])
        if xy not in pixels:raise ValueError('missing decoded pixel evidence, not transparent black')
        rgba=pixels[xy]
        if len(rgba)!=4 or any(type(v) is not int or not 0<=v<=255 for v in rgba):raise ValueError('actual RGBA8 texel required')
        values.append([v/255 for v in rgba])
    f['rgba']=[sequential_sum(f['taps'][j]['weight']*values[j][i] for j in range(4)) for i in range(4)];return f

def fragment(sample,varying_color,external_alpha=None,enable_external_alpha=0.):
    t=vector(sample,4);c=vector(varying_color,4)
    if any(not 0<=v<=1 for v in t+c):raise ValueError('bounded normalized fragment inputs required')
    if type(enable_external_alpha) not in (float,int) or not math.isfinite(enable_external_alpha) or not 0<=enable_external_alpha<=1:raise ValueError('finite external-alpha weight0..1 required')
    if external_alpha is not None:
        if not math.isfinite(external_alpha) or not 0<=external_alpha<=1:raise ValueError('normalized external-alpha sample required')
        t[3]=enable_external_alpha*(external_alpha-t[3])+t[3]
    elif enable_external_alpha:raise ValueError('external-alpha texture sample missing')
    product=[t[i]*c[i] for i in range(4)];return [product[i]*product[3] for i in range(3)]+[product[3]]
