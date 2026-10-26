#!/usr/bin/env python3
"""Join enemy/boss animation references, keeping external/unresolved refs explicit.

Controller clip membership is not proof a state plays that clip. Event names
are not evidence of the receiving script without component-level matching.
"""
import csv
import gzip
import json
import re
from collections import Counter
from pathlib import Path

RAW = Path('reverse-engineering/raw/typetrees/native-types.jsonl.gz')


def local_ref(ref):
    return isinstance(ref, dict) and ref.get('m_FileID') == 0 and bool(ref.get('m_PathID'))


def build():
    by_type = {}
    with gzip.open(RAW, 'rt') as stream:
        for line in stream:
            row = json.loads(line)
            if row['type'] not in ('Animator', 'AnimatorController', 'AnimationClip'):
                continue
            table = by_type.setdefault(row['type'], {})
            assert row['path_id'] not in table, 'Ambiguous path_id; require source-file identity'
            table[row['path_id']] = row
    with gzip.open('datas/animator_map.csv.gz', 'rt') as stream:
        roots = {int(r['animator_path_id']): r['prefab_root'] for r in csv.DictReader(stream)}
    clips = by_type['AnimationClip']
    controllers = by_type['AnimatorController']
    output = []
    for pid, animator in by_type['Animator'].items():
        root = roots.get(pid, '')
        if not re.match(r'^(CB-\d+|Boss-\d+|MB-\d+)(?:$|/)', root):
            continue
        ref = animator.get('m_Controller', {})
        controller = controllers.get(ref.get('m_PathID')) if local_ref(ref) else None
        entry = dict(prefab_root=root, animator_path_id=pid,
                     gameobject_ref=animator.get('m_GameObject'), controller_ref=ref,
                     status='resolved' if controller else 'unresolved-controller', clips=[])
        if controller:
            entry['controller_name'] = controller.get('m_Name')
            entry['controller_name_table'] = controller.get('m_TOS', [])
            entry['declared_clip_count'] = controller.get('m_AnimationClips__count')
            refs = controller.get('m_AnimationClips')
            if refs is None:
                entry['status'] = 'clip-references-not-exported'
            else:
                assert len(refs) == entry['declared_clip_count']
                for clipref in refs:
                    clip = clips.get(clipref.get('m_PathID')) if local_ref(clipref) else None
                    linked = dict(ref=clipref, status='resolved' if clip else 'unresolved-clip')
                    if clip:
                        muscle = clip.get('m_MuscleClip', {})
                        linked.update(name=clip.get('m_Name'),
                                      start=muscle.get('m_StartTime'), stop=muscle.get('m_StopTime'),
                                      loop=muscle.get('m_LoopTime'), sample_rate=clip.get('m_SampleRate'),
                                      muscle_bytes=clip.get('m_MuscleClipSize'),
                                      events=clip.get('m_Events'),
                                      declared_event_count=clip.get('m_Events__count'),
                                      curves_decoded=False)
                        if linked['events'] is not None:
                            assert len(linked['events']) == linked['declared_event_count']
                    entry['clips'].append(linked)
        output.append(entry)
    return dict(status='PROVISIONAL static membership, not runtime playback or decoded curves',
                source=str(RAW), animators=output)


def main():
    result = build()
    rows = result['animators']
    unique = {c['ref']['m_PathID']: c for r in rows for c in r['clips'] if c['status'] == 'resolved'}
    events = [(pid, c, e) for pid, c in unique.items() for e in c.get('events') or []]
    result['summary'] = dict(prefab_roots=len({r['prefab_root'] for r in rows}),
                             animator_instances=len(rows), statuses=dict(Counter(r['status'] for r in rows)),
                             unique_resolved_clips=len(unique), unique_clip_events=len(events),
                             unique_looping_clips=sum(c['loop'] is True for c in unique.values()))
    dest = Path('reverse-engineering/raw/animation-audit/enemy-clip-links.json.gz')
    # Stable gzip metadata for reproducible extraction.
    with dest.open('wb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0, filename='') as stream:
            stream.write((json.dumps(result, ensure_ascii=False, indent=1)+'\n').encode())
    lines = ['# 36 — Enemy/boss: controller → clip → events (PROVISIONAL)', '',
             'Nối PPtr local bằng path_id; từ chối path_id trùng. Không dùng khớp tên.', '',
             '```json', json.dumps(result['summary'], ensure_ascii=False, indent=2), '```', '',
             '## Event timeline theo clip duy nhất', '',
             '| Clip path_id | Clip | Time (s) | Function | int / float / string |', '|---|---|---:|---|---|']
    for pid, c, e in sorted(events, key=lambda x: (x[0], x[2].get('time', 0))):
        args = [e.get('intParameter'), e.get('floatParameter'), e.get('data')]
        lines.append(f"| {pid} | {c['name']} | {e.get('time')} | {e.get('functionName')} | {args} |")
    lines += ['', '## Prefab → controller → clips', '', '| Prefab | Animator | Controller | Clip names |', '|---|---:|---|---|']
    for r in sorted(rows, key=lambda r: (r['prefab_root'], r['animator_path_id'])):
        lines.append(f"| {r['prefab_root']} | {r['animator_path_id']} | {r.get('controller_name', r['status'])} | " + ', '.join(c.get('name', '(unresolved)') for c in r['clips']) + ' |')
    lines += ['', '## Giới hạn', '',
              '- Danh sách clip thuộc controller không phải transition graph; m_TOS chỉ là bảng tên/hash.',
              '- Event chỉ chứng minh callback được serialize ở mốc clip-time, chưa chứng minh runtime đã phát.',
              '- Chưa nối receiver component trên chính GameObject; chưa suy tên function thành loại đòn.',
              '- Chưa decode transform/float curves; không dựng lại chuyển động từ duration/event.',
              '- Đếm event theo clip path_id duy nhất, không nhân theo số instance dùng chung controller.',
              '- loop đọc từ m_MuscleClip.m_LoopTime, không dùng m_WrapMode làm thay thế.']
    Path('docs/apk-analysis/36-enemy-clip-events.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(result['summary'], ensure_ascii=False))


if __name__ == '__main__':
    main()
