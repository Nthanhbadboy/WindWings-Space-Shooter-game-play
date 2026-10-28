#!/usr/bin/env python3
"""Bounded particle *model* built from the 954 scoped APK ParticleSystems.

What this tool is
-----------------
1. ``build``: joins the three artifact sources that actually carry numeric
   particle data and emits ``datas/l3_particle_model.json.gz`` —
   * ``datas/l3-visual-surface/particles-*.json.gz`` (954 scoped systems:
     identity, module enablement, renderer refs, GameObject, properties),
   * ``reverse-engineering/raw/typetrees/native-types.jsonl.gz`` (the only place
     that carries the decoded MinMaxCurve **constants** per module),
   * ``datas/particle_systems.csv.gz`` (prefab root per system path_id).
2. ``sim``: a headless, deterministic emitter/particle model over those
   constants. It emits a state as a function of ``t``: emission schedule,
   per-particle age/lifetime/size/rotation/position, plus an explicit list of
   what it does *not* model.

What this tool is not
---------------------
* Not Unity's particle simulation and not a render. The game's ParticleSystem is
  native engine code; nothing here executes engine bytes.
* Not curve-exact: the export carries ``<curve>.scalar``/``.minScalar`` only.
  Curve keys, gradients, burst tables, noise fields, collision planes and
  ``inWorldSpace`` flags are **absent** from every artifact in this repo, so
  those stays are reported as absent instead of being invented. A CI-visible
  count of how many systems each absence touches lives in ``counts``.
* The random sequence is a documented splitmix64 hash, *not* Unity's generator.

CLI
---
    python3 -m tools.verify.l3_particle_model --build
    python3 -m tools.verify.l3_particle_model --system 4783 --times 0,0.25,1 --seed 7
    python3 -m tools.verify.l3_particle_model --list --filter Box
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from l3_model_common import (ROOT, envelope, fin, inputs_map, lerp, minmax_pair,
                             read_json_gz, sha256_file, uniform01, write_json_gz)

SCOPED_GLOB = 'datas/l3-visual-surface/particles-*.json.gz'
NATIVE_TYPES = 'reverse-engineering/raw/typetrees/native-types.jsonl.gz'
PREFAB_CSV = 'datas/particle_systems.csv.gz'
OUT_DEFAULT = 'datas/l3_particle_model.json.gz'

MODULE_ORDER = [
    'InitialModule', 'EmissionModule', 'ShapeModule', 'VelocityModule',
    'SizeModule', 'RotationModule', 'ColorModule', 'ColorBySpeedModule',
    'SizeBySpeedModule', 'RotationBySpeedModule', 'ForceModule',
    'ExternalForcesModule', 'ClampVelocityModule', 'NoiseModule',
    'InheritVelocityModule', 'LifetimeByEmitterSpeedModule', 'CollisionModule',
    'TriggerModule', 'SubModule', 'LightsModule', 'TrailModule',
    'CustomDataModule', 'UVModule',
]

# Modules whose numeric payload is a curve or a structured gradient in the APK.
# For these the export only carries a constant scalar (or nothing at all).
CURVE_MODULES = {
    'SizeModule', 'ColorModule', 'ColorBySpeedModule', 'SizeBySpeedModule',
    'RotationBySpeedModule', 'RotationModule', 'VelocityModule', 'ForceModule',
    'NoiseModule', 'ClampVelocityModule', 'InheritVelocityModule',
    'LifetimeByEmitterSpeedModule', 'ExternalForcesModule', 'TrailModule',
    'LightsModule', 'CustomDataModule', 'UVModule', 'CollisionModule',
    'InitialModule', 'EmissionModule',
}

SCOPE = (
    'Bounded particle model over the 954 ParticleSystems whose GameObject sits in the '
    'L3 visual-surface scope. Emission/velocity/size/rotation are modelled from the '
    'decoded serialized *constants*; curve keys, gradients, burst tables, noise fields '
    'and collision planes are absent from every artifact in this repo and are reported '
    'as absent. Deterministic model PRNG (splitmix64), not Unity RNG. No simulation of '
    'engine bytes, no particle vertices, no render.'
)

DECODE_LIMITS = [
    'curve_keys_absent: export carries <curve>.scalar and .minScalar only; every '
    'over-lifetime/over-speed curve is modelled as its constant scalar',
    'gradient_absent: ColorModule/ColorBySpeed gradients are not exported, so particle '
    'colour and alpha over lifetime are not modelled (alpha reported as 1.0 with flag)',
    'bursts_not_exported: only EmissionModule.m_BurstCount survives; burst time/count/'
    'cycle tables are absent, so burst emission is not scheduled',
    'shape_enums_not_interpreted: ShapeModule.type is exported as a raw integer; the '
    'direction model uses the declared cone angle around a declared local axis only',
    'local_vs_world_flags_absent: VelocityModule/ForceModule inWorldSpace flags are '
    'exported as key names without values; the model treats them as emitter-local',
    'engine_constants_external: gravity vector, drag reference and timescale are caller '
    'inputs; the model never substitutes an engine default silently',
    'random_sequence_not_engine: splitmix64(seed, stream, particle_index) is our own '
    'generator; per-particle values are reproducible but not engine-equal',
    'max_particles_policy: when the alive set exceeds InitialModule.maxNumParticles the '
    'model drops the oldest particles (declared policy, ring-buffer modes not modelled)',
    'sub_emitters_not_modelled: SubModule/SubEmitters are counted but not simulated',
]


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------
def load_scoped_systems():
    """954 scoped ParticleSystem records with module enablement + refs."""
    out = []
    for path in sorted(ROOT.glob(SCOPED_GLOB)):
        out.extend(read_json_gz(path))
    return out


def load_native_constants(path=NATIVE_TYPES):
    """path_id -> flat serialized ParticleSystem record (4845 in the export)."""
    import gzip
    table = {}
    with gzip.open(ROOT / path, 'rt', encoding='utf-8') as fh:
        for line in fh:
            rec = json.loads(line)
            if rec.get('type') != 'ParticleSystem':
                continue
            table[int(rec['path_id'])] = rec
    return table


def load_prefab_roots(path=PREFAB_CSV):
    import gzip
    table = {}
    with gzip.open(ROOT / path, 'rt', encoding='utf-8', newline='') as fh:
        for row in csv.DictReader(fh):
            table[int(row['particle_path_id'])] = {
                'prefab_root': row['prefab_root'],
                'length_in_sec_csv': float(row['length_in_sec']),
                'looping_csv': row['looping'] == 'True',
            }
    return table


def split_constants(record):
    """``Module.component.scalar``/``.minScalar`` -> {dotted_component: pair}.

    The export flattens every MinMaxCurve to its two constants; the curve mode is
    not exported, so no key here may be read as "the curve is constant".
    """
    pairs = {}
    for key, value in record.items():
        if key.endswith('.scalar'):
            pairs.setdefault(key[:-len('.scalar')], {})['scalar'] = value
        elif key.endswith('.minScalar'):
            pairs.setdefault(key[:-len('.minScalar')], {})['minScalar'] = value
    return pairs


def curve_pair(scalars, dotted):
    """MinMaxCurve pair for ``Module.component`` (dotted path without suffix)."""
    bucket = scalars.get(dotted) or {}
    scal = bucket.get('scalar')
    mini = bucket.get('minScalar')
    if scal is None or mini is None:
        return {'value': None, 'min_scalar': None, 'bounds': None, 'mode': 'absent',
                'mode_proven': False, 'source_key': dotted}
    pair = minmax_pair(scal, mini)
    pair['source_key'] = dotted
    return pair


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------
def build_system_model(scoped, native, prefab):
    """One model record per scoped ParticleSystem (no estimates, no fills)."""
    pid = int(scoped['identity']['path_id'])
    props = scoped.get('properties') or {}
    raw_native = native.get(pid)
    enabled = {m['field']: m['enabled'] for m in scoped.get('modules') or []
               if m['field'] in MODULE_ORDER}

    flags = ['curve_keys_absent']
    if not raw_native:
        flags.append('native_constants_missing')
        scalars, module_dicts = {}, {}
    else:
        scalars = split_constants(raw_native)
        module_dicts = {m: (raw_native.get(m) or {}) for m in MODULE_ORDER}

    def module_enabled(name):
        return bool(enabled.get(name)) if name in enabled else bool(
            (module_dicts.get(name) or {}).get('enabled'))

    initial = {
        'start_lifetime': curve_pair(scalars, 'InitialModule.startLifetime'),
        'start_speed': curve_pair(scalars, 'InitialModule.startSpeed'),
        'start_size': curve_pair(scalars, 'InitialModule.startSize'),
        'start_size_y': curve_pair(scalars, 'InitialModule.startSizeY'),
        'start_size_z': curve_pair(scalars, 'InitialModule.startSizeZ'),
        'start_rotation': curve_pair(scalars, 'InitialModule.startRotation'),
        'start_rotation_x': curve_pair(scalars, 'InitialModule.startRotationX'),
        'start_rotation_y': curve_pair(scalars, 'InitialModule.startRotationY'),
        'gravity_modifier': curve_pair(scalars, 'InitialModule.gravityModifier'),
        'max_particles': (module_dicts.get('InitialModule') or {}).get('maxNumParticles'),
        'size_3d': (module_dicts.get('InitialModule') or {}).get('size3D'),
        'rotation_3d': (module_dicts.get('InitialModule') or {}).get('rotation3D'),
        'randomize_rotation_direction':
            (module_dicts.get('InitialModule') or {}).get('randomizeRotationDirection'),
        'start_color': 'gradient_not_exported',
    }

    emission = {
        'rate_over_time': curve_pair(scalars, 'EmissionModule.rateOverTime'),
        'rate_over_distance': curve_pair(scalars, 'EmissionModule.rateOverDistance'),
        'burst_count': (module_dicts.get('EmissionModule') or {}).get('m_BurstCount'),
        'bursts': 'not_exported',
    }
    if (emission['burst_count'] or 0) > 0:
        flags.append('bursts_not_exported')

    shape_raw = module_dicts.get('ShapeModule') or {}
    shape = {
        'enabled': module_enabled('ShapeModule'),
        'type_raw': shape_raw.get('type'),
        'type_interpreted': False,
        'angle': shape_raw.get('angle'),
        'radius': shape_raw.get('radius'),
        'length': shape_raw.get('length'),
        'radius_thickness': shape_raw.get('radiusThickness'),
        'donut_radius': shape_raw.get('donutRadius'),
        'placement_mode': shape_raw.get('placementMode'),
        'random_direction_amount': shape_raw.get('randomDirectionAmount'),
        'spherical_direction_amount': shape_raw.get('sphericalDirectionAmount'),
        'random_position_amount': shape_raw.get('randomPositionAmount'),
        'scale': shape_raw.get('m_Scale'),
        'rotation': shape_raw.get('m_Rotation'),
        'status': 'direction_model_uses_declared_cone_angle_only',
    }

    velocity = {
        'enabled': module_enabled('VelocityModule'),
        'x': curve_pair(scalars, 'VelocityModule.x'),
        'y': curve_pair(scalars, 'VelocityModule.y'),
        'z': curve_pair(scalars, 'VelocityModule.z'),
        'radial': curve_pair(scalars, 'VelocityModule.radial'),
        'speed_modifier': curve_pair(scalars, 'VelocityModule.speedModifier'),
        'orbital_x': curve_pair(scalars, 'VelocityModule.orbitalX'),
        'orbital_y': curve_pair(scalars, 'VelocityModule.orbitalY'),
        'orbital_z': curve_pair(scalars, 'VelocityModule.orbitalZ'),
        'orbital_offset_x': curve_pair(scalars, 'VelocityModule.orbitalOffsetX'),
        'orbital_offset_y': curve_pair(scalars, 'VelocityModule.orbitalOffsetY'),
        'orbital_offset_z': curve_pair(scalars, 'VelocityModule.orbitalOffsetZ'),
        'space': 'modelled_as_emitter_local (inWorldSpace flag absent)',
    }
    if velocity['enabled']:
        flags.append('local_vs_world_flags_absent')

    size_over_life = {
        'enabled': module_enabled('SizeModule'),
        'curve': curve_pair(scalars, 'SizeModule.curve'),
        'y': curve_pair(scalars, 'SizeModule.y'),
        'z': curve_pair(scalars, 'SizeModule.z'),
        'separate_axes': (module_dicts.get('SizeModule') or {}).get('separateAxes'),
        'status': 'constant_only_curve_keys_absent',
    }
    rotation_over_life = {
        'enabled': module_enabled('RotationModule'),
        'curve': curve_pair(scalars, 'RotationModule.curve'),
        'x': curve_pair(scalars, 'RotationModule.x'),
        'y': curve_pair(scalars, 'RotationModule.y'),
        'status': 'constant_only_curve_keys_absent_units_unproven',
    }
    color_over_life = {
        'enabled': module_enabled('ColorModule'),
        'gradient': 'not_exported',
        'status': 'color_over_lifetime_not_modelled',
    }
    if color_over_life['enabled'] or module_enabled('ColorBySpeedModule'):
        flags.append('gradient_absent')

    forces = {
        'enabled': module_enabled('ForceModule'),
        'x': curve_pair(scalars, 'ForceModule.x'),
        'y': curve_pair(scalars, 'ForceModule.y'),
        'z': curve_pair(scalars, 'ForceModule.z'),
        'space': 'modelled_as_emitter_local (inWorldSpace flag absent)',
    }
    noise = {
        'enabled': module_enabled('NoiseModule'),
        'strength': curve_pair(scalars, 'NoiseModule.strength'),
        'frequency': (module_dicts.get('NoiseModule') or {}).get('frequency'),
        'octaves': (module_dicts.get('NoiseModule') or {}).get('octaves'),
        'status': 'field_absent_not_simulated',
    }
    if noise['enabled']:
        flags.append('noise_field_absent')

    clamp = {
        'enabled': module_enabled('ClampVelocityModule'),
        'x': curve_pair(scalars, 'ClampVelocityModule.x'),
        'y': curve_pair(scalars, 'ClampVelocityModule.y'),
        'z': curve_pair(scalars, 'ClampVelocityModule.z'),
        'magnitude': curve_pair(scalars, 'ClampVelocityModule.magnitude'),
        'drag': curve_pair(scalars, 'ClampVelocityModule.drag'),
        'status': 'not_simulated_this_round',
    }
    collision = {
        'enabled': module_enabled('CollisionModule'),
        'bounce': curve_pair(scalars, 'CollisionModule.m_Bounce'),
        'dampen': curve_pair(scalars, 'CollisionModule.m_Dampen'),
        'status': 'planes_absent_not_simulated',
    }
    if collision['enabled']:
        flags.append('collision_planes_absent')
    trail = {
        'enabled': module_enabled('TrailModule'),
        'lifetime': curve_pair(scalars, 'TrailModule.lifetime'),
        'width_over_trail': curve_pair(scalars, 'TrailModule.widthOverTrail'),
        'status': 'not_simulated_this_round',
    }
    uv = {
        'enabled': module_enabled('UVModule'),
        'frame_over_time': curve_pair(scalars, 'UVModule.frameOverTime'),
        'start_frame': curve_pair(scalars, 'UVModule.startFrame'),
        'tiles': [(module_dicts.get('UVModule') or {}).get('tilesX'),
                  (module_dicts.get('UVModule') or {}).get('tilesY')],
        'status': 'not_simulated_texture_decode_is_another_digger',
    }
    if module_enabled('SubModule'):
        flags.append('sub_emitters_not_modelled')

    if props.get('autoRandomSeed') is False:
        flags.append('explicit_serialized_random_seed')
    if props.get('prewarm'):
        flags.append('prewarm_declared_not_simulated')

    prefab_row = prefab.get(pid) or {}
    return {
        'identity': scoped['identity'],
        'gameobject': scoped.get('gameobject'),
        'raw_location': scoped.get('raw_location'),
        'raw_object_sha256': scoped.get('raw_object_sha256'),
        'prefab_root': prefab_row.get('prefab_root'),
        'renderers': scoped.get('renderers') or [],
        'properties': {
            'length_in_sec': props.get('lengthInSec'),
            'simulation_speed': props.get('simulationSpeed'),
            'looping': props.get('looping'),
            'prewarm': props.get('prewarm'),
            'play_on_awake': props.get('playOnAwake'),
            'use_unscaled_time': props.get('useUnscaledTime'),
            'auto_random_seed': props.get('autoRandomSeed'),
            'random_seed': props.get('randomSeed'),
            'scaling_mode': props.get('scalingMode'),
            'move_with_transform': props.get('moveWithTransform'),
            'stop_action': props.get('stopAction'),
            'culling_mode': props.get('cullingMode'),
            'ring_buffer_mode': props.get('ringBufferMode'),
            'ring_buffer_loop_range': props.get('ringBufferLoopRange'),
            'emitter_velocity_mode': props.get('emitterVelocityMode'),
        },
        'modules_enabled': {m: enabled.get(m) for m in MODULE_ORDER},
        'model': {
            'initial': initial,
            'emission': emission,
            'shape': shape,
            'velocity': velocity,
            'size_over_lifetime': size_over_life,
            'rotation_over_lifetime': rotation_over_life,
            'color_over_lifetime': color_over_life,
            'forces': forces,
            'noise': noise,
            'clamp_velocity': clamp,
            'collision': collision,
            'trail': trail,
            'uv': uv,
        },
        'decode_flags': flags,
    }


def _mode_counts(systems, path):
    counts = {}
    for sysrec in systems:
        node = sysrec['model']
        for part in path.split('.'):
            node = node.get(part) or {}
        mode = node.get('mode')
        if mode is None:
            continue
        counts[mode] = counts.get(mode, 0) + 1
    return counts


def build():
    """Full artifact. Every count is measured here, never copied from prose."""
    scoped = load_scoped_systems()
    native = load_native_constants()
    prefab = load_prefab_roots()

    systems = [build_system_model(s, native, prefab) for s in scoped]
    by_file = {}
    for rec in systems:
        by_file[rec['identity']['serialized_file']] = \
            by_file.get(rec['identity']['serialized_file'], 0) + 1

    module_enabled = {}
    for mod in MODULE_ORDER:
        module_enabled[mod] = sum(1 for r in systems if r['modules_enabled'].get(mod))

    flag_counts = {}
    for rec in systems:
        for flag in rec['decode_flags']:
            flag_counts[flag] = flag_counts.get(flag, 0) + 1

    def nonzero_rate(rec):
        rate = rec['model']['emission']['rate_over_time']
        return bool(rate.get('value') and rate['value'] > 0)

    def constant(rec, *path):
        node = rec['model']
        for part in path:
            node = node.get(part) or {}
        return node.get('mode') == 'equal_values'

    counts = {
        'systems': len(systems),
        'systems_by_file': by_file,
        'native_constant_records': len(native),
        'native_constants_joined': sum(1 for r in systems
                                       if 'native_constants_missing' not in r['decode_flags']),
        'prefab_root_joined': sum(1 for r in systems if r['prefab_root']),
        'distinct_prefab_roots': len({r['prefab_root'] for r in systems if r['prefab_root']}),
        'module_enabled': module_enabled,
        'looping': sum(1 for r in systems if r['properties']['looping'] is True),
        'play_on_awake': sum(1 for r in systems if r['properties']['play_on_awake'] is True),
        'prewarm': sum(1 for r in systems if r['properties']['prewarm'] is True),
        'explicit_random_seed': sum(1 for r in systems
                                    if r['properties']['auto_random_seed'] is False),
        'length_modes': _histogram(r['properties']['length_in_sec'] for r in systems),
        'simulation_speed_modes':
            _histogram(r['properties']['simulation_speed'] for r in systems),
        'start_lifetime_mode': _mode_counts(systems, 'initial.start_lifetime'),
        'start_speed_mode': _mode_counts(systems, 'initial.start_speed'),
        'start_size_mode': _mode_counts(systems, 'initial.start_size'),
        'rate_over_time_mode': _mode_counts(systems, 'emission.rate_over_time'),
        'emission_positive_rate': sum(1 for r in systems if nonzero_rate(r)),
        'emission_zero_rate': sum(1 for r in systems if not nonzero_rate(r)),
        'bursts_positive': sum(1 for r in systems
                               if (r['model']['emission']['burst_count'] or 0) > 0),
        'zero_start_speed': sum(1 for r in systems
                                if (r['model']['initial']['start_speed'].get('value') or 0) == 0),
        'gravity_modifier_nonzero': sum(
            1 for r in systems
            if (r['model']['initial']['gravity_modifier'].get('value') or 0) != 0),
        'max_particles_le_10': sum(1 for r in systems
                                   if (r['model']['initial']['max_particles'] or 0) <= 10),
        'constant_curves': {
            'start_lifetime': sum(1 for r in systems
                                  if constant(r, 'initial', 'start_lifetime')),
            'start_speed': sum(1 for r in systems
                               if constant(r, 'initial', 'start_speed')),
            'rate_over_time': sum(1 for r in systems
                                  if constant(r, 'emission', 'rate_over_time')),
            'size_curve': sum(1 for r in systems
                              if constant(r, 'size_over_lifetime', 'curve')),
        },
        'decode_flag_counts': flag_counts,
    }

    artifact = envelope(SCOPE, inputs_map([
        'datas/l3-visual-surface/particles-000.json.gz',
        'datas/l3-visual-surface/particles-001.json.gz',
        'datas/l3-visual-surface/particles-002.json.gz',
        NATIVE_TYPES, PREFAB_CSV,
        'tools/verify/l3_particle_model.py',
        'tools/verify/l3_model_common.py',
    ]), DECODE_LIMITS)
    artifact.update({
        'counts': counts,
        'simulation_model': SIMULATION_MODEL,
        'systems': systems,
    })
    artifact['build'] = {
        'tool_sha256': sha256_file(Path(__file__).resolve()),
        'common_sha256': sha256_file(Path(__file__).with_name('l3_model_common.py')),
        'generator': 'tools/verify/l3_particle_model.py --build',
    }
    return artifact


def _histogram(values):
    out = {}
    for v in values:
        if v is None:
            key = 'null'
        else:
            key = repr(float(v))
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))


SIMULATION_MODEL = {
    'time': 'emitter_time = t * simulationSpeed; cycle_time = emitter_time mod '
            'lengthInSec when looping, else min(emitter_time, lengthInSec)',
    'emission': 'births happen at k / rate for k = 1.. while k/rate <= emitter_time '
                '(non-looping stops at lengthInSec); rate is the collapsed MinMax scalar',
    'per_particle': 'lifetime/speed/size use the exported curve constant by default; '
                    'with spread=range each particle draws uniformly inside the exported '
                    'constant pair using splitmix64(seed, stream, k) (a model choice, '
                    'not engine-proven)',
    'direction': 'cone of half-angle ShapeModule.angle around declared emitter-local +Y; '
                 'ShapeModule.type is NOT interpreted',
    'motion': 'position = v0 * age + 0.5 * gravity * age^2, v0 = speed * direction + '
              'constant VelocityModule components (emitter local)',
    'size': 'size = startSize * SizeModule.curve constant (curve keys absent)',
    'rotation': 'rotation = startRotation + RotationModule.curve scalar * age '
                '(units not decoded)',
    'alpha': 'alpha = 1.0 always; ColorModule gradients are absent, so no fade is claimed',
    'cap': 'alive set is truncated to InitialModule.maxNumParticles by dropping the oldest',
    'not_simulated': ['bursts', 'noise', 'collision', 'drag/clamp', 'trails', 'UV frame '
                      'animation', 'sub emitters', 'prewarm', 'rateOverDistance'],
    'proven': False,
}


# --------------------------------------------------------------------------
# Simulation
# --------------------------------------------------------------------------
class ParticleSim:
    """Deterministic bounded particle model for one system record."""

    def __init__(self, system, seed=0, gravity=(0.0, 0.0, 0.0), spread='none',
                 overrides=None, axis=(0.0, 1.0, 0.0)):
        self.system = system
        self.seed = int(seed)
        self.gravity = tuple(float(x) for x in gravity)
        self.spread = spread
        self.axis = tuple(float(x) for x in axis)
        self.path_id = int(system['identity']['path_id'])
        self.overrides = dict(overrides or {})
        model = system['model']
        props = system['properties']
        self.length = float(props['length_in_sec'] or 0.0)
        self.speed_scale = float(props['simulation_speed'] or 1.0)
        self.looping = bool(props['looping'])
        self.rate = self._scalar(model['emission']['rate_over_time'])
        self.lifetime = model['initial']['start_lifetime']
        self.start_speed = model['initial']['start_speed']
        self.start_size = model['initial']['start_size']
        self.start_rotation = model['initial']['start_rotation']
        self.gravity_modifier = self._scalar(model['initial']['gravity_modifier'])
        self.size_curve = self._scalar(model['size_over_lifetime']['curve'], default=1.0)
        self.rotation_curve = self._scalar(model['rotation_over_lifetime']['curve'],
                                           default=0.0)
        self.angle = float(model['shape'].get('angle') or 0.0)
        self.max_particles = int(model['initial'].get('max_particles') or 0)
        vel = model['velocity']
        self.velocity_local = tuple(self._scalar(vel[c]) for c in ('x', 'y', 'z')) \
            if vel['enabled'] else (0.0, 0.0, 0.0)
        self.frame_flags = sorted(set(system['decode_flags']))

    # -- helpers ----------------------------------------------------------
    def _scalar(self, pair, default=0.0):
        key = pair.get('source_key')
        if key and key in self.overrides:
            return float(self.overrides[key])
        value = pair.get('value')
        return default if value is None else float(value)

    def _draw(self, pair, stream, index, default=1.0):
        """Per-particle value: the exported constant, or a spread over the pair."""
        key = pair.get('source_key')
        if key and key in self.overrides:
            return float(self.overrides[key])
        value = pair.get('value')
        if value is None:
            return default
        if self.spread != 'range':
            return float(value)
        bounds = pair.get('bounds') or [value, value]
        if bounds[0] == bounds[1]:
            return float(bounds[0])
        return lerp(bounds[0], bounds[1], uniform01(self.seed, stream, index))

    def emitter_time(self, t):
        return float(t) * self.speed_scale

    def births_before(self, t):
        """Number of births with birth_time <= emitter time (1-based count)."""
        tc = self.emitter_time(t)
        if self.rate <= 0:
            return 0
        limit = tc if self.looping else min(tc, self.length)
        if limit <= 0:
            return 0
        return int(limit * self.rate + 1e-9)

    # -- state ------------------------------------------------------------
    def sample(self, t, limit=64):
        if not fin(t) or t < 0:
            raise ValueError('sample time must be a finite t >= 0')
        tc = self.emitter_time(t)
        cycle = (tc % self.length) if (self.looping and self.length > 0) else \
            (min(tc, self.length) if self.length else tc)
        n_births = self.births_before(t)
        alive = []
        dropped = 0
        for k in range(n_births, 0, -1):
            birth = k / self.rate
            age = tc - birth
            lifetime = self._draw(self.lifetime, 1, k, default=1.0)
            if age < 0 or age >= lifetime:
                continue
            alive.append((k, birth, age, lifetime))
            if self.max_particles and len(alive) > self.max_particles:
                alive.pop()
                dropped += 1
        alive.reverse()
        particles = [self._particle(k, birth, age, life) for k, birth, age, life in alive]
        return {
            't': float(t),
            'emitter_time': tc,
            'cycle_time': cycle,
            'system': self.system['identity'],
            'prefab_root': self.system.get('prefab_root'),
            'length_in_sec': self.length,
            'looping': self.looping,
            'emission_rate': self.rate,
            'births_total': n_births,
            'alive': len(particles),
            'dropped_for_cap': dropped,
            'particles': particles[:limit],
            'particles_truncated': max(0, len(particles) - limit),
            'model_flags': self.frame_flags + ['color_over_lifetime_not_modelled',
                                               'random_sequence_not_engine'],
            'not_modelled': SIMULATION_MODEL['not_simulated'],
            'gravity_input': list(self.gravity),
        }

    def _particle(self, index, birth, age, lifetime):
        u2 = uniform01(self.seed, 2, index)
        u3 = uniform01(self.seed, 3, index)
        speed = self._draw(self.start_speed, 4, index, default=0.0)
        # cone of half-angle self.angle around the declared local axis
        import math
        half = math.radians(self.angle) * u3
        azimuth = 2.0 * math.pi * u2
        sin_half = math.sin(half)
        direction = (sin_half * math.cos(azimuth), math.cos(half),
                     sin_half * math.sin(azimuth))
        vx = speed * direction[0] + self.velocity_local[0]
        vy = speed * direction[1] + self.velocity_local[1]
        vz = speed * direction[2] + self.velocity_local[2]
        g = tuple(self.gravity_modifier * self.gravity[i] for i in range(3))
        position = [vx * age + 0.5 * g[0] * age * age,
                    vy * age + 0.5 * g[1] * age * age,
                    vz * age + 0.5 * g[2] * age * age]
        size = self._draw(self.start_size, 5, index, default=1.0) * self.size_curve
        rotation = (self._draw(self.start_rotation, 6, index, default=0.0)
                    + self.rotation_curve * age)
        return {
            'index': index,
            'birth_time': birth,
            'age': age,
            'lifetime': lifetime,
            'normalized_age': age / lifetime if lifetime > 0 else None,
            'position': position,
            'direction': list(direction),
            'speed': speed,
            'size': size,
            'rotation_model': rotation,
            'alpha': 1.0,
            'alpha_status': 'color_gradient_absent',
        }


def sim_cli(system_path_id, times, seed=0, limit=64, gravity=(0.0, 0.0, 0.0),
            spread='none', overrides=None):
    artifact = read_json_gz(ROOT / OUT_DEFAULT)
    rec = None
    for candidate in artifact['systems']:
        if int(candidate['identity']['path_id']) == int(system_path_id):
            rec = candidate
            break
    if rec is None:
        raise SystemExit(f'ParticleSystem {system_path_id} is not in the scoped model')
    sim = ParticleSim(rec, seed=seed, gravity=gravity, spread=spread,
                      overrides=overrides)
    return {'system': rec['identity'], 'prefab_root': rec['prefab_root'],
            'model_notice': artifact['model_notice'],
            'decode_flags': rec['decode_flags'],
            'samples': [sim.sample(t, limit=limit) for t in times]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--build', action='store_true', help='regenerate the artifact')
    ap.add_argument('--out', default=OUT_DEFAULT)
    ap.add_argument('--system', type=int, help='ParticleSystem path_id to sample')
    ap.add_argument('--times', default='0,0.25,0.5,1.0')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--limit', type=int, default=16)
    ap.add_argument('--gravity', default='0,0,0')
    ap.add_argument('--spread', default='none', choices=['none', 'range'],
                    help='none = use each curve constant; range = draw inside the '
                         'exported constant pair (model choice, not engine-proven)')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--filter', default='')
    args = ap.parse_args(argv)

    if args.build:
        artifact = build()
        write_json_gz(ROOT / args.out, artifact)
        print(f"wrote {args.out}: {artifact['counts']['systems']} systems, "
              f"{artifact['counts']['module_enabled']['EmissionModule']} emitters, "
              f"flags={artifact['counts']['decode_flag_counts']}")
        return 0

    if args.list:
        artifact = read_json_gz(ROOT / OUT_DEFAULT)
        n = 0
        for rec in artifact['systems']:
            name = (rec.get('prefab_root') or '')
            if args.filter and args.filter.lower() not in name.lower():
                continue
            print(rec['identity']['path_id'], name,
                  rec['model']['emission']['rate_over_time'].get('value'),
                  rec['properties']['length_in_sec'])
            n += 1
            if args.limit and n >= args.limit:
                break
        return 0

    if args.system is None:
        ap.error('one of --build/--list/--system is required')

    times = [float(x) for x in args.times.split(',') if x.strip()]
    gravity = tuple(float(x) for x in args.gravity.split(','))
    out = sim_cli(args.system, times, seed=args.seed, limit=args.limit, gravity=gravity,
                  spread=args.spread)
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
