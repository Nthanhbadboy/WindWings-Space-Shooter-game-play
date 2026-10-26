"""Execute all five previously intercepted Basic/Circle leaves.
SDK Pool/Quaternion/Delegate/IBullet/CreateBullets remain explicit adapters.
"""
import json,struct
from tools.verify.wing_emission_fixture import EmissionFixture,ROOT,SELF,POOLED,NativeFault
FORMATION=0x1006800
class PooledLeafFixture(EmissionFixture):
    def __init__(self,i):
        super().__init__(i)
        for m in self.members:
            if 'g__Shoot' in m['signature']:self.hooks.pop(int(m['va'],16),None)
        self.hooks.update({0x123ab5c:self.pool_packet,0x2789428:self.euler,0x27815fc:self.not_null,0x2146010:self.combine,0x110d130:self.cast,0x110d5ec:self.bad_cast,0x123acd0:self.recycle,0x123d98c:self.create})
        p=ROOT/'reverse-engineering/raw/wing-emission/formation-trampoline.json'
        if p.exists():
            self.vm.mem_map(0x2990000,0x1000)
            for c in json.loads(p.read_bytes())['cells']:self.vm.mem_write(int(c['va'],16),bytes.fromhex(c['hex']))
        self.ibullet=True;self.formation=True;self.unity_alive=True;self.cast_ok=True;self.point_euler=30.;self.pooled_euler=77.;self.transform_null=False
        self.put('btlSpeed',17.);self.wi(SELF+self.names['targetLayer'],246)
    def euler(self):
        z=self.pooled_euler if self.x(0)==0x1005400 else self.point_euler
        self.sf(0,0.);self.sf(1,0.);self.sf(2,z)
    def pool_packet(self):
        self.events.append(dict(kind='pool_packet',id=self.x(0)&0xffffffff,position=[self.f(k) for k in range(3)],quaternion=[self.f(k) for k in range(3,7)]))
        self.sx(0,0 if self.pool_null else POOLED)
    def component(self):
        rel={x['offset']:int(x['addend'],16) for x in self.payload['relocations']}
        is_formation=self.x(1)==rel['0x2ae8030']
        self.events.append(dict(kind='get_component',component='formation' if is_formation else 'IBullet'))
        if is_formation:self.sx(0,FORMATION if self.formation else 0)
        else:super().component()
    def not_null(self):self.sx(0,int(bool(self.x(0)) and self.unity_alive))
    def cast(self):
        if not self.cast_ok:self.sx(0,0)
    def bad_cast(self):raise NativeFault('delegate cast')
    def descriptor(self,a):return self.delegates.get(a,('external',a)) if a else ()
    def combine(self):
        a,b=self.x(0),self.x(1)
        if not a:self.sx(0,b);return
        if not b:return
        desc=('combine',self.descriptor(a),self.descriptor(b));p=self.next_heap;self.next_heap+=0x100;self.delegates[p]=desc;self.sx(0,p)
    def set_bullet(self):
        super().set_bullet();self.events[-1].update(kind='set_bullet',collision=self.descriptor(self.x(4)),destroy=self.descriptor(self.x(5)))
    def go_transform(self):self.sx(0,0 if self.transform_null else 0x1005400)
    def recycle(self):self.events.append(dict(kind='recycle',object=self.x(0)))
    def create(self):self.events.append(dict(kind='create',force=self.x(1),target=self.x(2),mask=self.x(3),speed=self.f(0),lifetime=self.f(1),collision=self.descriptor(self.x(4))))
