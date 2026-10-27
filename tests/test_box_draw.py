"""Contracts for report 130 (box draw / `typeBox`): static, byte-pinned."""
import gzip
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import box_draw  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_box_draw.json.gz'
PIN_SHA = 'f36bade4e1e27222f15ce171aa1f9bbbaeefc70984f2da131f992be80388a441'


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_artifact_is_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_same_bytes(self):
        self.assertEqual(box_draw.build(), payload())

    def test_sources_are_pinned(self):
        sources = {Path(s['path']).name: s['sha256']
                   for s in payload()['provenance']['sources']}
        self.assertEqual(sources['native.json.gz'].__len__(), 64)
        self.assertEqual(len(payload()['provenance']['sources']), 4)
        names = {Path(s['path']).parent.name for s in payload()['provenance']['sources']}
        self.assertEqual(names, {'meta-rewards-535b0541', 'pack-index-535b0541',
                                 'box-draw-535b0541', 'il2cpp'})

    def test_evidence_is_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', blob['note'])


class TypeBox(unittest.TestCase):
    def test_field_and_slot(self):
        box = payload()['type_box']
        self.assertEqual(box['field'], 'Board_QuestRewards.typeBox')
        self.assertEqual(box['declared'], 'int')
        self.assertEqual(box['static_offset'], 0)
        self.assertEqual(box['class_slot_va'], 44962168)

    def test_exactly_two_writers(self):
        writers = payload()['type_box']['writers']
        self.assertEqual(payload()['type_box']['writers_total'], 2)
        self.assertEqual([w['rva'] for w in writers], [19994092, 19955344])
        self.assertEqual([w['instruction'] for w in writers], ['str d0, [x8]', 'str w20, [x8]'])

    def test_caller_supplies_the_index(self):
        writer = payload()['type_box']['writer']
        self.assertEqual(writer['method'],
                         'Board_Quest.OnPressedButtonOpenBox(int _index)')
        self.assertEqual((writer['rva'], writer['size']), (19955240, 168))
        self.assertEqual(writer['store_rva'], 19955344)
        self.assertEqual(writer['after']['event_value'], 56)      # EventID.OpenBoard
        self.assertEqual(writer['after']['board_value'], 18)      # BoardID.BoardQuestRewards
        self.assertEqual(writer['after']['post_event_rva'], 21187764)

    def test_initial_value_comes_from_pinned_rodata(self):
        initial = payload()['type_box']['initial']
        self.assertEqual(initial['rodata_hex'], '0000000001000000')
        self.assertEqual(initial['rodata_va'], 7697232)
        self.assertEqual(initial['rodata_length'], 8)
        self.assertEqual(initial['type_box'], 0)
        self.assertEqual(initial['time_update'], 1)
        self.assertEqual((initial['rva'], initial['size']), (19994024, 80))

    def test_domain_is_three_boxes(self):
        domain = payload()['type_box']['domain']
        self.assertEqual(domain['values'], [0, 1, 2])


class CallSites(unittest.TestCase):
    def test_all_call_sites_are_found(self):
        sites = payload()['call_sites']
        self.assertEqual([s['callee_rva'] for s in sites],
                         [20199416, 20199416, 20234188])

    def test_draw_site_arguments(self):
        draw = [s for s in payload()['call_sites']
                if s['callee'] == 'GetListIndexRandomRewards'][0]
        self.assertEqual(draw['call_rva'], 19997080)
        self.assertEqual(draw['caller_class'], 'Board_QuestRewards.<OpenBox>d__43')
        self.assertEqual(draw['argument_writes']['w2']['instruction'], 'ldr w2, [x8]')
        self.assertEqual(draw['argument_writes']['w2']['rva'], 19997032)
        self.assertEqual(draw['argument_writes']['w1']['instruction'], 'ldr w1, [x8, #0x20]')

    def test_season_pass_sites_are_deterministic(self):
        others = [s for s in payload()['call_sites'] if s['callee'] == 'GetListIndexRewards']
        self.assertEqual([s['call_rva'] for s in others], [19440164, 19450624])
        self.assertEqual({s['caller_class'] for s in others}, {'Board_EventSeasonPass'})


class Economy(unittest.TestCase):
    def test_arrays_and_offsets(self):
        arrays = payload()['box_cost']['arrays']
        self.assertEqual({name: spec['offset'] for name, spec in arrays.items()},
                         {'BoxKeyCost': 0x38, 'KeyPrices': 0x40, 'NumberRewards': 0x48})
        self.assertTrue(all(spec['declared'] == 'int[]' for spec in arrays.values()))
        self.assertTrue(all(spec['length'] == 3 for spec in arrays.values()))

    def test_array_initializers_are_named_as_a_gap(self):
        blobs = payload()['box_cost']['array_initializers']
        self.assertEqual([b['statics_offset'] for b in blobs], [0x38, 0x40, 0x48, 0x50])
        self.assertEqual([b['handle_token_index'] for b in blobs], [1341, 1311, 1383, 485])
        self.assertIn('RuntimeHelpers.InitializeArray', payload()['not_decoded'][0]['blocking'])
        self.assertIn('33927292', payload()['not_decoded'][0]['blocking'])

    def test_key_count_wiring(self):
        cost = payload()['box_cost']
        self.assertEqual(cost['key_count_statics'],
                         {'KeyCount0': 0x50, 'KeyCount1': 0x54, 'KeyCount2': 0x58})
        self.assertEqual(cost['getters'],
                         {'KeyCount0': 20070740, 'KeyCount1': 20071068, 'KeyCount2': 20071396})
        self.assertEqual(cost['setters'],
                         {'KeyCount0': 20070940, 'KeyCount1': 20071268, 'KeyCount2': 20071596})
        self.assertEqual(cost['sprite']['index_rule'], 'typeBox + 16')

    def test_energy_shop(self):
        shop = payload()['energy_shop']
        self.assertEqual((shop['buy']['gem_cost'], shop['buy']['energy_gain']), (30, 50))
        self.assertEqual(shop['buy']['guard']['rva'], 20750332)
        self.assertEqual(shop['free']['energy_gain'], 30)
        self.assertEqual(shop['free']['ads']['position'], 14)
        self.assertEqual(shop['free']['success_callback']['rva'], 19432800)
        self.assertEqual(shop['exchange']['gems_per_energy'], 0.3)

    def test_caller_chain_reaches_the_draw(self):
        chain = payload()['caller_chain']
        self.assertEqual([step['rva'] for step in chain],
                         [19955240, 21187764, 19985576, 19989112, 19991076, 19996384])


if __name__ == '__main__':
    unittest.main()
