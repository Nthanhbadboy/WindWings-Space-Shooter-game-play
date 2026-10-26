#!/usr/bin/env python3
"""Audit asset/declaration coverage; never infer stage gates from method names."""
import collections
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLASSES = ('DataTutorials', 'GP_Tutorials', 'Board_Home', 'Board_Maps',
           'Board_Stage', 'Board_Endgame', 'Board_Players', 'Board_Drones',
           'Board_Pause', 'Board_Reborn', 'Board_Reborn_IAP', 'BoardManager',
           'SkipTutorial', 'Tut_Settings', 'Tut_Settings1')


def audit(root=ROOT):
    dump = root / 'reverse-engineering/il2cpp/dump.cs.gz'
    text = gzip.open(dump, 'rt').read()
    declarations = {}
    for block in re.split(r'(?=// Namespace:)', text):
        m = re.search(r'public class (\w+)\s*:', block)
        if not m:
            m = re.search(r'public class (\w+)\s*\n', block)
        if m and m[1] in CLASSES:
            declarations[m[1]] = block
    layouts = collections.defaultdict(list)
    components = collections.defaultdict(set)
    for p in sorted((root / 'reverse-engineering/raw/ui').glob('*.json.gz')):
        d = json.load(gzip.open(p, 'rt'))
        nodes = d.get('nodes', [])
        for node in nodes:
            for c in node.get('components', []):
                if c.get('class') in CLASSES:
                    components[c['class']].add(str(p.relative_to(root)))
        if d.get('class') in CLASSES:
            # Root IDs in old layout filenames are not stable Unity PPtr IDs.
            digest = hashlib.sha256(json.dumps(nodes, sort_keys=True).encode()).hexdigest()
            layouts[d['class']].append({
                'source': str(p.relative_to(root)), 'nodes_sha256': digest,
                'node_count': len(nodes),
                'relevant_nodes': [{'path': n.get('path'), 'active': n.get('active'),
                                    'component_classes': [c.get('class') for c in n.get('components', [])]}
                                   for n in nodes if re.search(
                    r'tut|focus|unlock|lock|continue|replay|back|play|pause|skill|drone|upgrade',
                    n.get('path', ''), re.I)]})
    rows = []
    for cls in CLASSES:
        p = root / f'reverse-engineering/raw/il2cpp-consts/{cls}.json'
        rows.append({'class': cls, 'declaration_found': cls in declarations,
                     'layout_exports': len(layouts[cls]),
                     'distinct_node_hashes': len({x['nodes_sha256'] for x in layouts[cls]}),
                     'component_layout_sources': sorted(components[cls]),
                     'native_export_available': p.exists()})
    return {'status': 'PROVISIONAL', 'source_dump_sha256': hashlib.sha256(dump.read_bytes()).hexdigest(),
            'scope': 'asset/declaration inventory, NOT execution coverage or stage-to-tutorial mapping',
            'classes': rows, 'declarations': declarations, 'layouts': dict(layouts),
            'stage_gates': [{'display_stage': n, 'tutorial': 'UNRESOLVED',
                             'post_victory_popup_order': 'UNRESOLVED',
                             'replay_once_flags': 'UNRESOLVED'} for n in (1, 2, 3)]}


def main():
    d = audit()
    out = ROOT / 'reverse-engineering/raw/ui-audit'
    out.mkdir(exist_ok=True)
    with gzip.open(out / 'early-stage-coverage.json.gz', 'wt') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print(json.dumps(d['classes'], indent=2))


if __name__ == '__main__':
    main()
