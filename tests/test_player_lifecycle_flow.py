import json,unittest
from tools.verify.damage_receiver_models import Player,Damager,player_take_damage,f32
from tools.verify.player_lifecycle_flow import OUT,build
from tools.verify.player_lifecycle_models import (Lifecycle,gain_health,heal_hp,zone_heal,
    no_touch,normal_extra_life,pvp_extra_life)


class LifecycleTests(unittest.TestCase):
    def test_regeneration(self):self.assertEqual(build(),json.loads(OUT.read_text()))

    def test_exact_binding_not_method_name_inference(self):
        rows={r['got']:r for r in build()['bindings']}
        self.assertEqual(rows['0x2ae8480']['effective'],'0x2bc83d0')
        self.assertEqual(rows['0x2ae8480']['method_rva'],'0x14c42d4')
        self.assertEqual(rows['0x2ae8418']['method_rva'],'0x1471884')
        self.assertEqual(rows['0x2ae85a8']['method_rva'],'0x14c52e4')

    def test_exact_nonround_zone_heal_literal(self):
        c={c['va']:c for c in build()['literals']}
        self.assertEqual(c['0x756b7c']['hex'],'a8574a3c')
        self.assertEqual(c['0x756b7c']['value'],f32(.01235))

    def test_gain_health_caps_at_max(self):
        p=Player(hp=99);events=[];gain_health(p,5,post=lambda *a:events.append(a))
        self.assertEqual((p.hp,events),(100,[(21,100)]))

    def test_gain_health_has_no_zero_floor(self):
        p=Player(hp=1);gain_health(p,-5);self.assertEqual(p.hp,-4)

    def test_gain_payload_loaded_after_fx_call(self):
        p=Player(hp=1);seen=[]
        gain_health(p,1,has_fx=True,fx=lambda:setattr(p,'hp',7),post=lambda *a:seen.append(a))
        self.assertEqual(seen,[(21,7)])

    def test_heal_target_snapshot_not_current_hp(self):
        p=Player(hp=100);seen=[]
        g=heal_hp(lambda:p.start_hp,.5,lambda:1,lambda amount:seen.append(amount))
        self.assertEqual(next(g),('frame',None));p.start_hp=200
        self.assertEqual(next(g),('frame',None))
        with self.assertRaises(StopIteration):next(g)
        self.assertEqual(seen,[25,25])  # target50/progress1, not target100 after max change

    def test_heal_progress_starts_one_not_zero(self):
        p=Player(hp=1,start_hp=100);amounts=[]
        g=heal_hp(lambda:p.start_hp,.5,lambda:1.96,lambda a:amounts.append(a))
        self.assertEqual(next(g),('frame',None))
        with self.assertRaises(StopIteration):next(g)
        self.assertEqual(amounts,[49])

    def test_heal_can_overshoot_local_target_but_gain_clamps_live_hp(self):
        p=Player(hp=1)
        g=heal_hp(lambda:p.start_hp,1,lambda:3,lambda amount:gain_health(p,amount))
        next(g)
        with self.assertRaises(StopIteration):next(g)
        self.assertEqual(p.hp,100)

    def test_heal_zero_scaled_dt_yields_without_progress(self):
        amounts=[];g=heal_hp(lambda:100,.5,lambda:0,amounts.append)
        self.assertEqual([next(g) for _ in range(3)],[('frame',None)]*3)
        self.assertEqual(amounts,[0,0,0]);g.close()

    def test_small_target_at_or_below_one_does_not_gain(self):
        for percent in [0,-1,.01]:
            self.assertEqual(list(heal_hp(lambda:100,percent,lambda:1,lambda _:self.fail('no gain'))),[])

    def test_zone_wait_before_first_heal_and_live_max(self):
        max_hp=[100];seen=[];g=zone_heal(lambda:max_hp[0],lambda *a:seen.append(a))
        self.assertEqual(next(g),('wait',f32(.2)));self.assertEqual(seen,[])
        next(g);max_hp[0]=200;next(g)
        self.assertEqual(seen,[(f32(100*f32(.01235)),True),(f32(200*f32(.01235)),True)])
        g.close()

    def test_no_touch_short_circuit_and_all_four_checks(self):
        for flags,expected in [((False,False,False,0),True),((True,False,False,0),False),
                               ((False,True,False,0),False),((False,False,True,0),False),
                               ((False,False,False,1),False)]:
            self.assertEqual(no_touch(*(lambda x=x:x for x in flags)),expected)

    def test_normal_gain_one_and_invincibility_before_wait(self):
        p=Player(hp=0);state=Lifecycle();seen=[]
        g=normal_extra_life(p,state,gain=lambda a:gain_health(p,a),no_touch_predicate=lambda:False,
            schedule_done=lambda:seen.append(('schedule',p.hp,p.invincible)),start_heal=seen.append)
        kind,predicate=next(g)
        self.assertEqual((kind,predicate()),('wait_until',False))
        self.assertEqual((p.hp,p.invincible,state.hit_enemy_enabled,state.time_scale),(1,True,False,0))
        self.assertEqual(seen,[('schedule',1,True)])
        g.close()

    def test_normal_resume_scale_point_zero_five_not_one(self):
        p=Player(hp=0);state=Lifecycle();started=[]
        g=normal_extra_life(p,state,gain=lambda a:gain_health(p,a),no_touch_predicate=lambda:True,
            schedule_done=lambda:None,start_heal=started.append)
        next(g)
        with self.assertRaises(StopIteration):next(g)
        self.assertEqual(state.time_scale,f32(.05));self.assertEqual(started,[.5])
        self.assertEqual(state.flag_pair,(False,False));self.assertEqual(p.hp,1)

    def test_pvp_event_precedes_gain_and_no_pause_or_wait(self):
        p=Player(hp=0);state=Lifecycle(time_scale=.7);seen=[]
        pvp_extra_life(p,state,post=lambda e,_:seen.append((e,p.hp)),
            gain=lambda a:gain_health(p,a,post=lambda e,v:seen.append((e,v))),
            schedule_done=lambda:seen.append(('schedule',p.invincible)),start_heal=seen.append)
        self.assertEqual(seen,[(86,0),(21,1),('schedule',True),1])
        self.assertEqual(state.time_scale,.7)

    def test_dead_receiver_with_concrete_normal_callback_restores_one_not_full(self):
        p=Player(hp=100);state=Lifecycle();pending=[];events=[]
        def extra():
            g=normal_extra_life(p,state,gain=lambda a:gain_health(p,a,post=lambda e,v:events.append((e,v))),
                no_touch_predicate=lambda:False,schedule_done=lambda:None,start_heal=lambda _:None)
            next(g);pending.append(g)
        p.on_extra_life=extra
        player_take_damage(p,Damager(500),level=lambda n:int(n==16),post=lambda e,v:events.append((e,v)))
        self.assertEqual((p.hp,p.is_alive,p.invincible),(1,True,True))
        self.assertEqual(events,[(21,0),(39,None),(21,1)])
        pending[0].close()

    def test_heal_abort_does_not_add_completion_heal(self):
        p=Player(hp=1);g=heal_hp(lambda:100,.5,lambda:.1,lambda a:gain_health(p,a))
        next(g);hp=p.hp;g.close();self.assertEqual(p.hp,hp)

    def test_no_touch_native_up_down_held_order(self):
        calls=[]
        def read(name,value):
            def f():calls.append(name);return value
            return f
        self.assertTrue(no_touch(read('up',False),read('down',False),read('held',False),read('touch',0)))
        self.assertEqual(calls,['up','down','held','touch'])
