"""Tests for the driven-property route model (tools/verify/l3_driven_props.py).

These tests pin the channel layout / attribution arithmetic, the CRC field route, the
absence of CanvasRenderer/CanvasGroup bindings, one independent reproduction of the
property probe published in report 99, and the concrete driven rect/alpha/active values
of the modelled states.
"""
import sys
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path('tools/verify').resolve()))
from l3_model_common import read_json_gz
from l3_driven_props import (OUT_DEFAULT, as_int32, channel_value, clip_layout_info,
                             curve_layout, load_motion, route_table)


class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clips = load_motion()

    def test_every_clip_channel_count_matches_the_expanded_bindings(self):
        self.assertEqual(len(self.clips), 665)
        mismatched = [(key, info) for key, clip in self.clips.items()
                      for info in [clip_layout_info(clip)]
                      if info['channels'] != info['channel_count']]
        self.assertEqual(mismatched, [])

    def test_streamed_channel_indices_are_a_prefix_of_the_layout(self):
        for key, clip in self.clips.items():
            info = clip_layout_info(clip)
            self.assertTrue(info['streamed_indices_are_prefix'], key)

    def test_layout_exactness_is_measured(self):
        exact = [key for key, clip in self.clips.items()
                 if clip_layout_info(clip)['layout_exact']]
        self.assertEqual(len(exact), 634)
        partial = [key for key, clip in self.clips.items()
                   if not clip_layout_info(clip)['layout_exact']]
        self.assertEqual(len(partial), 31)
        # the partial ones carry discrete (int/PPtr) curves whose count sits outside
        # streamed+constant, so they are not attributed instead of guessed
        for key in partial:
            clip = self.clips[key]
            self.assertGreater(clip['discrete_curve_count'], 0, key)

    def test_transform_bindings_expand_to_vector_channels(self):
        clip = self.clips[('data.unity3d/resources.assets', 1572)]
        layout = curve_layout(clip)
        self.assertEqual(len(layout), 4)
        self.assertEqual([c['channel'] for c in layout if c['typeID'] == 4], [0, 1, 2])
        self.assertEqual(layout[3]['attribute'], 304273561)

    def test_dense_curves_are_absent_everywhere(self):
        self.assertEqual([key for key, clip in self.clips.items()
                          if (clip['dense'].get('m_CurveCount') or 0) > 0], [])


class EvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clips = load_motion()

    def test_report99_property_probe_is_reproduced_from_artifacts(self):
        clip = self.clips[('data.unity3d/resources.assets', 1572)]
        self.assertEqual(clip['name'], 'Appear')
        at_zero = [channel_value(clip, channel, 0.0)['value'] for channel in (0, 1, 2, 3)]
        self.assertEqual(at_zero, [0.0, 0.0, 1.0, 0.0])
        mid = [channel_value(clip, channel, 0.25)['value'] for channel in (0, 1, 2, 3)]
        self.assertAlmostEqual(mid[0], 1.030399899053574, places=12)
        self.assertAlmostEqual(mid[1], 1.030399899053574, places=12)
        self.assertEqual(mid[2], 1.0)
        self.assertAlmostEqual(mid[3], 0.8313725590705872, places=12)
        end = [channel_value(clip, channel, 0.5)['value'] for channel in (0, 1, 2, 3)]
        self.assertEqual(end, [1.0, 1.0, 1.0, 0.8313725590705872])

    def test_initial_sentinel_frame_is_used_only_when_no_key_precedes(self):
        clip = self.clips[('data.unity3d/resources.assets', 1572)]
        first = channel_value(clip, 0, 0.0)
        self.assertEqual(first['status'], 'streamed_polynomial')
        self.assertEqual(first['value'], 0.0)

    def test_values_do_not_depend_on_other_curves(self):
        clip = self.clips[('data.unity3d/resources.assets', 1572)]
        self.assertNotEqual(channel_value(clip, 0, 0.1)['value'],
                            channel_value(clip, 3, 0.1)['value'])

    def test_int_curve_constant_is_reinterpreted_as_int32(self):
        self.assertEqual(as_int32(5.74532370373175e-42), 4100)
        clip = self.clips[('data.unity3d/resources.assets', 986)]
        value = channel_value(clip, 33, 0.0, is_int=True)
        self.assertEqual(value['status'], 'constant_int')
        self.assertEqual(value['value_int'], 4100)

    def test_time_beyond_the_last_key_holds_the_last_value(self):
        clip = self.clips[('data.unity3d/resources.assets', 1572)]
        self.assertEqual(channel_value(clip, 2, 10.0)['value'],
                         channel_value(clip, 2, 0.5)['value'])


class RouteTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = read_json_gz(OUT_DEFAULT)
        cls.counts = cls.artifact['counts']
        cls.table = {(row['class_id'], row['attribute']): row
                     for row in cls.artifact['property_route']}

    def test_route_table_is_recomputed_from_the_bindings(self):
        table, class_ids = route_table()
        self.assertEqual(len(table), self.counts['route_entries'])
        self.assertEqual({str(k): v for k, v in sorted(class_ids.items())},
                         self.counts['class_ids'])
        self.assertEqual(sum(row['bindings'] for row in table),
                         self.counts['bindings_total'])
        self.assertEqual(self.counts['bindings_total'], 52400)

    def test_every_named_field_matches_its_crc32_attribute(self):
        checked = 0
        for row in self.artifact['property_route']:
            if not row['field'] or row['class_id'] == 4:
                continue
            checked += 1
            self.assertEqual(zlib.crc32(row['field'].encode()) & 0xFFFFFFFF,
                             row['attribute'])
            self.assertTrue(row['crc32_matches_attribute'])
        self.assertEqual(checked, 52)
        self.assertTrue(self.artifact['cross_checks']
                        ['crc32_field_name_matches_attribute']['equal'])

    def test_known_field_routes(self):
        self.assertEqual(self.table[(224, 1967290853)]['field'], 'm_SizeDelta.x')
        self.assertEqual(self.table[(224, 1460864421)]['field'], 'm_AnchoredPosition.x')
        self.assertEqual(self.table[(212, 304273561)]['field'], 'm_Color.a')
        self.assertEqual(self.table[(1, 2086281974)]['field'], 'm_IsActive')
        self.assertEqual(self.table[(224, 1967290853)]['kind'], 'rect')

    def test_transform_bindings_use_the_declared_component_convention(self):
        present = {attribute for (class_id, attribute) in self.table if class_id == 4}
        self.assertEqual(present, {1, 3, 4})  # no clip binds m_LocalRotation (attr 2)
        for attribute, field in ((1, 'm_LocalPosition'), (3, 'm_LocalScale'),
                                 (4, 'm_LocalEulerAngles')):
            row = self.table[(4, attribute)]
            self.assertEqual(row['field'], field)
            self.assertEqual(row['field_sources'],
                             {'transform_attribute_convention': row['bindings']})
        self.assertNotIn((4, 2), self.table)

    def test_no_canvas_bindings_exist_in_this_artifact(self):
        self.assertEqual(self.counts['canvas_renderer_bindings'], 0)
        self.assertEqual(self.counts['canvas_group_bindings'], 0)
        self.assertNotIn(222, self.counts['class_ids'])
        self.assertNotIn(225, self.counts['class_ids'])

    def test_unresolved_fields_are_kept_not_guessed(self):
        self.assertEqual(self.counts['bindings_unresolved_field'], 16671)
        row = self.table[(114, 3721021157)]
        self.assertIsNone(row['field'])
        self.assertEqual(row['kind'], 'unresolved')
        self.assertEqual(row['bindings'], 75)

    def test_driven_kind_totals(self):
        self.assertEqual(self.counts['driven_rect_bindings'], 755)
        self.assertEqual(self.counts['driven_alpha_bindings'], 3575)
        self.assertEqual(self.counts['driven_active_bindings'], 5230)
        self.assertEqual(self.counts['driven_particle_module_bindings'], 147)

    def test_every_input_is_sha_pinned(self):
        for path, sha in self.artifact['inputs'].items():
            self.assertIsNotNone(sha, path)
            self.assertEqual(len(sha), 64, path)


class CaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = read_json_gz(OUT_DEFAULT)
        cls.cases = {case['name']: case for case in cls.artifact['cases']}

    @staticmethod
    def target(case, sample_index, path_id):
        for target in case['samples'][sample_index]['targets']:
            if target['identity']['path_id'] == path_id:
                return target
        raise AssertionError(f'target {path_id} missing')

    def test_box_gift_appear_baseline_and_driven_rect(self):
        case = self.cases['box_gift_appear']
        self.assertEqual(case['clip']['path_id'], 986)
        self.assertEqual(case['state_names'], ['Appear'])
        self.assertEqual(case['bindings'], 26)
        self.assertEqual(case['bindings_with_field'], 25)
        self.assertEqual(case['targets_snapshotted'], case['targets_total'])
        target = self.target(case, 0, 576148)
        self.assertEqual(target['type'], 'RectTransform')
        self.assertEqual(target['kinds'], ['local_scale', 'rect', 'local_position'])
        self.assertEqual(target['baseline']['m_SizeDelta.x'], 1.0)
        self.assertEqual(target['fields']['m_SizeDelta.x'], 1.850000023841858)
        self.assertEqual(target['changed']['m_SizeDelta.x'],
                         {'baseline': 1.0, 'driven': 1.850000023841858})
        self.assertEqual(target['changed']['m_AnchoredPosition.x'],
                         {'baseline': 0.4860000014305115, 'driven': 0.0})
        self.assertEqual(target['baseline_status'], 'serialized_inline')

    def test_box_gift_pop_scale_and_alpha_over_time(self):
        case = self.cases['box_gift_appear']
        first = self.target(case, 0, 277770)['fields']
        self.assertEqual(first['m_LocalScale.x'], 0.5)
        self.assertEqual(first['m_LocalScale.y'], 0.5)
        self.assertEqual(first['m_LocalScale.z'], 1.0)
        near_quarter = self.target(case, 2, 277770)['fields']
        self.assertAlmostEqual(near_quarter['m_LocalScale.x'], 1.2000000565140336,
                               places=9)
        alpha_target = self.target(case, 0, 532836)
        self.assertEqual(alpha_target['baseline'], {'m_Color.a': 0.0})
        self.assertEqual(alpha_target['fields'], {'m_Color.a': 1.0})
        self.assertEqual(self.target(case, 3, 532836)['fields']['m_Color.a'],
                         0.5000000447034836)

    def test_text_mesh_pro_scalars_are_applied_without_a_baseline(self):
        case = self.cases['box_gift_appear']
        target = self.target(case, 0, 652439)
        self.assertEqual(target['baseline_status'], 'component_snapshot_not_inlined')
        self.assertEqual(target['fields']['m_fontSize'], 3.8499999046325684)
        self.assertEqual(target['fields']['m_fontSizeMin'], 3.0)
        self.assertEqual(target['fields']['m_fontSizeMax'], 6.4000000953674316)
        self.assertEqual(target['int_fields'], {'m_textAlignment': 4100})

    def test_unresolved_binding_is_reported_per_sample(self):
        case = self.cases['box_gift_appear']
        self.assertEqual(case['skipped_reasons'], {'field_unresolved': 5})
        for sample in case['samples']:
            self.assertEqual([item['binding_index'] for item in sample['skipped']], [22])

    def test_extra_life_activates_four_gameobjects(self):
        case = self.cases['extra_life_apear']
        active = [target for target in case['samples'][0]['targets']
                  if 'active' in target['kinds']]
        self.assertEqual([t['identity']['path_id'] for t in active],
                         [32691, 32692, 32694, 32695])
        for target in active:
            self.assertEqual(target['fields'], {'m_IsActive': 1.0})
            self.assertEqual(target['bool_model'], {'m_IsActive': True})
        rect = self.target(case, 0, 571782)
        self.assertEqual(rect['fields']['m_LocalScale.x'], 0.0)
        later = self.target(case, 1, 571782)['fields']['m_LocalScale.x']
        self.assertGreater(later, 0.5)
        self.assertLess(later, 0.52)

    def test_effect_rect_and_colour_are_driven_over_time(self):
        case = self.cases['efx_90016_active']
        rect_values = [self.target(case, index, 578905)['fields']['m_AnchoredPosition.y']
                       for index in range(len(case['samples']))]
        self.assertEqual(rect_values[0], 0.0)
        self.assertAlmostEqual(rect_values[2], 0.3386435861136867, places=12)
        self.assertEqual(rect_values[4], 1.5)
        self.assertEqual(rect_values, sorted(rect_values))
        self.assertEqual([s['clip_time'] for s in case['samples']],
                         [0.0, 0.25, 0.75, 1.0, 1.5])
        colour = self.target(case, 2, 654176)['fields']
        self.assertAlmostEqual(colour['m_fontColor.g'], 0.863033879244307, places=12)
        self.assertAlmostEqual(colour['m_fontColor.r'], 0.526232133817304, places=12)
        self.assertEqual(colour['m_fontColor.a'], 1.0)

    def test_scheduled_timeline_links_scheduler_and_driven_state(self):
        timeline = self.artifact['scheduled_timeline_case']
        self.assertEqual([(t['from_state'], t['to_state'])
                          for t in timeline['transitions_taken']], [(0, 1), (1, 2), (2, 0)])
        rows = [row for row in timeline['timeline'] if 'state' in row]
        self.assertEqual(rows[0]['state'], 0)
        self.assertEqual(rows[0]['state_name'], 'Appear')
        self.assertTrue(all(row['states'] for row in rows))
        self.assertTrue(all(abs(sum(state['weight'] for state in row['states']) - 1.0)
                            < 1e-9 for row in rows))
        self.assertIn('declared model choice',
                      timeline['blend_weighting_status'])

    def test_scope_and_limits_stay_declared(self):
        self.assertIn('No render', self.artifact['scope'])
        limits = ' '.join(self.artifact['decode_limits'])
        self.assertIn('no_canvas_bindings', limits)
        self.assertIn('blend_weights_model', limits)
        for case in self.artifact['cases']:
            self.assertIn('layout', case)
            self.assertTrue(case['layout']['layout_exact'])


class RegenerationTests(unittest.TestCase):
    def test_artifact_reproduces_byte_identically(self):
        from l3_model_common import write_json_gz
        import tempfile
        from l3_driven_props import build
        rebuilt = build()
        self.assertEqual(rebuilt, read_json_gz(OUT_DEFAULT))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'rebuilt.json.gz'
            write_json_gz(path, rebuilt)
            self.assertEqual(path.read_bytes(), Path(OUT_DEFAULT).read_bytes())


if __name__ == '__main__':
    unittest.main()
