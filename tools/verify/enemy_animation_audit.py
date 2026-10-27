#!/usr/bin/env python3
"""Offline evidence inventory: never equate a controller name with a clip name."""
import csv
import gzip
import json
import re
from collections import Counter
from pathlib import Path

RAW = Path('reverse-engineering/raw/typetrees')

def main():
    with gzip.open('datas/animator_map.csv.gz', 'rt') as f:
        animators = [r for r in csv.DictReader(f)
                     if re.match(r'^(CB-\d+|Boss-\d+|MB-\d+)(?:$|/)', r['prefab_root'])]
    groups = {}
    for r in animators:
        groups.setdefault(r['prefab_root'], []).append(r)
    bindings = []
    for path in sorted(RAW.glob('*.jsonl.gz')):
        if not any(k in path.name for k in ('Director', 'Enemy_')):
            continue
        with gzip.open(path, 'rt') as f:
            for line in f:
                r = json.loads(line)
                fields = {k: v for k, v in r.get('tree', {}).items()
                          if isinstance(v, str) and v and re.search(r'state|anim', k, re.I)
                          and not k.startswith('m_')}
                if fields:
                    bindings.append(dict(source=str(path), path_id=r['path_id'],
                                         gameobject=r.get('gameobject'), fields=fields,
                                         animation_component=r['tree'].get('skeleton')))
    clips = []
    controllers = []
    with gzip.open(RAW / 'native-types.jsonl.gz', 'rt') as f:
        for line in f:
            r = json.loads(line)
            if r['type'] == 'AnimationClip':
                clips.append(r)
            elif r['type'] == 'AnimatorController':
                controllers.append(r)
    names = Counter(r['m_Name'] for r in clips)
    for b in bindings:
        b['name_candidates_only'] = {k: names.get(v, 0) for k, v in b['fields'].items()}
    out = dict(status='PROVISIONAL static evidence; no runtime animation playback verified',
               prefab_animators=groups, serialized_animation_bindings=bindings,
               limits=['Controller->clip references omitted by old exporter; names are NOT a verified join',
                       'No decoded Unity transform/float curves; missing curves do not mean no animation',
                       'Spine rigs not assigned to enemy/boss by guesswork'],
               global_clip_count=len(clips))
    dest = Path('reverse-engineering/raw/animation-audit')
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'enemy-boss.json').write_text(json.dumps(out, ensure_ascii=False, indent=1)+'\n')
    report = ['# 32 — Kiểm animation enemy/boss (tạm thời)', '',
              'Nguồn: Animator prefab joins + raw MonoBehaviour fields. Không coi khớp tên là khớp clip.', '',
              f'- {len(groups)} prefab root có Animator, {len(animators)} instance (lọc CB-/Boss-/MB- + id).',
              f'- {len(bindings)} component có serialized state/animation-name fields.',
              '- Chưa decode Unity keyframe; chưa xác minh state machine transition hoặc runtime playback.',
              '- Raw đối chiếu: `reverse-engineering/raw/animation-audit/enemy-boss.json`.', '',
              '## State được serialize trực tiếp', '', '| Object | Component source | Fields |', '|---|---|---|']
    for b in bindings:
        report.append(f"| {b['gameobject']} | {Path(b['source']).name} | " + '; '.join(f'{k}={v}' for k,v in b['fields'].items()) + ' |')
    report += ['', '## Animator theo prefab', '', '| Prefab | Instances | Controller names (không phải clip) |', '|---|---:|---|']
    for root, rows in sorted(groups.items()):
        report.append(f"| {root} | {len(rows)} | " + ', '.join(sorted({r['controller_name'] or '(unresolved)' for r in rows})) + ' |')
    Path('docs/apk-analysis/32-enemy-boss-animation.md').write_text('\n'.join(report)+'\n')
    print(f'{len(groups)} roots / {len(animators)} Animator instances / {len(bindings)} state-bearing components')

if __name__ == '__main__':
    main()
