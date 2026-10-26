"""Keep a handed-off #5 receipt immutable while later items sync live needles.
provenance: arena/8141386a-windwings-space-shooter-game-p
Historical pins are checked against actual own Git commit bytes, not waived/rebased.
"""
from __future__ import annotations
import gzip
import json
import subprocess
from tools.verify.geometry_8141386a_sources import ROOT,RAW,sha

HEAD5='c86db3ee52b9dcf9108600e64717637a5ca59dd4'
MUTABLE_LIVE={'tools/verify-claims.py','docs/spec/START_HERE.md','docs/spec/README.md',
              'reverse-engineering/raw/geometry-8141386a/verification-support-imports.json',
              '.github/workflows/verify-geometry-8141386a.yml'}


def blob(path):
    return subprocess.check_output(['git','-C',str(ROOT),'show',HEAD5+':'+path])


def check():
    path='reverse-engineering/raw/geometry-8141386a/verification-5.json.gz'
    old=blob(path)
    if (ROOT/path).read_bytes()!=old:raise ValueError('handed-off #5 receipt was changed')
    value=json.loads(gzip.decompress(old))
    for p,digest in value['worktree_pins'].items():
        if sha(blob(p))!=digest:raise ValueError('historical scientific commit disagrees with receipt: '+p)
        if p not in MUTABLE_LIVE and sha((ROOT/p).read_bytes())!=digest:
            raise ValueError('immutable #5 scientific path changed: '+p)
    for item in value['log_receipts'].values():
        if (ROOT/item['path']).read_bytes()!=blob(item['path']):raise ValueError('historical log changed')
    snap=value['support_snapshot']
    if sha((ROOT/snap['bundle_path']).read_bytes())!=snap['bundle_sha256']:raise ValueError('historical support snapshot changed')
    print('PASS immutable #5 historical evidence against actual Git bytes at '+HEAD5)
    print('Historical report needles remain118/107, AI1 datas76, RD1(41,0); CURRENT needles are checked separately.')


if __name__=='__main__':check()
