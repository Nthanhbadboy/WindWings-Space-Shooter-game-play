import itertools,json,unittest
from tools.verify.damage_receiver_models import Player
from tools.verify.player_lifecycle_models import Lifecycle,normal_extra_life,gain_health
from tools.verify.player_shield_models import Shields,ZoneState,shield_callback,reborn_done_flag_block,set_zone_invisible
from tools.verify.player_shield_flow import OUT,build


class ShieldTests(unittest.TestCase):
    def test_regeneration(self):self.assertEqual(build(),json.loads(OUT.read_text()))

    def test_literal_and_packed_initializer(self):
        r=build();self.assertEqual(r['invoke_target']['utf8'],'RebornDone')
        self.assertEqual(r['invoke_target']['index'],7049)
        self.assertEqual((r['packed_static_initializer']['TimeResetInvincible'],r['packed_static_initializer']['TimeCanActiveInvincible']),(3,10))

    def test_field_erratum(self):
        ff={(r['class'],r['offset']):r['name'] for r in build()['typed_fields']}
        self.assertEqual(ff['Player_Physics','0x90'],'activeHitEnemey')
        self.assertEqual(ff['Player_Controller','0x48'],'playerTalentScript')
        self.assertEqual(ff['Player_Talent','0x20'],'reborning')

    def test_all_reborn_flag_combinations_preserve_vs_clear(self):
        for skill,d101,d103,onehit,initial in itertools.product((False,True),repeat=5):
            with self.subTest(skill=skill,d101=d101,d103=d103,onehit=onehit,initial=initial):
                p=Player(invincible=initial);s=Lifecycle();f=Shields(skill,d101,d103,onehit);calls=[]
                result=reborn_done_flag_block(p,s,f,restricted_cleanup=lambda:calls.append('cleanup'))
                self.assertEqual(p.invincible,initial if any((skill,d101,d103,onehit)) else False)
                self.assertEqual(s.hit_enemy_enabled,not any((skill,d101,d103)))
                self.assertEqual(calls,['cleanup'] if skill or d101 else [])
                self.assertEqual(result,{'talent_reborning_write':False if skill or d101 else None})

    def test_all_shield_callback_combinations(self):
        for bits in itertools.product((False,True),repeat=4):
            for kind,active,initial in itertools.product(('skill','droid101','droid103','onehit'),(False,True),(False,True)):
                f=Shields(*bits);p=Player(invincible=initial);s=Lifecycle()
                shield_callback(p,s,f,kind,active)
                aggregate=f.skill or f.droid101 or f.droid103
                self.assertEqual(p.invincible,initial if kind=='onehit' else bool(aggregate))
                self.assertEqual(s.hit_enemy_enabled,not aggregate)
                self.assertEqual(getattr(f,kind),active)

    def test_shield_callback_does_not_refcount_rebirth(self):
        p=Player();s=Lifecycle();f=Shields()
        g=normal_extra_life(p,s,gain=lambda a:gain_health(p,a),no_touch_predicate=lambda:True,schedule_done=lambda:None,start_heal=lambda _:None)
        next(g);self.assertTrue(p.invincible)
        shield_callback(p,s,f,'skill',False)
        self.assertFalse(p.invincible);self.assertTrue(s.hit_enemy_enabled);g.close()

    def test_onehit_only_reborn_preserves_false_not_force_true(self):
        p=Player(invincible=False);s=Lifecycle();f=Shields(onehit=True)
        reborn_done_flag_block(p,s,f)
        self.assertFalse(p.invincible);self.assertTrue(s.hit_enemy_enabled)

    def test_restricted_cleanup_runs_after_contact_flag_write(self):
        p=Player(invincible=True);s=Lifecycle()
        def cleanup():
            self.assertFalse(s.hit_enemy_enabled)
            raise RuntimeError('helper')
        with self.assertRaises(RuntimeError):reborn_done_flag_block(p,s,Shields(droid101=True),restricted_cleanup=cleanup)
        self.assertFalse(s.hit_enemy_enabled);self.assertTrue(p.invincible)

    def test_onehit_callback_leaves_health_invincible_unchanged(self):
        p=Player(invincible=True);s=Lifecycle();shield_callback(p,s,Shields(),'onehit',False)
        self.assertTrue(p.invincible);self.assertTrue(s.hit_enemy_enabled)

    def test_reborn_root_does_not_directly_replay_zone_visibility(self):
        m=next(m for m in build()['methods'] if m['method']=='RebornDone')
        self.assertNotIn('#0x14c2e68',[r['args'] for r in m['calls']])


class ZoneTests(unittest.TestCase):
    def apply(self,s,zone,invisible,heal=False,reborn=False):
        calls=[]
        set_zone_invisible(s,zone,invisible,heal,lambda:reborn,start_heal=lambda:calls.append('start') or 'cor',stop_heal=lambda cor:calls.append(('stop',cor)),display=lambda show:calls.append(('display',show)))
        return calls

    def test_heal_setup_precedes_reborn_guard(self):
        s=ZoneState(set());self.assertEqual(self.apply(s,'A',True,True,True),['start'])
        self.assertTrue(s.healing);self.assertEqual(s.zones,{'A'})
        self.assertFalse(s.health_invisible);self.assertFalse(s.physics_invisible)

    def test_leaving_during_reborn_updates_list_but_skips_stop(self):
        s=ZoneState({'A'},True,'old',True,True)
        self.assertEqual(self.apply(s,'A',False,reborn=True),[])
        self.assertEqual(s.zones,set());self.assertTrue(s.healing);self.assertTrue(s.health_invisible)

    def test_multiple_zones_not_aggregate_visibility(self):
        s=ZoneState(set());self.apply(s,'A',True);self.apply(s,'B',True)
        self.apply(s,'A',False)
        self.assertEqual(s.zones,{'B'});self.assertFalse(s.health_invisible);self.assertFalse(s.physics_invisible)

    def test_enter_twice_no_duplicate_zone_or_restart(self):
        s=ZoneState(set());self.apply(s,'A',True,True)
        self.assertEqual(self.apply(s,'A',True,True),[('display',False)])
        self.assertEqual(s.zones,{'A'})

    def test_enter_without_heal_does_not_stop_previous_heal(self):
        s=ZoneState({'A'},True,'cor');calls=self.apply(s,'B',True)
        self.assertNotIn(('stop','cor'),calls);self.assertTrue(s.healing)

    def test_exit_nonmember_still_clears_and_stops(self):
        s=ZoneState({'A'},True,'cor',True,True)
        self.assertEqual(self.apply(s,'B',False),[('display',True),('stop','cor')])
        self.assertFalse(s.healing);self.assertEqual(s.heal_cor,'cor');self.assertEqual(s.zones,{'A'})

    def test_stale_coroutine_stop_before_new_start(self):
        s=ZoneState(set(),False,'stale')
        self.assertEqual(self.apply(s,'A',True,True),[('stop','stale'),'start',('display',False)])

    def test_reborn_guard_reread_after_start_helper(self):
        s=ZoneState(set());live={'reborn':False};seen=[]
        def start():live['reborn']=True;return 'cor'
        set_zone_invisible(s,'A',True,True,lambda:live['reborn'],start_heal=start,stop_heal=lambda _:None,display=seen.append)
        self.assertTrue(s.healing);self.assertFalse(s.health_invisible);self.assertEqual(seen,[])
