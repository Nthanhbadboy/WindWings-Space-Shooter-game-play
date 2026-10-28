"""Keep handed-off item receipts immutable while later items sync live needles.
provenance: arena/8141386a-windwings-space-shooter-game-p
Historical pins are checked against actual own scientific Git bytes, not waived/rebased.
"""
from __future__ import annotations
import argparse
import gzip
import json
import re
import subprocess
from tools.verify.geometry_8141386a_sources import ROOT,RAW,BRANCH,sha

HEAD5='c86db3ee52b9dcf9108600e64717637a5ca59dd4'
MUTABLE_LIVE={'tools/verify-claims.py','docs/spec/START_HERE.md','docs/spec/README.md',
              'reverse-engineering/raw/geometry-8141386a/verification-support-imports.json',
              '.github/workflows/verify-geometry-8141386a.yml'}


def blob(head,path):
    return subprocess.check_output(['git','-C',str(ROOT),'show',head+':'+path])


def check(fetch=False):
    for record in sorted(RAW.glob('scientific-ci-*.json.gz')):
        ci=json.loads(gzip.decompress(record.read_bytes()));item=ci['item'];head=ci['scientific_commit']
        if ci['provenance']!=BRANCH or not re.fullmatch('[0-9a-f]{40}',head):raise ValueError('invalid historical provenance')
        if item==5 and head!=HEAD5:raise ValueError('fixed #5 source changed')
        runs=[v for v in ci.values() if isinstance(v,dict) and 'head_sha' in v and 'conclusion' in v]
        if len(runs)<2 or any(r['head_sha']!=head or r['status']!='completed' or r['conclusion']!='success' for r in runs):
            raise ValueError('historical CI not exact-source completed GREEN')
        if fetch:subprocess.run(['git','-C',str(ROOT),'fetch','--depth=1','origin',head],check=True)
        path=f'reverse-engineering/raw/geometry-8141386a/verification-{item}.json.gz'
        old=blob(head,path)
        if (ROOT/path).read_bytes()!=old:raise ValueError(f'handed-off #{item} receipt was changed')
        value=json.loads(gzip.decompress(old))
        for p,digest in value['worktree_pins'].items():
            if sha(blob(head,p))!=digest:raise ValueError('historical scientific commit disagrees with receipt: '+p)
            if p not in MUTABLE_LIVE and sha((ROOT/p).read_bytes())!=digest:
                raise ValueError(f'immutable #{item} scientific path changed: '+p)
        for row in value['log_receipts'].values():
            if (ROOT/row['path']).read_bytes()!=blob(head,row['path']):raise ValueError('historical log changed')
        snap=value['support_snapshot']
        if sha((ROOT/snap['bundle_path']).read_bytes())!=snap['bundle_sha256']:raise ValueError('historical support snapshot changed')
        print(f'PASS immutable #{item} historical scientific evidence against actual Git bytes at {head}')
    print('CURRENT live needles are checked separately; no historical acceptance is rebased onto live docs.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fetch',action='store_true');a=p.parse_args();check(a.fetch)
