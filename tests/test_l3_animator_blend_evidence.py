"""Tests for the bounded Animator blend/interpolation evidence inventory (#15)."""
import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path('tools/verify').resolve()))
import l3_animator_blend_evidence as evidence

ARTIFACT = evidence.build()


class SerializedCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = ARTIFACT
        cls.graph = cls.artifact['serialized_controller_graphs']
        cls.components = cls.artifact['serialized_component_inventory']
        cls.scope = cls.artifact['transition_model_scope_check']

    def test_all_308_recovered_controller_graphs_have_one_layer(self):
        self.assertEqual(self.graph['controller_records'], 308)
        self.assertEqual(self.graph['unique_path_ids'], 308)
        self.assertEqual(self.graph['duplicate_path_id_records'], 0)
        self.assertEqual(self.graph['layer_count_distribution'], {'1': 308})
        self.assertEqual(self.graph['controllers_with_multiple_layers'], 0)
        self.assertEqual(self.graph['serialized_layer_total'], 308)

    def test_serialized_layer_values_stay_literal(self):
        self.assertEqual(self.graph['layer_blending_mode_raw_distribution'], {'0': 308})
        self.assertEqual(self.graph['layer_default_weight_distribution'], {'0.0': 308})
        self.assertEqual(self.graph['synchronized_layer_index_distribution'], {'0': 308})
        self.assertEqual(self.graph['sync_affects_timing_distribution'], {'False': 308})

    def test_232_controller_model_subset_joins_without_missing_rows(self):
        self.assertEqual(self.scope['program_controllers'], 232)
        self.assertEqual(self.scope['matched_to_graph_by_path_id_and_name'], 232)
        self.assertEqual(self.scope['unmatched'], [])
        self.assertEqual(self.scope['layer_count_distribution'], {'1': 232})
        self.assertEqual(self.scope['layer_mode_raw_distribution'], {'0': 232})
        self.assertEqual(self.scope['transition_model_controllers'], 232)
        self.assertEqual(self.scope['transition_model_layers_total'], 232)

    def test_animator_and_controller_component_counts_are_reported(self):
        self.assertEqual(self.components['animator_components'], 5792)
        self.assertEqual(self.components['animator_null_controller_refs'], 14)
        self.assertEqual(self.components['animator_distinct_nonzero_controller_refs'], 307)
        self.assertEqual(self.components['animator_controller_asset_records'], 308)
        cross = self.artifact['controller_identity_cross_check']
        self.assertEqual(cross['shared_path_ids'], 308)
        self.assertEqual(cross['graph_only_path_ids'], [])
        self.assertEqual(cross['native_type_only_path_ids'], [])
        self.assertEqual(cross['name_mismatches_on_shared_path_id'], [])
        self.assertEqual(self.scope['graph_controllers_referenced_by_animator_count'], 307)
        self.assertEqual(self.scope['graph_controllers_unreferenced_by_animator_count'], 1)

    def test_native_animation_clip_curve_arrays_are_not_misread_as_zero_motion(self):
        clips = self.components
        self.assertEqual(clips['animation_clip_records'], 791)
        self.assertEqual(clips['ordinary_animation_clip_curve_totals'], {
            'm_CompressedRotationCurves__count': 0,
            'm_EulerCurves__count': 0,
            'm_FloatCurves__count': 0,
            'm_PPtrCurves__count': 0,
            'm_PositionCurves__count': 0,
            'm_RotationCurves__count': 0,
            'm_ScaleCurves__count': 0,
        })
        self.assertGreater(self.artifact['serialized_animation_curve_inventory']['counts']
                           ['streamed_key_records_in_export'], 0)


class ApiEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = ARTIFACT['managed_api_surface_from_il2cpp_dump']
        cls.animator_methods = cls.api['methods']['Animator']
        cls.curve_methods = cls.api['methods']['AnimationCurve']

    def test_layer_weight_and_state_clip_weight_api_surface_is_present(self):
        declarations = [item['declaration'] for item in self.animator_methods]
        for expected in ('public int get_layerCount()', 'public float GetLayerWeight(int layerIndex)',
                         'public AnimatorStateInfo GetCurrentAnimatorStateInfo(int layerIndex)',
                         'public AnimatorStateInfo GetNextAnimatorStateInfo(int layerIndex)',
                         'public void GetCurrentAnimatorClipInfo(int layerIndex, List<AnimatorClipInfo> clips)',
                         'public void GetNextAnimatorClipInfo(int layerIndex, List<AnimatorClipInfo> clips)'):
            self.assertIn(expected, declarations)

    def test_curve_evaluate_entry_and_keyframe_tangent_fields_are_present(self):
        self.assertTrue(any(item['declaration'] == 'public float Evaluate(float time)'
                            for item in self.curve_methods))
        keyframe_fields = self.api['fields']['Keyframe']
        for field in ('float m_Time', 'float m_Value', 'float m_InTangent',
                      'float m_OutTangent', 'int m_WeightedMode',
                      'float m_InWeight', 'float m_OutWeight'):
            self.assertIn(field, keyframe_fields)

    def test_dump_placeholders_are_not_misrepresented_as_native_bodies(self):
        self.assertTrue(self.api['all_extracted_method_bodies_are_empty_placeholders'])
        self.assertIn('empty bodies do not disclose', self.api['evidence_interpretation'])
        counts = self.api['global_api_name_occurrence_counts']
        self.assertEqual(counts['SetLayerWeight'], 0)
        self.assertEqual(counts['CrossFade'], 0)

    def test_engine_algorithm_remains_unproven_and_inventory_marks_it(self):
        result = ARTIFACT['conclusion']
        self.assertFalse(result['property_interpolation_native_algorithm_proven'])
        self.assertEqual(result['multi_layer_blending_status'],
                         'NOT_EXERCISED_IN_RECOVERED_GRAPH_SET')
        self.assertIn('runtime probe', result['native_evidence_blocker'])


class ArtifactTests(unittest.TestCase):
    def test_inputs_and_generator_are_sha_pinned(self):
        artifact = ARTIFACT
        self.assertEqual(len(artifact['inputs']), 6)
        self.assertTrue(all(len(value) == 64 for value in artifact['inputs'].values()))
        self.assertEqual(len(artifact['build']['tool_sha256']), 64)
        self.assertTrue(artifact['conclusion']['property_curve_data_available'])

    def test_deterministic_artifact_rebuild(self):
        artifact = evidence.build()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'evidence.json.gz'
            evidence.write_gz(target, artifact)
            self.assertEqual(target.read_bytes(),
                             (evidence.ROOT / evidence.OUT_DEFAULT).read_bytes())
            with gzip.open(target, 'rt', encoding='utf-8') as stream:
                parsed = json.load(stream)
        self.assertEqual(parsed['conclusion'], artifact['conclusion'])


if __name__ == '__main__':
    unittest.main()
