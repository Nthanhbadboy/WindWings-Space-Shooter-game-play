import json,math,unittest
from tools.verify.wing_emission_flow import build,OUT
from tools.verify.wing_emission_fixture import EmissionFixture,SELF,PARENT,NativeFault
from tools.verify.wing_emission_models import basic,circle,Iterator13,Iterator23
from tools.verify.enemy_damage_model import f32

class Evidence(unittest.TestCase):
    def test_reproducible(self):self.assertEqual(build(),json.loads(OUT.read_text()))
    def test_no_circle_on24(self):self.assertEqual(json.loads(OUT.read_text())['circle_geometry']['implementations'],[22,23])

class Shoot(unittest.TestCase):
    def test_deadline_equality_all_four(self):
        for i in (13,22,23,24):
            v=EmissionFixture(i);v.reset(deadline=10.);v.shoot();self.assertAlmostEqual(v.get('timeToShot'),10.12,places=5)
    def test_before_deadline_all_four(self):
        for i in (13,22,23,24):
            v=EmissionFixture(i);v.reset(deadline=11.);v.shoot();self.assertEqual(v.events,[]);self.assertEqual(v.get('timeToShot'),11.)
    def test_start_order_13_vs23_24(self):
        for i in (13,23,24):
            v=EmissionFixture(i);v.shoot();self.assertEqual(v.events[0]['deadline'],0. if i==13 else f32(10.+f32(.12)))
    def test_callback_changes_rate13_only_before_deadline(self):
        for i in (13,23,24):
            v=EmissionFixture(i);v.on_start=lambda fixture,_:fixture.put('shotRate',.7);v.shoot();self.assertEqual(v.get('timeToShot'),f32(10.+f32(.7 if i==13 else .12)))
    def test_start_exception_write_order(self):
        for i in (13,23,24):
            v=EmissionFixture(i)
            def fail(*_):raise RuntimeError('SDK boundary')
            v.on_start=fail
            with self.assertRaises(RuntimeError):v.shoot()
            self.assertEqual(v.get('timeToShot'),0. if i==13 else f32(10.+f32(.12)))
    def test_empty_children_22_spends_deadline(self):
        v=EmissionFixture(22);v.reset(children=());v.shoot();self.assertEqual(v.events,[]);self.assertGreater(v.get('timeToShot'),10.)
    def test_null_parent22_spends_deadline(self):
        v=EmissionFixture(22);v.vm.mem_write(SELF+v.names['barrel'],bytes(8))
        with self.assertRaisesRegex(NativeFault,'null'):v.shoot()
        self.assertGreater(v.get('timeToShot'),10.)
    def test22_direct_loop_rereads_child_count(self):
        v=EmissionFixture(22)
        def grow(f):
            if len(f.children)==2:f.children.append((70.,80.,90.))
        v.on_leaf=grow;v.shoot(1);self.assertEqual(len(v.events),3)
    def test_no_busy_flag_guard(self):
        for i in (13,23,24):
            v=EmissionFixture(i);v.shoot();v.now=lambda:v.get('timeToShot');v.shoot();self.assertEqual(len(v.started),2)
    def test_sound_intervals_volume(self):
        for i in (13,22,23,24):
            for super_mode in (False,True):
                v=EmissionFixture(i);v.reset(super_mode=super_mode,sound_deadline=0.);v.shoot(1)
                if i==13:v.move(v.started[0])
                e=next(x for x in v.events if x['kind']=='sound');self.assertEqual(e['clip'],5);self.assertEqual(e['volume'],1. if super_mode else f32(.6));self.assertEqual(v.get('timeToPlaySound'),f32(10.+f32(.04 if super_mode else .08)))
    def test_demo_suppresses_sound_not_packet(self):
        for i in (13,22,23,24):
            v=EmissionFixture(i);v.reset(demo=True,sound_deadline=0.);v.shoot(1)
            if v.started:v.move(v.started[0])
            self.assertFalse(any(x['kind']=='sound' for x in v.events));self.assertTrue(any(x['kind'] in ('pool13','basic') for x in v.events))

class Iterators(unittest.TestCase):
    def test13_pair_count_and_trailing_wait(self):
        v=EmissionFixture(13);v.shoot(3);a=v.started[0];returns=[v.move(a) for _ in range(4)];self.assertEqual(returns,[True]*3+[False]);self.assertEqual(sum(e['kind']=='pool13' for e in v.events),6);self.assertEqual(v.waits,[f32(f32(.12)/3)]*3)
    def test13_interval_cap(self):
        v=EmissionFixture(13);v.reset(rate=1.);v.shoot(2);self.assertTrue(v.move(v.started[0]));self.assertEqual(v.waits,[f32(.05)])
    def test13_interval_frozen_across_yields(self):
        v=EmissionFixture(13);v.shoot(3);a=v.started[0];v.move(a);v.put('shotRate',.9);v.move(a);self.assertEqual(v.waits[0],v.waits[1])
    def test13_nonpositive_count_no_emission_no_wait(self):
        for n in (0,-1,-3):
            v=EmissionFixture(13);v.shoot(n);self.assertFalse(v.move(v.started[0]));self.assertFalse(v.waits);self.assertFalse(any(e['kind']=='pool13' for e in v.events))
    def test23_24_one_child_each_yield_and_trailing_wait(self):
        for i in (23,24):
            v=EmissionFixture(i);v.shoot(3);a=v.started[0];self.assertEqual([v.move(a) for _ in range(3)],[True,True,False]);self.assertEqual(v.waits,[f32(f32(.12)/2)]*2);self.assertEqual(sum(e['kind']=='basic' for e in v.events),6)
    def test23_24_wait_live_after_packet(self):
        for i in (23,24):
            v=EmissionFixture(i);v.shoot(1);a=v.started[0]
            def mutate(f):f.put('shotRate',.6);f.children.pop() if len(f.children)>1 else None
            v.on_leaf=mutate;self.assertTrue(v.move(a));self.assertEqual(v.waits,[f32(.6)]);self.assertFalse(v.move(a))
    def test23_24_zero_count_after_emit_yields_infinity_not_silent_skip(self):
        for i in (23,24):
            v=EmissionFixture(i);v.shoot(1);v.on_leaf=lambda f:f.children.clear();self.assertTrue(v.move(v.started[0]));self.assertTrue(math.isinf(v.waits[0]))
    def test23_24_new_rate_each_wait(self):
        for i in (23,24):
            v=EmissionFixture(i);v.shoot(1);a=v.started[0];v.move(a);v.put('shotRate',.8);v.move(a);self.assertEqual(v.waits,[f32(f32(.12)/2),f32(f32(.8)/2)])
    def test23_24_empty_children_no_wait(self):
        for i in (23,24):
            v=EmissionFixture(i);v.reset(children=());v.shoot();self.assertFalse(v.move(v.started[0]));self.assertEqual(v.waits,[])
    def test_unknown_state_does_not_restart(self):
        for i in (13,23,24):
            v=EmissionFixture(i);v.shoot();a=v.started[0];v.wi(a+0x10,2);self.assertFalse(v.move(a));self.assertEqual(v.ri(a+0x10),2)
    def test_dispose_no_state_reset(self):
        for i in (13,23,24):
            v=EmissionFixture(i);v.shoot();a=v.started[0];v.move(a);m=next(m for m in v.members if m['method']=='Dispose' and ('ShotAllBarrels' in m['cls'] or 'IEShootBarrels' in m['cls']));v.call(m,a);self.assertEqual(v.ri(a+0x10),1)
    def test_models_match_native_state_sequences(self):
        for i in (13,23,24):
            v=EmissionFixture(i);v.shoot(3);a=v.started[0];model=Iterator13() if i==13 else Iterator23();waits=[]
            for _ in range(4):
                native=v.move(a)
                expected=model.step(number=3,get_rate=lambda:f32(.12),emit_pair=lambda _:None,wait=waits.append) if i==13 else model.step(child_count=lambda:2,get_rate=lambda:f32(.12),emit=lambda _:None,wait=waits.append)
                self.assertEqual(native,expected);self.assertEqual(v.ri(a+0x10),model.state)
                if not native:break
            self.assertEqual(v.waits,waits)

class Geometry(unittest.TestCase):
    def compare(self,i,demo,dx):
        v=EmissionFixture(i)
        for n in range(-3,9):
            v.reset(demo=demo,spacing=(dx,3.));v.basic(n);expected=[];basic(n,80001,get_position=lambda:(10.,20.,30.),spacing=(dx,3.),delta=5.,start_y=4.,directions=(-1,1),demo=demo,layer_bullet=9.,emit=expected.append)
            self.assertEqual([{k:e[k] for k in ('position','angle')} for e in v.events],expected,(i,n,demo,dx))
    def test_id_minus_one_basic_no_attempt(self):
        for i in (22,23,24):v=EmissionFixture(i);v.basic(5,-1);self.assertEqual(v.events,[])
    def test_even_zero_spacing_extra_center(self):
        for i in (22,23,24):v=EmissionFixture(i);v.reset(spacing=(0.,3.));v.basic(2);self.assertEqual(len(v.events),3)
    def test_number_zero_can_emit_center(self):
        for i in (22,23,24):v=EmissionFixture(i);v.reset(spacing=(0.,3.));v.basic(0);self.assertEqual(len(v.events),1)
    def test_directions_exception_after_partial_packet(self):
        for i in (22,23,24):
            v=EmissionFixture(i);v.reset(directions=(-1,))
            with self.assertRaisesRegex(NativeFault,'bounds'):v.basic(2)
            self.assertEqual(len(v.events),1)
    def test_no_direction_access_for_single_center(self):
        for i in (22,23,24):v=EmissionFixture(i);v.reset(directions=None);v.basic(1);self.assertEqual(len(v.events),1)
    def test_callback_ref_layouts_are_different_but_binding_preserved(self):
        for i in (22,23,24):v=EmissionFixture(i);v.basic(1);self.assertEqual(v.events[0]['callbacks'],[0x111,0x222])
    def test_position_getters_are_reread(self):
        for i in (22,23,24):
            v=EmissionFixture(i);v.reset(demo=True);calls=iter([(1.,2.,3.),(4.,5.,6.),(7.,8.,9.)]);v.position_provider=lambda _:next(calls);v.basic(1);self.assertEqual(v.events[0]['position'],[1.,9.,f32(9.+f32(.1))])
    def test_circle_uniform_without_duplicate_endpoint(self):
        for i in (22,23):
            for n in (-2,0,1,2,3,8):
                v=EmissionFixture(i);v.circle(n);expected=[];circle(n,get_position=lambda:(10.,20.,30.),arc=360.,start_angle=-180.,emit=expected.append);self.assertEqual([{k:e[k] for k in ('position','angle')} for e in v.events],expected)
    def test_circle_does_not_filter_minus_one_id(self):
        for i in (22,23):v=EmissionFixture(i);v.circle(2,-1);self.assertEqual([e['id'] for e in v.events],[-1,-1])
    def test_circle_uses_world_z_not_basic_layer_override(self):
        for i in (22,23):v=EmissionFixture(i);v.circle(1);self.assertEqual(v.events[0]['position'][2],30.)

def case(i,demo,dx):
    def test(self):self.compare(i,demo,dx)
    return test
for i in (22,23,24):
    for demo in (False,True):
        for dx in (0.,2.):setattr(Geometry,f'test_basic_{i}_{demo}_{dx}',case(i,demo,dx))

class Configured13(unittest.TestCase):
    def test_positions_angles_and_activation(self):
        v=EmissionFixture(13);v.ibullet=True;v.put('btlSpeed',17.);v.shoot(3);a=v.started[0]
        for _ in range(3):self.assertTrue(v.move(a))
        self.assertEqual([e['position'][0] for e in v.events if e['kind']=='position13'],[10.,40.,8.,42.,6.,44.])
        cfg=[e for e in v.events if e['kind']=='set_bullet13'];self.assertEqual([e['angle'] for e in cfg],[0.,-0.,4.,-4.,8.,-8.])
        for e in cfg:self.assertEqual((e['speed'],e['lifetime'],e['force'],e['target']),(17.,2.,1,0));self.assertIsNotNone(e['collision']);self.assertIsNotNone(e['destroy'])
        self.assertEqual(sum(e['kind']=='activate13' for e in v.events),6)
    def test_super_through_shield_guard(self):
        for super_mode in (False,True):
            for through in (False,True):
                v=EmissionFixture(13);v.reset(super_mode=super_mode);v.ibullet=True;v.vm.mem_write(SELF+v.names['throughShield'],bytes([through]));v.shoot(1);v.move(v.started[0]);self.assertEqual([e['through'] for e in v.events if e['kind']=='set_bullet13'],[int(super_mode and through)]*2)
    def test_demo13_z_uses_barrel_parent_not_child_z(self):
        v=EmissionFixture(13);v.reset(demo=True);v.ibullet=True;v.shoot(1);v.move(v.started[0]);self.assertEqual([e['position'][2] for e in v.events if e['kind']=='position13'],[f32(30.+f32(.1))]*2)
    def test_missing_component_still_two_attempts_but_no_activation(self):
        v=EmissionFixture(13);v.shoot(1);v.move(v.started[0]);self.assertEqual(sum(e['kind']=='pool13' for e in v.events),2);self.assertFalse(any(e['kind']=='activate13' for e in v.events))
    def test_present_component_requires_second_child(self):
        v=EmissionFixture(13);v.reset(children=((10.,20.,30.),));v.ibullet=True;v.shoot(1)
        with self.assertRaisesRegex(NativeFault,'child bounds'):v.move(v.started[0])
        self.assertEqual(sum(e['kind']=='pool13' for e in v.events),2)
    def test_null_pool_is_exception_not_component_skip(self):
        v=EmissionFixture(13);v.pool_null=True;v.shoot(1)
        with self.assertRaisesRegex(NativeFault,'null'):v.move(v.started[0])
        self.assertEqual(sum(e['kind']=='pool13' for e in v.events),1)
