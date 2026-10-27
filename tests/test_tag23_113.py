import copy,gzip,json,struct,unittest
from pathlib import Path
from tools.verify import tag23_113 as report
from tools.verify.tag23_113_native import Fixture,registration,registered_fixture,dispatch,resolve,callbacks,type_records,binding_policy

def patch(raw,address,data):
    raw=copy.deepcopy(raw)
    blocks=raw['windows']+raw['native_slices']+raw['pointed_strings']+[o for s in raw['strings'] for o in s['occurrences']]
    changed=0
    for w in blocks:
        b=bytearray.fromhex(w['hex']);offset=address-w['va']
        if 0<=offset and offset+len(data)<=len(b):b[offset:offset+len(data)]=data;w['hex']=b.hex();changed+=1
    assert changed
    return raw

class NativeTag23(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=report.load_raw();cls.saved=json.load(gzip.open(report.OUT));cls.binding=cls.saved['model_bridge']['binding']['binding']
    def test_01_inputs_pinned(self):
        for p,h in self.saved['inputs'].items():self.assertEqual(report.digest(report.ROOT/p),h,p)
    def test_02_recovery_source_pinned(self):self.assertEqual(self.raw['tool_sha256'],report.digest(report.ROOT/'tools/recovery/tag23_113.py'))
    def test_03_component_static_record(self):
        r=type_records(self.raw)[0];self.assertEqual((r['name'],r['class_id'],r['descriptor']),('SpriteRenderer',212,0x10ead38))
    def test_04_value_static_record(self):
        r=type_records(self.raw)[1];self.assertEqual((r['name'],r['class_id'],r['descriptor']),('Sprite',213,0x10e8fe0))
    def test_05_native_registry_stores(self):
        r=registration(self.raw);self.assertEqual((r['map_length'],r['map_tag'],r['map_type_descriptor']),(1,23,0x10ead38));self.assertEqual(r['slot_23'],r['handler']);self.assertEqual(r['handler_vtable'],0x10b9d80)
    def test_06_registry_is_not_hooked(self):
        r=registration(self.raw);self.assertEqual(r['hooks'],[0x3c9298]);self.assertTrue({0x492da8,0x6a9d50,0x6a97a0,0x6a97f0}.issubset(r['run']['executed_addresses']))
    def test_07_absent_service(self):
        r=registration(self.raw,False);self.assertEqual(r['map_length'],0);self.assertFalse(r['allocator_calls']);self.assertEqual(r['slot_23'],0)
    def test_08_registration_counterfactual_tag24(self):
        r=registration(patch(self.raw,0x94026c,struct.pack('<I',0x52800302)));self.assertEqual(r['map_tag'],24);self.assertEqual(r['slot_23'],0)
    def test_09_native_dispatch(self):
        r=dispatch(self.raw);self.assertEqual(r['output']['tag'],23);self.assertEqual(r['lookup']['return_value'],0x10e8fe0);self.assertEqual(r['output']['handler'],r['registration']['handler'])
    def test_10_unregistered_slot_in_isolated_fixture(self):self.assertEqual(dispatch(self.raw,tag=22)['lookup']['return_value'],0)
    def test_11_foreign_class_in_fixture_service(self):self.assertEqual(dispatch(self.raw,type_id=214)['lookup']['return_value'],0)
    def test_12_native_virtual_reader(self):self.assertEqual(dispatch(self.raw,value=0x11223344)['read']['return_value'],0x11223344)
    def test_13_native_virtual_writer(self):
        r=dispatch(self.raw,value=0x11223344);self.assertEqual(r['setter_sink_calls'],[dict(object=r['output']['object'],value=0x11223344)])
    def test_14_reader_offset_counterfactual(self):
        word=struct.unpack('<I',bytes.fromhex(next(w for w in self.raw['native_slices'] if w['va']==0x946cd8)['hex'])[0x946d04-0x946cd8:0x946d08-0x946cd8])[0]
        r=callbacks(patch(self.raw,0x946d04,struct.pack('<I',word+(1<<10))));self.assertEqual(r['read']['return_value'],0)
    def test_15_relocated_reader_counterfactual(self):
        raw=copy.deepcopy(self.raw)
        next(r for r in raw['relocations'] if r['address']==0x10b9d98)['addend']=0x946cd8
        self.assertNotEqual(dispatch(raw)['read']['return_value'],0x12345678)
    def test_16_inline_property(self):self.assertEqual(resolve(self.raw)['return_value'],1)
    def test_17_external_property(self):self.assertEqual(resolve(self.raw,inline=False)['return_value'],1)
    def test_18_inline_mode_is_one(self):
        f=Fixture(self.raw);a=f.smallstring('m_Sprite',True);self.assertEqual(f.u.mem_read(a+32,1),b'\1')
    def test_19_flag_zero_rejected(self):self.assertEqual(resolve(self.raw,flags=0)['return_value'],0)
    def test_20_other_bit_rejected(self):self.assertEqual(resolve(self.raw,flags=2)['return_value'],0)
    def test_21_low_bit_not_exact_flag_equality(self):self.assertEqual(resolve(self.raw,flags=3)['return_value'],1)
    def test_22_exact_not_prefix_or_casefold(self):
        for name in ('m_Sprit','m_SpriteX','M_Sprite','m_Color',''):
            self.assertEqual(resolve(self.raw,name)['return_value'],0,name)
    def test_23_output_only_attribute_word_changed(self):self.assertEqual(resolve(self.raw)['output_hex'],'a5a5a5a500000000a5a5a5a5a5a5a5a5')
    def test_24_reject_leaves_output_untouched(self):self.assertEqual(resolve(self.raw,'m_Color')['output_hex'],'a5'*16)
    def test_25_original_string_counterfactual(self):
        raw=patch(self.raw,0x138aef,b'm_Colour\0');self.assertEqual(resolve(raw)['return_value'],0);self.assertEqual(resolve(raw,'m_Colour')['return_value'],1)
    def test_26_missing_string_fails_closed(self):
        raw=copy.deepcopy(self.raw)
        for s in raw['strings']:
            if s['text']=='m_Sprite':s['occurrences']=[]
        raw['pointed_strings']=[w for w in raw['pointed_strings'] if w['va']!=0x138aef]
        with self.assertRaises(Exception):resolve(raw)
    def test_27_missing_relocation_fails_closed(self):
        raw=copy.deepcopy(self.raw);raw['relocations']=[r for r in raw['relocations'] if r['address']!=raw['registry_vtable']+24]
        with self.assertRaises(Exception):registration(raw)
    def test_28_second_fixture_address(self):
        r=dispatch(self.raw,base=0x7000000);self.assertEqual(r['lookup']['return_value'],0x10e8fe0);self.assertEqual(r['read']['return_value'],0x12345678);self.assertEqual(r['registration']['map_tag'],23)
    def test_29_source_derived_opt_in_policy(self):self.assertEqual(binding_policy(self.raw,self.binding,212),'m_Sprite')
    def test_30_policy_rejects_changed_binding(self):
        for k,v in dict(attribute=1,customType=24,typeID=213,isPPtrCurve=0,isIntCurve=1,isSerializeReferenceCurve=1,script={'m_FileID':1,'m_PathID':1}).items():
            b=dict(self.binding);b[k]=v
            with self.assertRaises(ValueError,msg=k):binding_policy(self.raw,b,212)
    def test_31_policy_rejects_foreign_target(self):
        with self.assertRaises(ValueError):binding_policy(self.raw,self.binding,213)
    def test_32_model_bridge_keeps_default_rejection(self):
        m=self.saved['model_bridge'];self.assertIn('explicit field policy',m['default_rejection']);self.assertEqual(m['binding']['binding_index'],48);self.assertEqual(m['target_class_id'],212)
    def test_33_opt_in_model_readback_not_unity(self):
        m=self.saved['model_bridge'];self.assertEqual(len(m['samples']),6)
        self.assertEqual([s['sprite_write']['runtime_reference']['path_id'] for s in m['samples']],[3799,2633,3799,2633,3799,2633])
        for s in m['samples']:
            self.assertEqual(s['write_count'],51);self.assertEqual(s['sprite_write']['field'],'m_Sprite');self.assertEqual(s['readback'],['data.unity3d/resources.assets',s['sprite_write']['runtime_reference']['path_id']])
        self.assertIn('no projection/render',m['scope'])
if __name__=='__main__':unittest.main()
