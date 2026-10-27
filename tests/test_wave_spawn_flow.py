import gzip
import hashlib
import json
import unittest
from pathlib import Path


class WaveSpawnFlowTests(unittest.TestCase):
    def setUp(self):
        with gzip.open('reverse-engineering/raw/ui-audit/wave-spawn-flow.json.gz','rt') as f:
            self.raw=json.load(f)
        self.methods={(m['class'],m['method']):m for m in self.raw['methods']}

    def test_checks_and_source_hashes_are_current(self):
        self.assertTrue(all(self.raw['checks'].values()))
        for method in self.raw['methods']:
            self.assertFalse(method['inventory'].get('size_capped',False))
            self.assertEqual(hashlib.sha256(Path(method['source']).read_bytes()).hexdigest(),method['source_sha256'])

    def test_spawn_events_are_not_tutorial_callback_numbers(self):
        enum=self.raw['declarations']['EventID']
        for text in ('EventID SpawnEndedEvent = 73','EventID WaveEndedEvent = 74','EventID OnSpawnEnemy = 78'):
            self.assertIn(text,enum)
        self.assertEqual(self.raw['slots']['0x2ae8f50']['records'][0]['MethodAddress'],0x14f6104)

    def test_marker_and_enemy_fields_are_distinct(self):
        self.assertIn('SpawnTypes EndMapPoint = 5',self.raw['declarations']['SpawnTypes'])
        self.assertIn('SpawnTypes StartWavePoint = 6',self.raw['declarations']['SpawnTypes'])
        self.assertIn('public int countPoints; // 0x10',self.raw['declarations']['Wave.<>c__DisplayClass7_0'])
        self.assertIn('public List<GameObject> listActiveEnemies; // 0x70',self.raw['declarations']['GP_Datas'])

    def test_trigger_blocks_endgame_not_only_playing(self):
        asm=self.methods['Call_Point','FixedUpdate']['asm']
        self.assertIn('0x1465ae4: cmp      w8, #3',asm)
        self.assertIn('GameState Endgame = 3',self.raw['declarations']['GameState'])
        poll=self.methods['GP_Endgame._CheckEndgame_d__4','MoveNext']['asm']
        self.assertIn('0x14f1554: cmp      w8, #1',poll)
        self.assertIn('GameState Playing = 1',self.raw['declarations']['GameState'])
