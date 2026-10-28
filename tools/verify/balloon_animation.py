"""Decode BB-36001 serialized streamed keys; not a Unity playback simulator.

Format reference (not game evidence): AssetStudio d158e864b556b5970709c2a52e47944d53aa98a2,
AnimationClip.cs StreamedClip / AnimationClipBindingConstant, preserved with MIT license.
"""
import base64
import gzip
import hashlib
import json
import math
from pathlib import Path
import struct
import zlib

RAW = Path('reverse-engineering/raw/balloon-animation')
SOURCE = RAW / 'bb-36001-animation.json.gz'


def decode_stream(words, curve_count):
    data = struct.pack('<' + 'I' * len(words), *words)
    frames, offset, previous = [], 0, -math.inf
    while offset < len(data):
        if offset + 8 > len(data):
            raise ValueError('truncated frame header')
        time, count = struct.unpack_from('<fi', data, offset)
        offset += 8
        if math.isnan(time) or time < previous or count < 0 or offset + count * 20 > len(data):
            raise ValueError('invalid frame time/count')
        previous = time
        keys, seen = [], set()
        for _ in range(count):
            index, *coeff = struct.unpack_from('<i4f', data, offset)
            if index < 0 or index >= curve_count or index in seen:
                raise ValueError('invalid/duplicate curve index')
            seen.add(index)
            keys.append(dict(index=index, coeff=coeff, value=coeff[3], byte_offset=offset))
            offset += 20
        # The first frame is -FLT_MAX, not -Infinity. Preserve that distinction.
        frames.append(dict(time=time if math.isfinite(time) else str(time), keys=keys))
    return frames


def width(binding):
    return {1: 3, 2: 4, 3: 3, 4: 3}.get(binding['attribute'], 1) if binding['typeID'] == 4 else 1


def path_index(nodes):
    paths = {}
    for node in nodes:
        relative = node['path'].partition('/')[2]
        paths.setdefault(zlib.crc32(relative.encode()), []).append(dict(
            path=relative, gameobject=node['gameobject'], components=node['components']))
    return paths  # Never overwrite duplicate names/hash collisions.


def decode_clip(record, paths):
    tree = record['tree']
    muscle = tree['m_MuscleClip']
    data = muscle['m_Clip']['data']
    stream, dense, constant = data['m_StreamedClip'], data['m_DenseClip'], data['m_ConstantClip']['data']
    frames = decode_stream(stream['data'], stream['curveCount'])
    if len(dense['m_SampleArray']) != dense['m_FrameCount'] * dense['m_CurveCount']:
        raise ValueError('dense sample size mismatch')
    bindings, cursor = [], 0
    for binding in tree['m_ClipBindingConstant']['genericBindings']:
        channels = []
        for index in range(cursor, cursor + width(binding)):
            if index < stream['curveCount']:
                keys = [dict(time=f['time'], **k) for f in frames for k in f['keys'] if k['index'] == index]
                finite = [k for k in keys if isinstance(k['time'], (float, int)) and 0 <= k['time'] <= muscle['m_StopTime']]
                values = [k['value'] for k in finite]
                channels.append(dict(index=index, storage='streamed', keys=keys,
                                     keyed_range=[min(values), max(values)] if values else None))
            elif index < stream['curveCount'] + dense['m_CurveCount']:
                raise ValueError('dense channel decoding deliberately unsupported')
            else:
                i = index - stream['curveCount'] - dense['m_CurveCount']
                if i >= len(constant):
                    raise ValueError('binding channel outside clip data')
                channels.append(dict(index=index, storage='constant', value=constant[i], keyed_range=[constant[i], constant[i]]))
        candidates = paths.get(binding['path'], [])
        target_components = []
        for node in candidates:
            for component in node['components']:
                if binding['typeID'] == 114:
                    if component.get('header_script_pointer') != binding['script']:
                        continue
                elif component['type'] != {4: 'Transform', 61: 'BoxCollider2D'}.get(binding['typeID']):
                    continue
                target_components.append(dict(path=node['path'], path_id=component['path_id'],
                                              type=component.get('script_class', component['type'])))
        bindings.append(dict(binding=binding, paths=[n['path'] for n in candidates],
                             targets=target_components, channels=channels))
        cursor += width(binding)
    if cursor != stream['curveCount'] + dense['m_CurveCount'] + len(constant):
        raise ValueError('binding coverage mismatch')
    return dict(path_id=record['path_id'], name=tree['m_Name'], start=muscle['m_StartTime'],
                stop=muscle['m_StopTime'], loop=muscle['m_LoopTime'], events=tree['m_Events'],
                sample_rate=tree['m_SampleRate'], streamed_curve_count=stream['curveCount'],
                dense_curve_count=dense['m_CurveCount'], constant_count=len(constant),
                frames=frames, bindings=bindings)


def build():
    source_bytes = gzip.decompress(SOURCE.read_bytes())
    raw = json.loads(source_bytes)
    paths = path_index(raw['nodes'])
    clips = [decode_clip(c, paths) for c in raw['clips']]
    controller = raw['controller']['tree']
    tos = dict(controller['m_TOS'])
    machine = controller['m_Controller']['m_StateMachineArray'][0]['data']
    states = []
    for entry in machine['m_StateConstantArray']:
        state = entry['data']
        states.append(dict(name=tos[state['m_NameID']], speed=state['m_Speed'],
                           transitions=[t['data'] for t in state['m_TransitionConstantArray']],
                           clip_indices=[n['data']['m_ClipID'] for bt in state['m_BlendTreeConstantArray'] for n in bt['data']['m_NodeArray']]))
    byte_checks = {}
    for record in [raw['controller'], *raw['clips']]:
        byte_checks[str(record['path_id'])] = hashlib.sha256(base64.b64decode(record['bytes_base64'])).hexdigest() == record['bytes_sha256']
    checks = dict(
        root_identity=raw['root']['path_id'] == 185704,
        controller_identity=raw['controller']['path_id'] == 1908,
        serialized_bytes_hashes=all(byte_checks.values()),
        clip_order=[c['path_id'] for c in clips] == [1468, 1467, 1466],
        states=[s['name'] for s in states] == ['Spawn', 'Idle', 'Attack1'],
        default_spawn=machine['m_DefaultState'] == 0,
        destinations=[s['transitions'][0]['m_DestinationState'] for s in states] == [1, 2, 1],
        exit_time_only=all(len(s['transitions']) == 1 and not s['transitions'][0]['m_ConditionConstantArray'] and s['transitions'][0]['m_HasExitTime'] and s['transitions'][0]['m_ExitTime'] == 1 and s['transitions'][0]['m_TransitionDuration'] == 0 for s in states),
        no_parameters=controller['m_Controller']['m_Values']['data']['m_ValueArray'] == [],
        no_any_state=machine['m_AnyStateTransitionConstantArray'] == [],
        no_behaviours=controller['m_StateMachineBehaviours'] == [],
        no_events=all(c['events'] == [] for c in clips),
        root_position_all_clips=all(c['bindings'][0]['binding']['path'] == 0 and c['bindings'][0]['binding']['typeID'] == 4 and c['bindings'][0]['binding']['attribute'] == 1 for c in clips),
        all_targets_resolve=all(len(b['paths']) == 1 and len(b['targets']) == 1 for c in clips for b in c['bindings']),
        no_dense_curves=all(c['dense_curve_count'] == 0 for c in clips),
        no_gameobject_binding=all(b['binding']['typeID'] != 1 for c in clips for b in c['bindings']),
        enabled_hash=zlib.crc32(b'm_Enabled') == 3305885265,
    )
    toolchain = RAW / 'toolchain/AnimationClip.cs'
    return dict(status='PROVISIONAL_STATIC_NOT_PLAYBACK', source=dict(path=str(SOURCE), hash_bytes='gzip-decompressed', sha256=hashlib.sha256(source_bytes).hexdigest(), inputs_sha256=raw['inputs_sha256']),
                format_reference=dict(repository='Perfare/AssetStudio', commit='d158e864b556b5970709c2a52e47944d53aa98a2', path=str(toolchain), sha256=hashlib.sha256(toolchain.read_bytes()).hexdigest(), license=str(RAW / 'toolchain/LICENSE')),
                default_state=machine['m_DefaultState'], states=states, clips=clips,
                duplicate_paths={str(k): [n['path'] for n in v] for k, v in paths.items() if len(v) > 1}, checks=checks)


if __name__ == '__main__':
    result = build()
    assert all(result['checks'].values()), result['checks']
    with gzip.GzipFile(filename=str(RAW / 'decoded-clips.json.gz'), mode='wb', mtime=0) as f:
        f.write(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False).encode())
    print(f"{len(result['clips'])} clips; {len(result['checks'])} checks passed")
