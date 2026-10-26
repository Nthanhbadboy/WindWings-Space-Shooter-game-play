"""Explicit float64 affine/orthographic triangle model, not Unity numerical fidelity."""
import math
from tools.verify.ui_composition import sequential_sum

def point(m,p):
    if len(m)!=16 or list(m[12:])!=[0,0,0,1] or not all(math.isfinite(v) for v in m) or len(p)!=3 or not all(math.isfinite(v) for v in p):raise ValueError('finite affine matrix/point required')
    out=[sequential_sum(m[i*4+j]*p[j] for j in range(3))+m[i*4+3] for i in range(3)]
    if not all(math.isfinite(v) for v in out):raise ValueError('nonfinite modeled point')
    return out

def inverse(m):
    point(m,[0,0,0]);rows=[list(m[i*4:i*4+4])+[float(i==j) for j in range(4)] for i in range(4)]
    for i in range(4):
        pivot=max(range(i,4),key=lambda j:abs(rows[j][i]));rows[i],rows[pivot]=rows[pivot],rows[i]
        if abs(rows[i][i])<1e-12:raise ValueError('singular/ill-conditioned matrix not modeled')
        scale=rows[i][i];rows[i]=[v/scale for v in rows[i]]
        for j in range(4):
            if j!=i:
                scale=rows[j][i];rows[j]=[a-scale*b for a,b in zip(rows[j],rows[i])]
    return [v for row in rows for v in row[4:]]

def layer_gate(mask,layer):
    if isinstance(layer,bool) or not isinstance(layer,int) or not 0<=layer<32:raise ValueError('layer index must be0..31')
    if not isinstance(mask,int) or isinstance(mask,bool):raise ValueError('integer layer mask required')
    return bool((mask&0xffffffff)&(1<<layer))

def viewport_parameters(camera,width,height,half_height=None):
    t=camera['properties'];m=camera['serialized_world_matrix'];point(m,[0,0,0])
    if not t['orthographic']:raise ValueError('perspective outside this orthographic model')
    # Camera scale/shear must not be accidentally treated as a projection zoom.
    for i in range(3):
        for j in range(3):
            dot=sequential_sum(m[k*4+i]*m[k*4+j] for k in range(3))
            if abs(dot-float(i==j))>1e-5:raise ValueError('non-rigid camera matrix not modeled')
    det=m[0]*(m[5]*m[10]-m[6]*m[9])-m[1]*(m[4]*m[10]-m[6]*m[8])+m[2]*(m[4]*m[9]-m[5]*m[8])
    if abs(det-1.)>1e-5:raise ValueError('reflected camera basis not modeled')
    r=t['m_NormalizedViewPortRect'];h=t['orthographic size'] if half_height is None else half_height;near=t['near clip plane'];far=t['far clip plane']
    vals=[width,height,h,near,far]+[r[k] for k in ('x','y','width','height')]
    if not all(isinstance(v,(int,float)) and math.isfinite(v) for v in vals) or min(width,height,h,r['width'],r['height'])<=0 or near<0 or far<=near:raise ValueError('invalid finite viewport/camera parameters')
    hw=h*(width*r['width'])/(height*r['height']);rect=[width*r['x'],height*r['y'],width*r['width'],height*r['height']]
    if not all(math.isfinite(v) for v in [hw]+rect) or hw<=0:raise ValueError('overflow/underflow in viewport model')
    return dict(view=inverse(m),half_height=h,half_width=hw,near=near,far=far,pixel_rect=rect,scope='Conventional mono orthographic projection, camera local +Z forward; custom matrices/XR/render targets not simulated')

def clip_polygon(vertices,half_width,half_height,near,far):
    if not all(len(v)==3 and all(math.isfinite(n) for n in v) for v in vertices):raise ValueError('finite triangle/polygon required')
    planes=[(0,1,half_width),(0,-1,half_width),(1,1,half_height),(1,-1,half_height),(2,1,-near),(2,-1,far)]
    out=[list(v) for v in vertices]
    for axis,sign,offset in planes:
        source=out;out=[]
        if not source:break
        for a,b in zip(source,source[1:]+source[:1]):
            da=sign*a[axis]+offset;db=sign*b[axis]+offset;ia=da>=0;ib=db>=0
            if ia:out.append(a)
            if ia!=ib:
                t=da/(da-db);out.append([a[i]+t*(b[i]-a[i]) for i in range(3)])
    return out

def project_geometry(vertices,triangles,world,camera,width,height,half_height=None):
    p=viewport_parameters(camera,width,height,half_height);camera_vertices=[point(p['view'],point(world,v)) for v in vertices];polygons=[]
    for tri in triangles:
        if len(tri)!=3 or any(not isinstance(i,int) or not 0<=i<len(vertices) for i in tri):raise ValueError('valid triangle indices required')
        clipped=clip_polygon([camera_vertices[i] for i in tri],p['half_width'],p['half_height'],p['near'],p['far'])
        if len(clipped)<3:continue
        x,y,w,h=p['pixel_rect'];pixels=[[x+(v[0]/p['half_width']+1)*w*.5,y+(v[1]/p['half_height']+1)*h*.5] for v in clipped]
        area=abs(sequential_sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(pixels,pixels[1:]+pixels[:1])))*.5
        if area>1e-10:polygons.append(dict(camera=clipped,pixels=pixels))
    pixels=[v for poly in polygons for v in poly['pixels']]
    return dict(parameters={k:v for k,v in p.items() if k!='view'},camera_vertices=camera_vertices,clipped_polygons=polygons,intersects=bool(polygons),pixel_bounds=[min(v[0] for v in pixels),min(v[1] for v in pixels),max(v[0] for v in pixels),max(v[1] for v in pixels)] if pixels else None,scope='Triangle/box clipping and pixel footprint only, NOT renderer bounds culling, occlusion, alpha/stencil/shader rasterization or visibility')

def sprite_geometry(renderer,geometry,size=None):
    t=renderer['properties'];mode=t.get('m_DrawMode');g=geometry['geometry'];s=geometry['sprite_properties']
    if mode==0:vertices=[list(v) for v in g['m_Vertices']];triangles=[list(f) for group in g['triangles'] for f in group];kind='decoded_simple_sprite'
    elif mode==1 and all(v==0 for v in s['m_Border'].values()):
        size=[t['m_Size']['x'],t['m_Size']['y']] if size is None else size
        if len(size)!=2 or not all(math.isfinite(v) and v>0 for v in size):raise ValueError('positive finite sliced size required')
        w,h=size;p=s['m_Pivot'];x=-p['x']*w;y=-p['y']*h;vertices=[[x,y,0],[x+w,y,0],[x+w,y+h,0],[x,y+h,0]];triangles=[[0,1,2],[0,2,3]];kind='modeled_zero_border_sliced_rectangle'
    else:return dict(status='not_generated',reason='draw mode/border outside this bounded generator',vertices=None,triangles=None)
    for v in vertices:
        if t.get('m_FlipX'):v[0]=-v[0]
        if t.get('m_FlipY'):v[1]=-v[1]
    return dict(status=kind,vertices=vertices,triangles=triangles,scope='Position geometry only; no UV regeneration/live atlas override or Unity engine geometry execution')
