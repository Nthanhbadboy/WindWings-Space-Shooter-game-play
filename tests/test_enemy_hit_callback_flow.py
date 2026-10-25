import json,struct,unittest
from tools.verify.enemy_damage_model import Receiver,HpRef,calculate_with_callbacks,f32
from tools.verify.enemy_hit_callback_flow import OUT,build
from tools.verify.enemy_hit_callback_models import (combine,start_skeleton,start_drop_gold,start_test_enemy,
 TestTimer,test_first_hit,skeleton_hit,skeleton_cancel,DropGold,drop_gold,gold_plan,on_burst_golds,ellipse_target,burst_out)


class EvidenceTests(unittest.TestCase):
    def test_regeneration(self):self.assertEqual(build(),json.loads(OUT.read_text()))
    def test_real_callback_targets(self):
        r=build();self.assertEqual([b['method_rva'] for b in r['bindings']],['0x1321a1c','0x1581828','0x13231d0','0x14c8f14'])
    def test_serialized_bindings_not_names_alone(self):
        r=build();rows=r['attachments'];self.assertEqual(len(rows),19)
        self.assertEqual([(a['component'],a['health_component']) for a in rows if a['cls']=='Enemy_DropGold'],[(668817,691401),(668818,691402)])
        self.assertTrue(all(a['serialized_file']=='data.unity3d/resources.assets' and a['enabled']==1 for a in rows))
    def test_actual_property_and_invoke_literal(self):
        self.assertEqual([r['utf8'] for r in build()['literals']],['CancelEffect','_Black'])
    def test_direct_reference_census_not_only_test_component(self):
        self.assertEqual(set(build()['direct_metadata_reference_owners']),{'Enemy_Controller','Test_Enemy','Enemy_HitSkeletonRenderer','Enemy_DropGold'})


class RegistrationTests(unittest.TestCase):
    def test_skeleton_assigns_not_combines(self):
        seen=[];r=Receiver(hit_callback=lambda:seen.append('old'));calls=[]
        start_skeleton(lambda:calls.append('get') or r,lambda:seen.append('fx'),lambda:seen.append('cancel'))
        r.hit_callback();self.assertEqual(seen,['cancel','fx']);self.assertEqual(calls,['get','get'])
    def test_skeleton_missing_health_still_cancels(self):
        seen=[];start_skeleton(lambda:None,lambda:None,lambda:seen.append('cancel'));self.assertEqual(seen,['cancel'])
    def test_skeleton_second_getter_is_live(self):
        first=Receiver();second=Receiver();it=iter((first,second));callback=lambda:None
        start_skeleton(lambda:next(it),callback,lambda:None)
        self.assertIsNone(first.hit_callback);self.assertIs(second.hit_callback,callback)
    def test_skeleton_second_null_does_not_cancel_after_failure(self):
        calls=[];it=iter((Receiver(),None))
        with self.assertRaises(ValueError):start_skeleton(lambda:next(it),lambda:None,lambda:calls.append('cancel'))
        self.assertEqual(calls,[])
    def test_test_component_combines_after_skeleton(self):
        seen=[];r=Receiver();start_skeleton(lambda:r,lambda:seen.append('fx'),lambda:None)
        start_test_enemy(r,lambda:seen.append('timer'));r.hit_callback();self.assertEqual(seen,['fx','timer'])
    def test_reverse_registration_order_overwrites_test(self):
        seen=[];r=Receiver();start_test_enemy(r,lambda:seen.append('timer'))
        start_skeleton(lambda:r,lambda:seen.append('fx'),lambda:None);r.hit_callback();self.assertEqual(seen,['fx'])
    def test_drop_gold_combines_in_order(self):
        seen=[];r=Receiver(hit_damage_callback=lambda loss:seen.append(('old',loss)))
        start_drop_gold(r,lambda loss:seen.append(('gold',loss)));r.hit_damage_callback(2)
        self.assertEqual(seen,[('old',2),('gold',2)])
    def test_multicast_exception_stops_later_callback(self):
        seen=[]
        def fail(*_):raise RuntimeError('old callback')
        r=Receiver(hit_damage_callback=fail);start_drop_gold(r,lambda _:seen.append('gold'))
        with self.assertRaises(RuntimeError):r.hit_damage_callback(2)
        self.assertEqual(seen,[])
    def test_test_first_hit_timer_only_once(self):
        s=TestTimer();calls=[]
        test_first_hit(s,lambda:calls.append(1) or 4.5);test_first_hit(s,lambda:calls.append(2) or 9)
        self.assertEqual((s.started,s.time_start,calls),(True,4.5,[1]))
    def test_timer_sets_started_before_clock_failure(self):
        s=TestTimer()
        def clock():self.assertTrue(s.started);raise RuntimeError()
        with self.assertRaises(RuntimeError):test_first_hit(s,clock)
        self.assertTrue(s.started);self.assertEqual(s.time_start,0)


class GoldTests(unittest.TestCase):
    def call(self,s,hp,damage=1,post=lambda *_:None):
        return drop_gold(s,damage,get_current=lambda:hp,get_start=lambda:100,get_parent=lambda:'enemy',post=post)
    def test_threshold_is_strict_greater(self):
        s=DropGold();events=[];self.call(s,90,post=lambda *a:events.append(a));self.assertEqual(events,[])
        self.call(s,89,post=lambda *a:events.append(a));self.assertEqual(events,[(6,{'burstCoins':28,'parent':'enemy'})]);self.assertEqual(s.i_plus,2)
    def test_one_shot_no_ten_threshold_catchup(self):
        s=DropGold();events=[];self.call(s,0,post=lambda *a:events.append(a));self.assertEqual(len(events),1);self.assertEqual(s.i_plus,2)
    def test_damage_argument_is_unused(self):
        a=DropGold();b=DropGold();ea=[];eb=[]
        self.call(a,79,object(),post=lambda *a:ea.append(a));self.call(b,79,-9999,post=lambda *a:eb.append(a))
        self.assertEqual((a,ea),(b,eb))
    def test_heal_below_first_threshold_resets_counter(self):
        s=DropGold(i_plus=8);self.call(s,99);self.assertEqual(s.i_plus,1)
        s.i_plus=8;self.call(s,90);self.assertEqual(s.i_plus,8)  # exactly10 does NOT reset
    def test_i_plus_increment_before_post_and_not_rolled_back(self):
        s=DropGold()
        def post(*_):self.assertEqual(s.i_plus,2);raise RuntimeError()
        with self.assertRaises(RuntimeError):self.call(s,50,post=post)
        self.assertEqual(s.i_plus,2)
    def test_current_read_precedes_live_start_read(self):
        order=[];s=DropGold()
        drop_gold(s,None,get_current=lambda:order.append('current') or 80,get_start=lambda:order.append('start') or 100,get_parent=lambda:order.append('parent'),post=lambda *_:order.append('post'))
        self.assertEqual(order,['current','start','parent','post'])
    def test_constructor_payload28_spawns_eight_objects_not28(self):
        plan=gold_plan(28);self.assertEqual((plan['id70001_count'],plan['id70002_count']),(3,5));self.assertEqual(plan['radius'],f32(2.4))
    def test_exact_multiple10_has_special_small_item_split(self):
        p=gold_plan(10);self.assertEqual((p['id70001_count'],p['id70002_count'],p['pre_split_pieces'],p['radius']),(5,1,2,.75))
    def test_radius_four_uses_nonnearest_float_literal(self):
        p=gold_plan(4);self.assertEqual(struct.pack('<f',p['radius']).hex(),'6766e63f');self.assertNotEqual(p['radius'],f32(1.8))
    def test_budget_grouping_invariant_not_collected_currency(self):
        for n in range(0,1001):
            p=gold_plan(n);self.assertEqual(p['id70001_count']+5*p['id70002_count'],n)
    def test_parent_position_reread_per_spawn(self):
        calls=[];pos=[]
        on_burst_golds({'burstCoins':28,'parent':'P'},get_position=lambda parent:pos.append(parent) or len(pos),burst_out=lambda *args:calls.append(args))
        self.assertEqual([c[0] for c in calls],[70001]*3+[70002]*5);self.assertEqual([c[1] for c in calls],list(range(1,9)))
    def test_bad_payload_is_not_silent(self):
        for payload in (None,0,{}):
            with self.assertRaises(ValueError):on_burst_golds(payload,get_position=lambda _:None,burst_out=lambda *_:None)
    def test_receiver_to_real_registration_to_item_consumer(self):
        hp=HpRef(100);r=Receiver();s=DropGold();items=[];events=[]
        def post(event,payload):
            events.append(event);on_burst_golds(payload,get_position=lambda _:('x','y','z'),burst_out=lambda *a:items.append(a))
        start_drop_gold(r,lambda loss:drop_gold(s,loss,get_current=lambda:hp.hp,get_start=lambda:100,get_parent=lambda:'P',post=post))
        calculate_with_callbacks(r,hp,20)
        self.assertEqual((hp.hp,events,s.i_plus,len(items)),(80,[6],2,8))
    def test_combined_prior_callback_can_change_gold_ratio_not_loss_argument(self):
        hp=HpRef(100);r=Receiver(hit_damage_callback=lambda _:setattr(hp,'hp',99));s=DropGold(i_plus=5);events=[]
        start_drop_gold(r,lambda loss:drop_gold(s,loss,get_current=lambda:hp.hp,get_start=lambda:100,get_parent=lambda:'P',post=lambda *a:events.append(a)))
        trace=calculate_with_callbacks(r,hp,20)
        self.assertIn(('hit_damage_callback',20),trace)
        self.assertEqual((hp.hp,s.i_plus,events),(99,1,[]))
    def test_stable_multicast_snapshot_survives_field_replacement(self):
        hp=HpRef(100);s=DropGold();events=[];r=Receiver()
        r.hit_damage_callback=lambda _:setattr(r,'hit_damage_callback',None)
        start_drop_gold(r,lambda loss:drop_gold(s,loss,get_current=lambda:hp.hp,get_start=lambda:100,get_parent=lambda:'P',post=lambda *a:events.append(a)))
        calculate_with_callbacks(r,hp,20)
        self.assertEqual(len(events),1);self.assertIsNone(r.hit_damage_callback)
    def test_no_damage_blocks_gold_callback(self):
        r=Receiver(no_damage=True);seen=[];start_drop_gold(r,seen.append)
        calculate_with_callbacks(r,HpRef(100),50);self.assertEqual(seen,[])


class EffectsTests(unittest.TestCase):
    def test_black_property_write_then_cancel_reschedule(self):
        seen=[];color=(.7,.7,.7,1)
        skeleton_hit(lambda:['A','B'],lambda *a:seen.append(a),color,lambda _:True,lambda name:seen.append(('cancel',name)),lambda *a:seen.append(a))
        self.assertEqual(seen,[('A',color),('B',color),('cancel','CancelEffect'),('CancelEffect',f32(.01))])
    def test_effect_failure_does_not_schedule(self):
        seen=[]
        def fail(*_):raise KeyError('slot')
        with self.assertRaises(KeyError):skeleton_hit(lambda:['missing'],fail,(1,1,1,1),lambda _:False,lambda _:None,lambda *a:seen.append(a))
        self.assertEqual(seen,[])
    def test_cancel_resets_black_not_hit_color(self):
        seen=[];skeleton_cancel(lambda:['A'],lambda *a:seen.append(a));self.assertEqual(seen,[('A',(0,0,0,1))])
    def test_ellipse_sampling_calls_not_uniform_angle(self):
        calls=[]
        def rf(lo,hi):calls.append((lo,hi));return 0 if len(calls)==1 else .5
        point=ellipse_target((1,2),.75,random_float=rf,random_int=lambda lo,hi:calls.append((lo,hi)) or 1)
        self.assertEqual(calls,[(-.75,.75),(.375,.75),(0,5)]);self.assertEqual(point,(1,1.5))
    def test_large_radius_minimum_zero_and_sign_threshold_two(self):
        for sign in range(5):
            calls=[]
            def rf(lo,hi):calls.append((lo,hi));return 0 if len(calls)==1 else .5
            p=ellipse_target((0,0),2,random_float=rf,random_int=lambda *_:sign)
            self.assertEqual(calls[1][0],0);self.assertEqual(p[1],-.5 if sign<2 else .5)
    def test_pool_then_interface_then_activation(self):
        calls=[];seq=iter((0,.25))
        def pool(item,pos):calls.append(('pool',item,pos));return 'obj'
        def component(obj):calls.append(('get_iitem',obj));return lambda *a:calls.append(('interface',a))
        burst_out(70001,(2,3,9),.75,random_float=lambda *_:next(seq),random_int=lambda *_:4,get_item_z=lambda:-2,pool_get=pool,get_iitem=component,activate=lambda *a:calls.append(('activate',a)))
        self.assertEqual(calls,[('pool',70001,(2,3.25,-2)),('get_iitem','obj'),('interface',((2,3),(2,3.25))),('activate',('obj',True))])
    def test_interface_failure_prevents_explicit_activation(self):
        seen=[];seq=iter((0,.2))
        def interface(*_):raise RuntimeError()
        with self.assertRaises(RuntimeError):burst_out(70001,(0,0,0),.75,random_float=lambda *_:next(seq),random_int=lambda *_:4,get_item_z=lambda:0,pool_get=lambda *_:'obj',get_iitem=lambda _:interface,activate=lambda *a:seen.append(a))
        self.assertEqual(seen,[])
