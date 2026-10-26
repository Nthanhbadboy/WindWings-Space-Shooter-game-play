import gzip
import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path('tools/verify').resolve()))
from early_stage_denominators import build
from enemy_exit_missions import normal_mission_result


class EarlyStageDenominatorsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence=build()

    def test_rebuild_and_source_integrity(self):
        d=self.evidence
        with gzip.open('reverse-engineering/raw/early-waves/mission-denominators.json.gz','rt') as f:
            self.assertEqual(d,json.load(f))
        self.assertTrue(all(d['checks'].values()))
        for source in d['sources']:
            self.assertEqual(hashlib.sha256(Path(source['path']).read_bytes()).hexdigest(),source['sha256'])
        for m in d['methods']:
            self.assertEqual(hashlib.sha256(Path(m['source']).read_bytes()).hexdigest(),m['source_sha256'])
            self.assertFalse(m['inventory'].get('size_capped'))

    def test_denominator_is_filtered_not_raw_slot_sum(self):
        waves=self.evidence['waves']
        self.assertEqual([w['denominator'] for w in waves],[262,87,151])
        self.assertEqual([w['excluded_ids'] for w in waves],[{'38001':12},{'38001':8},{'38001':4}])
        self.assertEqual([w['denominator']+sum(w['excluded_ids'].values()) for w in waves],[274,95,155])
        self.assertEqual(len(self.evidence['ignored_ids']),31)

    def test_start_marker_is_empty_not_a_special_native_skip(self):
        for w in self.evidence['waves']:
            rows=w['calls'];self.assertNotIn(5,[r['spawn_type'] for r in rows])
            start=[r for r in rows if r['spawn_type']==6]
            self.assertEqual(len(start),1);self.assertEqual(start[0]['pooling_ids'],[])
            self.assertTrue(all(r['number_serialized']==0 for r in rows))

    def test_controller_points_to_concrete_base_destroy(self):
        self.assertEqual(len(self.evidence['enemy_roots']),14)
        for e in self.evidence['enemy_roots']:
            self.assertEqual(e['destroy_class'],'Enemy_Destroy')
            self.assertEqual(e['destroy_identity']['serialized_file'],e['identity']['serialized_file'])
        self.assertIn('public class Enemy_Sub : Sub_Character',self.evidence['declarations']['Enemy_Sub'])
        self.assertIn('public abstract class Sub_Character : Sub_Object',self.evidence['declarations']['Sub_Character'])

    def test_normal_tier_boundaries_with_real_static_denominators(self):
        arrays=json.load(gzip.open('reverse-engineering/raw/ui-audit/enemy-exit-missions.json.gz','rt'))['normal_mission_arrays']
        stages=self.evidence['stages']
        self.assertEqual([s['denominator'] for s in stages],[262,238])
        self.assertEqual([s['normal_thresholds_by_mode']['0'] for s in stages],[[52,117,209],[47,107,190]])
        for s in stages:
            for mode,thresholds in s['normal_thresholds_by_mode'].items():
                for tier,threshold in enumerate(thresholds):
                    coeffs=arrays[mode]['float32']
                    self.assertEqual(normal_mission_result(threshold,s['denominator'],coeffs),tier)
                    self.assertEqual(normal_mission_result(threshold-1,s['denominator'],coeffs),tier-1)
