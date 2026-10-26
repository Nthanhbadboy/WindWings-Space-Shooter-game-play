#!/usr/bin/env python3
"""Transition scheduler + layer-blend *model* over the 232 decoded controllers.

Scope of the model
------------------
``build`` normalises every controller in ``datas/l3_animator_programs.json.gz``
into an explicit state graph (states, motion clips with durations, AnyState and
state transitions, conditions, exit time, duration, offset, interruption source,
encoded destinations) and emits ``datas/l3_transition_model.json.gz``.
``Scheduler`` then plays that graph forward for a caller-supplied parameter
script and reports *which state is selected* and *what the blend weights are*.

What the model does **not** claim
---------------------------------
* It is not Unity's Animator. The evaluation order, the exit-time/duration
  interpretation and trigger consumption are **declared model policies**
  (``scheduler_policy`` in the artifact) with ``proven: false``; the APK does not
  contain the engine implementation of these rules.
* Encoded destinations (``30001``/``30000``/``UINT_MAX``) are never mapped onto a
  local state index. A transition whose destination is encoded is reported as
  ``encoded_destination_not_local`` and is not taken.
* Script-driven ``Play``/``CrossFade`` calls are out of scope, as are layer
  weights of multi-layer controllers (every controller in the artifact has
  exactly one layer, measured below, not assumed).
* Nothing here renders, samples engine memory, or replays audio/callbacks.

The data only exercises a narrow slice of Animator features, and the artifact
says so with counts: all 468 transitions carry interruption source 0 (no
interruption), every condition is mode 1/2 (``If``/``IfNot``) with threshold 0,
so numeric-threshold scheduling is implemented but never exercised by the APK.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from l3_model_common import (ROOT, envelope, inputs_map, read_json_gz, sha256_file,
                             write_json_gz)

PROGRAM_ARTIFACT = 'datas/l3_animator_programs.json.gz'
MOTION_GLOB = 'datas/l3-scene-chains/motion-*.json.gz'
OUT_DEFAULT = 'datas/l3_transition_model.json.gz'

SCOPE = (
    'Transition scheduler and layer/state blending model over the 232 decoded Animator '
    'controllers (667 states, 343 AnyState + 125 state transitions, 377 parameters). '
    'Conditions, exit time, duration, offset, interruption source and encoded '
    'destinations are taken verbatim from the source artifact; the scheduling rules are '
    'declared model policies (engine order not proven by the APK). No script Play/'
    'CrossFade invocation, no callback/audio dispatch, no render.'
)

DECODE_LIMITS = [
    'engine_rules_not_in_apk: Animator evaluation order, exit-time/duration normalisation '
    'and trigger consumption are implemented as declared policies, each flagged '
    'proven=false',
    'encoded_destinations_kept: raw 30001/30000/4294967295 stay encoded selectors/exit '
    'markers; the model refuses to take such a transition instead of guessing an index',
    'script_invocation_out_of_scope: nothing here models Animator.Play/CrossFade/'
    'SetTrigger calls from MonoBehaviour bodies (that evidence lives in reports 100/103)',
    'single_layer_only: every controller in the artifact has exactly one layer, so '
    'multi-layer weighting is not exercised; count is measured, not assumed',
    'blend_is_weight_only: a crossfade is a linear weight between two states; parameter '
    'interpolation (e.g. blending Transform values) is the driven-props tool\'s business',
    'clip_speed_ranges_not_exercised: all 667 states have m_Speed = 1.0 in this artifact',
    'duration_source: state length is taken from the referenced clip\'s key range when '
    'resolvable; the blend-tree m_Duration differs for some states and is kept separately',
    'no_events_dispatch: clip events/AnimationEvents are recorded in the clip artifact, '
    'not fired by this model',
]

# Unity EditorCurveBinding/AnimatorConditionMode names are public API names. The
# artifact records which values actually appear so the mapping stays falsifiable.
CONDITION_MODES = {
    1: 'If', 2: 'IfNot', 3: 'Greater', 4: 'Less', 5: 'Equals', 6: 'NotEqual',
}
PARAMETER_TYPES = {
    1: 'Float', 3: 'Int', 4: 'Bool', 9: 'Trigger',
}
INTERRUPTION_SOURCES = {
    0: 'None', 1: 'Source', 2: 'Destination',
    3: 'SourceThenDestination', 4: 'DestinationThenSource',
}

SCHEDULER_POLICY = {
    'tick': 'caller supplies dt; state time advances by dt * state_speed, then candidates '
            'are evaluated for that instant',
    'evaluation_order': {
        'rule': 'AnyState transitions in serialized order first, then the current state\'s '
                'transitions in serialized order; the first eligible one is taken',
        'proven': False,
        'why': 'the APK stores the lists but not the engine\'s evaluation order',
    },
    'condition_modes': {str(k): v for k, v in CONDITION_MODES.items()},
    'parameter_types': {str(k): v for k, v in PARAMETER_TYPES.items()},
    'exit_time': {
        'rule': 'eligible when state_time >= threshold, where threshold = exit_time when '
                'has_fixed_duration else exit_time * state_length',
        'proven': False,
        'looping_note': 'state_time is not wrapped for looping states in this model',
    },
    'transition_duration': {
        'rule': 'blend seconds = transition_duration when has_fixed_duration else '
                'transition_duration * source_state_length',
        'proven': False,
    },
    'blend': {
        'rule': 'destination weight = clamp(elapsed / blend_seconds, 0, 1), source weight '
                '= 1 - destination weight; both states advance while blending',
        'zero_duration': 'instant switch (weight jumps to 1)',
        'proven': False,
    },
    'interruption': {
        'sources': {str(k): v for k, v in INTERRUPTION_SOURCES.items()},
        'rule': 'while a transition is running, a candidate with interruption source None '
                '(0) cannot replace it; other sources are allowed',
        'proven': False,
        'exercised_in_apk': False,
    },
    'trigger_consumption': {
        'rule': 'a Trigger parameter referenced by a taken transition is reset to false',
        'proven': False,
    },
    'self_transition': {
        'rule': 'a transition whose destination is the current state is skipped when '
                'm_CanTransitionToSelf is false',
        'proven': True,
        'why': 'the flag is serialized per transition; skipping is the literal reading',
    },
    'encoded_destination': {
        'rule': 'a transition whose destination is not a local state index is reported and '
                'never taken',
        'proven': True,
    },
    'engine_equivalence': False,
}


# --------------------------------------------------------------------------
# Loading / normalising
# --------------------------------------------------------------------------
def load_clip_lengths():
    """clip identity -> key-range length in seconds (authority for state length)."""
    out = {}
    for path in sorted(ROOT.glob(MOTION_GLOB)):
        for clip in read_json_gz(path):
            key = (clip['identity']['serialized_file'], int(clip['identity']['path_id']))
            start = float(clip.get('start') or 0.0)
            stop = float(clip.get('stop') or 0.0)
            out[key] = {
                'name': clip.get('name'),
                'length': max(0.0, stop - start),
                'start': start,
                'stop': stop,
                'loop': bool(clip.get('loop')),
                'sample_rate': clip.get('sample_rate'),
            }
    return out


def normalize_parameters(controller):
    params = []
    for param in controller.get('parameters') or []:
        raw = param.get('raw') or {}
        ptype = raw.get('m_Type')
        params.append({
            'names': param.get('names') or [],
            'name': (param.get('names') or [None])[0],
            'id': raw.get('m_ID'),
            'index': raw.get('m_Index'),
            'type': ptype,
            'type_class': PARAMETER_TYPES.get(ptype, f'unknown_{ptype}'),
            'default': param.get('default'),
            'default_status': param.get('default_status'),
            'default_storage': param.get('default_storage'),
        })
    return params


def normalize_condition(cond):
    raw = cond.get('raw') or {}
    mode = raw.get('m_ConditionMode')
    return {
        'parameter_names': cond.get('parameter_names') or [],
        'parameter_id': raw.get('m_EventID'),
        'mode': mode,
        'mode_name': CONDITION_MODES.get(mode, f'unknown_{mode}'),
        'threshold': raw.get('m_EventThreshold'),
        'exit_time': raw.get('m_ExitTime'),
    }


def normalize_transition(wrapper, scope, source_index, machine_index, seq):
    """Normalise one decoded transition wrapper (raw + resolved destination)."""
    raw = wrapper.get('raw') or {}
    destination = wrapper.get('destination_index', raw.get('m_Destination'))
    dest_status = wrapper.get('destination_status')
    if dest_status is None:
        dest_status = ('local_state_index'
                       if isinstance(destination, int) and destination < 1000
                       else 'encoded_selector_or_exit_not_local_index')
    conditions = wrapper.get('conditions')
    if conditions is None:
        conditions = [{'raw': c} for c in raw.get('m_ConditionConstantArray') or []]
    source_tag = 'any' if scope == 'any' else f'state{source_index}'
    if scope == 'selector':
        source_tag = 'selector'
    return {
        'id': f'm{machine_index}:{source_tag}:{seq}',
        'scope': scope,
        'source_state_index': source_index,
        'destination': {'raw': destination, 'index': destination,
                        'status': dest_status},
        'conditions': [normalize_condition(c) for c in conditions],
        'has_exit_time': bool(raw.get('m_HasExitTime')),
        'exit_time': raw.get('m_ExitTime'),
        'transition_duration': raw.get('m_TransitionDuration'),
        'transition_offset': raw.get('m_TransitionOffset'),
        'has_fixed_duration': bool(raw.get('m_HasFixedDuration')),
        'interruption_source': raw.get('m_InterruptionSource'),
        'ordered_interruption': raw.get('m_OrderedInterruption'),
        'can_transition_to_self': raw.get('m_CanTransitionToSelf'),
    }


def normalize_controller(controller, clip_lengths):
    params = normalize_parameters(controller)
    machines = []
    for machine in controller.get('machines') or []:
        machine_index = machine.get('machine_index', 0)
        states = []
        for state in machine.get('states') or []:
            raw = state.get('raw') or {}
            motion = []
            for tree in state.get('trees') or []:
                for node in tree.get('nodes') or []:
                    clip = node.get('clip')
                    entry = {
                        'clip': clip,
                        'node_duration': (node.get('raw') or {}).get('m_Duration'),
                        'node_cycle_offset': (node.get('raw') or {}).get('m_CycleOffset'),
                        'clip_status': node.get('clip_status'),
                    }
                    if clip:
                        key = (clip['serialized_file'], int(clip['path_id']))
                        info = clip_lengths.get(key)
                        entry['clip_resolved'] = info is not None
                        entry['clip_length'] = info['length'] if info else None
                        entry['clip_name'] = info['name'] if info else None
                    else:
                        entry['clip_resolved'] = False
                        entry['clip_length'] = None
                        entry['clip_name'] = None
                    motion.append(entry)
            transitions = []
            for seq, trans in enumerate(state.get('transitions') or []):
                transitions.append(normalize_transition(
                    trans, 'state', state['state_index'], machine_index, seq))
            states.append({
                'state_index': state['state_index'],
                'names': state.get('name_candidates') or [],
                'paths': state.get('path_candidates') or [],
                'speed': raw.get('m_Speed'),
                'loop': bool(raw.get('m_Loop')),
                'write_default_values': raw.get('m_WriteDefaultValues'),
                'mirror': raw.get('m_Mirror'),
                'motion': motion,
                'transitions': transitions,
            })
        any_transitions = []
        for seq, trans in enumerate(machine.get('any_state_transitions') or []):
            any_transitions.append(normalize_transition(
                trans, 'any', None, machine_index, seq))
        selectors = []
        for selector in machine.get('selectors') or []:
            sraw = selector.get('raw') or {}
            transitions = []
            for seq, trans in enumerate(selector.get('transitions') or []):
                transitions.append(normalize_transition(
                    trans, 'selector', None, machine_index, seq))
            selectors.append({
                'is_entry': sraw.get('m_IsEntry'),
                'full_path_id': sraw.get('m_FullPathID'),
                'transitions': transitions,
            })
        machines.append({
            'machine_index': machine_index,
            'default_state_index': machine.get('default_state_index'),
            'default_status': machine.get('default_status'),
            'states': states,
            'any_state_transitions': any_transitions,
            'selectors': selectors,
        })
    return {
        'identity': controller['identity'],
        'name': controller['name'],
        'raw_object_sha256': controller.get('raw_object_sha256'),
        'layer_count': len(controller.get('layers') or []),
        'layers': controller.get('layers') or [],
        'parameters': params,
        'machines': machines,
    }


def all_transitions(controller_model):
    for machine in controller_model['machines']:
        for state in machine['states']:
            for trans in state['transitions']:
                yield trans
        for trans in machine['any_state_transitions']:
            yield trans
        for selector in machine['selectors']:
            for trans in selector['transitions']:
                yield trans


def count_model(models):
    states = sum(len(m['states']) for c in models for m in c['machines'])
    any_t = sum(len(m['any_state_transitions']) for c in models for m in c['machines'])
    state_t = sum(len(s['transitions']) for c in models for m in c['machines']
                  for s in m['states'])
    selectors = sum(len(m['selectors']) for c in models for m in c['machines'])
    selector_t = sum(len(s['transitions']) for c in models for m in c['machines']
                     for s in m['selectors'])
    params = sum(len(c['parameters']) for c in models)
    conditions = sum(len(t['conditions']) for c in models for t in all_transitions(c))
    return {
        'controllers': len(models),
        'machines': sum(len(c['machines']) for c in models),
        'states': states,
        'any_transitions': any_t,
        'state_transitions': state_t,
        'selectors': selectors,
        'selector_transitions': selector_t,
        'parameters': params,
        'conditions': conditions,
        'layers_total': sum(c['layer_count'] for c in models),
        'controllers_with_one_layer': sum(1 for c in models if c['layer_count'] == 1),
        'empty_machines': sum(1 for c in models for m in c['machines'] if not m['states']),
        'states_without_motion': sum(1 for c in models for m in c['machines']
                                     for s in m['states'] if not s['motion']),
        'motion_leaves': sum(len(s['motion']) for c in models for m in c['machines']
                             for s in m['states']),
        'motion_leaves_resolved': sum(1 for c in models for m in c['machines']
                                      for s in m['states'] for mv in s['motion']
                                      if mv['clip_resolved']),
        'states_looping': sum(1 for c in models for m in c['machines']
                               for s in m['states'] if s['loop']),
        'states_speed_not_one': sum(1 for c in models for m in c['machines']
                                    for s in m['states'] if s['speed'] != 1.0),
        'parameter_types': _counter_kv(p['type_class'] for c in models
                                       for p in c['parameters']),
        'condition_modes': _counter_kv(cond['mode'] for c in models
                                       for trans in all_transitions(c)
                                       for cond in trans['conditions']),
        'condition_thresholds': _counter_kv(th for c in models for tr in all_transitions(c)
                                            for th in [x['threshold'] for x in tr['conditions']]),
        'transitions_with_conditions': sum(1 for c in models for t in all_transitions(c)
                                           if t['conditions']),
        'transitions_without_conditions': sum(1 for c in models for t in all_transitions(c)
                                              if not t['conditions']),
        'transitions_with_exit_time': sum(1 for c in models for t in all_transitions(c)
                                          if t['has_exit_time']),
        'transitions_without_exit_time': sum(1 for c in models for t in all_transitions(c)
                                             if not t['has_exit_time']),
        'transitions_with_duration': sum(1 for c in models for t in all_transitions(c)
                                         if (t['transition_duration'] or 0) > 0),
        'transitions_fixed_duration': sum(1 for c in models for t in all_transitions(c)
                                          if t['has_fixed_duration']),
        'transitions_self_allowed': sum(1 for c in models for t in all_transitions(c)
                                        if t['can_transition_to_self']),
        # only serialized values are keys here; a transition that carries no
        # m_InterruptionSource at all is counted separately instead of being labelled
        # "null" (which would read as an unmeasured source)
        'interruption_sources': {k: v for k, v in _counter_kv(
            t['interruption_source'] for c in models for t in all_transitions(c)
            if t['interruption_source'] is not None).items()},
        'interruption_source_absent': sum(
            1 for c in models for t in all_transitions(c)
            if t['interruption_source'] is None),
        'interruption_source_absent_scope': _counter_kv(
            t['scope'] for c in models for t in all_transitions(c)
            if t['interruption_source'] is None),
        'encoded_destinations': _counter_kv(
            t['destination']['raw'] for c in models for t in all_transitions(c)
            if t['destination']['status'] != 'local_state_index'),
        'transitions_into_missing_state': sum(
            1 for c in models for t in all_transitions(c)
            if t['destination']['status'] == 'local_state_index'
            and not any(s['state_index'] == t['destination']['index']
                        for m in c['machines'] for s in m['states'])),
    }


def _counter_kv(values):
    out = {}
    for value in values:
        key = 'null' if value is None else str(value)
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))


# --------------------------------------------------------------------------
# Scheduler
# --------------------------------------------------------------------------
class Scheduler:
    """Play one controller's state graph forward under a declared policy."""

    def __init__(self, controller, policy=None):
        self.controller = controller
        self.policy = policy or SCHEDULER_POLICY
        machine = controller['machines'][0]
        self.machine = machine
        self.states = {s['state_index']: s for s in machine['states']}
        self.params = {}
        self.param_types = {}
        for param in controller['parameters']:
            name = param['name']
            if name is None:
                continue
            self.params[name] = param['default']
            self.param_types[name] = param['type_class']
        self.state = machine['default_state_index']
        self.state_time = 0.0
        self.blend = None
        self.time = 0.0
        self.events = []
        self.blocked = []
        self.taken = []

    # -- parameters -------------------------------------------------------
    def set(self, name, value):
        if name not in self.params:
            raise KeyError(f'parameter {name!r} is not declared on this controller')
        if self.param_types[name] == 'Trigger':
            raise ValueError(f'{name!r} is a Trigger; use set_trigger()')
        self.params[name] = value

    def set_trigger(self, name):
        if self.params.get(name) is None and name not in self.params:
            raise KeyError(f'parameter {name!r} is not declared on this controller')
        self.params[name] = True

    # -- helpers ----------------------------------------------------------
    def state_length(self, state_index):
        state = self.states.get(state_index)
        if not state:
            return 0.0
        for motion in state['motion']:
            if motion.get('clip_length') is not None:
                return float(motion['clip_length'])
        for motion in state['motion']:
            if motion.get('node_duration') is not None:
                return float(motion['node_duration'])
        return 0.0

    def normalized_time(self):
        length = self.state_length(self.state)
        if length <= 0:
            return 0.0
        return self.state_time / length

    def _condition_value(self, cond):
        for name in cond['parameter_names']:
            if name in self.params:
                return self.params[name], None
        return None, 'parameter_not_declared'

    def _condition_holds(self, cond):
        value, problem = self._condition_value(cond)
        if problem:
            return False, problem
        mode = cond['mode']
        threshold = cond['threshold'] or 0.0
        if mode == 1:
            return bool(value), None
        if mode == 2:
            return not bool(value), None
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False, f'non_numeric_parameter_for_mode_{mode}'
        if mode == 3:
            return value > threshold, None
        if mode == 4:
            return value < threshold, None
        if mode == 5:
            return value == threshold, None
        if mode == 6:
            return value != threshold, None
        return False, f'unsupported_condition_mode_{mode}'

    def _eval_transition(self, trans):
        """(eligible, reasons) for one transition at the current instant."""
        reasons = []
        dest = trans['destination']
        if dest['status'] != 'local_state_index':
            return False, ['encoded_destination_not_local']
        if dest['index'] not in self.states:
            return False, ['destination_state_missing']
        if dest['index'] == self.state and not trans['can_transition_to_self']:
            return False, ['self_transition_disallowed']
        if self.blend and trans['interruption_source'] == 0:
            return False, ['blocked_by_running_transition_no_interruption']
        for cond in trans['conditions']:
            holds, problem = self._condition_holds(cond)
            if problem:
                return False, [problem]
            if not holds:
                return False, ['condition_false']
            reasons.append(f"condition:{cond['mode_name']}:"
                           f"{','.join(cond['parameter_names']) or cond['parameter_id']}")
        if trans['has_exit_time']:
            source_length = self.state_length(self.state)
            raw_exit = trans['exit_time'] or 0.0
            threshold = raw_exit if trans['has_fixed_duration'] else raw_exit * source_length
            if self.state_time + 1e-9 < threshold:
                return False, ['exit_time_not_reached']
            reasons.append(f'exit_time:{threshold}')
        return True, reasons

    def _candidates(self):
        out = []
        for trans in self.machine['any_state_transitions']:
            out.append(('any', trans))
        for trans in self.states[self.state]['transitions']:
            out.append(('state', trans))
        return out

    def _take(self, trans, via):
        source = self.state
        dest = trans['destination']['index']
        source_length = self.state_length(source)
        if trans['has_fixed_duration']:
            blend_seconds = float(trans['transition_duration'] or 0.0)
        else:
            blend_seconds = float(trans['transition_duration'] or 0.0) * source_length
        offset = float(trans['transition_offset'] or 0.0) * self.state_length(dest)
        # consume triggers referenced by the taken transition
        consumed = []
        for cond in trans['conditions']:
            for name in cond['parameter_names']:
                if self.param_types.get(name) == 'Trigger' and self.params.get(name):
                    self.params[name] = False
                    consumed.append(name)
        event = {
            't': self.time,
            'transition_id': trans['id'],
            'via': via,
            'from_state': source,
            'to_state': dest,
            'blend_seconds': blend_seconds,
            'transition_offset_seconds': offset,
            'consumed_triggers': consumed,
            'state_time_at_take': self.state_time,
        }
        self.taken.append(event)
        if blend_seconds <= 0:
            self.state = dest
            self.state_time = offset
            self.blend = None
            event['applied'] = 'instant'
        else:
            self.blend = {
                'from_state': source,
                'to_state': dest,
                'elapsed': 0.0,
                'duration': blend_seconds,
                'from_time_start': self.state_time,
                'to_time_start': offset,
                'transition_id': trans['id'],
            }
            event['applied'] = 'blend'
        self.events.append(event)

    def tick(self, dt):
        """Advance by dt, then evaluate candidates (policy: advance then evaluate)."""
        if dt < 0:
            raise ValueError('dt must be >= 0')
        self.time += dt
        if self.blend:
            self.blend['elapsed'] += dt
            self.state_time += dt  # source state keeps advancing while blending
            if self.blend['elapsed'] + 1e-12 >= self.blend['duration']:
                self.state = self.blend['to_state']
                self.state_time = self.blend['to_time_start'] + self.blend['elapsed']
                self.blend = None
        else:
            self.state_time += dt
        for via, trans in self._candidates():
            eligible, reasons = self._eval_transition(trans)
            if eligible:
                self._take(trans, via)
                return
            self.blocked.append({'t': self.time, 'transition_id': trans['id'],
                                 'reasons': reasons})

    def snapshot(self):
        if self.blend:
            progress = self.blend['elapsed'] / self.blend['duration'] \
                if self.blend['duration'] else 1.0
            progress = min(1.0, max(0.0, progress))
            weights = {str(self.blend['to_state']): progress,
                       str(self.blend['from_state']): 1.0 - progress}
        else:
            progress = 0.0
            weights = {str(self.state): 1.0}
        state = self.states.get(self.state)
        return {
            't': self.time,
            'state': self.state,
            'state_name': (state['names'] or [None])[0] if state else None,
            'state_time': self.state_time,
            'state_length': self.state_length(self.state),
            'normalized_time': self.normalized_time(),
            'blend': {
                'active': bool(self.blend),
                'progress': progress,
                'weights': weights,
                'transition_id': self.blend['transition_id'] if self.blend else None,
            },
            'parameters': dict(self.params),
        }

    # -- convenience ------------------------------------------------------
    def run(self, dt, steps, script=None):
        """Advance ``steps`` ticks of ``dt`` applying a time-indexed script."""
        script = sorted(script or [], key=lambda e: e['t'])
        timeline = []
        cursor = 0
        for step in range(steps + 1):
            while cursor < len(script) and script[cursor]['t'] <= self.time + 1e-12:
                entry = script[cursor]
                for name, value in (entry.get('set') or {}).items():
                    self.set(name, value)
                for name in entry.get('trigger') or []:
                    self.set_trigger(name)
                timeline.append({'t': self.time, 'applied_script': entry})
                cursor += 1
            timeline.append(self.snapshot())
            if step < steps:
                self.tick(dt)
        return timeline


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------
CASE_SPECS = [
    {
        'name': 'bb_36002_auto_advance',
        'controller_path_id': 1910,
        'what': 'no parameters: three looping states chained by exit time only; one '
                'transition uses a normalised 0.2 duration on a 9.0 s clip',
        'script': [],
        'dt': 1 / 60,
        'steps': 60 * 40,
        'sample_every': 120,
    },
    {
        'name': 'blt_88011_trigger_then_blend',
        'controller_path_id': 1940,
        'what': 'AnyState trigger Attack -> Attack state, then exit-time transition with a '
                'fixed 0.5 s blend into an Idle state whose clip has zero length',
        'script': [{'t': 0.05, 'trigger': ['Attack']}],
        'dt': 1 / 60,
        'steps': 60 * 3,
        'sample_every': 6,
    },
    {
        'name': 'box_gift_triggers',
        'controller_path_id': 1792,
        'what': 'three AnyState trigger transitions with zero duration: instant switches '
                'between Appear/Flick/Change (the clips that drive RectTransform data)',
        'script': [{'t': 0.1, 'trigger': ['Flick']},
                   {'t': 0.6, 'trigger': ['Change']},
                   {'t': 1.0, 'trigger': ['Pop']}],
        'dt': 1 / 60,
        'steps': 60 * 2,
        'sample_every': 10,
    },
]


def build_cases(models, clip_lengths):
    by_id = {int(c['identity']['path_id']): c for c in models}
    cases = []
    for spec in CASE_SPECS:
        controller = by_id.get(spec['controller_path_id'])
        if controller is None:
            cases.append({'name': spec['name'], 'status': 'controller_not_found'})
            continue
        sched = Scheduler(controller)
        timeline = sched.run(spec['dt'], spec['steps'], spec['script'])
        samples = [row for row in timeline
                   if 'state' in row and isinstance(row.get('t'), float)
                   and int(round(row['t'] / spec['dt'])) % spec['sample_every'] == 0]
        cases.append({
            'name': spec['name'],
            'what': spec['what'],
            'controller': controller['identity'],
            'controller_name': controller['name'],
            'dt': spec['dt'],
            'steps': spec['steps'],
            'script': spec['script'],
            'parameters_declared': [
                {'name': p['name'], 'type': p['type_class'], 'default': p['default']}
                for p in controller['parameters']],
            'state_lengths': {str(idx): sched.state_length(idx)
                              for idx in sorted(sched.states)},
            'transitions_taken': sched.taken,
            'timeline_sampled': [{'t': s['t'], 'state': s['state'],
                                  'state_time': s['state_time'],
                                  'normalized_time': s['normalized_time'],
                                  'blend_active': s['blend']['active'],
                                  'blend_progress': s['blend']['progress'],
                                  'weights': s['blend']['weights']}
                                 for s in samples],
            'final': sched.snapshot(),
            'blocked_sample': sched.blocked[:10],
            'blocked_total': len(sched.blocked),
        })
    return cases


def build():
    programs = read_json_gz(ROOT / PROGRAM_ARTIFACT)
    clip_lengths = load_clip_lengths()
    models = [normalize_controller(c, clip_lengths) for c in programs['controllers']]
    counts = count_model(models)

    source_counts = programs.get('counts') or {}
    cross_check = {}
    for key, source_key in (('controllers', 'controllers'), ('states', 'states'),
                            ('any_transitions', 'any_transitions'),
                            ('state_transitions', 'state_transitions'),
                            ('parameters', 'parameters'),
                            ('motion_leaves', 'motion_leaves')):
        cross_check[key] = {
            'recomputed': counts[key],
            'source_artifact': source_counts.get(source_key),
            'equal': counts[key] == source_counts.get(source_key),
        }
    artifact = envelope(SCOPE, inputs_map([
        PROGRAM_ARTIFACT,
        'datas/l3-scene-chains/motion-000.json.gz',
        'tools/verify/l3_transition_scheduler.py',
        'tools/verify/l3_model_common.py',
    ]), DECODE_LIMITS)
    artifact.update({
        'scheduler_policy': SCHEDULER_POLICY,
        'counts': counts,
        'cross_check_against_source_artifact': cross_check,
        'clip_lengths_resolved': {
            'clips_in_motion_artifact': len(clip_lengths),
            'leaves_resolved': counts['motion_leaves_resolved'],
            'leaves_unresolved': counts['motion_leaves'] - counts['motion_leaves_resolved'],
        },
        'cases': build_cases(models, clip_lengths),
        'controllers': models,
    })
    artifact['build'] = {
        'tool_sha256': sha256_file(Path(__file__).resolve()),
        'common_sha256': sha256_file(Path(__file__).with_name('l3_model_common.py')),
        'generator': 'tools/verify/l3_transition_scheduler.py --build',
    }
    return artifact


def load_model(path=None):
    return read_json_gz(ROOT / (path or OUT_DEFAULT))


def scheduler_for(path_id, artifact=None):
    artifact = artifact or load_model()
    for controller in artifact['controllers']:
        if int(controller['identity']['path_id']) == int(path_id):
            return Scheduler(controller, artifact['scheduler_policy'])
    raise SystemExit(f'controller {path_id} is not in the model')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--build', action='store_true')
    ap.add_argument('--out', default=OUT_DEFAULT)
    ap.add_argument('--controller', type=int)
    ap.add_argument('--duration', type=float, default=2.0)
    ap.add_argument('--dt', type=float, default=1 / 60)
    ap.add_argument('--script', default='[]',
                    help='JSON list of {"t":s,"set":{...},"trigger":[...]}')
    ap.add_argument('--list', action='store_true')
    args = ap.parse_args(argv)

    if args.build:
        artifact = build()
        write_json_gz(ROOT / args.out, artifact)
        counts = artifact['counts']
        print(f"wrote {args.out}: {counts['controllers']} controllers / "
              f"{counts['states']} states / {counts['any_transitions']} any + "
              f"{counts['state_transitions']} state transitions / "
              f"{counts['conditions']} conditions")
        return 0

    if args.list:
        artifact = load_model()
        for controller in artifact['controllers']:
            states = sum(len(m['states']) for m in controller['machines'])
            print(controller['identity']['path_id'], controller['name'],
                  f'{states} states, {len(controller["parameters"])} params')
        return 0

    if args.controller is None:
        ap.error('one of --build/--list/--controller is required')
    sched = scheduler_for(args.controller)
    script = json.loads(args.script)
    steps = int(round(args.duration / args.dt))
    timeline = sched.run(args.dt, steps, script)
    out = {'controller': sched.controller['identity'],
           'policy_proven': {k: v.get('proven') for k, v in
                             sched.policy.items() if isinstance(v, dict)},
           'transitions_taken': sched.taken,
           'final': sched.snapshot(),
           'timeline': [row for row in timeline if 'state' in row]}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
