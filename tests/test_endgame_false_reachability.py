import gzip
import hashlib
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path('tools/verify').resolve()))
from endgame_false_reachability import build, conditional_result, conditional_target


class EndgameFalseReachabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.raw=build()

    def test_rebuild_and_pinned_sources(self):
        with gzip.open('reverse-engineering/raw/endgame-missions/false-result-reachability.json.gz','rt') as f:
            self.assertEqual(json.load(f),self.raw)
        self.assertEqual(len(self.raw['methods']),15)
        self.assertTrue(all(self.raw['checks'].values()))
        for s in self.raw['sources']:
            blob=Path(s['path']).read_bytes()
            if s['hash_bytes']=='gzip-decompressed':blob=gzip.decompress(blob)
            self.assertEqual(hashlib.sha256(blob).hexdigest(),s['sha256'])

    def test_interfaces_are_parsed_and_dispatch_slots_are_explicit(self):
        d=self.raw['declarations']
        self.assertIn('Slot: 1\n\tpublic abstract float GetCurrentHealth();',d['IHealth'])
        self.assertIn('Slot: 0\n\tpublic abstract void SetVictory();',d['IPlayer'])
        self.assertIn('public bool victory; // 0x10',d['GP_Endgame.<>c__DisplayClass4_0'])
        self.assertIn('public const GameState Playing = 1;',d['GameState'])

    def test_callback_metadata_connects_manager_and_closure(self):
        def targets(cls,method):
            m=next(m for m in self.raw['methods'] if (m['class'],m['method'])==(cls,method))
            return {r.get('MethodAddress') for l in m['metadata_loads'] for r in l['records'] if 'MethodAddress' in r}
        self.assertIn(0x14f6190,targets('GP_Manager','<Start>b__11_7'))
        self.assertIn(0x14f13ac,targets('GP_Endgame._CheckEndgame_d__4','MoveNext'))

    def test_result_and_health_branches(self):
        self.assertFalse(conditional_result(-1,100))
        for tier in range(3):
            self.assertTrue(conditional_result(tier,100))
            self.assertFalse(conditional_result(tier,0))
        # Native comparison is exact ==0, not a newly invented <=0 predicate.
        self.assertTrue(conditional_result(0,-1))

    def test_target_gates_and_max_stage_clamp(self):
        self.assertEqual(conditional_target(0,1,1,0,99),2)
        self.assertEqual(conditional_target(0,2,2,0,99),3)
        self.assertEqual(conditional_target(0,1,2,0,99),2) # replay != target
        self.assertEqual(conditional_target(1,2,2,0,99),2) # other game mode
        self.assertEqual(conditional_target(0,9,9,0,99),9) # zone cap
        self.assertEqual(conditional_target(0,2,2,0,2),2) # MAX_STAGE_INDEX cap

    def test_conditional_false_input_still_passes_target_gate(self):
        # Symbolic state witness, NOT an executed playthrough or proof that
        # arbitrary low kill counts can occur with actual wave geometry.
        self.assertFalse(conditional_result(-1,100))
        for stage in (1,2):
            self.assertEqual(conditional_target(0,stage,stage,0,99),stage+1)
        self.assertFalse(conditional_result(2,0))
        self.assertEqual(conditional_target(0,2,2,0,99),3)

    def test_wait_constructor_types_are_not_interchanged(self):
        calls=[c for m in self.raw['methods'] for c in m['calls']]
        for address,name in [('0x2786508','WaitForSeconds'),('0x2786604','WaitForSecondsRealtime')]:
            found=[c for c in calls if c['target_rva']==address]
            self.assertTrue(found)
            self.assertTrue(all(c['declaration']['class']==name for c in found))

    def test_move_dispatch_bytes_and_float_literals(self):
        ro=self.raw['move_rodata']
        self.assertEqual(ro['move_player_dispatch']['bytes_hex'],'00162d8d')
        values={f['va']:f['float32'] for f in ro['movement_floats']}
        self.assertAlmostEqual(values['0x756a58'],1e-10,delta=1e-17)
        self.assertAlmostEqual(values['0x7570e0'],0.3,places=7)

    def test_stage2_stage3_threshold_witness_is_below_first_tier(self):
        from enemy_exit_missions import normal_mission_result, f32
        d=json.load(gzip.open('reverse-engineering/raw/early-waves/mission-denominators.json.gz','rt'))
        for stage in d['stages']:
            threshold=stage['normal_thresholds_by_mode']['0'][0]
            # Same coefficients preserved/verified by the earlier raw verifier.
            result=normal_mission_result(threshold-1,stage['denominator'],[f32(v) for v in (0.2,0.45,0.8)])
            self.assertEqual(result,-1)
            self.assertFalse(conditional_result(result,100))
