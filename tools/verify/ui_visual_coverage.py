#!/usr/bin/env python3
"""Audit current indexed styles and tutorial linked panels; no runtime assumptions."""
import csv
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCREENS = {'Board_Home', 'Board_Maps', 'Board_Stage', 'Board_Endgame', 'Board_Pause',
           'Board_Players', 'Board_Drones', 'Board_Reborn', 'Board_Reborn_IAP',
           'GP_Tutorials', 'Tut_Settings', 'Tut_Settings1'}


def panel_inventory(panels, strings):
    result = []
    for panel in panels:
        texts = []
        for node in panel.get('nodes', []):
            for c in node.get('components', []):
                if 'key' in c:
                    texts.append({'node': node['path'], 'key': c['key'],
                                  'vi': strings.get(c['key']), 'status': 'resolved' if c['key'] in strings else 'missing_key'})
        result.append({'field': panel['field'], 'reference': panel['reference'],
                       'status': panel['status'], 'nodes': len(panel.get('nodes', [])), 'texts': texts})
    return result


def main():
    ui = ROOT / 'reverse-engineering/raw/ui'
    strings = json.loads((ROOT / 'i18n/vi.json').read_text())['strings']
    result = []
    for row in csv.DictReader((ui / '_index.csv').open()):
        if row['class'] not in SCREENS:
            continue
        p = ui / row['file']
        d = json.load(gzip.open(p, 'rt'))
        counts = Counter()
        for n in d['nodes']:
            for c in n['components']:
                v = c.get('visual_properties', {})
                if c['class'] in ('TextMeshPro', 'TextMeshProUGUI'):
                    counts['tmp'] += 1
                    counts['tmp_font_ref'] += bool(v.get('m_fontAsset'))
                    counts['tmp_size'] += 'm_fontSize' in v
                if c['class'] == 'SpriteRenderer':
                    counts['sprite_renderer'] += 1
                    counts['sprite_ref'] += 'm_Sprite' in v
                    counts['sorting_order'] += 'm_SortingOrder' in v
        result.append({'class': row['class'], 'source': str(p.relative_to(ROOT)),
                       'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'counts': dict(counts),
                       'node_count': len(d['nodes']),
                       'walk_diagnostics': d.get('walk_diagnostics', {'status': 'legacy_no_explicit_truncation', 'at_old_6000_limit': len(d['nodes']) >= 6000}),
                       'panels': panel_inventory(d.get('linked_panels', []), strings)})
    cameras = []
    p = ROOT / 'reverse-engineering/raw/typetrees/native-types.jsonl.gz'
    for line in gzip.open(p, 'rt'):
        d = json.loads(line)
        if d.get('type') == 'Camera':
            cameras.append(d)
    out = {'status': 'PROVISIONAL', 'scope': 'current _index only; styles serialized, not screen pixels',
           'screens': result, 'cameras': {'source': str(p.relative_to(ROOT)),
                                         'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'records': cameras}}
    p = ROOT / 'reverse-engineering/raw/ui-audit/visual-coverage.json'
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    for r in result:
        print(r['class'], r['counts'])
    print('camera records', len(cameras))


if __name__ == '__main__':
    main()
