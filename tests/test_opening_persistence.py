import gzip
import hashlib
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path('tools/verify').resolve()))
from opening_persistence import (build, tutorial_read, stage_target_read, drone_used_read,
                                 drone_unlocked_read, persistence_key)


class OpeningPersistenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build()

    def test_snapshot_and_sources_reproduce(self):
        raw = json.load(gzip.open('reverse-engineering/raw/persistence/opening-contracts.json.gz', 'rt'))
        self.assertEqual(raw, self.data)
        self.assertEqual(len(raw['methods']), 41)
        self.assertEqual(len(raw['checks']), 25)
        self.assertTrue(all(raw['checks'].values()))
        for source in raw['sources']:
            path = Path(source['path'])
            content = path.read_bytes()
            if path.suffix == '.gz':
                content = gzip.decompress(content)
            self.assertEqual(hashlib.sha256(content).hexdigest(), source['sha256_decompressed'])

    def test_derived_contract_links_raw_and_methods(self):
        derived = json.loads(Path('datas/opening_persistence.json').read_text())
        evidence = gzip.decompress(Path(derived['raw_evidence']).read_bytes())
        self.assertEqual(hashlib.sha256(evidence).hexdigest(), derived['raw_evidence_sha256_decompressed'])
        self.assertEqual(derived['contracts'], self.data['contracts'])
        self.assertEqual(len(derived['contracts']), 8)
        method_ids = {f"{r['class_name']}.{r['method']}" for r in self.data['methods']}
        for row in derived['contracts']:
            self.assertEqual(row['value_type'], 'int32')
            self.assertEqual(row['store'], 'Unity.PlayerPrefs')
            self.assertTrue(set(row['evidence_method_ids']) <= method_ids)
            self.assertIn(row['reader_method_id'], method_ids)
            self.assertTrue(set(row['writer_method_ids']) <= method_ids)

    def test_tutorial_lazy_cache_not_default_overwrite(self):
        self.assertEqual(tutorial_read(-1, 0, 0), (0, None))
        self.assertEqual(tutorial_read(-1, 1, 1), (1, None))
        self.assertEqual(tutorial_read(-1, 0, 2), (6, 6))
        self.assertEqual(tutorial_read(1, 0, 2), (1, None))
        self.assertEqual(tutorial_read(0, 5, 2), (6, 6))

    def test_stage_getter_one_increment_each_read(self):
        value, write = stage_target_read(-1, 0, 2, max_stage=199)
        self.assertEqual((value, write), (1, 1))
        self.assertEqual(stage_target_read(value, 0, 2, max_stage=199), (2, 2))
        self.assertEqual(stage_target_read(20, 0, 2, max_stage=199), (20, None))
        self.assertEqual(stage_target_read(-1, 0, 0, max_stage=199), (0, None))

    def test_stage_read_zone_guard_and_setter_cap(self):
        # Explicit max_stage=199 is a model input, not claimed APK constant.
        self.assertEqual(stage_target_read(0, 0, 24, max_stage=199), (0, None))
        self.assertEqual(stage_target_read(199, 199, 23, max_stage=199), (199, 199))
        self.assertEqual(stage_target_read(50, 0, 1, max_stage=199), (50, None))

    def test_key_parameters_order_and_domain(self):
        self.assertEqual(persistence_key('stars', stage=1, mode=0), 'StarStageMaster1_0')
        self.assertEqual(persistence_key('stars', stage=0, mode=1), 'StarStageMaster0_1')
        self.assertEqual(persistence_key('drone_used', slot=0), 'DroneUsed0')
        self.assertEqual(persistence_key('drone_unlocked', drone=20001), 'DroneUnlocked20001')
        self.assertNotEqual(persistence_key('drone_used', slot=0), persistence_key('drone_unlocked', drone=20001))

    def test_drone_getters_can_write_but_do_not_autoequip(self):
        self.assertEqual(drone_used_read(), (0, None))
        self.assertEqual(drone_used_read(-5), (0, 0))
        self.assertEqual(drone_used_read(20001), (20001, None))
        self.assertEqual(drone_unlocked_read(20001), (True, 1))
        self.assertEqual(drone_unlocked_read(20002), (False, None))
        self.assertEqual(drone_unlocked_read(20002, 1), (True, None))
        self.assertEqual(drone_unlocked_read(20002, 2), (False, None))
        self.assertEqual(drone_unlocked_read(0), (True, None))  # not a roster validation

    def test_two_stores_and_callback_guard_are_explicit(self):
        self.assertEqual({s['id'] for s in self.data['stores']}, {'Unity.PlayerPrefs', 'PlayerPreferences.dictionary'})
        self.assertTrue(self.data['checks']['typed_wrappers_six_unity_tailcalls'])
        self.assertTrue(self.data['checks']['custom_raw_serializes_dictionary_field'])
        self.assertTrue(self.data['checks']['no_unity_save_call_in_selected_wrapper_lifecycle'])
        self.assertTrue(self.data['checks']['touch_callback_increment_has_two_guards'])
        self.assertTrue(self.data['checks']['delete_key_only_unity_tailcall'])


if __name__ == '__main__':
    unittest.main()
