"""One new Board_Pause chain. APK native Align, explicit engine object stubs.
No Unity lifecycle order, readback or render claim.
"""
import copy,gzip,json,struct
from tools.verify.l3_chain_graph import ROOT,RAW,Graph,key,identity,read_chunks
from tools.verify.l3_recipe import Recipes
from tools.verify.l3_composition import merged_source
from tools.verify.l3_frame import Frame
from tools.verify.l3_layout_math import f32,inverse_point
from tools.verify.ui_composition import IDENTITY
F='data.unity3d/resources.assets'
def ident(p):return identity((F,p))
def source():
    recipe=Recipes().recipe(10);wanted={key(n['gameobject']) for n in recipe['nodes']}
    wanted.update(key(c['identity']) for n in recipe['nodes'] for c in n['component_identities'])
    g=merged_source()[0];rows=dict(g.rows);index=json.loads((RAW/'index.json').read_bytes())
    for r in read_chunks(index,'objects'):
        k=key(r)
        if k in wanted or k in {key(m['identity']) for m in recipe['motion']}:
            if k in rows:assert rows[k]['raw_object_sha256']==r['raw_object_sha256']
            else:rows[k]=r
    edges={(owner,loc):dict(owner=identity(owner),location=loc,status='resolved',target=dict(**identity(t),type=typ)) for owner,rr in g.refs.items() for loc,t,typ in rr}
    for l in read_chunks(index,'links'):
        if key(l['owner']) in wanted and l['status']=='resolved':
            ek=(key(l['owner']),l['location'])
            if ek in edges:assert key(edges[ek]['target'])==key(l['target'])
            edges[ek]=l
    for r in json.loads((ROOT/'reverse-engineering/raw/l3-textured105/objects.json').read_bytes()):
        k=key(r);assert rows[k]['raw_object_sha256']==r['raw_object_sha256'];rows[k]=r
        ptr=r['tree']['m_GameObject'];assert ptr['m_FileID']==0
        edges[k,'.m_GameObject']=dict(owner=identity(k),location='.m_GameObject',status='resolved',target=dict(serialized_file=F,path_id=ptr['m_PathID'],type='GameObject'))
    return Graph(list(rows.values()),list(edges.values())),recipe

def frame(g,recipe):
    f=Frame(1080,2400,identity(('data.unity3d/level2',3976)),g)
    # Source-attached 98 bindings, normalized to the 102 sampler shape. No invented curve.
    f.surface=dict(f.surface,sections=dict(f.surface['sections']));s=f.surface['sections'];s['animators']=s['animators']+[dict(identity=a['animator'],**{k:v for k,v in a.items() if k!='animator'}) for a in recipe['animators'] if key(a['animator']) not in {key(a['identity']) for a in s['animators']}]
    known={key(m['identity']) for m in s['motion']};s['motion']=s['motion']+[m for m in recipe['motion'] if key(m['identity']) not in known]
    known={(key(b['animator']),key(b['clip']),b['binding_index']) for b in s['bindings']}
    s['bindings']=s['bindings']+[dict(**{k:v for k,v in b.items() if k not in ('component_targets','property_crc32_candidates')},targets=b['component_targets'],property_candidates=b['property_crc32_candidates']) for b in recipe['animation_bindings'] if (key(b['animator']),key(b['clip']),b['binding_index']) not in known]
    return f

def align(f,safe_rect):
    """Run full source Board_Pause.Align body; nested anchor calls use 101 harness.
    Engine hooks read/write SAME Frame current overlays, with explicit affine bridge.
    """
    import unicorn as u
    from unicorn import arm64_const as a
    uc=u.Uc(u.UC_ARCH_ARM64,u.UC_MODE_ARM);mapped=set();trace=[];last=[None]
    def put(p,b):
        for page in range(p&~4095,(p+len(b)+4095)&~4095,4096):
            if page not in mapped:uc.mem_map(page,4096);mapped.add(page)
        uc.mem_write(p,b)
    def reg(i):return getattr(a,'UC_ARM64_REG_S'+str(i))
    def rf(i):return struct.unpack('<f',struct.pack('<I',uc.reg_read(reg(i))))[0]
    def wf(i,v):uc.reg_write(reg(i),struct.unpack('<I',struct.pack('<f',f32(v)))[0])
    raw=json.load(gzip.open(ROOT/'reverse-engineering/raw/l3-ui-native/method-bytes.json.gz'));m=next(m for m in raw['methods'] if m['cls']=='Board_Pause' and m['method']=='Align');entry=int(m['va'],16);put(entry,bytes.fromhex(m['hex']))
    evidence=json.loads((ROOT/'reverse-engineering/raw/l3-textured105/texture.json').read_bytes());cell=evidence['align_literal'];assert cell['va']=='0x756dd8';put(int(cell['va'],16),bytes.fromhex(cell['hex']))
    this=0x8000000;stop=0x1000000;put(this,b'\0'*0x2000);put(stop,bytes.fromhex('1f2003d5'));put(0x9000000,b'\0'*0x10000)
    props=f.g.tree((F,690342));addresses={};objects={}
    for n,(name,offset) in enumerate([('pointTopAnchors',0x150),('pointBotAnchors',0x158),('boxBound',0x160),('boxContent',0x168),('parentView',0x170)]):
        k=f.g.target((F,690342),'.'+name);assert k is not None;addr=this+0x1000+n*0x100;addresses[addr]=k;objects[k]=addr;put(this+offset,struct.pack('<Q',addr))
    # Other transforms returned by engine get_transform/parent are synthetic handles.
    def addr(k):
        if k not in objects:
            v=this+0x2000+len(objects)*0x100;objects[k]=v;addresses[v]=k
        return objects[k]
    hooks={0x15b6ae0:'ObjectAnchor',0x277f14c:'get_transform',0x27890c4:'get_parent',0x27891b8:'get_position',0x2789258:'set_position',0x27c5a90:'get_size',0x27c5b20:'set_size',0x27c5838:'get_offset',0x27c58c8:'set_offset',0x110d250:'null_trap'}
    for pc in hooks:put(pc,bytes.fromhex('c0035fd6'))
    def hook(uc,pc,sz,_):
        if entry<=pc<entry+m['width']:last[0]=pc
        if pc not in hooks:return
        name=hooks[pc]
        if name=='null_trap':raise ValueError('native null-reference trap')
        k=addresses[uc.reg_read(a.UC_ARM64_REG_X0)];row=dict(pc=hex(pc),callsite=hex(last[0]),operation=name,owner=identity(k));trace.append(row)
        if name=='ObjectAnchor':f.anchor(identity(k),safe_rect)
        elif name=='get_transform':uc.reg_write(a.UC_ARM64_REG_X0,addr(k if f.g.rows[k]['type'] in ('Transform','RectTransform') else f.g.go_transform[f.g.target(k,'.m_GameObject')]))
        elif name=='get_parent':uc.reg_write(a.UC_ARM64_REG_X0,addr(f.g.target(k,'.m_Father')))
        elif name=='get_position':
            mat=f.matrix(k)
            for i in range(3):wf(i,mat[i*4+3])
        elif name in ('get_size','get_offset'):
            path='m_Size' if name=='get_size' else 'm_Offset';v=f.view.tree(k)[path]
            for i,c in enumerate('xy'):wf(i,v[c])
        else:
            pending={}
            if name=='set_position':
                value=[rf(i) for i in range(3)];row['world_value']=value;parent=f.g.target(k,'.m_Father');local=inverse_point(f.matrix(parent) if parent else IDENTITY,value)
                for c,v in zip('xyz',local):f._set(k,'m_LocalPosition.'+c,v,pending)
            else:
                value=[rf(0),rf(1)];row['value']=value;path='m_Size' if name=='set_size' else 'm_Offset'
                for c,v in zip('xy',value):f._set(k,path+'.'+c,v,pending)
            f.trees.update(pending)
    uc.hook_add(u.UC_HOOK_CODE,hook);uc.reg_write(a.UC_ARM64_REG_SP,0x900f000);uc.reg_write(a.UC_ARM64_REG_LR,stop);uc.reg_write(a.UC_ARM64_REG_X0,this);uc.emu_start(entry,stop,count=20000)
    if uc.reg_read(a.UC_ARM64_REG_PC)!=stop:raise ValueError('bounded Align failed to return')
    result=dict(entry=m['va'],trace=trace,scope='Actual pinned Align instructions; synthetic object handles, engine/Transform bridges, nested 101 anchor harness; NOT Unity runtime')
    f.log.append(dict(kind='native_Board_Pause_Align',result=result));return result

def snapshot(f):
    result={}
    for p in [597593,616420,493280,492598,267691,549984,563997]:
        k=(F,p);t=f.view.tree(k);result[str(p)]={'type':f.g.rows[k]['type']}
        for field in ['m_Size','m_Offset','m_Color']:
            if field in t:result[str(p)][field]=copy.deepcopy(t[field])
        tr=k if f.g.rows[k]['type'] in ('Transform','RectTransform') else f.g.go_transform.get(f.g.target(k,'.m_GameObject'))
        if tr:result[str(p)]['world_matrix']=f.matrix(tr)
    return result

def scenario(g=None,recipe=None):
    if g is None:g,recipe=source()
    f=frame(g,recipe);before=snapshot(f);f.resize_camera(identity(('data.unity3d/level2',3976)))
    starts=[]
    for p in [597593,616420]:starts.append(f.anchor(ident(p),[0,96,1080,2208],start=True))
    after_start=snapshot(f);native=align(f,[0,96,1080,2208]);after_align=snapshot(f)
    f.clip(ident(498199),ident(1495),.25);after_clip=snapshot(f)
    other=frame(g,recipe);other.resize_camera(identity(('data.unity3d/level2',3976)))
    for p in [597593,616420]:other.anchor(ident(p),[0,96,1080,2208],start=True)
    other.clip(ident(498199),ident(1495),.25);align(other,[0,96,1080,2208]);reordered=snapshot(other)
    assert reordered==after_clip
    return dict(reordered_clip_before_align=reordered,disjoint_write_commutation=True,before=before,after_start=after_start,after_align=after_align,after_clip=after_clip,starts=starts,native=native,log=f.log,order_scope='Start invocations and clip-local time are caller-selected. Only internal Align top→bottom→collider→parent writes proved by executed instructions; no cross-component Unity scheduler order claim')
