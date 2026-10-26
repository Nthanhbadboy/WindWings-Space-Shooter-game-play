import unittest,json,struct
from tools.verify.wing_pooled_leaf_fixture import PooledLeafFixture,SELF,NativeFault
from tools.verify.wing_emission_fixture import POINT
from tools.verify.enemy_damage_model import f32
CASES=[(22,'basic'),(23,'basic'),(24,'basic'),(22,'circle'),(23,'circle')]
class Leaves(unittest.TestCase):
    def execute(self,v,kind,n=1):return getattr(v,kind)(n)
    def events(self,v,kind):return [e for e in v.events if e['kind']==kind]

def baseline(self,i,kind):
    v=PooledLeafFixture(i);self.execute(v,kind);e=self.events(v,'set_bullet')[0]
    self.assertEqual((e['force'],e['target'],e['mask'],e['speed'],e['angle']),(1,0,246,15. if kind=='circle' else 17.,77.))
    self.assertEqual(e['lifetime'],4. if kind=='basic' and i in (23,24) else 5. if i==22 else 10.)
    names=[x['kind'] for x in v.events];self.assertLess(names.index('activate13'),names.index('get_component'));self.assertLess(names.index('get_component'),names.index('set_bullet'))
    self.assertEqual(len(self.events(v,'create')),int(kind=='basic' and i!=22))
def missing(self,i,kind):
    v=PooledLeafFixture(i);v.ibullet=False;self.execute(v,kind)
    self.assertEqual(len(self.events(v,'activate13')),1);self.assertFalse(self.events(v,'set_bullet'));self.assertEqual(len(self.events(v,'recycle')),int(kind=='basic' and i!=22))
def nullpool(self,i,kind):
    v=PooledLeafFixture(i);v.pool_null=True
    with self.assertRaisesRegex(NativeFault,'null'):self.execute(v,kind)
    self.assertFalse(self.events(v,'activate13'));self.assertFalse(self.events(v,'recycle'))
def through(self,i,kind):
    for super_mode in (False,True):
        v=PooledLeafFixture(i);v.vm.mem_write(SELF+v.names['throughShield'],b'\x01');v.vm.mem_write(0x1001000+0x2a,bytes([super_mode]))
        self.execute(v,kind);self.assertEqual(self.events(v,'set_bullet')[0]['through'],1)
def geometry(self,i,kind):
    v=PooledLeafFixture(i);self.execute(v,kind,3);pool=self.events(v,'pool_packet')
    self.assertEqual(len(pool),3)
    if kind=='basic':
        self.assertEqual([x['position'] for x in pool],[[10.,24.,9.],[8.,27.,9.],[12.,27.,9.]])
        expected=[30.,25.,35.]
    else:expected=[-180.,-60.,60.]
    self.assertEqual([x['euler'][2] for x in self.events(v,'euler_rad13')],[f32(f32(x)*f32(.01745329238474369)) for x in expected])
    self.assertTrue(all(x['quaternion']==[0.,0.,0.,1.] for x in pool))
def callbacks(self,i,kind):
    v=PooledLeafFixture(i);self.execute(v,kind);e=self.events(v,'set_bullet')[0]
    if i==22 or kind=='circle':self.assertEqual((e['collision'],e['destroy']),(('external',0x222),('external',0x111)))
    else:
        self.assertEqual(e['collision'],('combine',(0x1006800,45876264),('external',0x222)));self.assertEqual(e['destroy'],('combine',(0x1006800,45876272),('external',0x111)))
        self.assertEqual(self.events(v,'create')[0]['collision'],('external',0x222))
for i,kind in CASES:
    for fn in (baseline,missing,nullpool,through,geometry,callbacks):
        def test(self,i=i,kind=kind,fn=fn):fn(self,i,kind)
        setattr(Leaves,f'test_{i}_{kind}_{fn.__name__}',test)
class FormationFailures(unittest.TestCase):
    def test_missing_formation_recycles_no_configure(self):
        for i in (23,24):
            v=PooledLeafFixture(i);v.formation=False;v.basic(1);self.assertEqual([e['kind'] for e in v.events][-1],'recycle');self.assertFalse(any(e['kind']=='set_bullet' for e in v.events))
    def test_unity_null_semantics_even_nonzero_pointer(self):
        for i in (23,24):
            v=PooledLeafFixture(i);v.unity_alive=False;v.basic(1);self.assertEqual(v.events[-1]['kind'],'recycle')
    def test_invalid_delegate_cast_not_success_or_recycle(self):
        for i in (23,24):
            v=PooledLeafFixture(i);v.cast_ok=False
            with self.assertRaisesRegex(NativeFault,'delegate cast'):v.basic(1)
            self.assertFalse(any(e['kind'] in ('recycle','set_bullet','create') for e in v.events))
    def test_null_transform_throws_after_activation(self):
        for i,k in CASES:
            v=PooledLeafFixture(i);v.transform_null=True
            with self.assertRaisesRegex(NativeFault,'null'):getattr(v,k)(1)
            self.assertTrue(any(e['kind']=='activate13' for e in v.events));self.assertFalse(any(e['kind']=='set_bullet' for e in v.events))
    def test_null_external_callbacks_preserve_formation_callbacks(self):
        for i in (23,24):
            v=PooledLeafFixture(i);v.call('ShootBasicBullets',SELF,POINT,80001,1,0,0);e=next(e for e in v.events if e['kind']=='set_bullet');self.assertEqual(e['collision'],(0x1006800,45876264));self.assertEqual(e['destroy'],(0x1006800,45876272));self.assertEqual(v.events[-1]['collision'],())
    def test_create_exception_is_after_interface_setup(self):
        for i in (23,24):
            v=PooledLeafFixture(i)
            def fail():raise RuntimeError('CreateBullets SDK')
            v.hooks[0x123d98c]=fail
            with self.assertRaisesRegex(RuntimeError,'CreateBullets'):v.basic(1)
            self.assertTrue(any(e['kind']=='set_bullet' for e in v.events));self.assertFalse(any(e['kind']=='recycle' for e in v.events))

class Evidence(unittest.TestCase):
    def test_regeneration(self):
        from tools.verify.wing_pooled_leaves import build,OUT
        self.assertEqual(build(),json.loads(OUT.read_bytes()))
    def test_native_trampoline_is_executed_not_substituted(self):
        v=PooledLeafFixture(23);self.assertNotIn(0x2990890,v.hooks);self.assertEqual(bytes(v.vm.mem_read(0x2990890,8)),bytes.fromhex('4af945f9de55ac17'));v.basic(1)
    def test_circle_minus_one_reaches_pool_as_int32_bits(self):
        for i in (22,23):
            v=PooledLeafFixture(i);v.circle(1,-1);self.assertEqual(next(e for e in v.events if e['kind']=='pool_packet')['id'],0xffffffff)
    def test_zero_spacing_even_count_reaches_all_three_real_leaves(self):
        for i in (22,23,24):
            v=PooledLeafFixture(i);v.vm.mem_write(SELF+v.names['spacing'],struct.pack('<2f',0.,3.));v.basic(2);self.assertEqual(sum(e['kind']=='set_bullet' for e in v.events),3)
