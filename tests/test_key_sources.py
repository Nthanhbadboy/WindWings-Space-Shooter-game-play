"""Contracts for report 132: who hands out the quest keys, and how they are stored."""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import key_sources  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_key_sources.json.gz'
PIN_SHA = 'e97ca22a1c71f436f2d87a10c8acaa78cf42ceea8c9b8326ae7b1e83c5a91c3c'


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


def callers():
    return {row['method_rva']: row for row in payload()['callers_detail']}


class ArtifactPin(unittest.TestCase):
    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        rebuilt = json.loads(json.dumps(key_sources.build_payload(), sort_keys=True))
        self.assertEqual(rebuilt, payload())

    def test_static_only_and_runtime_marked(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', blob['note'])
        self.assertTrue(any('runtime' in row['blocking'] for row in blob['not_decoded']))


class Provenance(unittest.TestCase):
    def test_six_sources_with_hashes(self):
        sources = payload()['provenance']['sources']
        self.assertEqual(len(sources), 6)
        for row in sources:
            self.assertEqual(len(row['sha256']), 64)
            self.assertTrue((ROOT / row['path']).exists())

    def test_hits_match_the_branch_scan(self):
        blob = payload()
        self.assertEqual(blob['provenance']['hits_total'], 191)
        self.assertEqual(blob['provenance']['words_scanned'], 6765005)
        self.assertEqual(len(blob['callers_detail']), 35)
        self.assertEqual(sum(row['hits'] for row in blob['callers'].values()), 191)


class Accessors(unittest.TestCase):
    def test_static_offsets(self):
        counters = payload()['accessors']['counters']
        self.assertEqual({k: v['static_offset'] for k, v in counters.items()},
                         {'KeyCount0': 0x50, 'KeyCount1': 0x54, 'KeyCount2': 0x58})
        self.assertEqual([counters[k]['getter'] for k in sorted(counters)],
                         [20070740, 20071068, 20071396])
        self.assertEqual([counters[k]['setter'] for k in sorted(counters)],
                         [20070940, 20071268, 20071596])

    def test_negative_clamp_and_write_through(self):
        semantics = payload()['accessors']['semantics']
        for name, row in semantics.items():
            self.assertIn('asr #31', row['negative_clamp'], name)
            self.assertIn('PlayerPrefs.SetInt', row['write_through'])
            self.assertEqual(row['unloaded_sentinel'], -1)

    def test_lazy_load_defaults_to_zero(self):
        for name, row in payload()['accessors']['semantics'].items():
            self.assertIn('PlayerPrefs.GetInt(key, 0)', row['lazy_load'], name)

    def test_prefs_literals_present(self):
        keys = payload()['accessors']['prefs_keys']
        self.assertEqual(keys['literals'], ['KeyCount0', 'KeyCount1', 'KeyCount2'])
        self.assertIn('not in the pinned data', keys['note'])


class Caps(unittest.TestCase):
    def test_key_caps(self):
        self.assertEqual(payload()['caps']['key_caps'],
                         {'KeyCount0': 1000000, 'KeyCount1': 500000, 'KeyCount2': 100000})

    def test_cap_rewrites_to_zero(self):
        rows = payload()['caps']['rows']
        self.assertEqual([row['reset_to'] for row in rows], [0, 0, 0])
        self.assertEqual([row['reset_target'] for row in rows],
                         ['KeyCount0', 'KeyCount1', 'KeyCount2'])
        self.assertEqual(sorted(payload()['caps']['other_resources']),
                         ['Coins', 'Energy', 'Gems', 'WingCoins'])


class PackValues(unittest.TestCase):
    def test_key_indices(self):
        pack = payload()['supply']['pack_values']
        self.assertEqual(pack['key_indices'],
                         {'16': 'get_KeyCount0', '17': 'get_KeyCount1',
                          '18': 'get_KeyCount2'})
        self.assertEqual(pack['table']['va'], 0x779C4A)
        self.assertEqual(pack['table']['length'], 22)

    def test_key_blocks_add_the_value(self):
        rows = payload()['supply']['pack_values']['routing']
        for index, key in ((16, 0), (17, 1), (18, 2)):
            row = rows[str(index)]
            self.assertTrue(row['adds_value'])
            self.assertEqual(row['set'], f'set_KeyCount{key}')

    def test_indices_without_a_key_block(self):
        pack = payload()['supply']['pack_values']
        for index in (16, 17, 18):
            self.assertNotIn(index, pack['default_indices'])
        for index in (8, 9, 10, 11, 12, 20):
            self.assertIn(index, pack['default_indices'])


class DirectGrants(unittest.TestCase):
    def test_quest_bar_fields(self):
        blocks = payload()['supply']['quest']['per_quest']['blocks']
        self.assertEqual({k: v['offset'] for k, v in blocks.items()},
                         {'key0': 0x10, 'key1': 0x14, 'key2': 0x18})
        self.assertEqual(blocks['key2']['effect'],
                         'set_KeyCount2(get_KeyCount2() + bonus.key2)')

    def test_collect_all_only_touches_key2(self):
        caq = payload()['supply']['quest']['collect_all']
        self.assertEqual(caq['method']['rva'], 19955408)
        self.assertEqual(caq['field'], 'Bonus_Quest.key2 (0x18)')
        self.assertIn('not from the quest count', caq['rule'])

    def test_display_multiplier_is_separate(self):
        row = payload()['supply']['quest']['display_multiplier']
        self.assertEqual(row['offset'], 0xA0)
        self.assertIn('stored value grows by bonus.keyN only', row['note'])

    def test_pvp_key2_reachable_and_key0_not(self):
        pvp = payload()['supply']['pvp']
        self.assertEqual(pvp['routing']['18']['action'], 'set_KeyCount2(+ amount)')
        self.assertEqual(pvp['dead_types'], [16, 17, 19, 20, 21, 22])
        self.assertEqual(sorted(pvp['live_types']),
                         ['14', '15', '18', '23'])
        self.assertEqual(pvp['table']['va'], 0x779DF0)


class Callers(unittest.TestCase):
    def test_role_counts(self):
        rows = {name: row['methods'] for name, row in payload()['callers'].items()}
        self.assertEqual(rows, {'grant_via_pack_value': 21, 'grant_direct': 3,
                                'spend': 2, 'cheat_guard': 1, 'serialization': 1,
                                'display_or_state': 7})
        self.assertEqual(sum(rows.values()), 35)

    def test_twenty_one_reward_screens_share_one_funnel(self):
        rows = [row for row in payload()['callers_detail']
                if row['role'] == 'grant_via_pack_value']
        self.assertEqual(len({row['class_name'] for row in rows}), 21)
        for row in rows:
            self.assertIn('SaveDataReward', row['signature'])

    def test_spend_is_the_box_button_only(self):
        rows = [row for row in payload()['callers_detail'] if row['role'] == 'spend']
        self.assertEqual({row['class_name'].split('.')[0] for row in rows},
                         {'Board_QuestRewards'})
        self.assertTrue(all('OnPressedButtonOpenNow' in row['signature'] for row in rows))

    def test_cheat_guard_is_not_a_source(self):
        row = callers()[20068376]
        self.assertEqual(row['role'], 'cheat_guard')
        self.assertEqual(len(row['targets']), 6)

    def test_grants_are_the_three_buttons(self):
        rows = [row for row in payload()['callers_detail'] if row['role'] == 'grant_direct']
        self.assertEqual(sorted(row['method_rva'] for row in rows),
                         [19792936, 19955408, 19965788])

    def test_no_timed_regeneration(self):
        self.assertIn('no idle or timed drip', payload()['supply']['no_regeneration'])
        for rva in (19980832, 19981872, 19982936):
            self.assertEqual(callers()[rva]['targets'].count('get_KeyCount0')
                             + callers()[rva]['targets'].count('get_KeyCount1')
                             + callers()[rva]['targets'].count('get_KeyCount2'), 1)
            self.assertFalse(any(t.startswith('set_') for t in callers()[rva]['targets']))

    def test_serialization_reads_only(self):
        row = callers()[19068296]
        self.assertEqual(row['role'], 'serialization')
        self.assertEqual(sorted(row['targets']),
                         ['get_KeyCount0', 'get_KeyCount1', 'get_KeyCount2'])


if __name__ == '__main__':
    unittest.main()
