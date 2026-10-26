#!/usr/bin/env python3
"""Independent, read-only replication audit of the decoded Animator transition graph.

This deliberately does not import the transition scheduler/normalizer. It counts and
canonicalizes the raw constant arrays in l3_animator_programs.json.gz, then compares that
independent pass with l3_transition_model.json.gz. It is an artifact-level replication,
not a second APK parser or a Unity runtime test.
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = 'datas/l3_animator_programs.json.gz'
MODEL = 'datas/l3_transition_model.json.gz'
OUT_DEFAULT = 'datas/l3_transition_replication.json.gz'

RAW_FIELD_MAP = {
    'destination': ('m_DestinationState', 'm_Destination'),
    'transition_duration': ('m_TransitionDuration',),
    'transition_offset': ('m_TransitionOffset',),
    'exit_time': ('m_ExitTime',),
    'has_exit_time': ('m_HasExitTime',),
    'has_fixed_duration': ('m_HasFixedDuration',),
    'interruption_source': ('m_InterruptionSource',),
    'ordered_interruption': ('m_OrderedInterruption',),
    'can_transition_to_self': ('m_CanTransitionToSelf',),
}

LIMITS = [
    'artifact_level_replication: independently traverses raw constant-array wrappers in '
    'l3_animator_programs.json.gz; it is not an independent APK extraction',
    'normalizer_not_imported: no import or call to l3_transition_scheduler.py; comparison '
    'target is l3_transition_model.json.gz, whose provenance remains a dependency',
    'raw_arrays_authority: transition counts and condition counts are taken from each '
    'wrapper raw.m_ConditionConstantArray and raw destination/flag fields',
    'destination_scope: numeric destinations are compared literally; encoded values are '
    'not assigned engine meanings and no scheduling/reachability is inferred',
    'identity_scope: controllers join by (serialized_file, path_id); transitions join '
    'within controller/machine/scope/array order, never by transition id alone',
    'no_runtime_claim: no Unity scheduling, state readback, parameter script, layer blend, '
    'property interpolation, or render is performed',
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def read_gz(path: Path):
    with gzip.open(path, 'rt', encoding='utf-8') as stream:
        return json.load(stream)


def write_gz(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False,
                         separators=(',', ':')).encode('utf-8')
    with path.open('wb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as packed:
            packed.write(payload)


def counter(values):
    counts = collections.Counter(str(value) for value in values)
    return dict(sorted(counts.items(), key=lambda pair: (-pair[1], pair[0])))


def identity_key(obj):
    ident = obj['identity']
    return (ident['serialized_file'], int(ident['path_id']))


def _transition_groups(machine):
    """Yield raw transition wrappers in serialized traversal order by declared scope."""
    yield 'any', list(machine.get('any_state_transitions') or [])
    yield 'state', [(int(state.get('state_index', -1)), transition)
                    for state in (machine.get('states') or [])
                    for transition in (state.get('transitions') or [])]
    yield 'selector', [(bool((selector.get('raw') or {}).get('m_IsEntry')),
                        transition)
                       for selector in (machine.get('selectors') or [])
                       for transition in (selector.get('transitions') or [])]


def _raw_destination(raw):
    for field in ('m_DestinationState', 'm_Destination'):
        if field in raw:
            return raw[field]
    return None


def _raw_conditions(wrapper):
    # The raw array is the decoded serialized source, not the prelinked name cache.
    return list(((wrapper.get('raw') or {}).get('m_ConditionConstantArray')) or [])


def _condition_raw(entry):
    return entry.get('data', entry) if isinstance(entry, dict) else {}


def _source_transition_signature(scope, source, wrapper):
    raw = wrapper.get('raw') or {}
    dest_field = 'm_Destination' if scope == 'selector' else 'm_DestinationState'
    conditions = []
    wrapped_conditions = wrapper.get('conditions') or []
    for index, entry in enumerate(_raw_conditions(wrapper)):
        cond = _condition_raw(entry)
        names = (wrapped_conditions[index].get('parameter_names') or []
                 if index < len(wrapped_conditions) else [])
        conditions.append({
            'mode': cond.get('m_ConditionMode'),
            'parameter_id': cond.get('m_EventID'),
            'threshold': cond.get('m_EventThreshold'),
            'exit_time': cond.get('m_ExitTime'),
            'parameter_names': names,
        })
    serialized = {}
    for key, fields in RAW_FIELD_MAP.items():
        if key == 'destination':
            continue
        field = fields[0]
        value = raw.get(field)
        # The normalizer deliberately converts absent bool flags to False; retain
        # source-key absence separately in distributions, but compare that exact
        # normalized value rather than calling it a mismatch.
        if key in ('has_exit_time', 'has_fixed_duration'):
            value = bool(value)
        serialized[key] = value
    return {
        'scope': scope,
        'source_state_index': source if scope == 'state' else None,
        'destination_raw': raw.get(dest_field),
        'conditions': conditions,
        'serialized': serialized,
    }


def _model_transition_signature(scope, source, transition):
    return {
        'scope': scope,
        'source_state_index': source if scope == 'state' else None,
        'destination_raw': (transition.get('destination') or {}).get('raw'),
        'conditions': [{key: cond.get(key) for key in
                       ('mode', 'parameter_id', 'threshold', 'exit_time', 'parameter_names')}
                       for cond in (transition.get('conditions') or [])],
        'serialized': {key: transition.get(key) for key in RAW_FIELD_MAP
                       if key != 'destination'},
    }


def _make_comparison(source_controllers, model_controllers):
    model_by_identity = {identity_key(item): item for item in model_controllers}
    field_mismatches = collections.Counter()
    examples = []
    compared_controllers = 0
    compared_machines = 0
    compared_transitions = 0
    compared_conditions = 0
    compared_states = 0
    compared_parameters = 0
    compared_motion_nodes = 0
    controller_rows = []
    source_identities = set()

    def compare(path_id, machine_index, scope, source, left, right):
        nonlocal compared_transitions, compared_conditions
        compared_transitions += 1
        s_sig = _source_transition_signature(scope, source, left)
        m_sig = _model_transition_signature(scope, source, right)
        for key in ('scope', 'source_state_index', 'destination_raw', 'serialized',
                    'conditions'):
            if s_sig[key] != m_sig[key]:
                field_mismatches[key] += 1
                if len(examples) < 20:
                    examples.append({'controller_path_id': path_id,
                                     'machine_index': machine_index, 'scope': scope,
                                     'source_state_index': source, 'field': key,
                                     'source': s_sig[key], 'model': m_sig[key]})
        compared_conditions += len(s_sig['conditions'])
        if len(left.get('conditions') or []) != len(right.get('conditions') or []):
            field_mismatches['condition_wrapper_count'] += 1

    for source_controller in source_controllers:
        key = identity_key(source_controller)
        source_identities.add(key)
        model_controller = model_by_identity.get(key)
        pid = int(key[1])
        row = {'serialized_file': key[0], 'path_id': pid,
               'controller_name': source_controller.get('name'),
               'model_present': model_controller is not None,
               'machines_compared': 0, 'transitions_compared': 0,
               'conditions_compared': 0, 'mismatches': {}}
        if model_controller is None:
            field_mismatches['controller_missing'] += 1
            controller_rows.append(row)
            continue
        compared_controllers += 1
        source_parameters = source_controller.get('parameters') or []
        model_parameters = model_controller.get('parameters') or []
        if len(source_parameters) != len(model_parameters):
            field_mismatches['parameter_count'] += 1
        for index, source_parameter in enumerate(source_parameters):
            if index >= len(model_parameters):
                continue
            model_parameter = model_parameters[index]
            raw_parameter = source_parameter.get('raw') or {}
            expected = {
                'names': source_parameter.get('names') or [],
                'id': raw_parameter.get('m_ID'),
                'index': raw_parameter.get('m_Index'),
                'type': raw_parameter.get('m_Type'),
                'default': source_parameter.get('default'),
                'default_status': source_parameter.get('default_status'),
                'default_storage': source_parameter.get('default_storage'),
            }
            compared_parameters += 1
            for field, value in expected.items():
                if model_parameter.get(field) != value:
                    field_mismatches[f'parameter_{field}'] += 1
        source_layer_count = len(source_controller.get('layers') or [])
        if model_controller.get('layer_count') != source_layer_count:
            field_mismatches['layer_count'] += 1
        source_machines = source_controller.get('machines') or []
        model_machines = model_controller.get('machines') or []
        if len(source_machines) != len(model_machines):
            field_mismatches['machine_count'] += 1
        model_machine_by_index = {int(machine.get('machine_index', -1)): machine
                                  for machine in model_machines}
        for source_machine in source_machines:
            machine_index = int(source_machine.get('machine_index', 0))
            model_machine = model_machine_by_index.get(machine_index)
            if model_machine is None:
                field_mismatches['machine_missing'] += 1
                continue
            compared_machines += 1
            row['machines_compared'] += 1
            for field in ('default_state_index', 'default_status'):
                if source_machine.get(field) != model_machine.get(field):
                    field_mismatches[f'machine_{field}'] += 1
            state_sources = {int(state.get('state_index', -1)): state
                             for state in (source_machine.get('states') or [])}
            model_states = {int(state.get('state_index', -1)): state
                            for state in (model_machine.get('states') or [])}
            if set(state_sources) != set(model_states):
                field_mismatches['state_indices'] += 1
            for state_index, source_state in state_sources.items():
                model_state = model_states.get(state_index)
                if model_state is None:
                    field_mismatches['state_missing'] += 1
                    continue
                compared_states += 1
                raw_state = source_state.get('raw') or {}
                state_expectations = {
                    'speed': raw_state.get('m_Speed'),
                    'loop': bool(raw_state.get('m_Loop')),
                    'write_default_values': raw_state.get('m_WriteDefaultValues'),
                    'mirror': raw_state.get('m_Mirror'),
                }
                for field, expected in state_expectations.items():
                    if model_state.get(field) != expected:
                        field_mismatches[f'state_{field}'] += 1
                source_nodes = [node for tree in (source_state.get('trees') or [])
                                for node in (tree.get('nodes') or [])]
                model_motion = model_state.get('motion') or []
                if len(source_nodes) != len(model_motion):
                    field_mismatches['state_motion_node_count'] += 1
                for node_index, source_node in enumerate(source_nodes):
                    if node_index >= len(model_motion):
                        continue
                    compared_motion_nodes += 1
                    source_clip = source_node.get('clip')
                    target_motion = model_motion[node_index]
                    source_node_raw = source_node.get('raw') or {}
                    for field, expected in (
                        ('clip', source_clip),
                        ('node_duration', source_node_raw.get('m_Duration')),
                        ('node_cycle_offset', source_node_raw.get('m_CycleOffset')),
                        ('clip_status', source_node.get('clip_status')),
                    ):
                        if target_motion.get(field) != expected:
                            field_mismatches[f'motion_{field}'] += 1
                source_transitions = source_state.get('transitions') or []
                model_transitions = model_state.get('transitions') or []
                if len(source_transitions) != len(model_transitions):
                    field_mismatches['state_transition_count'] += 1
                for i, left in enumerate(source_transitions):
                    if i < len(model_transitions):
                        before = compared_transitions
                        compare(pid, machine_index, 'state', state_index, left,
                                model_transitions[i])
                        row['transitions_compared'] += compared_transitions - before
            for scope, attr in (('any', 'any_state_transitions'),):
                lefts = source_machine.get(attr) or []
                rights = model_machine.get(attr) or []
                if len(lefts) != len(rights):
                    field_mismatches[f'{scope}_transition_count'] += 1
                for i, left in enumerate(lefts):
                    if i < len(rights):
                        before = compared_transitions
                        compare(pid, machine_index, scope, None, left, rights[i])
                        row['transitions_compared'] += compared_transitions - before
            source_selectors = source_machine.get('selectors') or []
            model_selectors = model_machine.get('selectors') or []
            if len(source_selectors) != len(model_selectors):
                field_mismatches['selector_count'] += 1
            for i, selector in enumerate(source_selectors):
                if i >= len(model_selectors):
                    continue
                model_selector = model_selectors[i]
                source_entry = (selector.get('raw') or {}).get('m_IsEntry')
                if source_entry != model_selector.get('is_entry'):
                    field_mismatches['selector_is_entry'] += 1
                lefts = selector.get('transitions') or []
                rights = model_selector.get('transitions') or []
                if len(lefts) != len(rights):
                    field_mismatches['selector_transition_count'] += 1
                for j, left in enumerate(lefts):
                    if j < len(rights):
                        before = compared_transitions
                        compare(pid, machine_index, 'selector', None, left, rights[j])
                        row['transitions_compared'] += compared_transitions - before
            row['conditions_compared'] += sum(
                len(_raw_conditions(transition))
                for _, group in _transition_groups(source_machine)
                for transition in (group if group and isinstance(group[0], dict)
                                   else [value[1] for value in group]))
        controller_rows.append(row)

    extra_identities = set(model_by_identity) - source_identities
    if extra_identities:
        field_mismatches['controller_extra_in_model'] += len(extra_identities)
    return {
        'controllers_compared': compared_controllers,
        'machines_compared': compared_machines,
        'transitions_compared': compared_transitions,
        'conditions_compared': compared_conditions,
        'states_compared': compared_states,
        'parameters_compared': compared_parameters,
        'motion_nodes_compared': compared_motion_nodes,
        'mismatch_counts': dict(sorted(field_mismatches.items())),
        'mismatch_examples': examples,
        'equal': not field_mismatches,
        'extra_model_controllers': len(extra_identities),
        'per_controller': controller_rows,
    }


def _audit_source(source):
    controllers = source.get('controllers') or []
    counts = collections.Counter()
    counters = {name: collections.Counter() for name in (
        'parameter_types_raw', 'condition_modes_raw', 'destinations_raw',
        'interruption_sources_raw', 'interruption_source_presence',
        'transition_scope', 'selector_entries', 'raw_field_presence_by_scope')}
    rows = []

    for controller in controllers:
        machines = controller.get('machines') or []
        counts['controllers'] += 1
        counts['machines'] += len(machines)
        counts['layers'] += len(controller.get('layers') or [])
        counts['parameters'] += len(controller.get('parameters') or [])
        for parameter in controller.get('parameters') or []:
            raw = parameter.get('raw') or {}
            counters['parameter_types_raw'][raw.get('m_Type', 'absent')] += 1
        controller_states = 0
        controller_transitions = 0
        controller_conditions = 0
        for machine in machines:
            states = machine.get('states') or []
            counts['states'] += len(states)
            controller_states += len(states)
            if not states:
                counts['empty_machines'] += 1
            state_indices = {int(state.get('state_index', -1)) for state in states}
            default = machine.get('default_state_index')
            if default is not None and int(default) in state_indices:
                counts['valid_defaults'] += 1
            else:
                counts['invalid_or_absent_defaults'] += 1
            if (machine.get('default_status') == 'valid_index') != (
                    default is not None and int(default) in state_indices):
                counts['default_status_disagreements'] += 1

            groups = []
            any_transitions = machine.get('any_state_transitions') or []
            groups.extend(('any', None, item) for item in any_transitions)
            for state in states:
                for item in state.get('transitions') or []:
                    groups.append(('state', int(state.get('state_index', -1)), item))
            for selector in machine.get('selectors') or []:
                is_entry = (selector.get('raw') or {}).get('m_IsEntry')
                counters['selector_entries'][str(is_entry)] += 1
                for item in selector.get('transitions') or []:
                    groups.append(('selector', None, item))
            for scope, source_state, wrapper in groups:
                raw = wrapper.get('raw') or {}
                counts[f'{scope}_transitions'] += 1
                controller_transitions += 1
                counters['transition_scope'][scope] += 1
                presence_fields = ('m_DestinationState', 'm_Destination',
                                   'm_TransitionDuration', 'm_TransitionOffset',
                                   'm_ExitTime', 'm_HasExitTime', 'm_HasFixedDuration',
                                   'm_InterruptionSource', 'm_OrderedInterruption',
                                   'm_CanTransitionToSelf')
                for field in presence_fields:
                    state = 'present' if field in raw else 'absent'
                    counters['raw_field_presence_by_scope'][f'{scope}:{field}:{state}'] += 1
                destination = _raw_destination(raw)
                counters['destinations_raw'][destination] += 1
                if destination not in state_indices:
                    counts['destination_not_local_to_machine'] += 1
                else:
                    counts['destination_local_to_machine'] += 1
                conditions = _raw_conditions(wrapper)
                counts['conditions'] += len(conditions)
                controller_conditions += len(conditions)
                counts['transitions_with_conditions' if conditions else
                       'transitions_without_conditions'] += 1
                for entry in conditions:
                    cond = _condition_raw(entry)
                    counters['condition_modes_raw'][cond.get('m_ConditionMode', 'absent')] += 1
                for field, predicate in (
                    ('has_exit_time_true', lambda v: bool(v.get('m_HasExitTime'))),
                    ('has_fixed_duration_true', lambda v: bool(v.get('m_HasFixedDuration'))),
                    ('duration_nonzero', lambda v: bool(v.get('m_TransitionDuration'))),
                    ('can_transition_to_self_true', lambda v: v.get('m_CanTransitionToSelf') is True),
                    ('can_transition_to_self_false', lambda v: v.get('m_CanTransitionToSelf') is False),
                ):
                    if predicate(raw):
                        counts[field] += 1
                if 'm_InterruptionSource' in raw:
                    counters['interruption_source_presence']['present'] += 1
                    counters['interruption_sources_raw'][raw['m_InterruptionSource']] += 1
                else:
                    counters['interruption_source_presence']['absent'] += 1
                counts['transition_raw_records'] += 1
        # Motion is counted from the source's leaf-node wrappers, no model scheduler data.
        for state in states:
            for tree in state.get('trees') or []:
                nodes = tree.get('nodes') or []
                counts['motion_nodes'] += len(nodes)
                for node in nodes:
                    clip = node.get('clip')
                    counts['motion_nodes_with_clip_identity' if clip else
                           'motion_nodes_without_clip_identity'] += 1
        rows.append({
            'serialized_file': controller['identity']['serialized_file'],
            'path_id': int(controller['identity']['path_id']),
            'name': controller.get('name'),
            'machines': len(machines), 'states': controller_states,
            'transitions': controller_transitions, 'conditions': controller_conditions,
            'parameters': len(controller.get('parameters') or []),
            'layers': len(controller.get('layers') or []),
        })

    counts['controllers_with_one_layer'] = sum(row['layers'] == 1 for row in rows)
    counts['states_speed_not_one'] = sum(
        1 for controller in controllers for machine in (controller.get('machines') or [])
        for state in (machine.get('states') or [])
        if (state.get('raw') or {}).get('m_Speed') not in (None, 1, 1.0))
    counts['states_looping'] = sum(
        1 for controller in controllers for machine in (controller.get('machines') or [])
        for state in (machine.get('states') or []) if bool((state.get('raw') or {}).get('m_Loop')))
    counts['states_without_motion'] = sum(
        1 for controller in controllers for machine in (controller.get('machines') or [])
        for state in (machine.get('states') or [])
        if not any(node.get('clip') for tree in (state.get('trees') or [])
                   for node in (tree.get('nodes') or [])))
    return {
        'counts': dict(sorted(counts.items())),
        'distributions': {name: dict(sorted(values.items(), key=lambda pair:
                                              (-pair[1], str(pair[0]))))
                          for name, values in counters.items()},
        'per_controller': sorted(rows, key=lambda row:
                                 (row['serialized_file'], row['path_id'])),
    }


def _compare_recomputed_counts(source_counts, model_counts):
    pairs = {
        'controllers': ('controllers', 'controllers'),
        'machines': ('machines', 'machines'),
        'states': ('states', 'states'),
        'any_transitions': ('any_transitions', 'any_transitions'),
        'state_transitions': ('state_transitions', 'state_transitions'),
        'selector_transitions': ('selector_transitions', 'selector_transitions'),
        'conditions': ('conditions', 'conditions'),
        'parameters': ('parameters', 'parameters'),
        'empty_machines': ('empty_machines', 'empty_machines'),
        'states_without_motion': ('states_without_motion', 'states_without_motion'),
        'motion_nodes': ('motion_leaves', 'motion_nodes'),
    }
    result = {}
    for model_key, (model_field, source_key) in pairs.items():
        got = source_counts.get(source_key, 0)
        want = model_counts.get(model_field)
        result[model_key] = {'source_recount': got, 'transition_model': want,
                             'equal': got == want}
    return result


def build():
    source = read_gz(ROOT / SOURCE)
    model = read_gz(ROOT / MODEL)
    audit = _audit_source(source)
    comparison = _make_comparison(source.get('controllers') or [],
                                  model.get('controllers') or [])
    counts_check = _compare_recomputed_counts(audit['counts'], model.get('counts') or {})
    counts_check['all_equal'] = all(item['equal'] for item in counts_check.values()
                                    if isinstance(item, dict))
    source_sha = sha256(ROOT / SOURCE)
    model_sha = sha256(ROOT / MODEL)
    return {
        'schema': 1,
        'provisional': True,
        'scope': ('Independent artifact-level recount and ordered raw-field comparison of the '
                  '232 decoded Animator transition graphs. Does not independently parse the APK.'),
        'model_notice': ('REPLICATION / MODEL AUDIT — not Unity execution, engine readback, '
                         'or rendering. It independently recounts decoded source artifact data.'),
        'replication': True,
        'inputs': {SOURCE: source_sha, MODEL: model_sha},
        'build': {
            'generator': 'tools/verify/l3_transition_replication.py --build',
            'tool_sha256': sha256(Path(__file__).resolve()),
        },
        'decode_limits': LIMITS,
        'source_provenance': {
            'animator_programs_schema': source.get('schema'),
            'animator_programs_provisional': source.get('provisional'),
            'transition_model_provisional': model.get('provisional'),
            'transition_model_inputs': model.get('inputs'),
            'not_independent_apk_extraction': True,
        },
        'counts_independent': audit['counts'],
        'distributions_independent': audit['distributions'],
        'per_controller': audit['per_controller'],
        'comparison_to_transition_model': {
            'counts': counts_check,
            'raw_ordered_field_comparison': comparison,
            'all_equal': counts_check['all_equal'] and comparison['equal'],
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true', help='recount and write the artifact')
    parser.add_argument('--controller', type=int, help='show one controller row by path ID')
    parser.add_argument('--summary', action='store_true', help='print compact comparison summary')
    parser.add_argument('--output', default=OUT_DEFAULT)
    args = parser.parse_args(argv)
    if args.build:
        artifact = build()
        write_gz(ROOT / args.output, artifact)
        cmp = artifact['comparison_to_transition_model']
        print(f"wrote {args.output}: {artifact['counts_independent'].get('controllers')} controllers / "
              f"{artifact['counts_independent'].get('states')} states / "
              f"{artifact['counts_independent'].get('conditions')} conditions; "
              f"count_equal={cmp['counts']['all_equal']} field_equal="
              f"{cmp['raw_ordered_field_comparison']['equal']}")
        return 0
    artifact = read_gz(ROOT / args.output)
    if args.controller is not None:
        matches = [row for row in artifact['per_controller']
                   if row['path_id'] == args.controller]
        print(json.dumps(matches, ensure_ascii=False, indent=2))
    elif args.summary:
        result = artifact['comparison_to_transition_model']
        print(json.dumps({
            'counts_independent': artifact['counts_independent'],
            'counts_match': result['counts']['all_equal'],
            'graph_match': result['raw_ordered_field_comparison']['equal'],
            'comparison_totals': {key: result['raw_ordered_field_comparison'][key]
                                  for key in ('controllers_compared', 'machines_compared',
                                              'states_compared', 'parameters_compared',
                                              'motion_nodes_compared', 'transitions_compared',
                                              'conditions_compared')},
            'mismatch_counts': result['raw_ordered_field_comparison']['mismatch_counts'],
        }, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(artifact['counts_independent'], ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
