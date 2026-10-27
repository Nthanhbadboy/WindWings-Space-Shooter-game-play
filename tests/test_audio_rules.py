import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path('tools/verify').resolve()))
from audio_rules import build,effective_volume,source_busy


class AudioRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=build()

    def test_snapshot_all_source_pins_and_uncapped_bodies(self):
        self.assertEqual(self.data,json.load(gzip.open('reverse-engineering/raw/audio-rules/contracts.json.gz','rt')))
        self.assertEqual(len(self.data['methods']),65)
        self.assertEqual(len(self.data['checks']),25)
        self.assertTrue(all(self.data['checks'].values()))
        for row in self.data['methods']:self.assertFalse(row['inventory']['size_capped'])
        for pin in self.data['sources']:
            path=Path(pin['path']);data=path.read_bytes()
            if path.suffix=='.gz':data=gzip.decompress(data)
            self.assertEqual(hashlib.sha256(data).hexdigest(),pin['sha256_decompressed'])

    def test_derived_references_and_overloads_use_distinct_RVAs(self):
        derived=json.loads(Path('datas/audio_rules.json').read_text())
        self.assertEqual(derived['rules'],self.data['rules'])
        self.assertEqual(hashlib.sha256(gzip.decompress(Path(derived['raw_evidence']).read_bytes())).hexdigest(),derived['raw_evidence_sha256_decompressed'])
        ids={r['id'] for r in self.data['methods']}
        self.assertEqual(len(ids),65)
        for r in derived['rules']:
            self.assertTrue(set(r['evidence_method_ids'])<=ids)
            for key in ['writer_method_id','coroutine_method_id']:
                if key in r:self.assertIn(r[key],ids)
        overloads=[r for r in self.data['methods'] if r['class_name']=='AudioManager' and r['method']=='GetAudioSource']
        self.assertEqual({r['inventory']['rva'] for r in overloads},{'0x15b5a68','0x15b5f38'})
        self.assertEqual(len({r['inventory']['signature'] for r in overloads}),2)

    def test_registry_enum_and_alias_counts_not_global_clip_identity(self):
        self.assertEqual(len(self.data['clip_enum']),118)
        rows=self.data['registry'];self.assertEqual(len(rows),92)
        self.assertTrue(all(r['enum_value'] is not None for r in rows))
        self.assertEqual(len({(r['clip_pptr']['m_FileID'],r['clip_pptr']['m_PathID']) for r in rows}),69)
        byname={r['sound_id']:r for r in rows}
        self.assertEqual(byname['Bgm_Boss1']['clip_pptr'],byname['Bgm_Boss2']['clip_pptr'])
        self.assertIn('no serialized-file identity',self.data['limitations'][1])

    def test_mute_exact_one_and_volume_getter_not_clamping(self):
        self.assertEqual(effective_volume(1,0.8),0)
        self.assertEqual(effective_volume(0,None,0.73),0.73)
        self.assertEqual(effective_volume(2,0.8),0.8)
        self.assertEqual(effective_volume(-1,-0.5),-0.5)

    def test_reclaim_waits_for_positive_time_or_playing(self):
        self.assertTrue(source_busy(0.2,False))
        self.assertTrue(source_busy(0,True))
        self.assertFalse(source_busy(0,False))

    def test_playlist_and_endgame_not_inferred_from_clip_names(self):
        rules={r['id']:r for r in self.data['rules']}
        self.assertEqual(rules['game_playlist']['clip_enum_values'],[33,34,35,36])
        self.assertIn('Bgm_Game5',{r['sound_id'] for r in self.data['registry']})
        self.assertEqual(rules['endgame_move']['enum_value'],self.data['clip_enum']['Sfx_Flying'])
        self.assertNotEqual(rules['endgame_move']['enum_value'],self.data['clip_enum']['Sfx_Victory'])


class AudioRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=importlib.util.spec_from_file_location('audio_native',Path('tools/recovery/audio_native.py'))
        cls.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.module)

    def test_mask_keeps_boundaries_and_no_player_output(self):
        rows=[('AudioManager','','A',1,2,'void A()'),('GP_Tutorials.X','','B',4,5,'void B()')]
        masked=self.module.mask_unselected(rows)
        self.assertEqual([r[1:] for r in rows],[r[1:] for r in masked])
        self.assertEqual(masked[0],rows[0]);self.assertEqual(masked[1][0],'__not_selected__')
        text=Path('tools/recovery/audio_native.py').read_text()
        self.assertIn('reverse-engineering/raw/audio-rules',text)
        self.assertNotIn('reverse-engineering/raw/player-loadout',text)

    def test_all_audio_coroutines_explicitly_selected(self):
        self.assertEqual(len(self.module.CLASSES),10)
        for name in ['AudioManager.<DelayFreeSource>d__27','AudioManager.<SmoothMusic>d__32','GP_SoundTracks.<Start>d__0']:
            self.assertIn(name,self.module.CLASSES)


if __name__=='__main__':unittest.main()
