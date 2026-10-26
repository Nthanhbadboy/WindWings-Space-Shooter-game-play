import gzip
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path('tools/verify').resolve()))
from l2_save_schema_end_to_end import build, OUTPUT, ROOT, SOURCES, sha256


class SaveSchemaEndToEndTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build()

    def test_artifact_reproduces_byte_for_byte(self):
        path = ROOT / OUTPUT
        saved = json.loads(gzip.decompress(path.read_bytes()))
        self.assertEqual(saved, self.data)
        encoded = (json.dumps(self.data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        self.assertEqual(path.read_bytes(), gzip.compress(encoded, mtime=0))

    def test_source_pins_and_recovery_identity(self):
        self.assertEqual({row['path']: row['sha256'] for row in self.data['source_pins']}, SOURCES)
        for path, expected in SOURCES.items():
            self.assertEqual(sha256((ROOT / path).read_bytes()), expected)
        ident = self.data['source_apk_identity']
        self.assertEqual(ident['xapk_sha256'], 'f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e')
        self.assertEqual(ident['global_metadata_sha256'], '449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69')
        self.assertEqual(ident['libil2cpp_sha256'], '9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99')
        self.assertEqual(ident['dump_decompressed_sha256'], '8996f7cb9ec9b8c0b9be7a81c746328e632189699a72beb53fdb7364fa168d5c')

    def test_four_slot_key_schema_and_wrapper_chain(self):
        schema = self.data['scope']['schema']
        self.assertEqual(schema['key_format'], 'PLAYER_DEVICE_{ship}_{slot}')
        self.assertEqual(schema['slot_count'], 4)
        self.assertEqual(schema['normal_missing_default'], -1)
        chain = self.data['scope']['storage_wrapper_chain']
        self.assertEqual(chain[1]['target_rva'], '0x277CC10')
        self.assertEqual(chain[3]['target_rva'], '0x277CCA0')
        self.assertIn('No PlayerPrefs.Save call', self.data['scope']['writer']['explicit_flush'])
        self.assertIn('shorter than four', ' '.join(self.data['scope']['writer']['behavior']))

    def test_lookup_gap_and_id_vs_instance_id_distinction(self):
        record = self.data['device_record_and_stat']
        self.assertEqual(record['lookup']['rva'], '0x12546D0')
        self.assertIn('implementation body was not present', record['lookup']['gap'])
        fields = {row['name']: row['offset'] for row in record['fields']}
        self.assertEqual(fields, {'id': '0x10', 'lv': '0x14', 'rank': '0x18', 'instanceId': '0x1C'})
        self.assertIn('Device.id is a distinct', self.data['scope']['schema']['value_semantics'])

    def test_consumer_paths_and_scoped_stat_formula(self):
        consumers = {row['type']: row for row in self.data['load_consumers']}
        self.assertIn('GetDevice(saved value) as instanceId', consumers['Player_Attack']['static_path'])
        self.assertTrue(any('GetStatValue2' in step for step in consumers['Player_Attack']['static_path']))
        self.assertEqual(consumers['Player_Health']['observed_category'], 'Device.id 1000..1999')
        stat = self.data['device_record_and_stat']['GetStatValue2']['observed_formula']
        self.assertIn('Device.id / 1000', stat)
        self.assertIn('Device.rank', stat)
        self.assertIn('Device.lv + 1', stat)

    def test_evidence_boundaries_do_not_overclaim_global_schema_or_runtime(self):
        self.assertEqual(self.data['status'], 'bounded_static_device_save_load_trace_not_global_schema_or_runtime')
        limits = '\n'.join(self.data['scope_limits'])
        self.assertIn('not a complete global save schema', limits)
        self.assertIn('no live app execution', limits)
        self.assertIn('No exhaustive global caller/callee search', limits)


if __name__ == '__main__':
    unittest.main()
