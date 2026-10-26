import gzip
import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path('tools/verify').resolve()))
from enemy_exit_missions import build, normal_mission_result


class EnemyExitMissionsTests(unittest.TestCase):
    def test_rebuild_and_source_hashes(self):
        d=build();stored=json.load(gzip.open('reverse-engineering/raw/ui-audit/enemy-exit-missions.json.gz','rt'))
        self.assertEqual(d,stored);self.assertTrue(all(d['checks'].values()))
        for m in d['methods']:
            self.assertEqual(hashlib.sha256(Path(m['source']).read_bytes()).hexdigest(),m['source_sha256'])
            self.assertFalse(m['inventory'].get('size_capped'))

    def test_raw_arrays_have_exact_hash_identity(self):
        d=build()
        for row in d['normal_mission_arrays'].values():
            self.assertEqual(hashlib.sha256(bytes.fromhex(row['bytes_hex'])).hexdigest().upper(),row['field'].rsplit('.',1)[1])
        self.assertEqual([[round(x,2) for x in d['normal_mission_arrays'][str(i)]['float32']] for i in range(3)],[[.20,.45,.80],[.35,.60,.98],[.50,.80,1.0]])
        self.assertIn('public static int ModeCurrent; // 0x34',d['declarations']['Stage_Datas'])

    def test_restricted_normal_model_is_not_100_percent_requirement(self):
        p=build()['normal_mission_arrays']['0']['float32']
        self.assertEqual([normal_mission_result(k,100,p) for k in (19,20,44,45,79,80,100)],[-1,0,0,1,1,2,2])
        # Truncation, not ceil: 20% of denominator4 is a threshold of0.
        # Synthetic arithmetic test, NOT a real-stage assertion.
        self.assertEqual(normal_mission_result(0,4,p),0)

    def test_pool_and_death_are_different_events(self):
        d=build();e=d['declarations']['EventID']
        for text in ('OnSpawnEnemy = 78','OnPoolEnemy = 79','OnEnemyDie = 19'):self.assertIn(text,e)
        self.assertIn('DestroyType WhenDone = 2',d['declarations']['DestroyType'])
        self.assertIn('public List<GameObject> listActiveEnemies; // 0x70',d['declarations']['GP_Datas'])
