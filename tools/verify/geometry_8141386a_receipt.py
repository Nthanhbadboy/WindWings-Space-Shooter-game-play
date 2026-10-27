"""Preserve #5 per-claim/group baseline + pinned support snapshot + real test receipts.
provenance: arena/8141386a-windwings-space-shooter-game-p
Implements spec condition6415328887; never equates compatibility with geometry/runtime.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import re

from tools.verify.geometry_8141386a_sources import ROOT, RAW, canonical, sha, BRANCH
from tools.verify.geometry_8141386a_claims import BUNDLE, SPEC, unpack_support

BASELINE=RAW/'_verify_baseline.json'
RECEIPT=RAW/'verification-5.json.gz'
SCRATCH=ROOT/'.arena/geometry-8141386a'
REPORT='docs/apk-analysis/113-geometry-5-arena-8141386a-windwings-space-shooter-game-p.md'


def claims(text):
    rows=[]
    for line in text.splitlines():
        m=re.match(r'^([A-Z][A-Za-z0-9]*)\s+(PASS|FAIL|SKIP|ERROR)\s+(.*)$',line)
        if m:rows.append(dict(id=m[1],ordinal=len(rows)+1,status=m[2],group=re.match('[A-Z]+',m[1])[0],row_verbatim=line))
    n=re.search(r'^PASS (\d+) · FAIL (\d+) · SKIP (\d+) · ERROR (\d+)$',text,re.M)
    if n is None:raise ValueError('missing claim summary')
    totals=dict(zip(('PASS','FAIL','SKIP','ERROR'),map(int,n.groups())))
    actual=Counter(r['status'] for r in rows)
    # Original verifier repeats GE1/GE2 IDs. Preserve all211 assertion rows with
    # ordinals rather than silently deduplicating them or altering historical counts.
    if any(actual.get(k,0)!=v for k,v in totals.items()):
        raise ValueError('claim detail counts differ from summary: '+str(actual)+' / '+str(totals))
    groups=defaultdict(lambda:defaultdict(list))
    for row in rows:groups[row['group']][row['status']].append(row['id'])
    return dict(counts=totals,claims=rows,per_group_status_ids=dict(groups),stdout_sha256=sha(text.encode()))


def tests(text):
    m=re.search(r'^Ran (\d+) tests in ([\d.]+)s$',text,re.M)
    if m is None or not text.rstrip().endswith('OK'):raise ValueError('not a complete successful unittest receipt')
    return dict(count=int(m[1]),seconds=float(m[2]),status='PASS',stdout_sha256=sha(text.encode()))


def build():
    baseline_text=(SCRATCH/'claims-before.txt').read_text()
    baseline=claims(baseline_text)
    if baseline['counts']!={'PASS':160,'FAIL':27,'SKIP':24,'ERROR':0}:raise ValueError('original diagnostic was changed')
    base=dict(schema=1,provenance=BRANCH,scope='ORIGINAL_UNSCOPED_INHERITED_DIAGNOSTIC_DO_NOT_RELABEL',
              own_base_commit='600a4a340bd27d7e9e63a53941bbe6d97ce430bf',
              ef_source='f5a447c15a117ca4571e2768f0274d1ad4f20b39',spec_tool_source=SPEC,
              result=baseline,
              reason_groups=['Old runtime-probe/build support D; missing phone A/E and collect D.',
                             'Legacy UI/ASSETS/BALANCE doc anchors N/Q/Y/Z/IA/IAB.',
                             'Historical source S1/T4/WRH1, gzip-header AP1, unsynced APKD1/AI1/RD1.'])
    body=canonical(base)
    if BASELINE.exists() and BASELINE.read_bytes()!=body:raise ValueError('baseline is frozen, refusing rewrite')
    BASELINE.write_bytes(body)
    scoped_text=(SCRATCH/'claims-scoped-5.txt').read_text()
    unscoped_text=(SCRATCH/'claims-unscoped-5.txt').read_text()
    scoped,unscoped=claims(scoped_text),claims(unscoped_text)
    old_fails={r['id'] for r in baseline['claims'] if r['status'] in ('FAIL','ERROR')}
    now_fails={r['id'] for r in unscoped['claims'] if r['status'] in ('FAIL','ERROR')}
    if not now_fails<=old_fails or unscoped['counts']['FAIL']>baseline['counts']['FAIL']:
        raise ValueError('inherited unscoped regressions increased')
    if scoped['counts']!={'PASS':209,'FAIL':0,'SKIP':2,'ERROR':0}:raise ValueError('scoped compatibility failed')
    logs={'original_baseline':baseline_text,'scoped_historical_support':scoped_text,'current_unscoped':unscoped_text,
          'focused_tests':(SCRATCH/'focused-5.txt').read_text(),
          'full_tests':(SCRATCH/'full-tests-5-final.txt').read_text()}
    log_receipts={}
    for name,text in logs.items():
        path=RAW/('verification-5-'+name+'.log.gz');path.write_bytes(gzip.compress(text.encode(),mtime=0))
        log_receipts[name]=dict(path=str(path.relative_to(ROOT)),bytes=path.stat().st_size,sha256=sha(path.read_bytes()))
    snapshot=json.loads(gzip.decompress(BUNDLE.read_bytes()))
    files=unpack_support()
    support=dict(scope=snapshot['scope'],source_commit=SPEC,bundle_path=str(BUNDLE.relative_to(ROOT)),
                 bundle_sha256=sha(BUNDLE.read_bytes()),path_groups=snapshot['path_groups'],exact=snapshot['exact'],
                 path_set=[{k:v for k,v in item.items() if k!='base64'} for item in snapshot['files']],
                 path_count=len(files),note='Snapshot and every per-group FAIL/SKIP result retained; no view reconstruction needed for review')
    pins=[REPORT,'tools/verify-claims.py','tools/refresh-readme-sizes.py','tools/raw-audit.py',
          'docs/spec/START_HERE.md','docs/spec/README.md',
          'reverse-engineering/raw/geometry-8141386a/verification-support-imports.json',
          'datas/l3_geometry_bounds.json.gz',str(BASELINE.relative_to(ROOT))]
    pins += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'tools/verify').glob('*8141386a*.py'))]
    pins += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'tests').glob('test_geometry_8141386a*.py'))]
    pins += ['.github/workflows/verify-geometry-8141386a.yml']
    result=dict(schema=1,provenance=BRANCH,item=5,support_snapshot=support,original_baseline=base,
                scoped_historical_support_result=scoped,current_unscoped_result=unscoped,
                unscoped_regression=dict(new_failure_ids=sorted(now_fails-old_fails),fail_count_not_increased=True),
                focused_tests=tests(logs['focused_tests']),full_tests=tests(logs['full_tests']),
                log_receipts=log_receipts,worktree_pins={p:sha((ROOT/p).read_bytes()) for p in sorted(set(pins))},
                live_needles=json.loads((RAW/'verification-support-imports.json').read_bytes())['current_needles'],
                scientific_ci='Recorded separately AFTER actual GitHub success; do not mistake recovery/setup CI for final scientific CI',
                boundary='Scoped historical-support compatibility, not all current ef raw/runtime-probe, Unity readback, native generator or render acceptance.')
    RECEIPT.write_bytes(gzip.compress(canonical(result),mtime=0))
    print('Saved per-claim/per-group baseline, current diagnostic, scoped support snapshot, focused/full test logs',RECEIPT.stat().st_size,'bytes')


def check():
    v=json.loads(gzip.decompress(RECEIPT.read_bytes()))
    if v['provenance']!=BRANCH or v['item']!=5:raise ValueError('wrong report receipt')
    if v['support_snapshot']['source_commit']!=SPEC or sha(BUNDLE.read_bytes())!=v['support_snapshot']['bundle_sha256']:
        raise ValueError('support snapshot drift')
    for p,d in v['worktree_pins'].items():
        if sha((ROOT/p).read_bytes())!=d:raise ValueError('worktree/report receipt drift: '+p)
    for item in v['log_receipts'].values():
        if sha((ROOT/item['path']).read_bytes())!=item['sha256']:raise ValueError('test/claim log drift')
    if v['original_baseline']['result']['counts']!={'PASS':160,'FAIL':27,'SKIP':24,'ERROR':0}:raise ValueError('baseline drift')
    if not v['unscoped_regression']['fail_count_not_increased'] or v['unscoped_regression']['new_failure_ids']:
        raise ValueError('unscoped regression')
    print('PASS: #5 byte/artifact/test receipt + approved historical-support snapshot boundary')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    check() if args.check else build()
