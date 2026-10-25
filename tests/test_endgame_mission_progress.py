import gzip
import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path('tools/verify').resolve()))
from endgame_mission_progress import build, normal_progress


class EndgameMissionProgressTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=build()
        cls.methods={(m['class'],m['method']):m for m in cls.raw['methods']}

    def test_rebuild_and_source_hashes(self):
        with gzip.open('reverse-engineering/raw/endgame-missions/mission-progress-flow.json.gz','rt') as f:
            self.assertEqual(self.raw,json.load(f))
        self.assertTrue(all(self.raw['checks'].values()))
        for s in self.raw['sources']:
            self.assertEqual(hashlib.sha256(Path(s['path']).read_bytes()).hexdigest(),s['sha256'])
        for m in self.raw['methods']:
            self.assertEqual(hashlib.sha256(Path(m['source']).read_bytes()).hexdigest(),m['source_sha256'])
            self.assertFalse(m['inventory'].get('size_capped'))

    def test_exact_mission_order_and_continue_target(self):
        p=self.raw['prefab'];self.assertEqual(p['resource_key'],'boards/board_endgame')
        self.assertEqual(p['node_count'],1070)
        self.assertEqual([r['path'].rsplit('/',1)[1] for r in p['normal_rows']],['Mission (0)','Mission (1)','Mission (2)'])
        self.assertTrue(all(r['fields']['anim']['type']=='Animator' for r in p['normal_rows']))
        self.assertEqual(p['continue']['persistent_call']['m_Target']['m_PathID'],p['board_component_path_id'])
        self.assertFalse(p['continue']['active_in_prefab']) # Not a runtime visibility assertion.

    def test_all_restricted_replay_states_are_monotonic(self):
        for saved in range(4):
            for result in range(-1,3):
                d=normal_progress(saved,result)
                self.assertGreaterEqual(d['saved_after'],saved)
                self.assertEqual(d['global_star_delta'],d['saved_after']-saved)
                self.assertEqual(d['new_rows'],list(range(saved,max(saved,result+1))))
                self.assertEqual(normal_progress(d['saved_after'],result)['global_star_delta'],0)
        self.assertEqual(normal_progress(3,0),{'old_flags':[True,True,True],'new_rows':[],'saved_after':3,'global_star_delta':0})

    def test_stage_thresholds_now_map_to_saved_stars(self):
        d=json.load(gzip.open('reverse-engineering/raw/early-waves/mission-denominators.json.gz','rt'))
        for s in d['stages']:
            self.assertEqual(len(s['normal_thresholds_by_mode']['0']),3)
            for tier in range(3):
                p=normal_progress(0,tier)
                self.assertEqual(p['saved_after'],tier+1)
                self.assertEqual(p['global_star_delta'],tier+1)

    def test_trigger_strings_and_preference_keys_are_raw_metadata(self):
        def strings(cls,method):
            return {r['Value'] for load in self.methods[cls,method]['metadata_loads'] for r in load['records'] if isinstance(r.get('Value'),str)}
        self.assertTrue({'None','Collected','txt_completed'}<=strings('Stage_Mission','InitMission'))
        self.assertIn('Clear',strings('Stage_Mission','ClearMission'))
        self.assertTrue({'StarStageMaster','_'}<=strings('Stage_Datas','SetStarStageMaster'))
        self.assertIn('StarCount',strings('GameDatas','set_StarCount'))
        calls=self.methods['PlayerPreferences','SetInt']['calls']
        self.assertTrue(any((c.get('declaration') or {}).get('class')=='PlayerPrefs' for c in calls))

    def test_target_advance_has_no_local_victory_bool_predicate(self):
        # This guards the local native block, NOT runtime reachability of defeat.
        asm=self.raw['target_advance_asm']
        self.assertNotRegex(asm,r'\b[wx]20\b')
        self.assertIn('0x14f09b4: bl       #0x12bac5c',asm)
