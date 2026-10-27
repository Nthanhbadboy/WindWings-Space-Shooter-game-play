#!/usr/bin/env python3
"""Separate successful typetree reads from usable scoped reference resolution."""
import csv
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    ui = ROOT / 'reverse-engineering/raw/ui'
    records = []
    for p in sorted((ui / 'render-context').glob('*.jsonl.gz')):
        rows = [json.loads(line) for line in gzip.open(p, 'rt')]
        counts = Counter(r.get('status', 'missing') for r in rows)
        records.append({'source': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                        'rows': len(rows), 'read_status': dict(counts),
                        'missing_file_scope': sum(not r.get('serialized_file') for r in rows),
                        'named_assets': [{'path_id': r['path_id'], 'serialized_file': r.get('serialized_file'),
                                          'name': r.get('tree', {}).get('m_Name')}
                                         for r in rows if r.get('type') == 'TMP_FontAsset']})
    layouts = []
    for r in csv.DictReader((ui / '_index.csv').open()):
        if r['class'] not in ('Board_Maps', 'Board_Home', 'GP_Tutorials'):
            continue
        p = ui / r['file']
        d = json.load(gzip.open(p, 'rt'))
        layouts.append({'class': r['class'], 'source': str(p.relative_to(ROOT)),
                        'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                        'nodes': len(d['nodes']), 'serialized_file': d.get('serialized_file'),
                        'walk_diagnostics': d.get('walk_diagnostics', {'status': 'unknown'})})
    result = {'status': 'PROVISIONAL', 'warning': 'exported typetree does not imply external references resolved',
              'render_context': records, 'layouts': layouts}
    (ROOT / 'reverse-engineering/raw/ui-audit/render-context-audit.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
