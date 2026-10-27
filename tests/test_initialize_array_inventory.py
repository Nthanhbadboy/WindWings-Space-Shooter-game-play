import gzip
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path('tools/verify').resolve()))
from initialize_array_inventory import build, decode


class InitializeArrayInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build()

    def test_preserved_inventory_reproduces(self):
        saved = json.loads(gzip.decompress(Path('reverse-engineering/raw/initialize-arrays/typed-inventory.json.gz').read_bytes()))
        self.assertEqual(saved, self.data)

    def test_map_population_and_payload_roundtrip(self):
        import struct
        rows = self.data['map_arrays']
        self.assertEqual(len(rows), 576)
        self.assertEqual(sum(self.data['map_length_histogram'].values()), 576)
        for row in rows:
            payload = struct.pack('<' + 'i' * row['len'], *row['values'])
            self.assertEqual((payload + bytes.fromhex(row['trailing_hex'])).hex(), row['raw'])
            self.assertEqual(row['binding_status'], 'container_and_index_not_bound_here')

    def test_player_types_not_four_float24(self):
        rows = self.data['player_arrays']
        self.assertEqual([(r['element_type'], r['len']) for r in rows],
                         [('int32',24), ('float32',24), ('float32',24), ('float32',24), ('float32',3), ('float32',3)])
        self.assertEqual(rows[1]['values'][:6], [4500,220,2680,8000,710,1650])
        self.assertAlmostEqual(rows[2]['values'][0], 4.8, places=5)
        self.assertEqual(rows[3]['values'][:6], [218,75,186,118,236,309])

    def test_float_bits_and_alignment_tail(self):
        row = dict(raw='0000803f0000000000000000', len=1, length_valid=True)
        self.assertEqual(decode(row, 'float32')['values'], [1.0])
        self.assertEqual(decode(row, 'int32')['values'], [1065353216])
        self.assertEqual(decode(row, 'float32')['trailing_hex'], '0000000000000000')

    def test_invalid_input_rejected(self):
        for row in [dict(raw='00', len=1, length_valid=True), dict(raw='00000000',len=1,length_valid=False)]:
            with self.assertRaises(ValueError):
                decode(row, 'int32')


if __name__ == '__main__':
    unittest.main()
