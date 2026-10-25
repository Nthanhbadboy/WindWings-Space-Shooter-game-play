import gzip
import hashlib
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path('tools/verify').resolve()))
from shared_stage_victory import RAW, build, intro_gate


class SharedStageVictoryTests(unittest.TestCase):
    def test_raw_rebuild_and_sources(self):
        result = build()
        self.assertEqual(json.load(gzip.open(RAW / 'endgame-missions/shared-stage-victory.json.gz', 'rt')), result)
        self.assertEqual(len(result['methods']), 21)
        self.assertEqual(len(result['checks']), 18)
        self.assertTrue(all(result['checks'].values()))
        for source in result['sources']:
            self.assertEqual(hashlib.sha256(Path(source['path']).read_bytes()).hexdigest(), source['sha256'])

    def test_stage_one_two_first_run_and_replay_gates(self):
        self.assertEqual(intro_gate(0, 0, False), dict(stage1=True, stage2=False, stage3=False))
        self.assertEqual(intro_gate(1, 1, False), dict(stage1=False, stage2=True, stage3=False))
        self.assertFalse(intro_gate(0, 2, False)['stage1'])
        self.assertFalse(intro_gate(1, 2, False)['stage2'])

    def test_stage_three_gate_not_index_tutorial(self):
        self.assertTrue(intro_gate(2, 0, False)['stage3'])
        self.assertTrue(intro_gate(2, 9, False)['stage3'])
        self.assertFalse(intro_gate(2, 2, True)['stage3'])
        self.assertFalse(any(intro_gate(3, 0, False).values()))

    def test_overlay_is_not_shared_score_predicate(self):
        raw = build()
        checks = raw['checks']
        for key in ('normal_kill_result_calls_shared_scorer', 'player_health_zero_overrides_false',
                    'result_closure_enters_one_openboard', 'board_init_uses_same_missions',
                    'board_tutorial_overlay_has_own_gate', 'continue_has_tutorial_routing'):
            self.assertTrue(checks[key])
        methods = {(r['class_name'], r['method']): r['asm'] for r in raw['methods']}
        self.assertIn('#0x14f4a14', methods['Board_Endgame', 'SetupTut'])
        self.assertNotIn('#0x14f4a14', methods['Board_Endgame', 'GetMissionCompleted'])


if __name__ == '__main__':
    unittest.main()
