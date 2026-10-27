import gzip
import json
from pathlib import Path
import unittest

class SpineReferencePackTests(unittest.TestCase):
    def test_every_source_copy_has_typed_provenance_and_exact_hash(self):
        folder=Path('reverse-engineering/raw/spine-identity')
        manifest=json.loads(gzip.decompress((folder/'reference-pack-manifest.json.gz').read_bytes()))
        contract=json.loads(Path('datas/spine_identity.json').read_text())
        rigs={r['identity']['path_id']:r for r in contract['rigs']}
        self.assertEqual(len(manifest['rigs']),27)
        self.assertEqual(len({r['folder'] for r in manifest['rigs']}),27)
        self.assertEqual(sum(len(r['files']) for r in manifest['rigs']),81)
        for rig in manifest['rigs']:
            source=rigs[rig['identity']['path_id']]
            atlas=source['atlases'][0]
            expected={'skeleton.json':source['skeleton'],'skeleton.atlas':atlas['atlas_text'],atlas['pages'][0]['page']:atlas['pages'][0]['texture']}
            self.assertEqual({r['file'] for r in rig['files']},set(expected))
            for copied in rig['files']:
                self.assertEqual(copied['source'],expected[copied['file']])
                self.assertEqual(copied['sha256'],copied['source']['sha256'])
                self.assertEqual(copied['bytes'],copied['source']['bytes'])

    def test_release_stays_draft_and_digest_matches_audited_zip(self):
        folder=Path('reverse-engineering/raw/spine-identity')
        audit=json.loads((folder/'reference-pack-audit.json').read_text())
        release=json.loads((folder/'reference-pack-release.json').read_text())
        self.assertTrue(release['draft'])
        self.assertEqual(audit['rigs'],27)
        self.assertEqual(audit['members'],110)
        self.assertTrue(all(audit['gates'].values()))
        self.assertEqual(release['asset']['size'],audit['bytes'])
        self.assertEqual(release['asset']['digest'],'sha256:'+audit['archive_sha256'])

if __name__=='__main__':unittest.main()
