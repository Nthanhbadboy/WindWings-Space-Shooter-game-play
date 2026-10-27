import gzip
import hashlib
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path('tools/verify').resolve()))
from player_loadout_persistence import (build, ship_used_read, ship_rank_read,
    ship_level_read, ship_unlocked_normal, rocket_count)


class PlayerLoadoutPersistenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build()

    def test_raw_reproduces_and_all_source_pins_match(self):
        raw = json.load(gzip.open('reverse-engineering/raw/player-loadout/contracts.json.gz', 'rt'))
        self.assertEqual(raw, self.data)
        self.assertEqual(len(raw['methods']), 33)
        self.assertEqual(len(raw['checks']), 43)
        self.assertTrue(all(raw['checks'].values()))
        self.assertTrue(all(not r['inventory']['size_capped'] for r in raw['methods']))
        for pin in raw['sources']:
            path = Path(pin['path'])
            content = path.read_bytes()
            if path.suffix == '.gz':
                content = gzip.decompress(content)
            self.assertEqual(hashlib.sha256(content).hexdigest(), pin['sha256_decompressed'])

    def test_derived_keys_types_and_every_evidence_reference(self):
        derived = json.loads(Path('datas/player_loadout_persistence.json').read_text())
        evidence = gzip.decompress(Path(derived['raw_evidence']).read_bytes())
        self.assertEqual(hashlib.sha256(evidence).hexdigest(), derived['raw_evidence_sha256_decompressed'])
        self.assertEqual(derived['contracts'], self.data['contracts'])
        self.assertEqual(len(derived['contracts']), 15)
        ids = {f"{r['class_name']}.{r['method']}" for r in self.data['methods']}
        for row in derived['contracts']:
            self.assertEqual(row['value_type'], 'int32')
            self.assertIn(row['reader_method_id'], ids)
            self.assertTrue(set(row['writer_method_ids']) <= ids)
        self.assertTrue(all(c['method_id'] in ids for c in derived['consumers']))
        self.assertIn(derived['rank_tables']['evidence_method_id'], ids)
        contracts = {r['key_format']:r for r in derived['contracts']}
        self.assertEqual(contracts['PlayerUnlocked{ship}']['reader_return_type'], 'bool')
        self.assertEqual(contracts['PLAYER_DEVICE_{ship}_{slot}']['reader_return_type'], 'int[]')
        self.assertEqual(contracts['FIRST_INSTALL_DEVICE']['reader_return_type'], 'void')

    def test_rank_arrays_bound_to_static_offsets_with_padding_kept(self):
        tables = self.data['rank_tables']
        self.assertEqual(tables['MaxLevelPerRanks'], [10,20,30,60,120,250,500])
        self.assertEqual(tables['CardUpgrades'], [0,20,50,80,250,500,800])
        self.assertEqual(tables['StartRanks'], [2]*24)
        self.assertEqual(tables['MAX_RANK_INDEX'], 6)
        arrays = self.data['array_evidence']['resolved']['methods']['Player_Saved_Datas.cctor']
        for row in arrays:
            self.assertTrue(row['length_valid'])
            raw = bytes.fromhex(row['raw'])
            self.assertEqual([int.from_bytes(raw[i:i+4], 'little', signed=True) for i in range(0,row['len']*4,4)], row['ints'])
            self.assertGreaterEqual(len(raw), row['len']*4)

    def test_missing_equip_values_are_defaults_not_initial_writes(self):
        self.assertEqual(ship_used_read({}, 0), (10001, {}, {}))
        self.assertEqual(ship_used_read({}, 1), (10002, {}, {}))
        self.assertEqual(ship_used_read({}, 9), (10002, {}, {}))
        # Native routine does not reject arbitrary positive IDs or duplicate equip.
        original = {'PlayerUsed0':999, 'PlayerUsed1':999}
        self.assertEqual(ship_used_read(original, 1), (999, original, {}))

    def test_nonpositive_slot_repairs_both_slots_and_can_overwrite_other_ship(self):
        original = {'PlayerUsed0':10009, 'PlayerUsed1':0}
        result, state, writes = ship_used_read(original, 1)
        self.assertEqual(result, 10002)
        self.assertEqual(writes, {'PlayerUsed0':10001,'PlayerUsed1':10002})
        self.assertEqual(state, writes)
        self.assertEqual(original, {'PlayerUsed0':10009,'PlayerUsed1':0})
        # For invalid slots the same two keys are repaired, not the requested key.
        self.assertEqual(ship_used_read({'PlayerUsed9':-3}, 9)[0], -3)

    def test_rank_repair_precedes_trial_override_and_does_not_clamp_trial(self):
        self.assertEqual(ship_rank_read({}, 10001), (2, {}, {}))
        store = {'PLAYER_RANK10001':1,'TRIAL_ID_10001':1}
        rank, state, writes = ship_rank_read(store,10001)
        self.assertEqual(rank,0)
        self.assertEqual(state['PLAYER_RANK10001'],2)
        self.assertEqual(writes, {'PLAYER_RANK10001':2})
        self.assertEqual(store['PLAYER_RANK10001'],1)
        self.assertEqual(ship_rank_read({'PLAYER_RANK10001':99},10001)[0],99)
        self.assertEqual(ship_rank_read({'TRIAL_ID_10001':1,'TRIAL_RANK_10001':-2},10001)[0],-2)

    def test_level_and_rank_trial_flag_is_exact_one(self):
        for flag in (0,2,-1):
            store = {'TRIAL_ID_10001':flag,'PLAYER_LEVEL10001':8,'TRIAL_LEVEL_10001':25,
                     'PLAYER_RANK10001':4,'TRIAL_RANK_10001':6}
            self.assertEqual(ship_level_read(store,10001),8)
            self.assertEqual(ship_rank_read(store,10001)[0],4)
        self.assertEqual(ship_level_read({'TRIAL_ID_10001':1,'TRIAL_LEVEL_10001':25},10001),25)
        self.assertEqual(ship_level_read({'PLAYER_LEVEL10001':-4},10001),-4)

    def test_normal_unlock_threshold_not_roster_validation(self):
        self.assertTrue(ship_unlocked_normal(10001,0))
        self.assertTrue(ship_unlocked_normal(10002,0))
        self.assertTrue(ship_unlocked_normal(-1,0))
        self.assertFalse(ship_unlocked_normal(10003,0))
        self.assertTrue(ship_unlocked_normal(10003,1))
        self.assertFalse(ship_unlocked_normal(10003,2))

    def test_rocket_count_preserves_non_monotonic_native_ranges(self):
        for level, expected in [(-1,7),(0,7),(1,8),(5,8),(6,3),(8,3),(9,10),(20,10)]:
            self.assertEqual(rocket_count(level),expected)

    def test_device_talent_defaults_and_no_save_version_claim(self):
        contracts = {r['key_format']:r for r in self.data['contracts']}
        for key in ('PLAYER_DEFAULT_SKIN{ship}','PLAYER_DEVICE_{ship}_{slot}','TALENT_SELECTED'):
            self.assertEqual(contracts[key]['normal_missing_default'],-1)
        for key in ('PlayerStatPoints{stat}','PlayerStatLevel{stat}','TECHLAB_LV','PLAYER_CARDS{ship}'):
            self.assertEqual(contracts[key]['normal_missing_default'],0)
        self.assertIn('pack format version', self.data['limitations'][0])
        self.assertEqual(self.data['array_evidence']['resolved']['methods']['Player_Device_Saved_Datas.GetPlayerDevices'][0]['ints'], [-1]*4)


if __name__ == '__main__':
    unittest.main()
