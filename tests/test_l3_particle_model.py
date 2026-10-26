"""Tests for the bounded particle model (tools/verify/l3_particle_model.py).

Everything asserted here is measured from the artifacts in this repo; nothing is an
engine claim. Synthetic system records are used only where the game data would need an
external engine constant (gravity) or an explicit spread policy.
"""
import gzip
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path('tools/verify').resolve()))
from l3_particle_model import (OUT_DEFAULT, ParticleSim, build, load_native_constants,
                               load_prefab_roots, load_scoped_systems)
from l3_model_common import minmax_pair, read_json_gz


def synthetic_system(**overrides):
    """Minimal system record: cone emission, constant lifetime/speed, no bursts."""
    system = {
        'identity': {'serialized_file': 'synthetic', 'path_id': 1},
        'prefab_root': 'Synthetic',
        'properties': {'length_in_sec': 2.0, 'simulation_speed': 1.0, 'looping': False,
                       'prewarm': False, 'auto_random_seed': True},
        'modules_enabled': {},
        'model': {
            'initial': {
                'start_lifetime': {'value': 0.5, 'min_scalar': 0.5,
                                   'bounds': [0.5, 0.5], 'mode': 'equal_values',
                                   'source_key': 'InitialModule.startLifetime'},
                'start_speed': {'value': 2.0, 'min_scalar': 2.0, 'bounds': [2.0, 2.0],
                                'mode': 'equal_values',
                                'source_key': 'InitialModule.startSpeed'},
                'start_size': {'value': 1.0, 'min_scalar': 1.0, 'bounds': [1.0, 1.0],
                               'mode': 'equal_values',
                               'source_key': 'InitialModule.startSize'},
                'start_rotation': {'value': 0.0, 'min_scalar': 0.0, 'bounds': [0.0, 0.0],
                                   'mode': 'equal_values',
                                   'source_key': 'InitialModule.startRotation'},
                'gravity_modifier': {'value': 1.0, 'min_scalar': 1.0, 'bounds': [1.0, 1.0],
                                     'mode': 'equal_values',
                                     'source_key': 'InitialModule.gravityModifier'},
                'max_particles': 100,
            },
            'emission': {'rate_over_time': {'value': 4.0, 'min_scalar': 4.0,
                                            'bounds': [4.0, 4.0], 'mode': 'equal_values',
                                            'source_key': 'EmissionModule.rateOverTime'},
                         'burst_count': 0},
            'shape': {'enabled': True, 'angle': 0.0},
            'velocity': {'enabled': False, 'x': {}, 'y': {}, 'z': {}},
            'size_over_lifetime': {'curve': {'value': 1.0}},
            'rotation_over_lifetime': {'curve': {'value': 0.0}},
        },
        'decode_flags': ['curve_keys_absent'],
    }
    for path, value in overrides.items():
        node = system['model']
        parts = path.split('__')
        for part in parts[:-1]:
            node = node[part]
        node[parts[-1]] = value
    return system


class MinMaxPairTests(unittest.TestCase):
    def test_constant_value_is_the_exported_scalar(self):
        pair = minmax_pair(2.0, 5.0)
        self.assertEqual(pair['value'], 2.0)
        self.assertEqual(pair['min_scalar'], 5.0)
        self.assertEqual(pair['bounds'], [2.0, 5.0])
        self.assertEqual(pair['mode'], 'differs')
        self.assertFalse(pair['mode_proven'])

    def test_equal_constants_are_reported_as_equal_not_as_proof(self):
        pair = minmax_pair(1.5, 1.5)
        self.assertEqual(pair['mode'], 'equal_values')
        self.assertEqual(pair['bounds'], [1.5, 1.5])
        self.assertFalse(pair['mode_proven'])


class ArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = read_json_gz(OUT_DEFAULT)
        cls.systems = cls.artifact['systems']

    def test_system_count_and_identity_are_measured(self):
        self.assertEqual(self.artifact['counts']['systems'], 954)
        identities = {(s['identity']['serialized_file'], s['identity']['path_id'])
                      for s in self.systems}
        self.assertEqual(len(identities), 954)
        by_file = {}
        for s in self.systems:
            by_file[s['identity']['serialized_file']] = \
                by_file.get(s['identity']['serialized_file'], 0) + 1
        self.assertEqual(by_file, {'data.unity3d/resources.assets': 883,
                                   'data.unity3d/level2': 71})
        self.assertEqual(self.artifact['counts']['systems_by_file'], by_file)

    def test_counts_match_the_scoped_source_shards(self):
        scoped = load_scoped_systems()
        self.assertEqual(len(scoped), len(self.systems))
        native = load_native_constants()
        prefab = load_prefab_roots()
        joined = sum(1 for s in self.systems
                     if s['identity']['path_id'] in native)
        self.assertEqual(joined, 954)
        self.assertEqual(self.artifact['counts']['native_constants_joined'], 954)
        prefab_joined = sum(1 for s in self.systems if s['prefab_root'])
        self.assertEqual(prefab_joined, 953)
        self.assertEqual(self.artifact['counts']['prefab_root_joined'], 953)
        self.assertEqual(len(prefab), 4845)

    def test_the_one_unjoined_prefab_system_is_named(self):
        unjoined = [s['identity'] for s in self.systems if not s['prefab_root']]
        self.assertEqual(unjoined, [{'serialized_file': 'data.unity3d/resources.assets',
                                     'path_id': 502274}])

    def test_module_enablement_is_recomputed_not_copied(self):
        enabled = {}
        for s in self.systems:
            for module, flag in s['modules_enabled'].items():
                if flag:
                    enabled[module] = enabled.get(module, 0) + 1
        measured = self.artifact['counts']['module_enabled']
        self.assertEqual({k: v for k, v in measured.items() if v}, enabled)
        self.assertEqual(measured['TriggerModule'], 0)  # key kept, zero counted
        self.assertEqual(enabled['EmissionModule'], 954)
        self.assertEqual(enabled['ShapeModule'], 504)
        self.assertEqual(enabled['ColorModule'], 801)

    def test_absent_data_is_flagged_instead_of_defaulted(self):
        flags = self.artifact['counts']['decode_flag_counts']
        self.assertEqual(flags['curve_keys_absent'], 954)
        self.assertEqual(flags['gradient_absent'], 801)
        self.assertEqual(flags['bursts_not_exported'], 402)
        self.assertEqual(flags['collision_planes_absent'], 18)
        self.assertEqual(flags['noise_field_absent'], 16)
        for system in self.systems:
            self.assertIn('curve_keys_absent', system['decode_flags'])
            self.assertEqual(system['model']['color_over_lifetime']['gradient'],
                             'not_exported')
            self.assertEqual(system['model']['emission']['bursts'], 'not_exported')

    def test_scope_states_what_is_not_modelled(self):
        self.assertFalse(self.artifact['simulation_model']['proven'])
        self.assertFalse(self.artifact['provisional'] is False)
        self.assertIn('bursts', self.artifact['simulation_model']['not_simulated'])
        self.assertIn('not Unity simulation', self.artifact['model_notice'])

    def test_every_input_is_sha_pinned(self):
        for path, sha in self.artifact['inputs'].items():
            self.assertIsNotNone(sha, path)
            self.assertEqual(len(sha), 64, path)


class SimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = read_json_gz(OUT_DEFAULT)
        cls.by_id = {s['identity']['path_id']: s for s in cls.artifact['systems']}

    def test_determinism_same_seed_same_state(self):
        system = self.by_id[4785]
        first = ParticleSim(system, seed=11, spread='range').sample(1.0)
        second = ParticleSim(system, seed=11, spread='range').sample(1.0)
        self.assertEqual(first, second)

    def test_seed_changes_spread_values_only_when_spread_enabled(self):
        system = self.by_id[4785]
        a = ParticleSim(system, seed=1, spread='range').sample(1.0)['particles']
        b = ParticleSim(system, seed=2, spread='range').sample(1.0)['particles']
        self.assertNotEqual([p['size'] for p in a], [p['size'] for p in b])
        c = ParticleSim(system, seed=1, spread='none').sample(1.0)['particles']
        d = ParticleSim(system, seed=2, spread='none').sample(1.0)['particles']
        self.assertEqual([p['size'] for p in c], [p['size'] for p in d])

    def test_birth_schedule_is_rate_times_time(self):
        sim = ParticleSim(synthetic_system(), seed=0)
        state = sim.sample(1.0)
        self.assertEqual(state['births_total'], 4)
        # births happen at k/rate = 0.25, 0.5, 0.75, 1.0; the first two are already
        # older than the 0.5 s lifetime and are therefore not in the alive set
        self.assertEqual([round(p['birth_time'], 9) for p in state['particles']],
                         [0.75, 1.0])
        self.assertEqual(state['emission_rate'], 4.0)

    def test_lifetime_bounds_and_alive_filter(self):
        sim = ParticleSim(synthetic_system(), seed=0)
        state = sim.sample(1.0)
        self.assertTrue(all(p['lifetime'] == 0.5 for p in state['particles']))
        # a particle born at 0.25 has age 0.75 > 0.5 and must be gone
        self.assertEqual([round(p['age'], 6) for p in state['particles']], [0.25, 0.0])
        self.assertTrue(all(0 <= p['age'] < p['lifetime'] for p in state['particles']))
        self.assertEqual(len(state['particles']), 2)

    def test_looping_wraps_cycle_time(self):
        system = self.by_id[4785]
        self.assertTrue(system['properties']['looping'])
        sim = ParticleSim(system, seed=0)
        state = sim.sample(5.0)
        self.assertAlmostEqual(state['cycle_time'],
                               5.0 % system['properties']['length_in_sec'], places=9)

    def test_max_particles_cap_drops_oldest(self):
        system = self.by_id[4783]
        self.assertEqual(system['model']['initial']['max_particles'], 1)
        sim = ParticleSim(system, seed=0)
        state = sim.sample(3.0)
        self.assertEqual(state['alive'], 1)
        self.assertGreater(state['dropped_for_cap'], 0)

    def test_gravity_is_a_caller_input_not_an_engine_default(self):
        system = synthetic_system()
        no_gravity = ParticleSim(system, seed=0).sample(0.5)
        gravity = ParticleSim(system, seed=0, gravity=(0.0, -10.0, 0.0)).sample(0.5)
        self.assertEqual(no_gravity['gravity_input'], [0.0, 0.0, 0.0])
        self.assertEqual(gravity['gravity_input'], [0.0, -10.0, 0.0])
        self.assertNotAlmostEqual(no_gravity['particles'][0]['position'][1],
                                  gravity['particles'][0]['position'][1], places=6)

    def test_cone_angle_bounds_direction(self):
        import math
        system = synthetic_system()
        system['model']['shape']['angle'] = 10.0
        for particle in ParticleSim(system, seed=3, spread='range').sample(1.0)['particles']:
            direction = particle['direction']
            self.assertAlmostEqual(direction[0] ** 2 + direction[1] ** 2
                                   + direction[2] ** 2, 1.0, places=9)
            self.assertGreaterEqual(direction[1], math.cos(math.radians(10.0)) - 1e-12)

    def test_alpha_is_never_claimed_because_gradients_are_absent(self):
        state = ParticleSim(synthetic_system(), seed=0).sample(1.0)
        self.assertEqual({p['alpha'] for p in state['particles']}, {1.0})
        self.assertEqual({p['alpha_status'] for p in state['particles']},
                         {'color_gradient_absent'})
        self.assertIn('color_over_lifetime_not_modelled', state['model_flags'])

    def test_overrides_reach_the_modelled_constant(self):
        system = synthetic_system()
        sim = ParticleSim(system, seed=0,
                          overrides={'InitialModule.startLifetime': 2.0})
        state = sim.sample(1.0)
        self.assertEqual({p['lifetime'] for p in state['particles']}, {2.0})
        self.assertEqual(len(state['particles']), 4)

    def test_rejects_non_finite_or_negative_time(self):
        sim = ParticleSim(synthetic_system(), seed=0)
        for bad in (-0.001, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                sim.sample(bad)

    def test_output_limit_is_declared(self):
        state = ParticleSim(synthetic_system(), seed=0).sample(2.0, limit=1)
        self.assertEqual(len(state['particles']), 1)
        self.assertGreater(state['particles_truncated'], 0)


class RegenerationTests(unittest.TestCase):
    def test_artifact_reproduces_byte_identically(self):
        from l3_model_common import write_json_gz
        import tempfile
        rebuilt = build()
        current = read_json_gz(OUT_DEFAULT)
        self.assertEqual(rebuilt, current)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'rebuilt.json.gz'
            write_json_gz(path, rebuilt)
            self.assertEqual(path.read_bytes(), Path(OUT_DEFAULT).read_bytes())


if __name__ == '__main__':
    unittest.main()
