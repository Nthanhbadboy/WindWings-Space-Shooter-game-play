import csv
import gzip
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path('tools/recovery').resolve()))
from asset_pack_audit import annotate_manifest_collisions,browser_html


class AssetPackCatalogTests(unittest.TestCase):
    def test_preserved_catalog_findings_reproduce_without_original_media(self):
        data=json.load(gzip.open('reverse-engineering/raw/asset-pack/catalog.json.gz','rt'))
        self.assertEqual(annotate_manifest_collisions(json.loads(json.dumps(data))),data)
        self.assertEqual(len(data['files']),2652)
        self.assertEqual(data['collision_summary']['paths'],151)
        self.assertEqual(data['collision_summary']['extra_manifest_rows'],321)
        self.assertEqual(len(data['manifest_size_mismatches']),320)
        self.assertTrue(data['validation_gates']['archive_crc_valid'])
        self.assertFalse(data['validation_gates']['manifest_path_mapping_injective'])
        self.assertFalse(data['validation_gates']['manifest_size_matches'])
        self.assertEqual(data['validation_gates']['complete_APK_reference'],'NOT_ESTABLISHED')
        self.assertEqual(data['counts_by_category']['AudioClip'],69)
        self.assertEqual(data['counts_by_category']['Font'],1)
        self.assertEqual(len(list(csv.DictReader(Path('reverse-engineering/raw/asset-pack/manifest-full.csv').read_text().splitlines()))),2907)

    def test_browser_matches_catalog_and_labels_ambiguous_identity(self):
        data=json.load(gzip.open('reverse-engineering/raw/asset-pack/catalog.json.gz','rt'))
        self.assertEqual(Path('docs/assets/pack-browser.html').read_text(),browser_html(data))
        self.assertIn('NOT a complete pack',browser_html(data))
        collision=next(r for r in data['files'] if r['path']=='Texture2D/skeleton.png')
        self.assertGreater(len(collision['identities']),1)
        self.assertEqual(collision['identity_status'],'ambiguous_manifest_path_collision')


if __name__=='__main__':unittest.main()
