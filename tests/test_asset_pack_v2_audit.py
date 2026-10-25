import gzip
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch
import zipfile
sys.path.insert(0, str(Path('tools/recovery').resolve()))
from asset_pack_v2_audit import audit_archive


class AssetPackV2AuditTests(unittest.TestCase):
    def fixture(self, folder, mutation=None):
        path='TextAsset/identity.txt'
        blob=b'reference'
        output=dict(path=path,bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest())
        catalog=dict(output_files=1,objects=[dict(type='TextAsset',name='reference',outputs=[output])])
        archive=Path(folder)/'assets-v2.zip'
        with zipfile.ZipFile(archive,'w') as z:
            z.writestr('manifest-v2.json',json.dumps(catalog))
            z.writestr('index.html','offline')
            z.writestr(path,b'corrupted' if mutation=='hash' else blob)
            if mutation=='extra':
                z.writestr('untracked.txt','not-in-manifest')
            if mutation=='unsafe':
                z.writestr('../escape.txt','unsafe')
        return archive,catalog

    def audit(self, archive, catalog):
        modules={'PIL':NS(Image=NS()),'fontTools':NS(),'fontTools.ttLib':NS(TTFont=NS())}
        with patch.dict(sys.modules,modules):
            return audit_archive(archive,catalog)

    def test_members_match_exactly(self):
        with tempfile.TemporaryDirectory() as folder:
            archive,catalog=self.fixture(folder)
            result=self.audit(archive,catalog)
            self.assertEqual(result['media_files_verified'],1)
            self.assertTrue(result['gates']['exact_media_population'])
            self.assertEqual(result['text_classification'],{'other_text':1})

    def test_corruption_untracked_and_unsafe_paths_rejected(self):
        for mutation in ('hash','extra','unsafe'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as folder:
                archive,catalog=self.fixture(folder,mutation)
                with self.assertRaises(ValueError):
                    self.audit(archive,catalog)


if __name__ == '__main__':
    unittest.main()
