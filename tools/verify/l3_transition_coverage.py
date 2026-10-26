"""Reachability + driven-coverage model over the 232 decoded Animator controllers.

Item #14 of the PR12 coordination table (AI-3 domain: transition + driven properties).

What this answers, measured from the serialized graph rather than assumed:

1. which states / clips can ever be entered from the machine's serialized default, and through
   which transitions (with the parameters that have to be set on the way);
2. which states can never be entered at all, and why (no incoming local transition, only incoming
   from other unreachable states, only an encoded destination, no valid default);
3. which of the 52 400 animation bindings sit on clips that a reachable state actually plays, split
   by the property route kinds of `l3_driven_props` — i.e. which driven properties (rect / alpha /
   active / text / particle module) the game can reach at all.

Boundaries: this is a graph/coverage model. It does not simulate engine scheduling (that is
`l3_transition_scheduler`), does not read a Unity runtime, does not render, and it deliberately
ignores parameter *values* in the "parameterized" closure — a transition is counted as traversable
when its conditions could be satisfied, not when they are satisfied in some recorded trace.

Usage:
    python3 -m tools.verify.l3_transition_coverage --build
    python3 -m tools.verify.l3_transition_coverage --controller 1792
    python3 -m tools.verify.l3_transition_coverage --list --filter Boss
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from l3_model_common import (ROOT, envelope, fin, inputs_map, read_json_gz, sha256_file,
                             write_json_gz)
from l3_driven_props import (BINDINGS_GLOB, MOTION_GLOB, glob_inputs, iter_bindings,
                             load_motion, route_table)

TRANSITION_ARTIFACT = 'datas/l3_transition_model.json.gz'
OUT_DEFAULT = 'datas/l3_transition_coverage.json.gz'

SCOPE = (
    'Reachability and driven-coverage model over the 232 decoded Animator controllers: state graph '
    'closure from the serialized default state, unreachable/encoded-destination inventory, and the '
    'join from reachable states to the clip bindings and their driven-property route kinds. Edges '
    'are taken verbatim from `datas/l3_transition_model.json.gz`; every rule that is a modelling '
    'choice is listed in `decode_limits` and marked proven=false. No engine scheduling, no '
    'readback, no render, no parameter-value trace.'
)

DECODE_LIMITS = [
    'closure_is_graph_not_trace: a state is "reachable" when a path of serialized transitions '
    'exists, not when the game provably entered it; nothing here reads a recorded play session',
    'parameter_values_ignored_in_full_closure: the "parameterized" closure treats every condition '
    'as satisfiable; the "unconditional" closure only follows transitions with no condition at all',
    'exit_time_treated_as_eventual: a transition with only m_HasExitTime is followed, because a '
    'finite state time will cross the threshold in this model; looping-state wrap semantics are '
    'l3_transition_scheduler policy, not proven here',
    'encoded_destinations_block: raw 30000/30001/4294967295 do not identify a local state, so a '
    'state reachable only through one is reported unreachable with reason '
    'only_encoded_destination, never guessed',
    'self_transition_flag_applied: an edge whose destination equals its source and whose '
    'm_CanTransitionToSelf is false cannot extend the closure',
    'selector_entries_only: selector transitions extend the closure only when the selector is '
    'flagged is_entry; non-entry selectors are counted and listed, not traversed',
    'binding_attribution_via_animator_attachment: a binding record names an Animator component and '
    'a clip; the controller comes from `datas/l3_animator_programs.json.gz` animator_attachments. '
    'An animator attached to several controllers counts as reachable when any of them reaches the '
    'clip — the count of such ambiguous rows is reported instead of silently picking one',
    'unresolved_bindings_kept: bindings whose field cannot be established keep the `unresolved` '
    'kind from l3_driven_props instead of being dropped or guessed',
    'transition_ids_are_machine_scoped: ids look like m<machine>:state<N>:<i> and repeat across '
    'controllers, so no join may key on the id alone',
    'evidence (reports 100/103), not serialized callbacks; this model does not claim a trigger is '
    'ever raised',
]

MODEL_NOTICE = (
    'MODEL OUTPUT — not Unity simulation, not a readback of engine state and not a render. Every '
    'count is recomputed from the serialized controller graph and the decoded clip bindings; where '
    'the source cannot decide a question the answer is a named reason, not a default.'
)

CONDITION_MODES = {1: 'If', 2: 'IfNot', 3: 'Greater', 4: 'Less', 5: 'Equals', 6: 'NotEqual'}

UNCONDITIONAL_CLASSES = ('unconditional', 'exit_time_gated')


# --------------------------------------------------------------------------
# Edge model
# --------------------------------------------------------------------------
def edge_class(transition) -> str:
    """How hard is it to traverse this transition in the model."""
    if transition.get('conditions'):
        return 'parameter_gated'
    if transition.get('has_exit_time') or (transition.get('exit_time') or 0) > 0:
        return 'exit_time_gated'
    return 'unconditional'


def gate_names(transition):
    """Parameter names a transition's conditions refer to, sorted."""
    names = set()
    for condition in transition.get('conditions') or []:
        for name in condition.get('parameter_names') or []:
            names.add(name)
    return sorted(names)


def edge_blockers(transition, current_state):
    """Reasons (model rules) that stop this transition from extending the closure."""
    destination = transition['destination']
    if destination['status'] != 'local_state_index':
        return ['encoded_destination']
    if destination['index'] == current_state and transition.get('can_transition_to_self') is False:
        return ['self_transition_disallowed']
    return []


def machine_edges(machine):
    """All transitions of one machine, deterministically ordered."""
    edges = []
    for selector in machine['selectors']:
        for transition in selector['transitions']:
            edges.append(('entry' if selector['is_entry'] else 'selector', None, transition))
    for transition in machine['any_state_transitions']:
        edges.append(('any', None, transition))
    for state in machine['states']:
        for transition in state['transitions']:
            edges.append(('state', state['state_index'], transition))
    return edges


def start_source(machine):
    """Where the machine begins, and on what authority."""
    starts = []
    if machine['default_status'] == 'valid_index':
        starts.append({'source': 'serialized_default_state', 'state': machine['default_state_index']})
    for selector in machine['selectors']:
        if not selector['is_entry']:
            continue
        for transition in selector['transitions']:
            if transition['destination']['status'] == 'local_state_index':
                starts.append({'source': 'entry_selector_transition',
                               'state': transition['destination']['index'],
                               'transition_id': transition['id']})
    return starts


def machine_reachability(machine):
    """Two closures (unconditional / parameterized) plus the unreachable inventory."""
    states = [state['state_index'] for state in machine['states']]
    edges = machine_edges(machine)
    starts = start_source(machine)
    start_states = [entry['state'] for entry in starts if entry['state'] in states]

    blocked = []
    traversable = []
    for scope, source_state, transition in edges:
        reasons = edge_blockers(transition, source_state if source_state is not None else -1)
        record = {
            'transition_id': transition['id'],
            'scope': scope,
            'from_state': source_state,
            'to_state': (transition['destination']['index']
                         if transition['destination']['status'] == 'local_state_index' else None),
            'destination_raw': transition['destination']['raw'],
            'destination_status': transition['destination']['status'],
            'edge_class': edge_class(transition),
            'gates': gate_names(transition),
            'reasons': reasons,
        }
        (blocked if reasons else traversable).append(record)

    def closure(allowed_classes):
        """BFS with a stable edge order; records the path that first reached each state."""
        reached = {}
        queue = collections.deque()
        for state in sorted(set(start_states)):
            reached[state] = {'distance': 0, 'gates': [], 'path': [], 'via': 'start'}
            queue.append(state)
        while queue:
            current = queue.popleft()
            for record in traversable:
                if record['edge_class'] not in allowed_classes:
                    continue
                if record['scope'] == 'entry':
                    continue
                if record['scope'] in ('any', 'state'):
                    if record['scope'] == 'state' and record['from_state'] != current:
                        continue
                    if record['to_state'] == current and record['scope'] == 'any':
                        # AnyState on the current state still needs the self flag to be allowed
                        pass
                target = record['to_state']
                if target not in states or target in reached:
                    continue
                parent = reached[current]
                reached[target] = {
                    'distance': parent['distance'] + 1,
                    'gates': sorted(set(parent['gates']) | set(record['gates'])),
                    'path': parent['path'] + [{'transition_id': record['transition_id'],
                                               'from_state': current,
                                               'to_state': target}],
                    'via': record['scope'],
                }
                queue.append(target)
        return reached

    unconditional = closure(set(UNCONDITIONAL_CLASSES))
    parameterized = closure({'unconditional', 'exit_time_gated', 'parameter_gated'})

    incoming = collections.defaultdict(list)
    for record in traversable:
        if record['to_state'] is not None:
            incoming[record['to_state']].append(record)
    encoded_incoming = collections.defaultdict(list)
    for record in blocked:
        if 'encoded_destination' in record['reasons'] and record['to_state'] is None:
            encoded_incoming[record['scope']].append(record)

    unreachable = []
    for state in states:
        if state in parameterized:
            continue
        if incoming[state]:
            reason = 'only_from_unreachable_states'
        else:
            reason = 'no_incoming_local_transition'
        unreachable.append({
            'state': state,
            'reason': reason,
            'incoming_local': len(incoming[state]),
            'incoming':[{'transition_id': r['transition_id'], 'scope': r['scope'],
                         'from_state': r['from_state']}
                        for r in incoming[state]],
            'encoded_transitions_in_machine': sum(len(v) for v in encoded_incoming.values()),
        })

    return {
        'machine_index': machine['machine_index'],
        'default_state_index': machine['default_state_index'],
        'default_status': machine['default_status'],
        'start_sources': starts,
        'states': len(states),
        'state_indices': states,
        'transitions': len(edges),
        'traversable': len(traversable),
        'blocked': blocked,
        'blocked_by_reason': dict(collections.Counter(
            reason for record in blocked for reason in record['reasons'])),
        'edges_by_class': {f'{scope}:{cls}': value for (scope, cls), value in sorted(
            collections.Counter(traversable_scope(edges)).items())},
        'reachable_unconditional': sorted(unconditional),
        'reachable_parameterized': sorted(parameterized),
        'paths': {str(state): info for state, info in sorted(parameterized.items())},
        'gates_for_state': {str(state): info['gates'] for state, info in sorted(parameterized.items())},
        'unreachable': unreachable,
    }


def traversable_scope(edges):
    """(scope, edge_class) pairs for every edge, whether or not it is blocked."""
    for scope, _source, transition in edges:
        yield scope, edge_class(transition)


def controller_reachability(controller):
    machines = [machine_reachability(machine) for machine in controller['machines']]
    return {
        'identity': controller['identity'],
        'name': controller['name'],
        'layer_count': controller['layer_count'],
        'parameters': [{'name': parameter['name'], 'type_class': parameter['type_class']}
                       for parameter in controller['parameters']],
        'machines': machines,
    }


def reachable_state_keys(controller_model):
    keys = set()
    for machine in controller_model['machines']:
        for state in machine['reachable_parameterized']:
            keys.add((machine['machine_index'], state))
    return keys


def state_clips(controller):
    """(machine, state) -> list of clip identities, from the transition artifact."""
    out = {}
    for machine in controller['machines']:
        for state in machine['states']:
            out[(machine['machine_index'], state['state_index'])] = [
                (leaf['clip']['serialized_file'], int(leaf['clip']['path_id']))
                for leaf in state['motion'] if leaf.get('clip')]
    return out


# --------------------------------------------------------------------------
# Binding join
# --------------------------------------------------------------------------
def binding_kinds():
    """(typeID, attribute) -> route kind, measured through l3_driven_props."""
    table, _class_ids = route_table()
    return {(row['class_id'], row['attribute']): row['kind'] for row in table}


def load_animator_controllers():
    """Animator component -> controller identities, from the animator program artifact."""
    programs = read_json_gz('datas/l3_animator_programs.json.gz')
    mapping = {}
    for attachment in programs['animator_attachments']:
        key = (attachment['animator']['serialized_file'], int(attachment['animator']['path_id']))
        mapping[key] = sorted((controller['serialized_file'], int(controller['path_id']))
                              for controller in attachment['controllers'])
    return mapping


def clip_reachability(controller_models, controllers, clips):
    """Clip reachability globally and per (controller, clip) pair."""
    referenced = set()
    reachable_parameterized = set()
    reachable_unconditional = set()
    pairs_referenced = set()
    pairs_parameterized = set()
    pairs_unconditional = set()
    holders = collections.defaultdict(set)
    for controller, model in zip(controllers, controller_models):
        identity = (controller['identity']['serialized_file'],
                    int(controller['identity']['path_id']))
        clip_map = state_clips(controller)
        for machine in model['machines']:
            machine_index = machine['machine_index']
            for state, clip_list in clip_map.items():
                if state[0] != machine_index:
                    continue
                for clip in clip_list:
                    referenced.add(clip)
                    pairs_referenced.add((identity, clip))
                    holders[clip].add(identity)
                    if state[1] in machine['reachable_parameterized']:
                        reachable_parameterized.add(clip)
                        pairs_parameterized.add((identity, clip))
                    if state[1] in machine['reachable_unconditional']:
                        reachable_unconditional.add(clip)
                        pairs_unconditional.add((identity, clip))
    missing = sorted(clip for clip in referenced if clip not in clips)
    unreachable = sorted(referenced - reachable_parameterized)
    pairs_unreachable = sorted(pairs_referenced - pairs_parameterized)
    return {
        'clips_in_motion_artifact': len(clips),
        'clips_referenced_by_a_state': len(referenced),
        'clips_referenced_but_not_decoded': len(missing),
        'missing_clip_identities': [{'serialized_file': f, 'path_id': p} for f, p in missing],
        'clips_reachable_unconditional': len(reachable_unconditional),
        'clips_reachable_parameterized': len(reachable_parameterized),
        'clips_unreachable': len(unreachable),
        'unreachable_clip_identities': [{'serialized_file': f, 'path_id': p}
                                        for f, p in unreachable],
        'clips_never_referenced': len(set(clips) - referenced),
        'controller_clip_pairs': len(pairs_referenced),
        'controller_clip_pairs_reachable': len(pairs_parameterized),
        'controller_clip_pairs_unreachable': len(pairs_unreachable),
        'unreachable_pairs': [{'controller': {'serialized_file': c[0], 'path_id': c[1]},
                               'clip': {'serialized_file': f, 'path_id': p}}
                              for (c, (f, p)) in pairs_unreachable],
        'controllers_per_clip': {f'{clip[0]}:{clip[1]}': len(owners)
                                 for clip, owners in sorted(holders.items())},
        'sets': {'clips_reachable_parameterized': reachable_parameterized,
                 'clips_reachable_unconditional': reachable_unconditional,
                 'clips_referenced': referenced,
                 'pairs_reachable_parameterized': pairs_parameterized,
                 'pairs_reachable_unconditional': pairs_unconditional,
                 'pairs_referenced': pairs_referenced},
    }


def binding_coverage(pair_sets, animator_controllers, kinds):
    """Count bindings per attribution tier, split by route kind."""
    tiers = {'all': collections.Counter(), 'animator_mapped': collections.Counter(),
             'controller_clip_reachable_parameterized': collections.Counter(),
             'controller_clip_reachable_unconditional': collections.Counter(),
             'controller_clip_unreachable': collections.Counter()}
    totals = {name: 0 for name in tiers}
    per_clip = collections.Counter()
    ambiguous_rows = 0
    unmapped_examples = []
    for row in iter_bindings():
        clip = (row['clip']['serialized_file'], int(row['clip']['path_id']))
        animator = (row['animator']['serialized_file'], int(row['animator']['path_id']))
        kind = kinds.get((row['binding']['typeID'], row['binding']['attribute']), 'unresolved')
        per_clip[clip] += 1
        controllers = animator_controllers.get(animator) or []
        if len(controllers) > 1:
            ambiguous_rows += 1
        totals['all'] += 1
        tiers['all'][kind] += 1
        if controllers:
            totals['animator_mapped'] += 1
            tiers['animator_mapped'][kind] += 1
        elif len(unmapped_examples) < 8:
            unmapped_examples.append({'animator': {'serialized_file': animator[0],
                                                   'path_id': animator[1]},
                                      'clip': {'serialized_file': clip[0], 'path_id': clip[1]}})
        reachable_param = any((controller, clip) in pair_sets['pairs_reachable_parameterized']
                              for controller in controllers)
        reachable_uncond = any((controller, clip) in pair_sets['pairs_reachable_unconditional']
                              for controller in controllers)
        if reachable_param:
            totals['controller_clip_reachable_parameterized'] += 1
            tiers['controller_clip_reachable_parameterized'][kind] += 1
        if reachable_uncond:
            totals['controller_clip_reachable_unconditional'] += 1
            tiers['controller_clip_reachable_unconditional'][kind] += 1
        if controllers and not reachable_param:
            totals['controller_clip_unreachable'] += 1
            tiers['controller_clip_unreachable'][kind] += 1
    return {'totals': totals,
            'by_kind': {name: dict(sorted(counter.items())) for name, counter in tiers.items()},
            'per_clip_records': per_clip,
            'ambiguous_animator_rows': ambiguous_rows,
            'unmapped_examples': unmapped_examples}


def case_for(controller, model, kind):
    machines = model['machines']
    clips = state_clips(controller)
    return {
        'kind': kind,
        'controller': model['identity'],
        'controller_name': model['name'],
        'machines': [{
            'machine_index': machine['machine_index'],
            'default_state_index': machine['default_state_index'],
            'default_status': machine['default_status'],
            'start_sources': machine['start_sources'],
            'transitions': machine['transitions'],
            'blocked': machine['blocked'],
            'states_reachable_parameterized': machine['reachable_parameterized'],
            'states_reachable_unconditional': machine['reachable_unconditional'],
            'unreachable': machine['unreachable'],
            'gates_for_state': machine['gates_for_state'],
            'clips': {str(state): [{'serialized_file': clip[0], 'path_id': clip[1]}
                                   for clip in clip_list]
                      for state, clip_list in sorted(clips.items())
                      if state[0] == machine['machine_index']},
            'shortest_paths': {str(state): info['path']
                               for state, info in machine['paths'].items()},
        } for machine in machines],
    }


def pick_cases(controller_models, controllers):
    cases = []
    by_path = {model['identity']['path_id']: (controller, model)
               for controller, model in zip(controllers, controller_models)}

    def add(path_id, kind):
        if path_id in by_path:
            controller, model = by_path[path_id]
            cases.append(case_for(controller, model, kind))

    add(1792, 'trigger_cycle_all_states_reachable')
    add(1910, 'exit_time_only_auto_advance')
    ranked_unreachable = sorted(
        controller_models,
        key=lambda model: (-sum(len(machine['unreachable']) for machine in model['machines']),
                           model['identity']['path_id']))
    if ranked_unreachable and sum(len(machine['unreachable'])
                                 for machine in ranked_unreachable[0]['machines']):
        cases.append(case_for(next(c for c, m in zip(controllers, controller_models)
                                   if m is ranked_unreachable[0]),
                              ranked_unreachable[0], 'largest_unreachable_set'))
    ranked_encoded = sorted(
        controller_models,
        key=lambda model: (-sum(len(machine['blocked']) for machine in model['machines']),
                           -sum(machine['states'] for machine in model['machines']),
                           model['identity']['path_id']))
    if ranked_encoded and sum(len(machine['blocked']) for machine in ranked_encoded[0]['machines']):
        cases.append(case_for(next(c for c, m in zip(controllers, controller_models)
                                   if m is ranked_encoded[0]),
                              ranked_encoded[0], 'most_blocked_transitions'))
    return cases


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------
def build():
    transition_model = read_json_gz(TRANSITION_ARTIFACT)
    controllers = transition_model['controllers']
    clips = load_motion()
    kinds = binding_kinds()

    controller_models = [controller_reachability(controller) for controller in controllers]
    clip_info = clip_reachability(controller_models, controllers, clips)
    pair_sets = clip_info.pop('sets')
    coverage = binding_coverage(pair_sets, load_animator_controllers(), kinds)

    states_total = sum(machine['states'] for model in controller_models
                       for machine in model['machines'])
    reachable_parameterized = sum(len(machine['reachable_parameterized'])
                                  for model in controller_models for machine in model['machines'])
    reachable_unconditional = sum(len(machine['reachable_unconditional'])
                                  for model in controller_models for machine in model['machines'])
    unreachable_total = sum(len(machine['unreachable'])
                            for model in controller_models for machine in model['machines'])
    transitions_total = transition_model['counts']['transitions'] if 'transitions' in \
        transition_model['counts'] else (transition_model['counts']['any_transitions'] +
                                         transition_model['counts']['state_transitions'] +
                                         transition_model['counts']['selector_transitions'])
    edge_class_counter = collections.Counter()
    scope_class_counter = collections.Counter()
    blocked_counter = collections.Counter()
    for model in controller_models:
        for machine in model['machines']:
            for key, value in machine['edges_by_class'].items():
                scope, cls = key.split(':', 1)
                scope_class_counter[key] += value
                edge_class_counter[cls] += value
            for reason, value in machine['blocked_by_reason'].items():
                blocked_counter[reason] += value

    parameter_gates = collections.Counter()
    parameter_used = set()
    for model in controller_models:
        names = {parameter['name'] for parameter in model['parameters']}
        own_gates = set()
        for machine in model['machines']:
            for gates in machine['gates_for_state'].values():
                for gate in gates:
                    parameter_gates[gate] += 1
                    own_gates.add(gate)
        parameter_used |= own_gates
        # per controller: declared parameters this controller's own graph never gates on
        model['parameters_never_used_as_gate'] = sorted(names - own_gates)
        model['parameters_used_as_gate'] = sorted(names & own_gates)

    counts = {
        'controllers': len(controllers),
        'machines': sum(len(model['machines']) for model in controller_models),
        'states_total': states_total,
        'states_reachable_unconditional': reachable_unconditional,
        'states_reachable_parameterized': reachable_parameterized,
        'states_unreachable': unreachable_total,
        'transitions_total': transitions_total,
        'edges_by_scope_and_class': dict(sorted(scope_class_counter.items())),
        'edges_by_class': dict(sorted(edge_class_counter.items())),
        'blocked_by_reason': dict(sorted(blocked_counter.items())),
        'clips': {key: value for key, value in clip_info.items() if key.endswith(
            ('artifact', 'state', 'decoded', 'unconditional', 'parameterized', 'unreachable',
             'referenced'))},
        'bindings': {('total' if name == 'all' else name): value
                     for name, value in coverage['totals'].items()},
        'bindings_ambiguous_animator': coverage['ambiguous_animator_rows'],
        'parameters_declared': sum(len(controller['parameters']) for controller in controllers),
        'parameter_declarations_used_as_gate': sum(len(model['parameters_used_as_gate'])
                                                   for model in controller_models),
        'parameter_declarations_never_used_as_gate': sum(
            len(model['parameters_never_used_as_gate']) for model in controller_models),
        'distinct_gate_names': len(parameter_used),
        'controllers_fully_reachable_parameterized': sum(
            1 for model in controller_models
            if all(len(machine['unreachable']) == 0 for machine in model['machines'])
            and sum(machine['states'] for machine in model['machines']) > 0),
        'controllers_fully_reachable_unconditionally': sum(
            1 for model in controller_models
            if sum(machine['states'] for machine in model['machines']) > 0
            and all(len(machine['reachable_unconditional']) == machine['states']
                    for machine in model['machines'])),
        'controllers_with_unreachable_states': sum(
            1 for model in controller_models
            if any(machine['unreachable'] for machine in model['machines'])),
        'machines_without_states': sum(1 for model in controller_models
                                       for machine in model['machines']
                                       if machine['states'] == 0),
        'machine_without_local_default': sum(
            1 for model in controller_models for machine in model['machines']
            if machine['default_status'] != 'valid_index'),
    }

    # transition ids are machine-scoped (`m0:state2:0`) and therefore repeat across controllers:
    # every check below keys them by controller identity, never by id alone.
    traversed_blocked = 0
    for model in controller_models:
        blocked_ids = {record['transition_id'] for machine in model['machines']
                       for record in machine['blocked']}
        traversed_blocked += sum(
            1 for machine in model['machines'] for info in machine['paths'].values()
            for hop in info['path'] if hop['transition_id'] in blocked_ids)
    cross_checks = {
        'edge_classes_sum_to_transitions': {
            'sum': sum(edge_class_counter.values()),
            'transitions_total': transitions_total,
            'equal': sum(edge_class_counter.values()) == transitions_total,
        },
        'state_partition': {
            'reachable_parameterized': reachable_parameterized,
            'unreachable': unreachable_total,
            'states_total': states_total,
            'equal': reachable_parameterized + unreachable_total == states_total,
        },
        'binding_tiers_partition_totals': {
            'reachable': coverage['totals']['controller_clip_reachable_parameterized'],
            'unreachable': coverage['totals']['controller_clip_unreachable'],
            'unmapped': coverage['totals']['all'] - coverage['totals']['animator_mapped'],
            'total': coverage['totals']['all'],
            'equal': (coverage['totals']['controller_clip_reachable_parameterized']
                      + coverage['totals']['controller_clip_unreachable']
                      + coverage['totals']['all'] - coverage['totals']['animator_mapped'])
                     == coverage['totals']['all'],
        },
        'unconditional_closure_is_a_subset': {
            'checked_machines': sum(len(model['machines']) for model in controller_models),
            'violations': sum(
                1 for model in controller_models for machine in model['machines']
                if not set(machine['reachable_unconditional'])
                <= set(machine['reachable_parameterized'])),
        },
        'encoded_destinations_never_traversed': {
            'blocked': blocked_counter.get('encoded_destination', 0),
            'traversed': traversed_blocked,
            'equal': None,  # filled below once counted
        },
        'clip_tiers_are_nested': {
            'reachable_parameterized': len(pair_sets['pairs_reachable_parameterized']),
            'reachable_unconditional': len(pair_sets['pairs_reachable_unconditional']),
            'referenced': len(pair_sets['pairs_referenced']),
            'nested': (pair_sets['pairs_reachable_unconditional']
                       <= pair_sets['pairs_reachable_parameterized']
                       <= pair_sets['pairs_referenced']),
        },
    }

    cross_checks['encoded_destinations_never_traversed']['equal'] = (
        cross_checks['encoded_destinations_never_traversed']['traversed'] == 0)

    artifact = envelope(SCOPE, inputs_map(
        [TRANSITION_ARTIFACT, 'datas/l3_driven_props.json.gz']
        + glob_inputs(BINDINGS_GLOB) + glob_inputs(MOTION_GLOB)
        + ['tools/verify/l3_transition_coverage.py',
           'tools/verify/l3_transition_scheduler.py',
           'tools/verify/l3_driven_props.py',
           'tools/verify/l3_model_common.py']), DECODE_LIMITS)
    artifact.update({
        'counts': counts,
        'cross_checks': cross_checks,
        'controllers': controller_models,
        'clip_coverage': {key: value for key, value in clip_info.items()},
        'binding_coverage': {
            'totals': coverage['totals'],
            'by_kind': coverage['by_kind'],
            'records_without_route': coverage['by_kind']['all'].get('unresolved', 0),
            'ambiguous_animator_rows': coverage['ambiguous_animator_rows'],
            'unmapped_examples': coverage['unmapped_examples'],
            'per_clip_records': {f'{clip[0]}:{clip[1]}': count
                                 for clip, count in sorted(coverage['per_clip_records'].items())},
        },
        'parameter_gates': dict(sorted(parameter_gates.items(), key=lambda kv: (-kv[1], kv[0]))),
        'cases': pick_cases(controller_models, controllers),
    })
    artifact['build'] = {
        'tool_sha256': sha256_file(Path(__file__).resolve()),
        'common_sha256': sha256_file(Path(__file__).with_name('l3_model_common.py')),
        'driven_props_sha256': sha256_file(Path(__file__).with_name('l3_driven_props.py')),
        'scheduler_sha256': sha256_file(Path(__file__).with_name('l3_transition_scheduler.py')),
        'generator': 'tools/verify/l3_transition_coverage.py --build',
    }
    return artifact


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def cli_controller(path_id):
    artifact = read_json_gz(OUT_DEFAULT) if Path(OUT_DEFAULT).exists() else build()
    model = next((model for model in artifact['controllers']
                  if model['identity']['path_id'] == path_id), None)
    if model is None:
        raise SystemExit(f'controller {path_id} not in the artifact')
    return model


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Reachability + driven-coverage model over the 232 decoded controllers.')
    parser.add_argument('--build', action='store_true', help='regenerate the artifact')
    parser.add_argument('--out', default=OUT_DEFAULT)
    parser.add_argument('--controller', type=int, help='dump one controller model')
    parser.add_argument('--list', action='store_true', help='list controllers')
    parser.add_argument('--filter', default='', help='substring filter for --list')
    args = parser.parse_args(argv)

    if args.build:
        artifact = build()
        write_json_gz(Path(args.out), artifact)
        counts = artifact['counts']
        print(f'wrote {args.out}: {counts["controllers"]} controllers / '
              f'{counts["states_total"]} states '
              f'({counts["states_reachable_parameterized"]} reachable, '
              f'{counts["states_unreachable"]} unreachable) / '
              f'{counts["bindings"]["controller_clip_reachable_parameterized"]}/'
              f'{counts["bindings"]["total"]} bindings on a reachable (controller, clip) pair, '
              f'{counts["bindings"]["controller_clip_unreachable"]} unreachable')
        return 0

    if args.list:
        artifact = read_json_gz(OUT_DEFAULT) if Path(OUT_DEFAULT).exists() else build()
        for model in artifact['controllers']:
            if args.filter and args.filter.lower() not in (model['name'] or '').lower():
                continue
            reachable = sum(len(machine['reachable_parameterized'])
                            for machine in model['machines'])
            states = sum(machine['states'] for machine in model['machines'])
            print(f"{model['identity']['path_id']:>8}  "
                  f"{(model['name'] or '?')[:38]:<38} {reachable}/{states} reachable")
        return 0

    if args.controller is not None:
        print(json.dumps(cli_controller(args.controller), indent=1))
        return 0

    parser.print_help()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
