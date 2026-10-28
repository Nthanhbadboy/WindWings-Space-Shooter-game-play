#!/usr/bin/env python3
"""Evidence inventory for Animator layer blending/property interpolation (#15).

This tool separates facts recoverable from APK-derived serialized data and the IL2CPP
metadata dump from the actual Unity engine algorithms, which are not present in the input.
It does not add a blending/interpolation policy or claim native runtime behavior.
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRAPH = 'reverse-engineering/raw/typetrees/animator-controller-graphs.jsonl.gz'
NATIVE_TYPES = 'reverse-engineering/raw/typetrees/native-types.jsonl.gz'
IL2CPP_DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'
PROGRAMS = 'datas/l3_animator_programs.json.gz'
TRANSITIONS = 'datas/l3_transition_model.json.gz'
MOTION = 'datas/l3-scene-chains/motion-000.json.gz'
OUT_DEFAULT = 'datas/l3_animator_blend_native_evidence.json.gz'

LIMITS = [
    'serialized_inventory_not_runtime: controller layer fields and curve records are APK-derived '
    'serialized data, not a live Animator observation',
    'managed_dump_surface_not_engine_body: IL2CPP dump.cs provides UnityEngine API declarations '
    'and RVAs with empty method bodies; it does not provide Unity native implementation code',
    'one_layer_scope: all 308 recovered AnimatorController graphs have one serialized layer, so '
    'multi-layer blending is not exercised by these graphs',
    'enum_values_literal_only: m_LayerBlendingMode is retained as its integer value; no engine '
    'enum semantics are inferred from value 0',
    'curve_streams_not_full_runtime: motion artifact carries streamed/dense/constant data; a '
    'coefficient vector is recorded literally, not claimed to prove Unity evaluation semantics',
    'no_property_crossfade_claim: no experiment compares native Animator output during a '
    'transition against interpolated driven property values',
    'workspace_boundary: absence means unavailable in the inspected repository inputs only; '
    'it is not proof that no Unity engine source exists elsewhere',
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def read_gz(path: Path):
    with gzip.open(path, 'rt', encoding='utf-8') as stream:
        return json.load(stream)


def read_jsonl_gz(path: Path):
    with gzip.open(path, 'rt', encoding='utf-8') as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def write_gz(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False,
                         separators=(',', ':')).encode('utf-8')
    with path.open('wb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as packed:
            packed.write(payload)


def _counter(counter):
    return dict(sorted(((str(key), int(value)) for key, value in counter.items()),
                       key=lambda item: (-item[1], item[0])))


def _unwrap(item):
    if isinstance(item, dict) and isinstance(item.get('data'), dict):
        return item['data']
    return item if isinstance(item, dict) else {}


def _graph_inventory():
    rows = list(read_jsonl_gz(ROOT / GRAPH))
    layer_counts = collections.Counter()
    blend_modes = collections.Counter()
    default_weights = collections.Counter()
    sync_indices = collections.Counter()
    sync_timing = collections.Counter()
    state_machine_count = collections.Counter()
    graph_ids = collections.Counter()
    graph_names = collections.Counter()
    controllers = []
    layers_total = 0
    for row in rows:
        path_id = int(row['path_id'])
        name = row.get('tree', {}).get('m_Name')
        graph_ids[path_id] += 1
        graph_names[(path_id, name)] += 1
        controller = row.get('tree', {}).get('m_Controller') or {}
        layers = controller.get('m_LayerArray') or []
        layer_counts[len(layers)] += 1
        state_machine_count[len(controller.get('m_StateMachineArray') or [])] += 1
        layers_total += len(layers)
        layer_rows = []
        for wrapper in layers:
            layer = _unwrap(wrapper)
            blending = layer.get('(int&)m_LayerBlendingMode')
            weight = layer.get('m_DefaultWeight')
            sync = layer.get('m_StateMachineSynchronizedLayerIndex')
            sync_affects = layer.get('m_SyncedLayerAffectsTiming')
            blend_modes[blending] += 1
            default_weights[weight] += 1
            sync_indices[sync] += 1
            sync_timing[str(sync_affects)] += 1
            layer_rows.append({
                'state_machine_index': layer.get('m_StateMachineIndex'),
                'synchronized_layer_index': sync,
                'blending_mode_raw': blending,
                'default_weight': weight,
                'synced_layer_affects_timing': sync_affects,
                'ik_pass': layer.get('m_IKPass'),
            })
        controllers.append({
            'path_id': path_id,
            'name': name,
            'layer_count': len(layers),
            'state_machine_count': len(controller.get('m_StateMachineArray') or []),
            'layers': layer_rows,
        })
    return {
        'controller_records': len(rows),
        'unique_path_ids': len(graph_ids),
        'duplicate_path_id_records': sum(count - 1 for count in graph_ids.values()),
        'duplicate_path_name_records': sum(count - 1 for count in graph_names.values()),
        'serialized_layer_total': layers_total,
        'controllers_with_multiple_layers': sum(count for n, count in layer_counts.items() if n > 1),
        'controllers_with_zero_layers': layer_counts.get(0, 0),
        'layer_count_distribution': _counter(layer_counts),
        'layer_blending_mode_raw_distribution': _counter(blend_modes),
        'layer_default_weight_distribution': _counter(default_weights),
        'synchronized_layer_index_distribution': _counter(sync_indices),
        'sync_affects_timing_distribution': _counter(sync_timing),
        'state_machine_count_distribution': _counter(state_machine_count),
        'controllers': sorted(controllers, key=lambda item: (item['path_id'], item['name'] or '')),
    }


def _serialized_component_inventory():
    type_counts = collections.Counter()
    animator_controller_refs = collections.Counter()
    controller_names = {}
    controller_identity_rows = []
    animator_records = []
    clip_curve_totals = collections.Counter()
    clip_curve_nonzero = collections.Counter()
    clips = 0
    for record in read_jsonl_gz(ROOT / NATIVE_TYPES):
        kind = record.get('type')
        type_counts[kind] += 1
        if kind == 'AnimatorController':
            controller_names[int(record['path_id'])] = record.get('m_Name')
            controller_identity_rows.append({'path_id': int(record['path_id']),
                                             'name': record.get('m_Name')})
        elif kind == 'Animator':
            ref = record.get('m_Controller') or {}
            path_id = int(ref.get('m_PathID') or 0)
            animator_controller_refs[path_id] += 1
            animator_records.append({
                'path_id': int(record['path_id']),
                'controller_path_id': path_id,
                'controller_file_id': int(ref.get('m_FileID') or 0),
                'enabled': record.get('m_Enabled'),
                'update_mode': record.get('m_UpdateMode'),
                'keep_state_on_disable': record.get('m_KeepAnimatorStateOnDisable'),
            })
        elif kind == 'AnimationClip':
            clips += 1
            for field in ('m_RotationCurves__count', 'm_CompressedRotationCurves__count',
                          'm_EulerCurves__count', 'm_PositionCurves__count',
                          'm_ScaleCurves__count', 'm_FloatCurves__count',
                          'm_PPtrCurves__count'):
                count = int(record.get(field) or 0)
                clip_curve_totals[field] += count
                if count:
                    clip_curve_nonzero[field] += 1
    nonzero_refs = {key for key in animator_controller_refs if key != 0}
    return {
        'type_counts': _counter(type_counts),
        'animator_components': len(animator_records),
        'animator_null_controller_refs': animator_controller_refs.get(0, 0),
        'animator_distinct_nonzero_controller_refs': len(nonzero_refs),
        'animator_components_by_controller': _counter(animator_controller_refs),
        'animator_controller_asset_records': len(controller_names),
        'animator_controller_identity_rows': sorted(controller_identity_rows,
                                                    key=lambda item: item['path_id']),
        'controller_assets_not_referenced_by_animator': sorted(set(controller_names) - nonzero_refs),
        'animation_clip_records': clips,
        'ordinary_animation_clip_curve_totals': _counter(clip_curve_totals),
        'ordinary_animation_clip_rows_nonzero': _counter(clip_curve_nonzero),
        'animator_component_examples': sorted(animator_records,
                                               key=lambda item: item['path_id'])[:8],
    }


def _parse_dump_type(dump_text, marker):
    start = dump_text.find(marker)
    if start < 0:
        return None
    opening = dump_text.find('{', start)
    depth = 0
    for index in range(opening, len(dump_text)):
        char = dump_text[index]
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return dump_text[start:index + 1]
    return None


def _dump_api_inventory():
    dump_path = ROOT / IL2CPP_DUMP
    with gzip.open(dump_path, 'rt', encoding='utf-8', errors='replace') as stream:
        text = stream.read()
    type_markers = {
        'Animator': 'public class Animator : Behaviour // TypeDefIndex: 10666',
        'AnimationCurve': 'public class AnimationCurve : IEquatable<AnimationCurve>',
        'Keyframe': 'public struct Keyframe // TypeDefIndex: 7662',
        'AnimatorStateInfo': 'public struct AnimatorStateInfo // TypeDefIndex: 10664',
        'AnimatorTransitionInfo': 'public struct AnimatorTransitionInfo // TypeDefIndex: 10665',
        'AnimatorClipInfo': 'public struct AnimatorClipInfo // TypeDefIndex: 10663',
    }
    parsed = {name: _parse_dump_type(text, marker) for name, marker in type_markers.items()}
    methods = {}
    fields = {}
    for name, block in parsed.items():
        if not block:
            methods[name] = []
            fields[name] = []
            continue
        methods[name] = [
            {'rva': match.group(1), 'declaration': match.group(2).strip(),
             'empty_dump_body': True}
            for match in re.finditer(
                r'// RVA: (0x[0-9A-Fa-f]+)[^\n]*\n\s*((?:public|private|internal|protected) '
                r'[^\n]+?)\s*\{\s*\}', block)
        ]
        field_body = block[block.find('{') + 1:]
        fields[name] = re.findall(r'^\s*(?:private|public|internal)\s+([^;]+);',
                                  field_body, re.MULTILINE)
    searches = ('SetLayerWeight', 'CrossFade', 'CrossFadeInFixedTime',
                'GetAnimatorTransitionInfo', 'IsInTransition', 'SetFloat',
                'GetFloat', 'SetTrigger', 'GetLayerWeight',
                'GetCurrentAnimatorStateInfo', 'GetNextAnimatorStateInfo',
                'GetCurrentAnimatorClipInfo', 'GetNextAnimatorClipInfo')
    global_surface_counts = {term: len(re.findall(r'\b' + re.escape(term) + r'\b', text))
                             for term in searches}
    return {
        'dump_sha256': sha256(dump_path),
        'type_present': {name: block is not None for name, block in parsed.items()},
        'methods': methods,
        'fields': fields,
        'global_api_name_occurrence_counts': global_surface_counts,
        'all_extracted_method_bodies_are_empty_placeholders': all(
            entry['empty_dump_body'] for records in methods.values() for entry in records),
        'evidence_interpretation': ('API/type declarations plus RVA addresses only; empty bodies '
                                    'do not disclose Unity native implementation or behavior'),
    }


def _motion_inventory():
    clips = read_gz(ROOT / MOTION)
    counts = collections.Counter()
    coeff_sizes = collections.Counter()
    for clip in clips:
        counts['clips'] += 1
        counts['channel_count_sum'] += int(clip.get('channel_count') or 0)
        counts['continuous_stream_curve_count_sum'] += int(
            clip.get('continuous_stream_curve_count') or 0)
        counts['discrete_curve_count_sum'] += int(clip.get('discrete_curve_count') or 0)
        counts['dense_curve_count_sum'] += int(
            (clip.get('dense') or {}).get('m_CurveCount') or 0)
        counts['dense_frames_sum'] += int((clip.get('dense') or {}).get('m_FrameCount') or 0)
        counts['dense_sample_values_sum'] += len((clip.get('dense') or {}).get('m_SampleArray') or [])
        counts['constant_values_sum'] += len(clip.get('constants') or [])
        counts['streamed_frame_records_in_export'] += len(clip.get('streamed') or [])
        for frame in (clip.get('streamed') or []):
            for key in (frame.get('keys') or []):
                counts['streamed_key_records_in_export'] += 1
                coeff = key.get('coeff') or []
                coeff_sizes[len(coeff)] += 1
    return {
        'counts': dict(sorted(counts.items())),
        'streamed_coefficient_vector_length_distribution': _counter(coeff_sizes),
        'interpretation': ('counts exported key records/prefixes as stored; it does not decode '
                           'the Unity native curve evaluation algorithm'),
    }


def build():
    graph = _graph_inventory()
    serialized = _serialized_component_inventory()
    api = _dump_api_inventory()
    motion = _motion_inventory()
    programs = read_gz(ROOT / PROGRAMS)
    transitions = read_gz(ROOT / TRANSITIONS)
    graph_by_key = {(row['path_id'], row['name']): row for row in graph['controllers']}
    graph_by_id = {row['path_id']: row for row in graph['controllers']}
    native_by_id = {row['path_id']: row for row in
                    serialized['animator_controller_identity_rows']}
    native_graph_id_matches = set(graph_by_id) & set(native_by_id)
    native_graph_identity_mismatches = [
        {'path_id': path_id, 'graph_name': graph_by_id[path_id]['name'],
         'native_type_name': native_by_id[path_id]['name']}
        for path_id in sorted(native_graph_id_matches)
        if graph_by_id[path_id]['name'] != native_by_id[path_id]['name']]
    program_matches = []
    missing = []
    selected_layer_counts = collections.Counter()
    selected_modes = collections.Counter()
    selected_weights = collections.Counter()
    for controller in programs.get('controllers') or []:
        path_id = int(controller['identity']['path_id'])
        name = controller.get('name')
        raw = graph_by_key.get((path_id, name))
        if raw is None:
            missing.append({'path_id': path_id, 'name': name})
            continue
        selected_layer_counts[raw['layer_count']] += 1
        for layer in raw['layers']:
            selected_modes[layer['blending_mode_raw']] += 1
            selected_weights[layer['default_weight']] += 1
        program_matches.append({'path_id': path_id, 'name': name,
                                'serialized_file': controller['identity']['serialized_file'],
                                'graph_layer_count': raw['layer_count']})
    used_animator_ids = {int(row['controller_path_id']) for row in
                         serialized['animator_component_examples']
                         if row['controller_path_id']}
    # Full reference set is recovered from `animator_components_by_controller` keys.
    used_animator_ids.update(int(path_id) for path_id in
                             serialized['animator_components_by_controller'] if path_id != '0')
    graph_ids = {row['path_id'] for row in graph['controllers']}
    referenced_graph_ids = graph_ids & used_animator_ids
    return {
        'schema': 1,
        'provisional': True,
        'scope': ('Evidence inventory for #15: serialized layer-blend coverage across decoded '
                  'AnimatorControllers and the available IL2CPP Animator/curve API surface. '
                  'No layer-blending or property-interpolation algorithm is implemented.'),
        'model_notice': ('EVIDENCE INVENTORY — serialized facts and API declarations are not '
                         'Unity execution or proof of native algorithm semantics.'),
        'artifact_kind': 'bounded_native_animator_evidence_and_gap_map',
        'inputs': {rel: sha256(ROOT / rel) for rel in
                   (GRAPH, NATIVE_TYPES, IL2CPP_DUMP, PROGRAMS, TRANSITIONS, MOTION)},
        'build': {'generator': 'tools/verify/l3_animator_blend_evidence.py --build',
                  'tool_sha256': sha256(Path(__file__).resolve())},
        'decode_limits': LIMITS,
        'serialized_controller_graphs': graph,
        'serialized_component_inventory': serialized,
        'controller_identity_cross_check': {
            'raw_graph_records': len(graph_by_id),
            'native_type_records': len(native_by_id),
            'shared_path_ids': len(native_graph_id_matches),
            'graph_only_path_ids': sorted(set(graph_by_id) - set(native_by_id)),
            'native_type_only_path_ids': sorted(set(native_by_id) - set(graph_by_id)),
            'name_mismatches_on_shared_path_id': native_graph_identity_mismatches,
        },
        'transition_model_scope_check': {
            'program_controllers': len(programs.get('controllers') or []),
            'matched_to_graph_by_path_id_and_name': len(program_matches),
            'unmatched': missing,
            'layer_count_distribution': _counter(selected_layer_counts),
            'layer_mode_raw_distribution': _counter(selected_modes),
            'layer_default_weight_distribution': _counter(selected_weights),
            'matches': sorted(program_matches, key=lambda row: row['path_id']),
            'transition_model_controllers': transitions.get('counts', {}).get('controllers'),
            'transition_model_layers_total': transitions.get('counts', {}).get('layers_total'),
            'transition_model_controllers_with_one_layer': transitions.get('counts', {}).get(
                'controllers_with_one_layer'),
            'total_native_animators_referencing_a_graph_controller': sum(
                int(count) for path_id, count in
                serialized['animator_components_by_controller'].items()
                if int(path_id) in graph_ids),
            'graph_controllers_referenced_by_animator_count': len(referenced_graph_ids),
            'graph_controllers_unreferenced_by_animator_count': len(graph_ids - used_animator_ids),
        },
        'managed_api_surface_from_il2cpp_dump': api,
        'serialized_animation_curve_inventory': motion,
        'conclusion': {
            'multi_layer_blending_exercised_by_recovered_controller_graphs': (
                graph['controllers_with_multiple_layers'] > 0),
            'multi_layer_blending_status': 'NOT_EXERCISED_IN_RECOVERED_GRAPH_SET',
            'property_curve_data_available': motion['counts']['streamed_key_records_in_export'] > 0,
            'property_interpolation_native_algorithm_proven': False,
            'reason_property_interpolation_unproven': (
                'The export contains curve API/type declarations, serialized streamed coefficients '
                'and clip/layout data, but no Unity engine method bodies or native runtime '
                'readback comparing evaluated property values.'),
            'native_evidence_blocker': (
                'Need pinned Unity native Animator/AnimationCurve implementation bytes or a '
                'reproducible runtime probe sampling current/next Animator state, layer weight, '
                'clip weights, and bound property values at several transition times.'),
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true', help='write pinned evidence artifact')
    parser.add_argument('--summary', action='store_true', help='print short decision and totals')
    parser.add_argument('--output', default=OUT_DEFAULT)
    args = parser.parse_args(argv)
    if args.build:
        artifact = build()
        write_gz(ROOT / args.output, artifact)
        conclusion = artifact['conclusion']
        print(f"wrote {args.output}: {artifact['serialized_controller_graphs']['controller_records']} "
              f"controller graphs / {artifact['serialized_component_inventory']['animator_components']} "
              f"Animator components; multi-layer={conclusion['multi_layer_blending_status']}; "
              f"native interpolation proven={conclusion['property_interpolation_native_algorithm_proven']}")
        return 0
    artifact = read_gz(ROOT / args.output)
    if args.summary:
        summary = {
            'serialized_controller_graphs': artifact['serialized_controller_graphs']['controller_records'],
            'layer_count_distribution': artifact['serialized_controller_graphs']['layer_count_distribution'],
            'animator_components': artifact['serialized_component_inventory']['animator_components'],
            'transition_model_scope': artifact['transition_model_scope_check']['layer_count_distribution'],
            'native_layer_readback_and_clip_weight_api': artifact['managed_api_surface_from_il2cpp_dump']['global_api_name_occurrence_counts'],
            'conclusion': artifact['conclusion'],
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(artifact['conclusion'], ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
