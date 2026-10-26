#!/usr/bin/env python3
"""Measure drawing inputs, not runtime flow completeness, from indexed APK layouts."""
import collections
import csv
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCREENS = ('Board_Home', 'Board_Maps', 'Board_Stage', 'Board_Endgame',
           'Board_Players', 'Board_Drones', 'Board_Pause', 'Board_Reborn', 'Board_Reborn_IAP')


def sprite_match(name, by_name):
    matches = by_name.get(name, [])
    return {'status': 'unique_name_candidate' if len(matches) == 1 else
            'ambiguous_name' if matches else 'not_in_index', 'candidates': matches}


def main():
    ui = ROOT / 'reverse-engineering/raw/ui'
    index = list(csv.DictReader((ui / '_index.csv').open()))
    by_name = collections.defaultdict(list)
    # Gallery names are sanitized filenames, not the original Unity names.
    # Join original-name table to gallery by (type, path_id); never guess a
    # sanitized filename because collision suffixes can select another sprite.
    gallery = collections.defaultdict(list)
    for row in csv.DictReader((ROOT / 'docs/assets/sprites-index.csv').open()):
        gallery[(row['kind'], row['path_id'])].append(row)
    for row in csv.DictReader((ROOT / 'datas/sprites.csv').open()):
        if row['type'] != 'Sprite':
            continue
        for asset in gallery.get((row['type'], row['path_id']), []):
            by_name[row['name']].append(dict(asset, unity_name=row['name']))
    vi = json.loads((ROOT / 'i18n/vi.json').read_text())['strings']
    records = []
    for row in index:
        if row['class'] not in SCREENS:
            continue
        p = ui / row['file']
        d = json.load(gzip.open(p, 'rt'))
        counts = collections.Counter()
        visual = []
        for n in d['nodes']:
            counts['nodes'] += 1
            counts['position_present'] += n.get('local_pos') is not None
            counts['rect_size_present'] += n.get('size_delta') is not None
            comps = n.get('components', [])
            counts['button_nodes'] += any('Button' in c.get('class', '') for c in comps)
            for c in comps:
                if c.get('class') == 'SpriteRenderer':
                    counts['sprite_renderers'] += 1
                    counts['sprite_name_present'] += bool(c.get('sprite'))
                if c.get('class') in ('TextMeshPro', 'TextMeshProUGUI'):
                    counts['tmp_components'] += 1
                    counts['tmp_text_present'] += bool(c.get('text'))
                if c.get('key'):
                    counts['localization_keys'] += 1
                    counts['vi_resolved'] += c['key'] in vi
                if not (c.get('sprite') or c.get('text') or c.get('key')):
                    continue
                v = {'path': n['path'], 'active_in_prefab': n.get('active'),
                     'component': c, 'local_pos': n.get('local_pos'),
                     'scale': n.get('scale'), 'size_delta': n.get('size_delta')}
                if c.get('sprite'):
                    counts['sprite_components_with_name'] += 1
                    v['sprite_join'] = sprite_match(c['sprite'], by_name)
                    counts[v['sprite_join']['status']] += 1
                if c.get('key'):
                    v['vi'] = vi.get(c['key'])
                visual.append(v)
        records.append({'class': row['class'], 'source': str(p.relative_to(ROOT)),
                        'source_sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                        'counts': dict(counts), 'visual_nodes': visual})
    out = ROOT / 'reverse-engineering/raw/ui-audit/drawing-inputs.json.gz'
    with gzip.open(out, 'wt') as f:
        json.dump({'status': 'PROVISIONAL', 'selection': 'current ui/_index.csv, not historical glob',
                   'warning': 'name joins are candidates, not exact PPtr resolution; local position is parent-relative',
                   'screens': records}, f, ensure_ascii=False, indent=2)
    for r in records:
        print(r['class'], r['counts'])


if __name__ == '__main__':
    main()
