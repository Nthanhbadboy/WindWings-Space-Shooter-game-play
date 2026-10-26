"""Tests for the reachability / driven-coverage model (tools/verify/l3_transition_coverage.py).

The tests re-derive the counts from the transition contract instead of trusting the artifact, and
they pin the graph invariants that would catch a silently wrong closure: subset nesting, the
state partition, encoded destinations never traversed, and the binding tiers partitioning the
52 400 records.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path('tools/verify').resolve()))
from l3_model_common import read_json_gz, write_json_gz
from l3_transition_coverage import (OUT_DEFAULT, build, edge_blockers, edge_class, gate_names,
                                    machine_edges, start_source)


class EdgeModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.transitions = read_json_gz('datas/l3_transition_model.json.gz')
        cls.controllers = cls.transitions['controllers']

    def test_edge_classes_account_for_every_transition(self):
        total = 0
        for controller in self.controllers:
            for machine in controller['machines']:
                total += len(machine_edges(machine))
        counts = self.transitions['counts']
        self.assertEqual(total, counts['any_transitions'] + counts['state_transitions']
                         + counts['selector_transitions'])
        self.assertEqual(total, 932)

    def test_conditions_make_an_edge_parameter_gated(self):
        self.assertEqual(edge_class({'conditions': [{'mode': 1}], 'has_exit_time': False,
                                     'exit_time': 0.0}), 'parameter_gated')
        self.assertEqual(edge_class({'conditions': [], 'has_exit_time': False,
                                     'exit_time': 0.0}), 'unconditional')
        self.assertEqual(edge_class({'conditions': [], 'has_exit_time': True,
                                     'exit_time': 1.0}), 'exit_time_gated')

    def test_gate_names_are_deduplicated_and_sorted(self):
        transition = {'conditions': [{'parameter_names': ['B', 'A']},
                                     {'parameter_names': ['A']}]}
        self.assertEqual(gate_names(transition), ['A', 'B'])
        self.assertEqual(gate_names({'conditions': []}), [])

    def test_start_sources_are_declared_not_guessed(self):
        machine = next(m for c in self.controllers for m in c['machines']
                       if m['default_status'] == 'valid_index' and m['selectors'])
        starts = start_source(machine)
        self.assertTrue(any(s['source'] == 'serialized_default_state' for s in starts))
        self.assertTrue(all('state' in entry for entry in starts))
        empty = next(m for c in self.controllers for m in c['machines']
                     if m['default_status'] != 'valid_index')
        self.assertEqual([e for e in start_source(empty)
                          if e['source'] == 'serialized_default_state'], [])


class ClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = read_json_gz(OUT_DEFAULT)
        cls.transitions = read_json_gz('datas/l3_transition_model.json.gz')
        cls.models = {model['identity']['path_id']: model for model in cls.artifact['controllers']}
        cls.by_path = {controller['identity']['path_id']: controller
                       for controller in cls.transitions['controllers']}

    def test_every_state_is_either_reachable_or_explained(self):
        for model in self.artifact['controllers']:
            for machine in model['machines']:
                self.assertEqual(len(machine['reachable_parameterized'])
                                 + len(machine['unreachable']), machine['states'],
                                 (model['name'], machine['machine_index']))
                for entry in machine['unreachable']:
                    self.assertIn(entry['reason'],
                                  ('no_incoming_local_transition', 'only_from_unreachable_states'))

    def test_unconditional_closure_never_exceeds_the_parameterized_one(self):
        for model in self.artifact['controllers']:
            for machine in model['machines']:
                self.assertLessEqual(set(machine['reachable_unconditional']),
                                     set(machine['reachable_parameterized']))

    def test_every_recorded_path_uses_real_edges_of_the_machine(self):
        checked = 0
        for path_id, model in self.models.items():
            controller = self.by_path[path_id]
            for machine_model in model['machines']:
                machine = controller['machines'][machine_model['machine_index']]
                allowed = {}
                for scope, source_state, transition in machine_edges(machine):
                    if scope == 'entry':
                        continue
                    if edge_blockers(transition, source_state if source_state is not None else -1):
                        continue
                    allowed[transition['id']] = (scope, source_state,
                                                 transition['destination']['index'],
                                                 edge_class(transition),
                                                 gate_names(transition))
                for state, info in machine_model['paths'].items():
                    for hop in info['path']:
                        self.assertIn(hop['transition_id'], allowed, (model['name'], state))
                        scope, source_state, target, _cls, _gates = allowed[hop['transition_id']]
                        self.assertEqual(hop['to_state'], target)
                        self.assertEqual(hop['from_state'], source_state
                                         if scope == 'state' else hop['from_state'])
                        checked += 1
        self.assertGreater(checked, 400)

    def test_paths_are_shortest_and_gates_recompute_from_the_contract(self):
        for path_id, model in self.models.items():
            controller = self.by_path[path_id]
            for machine_model in model['machines']:
                machine = controller['machines'][machine_model['machine_index']]
                by_id = {transition['id']: transition
                         for _scope, _source, transition in machine_edges(machine)}
                for state, info in machine_model['paths'].items():
                    self.assertEqual(info['distance'], len(info['path']))
                    expected = set()
                    for hop in info['path']:
                        expected |= set(gate_names(by_id[hop['transition_id']]))
                    self.assertEqual(info['gates'], sorted(expected), (model['name'], state))
                    self.assertEqual(machine_model['gates_for_state'][state], info['gates'])

    def test_encoded_destinations_are_blocked_not_guessed(self):
        for model in self.artifact['controllers']:
            for machine in model['machines']:
                for record in machine['blocked']:
                    self.assertIn('encoded_destination', record['reasons'])
                    self.assertIsNone(record['to_state'])
                    self.assertIn(record['destination_raw'], (30000, 30001, 4294967295))
        self.assertEqual(self.artifact['cross_checks']
                         ['encoded_destinations_never_traversed']['traversed'], 0)

    def test_box_gift_needs_one_trigger_per_state(self):
        model = self.models[1792]
        machine = model['machines'][0]
        self.assertEqual(machine['states'], 3)
        self.assertEqual(machine['reachable_parameterized'], [0, 1, 2])
        self.assertEqual(machine['reachable_unconditional'], [0])
        self.assertEqual(machine['gates_for_state'],
                         {'0': [], '1': ['Flick'], '2': ['Change']})
        self.assertEqual([record['destination_raw'] for record in machine['blocked']], [30000])

    def test_bb_36002_advances_without_any_parameter(self):
        machine = self.models[1910]['machines'][0]
        self.assertEqual(machine['reachable_unconditional'], [0, 1, 2])
        self.assertEqual(machine['gates_for_state'], {'0': [], '1': [], '2': []})
        self.assertEqual(self.by_path[1910]['parameters'], [])

    def test_body_states_are_named_unreachable_with_a_reason(self):
        machine = self.models[1813]['machines'][0]
        reasons = {entry['state']: entry['reason'] for entry in machine['unreachable']}
        self.assertEqual(reasons, {1: 'no_incoming_local_transition',
                                   13: 'no_incoming_local_transition'})
        self.assertEqual(len(machine['reachable_parameterized']), 13)

    def test_a_machine_without_a_local_default_is_reported(self):
        model = next(model for model in self.artifact['controllers']
                     if any(machine['default_status'] != 'valid_index'
                            for machine in model['machines']))
        machine = next(machine for machine in model['machines']
                       if machine['default_status'] != 'valid_index')
        self.assertEqual(machine['states'], 0)
        self.assertEqual(machine['reachable_parameterized'], [])
        self.assertEqual(self.artifact['counts']['machine_without_local_default'], 1)

    def test_transition_ids_are_not_globally_unique(self):
        """Regression: a cross-check keyed on the id alone miscounted 13 traversed blockers."""
        ids = [model['identity']['path_id'] for model in self.artifact['controllers']]
        self.assertEqual(len(ids), len(set(ids)))
        blocked = [record['transition_id'] for model in self.artifact['controllers']
                   for machine in model['machines'] for record in machine['blocked']]
        self.assertLess(len(set(blocked)), len(blocked))


class CountTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = read_json_gz(OUT_DEFAULT)
        cls.counts = cls.artifact['counts']
        cls.transitions = read_json_gz('datas/l3_transition_model.json.gz')

    def test_controller_and_state_totals_come_from_the_contract(self):
        source = self.transitions['counts']
        self.assertEqual(self.counts['controllers'], source['controllers'])
        self.assertEqual(self.counts['machines'], source['machines'])
        self.assertEqual(self.counts['states_total'], source['states'])
        self.assertEqual(self.counts['transitions_total'],
                         source['any_transitions'] + source['state_transitions']
                         + source['selector_transitions'])

    def test_counts_are_recomputed_from_the_controller_models(self):
        reachable = sum(len(machine['reachable_parameterized'])
                        for model in self.artifact['controllers']
                        for machine in model['machines'])
        unreachable = sum(len(machine['unreachable'])
                          for model in self.artifact['controllers']
                          for machine in model['machines'])
        self.assertEqual(reachable, self.counts['states_reachable_parameterized'])
        self.assertEqual(unreachable, self.counts['states_unreachable'])
        self.assertEqual(sum(self.counts['edges_by_class'].values()),
                         self.counts['transitions_total'])

    def test_closures_are_reported_per_controller(self):
        fully = sum(1 for model in self.artifact['controllers']
                    if all(not machine['unreachable'] for machine in model['machines'])
                    and sum(machine['states'] for machine in model['machines']) > 0)
        self.assertEqual(fully, self.counts['controllers_fully_reachable_parameterized'])
        broken = sum(1 for model in self.artifact['controllers']
                     if any(machine['unreachable'] for machine in model['machines']))
        self.assertEqual(broken, self.counts['controllers_with_unreachable_states'])
        empty = sum(1 for model in self.artifact['controllers']
                    if sum(machine['states'] for machine in model['machines']) == 0)
        self.assertEqual(empty, self.counts['machines_without_states'])
        self.assertEqual(fully + broken + empty, self.counts['controllers'])

    def test_parameter_accounting_is_per_controller(self):
        declared = sum(len(controller['parameters'])
                       for controller in self.transitions['controllers'])
        self.assertEqual(declared, self.counts['parameters_declared'])
        self.assertEqual(self.counts['parameter_declarations_used_as_gate']
                         + self.counts['parameter_declarations_never_used_as_gate'],
                         declared)
        self.assertLess(self.counts['distinct_gate_names'], declared)


class CoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = read_json_gz(OUT_DEFAULT)
        cls.counts = cls.artifact['counts']
        cls.coverage = cls.artifact['binding_coverage']

    def test_binding_tiers_partition_the_records(self):
        totals = self.coverage['totals']
        self.assertEqual(totals['all'], 52400)
        self.assertEqual(totals['controller_clip_reachable_parameterized']
                         + totals['controller_clip_unreachable']
                         + totals['all'] - totals['animator_mapped'], totals['all'])
        self.assertEqual(self.coverage['ambiguous_animator_rows'], 0)
        self.assertEqual([k for k in self.coverage['by_kind']['controller_clip_unreachable']],
                         sorted(k for k in self.coverage['by_kind']['controller_clip_unreachable']))

    def test_kind_breakdowns_sum_back_to_their_tier(self):
        for tier, kinds in self.coverage['by_kind'].items():
            self.assertEqual(sum(kinds.values()), self.coverage['totals'][tier], tier)

    def test_unreachable_bindings_are_a_real_subset(self):
        unreachable = self.coverage['totals']['controller_clip_unreachable']
        self.assertEqual(unreachable, 768)
        self.assertEqual(self.counts['bindings']['controller_clip_unreachable'], unreachable)
        self.assertLess(unreachable, self.counts['bindings']['total'])
        unconditional = self.coverage['totals']['controller_clip_reachable_unconditional']
        self.assertLess(unconditional, self.coverage['totals']['controller_clip_reachable_parameterized'])

    def test_clip_tiers_are_nested_and_measured(self):
        clips = self.artifact['clip_coverage']
        self.assertEqual(clips['clips_in_motion_artifact'], 665)
        self.assertEqual(clips['clips_referenced_by_a_state'], 665)
        self.assertEqual(clips['clips_never_referenced'], 0)
        self.assertLessEqual(clips['clips_reachable_parameterized'],
                             clips['clips_referenced_by_a_state'])
        self.assertLessEqual(clips['clips_reachable_unconditional'],
                             clips['clips_reachable_parameterized'])
        self.assertEqual(clips['controller_clip_pairs_unreachable'],
                         len(clips['unreachable_pairs']))
        self.assertEqual(clips['clips_unreachable'], 19)

    def test_every_input_is_sha_pinned(self):
        for path, sha in self.artifact['inputs'].items():
            self.assertIsNotNone(sha, path)
            self.assertEqual(len(sha), 64, path)

    def test_scope_and_limits_stay_declared(self):
        self.assertIn('No engine scheduling', self.artifact['scope'])
        limits = ' '.join(self.artifact['decode_limits'])
        for needle in ('closure_is_graph_not_trace', 'parameter_values_ignored_in_full_closure',
                       'encoded_destinations_block', 'binding_attribution_via_animator_attachment',
                       'transition_ids_are_machine_scoped'):
            self.assertIn(needle, limits)


class RegenerationTests(unittest.TestCase):
    def test_artifact_reproduces_byte_identically(self):
        import tempfile
        rebuilt = build()
        self.assertEqual(rebuilt, read_json_gz(OUT_DEFAULT))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'rebuilt.json.gz'
            write_json_gz(path, rebuilt)
            self.assertEqual(path.read_bytes(), Path(OUT_DEFAULT).read_bytes())


if __name__ == '__main__':
    unittest.main()
