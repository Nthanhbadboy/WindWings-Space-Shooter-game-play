import gzip
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/verify'))
from tutorial_consumer_flow import decode_manager_dispatch


class TutorialConsumerTests(unittest.TestCase):
    def test_dispatch_uses_signed_selector_offset_not_text_order(self):
        entries = decode_manager_dispatch('0029233d41555d634f74', 0x14f482c)
        self.assertEqual([r['event_state'] for r in entries], list(range(-1, 9)))
        self.assertEqual(entries[2], {'event_state':1,'target':'0x14f48b8'})
        self.assertEqual(entries[8], {'event_state':7,'target':'0x14f4968'})
        self.assertEqual(entries[-1]['target'], '0x14f49fc')

    def test_dispatch_rejects_truncated_table(self):
        for value in ('', '00', '00'*11):
            with self.assertRaises(ValueError):
                decode_manager_dispatch(value, 0x14f482c)

    def test_raw_rodata_and_preserved_consumer_agree(self):
        path = Path('reverse-engineering/raw/ui-audit')
        ro = json.loads((path/'stage23-rodata.json').read_text())
        with gzip.open(path/'tutorial-consumer-flow.json.gz','rt') as f:
            evidence = json.load(f)
        self.assertTrue(all(evidence['checks'].values()))
        self.assertEqual(evidence['native_sha256'], ro['native_sha256'])
        d = ro['manager_dispatch']
        self.assertEqual(decode_manager_dispatch(d['bytes_hex'], int(d['branch_base'],16)), d['entries'])
        self.assertEqual(evidence['startup_callback_slot']['records'][0]['MethodAddress'], 0x14f47cc)

    def test_loading_name_does_not_override_scene_enum(self):
        with gzip.open('reverse-engineering/raw/ui-audit/tutorial-consumer-flow.json.gz','rt') as f:
            evidence = json.load(f)
        self.assertIn('ScenesManager.Scene Game = 2', evidence['declarations']['ScenesManager.Scene'])
        methods = {(r['class'],r['method']):r for r in evidence['methods']}
        calls = methods['Board_Endgame','LoadToLoading']['calls']
        self.assertTrue(any(c['target_rva'] == '0x141b488' for c in calls))
