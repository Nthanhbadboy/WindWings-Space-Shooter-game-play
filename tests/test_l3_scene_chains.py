import gc
import gzip
import hashlib
import json
import struct
import unittest
from collections import Counter
from tools.verify.l3_chain_graph import Graph, ROOT, RAW, identity, key, bool_flag, read_chunks
from tools.verify.l3_scene_chains import build, decode_motion, scalar_fields
from tools.verify.l3_recipe import Recipes

class GraphFixtures(unittest.TestCase):
    def test_file_scoping_and_header_authority(self):
        a=dict(serialized_file='a',path_id=1,type='MonoBehaviour',tree={'m_Enabled':0,'m_Script':{'m_PathID':99}},header={'m_Enabled':1,'m_Script':{'m_PathID':2}})
        b=dict(serialized_file='b',path_id=1,type='GameObject',tree={})
        g=Graph([a,b],[])
        self.assertEqual(len(g.rows),2)
        self.assertEqual(g.tree(key(a))['m_Enabled'],1)
        self.assertEqual(g.tree(key(a))['m_Script']['m_PathID'],2)
        self.assertEqual(a['tree']['m_Enabled'],0)
        self.assertIsNone(g.target(key(a),'.missing'))
    def test_flags_are_not_visibility_defaults(self):
        self.assertIsNone(bool_flag(None));self.assertIsNone(bool_flag(2))
        self.assertIs(bool_flag(0),False);self.assertIs(bool_flag(1),True)
    def test_pointer_fields_are_not_scalar_properties(self):
        self.assertEqual(list(scalar_fields({'m_Color':{'a':.5},'m_Sprite':{'m_FileID':1,'m_PathID':5}})),[('m_Color.a',.5)])
    def test_discrete_stream_is_decoded_without_continuous_curves(self):
        # One frame, one sprite index; fixture uses the preserved decoder's native word format.
        payload=struct.pack('<fiiffff',0.,1,0,0.,0.,0.,1.)
        words=list(struct.unpack('<'+'I'*(len(payload)//4),payload))
        r=dict(serialized_file='f',path_id=1,tree={'m_MuscleClip':{'m_Clip':{'data':{'m_StreamedClip':{'curveCount':0,'discreteCurveCount':1,'data':words},'m_DenseClip':{'m_FrameCount':0,'m_CurveCount':0,'m_SampleArray':[]}}}},'m_ClipBindingConstant':{'genericBindings':[{'typeID':212,'attribute':1,'isPPtrCurve':1}],'pptrCurveMapping':[None,{'m_FileID':1,'m_PathID':7}]}})
        d=decode_motion(r)
        self.assertNotEqual(d['status'],'decode_error',d)
        self.assertTrue(d['binding_coverage_exact'])
        self.assertEqual(d['discrete_pptr_keys'][0]['keys'][0]['reference']['m_PathID'],7)
    def test_bad_dense_shape_remains_explicit(self):
        r=dict(serialized_file='f',path_id=1,tree={'m_MuscleClip':{'m_Clip':{'data':{'m_StreamedClip':{'curveCount':0,'data':[]},'m_DenseClip':{'m_FrameCount':2,'m_CurveCount':1,'m_SampleArray':[]}}}}})
        self.assertEqual(decode_motion(r)['status'],'decode_error')

class JoinedChains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=build();cls.sections=cls.data['sections'];cls.consumer=Recipes()
    @classmethod
    def tearDownClass(cls):
        cls.data=cls.sections=cls.consumer=None;gc.collect()
    def test_regenerate_header_from_raw(self):
        expected={k:v for k,v in self.consumer.header.items() if k!='chunks'}
        actual={k:v for k,v in self.data.items() if k!='sections'}
        self.assertEqual(actual,expected)
    def test_regenerate_every_derived_row_and_chunk_hash(self):
        for name,rows in self.sections.items():
            offset=0
            for c in self.consumer.header['chunks'][name]:
                b=(ROOT/c['path']).read_bytes();self.assertLess(len(b),5_000_000)
                self.assertEqual(hashlib.sha256(b).hexdigest(),c['sha256'])
                part=json.loads(gzip.decompress(b));self.assertEqual(len(part),c['rows'])
                self.assertEqual(rows[offset:offset+len(part)],part,(name,offset));offset+=len(part)
            self.assertEqual(offset,len(rows))
    def test_no_hierarchy_or_matrix_unknowns_in_selected_roots(self):
        self.assertEqual(self.data['transform_errors'],[]);self.assertEqual(self.data['hierarchy_errors'],[])
        for n in self.sections['nodes']:
            self.assertEqual(len(n['layout_frame_matrix']),16)
            self.assertIn('m_LocalPosition',n['transform_properties'])
            self.assertIn('m_Layer',n['gameobject_properties'])
    def test_every_logical_owner_is_retained_in_recipe(self):
        nodes=self.sections['nodes']
        for ri,r in enumerate(self.data['roots']):
            selected=[nodes[i] for i in r['node_indices']]
            self.assertEqual(len(selected),r['nodes'])
            self.assertTrue(all(n['root']==ri for n in selected))
            components={key(c['identity']) for n in selected for c in n['component_identities']}
            for section,field,owner in [('callbacks','callback_indices','owner'),('sounds','sound_indices','owner'),('animators','animator_indices','animator')]:
                for i in r[field]:self.assertIn(key(self.sections[section][i][owner]),components)
        self.assertGreater(self.data['counts']['logical_nodes'],self.data['counts']['visual_nodes'])
    def test_all_clips_decoded_and_channel_coverage_exact(self):
        self.assertEqual(len(self.sections['motion']),665)
        for m in self.sections['motion']:
            self.assertEqual(m['status'],'numeric_stream_dense_constant_decoded_not_playback',m['identity'])
            self.assertTrue(m['binding_coverage_exact'],m['identity'])
            self.assertEqual(len(m['pptr_curve_mapping']),len(m['pptr_targets']))
    def test_binding_ambiguities_are_not_selected(self):
        counts=Counter(b['status'] for b in self.sections['animation_bindings'])
        self.assertEqual(counts,{'unique_target':51990,'unresolved_target':393,'ambiguous_targets':17})
        for b in self.sections['animation_bindings']:
            self.assertEqual(b['status']=='unique_target',len(b['component_targets'])==1)
            if b['binding']['typeID']==1:
                self.assertEqual(b['component_targets'],[p['gameobject'] for p in b['path_candidates']])
    def test_binding_targets_match_native_class_ids_not_name_guesses(self):
        index=json.loads((RAW/'index.json').read_bytes())
        classes={key(r):r['class_id'] for r in read_chunks(index,'objects')}
        for b in self.sections['animation_bindings']:
            expected=b['binding']['typeID']
            for target in b['component_targets']:
                actual=classes[key(target)]
                self.assertIn(actual,(4,224) if expected==4 else (expected,))

    def test_sprite_keys_are_discrete_and_source_table_indexed(self):
        checked=0
        for m in self.sections['motion']:
            for channel in m['discrete_pptr_keys']:
                self.assertIn('NEVER blend',channel['interpolation'])
                for k in channel['keys']:
                    i=k['mapping_index']
                    if i is not None and 0<=i<len(m['pptr_curve_mapping']):self.assertEqual(k['reference'],m['pptr_curve_mapping'][i]);checked+=1
        self.assertGreater(checked,0)
    def test_asset_closure_only_contains_typed_assets(self):
        assets={key(a['identity']) for a in self.sections['assets']}
        for r in self.data['roots']:self.assertTrue({key(i) for i in r['asset_identities']}<=assets)
        for a in self.sections['assets']:
            raw=self.consumer.raw(a['raw_location'])
            self.assertEqual(key(a['identity']),key(raw));self.assertEqual(a['type'],raw['type'])
    def test_button_sound_joins_exact_enum_registry_and_native_rule(self):
        sounds=[s for s in self.sections['sounds'] if s['class_name']=='Button_Sound' and s['value'] in (1,2)]
        self.assertTrue(sounds)
        for s in sounds:
            self.assertEqual(s['enum'],{1:'Sfx_ClickDown',2:'Sfx_ClickUp'}[s['value']])
            self.assertTrue(s['registry']['clip']);self.assertTrue(s['registry']['media_outputs'])
            self.assertTrue(s['native_rules'])
    def test_pause_recipe_is_consumable_with_raw_nonvisual_components(self):
        ri=next(i for i,r in enumerate(self.data['roots']) if r['label']=='Board_Pause')
        d=self.consumer.recipe(ri,True)
        self.assertEqual(len(d['nodes']),235)
        self.assertTrue(d['assets']);self.assertTrue(d['sounds']);self.assertTrue(d['motion'])
        raw={key(r):r for r in d['raw_objects']}
        for s in d['sounds']:self.assertIn(key(s['owner']),raw)
        for b in d['animation_bindings']:self.assertIn(key(b['clip']),{key(m['identity']) for m in d['motion']})
    def test_native_wing_sound_bridge_uses_proven_clip5(self):
        links=[s for r in self.data['roots'] for s in r['native_sound_links']]
        self.assertTrue(links)
        for s in links:
            self.assertEqual(s['clip_enum'],5);self.assertEqual(s['sound_enum'],'Sfx_Shot1')
            self.assertEqual(s['registry'],self.data['registry']['Sfx_Shot1'])
    def test_scene_camera_canvas_context_is_retained_not_assumed_global(self):
        self.assertTrue(any(c['type']=='Camera' for c in self.data['scene_context']))
        self.assertTrue(any(c['type']=='Canvas' for c in self.data['scene_context']))

if __name__=='__main__':unittest.main()
