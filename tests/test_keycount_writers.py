"""Contracts for report 176: who writes `GameDatas.KeyCount0/1/2`.

132 left an open item because its scan saw calls, not stores. 176 scans stores — but the
premise was wrong: 0x50/0x54/0x58 are instance fields on the holder behind the singleton
slot 0x2adb000+0xaf8, so a "static store" cannot exist. Following the chain finds exactly
six writers, all accessors of the same class: three setters and the three getters that
cache the value they lazily load.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import keycount_writers as KW  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_keycount_writers.json.gz'
PIN_BYTES = 9416
PIN_SHA = 'f44fdb903dc2e67c651aedfa38fc725e779f398626bcc1c4281253eff93dbcdc'

GETTERS = {20070740: (20070896, 0x50), 20071068: (20071224, 0x54), 20071396: (20071552, 0x58)}
SETTERS = {20070940: (20071048, 0x50), 20071268: (20071376, 0x54), 20071596: (20071704, 0x58)}


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        _, packed = KW.build(None)
        self.assertEqual(packed, ARTIFACT.read_bytes())

    def test_static_only(self):
        self.assertEqual(payload()['evidence'], 'STATIC_ONLY_ORIGINAL_APK')

    def test_every_check_passed(self):
        rows = payload()['checks']
        self.assertEqual(len(rows), 14)
        self.assertEqual([row['name'] for row in rows if not row['passed']], [])


class Writers(unittest.TestCase):
    def rows(self):
        return {row['method_rva']: row for row in payload()['writers']}

    def test_six_writers(self):
        self.assertEqual(sorted(self.rows()), sorted(list(GETTERS) + list(SETTERS)))

    def test_all_in_game_datas(self):
        self.assertEqual({row['klass'] for row in payload()['writers']}, {'GameDatas'})

    def test_three_getters_three_setters(self):
        rows = payload()['writers']
        self.assertEqual(len([r for r in rows if r['role'] == 'getter']), 3)
        self.assertEqual(len([r for r in rows if r['role'] == 'setter']), 3)

    def test_the_store_sites(self):
        rows = self.rows()
        for rva, (store, offset) in list(GETTERS.items()) + list(SETTERS.items()):
            self.assertEqual(rows[rva]['rva'], store)
            self.assertEqual(rows[rva]['offset'], offset)

    def test_each_accessor_writes_its_own_field(self):
        rows = self.rows()
        self.assertEqual(rows[20070940]['field'], 'KeyCount0')
        self.assertEqual(rows[20071268]['field'], 'KeyCount1')
        self.assertEqual(rows[20071596]['field'], 'KeyCount2')

    def test_the_getters_cache_so_they_are_writers(self):
        rows = self.rows()
        self.assertEqual(rows[20070740]['op'], 'w19, [x9, #0x50]')
        self.assertEqual(rows[20070940]['op'], 'w19, [x8, #0x50]')


class Premise(unittest.TestCase):
    def test_the_item_said_static(self):
        self.assertIn('statics 0x50/0x54/0x58', payload()['premise']['claimed'])

    def test_the_truth_is_an_instance_field(self):
        self.assertIn('instance fields', payload()['premise']['actual'])

    def test_the_chain_is_written_out(self):
        chain = payload()['premise']['chain']
        self.assertEqual([row['step'] for row in chain],
                         ['singleton slot', 'object behind it', 'counter holder'])
        self.assertEqual((chain[0]['page'], chain[0]['offset']), (0x2adb000, 0xaf8))
        self.assertEqual(chain[2]['addend'], 0xb8)

    def test_the_chain_is_visible_in_the_bytes(self):
        window = {row['rva']: row['op'] for row in payload()['premise']['window']}
        self.assertEqual(window[20070952], 'x20, #0x2adb000')
        self.assertEqual(window[20070960], 'x20, [x20, #0xaf8]')
        self.assertEqual(window[20071004], 'x0, [x20]')
        self.assertEqual(window[20071036], 'x8, [x0, #0xb8]')
        self.assertEqual(window[20071048], 'w19, [x8, #0x50]')

    def test_no_static_cell_write_exists(self):
        self.assertEqual(payload()['premise']['actual'].count('not statics'), 1)


class Coverage(unittest.TestCase):
    def test_native(self):
        native = payload()['coverage']['native']
        self.assertEqual((native['methods'], native['instructions']), (1788, 159059))
        self.assertEqual(len(native['scans']), 6)
        self.assertEqual(native['scans_on_disk'], 8)

    def test_asm(self):
        asm = payload()['coverage']['asm']
        self.assertEqual((asm['files'], asm['instructions']), (139, 138226))

    def test_offsets_alone_are_useless(self):
        naive = payload()['coverage']['naive_offset_only_writes']
        self.assertGreater(naive, 100)
        self.assertEqual(naive // 6, 17)

    def test_the_two_corpora_agree(self):
        native = sorted(row['rva'] for row in payload()['writers'])
        expected = sorted([store for store, _ in GETTERS.values()]
                          + [store for store, _ in SETTERS.values()])
        self.assertEqual(native, expected)


class Limits(unittest.TestCase):
    def test_it_narrows_rather_than_closes(self):
        text = ' '.join(payload()['limits'])
        self.assertIn('coverage is the corpus, not the binary', text)
        self.assertIn('MODEL_NOT_MEASURED', text)

    def test_provenance_hashes_match_the_files(self):
        prov = payload()['provenance']
        for row in prov['inputs'] + prov['asm']:
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            self.assertEqual(digest, row['sha256'], row['path'])
        self.assertEqual(len(prov['inputs']), 8)
        self.assertEqual(len(prov['asm']), 139)


if __name__ == '__main__':
    unittest.main()
