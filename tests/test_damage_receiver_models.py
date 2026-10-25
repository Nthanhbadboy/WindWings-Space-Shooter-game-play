import unittest
from tools.verify.enemy_damage_model import HpRef, Receiver, calculate_with_callbacks
from tools.verify.damage_receiver_models import (Damager, Enemy, Player, base_enemy_destroy_zero,
    enemy_take_damage, player_damage_amount, player_take_damage, f32)


class EnemyCallbackTests(unittest.TestCase):
    def test_hit_runs_for_zero_and_negative_requested_damage(self):
        for damage, hp in [(0, 100), (-20, 120)]:
            calls=[]; ref=HpRef(100); r=Receiver(hit_callback=lambda:calls.append('hit'),hit_damage_callback=calls.append)
            calculate_with_callbacks(r,ref,damage)
            self.assertEqual(ref.hp,hp);self.assertEqual(calls,['hit'])

    def test_invincible_and_dead_skip_both_callbacks(self):
        for hp, inv in [(100,True),(0,False),(-1,False)]:
            r=Receiver(no_damage=inv,hit_callback=lambda:self.fail('must not call'))
            self.assertEqual(calculate_with_callbacks(r,HpRef(hp),20),[])

    def test_ignore_invincible_still_damage_and_callbacks(self):
        calls=[];ref=HpRef(100)
        calculate_with_callbacks(Receiver(no_damage=True,hit_damage_callback=calls.append),ref,20,True)
        self.assertEqual((ref.hp,calls),(80,[20]))

    def test_hit_callback_can_heal_and_suppress_loss_callback(self):
        ref=HpRef(100)
        r=Receiver(hit_callback=lambda:setattr(ref,'hp',120),hit_damage_callback=lambda _:self.fail('no positive delta'))
        calculate_with_callbacks(r,ref,200);self.assertEqual(ref.hp,120)

    def test_hit_callback_can_replace_or_clear_second_callback(self):
        for clear in [False,True]:
            ref=HpRef(100);calls=[];r=Receiver(hit_damage_callback=lambda _:self.fail('stale delegate'))
            def hit():r.hit_damage_callback=None if clear else calls.append;ref.hp=10
            r.hit_callback=hit;calculate_with_callbacks(r,ref,20)
            self.assertEqual(calls,[] if clear else [90])

    def test_second_callback_changes_final_hp_after_loss_argument(self):
        ref=HpRef(100);seen=[]
        def loss(d):seen.append(d);ref.hp=200
        calculate_with_callbacks(Receiver(hit_damage_callback=loss),ref,200)
        self.assertEqual((ref.hp,seen),(200,[100]))

    def test_ref_capture_survives_outer_data_replacement(self):
        old=HpRef(100);enemy=Enemy(old);loss=[]
        enemy.receiver.hit_callback=lambda:setattr(enemy,'data',HpRef(50))
        enemy.receiver.hit_damage_callback=loss.append
        t=enemy_take_damage(enemy,Damager(200))
        self.assertEqual((old.hp,enemy.data.hp,loss),(0,50,[100]))
        self.assertIn(('survive',None),t);self.assertNotIn(('destroy_dispatch',0),t)

    def test_display_hit_precedes_controller_gates(self):
        for hp,can_attack in [(0,True),(100,False)]:
            calls=[];enemy=Enemy(HpRef(hp),can_attack=can_attack)
            self.assertEqual(enemy_take_damage(enemy,Damager(20),on_hit=lambda:calls.append(1)),[('display_on_hit',None)])
            self.assertEqual(calls,[1])

    def test_no_damage_does_not_skip_hpbar_or_survival_abilities(self):
        enemy=Enemy(HpRef(100),Receiver(no_damage=True))
        t=enemy_take_damage(enemy,Damager(20),level=lambda n:1 if n==31 else 0,coefficient=lambda _:10)
        self.assertIn(('update_hp_bar',None),t);self.assertIn(('stun',3.0),t)
        self.assertEqual(enemy.data.hp,100)

    def test_null_damager_logs_then_updates_hpbar(self):
        t=enemy_take_damage(Enemy(HpRef(100)),None)
        self.assertEqual(t,[('display_on_hit',None),('log_error',None),('update_hp_bar',None),('survive',None)])

    def test_dead_callback_revive_is_decided_before_controller_death(self):
        enemy=Enemy(HpRef(100));enemy.receiver.hit_damage_callback=lambda _:setattr(enemy.data,'hp',1)
        t=enemy_take_damage(enemy,Damager(500))
        self.assertIn(('survive',None),t);self.assertFalse(enemy.invisible)

    def test_kill_callback_reloaded_after_destroy_dispatch(self):
        calls=[];d=Damager(500,lambda:self.fail('stale'))
        def destroy():calls.append('destroy');d.kill_event=lambda:calls.append('new_kill')
        enemy=Enemy(HpRef(100));t=enemy_take_damage(enemy,d,destroy=destroy)
        self.assertEqual(calls,['destroy','new_kill']);self.assertTrue(enemy.invisible);self.assertFalse(enemy.can_move)
        self.assertLess(t.index(('update_hp_bar',None)),t.index(('destroy_dispatch',0)))

    def test_base_death_on_destroyed_null_still_pools_but_skips_death_event(self):
        self.assertEqual(base_enemy_destroy_zero(),['pool','event_79_pool_enemy'])

    def test_base_death_on_dead_can_replace_on_destroyed(self):
        calls=[];slot=[None]
        def dead():calls.append('dead');slot[0]=lambda:calls.append('destroyed')
        t=base_enemy_destroy_zero(on_dead=dead,on_destroyed=lambda:slot[0],pool=lambda:calls.append('pool'))
        self.assertEqual(calls,['dead','destroyed','pool']);self.assertEqual(t.count('event_79_pool_enemy'),2)
        self.assertEqual(t.index('event_19_enemy_die'),t.index('event_79_pool_enemy')-1)

    def test_stun_equality_and_burn_copy_requested_not_hp_loss(self):
        d=Damager(20);copied=[]
        t=enemy_take_damage(Enemy(HpRef(100),Receiver(armor=100)),d,
            level=lambda _:1,coefficient=lambda _:10,random_int=lambda:10,
            random_float=lambda:10,burn=lambda *args:copied.append(args))
        self.assertIn(('stun',3.0),t);self.assertEqual(copied[0][0].damage,20)
        self.assertIsNot(copied[0][0],d);self.assertEqual(copied[0][1:],(f32(.4),6.0))

    def test_callback_exception_aborts_later_hpbar_and_kill(self):
        calls=[]
        def explode():raise RuntimeError('fixture callback')
        with self.assertRaises(RuntimeError):
            enemy_take_damage(Enemy(HpRef(100),Receiver(hit_callback=explode)),Damager(500,lambda:calls.append('kill')))
        self.assertEqual(calls,[])


class PlayerReceiverTests(unittest.TestCase):
    def test_two_truncations_not_one(self):
        self.assertEqual(player_damage_amount(3.8,0,0,.2,0),(3,2))
        self.assertEqual(int(f32(f32(3.8)*f32(.8))),3)

    def test_negative_damage_heals_without_start_hp_cap(self):
        p=Player();t=player_take_damage(p,Damager(-20))
        self.assertEqual(p.hp,120);self.assertIn(('event',39),t)

    def test_all_entry_gates(self):
        for kwargs,d in [({'hp':0},Damager(5)),({'invisible':True},Damager(5)),({'victory':True},Damager(5)),({},None)]:
            self.assertEqual(player_take_damage(Player(**kwargs),d),[])

    def test_expired_immune_deadline_skips_hit_and_uses_two_time_reads(self):
        p=Player();times=iter([1,2]);t=player_take_damage(p,Damager(5),clock=lambda:next(times),immune_time=lambda:.5)
        self.assertEqual((p.hp,p.immune_deadline),(100,2.5));self.assertEqual(t,[('immune_deadline_store',2.5)])

    def test_equal_or_future_deadline_allows_damage(self):
        for deadline in [0,1]:
            p=Player(immune_deadline=deadline);player_take_damage(p,Damager(5));self.assertEqual(p.hp,95)

    def test_ignore_does_not_bypass_attack_invisibility(self):
        self.assertEqual(player_take_damage(Player(attack_invisible=True),Damager(10),ignore=True),[])

    def test_dodge_precedes_shield_and_strict_equality_is_not_miss(self):
        for roll,shield,hp in [(9,True,100),(10,False,100)]:
            p=Player(shield=True)
            t=player_take_damage(p,Damager(20),level=lambda n:int(n==8),coefficient=lambda _:10,random_float=lambda:roll)
            self.assertEqual((p.shield,p.hp),(shield,hp));self.assertEqual(t[0][0],'miss' if roll==9 else 'shield_clear')

    def test_low_hp_bonus_strict_below_point_three_and_cap_ninety(self):
        for hp,missed in [(29,True),(30,False)]:
            p=Player(hp=hp)
            t=player_take_damage(p,Damager(1),level=lambda n:int(n in (8,22)),coefficient=lambda n:10 if n==8 else 100,
                random_float=lambda:89)
            self.assertEqual(('miss',None) in t,missed)
        p=Player(hp=29)
        t=player_take_damage(p,Damager(1),level=lambda n:int(n in (8,22)),coefficient=lambda _:100,random_float=lambda:90)
        self.assertNotIn(('miss',None),t)

    def test_shield_clear_visible_to_callback_and_ignore_does_not_bypass(self):
        p=Player(shield=True);seen=[];p.destroy_shield=lambda:seen.append(p.shield)
        t=player_take_damage(p,Damager(500),ignore=True)
        self.assertEqual((p.hp,seen),(100,[False]));self.assertFalse(any(x[0]=='event' for x in t))

    def test_ability30_invincible_heal_and_equality(self):
        p=Player(invincible=True);seen=[]
        t=player_take_damage(p,Damager(500),level=lambda n:2 if n==30 else 0,
            coefficient=lambda n:10 if n==30 else 5,random_float=lambda:20,heal_start_hp=lambda:200,heal=seen.append)
        self.assertEqual(seen,[20]);self.assertEqual(t,[('heal_interface',20)])

    def test_ability35_before_damage_reload_and_clear_deadline_strict(self):
        p=Player(clear_deadline=0,immune_deadline=9);d=Damager(5)
        t=player_take_damage(p,d,clock=lambda:1,level=lambda n:int(n in (28,35)),ability35=lambda:setattr(d,'damage',20))
        self.assertEqual(p.hp,80);self.assertEqual(p.clear_deadline,2)
        self.assertLess(t.index(('ability35_virtual',True)),t.index(('hp_store',80)))

    def test_post21_can_revive_and_payload_stays_boxed_then_post39(self):
        p=Player();seen=[]
        def post(e,payload):
            seen.append((e,payload,p.hp))
            if e==21:p.hp=50
        t=player_take_damage(p,Damager(500),post=post)
        self.assertEqual(seen,[(21,0,0),(39,None,50)]);self.assertIn(('set_attack_invisible',None),t)
        self.assertTrue(p.is_alive)

    def test_post39_can_kill_before_final_hp_reread(self):
        p=Player();seen=[]
        def post(e,payload):
            if e==39:p.hp=0
            seen.append(e)
        t=player_take_damage(p,Damager(1),post=post)
        self.assertFalse(p.is_alive);self.assertEqual(seen,[21,39,18]);self.assertIn(('on_die',None),t)

    def test_pvp_life_decrement_before_extra_life_no_die_event(self):
        p=Player(mode=6,pvp_life=2);seen=[];p.on_extra_life=lambda:seen.append(p.pvp_life)
        t=player_take_damage(p,Damager(500))
        self.assertEqual(seen,[1]);self.assertTrue(p.is_alive);self.assertEqual(p.hp,0)
        self.assertNotIn(('event',18),t)

    def test_ability16_uses_reborn_counter_and_optional_callback_can_be_null(self):
        p=Player(reborn_now=0)
        t=player_take_damage(p,Damager(500),level=lambda n:int(n==16))
        self.assertEqual(p.reborn_now,1);self.assertEqual(p.pvp_life,-1);self.assertTrue(p.is_alive)
        self.assertNotIn(('on_die',None),t)
        p=Player(reborn_now=1)
        t=player_take_damage(p,Damager(500),level=lambda n:int(n==16))
        self.assertFalse(p.is_alive);self.assertIn(('event',18),t)

    def test_is_alive_false_before_on_die_and_cleanup_then_event18(self):
        p=Player();seen=[]
        player_take_damage(p,Damager(500),on_die=lambda:seen.append(('die',p.is_alive)),
            cleanup=lambda:seen.append(('cleanup',p.is_alive)),post=lambda e,_:seen.append((e,p.is_alive)))
        self.assertEqual(seen,[(21,True),(39,True),('die',False),('cleanup',False),(18,False)])

    def test_on_die_null_is_not_silently_ignored(self):
        p=Player()
        with self.assertRaises(ValueError):player_take_damage(p,Damager(500),on_die=None)
        self.assertFalse(p.is_alive)

    def test_out_of_range_model_not_claimed_native_reject(self):
        with self.assertRaises(ValueError):player_damage_amount(2**32,0,0,0,0)
        with self.assertRaises(ValueError):player_damage_amount(float('inf'),0,0,0,0)


class DeathOverrideTests(unittest.TestCase):
    def test_delayed_uses_live_waituntil_predicate_not_two_second_timer(self):
        from tools.verify.damage_receiver_models import delayed_enemy_destroy
        events=[];slot=[lambda:False]
        g=delayed_enemy_destroy(lambda:events.append('start'),lambda:slot[0],lambda:events.append('base'))
        kind,predicate=next(g);self.assertEqual(kind,'wait_until');self.assertFalse(predicate())
        self.assertEqual(events,['start']);slot[0]=lambda:True;self.assertTrue(predicate())
        with self.assertRaises(StopIteration):next(g)
        self.assertEqual(events,['start','base'])

    def test_delayed_null_condition_is_not_false(self):
        from tools.verify.damage_receiver_models import delayed_enemy_destroy
        _,predicate=next(delayed_enemy_destroy(None,lambda:None,lambda:None))
        with self.assertRaises(ValueError):predicate()

    def test_mb_three_waits_then_death_events_without_pool(self):
        from tools.verify.damage_receiver_models import mb_die_effect
        events=[]
        g=mb_die_effect(lambda:events.append('effect'),lambda:events.append('hide'),
            lambda:events.append('burst'),lambda:events.append('destroyed'),events.append)
        self.assertEqual(next(g),('wait',1));self.assertEqual(events,['effect'])
        self.assertEqual(next(g),('wait',1));self.assertEqual(events,['effect','hide'])
        self.assertEqual(next(g),('wait',1));self.assertEqual(events,['effect','hide','burst'])
        with self.assertRaises(StopIteration):next(g)
        self.assertEqual(events,['effect','hide','burst','destroyed',19,79])

    def test_delayed_dispatch_returns_then_kill_before_deferred_base(self):
        from tools.verify.damage_receiver_models import delayed_enemy_destroy
        events=[];pending=[]
        def dispatch():
            g=delayed_enemy_destroy(None,lambda:lambda:True,lambda:events.append('base'))
            next(g);pending.append(g)
        enemy_take_damage(Enemy(HpRef(1)),Damager(5,lambda:events.append('kill')),destroy=dispatch)
        self.assertEqual(events,['kill'])
        with self.assertRaises(StopIteration):next(pending[0])
        self.assertEqual(events,['kill','base'])

    def test_immune_interval_all_tech_boundaries(self):
        from tools.verify.damage_receiver_models import immune_interval
        self.assertEqual([immune_interval(i) for i in range(1,12)],
                         [50,50,50,45,45,40,35,35,30,25,25])
        self.assertEqual(immune_interval(0),f32(3.4028234663852886e38))


class DeathBlastTests(unittest.TestCase):
    def test_same_receiver_multiple_colliders_not_deduplicated(self):
        from tools.verify.damage_receiver_models import death_blast
        calls=[]
        hits=death_blast(1,100,lambda:self.fail('no random'),lambda:7,lambda r,m:['c1','c2'],1,
            get_damageable=lambda _:'same',take_damage=lambda *a:calls.append(a))
        self.assertEqual(len(calls),2);self.assertEqual([x[1].damage for x in hits],[7,7])
        self.assertTrue(all(x[1].kill_event is None for x in hits));self.assertIsNot(hits[0][1],hits[1][1])
        self.assertTrue(all(not x[2] for x in calls))

    def test_chance_equality_pass_and_layer_recheck(self):
        from tools.verify.damage_receiver_models import death_blast
        hits=death_blast(1,10,lambda:10,lambda:5,lambda r,m:[0,1],1,layer=lambda c:c)
        self.assertEqual(len(hits),1);self.assertEqual(hits[0][0],0)
        self.assertEqual(death_blast(1,10,lambda:11,lambda:5,lambda *_:self.fail('no query'),1),[])

    def test_health_object_required_not_health_is_alive_predicate(self):
        from tools.verify.damage_receiver_models import death_blast
        class Health:
            def IsAlive(self):raise AssertionError('native does not call this')
        hits=death_blast(1,100,lambda:0,lambda:5,lambda *_:['a'],1,get_health=lambda _:Health())
        self.assertEqual(len(hits),1)
