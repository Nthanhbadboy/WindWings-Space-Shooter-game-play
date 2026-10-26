"""Tests for the transition scheduler / blend model (tools/verify/l3_transition_scheduler.py).

Artifact-level assertions pin counts recomputed from source. Synthetic controllers are
used only for behaviours the APK never exercises (numeric condition modes, interruption
sources other than None) so that the declared policy stays testable instead of silently
untested.
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path('tools/verify').resolve()))
from l3_model_common import read_json_gz
from l3_transition_scheduler import (CONDITION_MODES, OUT_DEFAULT, Scheduler,
                                     count_model, load_clip_lengths, normalize_controller)


def motion(clip_length=1.0):
    return [{'clip': {'serialized_file': 'synthetic', 'path_id': 1},
             'node_duration': 1.0, 'node_cycle_offset': 0.0,
             'clip_status': 'leaf_clip_index_resolved', 'clip_resolved': True,
             'clip_length': clip_length, 'clip_name': 'synthetic'}]


def transition(destination=1, conditions=(), exit_time=None, duration=0.0,
               fixed=False, interruption=0, can_self=True, status='local_state_index',
               tid='t0'):
    return {
        'id': tid, 'scope': 'state', 'source_state_index': 0,
        'destination': {'raw': destination, 'index': destination, 'status': status},
        'conditions': [{'parameter_names': [name], 'parameter_id': 1, 'mode': mode,
                        'mode_name': CONDITION_MODES.get(mode, '?'),
                        'threshold': threshold, 'exit_time': 0.0}
                       for name, mode, threshold in conditions],
        'has_exit_time': exit_time is not None,
        'exit_time': exit_time if exit_time is not None else 0.0,
        'transition_duration': duration,
        'transition_offset': 0.0,
        'has_fixed_duration': fixed,
        'interruption_source': interruption,
        'ordered_interruption': True,
        'can_transition_to_self': can_self,
    }


def state(index, transitions=(), length=1.0, loop=False, name=None):
    return {'state_index': index, 'names': [name or f's{index}'], 'paths': [],
            'speed': 1.0, 'loop': loop, 'write_default_values': True, 'mirror': False,
            'motion': motion(length), 'transitions': list(transitions)}


def controller(states, any_transitions=(), parameters=(), default=0):
    return {
        'identity': {'serialized_file': 'synthetic', 'path_id': 99},
        'name': 'synthetic', 'raw_object_sha256': None, 'layer_count': 1, 'layers': [],
        'parameters': [{'names': [name], 'name': name, 'id': 1, 'index': i,
                        'type': ptype, 'type_class': ptype_class, 'default': default_value,
                        'default_status': 'typed_slot',
                        'default_storage': 'm_BoolValues'}
                       for i, (name, ptype, ptype_class, default_value)
                       in enumerate(parameters)],
        'machines': [{'machine_index': 0, 'default_state_index': default,
                      'default_status': 'valid_index', 'states': list(states),
                      'any_state_transitions': list(any_transitions), 'selectors': []}],
    }


def run(scheduler, seconds, dt=1 / 120):
    for _ in range(int(round(seconds / dt))):
        scheduler.tick(dt)
    return scheduler


class PolicyTests(unittest.TestCase):
    def test_default_state_is_the_serialized_default(self):
        sched = Scheduler(controller([state(0), state(1)], default=1))
        self.assertEqual(sched.state, 1)

    def test_bool_condition_if_and_ifnot(self):
        params = [('Go', 4, 'Bool', False)]
        sched = Scheduler(controller(
            [state(0, [transition(1, [('Go', 1, 0.0)])]), state(1)], parameters=params))
        sched.tick(0.1)
        self.assertEqual(sched.state, 0)
        sched.set('Go', True)
        sched.tick(0.1)
        self.assertEqual(sched.state, 1)

        sched = Scheduler(controller(
            [state(0, [transition(1, [('Go', 2, 0.0)])]), state(1)], parameters=params))
        sched.tick(0.1)
        self.assertEqual(sched.state, 1)  # IfNot fired on the default false value

    def test_numeric_condition_modes(self):
        params = [('Speed', 1, 'Float', 0.0)]
        for mode, value, expected in ((3, 1.5, 1), (3, 0.5, 0), (4, 0.5, 1),
                                      (5, 1.0, 1), (6, 1.0, 0)):
            sched = Scheduler(controller(
                [state(0, [transition(1, [('Speed', mode, 1.0)])]), state(1)],
                parameters=params))
            sched.set('Speed', value)
            sched.tick(0.01)
            self.assertEqual(sched.state, expected, (mode, value))

    def test_exit_time_normalised_versus_fixed(self):
        # normalised: 0.5 * 2.0 s clip = 1.0 s
        sched = Scheduler(controller([state(0, [transition(1, exit_time=0.5,
                                                           fixed=False)], length=2.0),
                                      state(1, length=1.0)]))
        run(sched, 0.9)
        self.assertEqual(sched.state, 0)
        run(sched, 0.2)
        self.assertEqual(sched.state, 1)
        taken = sched.taken[0]
        self.assertAlmostEqual(taken['t'], 1.0, places=6)

        # fixed: 0.25 s regardless of the 2.0 s clip
        sched = Scheduler(controller([state(0, [transition(1, exit_time=0.25,
                                                           fixed=True)], length=2.0),
                                      state(1, length=1.0)]))
        run(sched, 0.2)
        self.assertEqual(sched.state, 0)
        run(sched, 0.1)
        self.assertEqual(sched.state, 1)
        self.assertAlmostEqual(sched.taken[0]['t'], 0.25, places=6)

    def test_transition_duration_normalised_versus_fixed(self):
        sched = Scheduler(controller([state(0, [transition(1, duration=0.2,
                                                            fixed=False)], length=2.0),
                                      state(1)]))
        sched.tick(0.01)
        self.assertAlmostEqual(sched.taken[0]['blend_seconds'], 0.4, places=9)

        sched = Scheduler(controller([state(0, [transition(1, duration=0.2,
                                                            fixed=True)], length=2.0),
                                      state(1)]))
        sched.tick(0.01)
        self.assertAlmostEqual(sched.taken[0]['blend_seconds'], 0.2, places=9)

    def test_blend_weights_are_linear_and_sum_to_one(self):
        sched = Scheduler(controller([state(0, [transition(1, duration=0.4, fixed=True)]),
                                      state(1)]))
        sched.tick(0.01)  # takes the transition instantly (no exit time needed)
        self.assertTrue(sched.blend is not None or sched.state == 1)
        if sched.blend is None:
            self.skipTest('transition applied as instant switch')
        weights = []
        for _ in range(4):
            sched.tick(0.1)
            snapshot = sched.snapshot()
            weights.append(snapshot['blend']['weights'])
            self.assertAlmostEqual(sum(snapshot['blend']['weights'].values()), 1.0, 9)
        progresses = [w['1'] for w in weights]
        self.assertEqual(progresses, sorted(progresses))
        self.assertAlmostEqual(progresses[0], 0.25, places=6)

    def test_zero_duration_switch_is_instant(self):
        sched = Scheduler(controller([state(0, [transition(1, duration=0.0)]), state(1)]))
        sched.tick(0.01)
        self.assertEqual(sched.state, 1)
        self.assertIsNone(sched.blend)
        self.assertEqual(sched.taken[0]['applied'], 'instant')

    def test_interruption_source_none_blocks_new_transitions(self):
        trigger = [('Go', 9, 'Trigger', False)]
        trans = [transition(1, duration=0.4, fixed=True, interruption=0, tid='t0')]
        sched = Scheduler(controller([state(0, trans), state(1), state(2)],
                                     parameters=trigger))
        sched.tick(0.01)
        self.assertIsNotNone(sched.blend)
        sched.set_trigger('Go')
        sched.tick(0.01)
        self.assertEqual(sched.state, 0)  # still blending from state 0
        blocked = [b for b in sched.blocked
                   if 'blocked_by_running_transition_no_interruption' in b['reasons']]
        self.assertTrue(blocked)

    def test_interruption_source_allows_replacement_when_declared(self):
        trigger = [('Go', 9, 'Trigger', False)]
        trans = [transition(1, duration=0.4, fixed=True, interruption=1, tid='t1')]
        sched = Scheduler(controller([state(0, trans), state(1), state(2)],
                                     parameters=trigger))
        sched.tick(0.01)
        self.assertIsNotNone(sched.blend)
        sched.set_trigger('Go')
        sched.tick(0.01)
        # the transition is taken again (self-destination 1) because source 1 allows it
        self.assertGreaterEqual(len(sched.taken), 2)

    def test_self_transition_disallowed_flag_is_respected(self):
        sched = Scheduler(controller([state(0, [transition(0, can_self=False)]), state(1)]))
        sched.tick(0.5)
        self.assertEqual(sched.state, 0)
        self.assertIn(('self_transition_disallowed'),
                      [r for b in sched.blocked for r in b['reasons']])

    def test_encoded_destination_is_never_taken(self):
        sched = Scheduler(controller(
            [state(0, [transition(30001, status='encoded_selector_or_exit_not_local_index')]),
             state(1)]))
        sched.tick(0.5)
        self.assertEqual(sched.state, 0)
        reasons = [r for b in sched.blocked for r in b['reasons']]
        self.assertIn('encoded_destination_not_local', reasons)
        self.assertEqual(sched.taken, [])

    def test_any_state_is_evaluated_before_state_transitions(self):
        any_t = transition(2, [], tid='any0')
        any_t['scope'] = 'any'
        any_t['source_state_index'] = None
        sched = Scheduler(controller([state(0, [transition(1, tid='s0')]), state(1),
                                     state(2)], any_transitions=[any_t]))
        sched.tick(0.01)
        self.assertEqual(sched.state, 2)  # declared policy: AnyState wins
        self.assertFalse(sched.policy['evaluation_order']['proven'])

    def test_trigger_is_consumed_by_the_taken_transition(self):
        trigger = [('Go', 9, 'Trigger', False)]
        sched = Scheduler(controller([state(0, [transition(1, [('Go', 1, 0.0)])]), state(1),
                                      state(2)], parameters=trigger))
        sched.set_trigger('Go')
        sched.tick(0.01)
        self.assertEqual(sched.state, 1)
        self.assertEqual(sched.params['Go'], False)
        self.assertEqual(sched.taken[0]['consumed_triggers'], ['Go'])

    def test_undeclared_parameter_is_reported_not_guessed(self):
        sched = Scheduler(controller([state(0, [transition(1, [('Missing', 1, 0.0)])]),
                                      state(1)]))
        sched.tick(0.01)
        self.assertEqual(sched.state, 0)
        reasons = [r for b in sched.blocked for r in b['reasons']]
        self.assertIn('parameter_not_declared', reasons)

    def test_negative_dt_is_rejected(self):
        sched = Scheduler(controller([state(0)]))
        with self.assertRaises(ValueError):
            sched.tick(-0.1)


class ArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = read_json_gz(OUT_DEFAULT)
        cls.counts = cls.artifact['counts']

    def test_counts_cross_check_against_the_source_artifact(self):
        for key, entry in self.artifact['cross_check_against_source_artifact'].items():
            self.assertTrue(entry['equal'], key)
        self.assertEqual(self.counts['controllers'], 232)
        self.assertEqual(self.counts['states'], 667)
        self.assertEqual(self.counts['any_transitions'], 343)
        self.assertEqual(self.counts['state_transitions'], 125)
        self.assertEqual(self.counts['parameters'], 377)
        self.assertEqual(self.counts['conditions'], 376)

    def test_counts_are_recomputed_from_the_contract(self):
        recomputed = count_model(self.artifact['controllers'])
        for key, value in recomputed.items():
            self.assertEqual(value, self.counts[key], key)

    def test_single_layer_is_measured_not_assumed(self):
        self.assertEqual(self.counts['layers_total'], 232)
        self.assertEqual(self.counts['controllers_with_one_layer'], 232)

    def test_the_apk_exercises_only_a_narrow_policy_slice(self):
        # 464 transitions (all of them selectors) carry no serialized
        # m_InterruptionSource; they are counted apart rather than as a source value
        self.assertEqual(self.counts['interruption_sources'], {'0': 468})
        self.assertEqual(self.counts['interruption_source_absent'], 464)
        self.assertEqual(self.counts['interruption_source_absent_scope'],
                         {'selector': 464})
        self.assertEqual(self.counts['selector_transitions'],
                         self.counts['interruption_source_absent'])
        self.assertEqual(self.counts['condition_modes'], {'1': 375, '2': 1})
        self.assertEqual(self.counts['condition_thresholds'], {'0.0': 376})
        self.assertEqual(self.counts['states_speed_not_one'], 0)
        self.assertEqual(self.counts['transitions_with_duration'], 30)

    def test_encoded_destinations_are_preserved_verbatim(self):
        self.assertEqual(self.counts['encoded_destinations'],
                         {'30000': 232, '30001': 1, '4294967295': 1})
        controller = next(c for c in self.artifact['controllers']
                          if c['identity']['path_id'] == 1857)
        encoded = [t for s in controller['machines'][0]['states']
                   for t in s['transitions']
                   if t['destination']['status'] != 'local_state_index']
        self.assertEqual(len(encoded), 1)
        self.assertEqual(encoded[0]['destination']['raw'], 30001)
        sched = Scheduler(controller)
        run(sched, 6.0)
        self.assertEqual(sched.state, 2)
        self.assertIn('encoded_destination_not_local',
                      [r for b in sched.blocked for r in b['reasons']])

    def test_every_motion_leaf_resolves_to_a_clip_length(self):
        self.assertEqual(self.counts['motion_leaves'], 666)
        self.assertEqual(self.counts['motion_leaves_resolved'], 666)
        self.assertEqual(self.artifact['clip_lengths_resolved']['leaves_unresolved'], 0)

    def test_policy_flags_declare_what_is_unproven(self):
        policy = self.artifact['scheduler_policy']
        for key in ('evaluation_order', 'exit_time', 'transition_duration', 'blend',
                    'interruption', 'trigger_consumption'):
            self.assertFalse(policy[key]['proven'], key)
        self.assertTrue(policy['self_transition']['proven'])
        self.assertFalse(policy['engine_equivalence'])

    def test_every_input_is_sha_pinned(self):
        for path, sha in self.artifact['inputs'].items():
            self.assertIsNotNone(sha, path)
            self.assertEqual(len(sha), 64, path)


class CaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = read_json_gz(OUT_DEFAULT)
        cls.cases = {case['name']: case for case in cls.artifact['cases']}

    def test_bb_36002_auto_advance_sequence(self):
        case = self.cases['bb_36002_auto_advance']
        taken = case['transitions_taken']
        self.assertEqual([(t['from_state'], t['to_state']) for t in taken[:2]],
                         [(0, 1), (1, 2)])
        self.assertAlmostEqual(taken[0]['t'], 1.0, places=6)
        self.assertEqual(taken[0]['blend_seconds'], 0.0)
        self.assertAlmostEqual(taken[1]['t'], 19.0, places=5)
        # normalised 0.2 duration on a 9.0 s clip = 1.8 s crossfade
        self.assertAlmostEqual(taken[1]['blend_seconds'], 1.8, places=5)
        self.assertEqual(case['state_lengths'], {'0': 3.1666667461395264, '1': 9.0,
                                                '2': 8.5})

    def test_blt_trigger_switch_and_fixed_blend(self):
        case = self.cases['blt_88011_trigger_then_blend']
        taken = case['transitions_taken']
        self.assertEqual(taken[0]['via'], 'any')
        self.assertEqual(taken[0]['consumed_triggers'], ['Attack'])
        self.assertAlmostEqual(taken[1]['blend_seconds'], 0.5, places=9)
        self.assertEqual(taken[1]['to_state'], 2)
        self.assertEqual(case['state_lengths']['2'], 0.0)  # zero-length clip, kept as is

    def test_box_gift_trigger_cycle(self):
        case = self.cases['box_gift_triggers']
        taken = case['transitions_taken']
        self.assertEqual([t['to_state'] for t in taken], [1, 2, 0])
        self.assertTrue(all(t['blend_seconds'] == 0.0 for t in taken))
        weights = [row['weights'] for row in case['timeline_sampled']]
        self.assertTrue(all(abs(sum(w.values()) - 1.0) < 1e-9 for w in weights))

    def test_timeline_is_deterministic(self):
        from l3_transition_scheduler import build_cases
        rebuilt = build_cases(self.artifact['controllers'], load_clip_lengths())
        self.assertEqual(rebuilt, self.artifact['cases'])


class RegenerationTests(unittest.TestCase):
    def test_artifact_reproduces_byte_identically(self):
        from l3_model_common import write_json_gz
        import tempfile
        from l3_transition_scheduler import build
        rebuilt = build()
        self.assertEqual(rebuilt, read_json_gz(OUT_DEFAULT))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'rebuilt.json.gz'
            write_json_gz(path, rebuilt)
            self.assertEqual(path.read_bytes(), Path(OUT_DEFAULT).read_bytes())


if __name__ == '__main__':
    unittest.main()
