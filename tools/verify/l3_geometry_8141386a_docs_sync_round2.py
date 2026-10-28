"""H4/121: pinned-document locators and human text-review decisions, not native proof.
provenance: arena/8141386a-windwings-space-shooter-game-p
Only selected Markdown/Git bytes are read; no peer tool import, raw/native execution,
producer edit, runtime, #27-full closure or automatic natural-language classification.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import quote

from tools.verify.geometry_8141386a_atlas_io import ROOT, BRANCH, canonical, sha, sha_file

RAW = ROOT / 'reverse-engineering/raw/geometry-8141386a/docs-sync-round2'
OUTPUT = ROOT / 'datas/l3_geometry_docs_sync_round2_8141386a.json.gz'
SPEC = 'e301feb409c75527f4c796a4a548093d4b2bf95d'
A5 = '64d3dd21054b6e8756abd8a1b9b5c83ec7133cc6'
AI4 = '97f989f389784db59b6627756055676314011423'
EF = 'ea6a3835f786306b07df9658262a6e3f6658f809'
ROLE_COMMITS = {'SPEC_DOC': SPEC, 'TEMPLATE': A5, 'A5_REPORT': A5,
                'AI4_PUBLISHED_TEXT': AI4, 'EF_PUBLISHED_TEXT_NOT_NATIVE_REVIEW': EF}
ROLE_COUNTS = {'SPEC_DOC': 13, 'TEMPLATE': 1, 'A5_REPORT': 7,
               'AI4_PUBLISHED_TEXT': 12, 'EF_PUBLISHED_TEXT_NOT_NATIVE_REVIEW': 2}
VERDICTS = {'SYNCED', 'PARTIALLY_SYNCED', 'DRIFT', 'OUT_OF_SCOPE'}
MAX_TEXT = 1_000_000


def git_blob_id(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def validate_snapshot(pin, packed):
    """Check both stored gzip and original Markdown identities, including Git blob ID."""
    if sha(packed) != pin['snapshot_sha256']:
        raise ValueError('snapshot SHA mismatch: ' + pin['snapshot'])
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        data = stream.read(MAX_TEXT + 1)
    if len(data) > MAX_TEXT or len(data) != pin['size'] or sha(data) != pin['source_sha256']:
        raise ValueError('Markdown size/SHA mismatch: ' + pin['path'])
    if git_blob_id(data) != pin['git_blob']:
        raise ValueError('Git blob identity mismatch: ' + pin['path'])
    text = data.decode('utf-8')
    if len(text.splitlines()) != pin['line_count']:
        raise ValueError('source line count mismatch: ' + pin['path'])
    return data


def load_sources(manifest=None):
    manifest = manifest or json.loads((RAW / 'peer-pins.json').read_bytes())
    if manifest['schema'] != 1 or manifest['item'] != 121 or manifest['provenance'] != BRANCH:
        raise ValueError('wrong H4 manifest provenance')
    pins = manifest['sources']
    if Counter(p['role'] for p in pins) != ROLE_COUNTS:
        raise ValueError('selected-document role coverage changed')
    sources = {}
    for p in pins:
        if p['commit'] != ROLE_COMMITS[p['role']] or not re.fullmatch('[0-9a-f]{40}', p['git_blob']):
            raise ValueError('fixed source commit/blob changed')
        path = Path(p['path'])
        if path.is_absolute() or '..' in path.parts or path.suffix != '.md' or path.parts[:2] != ('docs', 'spec' if p['role'] == 'SPEC_DOC' else 'apk-analysis'):
            raise ValueError('not a selected Markdown document')
        if Path(p['snapshot']).parent != RAW.relative_to(ROOT):
            raise ValueError('snapshot outside selected H4 folder')
        name = Path(p['snapshot']).name.removesuffix('.gz')
        if name in sources:
            raise ValueError('duplicate document key')
        data = validate_snapshot(p, (ROOT / p['snapshot']).read_bytes())
        sources[name] = dict(pin=p, data=data, text=data.decode('utf-8'))
    return sources


def verify_git(sources, fetch=False):
    """Compare selected snapshots to actual commit:path Git bytes, never checkout peers.

    Optional partial fetch obtains four fixed commits; git show reads only the selected
    Markdown blobs. No peer worktree/tool/data import and no branch switch is performed.
    This operation is explicit so ordinary unit tests remain offline.
    """
    for head in sorted({s['pin']['commit'] for s in sources.values()}):
        exists = subprocess.run(['git', '-C', str(ROOT), 'cat-file', '-e', head + '^{commit}'],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
        if not exists:
            if not fetch:
                raise ValueError('missing pinned Git commit; fetch explicitly: ' + head)
            subprocess.run(['git', '-C', str(ROOT), 'fetch', '--no-tags', '--depth=1',
                            '--filter=blob:none', 'origin', head], check=True)
    for name, s in sources.items():
        p = s['pin']
        data = subprocess.check_output(['git', '-C', str(ROOT), 'show', p['commit'] + ':' + p['path']])
        if data != s['data']:
            raise ValueError('actual pinned Git bytes disagree: ' + name)
    return len(sources)


def locate(selector, sources):
    if set(selector) != {'source', 'needle', 'before', 'after'}:
        raise ValueError('invalid selector shape')
    s = sources[selector['source']]
    text = s['text']; needle = selector['needle']
    if not needle or '\n' in needle or text.count(needle) != 1:
        raise ValueError('citation anchor must match exactly once: ' + selector['source'])
    before, after = selector['before'], selector['after']
    if any(type(n) is not int or not 0 <= n <= 8 for n in (before, after)):
        raise ValueError('unbounded citation context')
    lines = text.splitlines(keepends=True)
    anchor = text[:text.index(needle)].count('\n')
    start, stop = max(0, anchor - before), min(len(lines), anchor + after + 1)
    excerpt = ''.join(lines[start:stop])
    headings = []
    for n, line in enumerate(lines[:anchor + 1], 1):
        m = re.match(r'^(#{1,6}) (.+?)\s*$', line)
        if m:
            depth = len(m[1])
            headings = [h for h in headings if h['depth'] < depth]
            headings.append(dict(depth=depth, line=n, heading=m[2]))
    p = s['pin']
    return dict(source=selector['source'], commit=p['commit'], path=p['path'], git_blob=p['git_blob'],
                source_sha256=p['source_sha256'], start_line=start + 1, end_line=stop,
                anchor_line=anchor + 1, heading_path=headings, quote=excerpt, quote_sha256=sha(excerpt.encode()),
                url='https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/' +
                    p['commit'] + '/' + quote(p['path'], safe='/') + f'#L{start + 1}-L{stop}')


def published_text_checks(sources):
    """Small reproducible document counts/arithmetic, explicitly NOT original-data recounts."""
    log = sources['spec-DATA_SYNC.md']['text']
    headers = [(int(m[1]), log[:m.start()].count('\n') + 1, m[0])
               for m in re.finditer(r'^### 24\.(\d+) .+$', log, re.MULTILINE) if 85 <= int(m[1]) <= 96]
    if Counter(n for n, _, _ in headers) != Counter(range(85, 97)):
        raise ValueError('DATA_SYNC24.85-96 header selection mismatch')
    n1 = sources['a5-report159.md']['text']
    rows = re.findall(r'^\| (\d+) \| .*? \| \*\*(CONFIRMED|SUPERSEDED|UNVERIFIABLE)\*\* \|', n1, re.MULTILINE)
    if [int(n) for n, _ in rows] != list(range(1, 17)):
        raise ValueError('N1 published assertion table coverage changed')
    n1_counts = dict(Counter(v for _, v in rows))
    if n1_counts != {'CONFIRMED': 9, 'SUPERSEDED': 6, 'UNVERIFIABLE': 1}:
        raise ValueError('N1 published classification counts changed')
    g6 = sources['a5-report156.md']['text']
    sizes = [int(n) for n in re.findall(r'^\| `Player_.*? \| int\[(\d+)\];', g6, re.MULTILINE)]
    if sizes != [4, 7, 7, 7, 24] or g6.count('**Direct field bind:**') != 3:
        raise ValueError('G6 published table coverage changed')
    if 'Sửa lại: **10 = 4' not in sources['ai4-report147.md']['text']:
        raise ValueError('published145 correction locator missing')
    return dict(data_sync_headers_in_file_order=[dict(section=f'24.{n}', line=line, heading=h) for n, line, h in headers],
                n1_published_rows=len(rows), n1_published_classifications=n1_counts,
                g6_published_blob_lengths=sizes, g6_published_int32_sum=sum(sizes),
                g6_published_named_field_rows=3, g6_published_method_local_rows=2,
                corrected145_published_arithmetic=dict(old_reconstruction=170, corrected=174,
                    full_calls=184, gap=184-174, key_jump=4, meta_rewards=6),
                boundary='Counts parse published Markdown tables/headers and check stated arithmetic only. No native/store/blob/serialized recount.')


def review(plan, sources):
    if plan['schema'] != 1 or plan['item'] != 121 or plan['provenance'] != BRANCH:
        raise ValueError('wrong review-map provenance')
    cases = plan['cases']
    if [c['id'] for c in cases] != [f'H4-{i:02}' for i in range(1, 21)]:
        raise ValueError('human assertion IDs/coverage changed')
    compiled = []; referenced = set()
    for row in cases:
        if row['verdict'] not in VERDICTS or row['priority'] not in {'NONE', 'P1', 'P2'}:
            raise ValueError('unsupported human classification')
        if (row['priority'] == 'NONE') != (row['verdict'] in {'SYNCED', 'OUT_OF_SCOPE'}):
            raise ValueError('priority inconsistent with declared review status')
        if not all(row[k] for k in ('title', 'conclusion', 'recommendation')) or len(row['citations']) < 2:
            raise ValueError('missing review rationale/paired citations')
        citations = [locate(c, sources) for c in row['citations']]
        referenced.update(c['source'] for c in row['citations'])
        if not any(c['source'].startswith('spec-') for c in row['citations']):
            raise ValueError('no producer-spec comparison')
        compiled.append({**row, 'citations': citations})
    return compiled, referenced


def build():
    sources = load_sources()
    plan = json.loads((RAW / 'review-map.json').read_bytes())
    cases, referenced = review(plan, sources)
    counts = dict(sorted(Counter(c['verdict'] for c in cases).items()))
    paths = [str(p.relative_to(ROOT)) for p in (RAW / 'peer-pins.json', RAW / 'review-map.json')]
    paths += ['tools/verify/l3_geometry_8141386a_docs_sync_round2.py']
    paths += [s['pin']['snapshot'] for s in sources.values()]
    return dict(schema=1, item=121, provenance=BRANCH, assignment=6425374777, claim=6425778321,
                progress=6425919499, review='H4 docs-only sync-review round2; human assertions plus mechanical pinned-text checks',
                verdict=plan['verdict'], classification_rule=plan['classification_rule'],
                fixed_commits=dict(spec=SPEC, a5=A5, ai4=AI4, corrected_ef_text=EF),
                sources=[s['pin'] for s in sources.values()], cases=cases,
                counts=dict(archived_full_text_documents=len(sources), compared_assertions=len(cases),
                    exact_citations=sum(len(c['citations']) for c in cases), classifications=counts,
                    producer_actionable_assertions=sum(c['priority'] != 'NONE' for c in cases),
                    native_executions=0, raw_artifacts_inspected=0, runtime_or_readback_measurements=0),
                published_text_checks=published_text_checks(sources),
                archived_not_cited_claim_by_claim=sorted(set(sources)-referenced),
                out_of_scope=['a5 H1-H3/report160+, AI4 report148+ followups, ef126/native/instance work',
                    'Any original-APK/native/FDE/serialized reparse, byte-review or peer harness execution',
                    'Actual stored values, dispatch, Android/runtime/session/device/emulator, render, #27-full acceptance',
                    'Producer source corrections, peer tool import, self-ACK or frozen scientific-evidence mutation'],
                limits=['35 complete text snapshots do not imply every sentence or every report assertion was reviewed.',
                    'SYNCED means compared text agrees within stated bounds; it is not independent native/raw verification.',
                    'Classification is human input. GREEN checker validates source identity, quotations, locators and bookkeeping, not natural-language truth.',
                    'Legitimately superseded historical prose stays history; later explicit correction is authoritative for this pinned review.',
                    'No producer correction is claimed applied; findings belong to the pinned spec baseline, not an unobserved future head.'],
                source_pins={p: sha_file(ROOT / p) for p in sorted(paths)})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true')
    p.add_argument('--git', action='store_true', help='compare all35 actual commit:path Git bytes')
    p.add_argument('--fetch', action='store_true', help='allow explicit fixed-commit partial fetch when missing')
    a = p.parse_args()
    if a.fetch and not a.git:
        p.error('--fetch requires --git')
    value = build(); body = gzip.compress(canonical(value) + b'\n', mtime=0)
    if a.check:
        if OUTPUT.read_bytes() != body:
            raise SystemExit('H4 pinned-text artifact drift')
    else:
        OUTPUT.write_bytes(body)
    if a.git:
        print('PASS actual pinned Git Markdown bytes:', verify_git(load_sources(), a.fetch))
    print(value['verdict'], value['counts'])
    print('artifact', len(body), 'SHA256', sha(body))


if __name__ == '__main__':
    main()
