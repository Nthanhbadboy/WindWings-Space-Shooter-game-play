#!/usr/bin/env python3
"""Resolve local SkeletonAnimation->SkeletonDataAsset->TextAsset and prefab root."""
import csv
import gzip
import json
import re
from collections import Counter
from pathlib import Path

RAW = Path('reverse-engineering/raw/typetrees')


def main():
    with gzip.open(RAW / 'transform-tree.tsv.gz', 'rt') as stream:
        next(stream)
        transforms = [tuple(map(int, line.strip().split('\t'))) for line in stream]
    parents = {t: p for t, g, p in transforms}
    go_to_transform = {g: t for t, g, p in transforms if g}
    with (RAW / 'prefab-roots.csv').open() as stream:
        roots = {int(r['transform_path_id']): r['name'] for r in csv.DictReader(stream)}

    def root_for(go):
        t = go_to_transform.get(go)
        visited = set()
        while t and t not in visited:
            visited.add(t)
            if not parents.get(t):
                return roots.get(t)
            t = parents[t]
        return None

    rigs = {r['skeleton_data_path_id']: r for r in json.load(open('datas/spine.json'))['rigs']}
    assets = {}
    for line in gzip.open(RAW / 'SkeletonDataAsset.jsonl.gz', 'rt'):
        row = json.loads(line)
        assert row['path_id'] not in assets
        assets[row['path_id']] = row['tree']
    rows = []
    for line in gzip.open(RAW / 'SkeletonAnimation.jsonl.gz', 'rt'):
        row = json.loads(line)
        tree = row['tree']
        go = tree.get('m_GameObject', {})
        root = root_for(go.get('m_PathID')) if go.get('m_FileID') == 0 else None
        if not root or not re.match(r'^(Boss-|CB-|MB-)\d+(?:$|/)', root):
            continue
        ref = tree.get('skeletonDataAsset', {})
        asset = assets.get(ref.get('m_PathID')) if ref.get('m_FileID') == 0 else None
        rig = rigs.get(ref.get('m_PathID')) if asset else None
        result = dict(prefab=root, component_path_id=row['path_id'], gameobject_ref=go,
                      skeleton_data_ref=ref, status='resolved' if rig else 'unresolved',
                      initial_animation=tree.get('_animationName'), initial_skin=tree.get('initialSkinName'),
                      component_loop=tree.get('loop'), time_scale=tree.get('timeScale'))
        if asset and rig:
            textref = asset['skeletonJSON']
            assert textref['m_FileID'] == 0 and textref['m_PathID'] == rig['skeleton_json_path_id']
            result.update(skeleton_json_ref=textref, scale=asset.get('scale'),
                          default_mix=asset.get('defaultMix'),
                          explicit_mixes=dict(fromAnimation=asset.get('fromAnimation'),
                                              toAnimation=asset.get('toAnimation'), duration=asset.get('duration')),
                          animations=rig['animations'], animation_seconds=rig['animation_seconds'],
                          events=rig['events'])
        rows.append(result)
    out = dict(status='PROVISIONAL static local-PPtr joins, not proof of runtime playback; no skeleton__N filename assumptions',
               summary=dict(components=len(rows), prefabs=len({r['prefab'] for r in rows}), statuses=dict(Counter(r['status'] for r in rows))),
               components=rows)
    Path('reverse-engineering/raw/animation-audit/spine-prefabs.json').write_text(json.dumps(out, ensure_ascii=False, indent=1)+'\n')
    lines = ['# 38 — Enemy/boss Spine PPtr joins (PROVISIONAL)', '',
             'SkeletonAnimation → local SkeletonDataAsset → local TextAsset, không đoán theo tên/bone.', '',
             '```json', json.dumps(out['summary'], indent=2), '```', '',
             '| Prefab | Component | SDA | JSON TextAsset | Initial animation | Scale | Mix |', '|---|---:|---:|---:|---|---:|---:|']
    for r in rows:
        lines.append(f"| {r['prefab']} | {r['component_path_id']} | {r['skeleton_data_ref'].get('m_PathID')} | {r.get('skeleton_json_ref', {}).get('m_PathID')} | {r['initial_animation']} | {r.get('scale')} | {r.get('default_mix')} |")
    lines += ['', 'Nguồn raw giữ danh sách animation, thời lượng, explicit mix và PPtr.',
              'Không coi không tìm thấy SkeletonAnimation là không dùng Spine (có thể renderer/subclass khác).',
              'component_loop chỉ là giá trị serialize ban đầu; script có thể đổi state/loop lúc chạy.',
              'TextAsset path_id là định danh trong tập raw hiện tại; không đồng nhất với tên file skeleton__N.']
    Path('docs/apk-analysis/38-spine-prefab-links.md').write_text('\n'.join(lines)+'\n')
    print(out['summary'])


if __name__ == '__main__':
    main()
