import gc
import gzip
import hashlib
import json
import unittest
from collections import Counter
from tools.verify.l3_animator_programs import build, load, probe_channels, probe_state, OUT
from tools.verify.l3_chain_graph import ROOT, key
from tools.verify.l3_recipe import Recipes

class Programs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=load();cls.r=Recipes()
    @classmethod
    def tearDownClass(cls):cls.p=cls.r=None;gc.collect()
    def test_regenerate_exactly_from_pinned_raw_controller_objects(self):
        self.assertEqual(build(),self.p)
        self.assertLess(OUT.stat().st_size,5_000_000)
    def test_compiled_source_counts(self):
        self.assertEqual(self.p['counts'],dict(controllers=232,animator_attachments=1587,parameters=377,machines=232,states=667,empty_machines=1,any_transitions=343,state_transitions=125,motion_leaves=666,binding_diagnostics=410))
    def test_default_indices_and_layer_machine_indices(self):
        empty=0
        for c in self.p['controllers']:
            for l in c['layers']:self.assertLess(l['m_StateMachineIndex'],len(c['machines']))
            for m in c['machines']:
                if not m['states']:empty+=1;self.assertEqual(m['default_status'],'empty_machine')
                else:self.assertTrue(0<=m['default_state_index']<len(m['states']))
        self.assertEqual(empty,1)
    def test_all_motion_leaves_point_to_recovered_clips(self):
        clips={key(m['identity']) for m in self.r.section('motion')}
        for c in self.p['controllers']:
            for m in c['machines']:
                for s in m['states']:
                    for tree in s['trees']:
                        for n in tree['nodes']:
                            self.assertEqual(n['clip_status'],'leaf_clip_index_resolved')
                            self.assertIn(key(n['clip']),clips)
                            self.assertEqual(n['clip'],c['clips'][n['raw']['m_ClipID']])
    def test_parameter_defaults_are_exact_typed_slots_not_zero_guesses(self):
        for c in self.p['controllers']:
            for p in c['parameters']:
                self.assertEqual(p['default_status'],'typed_slot')
                self.assertEqual(p['default'],c['parameter_default_arrays'][p['default_storage']][p['raw']['m_Index']])
                self.assertTrue(p['names'])
    def test_encoded_transition_destinations_not_cast_to_state_index(self):
        encoded=[]
        for c in self.p['controllers']:
            for m in c['machines']:
                transitions=m['any_state_transitions']+[t for s in m['states'] for t in s['transitions']]+[t for s in m['selectors'] for t in s['transitions']]
                for t in transitions:
                    if t['destination_index']>=len(m['states']):encoded.append(t);self.assertNotEqual(t['destination_status'],'local_state_index')
        self.assertTrue(encoded)
    def test_animator_links_only_direct_controller_references(self):
        ids={key(c['identity']) for c in self.p['controllers']}
        for a in self.p['animator_attachments']:
            for c in a['controllers']:self.assertIn(key(c),ids)
    def test_binding_audit_distinguishes_no_path_from_no_component(self):
        self.assertEqual(Counter(d['reason'] for d in self.p['binding_diagnostics']),{'path_not_in_animator_subtree':376,'required_component_class_absent':17,'multiple_component_targets':17})
        for d in self.p['binding_diagnostics']:
            if d['reason']=='required_component_class_absent':
                required='MonoBehaviour' if d['required']['typeID']==114 else 'BoxCollider2D'
                for p in d['candidates']:self.assertNotIn(required,[c['type'] for c in p['actual_components']])
    def test_pause_recipe_includes_programs_and_not_just_unordered_clips(self):
        recipe=self.r.recipe(10)
        c=next(c for c in recipe['controller_programs'] if c['name']=='Popup_Network')
        m=c['machines'][0];self.assertEqual(m['states'][m['default_state_index']]['name_candidates'],['Appear'])
        self.assertEqual(len(recipe['animator_program_links']),4)
    def test_selected_appear_state_joins_numeric_properties_to_actual_targets(self):
        ident=lambda v:dict(serialized_file='data.unity3d/resources.assets',path_id=v)
        d=probe_state(self.r,ident(495980),ident(1974),0,0,.25)
        self.assertEqual(d['state_names'],['Appear']);self.assertEqual(d['clip'],ident(1572))
        for p in d['properties']:
            self.assertEqual(p['target_binding']['status'],'unique_target')
        self.assertAlmostEqual(d['properties'][0]['channels'][0]['value'],1.030399899053574)
        self.assertAlmostEqual(d['properties'][1]['channels'][0]['value'],.8313725590705872)
    def test_wrong_controller_is_rejected_not_globally_matched(self):
        ident=lambda v:dict(serialized_file='data.unity3d/resources.assets',path_id=v)
        with self.assertRaises(ValueError):probe_state(self.r,ident(495980),ident(1927),0,0,0)

class CoefficientProbes(unittest.TestCase):
    def motion(self):
        return dict(start=0.,stop=1.,bindings=[dict(typeID=212,attribute=99,isPPtrCurve=0,isIntCurve=0)],continuous_stream_curve_count=1,discrete_curve_count=0,channel_count=1,streamed=[dict(time=-3.4e38,keys=[dict(index=0,coeff=[0,0,0,99])]),dict(time=0.,keys=[dict(index=0,coeff=[1,2,3,4])])],dense={'m_CurveCount':0},constants=[],pptr_targets=[])
    def test_cubic_coefficients_are_relative_to_key_time(self):
        m=self.motion();v=probe_channels(m,.5)[0]['channels'][0]['value'];self.assertEqual(v,6.125)
    def test_sentinel_is_not_extrapolated_as_real_key(self):
        m=self.motion();m['streamed']=m['streamed'][:1];m['streamed'][0]['keys'][0]['coeff'][0]=1.
        self.assertIsNone(probe_channels(m,.5)[0]['channels'][0]['value'])
    def test_constant_initial_key_is_time_independent_not_missing(self):
        m=self.motion();m['streamed']=m['streamed'][:1]
        self.assertEqual(probe_channels(m,.5)[0]['channels'][0]['value'],99.)
    def test_dense_grid_linear_and_constant_columns(self):
        m=self.motion();m.update(continuous_stream_curve_count=0,channel_count=2,bindings=[dict(typeID=212,attribute=99),dict(typeID=212,attribute=100)],dense=dict(m_CurveCount=1,m_FrameCount=2,m_SampleRate=1.,m_BeginTime=0.,m_SampleArray=[2.,6.]),constants=[7.])
        p=probe_channels(m,.25);self.assertEqual(p[0]['channels'][0]['value'],3.);self.assertEqual(p[1]['channels'][0]['value'],7.)
    def test_sprite_pointer_is_step_not_polynomial(self):
        m=self.motion();m['bindings'][0]['isPPtrCurve']=1;m['streamed'][1]['keys'][0]['coeff']=[100,100,100,1.];m['pptr_targets']=[None,dict(serialized_file='f',path_id=7)]
        p=probe_channels(m,.5)[0];self.assertEqual(p['pptr_mapping_index'],1);self.assertEqual(p['pptr_target']['path_id'],7)
    def test_integer_channels_are_steps(self):
        m=self.motion();m['bindings'][0]['isIntCurve']=1
        self.assertEqual(probe_channels(m,.5)[0]['channels'][0]['value'],4.)
    def test_nonfinite_polynomial_remains_unknown(self):
        m=self.motion();m['streamed'][1]['keys'][0]['coeff'][0]=float('inf')
        self.assertIsNone(probe_channels(m,.5)[0]['channels'][0]['value'])
    def test_out_of_clip_or_nonfinite_time_rejected(self):
        for t in (-.1,1.1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):probe_channels(self.motion(),t)

if __name__=='__main__':unittest.main()
