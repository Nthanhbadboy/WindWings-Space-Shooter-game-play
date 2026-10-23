#!/usr/bin/env python3
"""Candidate Unity AnimationEvent receivers: same-GO component + dump method.

No runtime-delivery claim. External references and missing exports stay unknown.
"""
import gzip
import importlib.util
import json
import tempfile
from collections import Counter, defaultdict
from pathlib import Path


def build():
    links = json.load(gzip.open('reverse-engineering/raw/animation-audit/enemy-clip-links.json.gz', 'rt'))
    event_names = {e['functionName'] for a in links['animators'] for c in a['clips'] for e in c.get('events') or []}
    spec = importlib.util.spec_from_file_location('consts', 'tools/apk-analyze/il2cpp_consts.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with tempfile.NamedTemporaryFile(mode='w+') as f:
        f.write(gzip.open('reverse-engineering/il2cpp/dump.cs.gz', 'rt').read())
        f.flush()
        methods = mod.parse_dump(f.name)
    candidates = defaultdict(lambda: defaultdict(list))
    for cls, ns, name, off, rva, signature in methods:
        if name in event_names:
            candidates[cls][name].append(dict(namespace=ns, signature=signature, rva=hex(rva)))
    components = defaultdict(list)
    for path in sorted(Path('reverse-engineering/raw/typetrees').glob('*.jsonl.gz')):
        cls = path.name.removesuffix('.jsonl.gz')
        if cls not in candidates:
            continue
        with gzip.open(path, 'rt') as stream:
            for line in stream:
                row = json.loads(line)
                go = row.get('tree', {}).get('m_GameObject', {})
                if go.get('m_FileID') != 0 or not go.get('m_PathID'):
                    continue
                components[go['m_PathID']].append(dict(class_name=cls, component_path_id=row['path_id'],
                                                      source=str(path), enabled=row['tree'].get('m_Enabled')))
    events = []
    for animator in links['animators']:
        go = animator['gameobject_ref']
        same_go = components.get(go.get('m_PathID'), []) if go.get('m_FileID') == 0 else []
        for clip in animator['clips']:
            for event in clip.get('events') or []:
                receivers = []
                for component in same_go:
                    signatures = candidates[component['class_name']].get(event['functionName'], [])
                    if signatures:
                        receivers.append(dict(**component, methods=signatures))
                events.append(dict(prefab=animator['prefab_root'], animator_path_id=animator['animator_path_id'],
                                   gameobject_ref=go, clip_ref=clip['ref'], clip_name=clip['name'], event=event,
                                   receiver_candidates=receivers,
                                   status='same-gameobject-method-candidate' if receivers else 'unresolved'))
    return dict(status='PROVISIONAL static receiver candidates; overload/parameter compatibility and runtime dispatch unverified',
                source='enemy-clip-links + component m_GameObject + dump.cs method declarations', events=events)


def main():
    out = build()
    rows = out['events']
    resolved = [e for e in rows if e['receiver_candidates']]
    out['summary'] = dict(event_uses=len(rows), candidate_event_uses=len(resolved), unresolved_event_uses=len(rows)-len(resolved),
                           prefab_roots_with_candidates=len({e['prefab'] for e in resolved}))
    path = Path('reverse-engineering/raw/animation-audit/event-receivers.json.gz')
    with path.open('wb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0) as stream:
        stream.write((json.dumps(out, ensure_ascii=False, indent=1)+'\n').encode())
    counts = Counter((e['prefab'], c['class_name'], e['event']['functionName']) for e in resolved for c in e['receiver_candidates'])
    lines = ['# 37 — Animation event → receiver component (PROVISIONAL)', '',
             'Method khai báo trên component cùng GameObject với Animator; không dùng match tên toàn game.', '',
             '```json', json.dumps(out['summary'], indent=2), '```', '',
             'Event uses tính mỗi Animator/clip-reference/event; khác 731 event theo clip duy nhất ở report 36.', '',
             '| Prefab | Component class | Callback | Event uses |', '|---|---|---|---:|']
    for (prefab, cls, name), n in sorted(counts.items()):
        lines.append(f'| {prefab} | {cls} | {name} | {n} |')
    lines += ['', '## Giới hạn', '', '- Candidate chưa chứng minh overload phù hợp tham số, receiver enabled hay runtime playback.',
              '- Không tìm được receiver không có nghĩa event vô hiệu: component có thể chưa được export, method có thể kế thừa.',
              '- Không dò method trên object cha/con để gán bừa vào event của Animator.',
              '- Raw giữ PPtr, component path_id, method RVA/signature, event time và tham số.']
    Path('docs/apk-analysis/37-animation-event-receivers.md').write_text('\n'.join(lines)+'\n')
    print(out['summary'])


if __name__ == '__main__':
    main()
