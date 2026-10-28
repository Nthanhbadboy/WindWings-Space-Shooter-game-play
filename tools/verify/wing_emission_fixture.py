"""Execute original Shoot/iterator/geometry bytes. SDK boundaries are explicit.

Basic/circle terminal helpers are OBSERVATION boundaries, not pooled-hit simulators.
13 iterator supports both missing-IBullet and present-IBullet SDK adapters;
SetBullet arguments are observed, not projectile physics or collision delivery.
"""
import gzip,json,struct
from unicorn.arm64_const import *
from tools.verify.wing_native_fixture import SetBarrelsFixture,ROOT,RAW,SELF,PLAYER,STOP,NativeFault
PARENT=0x1003000;POINT=0x1003400;STATIC=0x1003800;DIRECTS=0x1003900;POOLED=0x1005000

class EmissionFixture(SetBarrelsFixture):
    def __init__(self,i):
        self.i=i;rows=json.loads((ROOT/'datas/wing_implementations.json').read_bytes())['implementations'];super().__init__(f'Player_Attack_{i}',rows[i-1]['fields'])
        self.payload=json.load(gzip.open(RAW));self.members=[m for m in self.payload['methods'] if m['cls'].split('.')[0]==f'Player_Attack_{i}']
        for m in self.members:self.vm.mem_write(int(m['va'],16),bytes.fromhex(m['hex']))
        for a,n in ((0x2770000,0x20000),(0x2140000,0x10000),(0x19a9000,0x1000),(0x15b5000,0x1000),(0x171d000,0x1000)):self.vm.mem_map(a,n)
        for x in json.loads((ROOT/'reverse-engineering/raw/wing-emission/pool.json').read_bytes())['cells']:self.vm.mem_write(int(x['va'],16),bytes.fromhex(x['hex']))
        self.hooks.update({0x110d240:self.alloc,0x2143330:self.noop,0x19a9434:self.delegate,0x2786dc0:self.clock,0x278276c:self.start,0x2786508:self.wait,0x278a75c:self.child_count,0x278ab34:self.child,0x277f14c:self.transform,0x27891b8:self.position,0x27898a0:self.scale,0x110d12c:self.noop,0x15b50ac:self.sound,0x123a9fc:self.pool,0x171d8c4:self.component,0x2781748:self.go_transform,0x2789258:self.set_position,0x2778580:self.quaternion,0x27894d4:self.noop,0x11881d8:self.interface_entry,0x1030000:self.set_bullet,0x2781804:self.activate})
        for m in self.members:
            if '<ShootBasicBullets>g__Shoot' in m['signature']:self.hooks[int(m['va'],16)]=self.basic_leaf
            if '<ShootCircleBullets>g__Shoot' in m['signature']:self.hooks[int(m['va'],16)]=self.circle_leaf
        rel={x['offset']:int(x['addend'],16) for x in self.payload['relocations']};typ=rel['0x2adcdb0']
        self.vm.mem_write(typ+0xe0,struct.pack('<I',1));self.vm.mem_write(typ+0xb8,struct.pack('<Q',STATIC))
        self.reset()
    def f(self,r):return struct.unpack('<f',struct.pack('<I',self.vm.reg_read(UC_ARM64_REG_S0+r)))[0]
    def sf(self,r,v):self.vm.reg_write(UC_ARM64_REG_S0+r,struct.unpack('<I',struct.pack('<f',v))[0])
    def x(self,n):return self.vm.reg_read(UC_ARM64_REG_X0+n)
    def sx(self,n,v):self.vm.reg_write(UC_ARM64_REG_X0+n,v&0xffffffffffffffff)
    def wi(self,a,v):self.vm.mem_write(a,struct.pack('<i',v))
    def ri(self,a):return struct.unpack('<i',self.vm.mem_read(a,4))[0]
    def rq(self,a):return struct.unpack('<Q',self.vm.mem_read(a,8))[0]
    def reset(self,*,children=((10.,20.,30.),(40.,50.,60.)),rate=.12,deadline=0.,sound_deadline=100.,demo=False,super_mode=False,spacing=(2.,3.),delta=5.,start_y=4.,layer_bullet=9.,directions=(-1,1)):
        self.vm.mem_write(SELF,b'\0'*0x400);self.vm.mem_write(PLAYER,b'\0'*0x100);self.vm.mem_write(PLAYER+0x2a,bytes([super_mode]));self.vm.mem_write(SELF+0x30,bytes([demo]))
        self.ibullet=False;self.delegates={};self.pool_null=False;self.has_player=True;self.children=list(children);self.now=lambda:10.;self.times=[];self.events=[];self.waits=[];self.started=[];self.on_start=None;self.on_leaf=None;self.position_provider=None;self.position_reads=[];self.next_heap=0x1010000
        self.put('shotRate',rate);self.put('timeToShot',deadline);self.put('timeToPlaySound',sound_deadline);self.put('startY',start_y);self.put('deltaAngle',delta);self.put('arcRange',360.);self.put('startAngle',-180.)
        self.vm.mem_write(SELF+self.names['barrel'],struct.pack('<Q',PARENT))
        if 'spacing' in self.names:self.vm.mem_write(SELF+self.names['spacing'],struct.pack('<2f',*spacing))
        if 'directs' in self.names and directions is not None:
            self.vm.mem_write(SELF+self.names['directs'],struct.pack('<Q',DIRECTS));self.wi(DIRECTS+0x18,len(directions))
            self.vm.mem_write(DIRECTS+0x20,struct.pack('<'+'i'*len(directions),*directions))
        self.vm.mem_write(STATIC+0x14,struct.pack('<f',layer_bullet))
    def alloc(self):
        a=self.next_heap;self.next_heap+=0x100;self.vm.mem_write(a,b'\0'*0x100);self.sx(0,a)
    def clock(self):
        value=self.now();self.times.append(value);self.sf(0,value)
    def start(self):
        a=self.x(1);self.started.append(a);self.events.append(dict(kind='start',deadline=self.get('timeToShot'),state=self.ri(a+0x10)))
        if self.on_start:self.on_start(self,a)
        self.sx(0,a)
    def wait(self):self.waits.append(self.f(0))
    def child_count(self):self.sx(0,len(self.children))
    def child(self):
        i=self.x(1)&0xffffffff
        if i>=len(self.children):raise NativeFault('child bounds')
        self.sx(0,POINT+0x40*i)
    def transform(self):self.sx(0,PARENT)
    def position(self):
        a=self.x(0);xyz=self.children[(a-POINT)//0x40] if a>=POINT and a<POINT+0x100 else (10.,20.,30.)
        if self.position_provider:xyz=self.position_provider(a)
        self.position_reads.append(tuple(xyz))
        for r,v in enumerate(xyz):self.sf(r,v)
    def scale(self):
        for r,v in enumerate((6.,1.,1.)):self.sf(r,v)
    def sound(self):self.events.append(dict(kind='sound',clip=self.x(0)&0xffffffff,volume=self.f(0),deadline=self.get('timeToPlaySound')))
    def pool(self):self.events.append(dict(kind='pool13',id=self.x(0)&0xffffffff));self.sx(0,0 if self.pool_null else POOLED)
    def component(self):
        self.vm.mem_write(0x1006000,struct.pack('<Q',0x1006100));self.sx(0,0x1006000 if self.ibullet else 0)
    def delegate(self):self.delegates[self.x(0)]=(self.x(1),self.x(2))
    def go_transform(self):self.sx(0,0x1005400)
    def set_position(self):self.events.append(dict(kind='position13',position=[self.f(i) for i in range(3)]))
    def quaternion(self):
        self.events.append(dict(kind='euler_rad13',euler=[self.f(i) for i in range(3)]))
        for i,v in enumerate((0.,0.,0.,1.)):self.sf(i,v)
    def interface_entry(self):
        self.vm.mem_write(0x1020000,struct.pack('<QQ',0x1030000,0));self.sx(0,0x1020000)
    def set_bullet(self):self.events.append(dict(kind='set_bullet13',force=self.x(1),target=self.x(2),mask=self.x(3),speed=self.f(0),lifetime=self.f(1),angle=self.f(2),collision=self.delegates.get(self.x(4)),destroy=self.delegates.get(self.x(5)),through=self.x(6)))
    def activate(self):self.events.append(dict(kind='activate13',value=self.x(1)))
    def basic_leaf(self):
        ref=self.x(1);self.events.append(dict(kind='basic',id=self.ri(ref+8),position=[self.f(i) for i in range(3)],angle=self.f(3),point=self.rq(ref),callbacks=[self.rq(ref+(32 if self.i==22 else 16)),self.rq(ref+24)]))
        if self.on_leaf:self.on_leaf(self)
    def circle_leaf(self):
        ref=self.x(1);self.events.append(dict(kind='circle',id=self.ri(ref),position=[self.f(i) for i in range(3)],angle=self.f(3)))
        if self.on_leaf:self.on_leaf(self)
    def find_method(self,name,nested=False):return next(m for m in self.members if m['method']==name and ('.' in m['cls'])==nested)
    def call(self,m,*args,fp=()):
        if isinstance(m,str):m=self.find_method(m)
        self.vm.reg_write(UC_ARM64_REG_SP,0x400f000);self.vm.reg_write(UC_ARM64_REG_LR,STOP);self.vm.reg_write(UC_ARM64_REG_CPACR_EL1,3<<20);self.vm.reg_write(UC_ARM64_REG_FPCR,0)
        for n,v in enumerate(args):self.sx(n,v)
        for n,v in enumerate(fp):self.sf(n,v)
        self.vm.emu_start(int(m['va'],16),STOP,count=50000);assert self.vm.reg_read(UC_ARM64_REG_PC)==STOP,'fixture instruction budget'
        return self.x(0)
    def shoot(self,number=3,id_bullet=80001):return self.call('Shoot',SELF,number,id_bullet)
    def move(self,a):
        m=next(m for m in self.members if m['method']=='MoveNext' and ('IEShootBarrels' in m['cls'] or 'ShotAllBarrels' in m['cls']))
        return bool(self.call(m,a))
    def basic(self,number,id_bullet=80001):return self.call('ShootBasicBullets',SELF,POINT,id_bullet,number,0x111,0x222)
    def circle(self,number,id_bullet=80001):return self.call('ShootCircleBullets',SELF,id_bullet,number,0x111,0x222,fp=(15.,))
