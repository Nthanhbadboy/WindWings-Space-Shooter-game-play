import gzip,hashlib,json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'datas/l3_ef6b75ef134_native_refresh_leaves.json.gz'
PROBE=ROOT/'reverse-engineering/raw/owner134/probe.json.gz'
UP129=ROOT/'datas/l3_ef6b75ef129_native_owner_linkage.json.gz'
UP133=ROOT/'datas/l3_ef6b75ef133_native_builder_helpers.json.gz'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.load(gzip.open(p))
class Owner134Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=ART.read_bytes();cls.art=load(ART);cls.p=load(PROBE)
        cls.by={b['entry']:b for b in cls.art['bodies']}
        cls.wins={f['entry']:bytes.fromhex(f['hex']) for f in cls.p['functions']}
    def at(self,va,n=4):
        for e,w in self.wins.items():
            if e<=va<e+len(w):return w[va-e:va-e+n]
        return None
    def test_schema(self):
        self.assertEqual(sorted(self.art),['bodies','cluster','counts','focus','limits','notes','order','pins','provisional','seeds','slot_resolution'])
        self.assertIs(self.art['provisional'],True)
        self.assertTrue(self.art['limits'])
    def test_pins(self):
        p=self.art['pins']
        self.assertEqual(p['xapk_sha256'],'f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e')
        self.assertEqual(p['libunity_sha256'],'d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7')
        self.assertEqual(p['libunity_size'],17783496)
        self.assertEqual(p['probe']['sha256'],sha(PROBE.read_bytes()))
        self.assertEqual(p['probe']['size'],PROBE.stat().st_size)
        self.assertEqual(p['upstream']['129']['sha256'],sha(UP129.read_bytes()))
        self.assertEqual(p['upstream']['133']['sha256'],sha(UP133.read_bytes()))
    def test_tool_pins(self):
        for t,h in self.art['pins']['tools'].items():self.assertEqual(h,sha((ROOT/t).read_bytes()),t)
        self.assertEqual(len(self.art['pins']['tools']),2)
    def test_body_set(self):
        b=self.art['bodies']
        self.assertEqual(len(b),24)
        self.assertEqual(sum(1 for x in b if x['group']=='seed'),15)
        self.assertEqual(sum(1 for x in b if x['group']=='cluster_callee'),9)
        for x in b:self.assertEqual(x['body_sha256'],sha(self.wins[x['entry']]),hex(x['entry']))
        self.assertEqual([hex(x) for x in self.art['seeds']],['0x6d017c','0x6d14d4','0x6b2050','0x6b6dec','0x6b6fdc','0x6b82e8','0x6b2a0c','0x6b832c','0x6b22c8','0x572a9c','0x572834','0x5707c4','0x576c70','0x5770fc','0x49fe68'])
    def test_counts(self):
        c=self.art['counts']
        self.assertEqual(c['bodies'],24);self.assertEqual(c['facts'],211)
        self.assertEqual(c['seeds'],15);self.assertEqual(c['followed'],9)
        self.assertEqual(c['calls'],108);self.assertEqual(c['bl'],80)
        self.assertEqual(c['cluster_calls'],25);self.assertEqual(c['dispatch'],11)
        self.assertEqual(c['dispatch_rows_raw'],24);self.assertEqual(c['strings'],1)
        self.assertEqual(c['fields'],110);self.assertEqual(c['windows_bytes'],4424)
    def test_facts_bytes(self):
        import tools.verify.owner134 as v
        self.assertEqual(len(v.FACTS),211)
        for va,(hx,text,note) in v.FACTS.items():
            b=self.at(va)
            self.assertIsNotNone(b,hex(va))
            self.assertEqual(b.hex(),hx,hex(va))
            self.assertTrue(text and note)
    def test_accumulator(self):
        a=self.art['focus']['accumulator_word']
        self.assertEqual(a['entry'],0x6d14d4)
        self.assertEqual(a['extent'],0x30)
        self.assertEqual(a['guard'],{'slot':0x138,'bit':0,'clear_means':'no value'})
        self.assertEqual(a['value_field'],0x128)
        self.assertEqual(a['resolved_guard_slot'],0x6d137c)
        self.assertEqual(len(a['facts']),8)
        self.assertEqual(self.at(0x6d14e0).hex(),'089d40f9')
        self.assertEqual(self.at(0x6d14e8).hex(),'80000036')
    def test_producer_impl(self):
        p=self.art['focus']['producer_impl']
        self.assertEqual(p['entry'],0x6d017c)
        self.assertEqual(p['extent'],0x464)
        self.assertEqual(p['guard']['slot'],0x138)
        self.assertEqual(p['guard']['body_requires_empty'],'[node+0x160] == 0')
        self.assertEqual(p['source_field'],0x118)
        self.assertEqual(p['source_virtual_slot'],0xc8)
        self.assertEqual(p['element'],'int')
        self.assertEqual(p['resolve'],0x3d8614)
        self.assertEqual(p['per_element_slots'],[0x148,0x110])
        self.assertEqual(p['last_element_slot'],0x60)
        self.assertEqual(p['last_element_arg'],0x3d)
        self.assertEqual(p['vector'],{'base':0x150,'count':0x160,'grow':0x6bb944,'grow_params':[4,4],'push':0x6bb950})
        self.assertEqual(p['self_store_field'],0x178)
        self.assertEqual(p['returns'],'bool ([node+0x160] != 0)')
        self.assertEqual(len(p['facts']),51)
        for pc in (0x6d04f0,0x6d04f4,0x6d04f8,0x6d0520,0x6d0588):
            self.assertIn(pc,p['facts'])
        self.assertEqual(self.at(0x6d023c).hex(),'73be00f9')
        self.assertEqual(self.at(0x6d01bc).hex(),'e80100b4')
    def test_mirror(self):
        m=self.art['focus']['active_graph_mirror']
        self.assertEqual(m['pointer_field'],0x208);self.assertEqual(m['condition_byte'],0x1f1)
        self.assertEqual(m['mirror_byte'],0x188);self.assertEqual(m['writer'],0x6b6dec)
        self.assertEqual(m['writer_pcs'],[0x6b6fa8,0x6b6fb0,0x6b6fb8,0x6b6fbc])
        self.assertTrue(m['relation'].startswith('mirror byte = (pointer field != 0)'))
        self.assertIn('133',m['links'])
        self.assertEqual(self.at(0x6b6fb8).hex(),'e8079f1a')
        self.assertEqual(self.at(0x6b6fbc).hex(),'68220639')
    def test_apply(self):
        a=self.art['focus']['apply_step']
        self.assertEqual(a['entry'],0x6b6fdc)
        self.assertEqual(a['seed'],0x6b2ce8)
        self.assertEqual(a['seed_args'],[0x1b8,0x208,0xb0,0x640])
        self.assertEqual(a['per_entry'],[0x6b1538,0x6b2eec])
        self.assertEqual(a['per_entry_slot'],0x98)
        self.assertEqual(a['accumulator_byte'],0x491)
        self.assertEqual(a['driver_stride'],0x10)
        self.assertEqual(a['driver_flag_field'],0x160)
        self.assertEqual(a['driver_mask'],0xfffffffe)
        self.assertEqual(self.at(0x6b70b0).hex(),'68461239')
        self.assertEqual(self.at(0x6b7090).hex(),'8c791f12')
    def test_evaluate(self):
        e=self.art['focus']['evaluate_step']
        self.assertEqual(e['first_calls'],[0x6b6c40,0x6b6850])
        self.assertEqual(e['single_playable_path'],{'count_field':0x178,'count_value':1,'slot':0xb0})
        self.assertEqual(e['scratch']['release'],0x6b3e30)
        self.assertEqual(e['loop']['stride'],0x28)
        self.assertEqual(e['loop']['slot'],0xc0)
        self.assertEqual(e['counter_field'],0x610)
        self.assertEqual(self.at(0x6b6e7c).hex(),'1f0500f1')
        self.assertEqual(self.at(0x6b6fa8).hex(),'68c64739')
        self.assertEqual(self.at(0x6b6f90).hex(),'2895881a')
    def test_skin(self):
        s=self.art['focus']['skin_step']
        self.assertEqual(s['graph_field'],0x208);self.assertEqual(s['child_table_field'],0x1e0)
        self.assertEqual(s['steps'],[0x6b3c84,0x6bf2a0,0x6bf108,0x6bf1cc])
        self.assertEqual(s['mode_field'],0x190);self.assertEqual(s['mode_alloc'],1)
        self.assertEqual(s['alloc'],{'helper':0x51a81c,'size':0x40})
        self.assertEqual(s['tail'],0x6bf908)
        self.assertEqual(self.at(0x6b20e8).hex(),'01088052')
        self.assertEqual(self.at(0x6b20d8).hex(),'1f050071')
    def test_child_walk(self):
        c=self.art['focus']['child_walk']
        self.assertEqual(c['slot'],0xd0);self.assertEqual(c['holder_field'],0x30)
        self.assertEqual(c['count_offset'],0x30);self.assertEqual(c['index_getter'],0x6d788c)
        self.assertIs(c['recursive'],True)
        self.assertEqual(self.at(0x6b8378).hex(),'edffff97')
    def test_mode_select(self):
        m=self.art['focus']['mode_select']
        self.assertEqual(m['gate'],0x3d98bc);self.assertEqual(m['branch_byte'],0x189)
        self.assertEqual(m['mode_field'],0x18c);self.assertEqual(m['mode_value'],2)
        self.assertEqual(m['calls'],[0x5716c0,0x571174])
        self.assertEqual(self.at(0x6b22f8).hex(),'f5179f1a')
    def test_resolver(self):
        r=self.art['focus']['resolver']
        self.assertEqual(r['source_field'],0x19c);self.assertEqual(r['registry'],0x10e18b0)
        self.assertEqual(r['lookup'],0x38cbb4);self.assertEqual(r['fallback'],0x3d8614)
        self.assertEqual(self.at(0x6b6c58).hex(),'945a44f9')
    def test_handle_accessors(self):
        h=self.art['focus']['handle_accessors']
        self.assertEqual(h['map_strict'],{'entry':0x576c70,'handle_field':0x30,'mask':0xfffffffe,'payload_field':0x28,'flag_byte':0x38,'flag_bit':1,'returns_zero_when_set':True})
        self.assertEqual(h['map_plain']['entry'],0x5770fc)
        self.assertIs(h['map_plain']['flag_test'],False)
        self.assertEqual(h['identity']['field'],0x28)
        self.assertEqual(h['bit_test']['byte'],0xad)
        self.assertEqual(self.at(0x576c98).hex(),'3f011f72')
        self.assertEqual(self.at(0x577118).hex(),'001540f9')
    def test_vector_reset(self):
        r=self.art['focus']['vector_reset']
        self.assertEqual(r['entries'],[0x572a9c,0x6b82e8])
        self.assertEqual(r['sink'],0x3c9438);self.assertEqual(r['line'],0x306)
        self.assertEqual(r['fill_const'],0x143ff0)
        self.assertEqual(self.at(0x572ad4).hex(),'6006803d')
        self.assertEqual(self.at(0x6b8320).hex(),'6006803d')
    def test_deleter_and_formatter(self):
        d=self.art['focus']['deleter_slot']
        self.assertEqual(d['vtable_const'],0x10b0b30);self.assertEqual(d['callback_field'],0x10)
        self.assertEqual(d['cleared'],[0,0x18])
        f=self.art['focus']['format_helper']
        self.assertEqual(f['alloc'],{'helper':0x3c986c,'line':0x152,'element':4})
        self.assertEqual(f['fill'],{'helper':0x109ace0,'value':0xff})
        self.assertEqual(f['transforms'],[0x6d0964,0x6e46cc])
        self.assertEqual(f['free'],{'helper':0x3c9438,'line':0x19b})
        self.assertEqual(self.at(0x6b3d4c).hex(),'e59b2794')
    def test_reset_pairs(self):
        p=self.art['focus']['reset_pairs']
        self.assertEqual(p['count_field'],0x18);self.assertEqual(p['array_field'],0x8)
        self.assertEqual(p['stride'],0x10);self.assertEqual(p['sentinel'],0xffffffff)
        self.assertEqual(p['leaf'],0x49fdfc);self.assertEqual(p['tail'],0x49fee4)
        self.assertEqual(self.at(0x49fe9c).hex(),'3f040031')
    def test_samplers(self):
        s={x['entry']:x for x in self.art['focus']['samplers']}
        self.assertEqual(sorted(s),[0x6bf108,0x6bf1cc,0x6bf2a0])
        self.assertEqual(s[0x6bf2a0]['kind'],'float');self.assertEqual(s[0x6bf2a0]['load'],'ldr s0')
        self.assertEqual(s[0x6bf108]['count_field'],0x30);self.assertEqual(s[0x6bf108]['base_index_field'],0x20)
        self.assertEqual(s[0x6bf1cc]['kind_value'],0x0b);self.assertEqual(s[0x6bf1cc]['tests'],[0x6a99a4,0x6a99f0])
        self.assertEqual(self.at(0x6bf20c).hex(),'1f2d0071')
    def test_string(self):
        s=[x for b in self.art['bodies'] for x in b['strings']]
        self.assertEqual(len(s),1)
        self.assertEqual(s[0]['va'],0xe668b)
        self.assertEqual(s[0]['pc'],0x6d0520)
        self.assertTrue(s[0]['ascii'].startswith('An animator Reset was caused during %s::Awake. This will lead to'))
    def test_reset_warning(self):
        w=self.art['focus']['reset_warning']
        self.assertEqual(w['entry'],0x6d017c)
        self.assertEqual(w['string_va'],0xe668b)
        self.assertEqual(w['string_pc'],0x6d0520)
        self.assertTrue(w['format'].startswith('An animator Reset was caused during %s::Awake'))
        self.assertEqual(w['condition'],'source element count == 0 AND node vector count != 0')
        self.assertEqual(w['condition_pcs'],[0x6d04f0,0x6d04f4,0x6d04f8])
        self.assertEqual(w['message'],{'materialise':0x52e15c,'log':0xb2e604,'free':0x3c9438,'free_line':0x206})
        self.assertEqual(w['prefix_calls'],[0x6d05e0,0x6cee44])
        self.assertEqual(self.at(0x6d0524).hex(),'002c1a91')
        self.assertEqual(self.at(0x6d0588).hex(),'1f781194')
    def test_notes(self):
        n=self.art['notes']
        self.assertIn('+0x208',n['mirror_definition'])
        self.assertIn('+0x178',n['offset_class_warning'])
        self.assertIn('static' if 'static' in n['no_execution'] else 'executed',n['no_execution'])
    def test_slot_resolution(self):
        s=self.art['slot_resolution']
        self.assertEqual(s['slots'],{'40':0x6ce4fc,'80':0x3e079c,'224':0x6d017c,'264':0x6b6ab8,'312':0x6d137c})
        self.assertIn('129',s['source'])
        prod=self.art['focus']['producer_impl']
        self.assertEqual(prod['resolved_guard_slot'],0x6d137c)
    def test_bodies_consistent(self):
        for b in self.art['bodies']:
            self.assertEqual(b['words'],b['window_bytes']//4,hex(b['entry']))
            self.assertEqual(b['call_count'],len(b['calls']))
            self.assertLessEqual(b['window_bytes'],b['extent'])
            self.assertGreaterEqual(b['dispatch_rows_raw'],len(b['dispatch']))
    def test_render_deterministic(self):
        import tools.verify.owner134 as v
        one=v.render(v.build());two=v.render(v.build())
        self.assertEqual(one,two);self.assertEqual(one,self.raw)
        self.assertEqual(self.raw[:8].hex(),'1f8b080000000000')
    def test_check_mode(self):
        out=subprocess.run([sys.executable,'tools/verify/owner134.py','--check'],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(out.returncode,0,out.stderr)
        self.assertIn('check ok',out.stdout)
    def test_no_floats(self):
        def walk(x):
            if isinstance(x,dict):
                for v in x.values():walk(v)
            elif isinstance(x,list):
                for v in x:walk(v)
            elif isinstance(x,float):self.fail('float in artifact')
        walk(self.art)
if __name__=='__main__':unittest.main()
