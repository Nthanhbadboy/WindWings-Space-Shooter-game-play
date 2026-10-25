import gzip
import hashlib
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path('tools/verify').resolve()))
from balloon_lifecycle import RAW, build, gun_fixed_gate, movement_routes, scroll_y
from enemy_move_completion import fixed_exit_requested


class BalloonLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = build()

    def test_rebuild_checks_and_sources(self):
        self.assertEqual(json.load(gzip.open(RAW / 'balloon-animation/lifecycle-parent-scroll.json.gz', 'rt')), self.raw)
        self.assertEqual(len(self.raw['methods']), 40)
        self.assertEqual(len(self.raw['checks']), 26)
        self.assertTrue(all(self.raw['checks'].values()))
        for source in self.raw['sources']:
            data = Path(source['path']).read_bytes()
            if source['hash_bytes'] == 'gzip-decompressed':
                data = gzip.decompress(data)
            self.assertEqual(hashlib.sha256(data).hexdigest(), source['sha256'])

    def test_first_pool_get_overload_only_and_metadata(self):
        r = next(r for r in self.raw['methods'] if (r['class_name'], r['method']) == ('PoolingManager', 'GetObject'))
        self.assertEqual(r['signature'], 'public static GameObject GetObject(int index) { }')
        r = next(r for r in self.raw['methods'] if (r['class_name'], r['method']) == ('PoolingManager', 'getObject'))
        names = [z.get('Name', '') for m in r['metadata_loads'] for z in m['records']]
        self.assertIn('Method$UnityEngine.Object.Instantiate<GameObject>()', names)
        self.assertIn('Method$System.Collections.Generic.List<GameObject>.RemoveAt()', names)
        self.assertEqual(self.raw['integer_float_bits'], dict(pool_pref_pos=-99, get_object_default_pos=-255))

    def test_scroll_algebra_not_background_boost(self):
        self.assertEqual(scroll_y(10, .5, 2, 3, 4), -2)
        self.assertEqual(scroll_y(10, .5, 2, 3), 7)
        self.assertEqual(scroll_y(10, 0, 2, 3), 10)
        self.assertEqual(scroll_y(10, .5, 0, 3), 10)
        self.assertEqual(scroll_y(10, .5, -2, 3), 13)

    def test_gun_gate_border_timer_stun(self):
        self.assertFalse(gun_fixed_gate(False, 0, 10, 20, False, False))
        self.assertFalse(gun_fixed_gate(True, 0, 10, 20, True, False))
        self.assertTrue(gun_fixed_gate(True, 0, 10, 20, False, False))
        self.assertFalse(gun_fixed_gate(True, 1, 19, 20, False, False))
        self.assertTrue(gun_fixed_gate(True, 1, 20, 20, True, False))
        self.assertFalse(gun_fixed_gate(True, 1, 20, 20, False, True))

    def test_serialized_guns_and_no_death_hooks(self):
        a, b = self.raw['guns']
        self.assertEqual((a['path_id'], b['path_id']), (690037, 639146))
        for g in (a, b):
            t = g['tree']
            self.assertEqual((t['delayShoot'], t['typeDelay'], t['idBlt']), (1, 0, 80054))
            self.assertFalse(t['bltPinMap'])
            self.assertEqual(t['allGunDatas'], [])
            self.assertEqual(t['eventEnded']['m_PersistentCalls']['m_Calls'], [])
        self.assertAlmostEqual(a['tree']['shotRate'], .15, places=6)
        self.assertAlmostEqual(b['tree']['bRate'], .1, places=6)
        self.assertNotIn(' OnDisable(', self.raw['declarations']['SpaceShooter.Machine_Gun_Attack'])

    def test_restricted_no_path_non_turret_not_generic_escape(self):
        self.assertEqual(movement_routes(True, 0, False, False, False), [])
        # Even an out-of-screen animated position cannot enable these disabled gates.
        for x, y in [(-12.41, 7.33), (500, -500), (0, -100)]:
            self.assertFalse(fixed_exit_requested(True, False, 0, False, x, y))
        self.assertEqual(movement_routes(True, 0, True, False, False), ['path'])
        self.assertEqual(movement_routes(True, 2, False, False, True), ['linear_update', 'linear_boundary'])
        self.assertEqual(movement_routes(False, 2, True, True, True), [])

    def test_namespace_and_runtime_fields_not_serialized_movement_assumption(self):
        d = self.raw['declarations']['SpaceShooter.EnemySystem.Enemy_Movement']
        self.assertIn('private Enemy_Movement.TypeMove typeMove; // 0x4C', d)
        self.assertIn('private VertexPath path; // 0x50', d)
        self.assertIn('private Transform parentTerrains; // 0x30', self.raw['declarations']['SpaceShooter.SpawnSystem.PinTerrain_Spawner'])

    def test_inventories_not_capped(self):
        self.assertTrue(all(not r['inventory']['size_capped'] for r in self.raw['methods']))
        self.assertEqual(self.raw['status'], 'PROVISIONAL_STATIC_NOT_PLAYBACK')


if __name__ == '__main__':
    unittest.main()
