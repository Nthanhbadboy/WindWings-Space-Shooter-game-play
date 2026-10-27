import itertools
import json
import math
import unittest
from tools.verify.combat_coroutine_flow import OUT, build, RECIPES
from tools.verify.combat_coroutine_models import (
    attack10, attack11, attack17, control7_9, f32, move14, particle18,
    rank_rounds, shoot_children, shot_all13, sync12,
)


class CoroutineFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit=build();cls.rows={r['key']:r for r in cls.audit['coroutines']}

    def test_regeneration_and_25_semantic_source_walks(self):
        self.assertEqual(self.audit,json.loads(OUT.read_text()))
        self.assertEqual(set(self.rows),set(RECIPES))
        self.assertEqual(len(self.rows),25)
        self.assertTrue(all(r['state_writes'] and r['current_writes'] for r in self.rows.values()))

    def test_all_three_computed_branches_have_pinned_byte_targets(self):
        resolved={k:r['resolved_computed_dispatch'] for k,r in self.rows.items() if r['resolved_computed_dispatch']}
        self.assertEqual(len(resolved),3)
        seven=resolved['7.ControlMainCannonBullet'][0]['states']
        self.assertEqual(seven,{'0':'0x14b6314','1':'0x14b632c','2':'0x14b652c','3':'0x14b6308','4':'0x14b6308'})
        self.assertNotEqual(seven['0'],seven['2'])  # initial attack != post-attack delay
        six=resolved['6.ControlMainCannonBullet'][0]['states']
        self.assertEqual(six['2'],'0x14b3e2c');self.assertEqual(six['3'],'0x14b3e3c')

    def test_14_wait_ctor_sites_still_accounted_for(self):
        sites=[c for r in self.rows.values() for c in r['calls'] if c['target']=='0x2786508']
        self.assertEqual(len(sites),14)

    def test_18_particle_api_not_projectile_spawn(self):
        r=self.rows['18.IESpawnHeart'];targets={c['target'] for c in r['calls']}
        self.assertIn('0x27c2208',targets);self.assertIn('0x27c2564',targets)
        self.assertNotIn('0x123a9fc',targets);self.assertNotIn('0x11881d8',targets)
        self.assertFalse(r['indirect_calls'])
        self.assertEqual(list(itertools.islice(particle18(),8)),[
            ('set_rate_over_distance',2.0),('wait',0.5),('set_rate_over_distance',0.0),('wait',1.0)]*2)

    def test_10_rank_round_counts_and_last_wait(self):
        self.assertEqual([rank_rounds(i) for i in (1,2,3,4,5)],[1,1,2,3,3])
        self.assertEqual(len(list(attack10(4))),6)
        self.assertEqual(list(attack10(3))[-1],('wait',0.25))

    def test_11_checks_deadline_before_emission_and_stops_at_equality(self):
        times=iter([0.0,0.0,f32(0.4)])
        events=list(attack11(2,lambda:next(times)))
        self.assertEqual(events,[('barrel_descriptor_dispatch',i) for i in range(3)]+[('wait',f32(0.04))])
        times=iter([0.0,1.0]);self.assertEqual(list(attack11(3,lambda:next(times))),[])

    def test_12_wait_before_list_guard_and_no_repeated_wait(self):
        self.assertEqual(list(sync12(lambda:False)),[('wait',f32(0.2))])
        self.assertEqual(list(sync12(lambda:True)),[('wait',f32(0.2)),('side_dependent_sync_dispatch',None)])

    def test_13_pair_count_and_capped_wait(self):
        events=list(shot_all13(3,0.6,6.0))
        self.assertEqual(sum(e[0]=='barrel_dispatch' for e in events),6)
        self.assertEqual([e[1] for e in events if e[0]=='wait'],[f32(0.05)]*3)
        self.assertEqual(list(shot_all13(0,0.6,6.0)),[])  # division is float, not Python ZeroDivisionError

    def test_14_callback_only_after_arrival_wait_resume_even_when_zero(self):
        distances=iter([1.0,0.5]);moves=[]
        g=move14(lambda:next(distances),moves.append,lambda:0.1,12.0,0.0)
        self.assertEqual(next(g),('frame',None));self.assertEqual(next(g),('wait',0.0))
        self.assertEqual(next(g),('required_callback',None))
        self.assertEqual(moves,[f32(1.2)])

    def test_17_wait_after_pairs_not_each_position(self):
        self.assertEqual(list(attack17(3)),[('position_dispatch',0),('position_dispatch',1),('wait',f32(0.2)),('position_dispatch',2),('frame',None)])
        for n in range(8):
            self.assertEqual(sum(e[0]=='wait' for e in attack17(n)),n//2)
            self.assertEqual(list(attack17(n))[-1],('frame',None))

    def test_17_empty_array_still_terminal_frame_yield(self):
        self.assertEqual(list(attack17(0)),[('frame',None)])

    def test_23_24_wait_denominator_childcount_not_number(self):
        seen=[];events=list(shoot_children(lambda:2,lambda i,n:seen.append((i,n)),lambda:0.6,99))
        self.assertEqual(seen,[(0,99),(1,99)])
        self.assertEqual([e[1] for e in events if e[0]=='wait'],[f32(0.3)]*2)
        self.assertEqual(events[-1],('wait',f32(0.3)))

    def test_23_24_count_reread_after_helper_can_change(self):
        count=[2]
        def emit(i,number):count[0]=4 if i==0 else 0
        events=list(shoot_children(lambda:count[0],emit,lambda:1.0,7))
        waits=[e[1] for e in events if e[0]=='wait']
        self.assertEqual(waits[0],0.25);self.assertTrue(math.isinf(waits[1]))

    def test_23_24_no_children_no_wait_or_helper(self):
        self.assertEqual(list(shoot_children(lambda:0,lambda *_:self.fail('unexpected emission'),lambda:1.0,2)),[])

    def test_7_9_delay_follows_attack_wait_not_initial(self):
        attack=iter([False,True]);back=iter([False,True]);events=[]
        g=control7_9(lambda:next(attack),lambda:next(back),0.2,lambda:events.append('pool'),lambda:events.append('ended'))
        self.assertEqual(list(g),[('frame',None),('wait',f32(0.35)),('wait',0.2),('frame',None)])
        self.assertEqual(events,['pool','ended'])

    def test_7_9_nonpositive_delay_skipped_but_attack_wait_not_skipped(self):
        self.assertEqual(list(control7_9(lambda:True,lambda:True,0.0,lambda:None,lambda:None)),[('wait',f32(0.35))])

    def test_scale_and_saw_helpers_are_not_timed_emitter_loops(self):
        keys=[k for k in self.rows if 'IEUpdateRange' in k or 'SawAppear' in k or 'SawHide' in k]
        self.assertEqual(len(keys),6)
        for k in keys:
            self.assertNotIn('0x2786508',{c['target'] for c in self.rows[k]['calls']})
            self.assertIn(self.rows[k]['role'],('scale_animation','one_frame_saw_setup'))

    def test_rotation_uses_time_scale_not_delta_time(self):
        targets={c['target'] for c in self.rows['17.RotateClamp']['calls']}
        self.assertIn('0x2786eb0',targets);self.assertNotIn('0x2786de8',targets)

    def test_literal_width_and_negative_slowdown_are_pinned(self):
        cells={c['va']:c for c in self.audit['literal_cells']}
        self.assertEqual(cells['0x757918']['f32'],[f32(0.04),35.0])
        self.assertEqual(cells['0x756fd0']['f32'],[f32(-0.08)])
        self.assertEqual(cells['0x7796b0']['f32'],[6.0,7.0,f32(0.1),f32(0.1)])

    def test_iterator_stack_spill_dominance_is_checked_not_guessed(self):
        proof=self.rows['23.IEMainCannonAttack']['iterator_spill_proofs']
        self.assertEqual(len(proof),1)
        self.assertTrue(proof[0]['save_dominates_restore'])
        self.assertTrue(proof[0]['no_intervening_sp_use'])
        self.assertTrue(self.rows['23.IEMainCannonAttack']['current_writes'])

    def test_factory_arguments_are_copied_and_uncalled_factory_not_invented(self):
        fs=self.audit['factory_parameter_bindings']
        self.assertEqual(len(fs),7)
        nine=next(f for f in fs if f['implementation']=='Player_Attack_9')
        self.assertEqual(nine['factory'],'ControlMainCannonBullet')
        self.assertEqual(nine['direct_callers'],[])
        seven=next(f for f in fs if f['implementation']=='Player_Attack_7')
        self.assertTrue(seven['direct_callers'])

    def test_delegated_classes_are_now_exported_and_all_method_spans_validated(self):
        cs=self.audit['delegated_classes']
        self.assertEqual(len(cs),4)
        self.assertEqual(sum(len(c['methods']) for c in cs),30)
        self.assertEqual(sum(m['name']=='MoveNext' for c in cs for m in c['methods']),2)

    def test_clone_stop_and_pool_have_different_waits(self):
        from tools.verify.combat_coroutine_models import clone9_cleanup
        self.assertEqual(list(clone9_cleanup(4.0)),[('wait',4.0),('stop_attack',None),('wait',f32(0.34)),('pool_clone',None)])
        cells={c['va']:c['f32'] for c in self.audit['delegated_literal_cells']}
        self.assertEqual(cells['0x756aa4'],[f32(0.34)])
        self.assertEqual(cells['0x7581d0'],[f32(0.15),18.0])
        self.assertEqual(cells['0x7572e0'],[2.0,1.0])

    def test_pumpkin_strict_activation_and_expiry_then_laser_helper(self):
        from tools.verify.combat_coroutine_models import pumpkin_window_step
        at=pumpkin_window_step(1.0,4.0,9.0,False,1.0,0.0)
        self.assertFalse(at['active'])
        activated=pumpkin_window_step(1.1,4.0,9.0,False,1.0,0.0)
        self.assertTrue(activated['active']);self.assertNotIn('laser_helper',activated['events'])
        expired=pumpkin_window_step(3.1,4.0,9.0,True,1.0,3.0)
        self.assertFalse(expired['active']);self.assertIn('laser_helper',expired['events'])

    def test_pumpkin_timeout_callback_precedes_hide_and_no_frame(self):
        from tools.verify.combat_coroutine_models import pumpkin_window_step
        state=pumpkin_window_step(4.0,4.0,0.0,True,0.0,9.0)
        self.assertEqual(state['events'],['optional_callback','hide'])
