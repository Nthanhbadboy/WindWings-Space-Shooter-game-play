import ast,copy,gzip,json,struct,unittest
from tools.verify.controller112 import ROOT,RAW,OUT,build,core,flatten,sha
from tools.verify.controller112_native import generate
class NativeSchema112(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.raw=json.loads(gzip.decompress(RAW.read_bytes()));cls.saved=json.loads(gzip.decompress(OUT.read_bytes()));cls.gen=cls.saved['native_generation']
    def test_01_regeneration(self):self.assertEqual(build(),self.saved)
    def test_02_input_pins(self):
        for p,h in self.saved['inputs'].items():self.assertEqual(sha((ROOT/p).read_bytes()),h,p)
    def test_03_281_nodes(self):self.assertEqual(len(flatten(self.gen['schema'])),281)
    def test_04_single_allocator_hook(self):self.assertEqual(self.gen['sink_hooks'],[0x5eb544])
    def test_05_native_root_version5(self):self.assertEqual(self.gen['schema']['version'],5)
    def test_06_eight_root_fields(self):self.assertEqual([c['name'] for c in self.gen['schema']['children']],['m_Name','m_ControllerSize','m_Controller','m_TOS','m_AnimationClips','m_StateMachineBehaviourVectorDescription','m_StateMachineBehaviours','m_MultiThreadedStateMachine'])
    def test_07_core_full_equality(self):self.assertTrue(self.saved['all_four_core_fields_and_hierarchy_equal_builtin'])
    def test_08_308full_trees(self):self.assertEqual(self.saved['full_trees_equal'],308)
    def test_09_291564_payload_bytes(self):self.assertEqual(self.saved['decoded_payload_bytes'],291564)
    def test_10_616_selector_rows(self):self.assertEqual(self.saved['selector_transition_count'],616)
    def test_11_533_ordinary_rows(self):self.assertEqual(self.saved['ordinary_transition_count'],533)
    def test_12_native_selector_two_fields(self):
        ts=[t for t in self.saved['transition_type_schemas'] if t['type']=='SelectorTransitionConstant'];self.assertEqual(len(ts),1);self.assertEqual([f['name'] for f in ts[0]['fields']],['m_Destination','m_ConditionConstantArray'])
    def test_13_native_ordinary13fields(self):
        ts=[t for t in self.saved['transition_type_schemas'] if t['type']=='TransitionConstant'];self.assertEqual(len(ts),2);self.assertEqual([len(t['fields']) for t in ts],[13,13])
    def test_14_interruption_present_only_ordinary(self):
        for t in self.saved['transition_type_schemas']:self.assertEqual('m_InterruptionSource' in [f['name'] for f in t['fields']],t['type']=='TransitionConstant')
    def test_15_balanced280_native_end(self):
        for op in ('begin','end'):self.assertEqual(sum(e['op']==op for e in self.gen['events']),280)
    def test_16_native_align18(self):self.assertEqual(sum(e['op']=='align' for e in self.gen['events']),18)
    def test_17_libunity_pin(self):self.assertEqual(self.saved['libunity_sha256'],'d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7')
    def test_18_native_bytes_from_elf_exec_spans(self):
        for pc in self.gen['executed_addresses']:self.assertTrue(any(s['flags']&1 and s['va']<=pc<s['va']+s['file_size'] for s in self.raw['segments']))
    def test_19_rela_original_hex(self):
        for r in self.raw['native_evidence']['relocations']:self.assertEqual(struct.unpack('<QQq',bytes.fromhex(r['hex'])),(r['address'],1027,r['addend']))
    def test_20_native_instruction_count(self):self.assertEqual(self.gen['instruction_count'],74714);self.assertEqual(len(self.gen['executed_addresses']),3186)
    def test_21_hook_not_counted_native_instruction(self):self.assertNotIn(0x5eb544,self.gen['executed_addresses']);self.assertEqual(self.gen['code_hook_visits'],self.gen['instruction_count']+280+1)
    def test_22_guarded_source_data_reads(self):self.assertEqual(len(self.gen['source_reads']),31)
    def test_23_mutate_native_bool_size(self):
        r=copy.deepcopy(self.raw);pc=0xb7e3c4;v=next(v for v in r['native_evidence']['ranges'] if v['va']<=pc<v['va']+len(v['hex'])//2);b=bytearray.fromhex(v['hex']);pos=pc-v['va'];op=struct.unpack_from('<I',b,pos)[0];struct.pack_into('<I',b,pos,(op&~(65535<<5))|(2<<5));v['hex']=b.hex();s=generate(r)['schema'];self.assertEqual(s['children'][-1]['byte_size'],2)
    def test_24_mutate_original_field_string(self):
        r=copy.deepcopy(self.raw);s=next(s for s in r['strings'] if s['text']=='m_Destination')
        for o in s['occurrences']:o['hex']=b'm_DestinatioX\0'.hex()
        ns=[n for p,n in flatten(generate(r)['schema']) if n['type']=='SelectorTransitionConstant'];self.assertEqual(ns[0]['children'][0]['name'],'m_DestinatioX')
    def test_25_missing_float_literal_fails_not_zero_filled(self):
        r=copy.deepcopy(self.raw);r['native_evidence']['cells']=[c for c in r['native_evidence']['cells'] if c['va']!=0x149c00]
        with self.assertRaises(ValueError):generate(r)
    def test_26_missing_relocations_fail(self):
        r=copy.deepcopy(self.raw);r['native_evidence']['relocations']=[]
        with self.assertRaises(ValueError):generate(r)
    def test_27_missing_pptr_code_fails(self):
        r=copy.deepcopy(self.raw);r['native_evidence']['ranges']=[v for v in r['native_evidence']['ranges'] if v['va']!=0x3b4200]
        with self.assertRaises(ValueError):generate(r)
    def test_28_query_labels_not_schema_input(self):
        r=copy.deepcopy(self.raw);r.pop('query_schema_sha256')
        for s in r['strings']:s['text']='not_a_layout'
        for x in r['references']:x['field']='not_a_layout'
        self.assertEqual(generate(r)['schema'],self.gen['schema'])
    def test_29_object_address_counterfixture(self):self.assertEqual(generate(self.raw,object_address=0x7000000)['schema'],self.gen['schema'])
    def test_30_native_generator_has_no_database_file_io(self):
        t=ast.parse((ROOT/'tools/verify/controller112_native.py').read_text());names={n.id for n in ast.walk(t) if isinstance(n,ast.Name)};self.assertFalse({'open','Path','json','UnityPy'}&names)
    def test_31_all_payload_consumed(self):
        for r in self.saved['controller_results']:self.assertEqual(r['consumed'],r['byte_size']);self.assertEqual(r['decoded_tree_sha256'],r['baseline_tree_sha256'])
    def test_32_array_typeflags_native(self):
        arrays=[n for p,n in flatten(self.gen['schema']) if n['type']=='Array'];self.assertTrue(arrays);self.assertEqual({n['type_flags']&1 for n in arrays},{1})
    def test_33_limits_not_unity_readback(self):self.assertIn('NOT live Unity TypeTree readback',self.saved['scope']);self.assertTrue(any('class91 registration' in s for s in self.saved['limits']))
if __name__=='__main__':unittest.main()
