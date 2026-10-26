import gc,gzip,hashlib,json,unittest
from tools.verify.l3_native_cfg import interpret
from tools.verify.l3_class_hierarchy import hierarchy,lineage
from tools.verify.l3_ui_drivers import build,load,RAW_NATIVE,OUT
from tools.verify.l3_recipe import Recipes
from tools.verify.l3_chain_graph import key

class CFGFixtures(unittest.TestCase):
    def run_cfg(self,ops,decls=None,relocs=None,literals=None,static=False):
        return interpret([dict(pc=i*4,mnemonic=m,op_str=o,writes=w) for i,(m,o,w) in enumerate(ops)],decls or {},relocs or {},literals or {},static)
    def test_divergent_values_merge_to_unknown_not_last_path(self):
        p=self.run_cfg([('mov','x19, x0',['x19']),('cbz','w1, #0x10',[]),('mov','w1, #1',['w1']),('b','#0x14',[]),('mov','w1, #0',['w1']),('bl','#0x100',['lr']),('ret','',[])])
        self.assertIsNone(p['calls'][0]['arguments'][1]);self.assertEqual(p['calls'][0]['arguments'][0]['kind'],'this')
    def test_unsupported_write_kills_old_receiver(self):
        p=self.run_cfg([('eor','x0, x0, x1',['x0']),('bl','#0x100',['lr']),('ret','',[])])
        self.assertIsNone(p['calls'][0]['arguments'][0])
    def test_callee_clobbers_caller_saved_but_not_callee_saved(self):
        p=self.run_cfg([('mov','x19, x0',['x19']),('bl','#0x100',['lr']),('mov','x0, x19',['x0']),('bl','#0x104',['lr']),('ret','',[])])
        self.assertEqual(p['calls'][1]['arguments'][0]['kind'],'this');self.assertIsNone(p['calls'][1]['arguments'][1])
    def test_got_relocation_then_literal_slot(self):
        p=self.run_cfg([('adrp','x8, #0x2000',['x8']),('ldr','x8, [x8, #0x30]',['x8']),('ldr','x1, [x8]',['x1']),('bl','#0x100',['lr']),('ret','',[])],relocs={0x2030:0x3000},literals={0x3000:['Hide']})
        self.assertEqual(p['calls'][0]['arguments'][1]['values'],['Hide'])
    def test_gameobject_getter_preserves_symbolic_receiver(self):
        d={0x100:[dict(namespace='UnityEngine',**{'class':'Component'},method='get_gameObject')]}
        p=self.run_cfg([('bl','#0x100',['lr']),('mov','w1, wzr',['w1']),('b','#0x104',[])],d)
        self.assertEqual(p['calls'][1]['arguments'][0]['kind'],'component_gameobject');self.assertEqual(p['calls'][1]['arguments'][1]['value'],0)
        transform=self.run_cfg([('bl','#0x100',['lr']),('bl','#0x104',['lr']),('ret','',[])],{0x100:[dict(namespace='UnityEngine',**{'class':'Component'},method='get_transform')]})
        self.assertEqual(transform['calls'][1]['arguments'][0]['kind'],'component_transform')
    def test_static_argument_is_not_this(self):
        p=self.run_cfg([('bl','#0x100',['lr']),('ret','',[])],static=True)
        self.assertEqual(p['calls'][0]['arguments'][0]['kind'],'argument')
    def test_unreachable_call_not_reported(self):
        p=self.run_cfg([('b','#0x8',[]),('bl','#0x100',['lr']),('ret','',[])])
        self.assertEqual(p['calls'],[])
    def test_namespace_qualified_inheritance_does_not_global_match(self):
        text='// Namespace: A\npublic class Child : Base // TypeDefIndex: 1\n{}\n// Namespace: B\npublic class Base // TypeDefIndex: 2\n{}'
        self.assertEqual(lineage(('A','Child'),hierarchy(text)),[('A','Child')])

class UIDrivers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d=load();cls.r=Recipes()
    @classmethod
    def tearDownClass(cls):cls.d=cls.r=None;gc.collect()
    def test_regenerate_every_cfg_call_and_serialized_receiver_join(self):
        self.assertEqual(build(),self.d);self.assertLess(OUT.stat().st_size,5_000_000)
    def test_raw_method_bytes_and_relocation_records_are_pinned(self):
        i=json.loads((RAW_NATIVE/'index.json').read_bytes())
        for f in i['files']:self.assertEqual(hashlib.sha256((RAW_NATIVE/f['path']).read_bytes()).hexdigest(),f['sha256'])
        n=json.load(gzip.open(RAW_NATIVE/'method-bytes.json.gz'))
        for m in n['methods']:self.assertEqual(len(bytes.fromhex(m['hex'])),m['width'])
        self.assertEqual(len(n['methods']),1074)
    def test_conservative_resolution_counts_remain_explicit(self):
        self.assertEqual(self.d['counts']['receiver_status'],dict(resolved_serialized_receiver=1414,receiver_not_statically_resolved=337))
        self.assertEqual(self.d['counts']['inherited_event_candidates'],9)
    def test_popup_exit_resolves_hide_trigger_and_exact_controller(self):
        e=next(e for e in self.d['effects'] if e['owner']['path_id']==644901 and e['method']=='OnPressedButtonExit')
        self.assertEqual(e['receiver']['path_id'],495980);self.assertEqual(e['argument']['values'],['Hide'])
        self.assertEqual(e['animator_routes'][0]['controller']['path_id'],1974)
        self.assertEqual(e['animator_routes'][0]['transition']['destination_index'],1)
        confirm=next(m for m in self.d['methods'] if m['cls']=='Popup_Notices' and m['method']=='OnPressedButtonConfirm')
        self.assertTrue(any(b['symbolic_operand']==dict(kind='field',base=dict(kind='this',index=0),offset=0x38) for b in confirm['cfg']['branches']))
        self.assertEqual(self.d['declared_field_offsets']['Popup_Notices']['56']['name'],'exitAfterConfirm')
    def test_offboard_resolves_same_go_deactivation_not_arbitrary_object(self):
        e=next(e for e in self.d['effects'] if e['owner']['path_id']==644901 and e['method']=='OffBoard')
        self.assertEqual(e['receiver']['path_id'],57508);self.assertEqual(e['argument']['value'],0)
    def test_direct_callee_expansion_requires_exact_rva_and_receiver(self):
        for e in self.d['effects']:
            for i in e['direct_callee_effect_indices']:
                callee=self.d['effects'][i]
                self.assertEqual(key(callee['owner']),key(e['receiver']))
                self.assertEqual(self.d['methods'][callee['method_index']]['rva'],e['target_rva'])
    def test_animation_event_links_back_to_native_offboard(self):
        entry=next(e for e in self.d['callback_entries'] if e['callback_index']==1454)
        effects=[self.d['effects'][i] for i in entry['effect_indices']]
        self.assertTrue(any(e['method']=='OffBoard' and e['owner']['path_id']==644901 for e in effects))
    def test_inherited_offboard_candidate_is_kept_separate_from_runtime_delivery(self):
        e=next(e for e in self.d['inherited_events'] if e['owner']['path_id']==496687)
        self.assertEqual(e['candidates'][0]['component']['path_id'],594188)
        self.assertEqual(e['candidates'][0]['declared_in']['cls'],'Popup_Notices')
        self.assertIn('not_runtime_delivery',e['status'])
    def test_recipe_contains_native_effects_and_global_index_reference(self):
        p=self.r.recipe(10);self.assertEqual(p['native_ui']['artifact'],'datas/l3_ui_drivers.json.gz')
        owners={key(c['identity']) for n in p['nodes'] for c in n['component_identities']}
        self.assertTrue(p['native_ui']['effects'])
        self.assertTrue(all(key(e['owner']) in owners for e in p['native_ui']['effects']))

if __name__=='__main__':unittest.main()
