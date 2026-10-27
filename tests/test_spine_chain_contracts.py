import copy
import gzip
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path('tools/verify').resolve()))
from spine_chain_contracts import build,derive,select_local_page

class SpineChainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chains=json.loads(gzip.decompress(Path('reverse-engineering/raw/spine-identity/chains.json.gz').read_bytes()))
        cls.catalog=json.loads(gzip.decompress(Path('reverse-engineering/raw/asset-pack-v2/catalog.json.gz').read_bytes()))

    def test_local_search_never_global_basename(self):
        page=select_local_page('skeleton.png',[dict(texture_name='skeleton',texture='correct')])
        self.assertEqual(page['texture'],'correct')
        for rows in ([],[dict(texture_name='Skeleton')],[dict(texture_name='skeleton'),dict(texture_name='skeleton')]):
            with self.assertRaises(ValueError):select_local_page('skeleton.png',rows)
        with self.assertRaises(ValueError):select_local_page('../skeleton.png',[])

    def test_27_rigs_and_seven_dimension_mismatches_preserved(self):
        d=derive(self.chains,self.catalog)
        self.assertEqual(d['summary']['rigs'],27)
        self.assertEqual(d['summary']['pages'],27)
        self.assertEqual(d['summary']['observed_skeleton_versions'],{'3.8.84':1,'3.8.99':26})
        pages=[p for r in d['rigs'] for a in r['atlases'] for p in a['pages']]
        mismatches=[p for p in pages if not p['dimension_match']]
        self.assertEqual(len(mismatches),7)
        self.assertTrue(all(p['atlas_dimensions']==[1024,1024] and [p['width'],p['height']]==[512,512] for p in mismatches))

    def test_blend_replacement_targets_not_dropped(self):
        d=derive(self.chains,self.catalog)
        rigs=[r for r in d['rigs'] if r['blend_replacements']]
        self.assertEqual([r['identity']['path_id'] for r in rigs],[580647])
        self.assertEqual([b['material']['path_id'] for b in rigs[0]['blend_replacements']],[38,39])
        self.assertTrue(all(b['texture_targets'][0]['path_id']==413 for b in rigs[0]['blend_replacements']))

    def test_zero_fileid_cannot_be_joined_across_serialized_files(self):
        bad=copy.deepcopy(self.chains)
        link=next(l for l in bad['links'] if l['location']=='.skeletonJSON')
        self.assertEqual(link['pointer']['m_FileID'],0)
        link['target']['serialized_file']='different-file'
        with self.assertRaises(AssertionError):derive(bad,self.catalog)

    def test_no_invented_material_property_selection(self):
        bad=copy.deepcopy(self.chains)
        material=next(r for r in bad['objects'] if r['type']=='Material')
        material['tree']['m_SavedProperties']['m_TexEnvs'][0][0]='_NotMainTex'
        with self.assertRaises(AssertionError):derive(bad,self.catalog)

    def test_preserved_contract_and_native_policy_reproduce(self):
        data=build()
        self.assertEqual(json.loads(Path('datas/spine_identity.json').read_text()),data)
        self.assertTrue(all(data['native_policy']['checks'].values()))
        self.assertFalse(data['scan_scope']['all_MB_headers_classified'])
        self.assertEqual([e['path_id'] for e in data['scan_scope']['unclassified_MB']],[580792])
        for r in self.chains['objects']:
            if r['type']=='MonoBehaviour':
                self.assertIn('parsed_header',r)
                self.assertNotEqual(r['tree']['m_Script'],r['parsed_header']['m_Script'])

if __name__=='__main__':unittest.main()
