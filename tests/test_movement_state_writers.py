import gzip
import hashlib
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path('tools/verify').resolve()))
from movement_state_writers import RAW, State, build, contract, store_hints


class MovementStateWriterTests(unittest.TestCase):
    def test_rebuild_and_hashes(self):
        raw = build()
        self.assertEqual(json.load(gzip.open(RAW / 'balloon-animation/movement-state-writers.json.gz', 'rt')), raw)
        self.assertEqual(len(raw['methods']), 21)
        self.assertTrue(all(raw['checks'].values()))
        for source in raw['sources']:
            data = Path(source['path']).read_bytes()
            if source['hash_bytes'] == 'gzip-decompressed':
                data = gzip.decompress(data)
            self.assertEqual(hashlib.sha256(data).hexdigest(), source['sha256'])

    def test_stack_is_not_this_field(self):
        self.assertEqual(store_hints('0x100: str w8, [sp, #0x4c]'), [])
        self.assertEqual(store_hints('0x100: str w8, [x1, #0x4c]'), [])
        a = store_hints('0x100: mov w8, #2\n0x104: str w8, [x0, #0x4c]')
        self.assertEqual((a[0]['field'], a[0]['value']), ('typeMove', 2))

    def test_call_clobber_and_word_alias(self):
        self.assertEqual(store_hints('0x100: bl #0x200\n0x104: str wzr, [x0, #0x4c]'), [])
        self.assertEqual(store_hints('0x100: mov w0, #1\n0x104: str wzr, [x0, #0x4c]'), [])
        a = store_hints('0x100: mov x19, x0\n0x104: bl #0x200\n0x108: str wzr, [x19, #0x4c]')
        self.assertEqual(a[0]['value'], 0)

    def test_airfree_field_contract_preserves_history(self):
        state = State(type_move=2, path='old_path', distance=42, moving=False, movein=True)
        for name in ('enable', 'set_angle', 'airfree_set_position'):
            state = contract(state, name)
        state = contract(state, 'appeared')
        self.assertEqual(state, State(type_move=2, path='old_path', distance=42, moving=True, movein=True))

    def test_combined_setter_not_equivalent_to_two_separate_setters(self):
        state = State(type_move=2, moving=True, movein=True)
        combined = contract(state, 'set_position_and_angle')
        separate = contract(contract(state, 'set_angle'), 'airfree_set_position')
        self.assertFalse(combined.moving)
        self.assertFalse(combined.movein)
        self.assertEqual(separate, state)
        self.assertEqual(combined.type_move, 2)

    def test_short_waypoints_changes_mode_but_preserves_old_waypoints(self):
        state = State(type_move=0, path='p', waypoints=((0, 0), (1, 1)), distance=5)
        result = contract(state, 'set_waypoints', ())
        self.assertEqual(result.type_move, 1)
        self.assertEqual(result.distance, 0)
        self.assertEqual(result.waypoints, state.waypoints)
        self.assertEqual(result.path, 'p')
        with self.assertRaises(ValueError):
            contract(state, 'set_waypoints', None)

    def test_valid_path_does_not_clear_old_waypoints_or_stop(self):
        state = State(type_move=1, waypoints=((0, 0), (1, 1)), moving=True, movein=True, distance=8)
        result = contract(state, 'set_path_valid', 'new_path')
        self.assertEqual((result.type_move, result.path, result.distance), (0, 'new_path', 0))
        self.assertEqual(result.waypoints, state.waypoints)
        self.assertTrue(result.moving)
        self.assertTrue(result.movein)

    def test_stop_start_not_full_reset(self):
        state = State(type_move=1, path='p', distance=8, moving=True)
        self.assertEqual(contract(contract(state, 'stop'), 'start'), state)
        with self.assertRaises(ValueError):
            contract(state, 'unknown')


if __name__ == '__main__':
    unittest.main()
