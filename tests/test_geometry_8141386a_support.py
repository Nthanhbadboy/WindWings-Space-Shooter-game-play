"""Verify the support-scope boundary, not simply a desired PASS count.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.verify import geometry_8141386a_claims as support

ROOT=support.ROOT
RECEIPT=ROOT/'reverse-engineering/raw/geometry-8141386a/verification-support-imports.json'


class GeometrySupport8141386a(unittest.TestCase):
    def test_only_named_pinned_historical_support_inputs(self):
        files=support.unpack_support()
        self.assertEqual(len(files),99)
        self.assertTrue(all(support.in_group(p) for p in files))
        self.assertTrue(all(not Path(p).is_absolute() and '..' not in Path(p).parts for p in files))
        self.assertTrue(all(len(b)<5000000 for b in files.values()))
        self.assertFalse(any(p.endswith('.apk') or p.endswith('.xapk') for p in files))

    def test_original_expectations_are_unchanged_except_two_live_count_blocks(self):
        original=support.unpack_support()['tools/verify-claims.py'].decode()
        current=(ROOT/'tools/verify-claims.py').read_text()
        for start,end in [('claim("APKD1",','\nclaim("IA8",'),('claim("AI1",','\nclaim("AP1",')]:
            a=current.index(start);b=current.index(end,a)
            oa=original.index(start);ob=original.index(end,oa)
            current=current[:a]+original[oa:ob]+current[b:]
        marker='if __name__ == "__main__":'
        current=current[:current.rindex(marker)]+original[original.rindex(marker):]
        self.assertEqual(current,original,'No repairing unrelated failed assertions or fabricated 209PASS')

    def test_imports_retain_exact_pins_except_declared_needles_adapter(self):
        record=json.loads(RECEIPT.read_bytes())
        adjusted=record['post_import_adjustments']
        self.assertEqual(set(adjusted),{'docs/spec/START_HERE.md','tools/verify-claims.py'})
        self.assertEqual(len(record['imports']),50)
        for item in record['imports']:
            expected=adjusted.get(item['path'],{}).get('current_sha256',item['sha256'])
            self.assertEqual(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest(),expected,item['path'])

    def test_legacy_peer_docs_are_not_overwritten(self):
        record=json.loads(RECEIPT.read_bytes())
        for item in record['existing_preserved']:
            body=(ROOT/item['path']).read_bytes()
            if item['path']=='docs/spec/README.md':
                body=body.split(b'\n## Branch-owned verification-support index (8141386a)\n')[0].rstrip()
                expected=item['baseline_sha256_rstrip']
            else:expected=item['baseline_sha256']
            self.assertEqual(hashlib.sha256(body).hexdigest(),expected,item['path'])

    def test_three_protected_paths_remain_exact_initial_spec_bytes(self):
        pins={'datas/PROVENANCE.md':'75bc6a03003469f2d528d249f50fa529ee8b7aac0cca01eb5486458795c148ed',
              'datas/boss_anim_events.csv':'4ee93a35ed32ec70851ae07a98dda2d1398868c8311ac1a10cac857e97082a5c',
              'datas/player_start_stats.json':'d336295ae74f7a2a77d043c3119ee5be493a6d04dbd5c57492f1d2bb20b9b566'}
        self.assertEqual(json.loads(RECEIPT.read_bytes())['protected_paths_sha256'],pins)
        for p,h in pins.items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h,p)

    def test_copy_on_write_overlay_does_not_touch_original_target(self):
        with tempfile.TemporaryDirectory() as t:
            original=Path(t)/'original';view=Path(t)/'view'
            (original/'docs/inner').mkdir(parents=True);view.mkdir()
            (original/'docs/inner/a.txt').write_text('original')
            (view/'docs').symlink_to(original/'docs',target_is_directory=True)
            path=support.writable_parent(view,'docs/inner/a.txt')
            path.unlink();path.write_text('fixture')
            self.assertEqual((view/'docs/inner/a.txt').read_text(),'fixture')
            self.assertEqual((original/'docs/inner/a.txt').read_text(),'original')

    def test_corrupt_support_input_fails_not_fabricated_success(self):
        value=json.loads(gzip.decompress(support.BUNDLE.read_bytes()))
        item=next(i for i in value['files'] if 'base64' in i)
        item['base64']='Y29ycnVwdA=='
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'bad.json.gz';p.write_bytes(gzip.compress(json.dumps(value).encode(),mtime=0))
            with patch.object(support,'BUNDLE',p),self.assertRaisesRegex(ValueError,'witness mismatch'):
                support.unpack_support()

    def test_only_gzip_mtime_diff_is_reconstructed_inside_support(self):
        files=support.unpack_support();p='reverse-engineering/il2cpp/dump.cs.gz'
        original=files[p];current=(ROOT/p).read_bytes()
        self.assertNotEqual(original[:10],current[:10])
        self.assertEqual(original[10:],current[10:])
        self.assertEqual(gzip.decompress(original),gzip.decompress(current))

    def test_three_live_needles_pass_with_scope_banner(self):
        result=subprocess.run([sys.executable,str(ROOT/'tools/verify-claims.py'),'--require','APKD1,AI1,RD1'],
                              cwd=ROOT,text=True,capture_output=True,timeout=120)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('CURRENT OWN WORKTREE: APKD1 / AI1 / RD1 only',result.stdout)
        self.assertIn('PASS 209 · FAIL 0 · SKIP 2 · ERROR 0',result.stdout)
        for name in ('APKD1','AI1','RD1'):
            self.assertRegex(result.stdout,rf'{name}\s+PASS')


if __name__=='__main__':unittest.main()
