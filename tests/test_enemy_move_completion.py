import gzip
import hashlib
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path('tools/verify').resolve()))
from enemy_move_completion import build, completion_chain, path_callback_gate, fixed_exit_requested, pool_without_kill


class EnemyMoveCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.raw=build()

    def test_rebuild_and_source_hashes(self):
        with gzip.open('reverse-engineering/raw/early-waves/movement-completion.json.gz','rt') as f:
            self.assertEqual(json.load(f),self.raw)
        self.assertEqual(len(self.raw['methods']),28)
        self.assertTrue(all(self.raw['checks'].values()))
        for s in self.raw['sources']:
            b=Path(s['path']).read_bytes()
            if s['hash_bytes']=='gzip-decompressed':b=gzip.decompress(b)
            self.assertEqual(hashlib.sha256(b).hexdigest(),s['sha256'])

    def test_all_exact_movement_links_and_modes(self):
        self.assertEqual(len(self.raw['enemy_roots']),14)
        for r in self.raw['enemy_roots']:
            self.assertEqual(r['typeMoveEnded'],0)
            self.assertEqual(r['endOfPathInstruction'],2)
            self.assertEqual(r['movement_class'],'Enemy_Movement')
            self.assertEqual(r['persistent_move_event_calls'],[])
            self.assertFalse(r['isNoPool'])
            self.assertEqual(r['border'],dict(x=-10,y=10,z=-15,w=15))
        d=self.raw['declarations']
        self.assertIn('TypeMoveEnded Destroy = 0;',d['Enemy_Movement.TypeMoveEnded'])
        self.assertIn('EndOfPathInstruction Stop = 2;',d['EndOfPathInstruction'])
        self.assertIn('DestroyType WhenDone = 2;',d['DestroyType'])

    def test_callback_metadata_and_delegate_combine(self):
        def method(cls,name):return next(m for m in self.raw['methods'] if (m['class'],m['method'])==(cls,name))
        def targets(m):return {r.get('MethodAddress') for load in m['metadata_loads'] for r in load['records'] if 'MethodAddress' in r}
        d=self.raw['declarations']
        self.assertIn('Slot: 0\n\tpublic abstract void SetPosition(Vector3 position);',d['ITransform'])
        self.assertIn('Slot: 1\n\tpublic abstract void SetAngle(float angle);',d['ITransform'])
        self.assertIn('get_scale',d['UnityEngine.UIElements.ITransform'])
        self.assertNotEqual(d['ITransform'],d['UnityEngine.UIElements.ITransform'])
        self.assertIn(0x1584778,targets(method('Enemy_Controller','Appear')))
        self.assertIn(0x1584868,targets(method('Enemy_Controller','Appear')))
        m=method('Enemy_Movement','SetEventMoveEnded')
        self.assertIn(0x15869e4,targets(m))
        combines=[c for c in m['calls'] if c['target_rva']=='0x2146010']
        self.assertEqual(len(combines),2)
        self.assertTrue(all('Combine' in c['declaration']['signature'] for c in combines))

    def test_event_mode_is_not_always_pool(self):
        self.assertEqual(completion_chain(0),['stop_moving','unity_event','controller_destroy_when_done','pool_event79'])
        self.assertEqual(completion_chain(1),['stop_moving','unity_event'])
        self.assertEqual(completion_chain(0,False),['stop_moving','unity_event'])

    def test_path_callback_predicate_boundaries(self):
        e=self.raw['endpoint_epsilon']['float32']
        self.assertTrue(path_callback_gate(1,0,e))
        self.assertTrue(path_callback_gate(1,e/2,e))
        self.assertFalse(path_callback_gate(1,e,e))
        self.assertFalse(path_callback_gate(.999999,0,e))
        self.assertFalse(path_callback_gate(1,0,e,False))

    def test_fixed_exit_flags_and_strict_world_bounds(self):
        self.assertFalse(fixed_exit_requested(False,True,0,False,0,-20))
        self.assertFalse(fixed_exit_requested(True,True,0,False,0,-15))
        self.assertTrue(fixed_exit_requested(True,True,0,False,0,-15.01))
        self.assertFalse(fixed_exit_requested(True,False,2,False,11,0))
        self.assertFalse(fixed_exit_requested(True,False,1,True,11,0))
        for x,y in [(-10,0),(10,0),(0,-15),(0,15)]:
            self.assertFalse(fixed_exit_requested(True,False,2,True,x,y))
        for x,y in [(-10.01,0),(10.01,0),(0,-15.01),(0,15.01)]:
            self.assertTrue(fixed_exit_requested(True,False,2,True,x,y))

    def test_empty_active_list_does_not_increment_kills(self):
        # Restricted list model, not an executed low-kill playthrough.
        active,kills=pool_without_kill(['last-enemy'],'last-enemy',51)
        self.assertEqual((active,kills),([],51))
        self.assertEqual(pool_without_kill(active,'last-enemy',kills),([],51))
        self.assertEqual(pool_without_kill(['other'],'absent',51),(['other'],51))

    def test_slot_partition_and_airfree_exception(self):
        w=self.raw['waves']
        self.assertEqual([sum(x['slots_by_spawner'].values()) for x in w],[274,95,155])
        airfree=[row for row in w[0]['rows'] if row['spawner']=='AirFree_Spawner']
        self.assertEqual(len(airfree),1)
        bb=next(r for r in self.raw['enemy_roots'] if r['name']=='BB-36001')
        self.assertEqual(airfree[0]['enemy_roots'],[bb['identity']])
        self.assertEqual(len(bb['root_animators']),1)
        self.assertFalse(bb['isTurret'])
