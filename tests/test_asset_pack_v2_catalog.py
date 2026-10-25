import gzip
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path('tools/recovery').resolve()))
from asset_pack_v2 import browser_html, identity_path


class AssetPackV2CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(gzip.decompress(Path('reverse-engineering/raw/asset-pack-v2/catalog.json.gz').read_bytes()))

    def test_source_population_and_visible_exception(self):
        data = self.data
        self.assertEqual(data['source_counts'], dict(Texture2D=654,Sprite=2185,TextAsset=64,AudioClip=69,Font=1,SpriteAtlas=66))
        self.assertEqual(len(data['objects']), 3039)
        self.assertEqual(data['outcomes'], dict(exported=3038,failed=1))
        self.assertEqual(data['output_files'],3038)
        self.assertFalse(data['gates']['all_target_objects_exported'])
        failed = [r for r in data['objects'] if r['status']=='failed']
        self.assertEqual([(r['serialized_file'],r['path_id'],r['name'],r['source_dimensions']) for r in failed],
                         [('data.unity3d/resources.assets',535,'Font Texture',[0,0])])
        self.assertEqual(failed[0]['outputs'],[])

    def test_identities_paths_and_browser_reproduce(self):
        rows = self.data['objects']
        self.assertEqual(len({(r['serialized_file'],r['type'],r['path_id']) for r in rows}),len(rows))
        paths = [o['path'] for r in rows for o in r['outputs']]
        self.assertEqual(len(set(paths)),len(paths))
        for r in rows:
            for o in r['outputs']:
                self.assertTrue(o['path'].startswith(identity_path(r['serialized_file'],r['type'],r['path_id'])))
                self.assertEqual(len(o['sha256']),64)
        self.assertEqual(Path('docs/assets/pack-browser-v2.html').read_text(),browser_html(self.data))

    def test_independent_archive_audit_and_ambiguous_spine_pages(self):
        audit = json.loads(gzip.decompress(Path('reverse-engineering/raw/asset-pack-v2/archive-audit.json.gz').read_bytes()))
        self.assertEqual(audit['media_files_verified'],3038)
        self.assertEqual(audit['png_full_decodes'],2838)
        self.assertEqual(len(audit['audio']),69)
        self.assertAlmostEqual(audit['audio_duration_seconds'],571.4650289115647)
        self.assertTrue(all(audit['gates'].values()))
        self.assertEqual(audit['text_classification'],dict(atlas_text=27,spine_skeleton_json=27,other_text=10))
        self.assertEqual(len(audit['spine_atlas_page_candidates']),27)
        self.assertTrue(all(p['join_status']=='name_candidates_only_not_identity_proof' and len(p['texture_candidates'])>1
                            for p in audit['spine_atlas_page_candidates']))
        uploaded=json.loads(Path('reverse-engineering/raw/asset-pack-v2/release-upload.json').read_text())
        self.assertTrue(uploaded['draft'])
        asset=next(r for r in uploaded['assets'] if r['name']=='assets-v2.zip')
        self.assertEqual(asset['digest'],'sha256:'+audit['archive_sha256'])
        self.assertEqual(asset['size'],audit['archive_bytes'])

    def test_zero_texture_raw_has_no_image_payload(self):
        evidence=json.loads(Path('reverse-engineering/raw/asset-pack-v2/font-texture-exception.json').read_text())
        tree=evidence['typetree']
        self.assertEqual(evidence['path_id'],535)
        self.assertEqual([tree['m_Width'],tree['m_Height'],tree['m_CompleteImageSize']],[0,0,0])
        self.assertEqual(tree['image data'],[])
        self.assertEqual(tree['m_StreamData'],dict(offset=0,size=0,path=''))

    def test_null_sprite_texture_does_not_mean_missing_image(self):
        rows = [r for r in self.data['objects'] if r['type']=='Sprite']
        indirect = [r for r in rows if r['texture_pointer']['resolution']=='null']
        self.assertEqual(len(indirect),1550)
        self.assertTrue(all(r['sprite_atlas_pointer']['resolution']=='resolved' for r in indirect))
        self.assertTrue(all(r['status']=='exported' for r in indirect))


if __name__ == '__main__':
    unittest.main()
