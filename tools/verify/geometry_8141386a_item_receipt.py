"""Per-item scientific/support separation and verifiable complete test receipts.
provenance: arena/8141386a-windwings-space-shooter-game-p
Historical support compatibility is never runtime/geometry acceptance.
"""
from __future__ import annotations
import argparse
import gzip
import json
from pathlib import Path
from tools.verify.geometry_8141386a_sources import ROOT,RAW,BRANCH,sha,canonical
from tools.verify.geometry_8141386a_claims import BUNDLE,SPEC
from tools.verify.geometry_8141386a_receipt import claims,tests


def build(item,artifact,report):
    scratch=ROOT/'.arena/geometry-8141386a'
    baseline=json.loads((RAW/'_verify_baseline.json').read_bytes())
    scoped_text=(scratch/f'claims-scoped-{item}.txt').read_text()
    unscoped_text=(scratch/f'claims-unscoped-{item}.txt').read_text()
    focused_text=(scratch/f'focused-{item}.txt').read_text()
    full_text=(scratch/f'full-tests-{item}.txt').read_text()
    scoped,unscoped=claims(scoped_text),claims(unscoped_text)
    old={r['id'] for r in baseline['result']['claims'] if r['status'] in ('FAIL','ERROR')}
    now={r['id'] for r in unscoped['claims'] if r['status'] in ('FAIL','ERROR')}
    if not now<=old or unscoped['counts']['FAIL']>27:raise ValueError('unscoped failure regression')
    if scoped['counts']!={'PASS':209,'FAIL':0,'SKIP':2,'ERROR':0}:raise ValueError('scoped historical compatibility failed')
    logs={}
    for label,text in [('scoped_historical_support',scoped_text),('current_unscoped',unscoped_text),('focused_tests',focused_text),('full_tests',full_text)]:
        path=RAW/f'verification-{item}-{label}.log.gz';path.write_bytes(gzip.compress(text.encode(),mtime=0))
        logs[label]=dict(path=str(path.relative_to(ROOT)),sha256=sha(path.read_bytes()))
    snapshot=json.loads(gzip.decompress(BUNDLE.read_bytes()))
    support=dict(scope=snapshot['scope'],source_commit=SPEC,bundle_path=str(BUNDLE.relative_to(ROOT)),bundle_sha256=sha(BUNDLE.read_bytes()),
                 path_count=len(snapshot['files']),path_set=[{k:v for k,v in row.items() if k!='base64'} for row in snapshot['files']])
    pins=[artifact,report,'tools/verify-claims.py','tools/refresh-readme-sizes.py','tools/raw-audit.py',
          'docs/spec/START_HERE.md','docs/spec/README.md','reverse-engineering/raw/geometry-8141386a/_verify_baseline.json',
          'reverse-engineering/raw/geometry-8141386a/verification-support-imports.json','.github/workflows/verify-geometry-8141386a.yml']
    pins += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'tools/verify').glob('*8141386a*.py'))]
    pins += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'tests').glob('test_geometry_8141386a*.py'))]
    v=dict(schema=1,item=item,provenance=BRANCH,artifact=artifact,report=report,
           support_snapshot=support,original_baseline_sha256=sha((RAW/'_verify_baseline.json').read_bytes()),
           original_baseline_counts=baseline['result']['counts'],scoped_historical_support_result=scoped,current_unscoped_result=unscoped,
           unscoped_regression=dict(new_failure_ids=sorted(now-old),fail_count_not_increased=True),
           focused_tests=tests(focused_text),full_tests=tests(full_text),log_receipts=logs,
           live_needles=json.loads((RAW/'verification-support-imports.json').read_bytes())['current_needles'],
           worktree_pins={p:sha((ROOT/p).read_bytes()) for p in sorted(set(pins))},
           boundary='Source-owned static artifact/regressions separate from scoped historical-support compatibility and from native/runtime/readback/render.')
    path=RAW/f'verification-{item}.json.gz';path.write_bytes(gzip.compress(canonical(v),mtime=0))
    print('Saved complete item',item,'test/log/snapshot receipt',path.stat().st_size,'bytes')


def check(item):
    path=RAW/f'verification-{item}.json.gz';v=json.loads(gzip.decompress(path.read_bytes()))
    if v['item']!=item or v['provenance']!=BRANCH:raise ValueError('wrong item receipt')
    for p,digest in v['worktree_pins'].items():
        if sha((ROOT/p).read_bytes())!=digest:raise ValueError('receipt worktree drift: '+p)
    for row in v['log_receipts'].values():
        if sha((ROOT/row['path']).read_bytes())!=row['sha256']:raise ValueError('log drift')
    if sha(BUNDLE.read_bytes())!=v['support_snapshot']['bundle_sha256']:raise ValueError('support snapshot drift')
    if v['original_baseline_counts']!={'PASS':160,'FAIL':27,'SKIP':24,'ERROR':0}:raise ValueError('baseline drift')
    print('PASS item',item,'scientific/test receipt; original baseline and historical support remain separately scoped')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--item',type=int,required=True);p.add_argument('--artifact');p.add_argument('--report');p.add_argument('--check',action='store_true');a=p.parse_args()
    if a.check:check(a.item)
    else:
        if not a.artifact or not a.report:p.error('--artifact and --report required when building')
        build(a.item,a.artifact,a.report)
