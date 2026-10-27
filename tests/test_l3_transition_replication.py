"""Independent recount/differential checks for l3_transition_replication."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path('tools/verify').resolve()))
import l3_transition_replication as replication


class RawRecountTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = replication.read_gz(replication.ROOT / replication.SOURCE)
        cls.model = replication.read_gz(replication.ROOT / replication.MODEL)
        cls.audit = replication._audit_source(cls.source)

    def test_independent_counts_match_measured_source_contract(self):
        counts = self.audit['counts']
        self.assertEqual(counts['controllers'], 232)
        self.assertEqual(counts['machines'], 232)
        self.assertEqual(counts['states'], 667)
        self.assertEqual(counts['any_transitions'], 343)
        self.assertEqual(counts['state_transitions'], 125)
        self.assertEqual(counts['selector_transitions'], 464)
        self.assertEqual(counts['transition_raw_records'], 932)
        self.assertEqual(counts['conditions'], 376)
        self.assertEqual(counts['parameters'], 377)

    def test_destinations_are_counted_by_local_machine_state_indices(self):
        counts = self.audit['counts']
        self.assertEqual(counts['destination_local_to_machine'], 698)
        self.assertEqual(counts['destination_not_local_to_machine'], 234)
        self.assertEqual(sum(self.audit['distributions']['destinations_raw'].values()), 932)

    def test_transition_presence_is_not_conflated_with_default_false(self):
        presence = self.audit['distributions']['raw_field_presence_by_scope']
        self.assertEqual(presence['selector:m_InterruptionSource:absent'], 464)
        self.assertEqual(presence['selector:m_HasExitTime:absent'], 464)
        self.assertEqual(presence['any:m_InterruptionSource:present'], 343)
        self.assertEqual(presence['state:m_InterruptionSource:present'], 125)

    def test_every_state_motion_leaf_is_counted_from_source(self):
        counts = self.audit['counts']
        self.assertEqual(counts['motion_nodes'], 666)
        self.assertEqual(counts['motion_nodes_with_clip_identity'], 666)
        self.assertEqual(counts['states_without_motion'], 1)

    def test_per_controller_rows_partition_global_totals(self):
        rows = self.audit['per_controller']
        self.assertEqual(len(rows), 232)
        self.assertEqual(sum(row['states'] for row in rows), 667)
        self.assertEqual(sum(row['transitions'] for row in rows), 932)
        self.assertEqual(sum(row['conditions'] for row in rows), 376)


class DifferentialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = replication.read_gz(replication.ROOT / replication.SOURCE)
        cls.model = replication.read_gz(replication.ROOT / replication.MODEL)

    def test_ordered_normalized_fields_replicate_for_all_edges(self):
        result = replication._make_comparison(self.source['controllers'],
                                              self.model['controllers'])
        self.assertEqual(result['controllers_compared'], 232)
        self.assertEqual(result['machines_compared'], 232)
        self.assertEqual(result['transitions_compared'], 932)
        self.assertEqual(result['conditions_compared'], 376)
        self.assertTrue(result['equal'], result['mismatch_counts'])
        self.assertEqual(result['mismatch_counts'], {})

    def test_selector_bool_defaults_compare_but_raw_absence_is_retained(self):
        result = replication._make_comparison(self.source['controllers'],
                                              self.model['controllers'])
        self.assertTrue(result['equal'])
        presence = replication._audit_source(self.source)['distributions']
        self.assertEqual(presence['raw_field_presence_by_scope']
                         ['selector:m_HasExitTime:absent'], 464)

    def test_mutated_normalized_destination_is_detected(self):
        models = copy.deepcopy(self.model['controllers'])
        controller = next(item for item in models
                          if item['machines'][0]['any_state_transitions'])
        transition = controller['machines'][0]['any_state_transitions'][0]
        transition['destination']['raw'] += 100
        result = replication._make_comparison(self.source['controllers'], models)
        self.assertFalse(result['equal'])
        self.assertGreater(result['mismatch_counts'].get('destination_raw', 0), 0)
        self.assertTrue(any(item['field'] == 'destination_raw'
                            for item in result['mismatch_examples']))

    def test_mutated_condition_mode_is_detected(self):
        models = copy.deepcopy(self.model['controllers'])
        controller = next(item for item in models
                          if any(transition['conditions']
                                 for machine in item['machines']
                                 for transition in machine['any_state_transitions']))
        transition = next(transition for machine in controller['machines']
                          for transition in machine['any_state_transitions']
                          if transition['conditions'])
        transition['conditions'][0]['mode'] = 6
        result = replication._make_comparison(self.source['controllers'], models)
        self.assertFalse(result['equal'])
        self.assertGreater(result['mismatch_counts'].get('conditions', 0), 0)

    def test_joins_by_qualified_controller_identity_not_name(self):
        models = copy.deepcopy(self.model['controllers'])
        models[0]['name'] = 'different display name'
        result = replication._make_comparison(self.source['controllers'], models)
        self.assertTrue(result['equal'])

    def test_controller_transition_ids_are_not_used_as_join_keys(self):
        ids = [transition['id'] for controller in self.model['controllers']
               for machine in controller['machines']
               for transition in machine['any_state_transitions']]
        self.assertLess(len(set(ids)), len(ids))
        result = replication._make_comparison(self.source['controllers'],
                                              self.model['controllers'])
        self.assertTrue(result['equal'])


class ArtifactTests(unittest.TestCase):
    def test_artifact_pins_inputs_and_declares_replication_boundary(self):
        artifact = replication.build()
        self.assertTrue(artifact['replication'])
        self.assertTrue(artifact['source_provenance']['not_independent_apk_extraction'])
        self.assertEqual(set(artifact['inputs']), {replication.SOURCE, replication.MODEL})
        self.assertTrue(all(len(value) == 64 for value in artifact['inputs'].values()))
        self.assertTrue(artifact['comparison_to_transition_model']['all_equal'])

    def test_deterministic_gzip_rebuild(self):
        import gzip
        artifact = replication.build()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'replication.json.gz'
            replication.write_gz(target, artifact)
            expected = (replication.ROOT / replication.OUT_DEFAULT).read_bytes()
            self.assertEqual(target.read_bytes(), expected)
            with gzip.open(target, 'rt', encoding='utf-8') as stream:
                self.assertEqual(stream.read()[:1], '{')


if __name__ == '__main__':
    unittest.main()
