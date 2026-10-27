import sys
import gzip
import json
import hashlib
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/verify'))
from runtime_probe_audit import classify_jobs


class RuntimeProbeAuditTests(unittest.TestCase):
    def test_green_job_with_skipped_probe_is_not_runtime_evidence(self):
        result=classify_jobs([{'name':'ramus device probe','conclusion':'success','steps':[
            {'name':'Start session','conclusion':'skipped'},
            {'name':'Probe game state','conclusion':'skipped'}]}])
        self.assertEqual(result['classification'],'no_successful_game_state_probe')
        self.assertEqual(result['session_step'],'skipped')

    def test_successful_probe_still_requires_payload_review(self):
        result=classify_jobs([{'name':'ramus device probe','conclusion':'success','steps':[
            {'name':'Probe game state','conclusion':'success'}]}])
        self.assertEqual(result['classification'],'payload_review_required')

    def test_primary_apk_getter_evidence_retains_write_and_identity(self):
        root=Path(__file__).resolve().parents[1]
        p=root/'reverse-engineering/raw/runtime-probe/getter-observer-effect.json.gz'
        raw=json.load(gzip.open(p,'rt'))
        self.assertEqual(hashlib.sha256((root/raw['source']).read_bytes()).hexdigest(),raw['sha256'])
        self.assertTrue(all(raw['checks'].values()))
        calls={c['target_rva']:c.get('declaration') for c in raw['calls']}
        self.assertEqual(calls['0x12b1f68']['class'],'Stage_Datas')
        self.assertIn('get_StageTarget',calls['0x12b1f68']['signature'])
        self.assertEqual(calls['0x13f1a04']['class'],'PlayerPreferences')
        self.assertTrue(any(r.get('Value')=='TUTORIAL' for load in raw['metadata_loads'] for r in load['records']))

    def test_missing_job_is_not_success(self):
        self.assertEqual(classify_jobs([])['classification'],'no_successful_game_state_probe')


if __name__=='__main__':unittest.main()
