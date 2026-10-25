#!/usr/bin/env python3
"""Inventory serialized UnityEvent calls in available raw components.

UnityEvent is inline serialized data, not a standalone PPtr object.
Missing exported classes cannot be interpreted as zero uses in the APK.
"""
import gzip
import json
from collections import Counter
from pathlib import Path


def walk(value, path=''):
    if isinstance(value, dict):
        if isinstance(value.get('m_PersistentCalls'), dict):
            yield path, value['m_PersistentCalls'].get('m_Calls')
        for key, child in value.items():
            yield from walk(child, f'{path}.{key}' if path else key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f'{path}[{index}]')


def main():
    fields, counts = [], Counter()
    for source in sorted(Path('reverse-engineering/raw/typetrees').glob('*.jsonl.gz')):
        cls = source.name.removesuffix('.jsonl.gz')
        if cls in ('native-types', 'script-links'):
            continue
        for line in gzip.open(source, 'rt'):
            row = json.loads(line)
            tree = row.get('tree')
            if not isinstance(tree, dict):
                continue
            for field, calls in walk(tree):
                counts[cls] += 1
                fields.append(dict(owner_class=cls, owner_path_id=row['path_id'],
                                   gameobject=row.get('gameobject'), owner_gameobject_ref=tree.get('m_GameObject'),
                                   field=field, calls=calls, source=str(source)))
    nonempty = [f for f in fields if f['calls']]
    relevant = [f for f in fields if f['owner_class'].startswith(('Enemy_', 'Boss', 'MB', 'MiniBoss'))]
    result = dict(status='PROVISIONAL: available serialized components only; dynamic listeners not included',
                  summary=dict(event_fields=len(fields), nonempty_fields=len(nonempty),
                               persistent_calls=sum(len(f['calls'] or []) for f in fields),
                               relevant_enemy_boss_fields=len(relevant),
                               relevant_enemy_boss_calls=sum(len(f['calls'] or []) for f in relevant)),
                  fields=fields)
    out = Path('reverse-engineering/raw/animation-audit/persistent-calls.json.gz')
    with out.open('wb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0) as stream:
        stream.write((json.dumps(result, ensure_ascii=False, indent=1)+'\n').encode())
    lines = ['# 39 — Serialized UnityEvent persistent calls (PROVISIONAL)', '',
             'Quét đệ quy raw typetree hiện có; giữ cả field rỗng. Không suy ra dynamic listener.', '',
             '```json', json.dumps(result['summary'], indent=2), '```', '',
             '| Owner class | Object | Field | Calls |', '|---|---|---|---:|']
    for f in nonempty:
        lines.append(f"| {f['owner_class']} | {f['gameobject']} | {f['field']} | {len(f['calls'])} |")
    lines += ['', '## Giới hạn', '', '- UnityEvent chứa m_PersistentCalls inline, không phải asset PPtr riêng cần dereference.',
              '- Mỗi m_Target trong call vẫn là PPtr; raw giữ nguyên method/mode/arguments/call state.',
              '- Không tìm thấy call trong một class không chứng minh game chỉ nối bằng code.',
              '- Class không được export hoặc instance tạo runtime không nằm trong phép đo này.']
    Path('docs/apk-analysis/39-persistent-animation-events.md').write_text('\n'.join(lines)+'\n')
    print(result['summary'])
    print('Enemy_Movement:', [(f['field'], len(f['calls'] or [])) for f in relevant if f['owner_class']=='Enemy_Movement'][:3])


if __name__ == '__main__':
    main()
