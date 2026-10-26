import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('early_wave_prefabs', 'tools/verify/early_wave_prefabs.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class EarlyWavePrefabTests(unittest.TestCase):
    def test_rebuild_and_checks(self):
        fresh=module.build()
        stored=json.load(gzip.open('reverse-engineering/raw/early-waves/resolved-default-waves.json.gz','rt'))
        self.assertEqual(fresh,stored)
        self.assertTrue(all(fresh['checks'].values()))
        for w in fresh['waves']:
            self.assertEqual(hashlib.sha256(Path(w['source']).read_bytes()).hexdigest(),w['source_sha256'])

    def test_exact_keys_not_same_name_chapter_or_branch(self):
        index=json.loads(Path('reverse-engineering/raw/early-waves/index.json').read_text())
        self.assertEqual(len(index['entries']),14)
        for w in module.build()['waves']:
            self.assertTrue(w['resource_key'].startswith('datas/maps/waves/'))
            self.assertTrue(any(e['container_key']=='datas/maps/chapter2/waves/'+w['resource_key'].rsplit('/',1)[1] and e['root']!=w['root'] for e in index['entries']))

    def test_markers_do_not_add_enemy_slots(self):
        for w in module.build()['waves']:
            markers=[r for r in w['rows'] if r['marker']]
            self.assertEqual(sorted(r['spawn_type'] for r in markers),[5,6])
            self.assertTrue(all(r['configured_slots']==0 for r in markers))
            self.assertEqual(sum(w['prefab_histogram'].values()),w['configured_spawn_slots'])
