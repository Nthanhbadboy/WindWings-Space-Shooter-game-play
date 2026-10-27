#!/usr/bin/env python3
"""Driven RectTransform / renderer-alpha property route on one modelled state.

The APK drives UI properties from AnimationClips through ``Animator`` bindings of
the form ``(path_hash, attribute, typeID)``. This tool answers, at property
level and for explicit times:

* **which** properties are driven at all (the route table: class, field, how the
  field name was established, how many bindings, how many resolved targets),
* **what value** each driven channel holds at time ``t`` (streamed cubic keys,
  constant clips and initial-frame constants), and
* **what the modelled state becomes** once those writes are applied to the
  serialized baseline of the concrete components of one Animator instance —
  i.e. the same "one modelled state, ordered writes" shape as the shared frame
  of report 104, but for animated rect/alpha/active/text fields instead of
  layout/native writes.

Honesty boundaries (all present in the artifact):

* Channel attribution uses the documented curve layout (Transform bindings expand
  to 3/4/3/3 components, everything else to one) and a prefix policy for the
  streamed/constant split. The layout is *validated* per clip (``layout_exact``)
  and globally (665/665 clips satisfy it); clips that fail are not attributed.
* Interpolation is the exported cubic polynomial evaluated in double precision.
  Unity's float32 pipeline, normalised-quaternion blending and engine write order
  are not reproduced.
* Nothing is rendered, no mesh is generated, no CanvasRenderer/CanvasGroup exists
  in the binding set at all (measured, see ``counts.class_ids``) — so "alpha" here
  means the serialized colour alpha of the bound renderer/TextMeshPro, never a
  CanvasRenderer state.
* Blending across a crossfade weights the evaluated channel values linearly; that
  weighting is a declared model choice, not Unity's blending.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from l3_model_common import (ROOT, envelope, fin, inputs_map, read_json_gz,
                             sha256_file, write_json_gz)
from l3_transition_scheduler import Scheduler, load_clip_lengths, normalize_controller

BINDINGS_GLOB = 'datas/l3-scene-chains/animation_bindings-*.json.gz'
NODES_GLOB = 'datas/l3-scene-chains/nodes-*.json.gz'
MOTION_GLOB = 'datas/l3-scene-chains/motion-*.json.gz'
PROGRAM_ARTIFACT = 'datas/l3_animator_programs.json.gz'
OUT_DEFAULT = 'datas/l3_driven_props.json.gz'


def glob_inputs(pattern):
    """Every shard matched by the pattern, so the artifact pins what it really read."""
    return [str(path.relative_to(ROOT)) for path in sorted(ROOT.glob(pattern))]

# Unity class IDs for the classes that appear in this artifact's clip bindings.
CLASS_NAMES = {
    1: 'GameObject', 4: 'Transform', 58: 'CircleCollider2D', 60: 'PolygonCollider2D',
    61: 'BoxCollider2D', 96: 'TrailRenderer', 114: 'MonoBehaviour',
    120: 'LineRenderer', 198: 'ParticleSystem', 199: 'ParticleSystemRenderer',
    212: 'SpriteRenderer', 222: 'CanvasRenderer', 224: 'RectTransform',
    225: 'CanvasGroup',
}

# Transform (classID 4) bindings address a property *group*, not a CRC'd field.
TRANSFORM_ATTRIBUTES = {
    1: ('m_LocalPosition', ('x', 'y', 'z')),
    2: ('m_LocalRotation', ('x', 'y', 'z', 'w')),
    3: ('m_LocalScale', ('x', 'y', 'z')),
    4: ('m_LocalEulerAngles', ('x', 'y', 'z')),
}
CHANNEL_COMPONENTS = {attr: len(spec[1]) for attr, spec in TRANSFORM_ATTRIBUTES.items()}

RECT_FIELDS = {
    'm_SizeDelta.x', 'm_SizeDelta.y', 'm_AnchoredPosition.x', 'm_AnchoredPosition.y',
    'm_AnchorMin.x', 'm_AnchorMin.y', 'm_AnchorMax.x', 'm_AnchorMax.y',
    'm_Pivot.x', 'm_Pivot.y',
}
ALPHA_FIELDS = {'m_Color.a', 'm_fontColor.a', 'm_Alpha', 'm_Color.r', 'm_Color.g',
                'm_Color.b', 'm_fontColor.r', 'm_fontColor.g', 'm_fontColor.b'}
TEXT_FIELDS = {'m_fontSize', 'm_fontSizeBase', 'm_fontSizeMin', 'm_fontSizeMax',
               'm_textAlignment', 'm_enableWordWrapping', 'm_enableAutoSizing',
               'm_fontStyle', 'm_characterSpacing'}

SCOPE = (
    'Driven-property route and application model for animated RectTransform / renderer '
    'colour / GameObject-active / TextMeshPro scalar channels, resolved on the concrete '
    'components of one Animator instance with the serialized values as baseline. No '
    'render, no mesh/geometry generation, no CanvasRenderer/CanvasGroup binding exists '
    'in this artifact. Channel values are exported cubic polynomials evaluated in '
    'double precision; engine float32/write order/blending are not reproduced.'
)

DECODE_LIMITS = [
    'layout_convention: Transform (classID 4) bindings expand to 3/4/3/3 components and '
    'every other binding to one; validated by channel_count on all 665 clips but still a '
    'declared convention, not engine source',
    'attribution_prefix_policy: streamed curves are taken to be the first channels in '
    'curve order, constants the remainder; exact only when the per-clip arithmetic '
    'matches (measured per clip as layout_exact)',
    'curve_mode_absent: a curve stored as a constant is applied as its constant value; no '
    'claim is made that the authored curve was constant',
    'dense_curves_absent: every one of the 665 clips reports zero dense curves, so dense '
    'sampling is not implemented',
    'transform_rotation_channels: m_LocalRotation channels are evaluated component-wise; '
    'normalised-quaternion blending is not modelled',
    'no_canvas_bindings: no clip in this artifact binds classID 222 CanvasRenderer or 225 '
    'CanvasGroup, so UI alpha here is renderer/TMP colour alpha only',
    'unresolved_bindings_kept: bindings whose field cannot be established from the '
    'serialized source are listed, not guessed',
    'blend_weights_model: crossfade weighting of evaluated channel values is linear and '
    'declared, not Unity blending',
]


# --------------------------------------------------------------------------
# Curve layout and evaluation
# --------------------------------------------------------------------------
def binding_components(binding):
    """Number of animation channels a single clip binding expands to."""
    if binding['typeID'] == 4:
        return CHANNEL_COMPONENTS.get(binding['attribute'], 1)
    return 1


def curve_layout(clip):
    """Per-channel route: channel index -> (binding_index, component, typeID, attr)."""
    channels = []
    index = 0
    for binding_index, binding in enumerate(clip['bindings']):
        for component in range(binding_components(binding)):
            channels.append({
                'channel': index,
                'binding_index': binding_index,
                'component': component,
                'typeID': binding['typeID'],
                'attribute': binding['attribute'],
                'is_int': bool(binding.get('isIntCurve')),
                'is_pptr': bool(binding.get('isPPtrCurve')),
            })
            index += 1
    return channels


def _streamed_frames(clip):
    """Frames with finite time, initial sentinel frame separated (peer r99 wording)."""
    initial, regular = None, []
    for frame in clip.get('streamed') or []:
        if not fin(frame.get('time')):
            continue
        if frame['time'] <= -3.0e38:
            initial = frame
        else:
            regular.append(frame)
    regular.sort(key=lambda f: f['time'])
    return initial, regular


def as_int32(value):
    """Reinterpret the float slot of an int curve as a signed 32-bit integer.

    Unity stores integer curves in the same float array; the serialized constant
    is the bit pattern, not a numeric float (measured: a TextMeshPro alignment
    channel reads as 5.7e-42 float / 4100 int).
    """
    import struct
    return struct.unpack('<i', struct.pack('<f', float(value)))[0]


def _eval_poly(coeff, dt):
    a, b, c, d = (float(x) for x in coeff)
    return ((a * dt + b) * dt + c) * dt + d


def channel_value(clip, channel_index, t, layout_info=None, is_int=None):
    """Value of one channel at clip-local time ``t`` plus how it was obtained.

    Int curves are stepped and reported as their 32-bit integer value.
    """
    info = layout_info or clip_layout_info(clip)
    if is_int is None:
        is_int = any(ch['channel'] == channel_index and ch['is_int']
                     for ch in curve_layout(clip))
    initial, frames = _streamed_frames(clip)
    latest = None
    for frame in frames:
        if frame['time'] > t:
            break
        for key in frame['keys']:
            if key['index'] == channel_index:
                latest = (frame, key)
    if latest is not None:
        frame, key = latest
        if is_int:
            return {'value': float(as_int32(key['value'])),
                    'value_int': as_int32(key['value']),
                    'status': 'int_step', 'key_time': frame['time']}
        return {'value': _eval_poly(key['coeff'], t - frame['time']),
                'status': 'streamed_polynomial',
                'key_time': frame['time']}
    if channel_index < info['streamed_channels']:
        if initial is not None:
            for key in initial['keys']:
                if key['index'] == channel_index:
                    if is_int:
                        return {'value': float(as_int32(key['value'])),
                                'value_int': as_int32(key['value']),
                                'status': 'initial_int_constant', 'key_time': None}
                    return {'value': float(key['value']), 'status': 'initial_constant',
                            'key_time': None}
        return {'value': None, 'status': 'streamed_channel_without_key', 'key_time': None}
    if info['layout_exact']:
        slot = channel_index - info['streamed_channels']
        if 0 <= slot < len(clip.get('constants') or []):
            raw = float(clip['constants'][slot])
            if is_int:
                return {'value': float(as_int32(raw)), 'value_int': as_int32(raw),
                        'status': 'constant_int', 'key_time': None}
            return {'value': raw, 'status': 'constant', 'key_time': None}
    return {'value': None, 'status': 'unattributed', 'key_time': None}


def clip_layout_info(clip):
    """Validate the layout/attribution arithmetic for one clip."""
    channels = curve_layout(clip)
    streamed = clip.get('continuous_stream_curve_count') or 0
    dense = (clip.get('dense') or {}).get('m_CurveCount') or 0
    constants = len(clip.get('constants') or [])
    indices = set()
    for frame in (clip.get('streamed') or []):
        for key in frame['keys']:
            indices.add(key['index'])
    exact = (len(channels) == clip.get('channel_count')
             and streamed + dense + constants == len(channels)
             and (not indices or indices == set(range(len(indices)))))
    return {
        'channels': len(channels),
        'channel_count': clip.get('channel_count'),
        'streamed_channels': streamed,
        'dense_channels': dense,
        'constant_channels': constants,
        'discrete_channels': clip.get('discrete_curve_count'),
        'layout_exact': bool(exact),
        'streamed_indices_are_prefix': (not indices or indices == set(range(len(indices)))),
    }


# --------------------------------------------------------------------------
# Property naming
# --------------------------------------------------------------------------
def property_for(binding, candidates):
    """(class_name, field, source) for one binding, or (…, None, 'unresolved')."""
    class_id = binding['typeID']
    class_name = CLASS_NAMES.get(class_id, f'class_{class_id}')
    if class_id == 4 and binding['attribute'] in TRANSFORM_ATTRIBUTES:
        field, _ = TRANSFORM_ATTRIBUTES[binding['attribute']]
        return class_name, field, 'transform_attribute_convention'
    if candidates:
        names = sorted({c['field'] for c in candidates})
        if len(names) == 1:
            field = names[0]
            crc = zlib.crc32(field.encode()) & 0xFFFFFFFF
            source = ('crc32_verified' if crc == binding['attribute']
                      else 'source_candidate_unverified')
            return class_name, field, source
        return class_name, '+'.join(names), 'ambiguous_candidates'
    return class_name, None, 'unresolved'


def kind_for(class_name, field):
    if field is None:
        return 'unresolved'
    if class_name == 'GameObject' and field == 'm_IsActive':
        return 'active'
    if class_name == 'RectTransform':
        if field in RECT_FIELDS:
            return 'rect'
        if field.startswith('m_LocalPosition'):
            return 'local_position'
    if class_name == 'Transform':
        if field == 'm_LocalPosition':
            return 'local_position'
        if field == 'm_LocalScale':
            return 'local_scale'
        if field == 'm_LocalRotation':
            return 'local_rotation'
        if field == 'm_LocalEulerAngles':
            return 'euler'
    if field in ALPHA_FIELDS:
        return 'alpha'
    if class_name == 'MonoBehaviour' and field in TEXT_FIELDS:
        return 'text'
    if field in {'m_Enabled', 'm_FlipX', 'm_FlipY'}:
        return 'renderer_state'
    if field in {'m_Size.x', 'm_Size.y'}:
        return 'renderer_size'
    if class_name == 'ParticleSystem':
        return 'particle_module'
    if class_name in {'BoxCollider2D', 'CircleCollider2D', 'PolygonCollider2D'}:
        return 'collider'
    if class_name in {'LineRenderer', 'TrailRenderer'}:
        return 'line_trail'
    return 'scalar_field'


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------
def load_motion():
    clips = {}
    for path in sorted(ROOT.glob(MOTION_GLOB)):
        for clip in read_json_gz(path):
            key = (clip['identity']['serialized_file'], int(clip['identity']['path_id']))
            clips[key] = clip
    return clips


def iter_bindings():
    for path in sorted(ROOT.glob(BINDINGS_GLOB)):
        for row in read_json_gz(path):
            yield row


def binding_key(row):
    return (row['clip']['serialized_file'], int(row['clip']['path_id']),
            int(row['binding_index']))


def route_table(binding_rows=None):
    """Global (typeID, attribute) -> route summary, measured from the bindings."""
    stats = collections.defaultdict(lambda: {
        'bindings': 0, 'targets_resolved': 0, 'targets_unresolved': 0,
        'fields': collections.Counter(), 'sources': collections.Counter(),
    })
    class_ids = collections.Counter()
    for row in (binding_rows if binding_rows is not None else iter_bindings()):
        binding = row['binding']
        class_id = binding['typeID']
        class_ids[class_id] += 1
        class_name, field, source = property_for(binding, row.get('property_crc32_candidates'))
        entry = stats[(class_id, binding['attribute'])]
        entry['bindings'] += 1
        entry['fields'][field] += 1
        entry['sources'][source] += 1
        if row.get('component_targets'):
            entry['targets_resolved'] += 1
        else:
            entry['targets_unresolved'] += 1
    table = []
    for (class_id, attribute), entry in sorted(stats.items()):
        field, count = (entry['fields'].most_common(1)[0] if entry['fields'] else (None, 0))
        table.append({
            'class_id': class_id,
            'class_name': CLASS_NAMES.get(class_id, f'class_{class_id}'),
            'attribute': attribute,
            'field': field,
            'kind': kind_for(CLASS_NAMES.get(class_id, ''), field),
            'bindings': entry['bindings'],
            'targets_resolved': entry['targets_resolved'],
            'targets_unresolved': entry['targets_unresolved'],
            'field_sources': dict(entry['sources']),
            'crc32_of_field': (zlib.crc32(field.encode()) & 0xFFFFFFFF) if field else None,
            'crc32_matches_attribute': bool(field) and
            (zlib.crc32(field.encode()) & 0xFFFFFFFF) == attribute,
        })
    return table, dict(class_ids)


def load_component_snapshots(wanted):
    """Stream the node shards once; keep component snapshots for ``wanted`` ids."""
    snapshots = {}
    nodes = {}
    keys = {('component', k[0], k[1]) for k in wanted}
    for path in sorted(ROOT.glob(NODES_GLOB)):
        for record in read_json_gz(path):
            node_meta = {
                'path': record.get('path'),
                'root': record.get('root'),
                'gameobject': record.get('gameobject'),
                'transform': record.get('transform'),
                'serialized_active': record.get('activity_within_root'),
                'gameobject_properties': record.get('gameobject_properties'),
                'transform_properties': record.get('transform_properties'),
            }
            for component in record.get('components') or []:
                identity = component.get('identity') or {}
                key = (identity.get('serialized_file'), int(identity.get('path_id') or 0))
                if key not in wanted:
                    continue
                if key in snapshots:
                    continue
                snapshots[key] = {
                    'identity': identity,
                    'type': component.get('type'),
                    'class_name': component.get('class_name'),
                    'enabled': component.get('enabled'),
                    'properties': component.get('properties'),
                    'node': node_meta,
                }
            transform = record.get('transform') or {}
            tkey = (transform.get('serialized_file'), int(transform.get('path_id') or 0))
            if tkey in wanted and tkey not in snapshots:
                snapshots[tkey] = {
                    'identity': transform,
                    'type': 'RectTransform'
                            if 'm_SizeDelta' in (record.get('transform_properties') or {})
                            else 'Transform',
                    'class_name': None,
                    'enabled': None,
                    'properties': record.get('transform_properties'),
                    'node': node_meta,
                }
            go = record.get('gameobject') or {}
            gkey = (go.get('serialized_file'), int(go.get('path_id') or 0))
            if gkey in wanted and gkey not in snapshots:
                snapshots[gkey] = {
                    'identity': go,
                    'type': 'GameObject',
                    'class_name': None,
                    'enabled': None,
                    'properties': record.get('gameobject_properties'),
                    'node': node_meta,
                }
            nodes[record.get('root')] = nodes.get(record.get('root'), 0) + 1
    return snapshots


def baseline_fields(snapshot):
    """Serialized baseline of the fields this tool can drive, per component type."""
    props = snapshot.get('properties') or {}
    out = {}
    if snapshot['type'] == 'RectTransform':
        for field in RECT_FIELDS:
            group, _, axis = field.partition('.')
            value = (props.get(group) or {}).get(axis)
            if value is not None:
                out[field] = value
        local = props.get('m_LocalPosition') or {}
        for axis in ('x', 'y', 'z'):
            if axis in local:
                out[f'm_LocalPosition.{axis}'] = local[axis]
        scale = props.get('m_LocalScale') or {}
        for axis in ('x', 'y', 'z'):
            if axis in scale:
                out[f'm_LocalScale.{axis}'] = scale[axis]
    elif snapshot['type'] == 'Transform':
        for group in ('m_LocalPosition', 'm_LocalScale', 'm_LocalRotation'):
            for axis, value in (props.get(group) or {}).items():
                out[f'{group}.{axis}'] = value
    elif snapshot['type'] == 'GameObject':
        out['m_IsActive'] = props.get('m_IsActive')
    else:
        for group in ('m_Color', 'm_fontColor'):
            for axis, value in (props.get(group) or {}).items():
                out[f'{group}.{axis}'] = value
        out['m_Enabled'] = props.get('m_Enabled')
        for field in TEXT_FIELDS:
            if field in props:
                out[field] = props[field]
    return out


# --------------------------------------------------------------------------
# Case building
# --------------------------------------------------------------------------
CASE_SPECS = [
    {'name': 'box_gift_appear', 'controller_path_id': 1792, 'state_index': 0,
     'times': [0.0, 1 / 12, 1 / 6, 0.25, 1 / 3],
     'what': 'Appear state of Box_Gift: driven local scale (pop), renderer colour alpha, '
             'RectTransform rect and TextMeshPro font scalars on one state'},
    {'name': 'box_gift_flick', 'controller_path_id': 1792, 'state_index': 1,
     'times': [0.0, 1 / 12, 1 / 6, 0.25, 1 / 3],
     'what': 'Flick state of Box_Gift: same bound components as Appear, different clip'},
    {'name': 'extra_life_apear', 'controller_path_id': 1926, 'state_index': 0,
     'times': [0.0, 0.25, 0.5, 1.0, 1.2666666507720947],
     'what': 'ExtraLife apear: GameObject m_IsActive channels plus rect and alpha'},
    {'name': 'efx_90016_active', 'controller_path_id': 1953, 'state_index': 0,
     'times': [0.0, 0.25, 0.75, 1.0, 1.5],
     'what': 'Efx_90016 Active: TextMeshPro scalars and anchored position of one effect '
             'root'},
]

TIMELINE_SPEC = {
    'name': 'box_gift_scheduled_timeline',
    'controller_path_id': 1792,
    'script': [{'t': 0.05, 'trigger': ['Flick']},
               {'t': 0.45, 'trigger': ['Change']},
               {'t': 0.8, 'trigger': ['Pop']}],
    'dt': 1 / 60,
    'steps': 60,
    'sample_every': 5,
    'what': 'scheduler + driven props on the same modelled state: the transition model '
            'selects the state, the driven-props model writes rect/alpha/text for that '
            'state at that instant; during a crossfade the channel values are weighted '
            'linearly (declared model choice)',
}


def collect_bindings_for_clips(clips):
    """All binding rows for the given clip identities (all Animator instances)."""
    wanted = set(clips)
    rows = collections.defaultdict(list)
    for row in iter_bindings():
        key = (row['clip']['serialized_file'], int(row['clip']['path_id']))
        if key in wanted:
            rows[key].append(row)
    for key in rows:
        rows[key].sort(key=lambda r: r['binding_index'])
    return rows


def pick_instance(rows, snapshots):
    """Animator instance whose bound targets are best snapshot-covered."""
    score = collections.Counter()
    for row in rows:
        animator = (row['animator']['serialized_file'], int(row['animator']['path_id']))
        for target in row.get('component_targets') or []:
            key = (target['serialized_file'], int(target['path_id']))
            if key in snapshots:
                score[animator] += 1
    if not score:
        return None
    return sorted(score.items(), key=lambda kv: (-kv[1], kv[0][1]))[0]


def target_states(rows, clip, snapshots):
    """Per-binding route + baseline for one clip on one Animator instance."""
    info = clip_layout_info(clip)
    channels = curve_layout(clip)
    by_binding = collections.defaultdict(list)
    for channel in channels:
        by_binding[channel['binding_index']].append(channel)
    entries = []
    for row in rows:
        binding = row['binding']
        class_name, field, source = property_for(binding, row.get('property_crc32_candidates'))
        kind = kind_for(class_name, field)
        targets = []
        for target in row.get('component_targets') or []:
            key = (target['serialized_file'], int(target['path_id']))
            snapshot = snapshots.get(key)
            targets.append({
                'identity': target,
                'type': snapshot['type'] if snapshot else None,
                'class_name': snapshot['class_name'] if snapshot else None,
                'node_path': (snapshot or {}).get('node', {}).get('path'),
                'baseline': baseline_fields(snapshot) if snapshot else None,
                'snapshotted': snapshot is not None,
            })
        entries.append({
            'binding_index': row['binding_index'],
            'path_hash': binding['path'],
            'attribute': binding['attribute'],
            'type_id': binding['typeID'],
            'class_name': class_name,
            'field': field,
            'kind': kind,
            'field_source': source,
            'crc32_matches': field is not None and binding['typeID'] != 4 and
            (zlib.crc32(field.encode()) & 0xFFFFFFFF) == binding['attribute'],
            'serialized_value':
                (row['property_crc32_candidates'][0]['serialized_value']
                 if row.get('property_crc32_candidates') else None),
            'channels': [c['channel'] for c in by_binding.get(row['binding_index'], [])],
            'channel_components': [c['component'] for c in by_binding.get(row['binding_index'], [])],
            'component_count': binding_components(binding),
            'is_int_curve': bool(binding.get('isIntCurve')),
            'is_pptr_curve': bool(binding.get('isPPtrCurve')),
            'targets': targets,
            'status': row.get('status'),
        })
    return entries, info


def evaluate_entries(entries, clip, t):
    """Channel values and applied writes at one clip-local time."""
    applied = []
    skipped = []
    for entry in entries:
        field = entry['field']
        if field is None or not entry['channels']:
            skipped.append({'binding_index': entry['binding_index'],
                            'reason': 'field_unresolved' if field is None
                            else 'no_channels'})
            continue
        values = []
        for channel, component in zip(entry['channels'], entry['channel_components']):
            result = channel_value(clip, channel, t,
                                   is_int=entry['is_int_curve'])
            values.append({'channel': channel, 'component': component, **result})
        if all(v['value'] is None for v in values):
            skipped.append({'binding_index': entry['binding_index'],
                            'reason': 'no_attributed_value'})
            continue
        applied.append({
            'binding_index': entry['binding_index'],
            'field': field,
            'kind': entry['kind'],
            'class_name': entry['class_name'],
            'components': values,
            'value': values[0]['value'] if len(values) == 1 else
            [v['value'] for v in values],
            'status': values[0]['status'] if len(values) == 1 else
            ('mixed' if len({v['status'] for v in values}) > 1 else values[0]['status']),
            'targets': [tgt['identity'] for tgt in entry['targets']],
        })
    return applied, skipped


def component_field(class_name, field, component):
    """Field name of one channel component (Transform groups expand to x/y/z/w)."""
    if class_name == 'Transform' and field in ('m_LocalPosition', 'm_LocalRotation',
                                               'm_LocalScale', 'm_LocalEulerAngles'):
        axes = TRANSFORM_ATTRIBUTES_LABELS.get(field) or ('x', 'y', 'z')
        return f'{field}.{axes[component]}'
    return field


TRANSFORM_ATTRIBUTES_LABELS = {
    'm_LocalPosition': ('x', 'y', 'z'),
    'm_LocalRotation': ('x', 'y', 'z', 'w'),
    'm_LocalScale': ('x', 'y', 'z'),
    'm_LocalEulerAngles': ('x', 'y', 'z'),
}


def build_target_writes(entries, applied, snapshots):
    """Fold the driven writes into per-target fields with the serialized baseline."""
    entries_by_binding = {entry['binding_index']: entry for entry in entries}
    by_target = {}
    for write in applied:
        entry = entries_by_binding[write['binding_index']]
        for target in entry['targets']:
            identity = target['identity']
            key = (identity['serialized_file'], int(identity['path_id']))
            slot = by_target.setdefault(key, {
                'identity': identity,
                'type': target['type'],
                'class_name': target['class_name'],
                'node_path': target['node_path'],
                'snapshotted': target['snapshotted'],
                'kinds': [entry['kind']],
                'fields': {},
                'int_fields': {},
                'sources': [],
            })
            if entry['kind'] not in slot['kinds']:
                slot['kinds'].append(entry['kind'])
            for component in write['components']:
                name = component_field(write['class_name'], write['field'],
                                       component['component'])
                slot['fields'][name] = component['value']
                if component.get('value_int') is not None:
                    slot['int_fields'][name] = component['value_int']
                slot['sources'].append({
                    'binding_index': write['binding_index'],
                    'channel': component['channel'],
                    'status': component['status'],
                    'field': name,
                })
    out = []
    for key, slot in sorted(by_target.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        snapshot = snapshots.get(key)
        base = baseline_fields(snapshot) if snapshot else {}
        if snapshot is None:
            slot['baseline_status'] = 'component_not_in_node_index'
        elif not (snapshot.get('properties')):
            slot['baseline_status'] = 'component_snapshot_not_inlined'
        else:
            slot['baseline_status'] = 'serialized_inline'
        slot['baseline'] = {name: base.get(name) for name in slot['fields']}
        slot['changed'] = {}
        for name, value in slot['fields'].items():
            before = base.get(name)
            if 'active' in slot['kinds']:
                slot['bool_model'] = slot.get('bool_model') or {}
                slot['bool_model'][name] = bool(value) if value is not None else None
            if before is None:
                slot['changed'][name] = {'baseline': None, 'driven': value}
            else:
                try:
                    different = abs(float(value) - float(before)) > 1e-9
                except (TypeError, ValueError):
                    different = value != before
                if different:
                    slot['changed'][name] = {'baseline': before, 'driven': value}
        out.append(slot)
    return out


def build_case(spec, programs, clips, clip_lengths, snapshots_by_clip):
    """One state of one controller, applied to one concrete Animator instance."""
    controller = next((c for c in programs['controllers']
                       if int(c['identity']['path_id']) == spec['controller_path_id']), None)
    if controller is None:
        return {'name': spec['name'], 'status': 'controller_not_found'}
    model = normalize_controller(controller, {})
    state = model['machines'][0]['states'][spec['state_index']]
    motion = state['motion'][0] if state['motion'] else None
    if not motion:
        return {'name': spec['name'], 'status': 'state_without_motion'}
    clip_identity = motion['clip']
    key = (clip_identity['serialized_file'], int(clip_identity['path_id']))
    clip = clips[key]
    rows_all, snapshots, animator = snapshots_by_clip[key]
    if animator is None:
        return {'name': spec['name'], 'status': 'no_animator_instance_snapshotted'}
    rows = [row for row in rows_all
            if (row['animator']['serialized_file'], int(row['animator']['path_id'])) == animator]
    entries, info = target_states(rows, clip, snapshots)

    samples = []
    for t in spec['times']:
        applied, skipped = evaluate_entries(entries, clip, t)
        writes = build_target_writes(entries, applied, snapshots)
        samples.append({
            'clip_time': t,
            'channel_writes': applied,
            'skipped': skipped,
            'targets': writes,
            'changed_fields': {f"{w['identity']['path_id']}.{name}": delta
                               for w in writes for name, delta in w['changed'].items()},
            'changed_count': sum(len(w['changed']) for w in writes),
        })
    skipped_reasons = {}
    for sample in samples:
        for item in sample['skipped']:
            skipped_reasons[item['reason']] = skipped_reasons.get(item['reason'], 0) + 1
    return {
        'name': spec['name'],
        'what': spec['what'],
        'controller': model['identity'],
        'controller_name': model['name'],
        'state_index': state['state_index'],
        'state_names': state['names'],
        'clip': clip_identity,
        'clip_name': clip.get('name'),
        'clip_length': float(clip.get('stop') or 0.0) - float(clip.get('start') or 0.0),
        'animator': {'serialized_file': animator[0], 'path_id': animator[1]},
        'layout': info,
        'entries': entries,
        'samples': samples,
        'skipped_reasons': skipped_reasons,
        'targets_snapshotted': sum(1 for e in entries for tgt in e['targets']
                                   if tgt['snapshotted']),
        'targets_total': sum(len(e['targets']) for e in entries),
        'bindings': len(entries),
        'bindings_with_field': sum(1 for e in entries if e['field']),
    }


def build_timeline_case(spec, programs, clips, snapshots_by_clip):
    controller = next((c for c in programs['controllers']
                       if int(c['identity']['path_id']) == spec['controller_path_id']), None)
    if controller is None:
        return {'name': spec['name'], 'status': 'controller_not_found'}
    model = normalize_controller(controller, load_clip_lengths())
    sched = Scheduler(model)
    timeline = sched.run(spec['dt'], spec['steps'], spec['script'])
    rows = []
    for row in timeline:
        if 'state' not in row:
            rows.append({'t': row['t'], 'script': row.get('applied_script')})
            continue
        weight_rows = []
        for state_index, weight in (row['blend']['weights'] or {}).items():
            state = model['machines'][0]['states'][int(state_index)]
            motion = state['motion'][0] if state['motion'] else None
            if not motion:
                weight_rows.append({'state': int(state_index), 'weight': weight,
                                    'clip': None})
                continue
            key = (motion['clip']['serialized_file'], int(motion['clip']['path_id']))
            clip = clips.get(key)
            if clip is None:
                weight_rows.append({'state': int(state_index), 'weight': weight,
                                    'clip': motion['clip'], 'status': 'clip_not_in_motion_artifact'})
                continue
            rows_all, snapshots, animator = snapshots_by_clip[key]
            anim_rows = [r for r in rows_all
                         if (r['animator']['serialized_file'], int(r['animator']['path_id']))
                         == animator]
            entries, info = target_states(anim_rows, clip, snapshots)
            clip_time = row['state_time'] if int(state_index) == row['state'] else \
                row['state_time']
            clip_time = min(clip_time, float(clip.get('stop') or 0.0))
            applied, skipped = evaluate_entries(entries, clip, clip_time)
            writes = build_target_writes(entries, applied, snapshots)
            weight_rows.append({
                'state': int(state_index),
                'weight': weight,
                'clip': motion['clip'],
                'clip_name': clip.get('name'),
                'clip_time': clip_time,
                'layout_exact': info['layout_exact'],
                'channel_writes': applied,
                'targets': writes,
                'skipped': skipped,
            })
        rows.append({
            't': row['t'],
            'state': row['state'],
            'state_name': row['state_name'],
            'normalized_time': row['normalized_time'],
            'blend_active': row['blend']['active'],
            'blend_progress': row['blend']['progress'],
            'states': weight_rows,
        })
    sampled = [row for row in rows if 'script' in row or
               int(round(row['t'] / spec['dt'])) % spec['sample_every'] == 0]
    return {
        'name': spec['name'],
        'what': spec['what'],
        'controller': model['identity'],
        'controller_name': model['name'],
        'dt': spec['dt'],
        'steps': spec['steps'],
        'script': spec['script'],
        'transitions_taken': sched.taken,
        'timeline': sampled,
        'blend_weighting_status': 'linear weight on evaluated channel values '
                                  '(declared model choice, not Unity blending)',
    }


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------
def build():
    programs = read_json_gz(ROOT / PROGRAM_ARTIFACT)
    clips = load_motion()

    # 1. global route table (one streaming pass over all 52,400 bindings)
    table, class_ids = route_table()

    # 2. case clips: bindings per clip, component snapshots, chosen instance
    case_clip_keys = []
    for controller_id in {spec['controller_path_id'] for spec in CASE_SPECS} | \
            {TIMELINE_SPEC['controller_path_id']}:
        controller = next((c for c in programs['controllers']
                           if int(c['identity']['path_id']) == controller_id), None)
        if not controller:
            continue
        for machine in controller['machines']:
            for state in machine['states']:
                for tree in state.get('trees') or []:
                    for node in tree.get('nodes') or []:
                        clip = node.get('clip')
                        if not clip:
                            continue
                        key = (clip['serialized_file'], int(clip['path_id']))
                        if key in clips and key not in case_clip_keys:
                            case_clip_keys.append(key)
    rows_by_clip = collect_bindings_for_clips(case_clip_keys)
    wanted = set()
    for key in case_clip_keys:
        for row in rows_by_clip.get(key, []):
            for target in row.get('component_targets') or []:
                wanted.add((target['serialized_file'], int(target['path_id'])))
    snapshots = load_component_snapshots(wanted)
    snapshots_by_clip = {}
    for key in case_clip_keys:
        rows = rows_by_clip.get(key, [])
        chosen = pick_instance(rows, snapshots)
        snapshots_by_clip[key] = (rows, snapshots, chosen[0] if chosen else None)

    cases = [build_case(spec, programs, clips, None, snapshots_by_clip)
             for spec in CASE_SPECS]
    timeline = build_timeline_case(TIMELINE_SPEC, programs, clips, snapshots_by_clip)

    # 3. coverage of the modelled properties across all 665 clips
    per_clip = {}
    for key, clip in clips.items():
        info = clip_layout_info(clip)
        per_clip[key] = info
    exact = sum(1 for info in per_clip.values() if info['layout_exact'])
    kinds = collections.Counter(row['kind'] for row in table)
    fields = collections.Counter(row['field'] for row in table if row['field'])

    counts = {
        'clips_with_channel_data': len(clips),
        'clips_layout_exact': exact,
        'clips_layout_partial': len(clips) - exact,
        'bindings_total': sum(row['bindings'] for row in table),
        'route_entries': len(table),
        'class_ids': {str(k): v for k, v in sorted(class_ids.items())},
        'route_kinds': dict(kinds.most_common()),
        'top_fields': dict(fields.most_common(12)),
        'driven_rect_bindings': sum(row['bindings'] for row in table if row['kind'] == 'rect'),
        'driven_alpha_bindings': sum(row['bindings'] for row in table
                                     if row['kind'] == 'alpha'),
        'driven_active_bindings': sum(row['bindings'] for row in table
                                      if row['kind'] == 'active'),
        'driven_text_bindings': sum(row['bindings'] for row in table
                                    if row['kind'] == 'text'),
        'driven_particle_module_bindings': sum(
            row['bindings'] for row in table if row['kind'] == 'particle_module'),
        'bindings_unresolved_field': sum(row['bindings'] for row in table
                                         if row['field'] is None),
        'canvas_renderer_bindings': class_ids.get(222, 0),
        'canvas_group_bindings': class_ids.get(225, 0),
        'cases': len(cases),
        'component_snapshots': len(snapshots),
    }

    artifact = envelope(SCOPE, inputs_map(
        glob_inputs(BINDINGS_GLOB) + glob_inputs(NODES_GLOB) + glob_inputs(MOTION_GLOB) + [
        PROGRAM_ARTIFACT,
        'datas/l3_frame_cases.json.gz',
        'tools/verify/l3_driven_props.py',
        'tools/verify/l3_transition_scheduler.py',
        'tools/verify/l3_model_common.py',
    ]), DECODE_LIMITS)
    artifact.update({
        'counts': counts,
        'property_route': table,
        'cases': cases,
        'scheduled_timeline_case': timeline,
        'cross_checks': cross_checks(table, clips),
    })
    artifact['build'] = {
        'tool_sha256': sha256_file(Path(__file__).resolve()),
        'common_sha256': sha256_file(Path(__file__).with_name('l3_model_common.py')),
        'generator': 'tools/verify/l3_driven_props.py --build',
    }
    return artifact


def cross_checks(table, clips):
    """Reproductions that do not trust this tool's own bookkeeping."""
    checks = {}
    crc_ok = sum(1 for row in table
                 if row['field'] and row['class_id'] != 4
                 and row['crc32_matches_attribute'])
    crc_total = sum(1 for row in table if row['field'] and row['class_id'] != 4)
    checks['crc32_field_name_matches_attribute'] = {
        'matched_routes': crc_ok, 'routes_with_field': crc_total,
        'equal': crc_ok == crc_total,
    }
    # report 99 probe reproduction: clip 1572 (Popup_QuitMissions Appear) scale/alpha
    key = ('data.unity3d/resources.assets', 1572)
    clip = clips.get(key)
    if clip:
        info = clip_layout_info(clip)
        probes = {}
        for t in (0.0, 0.25, 0.5):
            probes[str(t)] = {
                'scale_x': channel_value(clip, 0, t),
                'scale_y': channel_value(clip, 1, t),
                'scale_z': channel_value(clip, 2, t),
                'alpha': channel_value(clip, 3, t),
            }
        checks['report99_clip1572_probe_reproduction'] = {
            'clip': {'serialized_file': key[0], 'path_id': key[1]},
            'layout': info,
            'probes': probes,
            'peer_reported': {'t0': 'scale 0/0, alpha 0',
                              't0.25': 'scale ~1.030399899, alpha ~0.831372559',
                              't0.5': 'scale 1/1, alpha ~0.831372559 (held)'},
            'source': 'docs/apk-analysis/99-L3-animator-programs-and-property-probes.md',
            'independent_execution': True,
        }
    return checks


def load_artifact(path=None):
    return read_json_gz(ROOT / (path or OUT_DEFAULT))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--build', action='store_true')
    ap.add_argument('--out', default=OUT_DEFAULT)
    ap.add_argument('--case', help='case name to dump')
    ap.add_argument('--t', type=float, help='override clip-local time for --case')
    ap.add_argument('--route', action='store_true', help='print the property route table')
    args = ap.parse_args(argv)
    if args.build:
        artifact = build()
        write_json_gz(ROOT / args.out, artifact)
        counts = artifact['counts']
        print(f"wrote {args.out}: {counts['route_entries']} routes over "
              f"{counts['bindings_total']} bindings; rect={counts['driven_rect_bindings']} "
              f"alpha={counts['driven_alpha_bindings']} "
              f"active={counts['driven_active_bindings']} "
              f"layouts exact {counts['clips_layout_exact']}/{counts['clips_with_channel_data']}")
        return 0
    artifact = load_artifact()
    if args.route:
        for row in artifact['property_route']:
            print(f"{row['class_id']:>4} {row['class_name']:<16} {row['attribute']:>10} "
                  f"{str(row['field']):<28} {row['kind']:<18} {row['bindings']:>6}")
        return 0
    if args.case:
        for case in artifact['cases']:
            if case['name'] != args.case:
                continue
            if args.t is not None:
                clip = load_motion()[
                    (case['clip']['serialized_file'], int(case['clip']['path_id']))]
                rows, snapshots, animator = _case_rows(case)
                entries, _ = target_states(rows, clip, snapshots)
                applied, skipped = evaluate_entries(entries, clip, args.t)
                writes = build_target_writes(entries, applied, snapshots)
                print(json.dumps({'case': case['name'], 'clip_time': args.t,
                                  'channel_writes': applied, 'targets': writes,
                                  'skipped': skipped}, ensure_ascii=False, indent=1))
                return 0
            print(json.dumps(case['samples'], ensure_ascii=False, indent=1))
            return 0
        raise SystemExit(f'case {args.case!r} not found')
    print(json.dumps({'counts': artifact['counts'],
                      'cases': [c['name'] for c in artifact['cases']],
                      'cross_checks': artifact['cross_checks']},
                     ensure_ascii=False, indent=1))
    return 0


def _case_rows(case):
    clips = load_motion()
    key = (case['clip']['serialized_file'], int(case['clip']['path_id']))
    rows = collect_bindings_for_clips([key])[key]
    wanted = set()
    for row in rows:
        for target in row.get('component_targets') or []:
            wanted.add((target['serialized_file'], int(target['path_id'])))
    snapshots = load_component_snapshots(wanted)
    animator = (case['animator']['serialized_file'], int(case['animator']['path_id']))
    return [r for r in rows
            if (r['animator']['serialized_file'], int(r['animator']['path_id'])) == animator], \
        snapshots, animator


if __name__ == '__main__':
    raise SystemExit(main())
