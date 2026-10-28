#!/usr/bin/env python3
"""Decode exported Unity ControllerConstant wrappers without inventing graph edges."""
import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path


def unwrap(value):
    return value.get('data', value) if isinstance(value, dict) else value


def transitions(items, names):
    output = []
    for item in items:
        t = unwrap(item)
        conditions = []
        for item_c in t.get('m_ConditionConstantArray', []):
            c = unwrap(item_c)
            conditions.append(dict(raw=c, parameter_name=names.get(c.get('m_EventID'))))
        output.append(dict(raw=t, conditions=conditions))
    return output


def main():
    links = json.load(gzip.open('reverse-engineering/raw/animation-audit/enemy-clip-links.json.gz', 'rt'))
    used = defaultdict(set)
    for row in links['animators']:
        if row['status'] == 'resolved':
            used[row['controller_ref']['m_PathID']].add(row['prefab_root'])
    output = []
    for line in gzip.open('reverse-engineering/raw/typetrees/animator-controller-graphs.jsonl.gz', 'rt'):
        row = json.loads(line)
        if row['path_id'] not in used:
            continue
        tree = row['tree']
        controller = tree['m_Controller']
        names = dict(tree['m_TOS'])
        parameters = [dict(raw=p, name=names.get(p['m_ID'])) for p in unwrap(controller['m_Values'])['m_ValueArray']]
        machines = []
        for mi, wrapped in enumerate(controller['m_StateMachineArray']):
            machine = unwrap(wrapped)
            states = []
            for si, item in enumerate(machine['m_StateConstantArray']):
                state = unwrap(item)
                nodes = []
                for bi, blend in enumerate(state.get('m_BlendTreeConstantArray', [])):
                    for ni, node in enumerate(unwrap(blend).get('m_NodeArray', [])):
                        node = unwrap(node)
                        clip_index = node.get('m_ClipID')
                        ref = tree['m_AnimationClips'][clip_index] if isinstance(clip_index, int) and 0 <= clip_index < len(tree['m_AnimationClips']) else None
                        nodes.append(dict(blend_index=bi, node_index=ni, raw=node, clip_ref_candidate=ref))
                states.append(dict(index=si, name=names.get(state.get('m_NameID')),
                                   path_name=names.get(state.get('m_FullPathID')),
                                   name_id=state.get('m_NameID'), speed=state.get('m_Speed'),
                                   transitions=transitions(state.get('m_TransitionConstantArray', []), names), blend_nodes=nodes))
            machines.append(dict(index=mi, default_state_index=machine.get('m_DefaultState'), states=states,
                                 any_state_transitions=transitions(machine.get('m_AnyStateTransitionConstantArray', []), names),
                                 selectors_raw=machine.get('m_SelectorStateConstantArray', [])))
        output.append(dict(path_id=row['path_id'], name=tree['m_Name'], prefab_roots=sorted(used[row['path_id']]),
                           parameters=parameters, machines=machines, layers_raw=controller['m_LayerArray'],
                           defaults_raw=controller['m_DefaultValues']))
    assert {r['path_id'] for r in output} == set(used), 'Missing controller graphs'
    all_transitions = [t for r in output for m in r['machines'] for t in m['any_state_transitions'] + [t for s in m['states'] for t in s['transitions']]]
    summary = dict(controllers=len(output), prefab_roots=len(set().union(*used.values())),
                   parameters=sum(len(r['parameters']) for r in output),
                   states=sum(len(m['states']) for r in output for m in r['machines']),
                   transitions=len(all_transitions), conditional_transitions=sum(bool(t['conditions']) for t in all_transitions))
    result = dict(status='PROVISIONAL static graph; raw destination encodings preserved (no guessed cross-machine edges)', summary=summary, controllers=output)
    with Path('reverse-engineering/raw/animation-audit/controller-graphs.json.gz').open('wb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0) as stream:
        stream.write((json.dumps(result, ensure_ascii=False, indent=1)+'\n').encode())
    lines = ['# 40 — Enemy/boss Animator graph (PROVISIONAL)', '',
             'Nguồn ControllerConstant đầy đủ, không suy transition từ m_TOS.', '',
             '```json', json.dumps(summary, indent=2), '```', '',
             '| Controller path_id | Name | Prefab count | Parameters (name:type-code) | States |', '|---|---|---:|---|---:|']
    for r in output:
        lines.append(f"| {r['path_id']} | {r['name']} | {len(r['prefab_roots'])} | " + ', '.join(f"{p['name']}:{p['raw']['m_Type']}" for p in r['parameters']) + f" | {sum(len(m['states']) for m in r['machines'])} |")
    lines += ['', 'Parameter type-code giữ numeric gốc; raw có threshold/mode/hasExitTime/default state/speed.',
              'Không có parameter không chứng minh script gọi Play: có thể tự phát default state/exit-time transition.',
              'ClipID được giữ cùng raw blend-node; clip_ref_candidate chưa phải playback trace.',
              'Tập này là 63 prefab theo filter CB-/Boss-/MB-, không đồng nhất roster 109 của nhánh spec.']
    Path('docs/apk-analysis/40-animator-controller-graphs.md').write_text('\n'.join(lines)+'\n')
    print(summary)


if __name__ == '__main__':
    main()
