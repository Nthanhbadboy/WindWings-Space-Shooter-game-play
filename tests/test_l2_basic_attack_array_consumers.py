import gzip
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path('tools/verify').resolve()))
from l2_basic_attack_array_consumers import build, OUTPUT, ROOT, SOURCES, sha256


class BasicAttackArrayConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build()

    def test_saved_artifact_reproduces(self):
        path = ROOT / OUTPUT
        saved = json.loads(gzip.decompress(path.read_bytes()))
        self.assertEqual(saved, self.data)
        encoded = (json.dumps(self.data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        self.assertEqual(path.read_bytes(), gzip.compress(encoded, mtime=0))

    def test_source_identity_and_pins(self):
        self.assertEqual({row['path']: row['sha256'] for row in self.data['sources']}, SOURCES)
        for path, expected in SOURCES.items():
            self.assertEqual(sha256((ROOT / path).read_bytes()), expected)
        self.assertEqual(self.data['source_apk_identity']['version'], '1.3.118')
        self.assertEqual(self.data['source_apk_identity']['version_code'], 312)
        self.assertEqual(self.data['source_apk_identity']['base_apk_sha256'],
                         '6843e79347f5b0bb68e4a2f9e1b1a3152e31d0875d4821b9928ad5799a95e1e1')

    def test_target_fields_and_initializer_sizes(self):
        fields = self.data['target']['fields']
        self.assertEqual([(row['name'], row['static_offset'], row['element_type'], row['length'])
                          for row in fields],
                         [('allBasicAtk', '0x10', 'float32', 24),
                          ('allDeltaAtk', '0x18', 'float32', 24)])
        self.assertEqual([row['initialized_by']['length'] for row in fields], [24, 24])
        self.assertEqual(fields[0]['initialized_by']['first_value'], 4640.0)
        self.assertAlmostEqual(fields[1]['initialized_by']['first_value'], 0.168, places=7)

    def test_direct_consumer_and_formula_are_assembly_anchored(self):
        consumer = self.data['consumer']
        self.assertEqual((consumer['method'], consumer['rva']), ('GetPlayerPower', '0x12D5DFC'))
        self.assertEqual(consumer['direct_array_reads']['allBasicAtk']['instruction_address'], '0x12d5eac')
        self.assertEqual(consumer['direct_array_reads']['allDeltaAtk']['instruction_address'], '0x12d5edc')
        self.assertEqual(consumer['level_source']['call_address'], '0x12d5e88')
        self.assertEqual(consumer['observed_float_operations'], [
            'delta[i] * GetPlayerLevel(_indexPlayer)',
            '1.0f + previous_product',
            'basic[i] * previous_sum',
        ])
        self.assertIn('0x12d5f18: ldr      s8, [x8, #0x20]',
                      consumer['evidence_windows'][1]['instructions'])
        self.assertIn('0x12d5f4c: fmul     s9, s8, s9',
                      consumer['evidence_windows'][1]['instructions'])

    def test_display_caller_is_not_misidentified_as_array_reader(self):
        display = self.data['downstream_display']
        self.assertEqual(display['method'], 'SetPlayerInfo')
        self.assertEqual(display['calls_GetPlayerPower_at'], '0x12d13fc')
        self.assertEqual(display['textPlayerPower_field_offset'], '0x40')
        self.assertIn('0x12d142c: blr      x9', display['evidence_window']['instructions'])

    def test_scope_does_not_claim_exhaustive_global_absence_or_runtime(self):
        self.assertEqual(self.data['status'], 'confirmed_consumer_in_recovered_ARM64')
        limits = '\n'.join(self.data['scope_limits'])
        self.assertIn('does not claim an exhaustive global cross-reference', limits)
        self.assertIn('not a live runtime readback', limits)
        self.assertIn('No conclusion about combat damage', limits)


if __name__ == '__main__':
    unittest.main()
