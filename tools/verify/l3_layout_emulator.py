"""Execute bounded APK AArch64 layout bodies with explicit engine/metadata stubs.
This checks native arithmetic/control flow, NOT IL2CPP initialization or Unity transforms/render.
"""
import gzip,json,struct
from collections import Counter
from tools.verify.l3_chain_graph import ROOT
from tools.verify.l3_layout_math import f32,point,inverse_point

def execute(entry,constants,local,parent,anchor=0,fixed=False,ui_half_height=9.6,ui_aspect=.5625,main_half_height=9.6,screen_height=1920,safe_rect=(0,0,1080,1920),cached_safe=(0.,0.),state=None,size=(3.,4.),full=True,clamp=True,clamp_value=None,play_on_start=True,ui_camera_null=False):
    import unicorn as u
    from unicorn import arm64_const as a
    uc=u.Uc(u.UC_ARCH_ARM64,u.UC_MODE_ARM);mapped=set()
    def ensure(address,size):
        for page in range(address&~4095,(address+size+4095)&~4095,4096):
            if page not in mapped:uc.mem_map(page,4096);mapped.add(page)
    def write(addr,data):ensure(addr,len(data));uc.mem_write(addr,data)
    def q(addr,value):write(addr,struct.pack('<Q',value))
    def fl(addr,value):write(addr,struct.pack('<f',f32(value)))
    def fs(addr,count):return list(struct.unpack('<'+'f'*count,uc.mem_read(addr,count*4)))
    def putvec(addr,values):write(addr,struct.pack('<'+'f'*len(values),*[f32(v) for v in values]))
    def sr(i):return getattr(a,'UC_ARM64_REG_S'+str(i))
    def getf(i):return struct.unpack('<f',struct.pack('<I',uc.reg_read(sr(i))))[0]
    def setf(i,value):uc.reg_write(sr(i),struct.unpack('<I',struct.pack('<f',f32(value)))[0])
    methods={};relocations={}
    for directory,selected in [('l3-ui-native',{'UIObjectAnchors'}),('l3-layout-native',{'SafeArea','ObjectScaler'})]:
        raw=json.load(gzip.open(ROOT/f'reverse-engineering/raw/{directory}/method-bytes.json.gz'))
        relocations.update({int(r['offset'],16):int(r['addend'],16) for r in raw['relocations']})
        for m in raw['methods']:
            if m['cls'] in selected:
                write(int(m['va'],16),bytes.fromhex(m['hex']));methods[(m['cls'],m['method'])]=int(m['va'],16)
    cells=json.loads((ROOT/'reverse-engineering/raw/l3-layout-native/anchor-cells.json').read_bytes())
    for c in cells['cells']:write(int(c['va'],16),bytes.fromhex(c['hex']))
    THIS=0x8000000;UI=THIS+0x1000;MAIN=THIS+0x2000;TR=THIS+0x3000;OSCLASS=THIS+0x4000;OSSTATIC=THIS+0x5000;SACLASS=THIS+0x6000;SASTATIC=THIS+0x7000;OBJECTCLASS=THIS+0x8000;SPRITE=THIS+0x9000
    ensure(THIS,0xa000);ensure(0x2ce1000,8192);ensure(0x9000000,65536);STOP=0x1000000;write(STOP,bytes.fromhex('1f2003d5'))
    for got,cl,st in [(0x2ae6148,OSCLASS,OSSTATIC),(0x2ae6158,SACLASS,SASTATIC),(0x2adb220,OBJECTCLASS,THIS+0xa000)]:
        slot=relocations[got];q(got,slot);q(slot,cl);q(cl+0xb8,st);write(cl+0xe0,struct.pack('<I',1))
    fl(OSSTATIC,constants['clamp'] if clamp_value is None else clamp_value);putvec(SASTATIC,cached_safe)
    pose=dict(local=[f32(v) for v in local]);pose['world']=point(parent,pose['local']);sprite_size=[f32(v) for v in size];writes=[];calls=Counter()
    q(THIS+0x20,SPRITE if entry[0]=='ObjectScaler' else (0 if ui_camera_null else UI))
    if entry[0]=='ObjectScaler':write(THIS+0x28,bytes([int(full),int(clamp)]))
    else:
        write(THIS+0x4c,bytes([int(play_on_start)]));write(THIS+0x28,struct.pack('<I',anchor));write(THIS+0x4e,bytes([int(fixed)]))
        if state:
            write(THIS+0x4d,b'\x01');putvec(THIS+0x2c,state['root']);putvec(THIS+0x34,state['real']);putvec(THIS+0x3c,state['start']);fl(THIS+0x48,state['cached_z'])
    hooks={0x110d028:'metadata_init_stub',0x110d12c:'class_init_stub',0x110d250:'null_trap',0x277f14c:'get_transform',0x27891b8:'get_position',0x27892f0:'get_localPosition',0x2789258:'set_position',0x2789390:'set_localPosition',0x27849c8:'op_Implicit',0x275e868:'get_main',0x275e174:'get_orthographicSize',0x275e238:'get_aspect',0x27665e4:'get_height',0x27666dc:'get_safeArea',0x278ada4:'get_size',0x278ae34:'set_size',0x2782ba0:'mono_ctor_stub'}
    for pc in hooks:write(pc,bytes.fromhex('c0035fd6'))
    def hook(uc,pc,size,_):
        name=hooks.get(pc)
        if not name:return
        calls[name]+=1
        if name=='null_trap':raise ValueError('native null-reference trap reached')
        if name=='get_transform':uc.reg_write(a.UC_ARM64_REG_X0,TR)
        elif name=='get_main':uc.reg_write(a.UC_ARM64_REG_X0,MAIN)
        elif name=='op_Implicit':uc.reg_write(a.UC_ARM64_REG_X0,int(uc.reg_read(a.UC_ARM64_REG_X0)!=0))
        elif name=='get_orthographicSize':setf(0,ui_half_height if uc.reg_read(a.UC_ARM64_REG_X0)==UI else main_half_height)
        elif name=='get_aspect':setf(0,ui_aspect)
        elif name=='get_height':uc.reg_write(a.UC_ARM64_REG_X0,screen_height)
        elif name in ('get_position','get_localPosition'):
            for i,v in enumerate(pose['world' if name=='get_position' else 'local']):setf(i,v)
        elif name in ('set_position','set_localPosition'):
            value=[getf(i) for i in range(3)];writes.append(dict(setter=name[4:],value=value))
            pose['local']=inverse_point(parent,value) if name=='set_position' else value;pose['world']=point(parent,pose['local'])
        elif name=='get_safeArea':
            for i,v in enumerate(safe_rect):setf(i,v)
        elif name=='get_size':setf(0,sprite_size[0]);setf(1,sprite_size[1])
        elif name=='set_size':sprite_size[:]=[getf(0),getf(1)];writes.append(dict(setter='size',value=list(sprite_size)))
        uc.reg_write(a.UC_ARM64_REG_PC,uc.reg_read(a.UC_ARM64_REG_LR))
    uc.hook_add(u.UC_HOOK_CODE,hook);uc.reg_write(a.UC_ARM64_REG_SP,0x900f000);uc.reg_write(a.UC_ARM64_REG_X0,THIS);uc.reg_write(a.UC_ARM64_REG_LR,STOP)
    uc.emu_start(methods[entry],STOP,count=20000)
    if uc.reg_read(a.UC_ARM64_REG_PC)!=STOP:raise ValueError('native execution did not return within instruction budget')
    state_out=dict(root=fs(THIS+0x2c,2),real=fs(THIS+0x34,2),start=fs(THIS+0x3c,3),cached_z=fs(THIS+0x48,1)[0])
    return dict(bound_ui_camera='main' if struct.unpack('<Q',uc.mem_read(THIS+0x20,8))[0]==MAIN else ('null' if struct.unpack('<Q',uc.mem_read(THIS+0x20,8))[0]==0 else 'explicit_stub'),state=state_out,world=pose['world'],local=pose['local'],size=sprite_size,writes=writes,safe=fs(SASTATIC,2),clamp=fs(OSSTATIC,1)[0],engine_stub_calls=dict(calls),scope='Bounded native instructions executed; engine, transform bridge and type metadata are stubs, NOT Unity.')
