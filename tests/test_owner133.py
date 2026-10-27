import gzip,hashlib,json,struct,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'datas/l3_ef6b75ef133_native_builder_helpers.json.gz'
PROBE=ROOT/'reverse-engineering/raw/owner133/probe.json.gz'
UP129=ROOT/'datas/l3_ef6b75ef129_native_owner_linkage.json.gz'
UP132=ROOT/'datas/l3_ef6b75ef132_native_dispatch_owners.json.gz'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.load(gzip.open(p))
class Owner133Test(unittest.TestCase):
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
        self.assertEqual(sorted(self.art),['bodies','cluster','correction','counts','focus','limits','order','pins','provisional','seeds','slot_resolution'])
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
        self.assertEqual(p['upstream']['132']['sha256'],sha(UP132.read_bytes()))
    def test_tool_pins(self):
        for t,h in self.art['pins']['tools'].items():self.assertEqual(h,sha((ROOT/t).read_bytes()),t)
        self.assertEqual(len(self.art['pins']['tools']),2)
    def test_body_set(self):
        b=self.art['bodies']
        self.assertEqual(len(b),22)
        self.assertEqual(sum(1 for x in b if x['group']=='seed'),11)
        self.assertEqual(sum(1 for x in b if x['group']=='cluster_callee'),11)
        for x in b:self.assertEqual(x['body_sha256'],sha(self.wins[x['entry']]),hex(x['entry']))
    def test_extents(self):
        e={k:self.by[k]['extent'] for k in self.by}
        self.assertEqual(e[0x6b8054],0x8c);self.assertEqual(e[0x6b80e0],0xe4)
        self.assertEqual(e[0x6cefdc],0x20);self.assertEqual(e[0x6b753c],0x38)
        self.assertEqual(e[0x6b7c58],0xa0);self.assertEqual(e[0x6b92c4],0x28)
        self.assertEqual(e[0x6b97d0],0x1c4);self.assertEqual(e[0x6b9638],0x198)
        self.assertEqual(e[0x6b3e30],0x38)
    def test_facts_bytes(self):
        self.assertEqual(self.art['counts']['facts'],144)
        import tools.verify.owner133 as v
        for va,(hx,text,note) in v.FACTS.items():
            b=self.at(va)
            self.assertIsNotNone(b,hex(va))
            self.assertEqual(b.hex(),hx,hex(va))
            self.assertTrue(note)
    def test_fact_count_and_annotation(self):
        self.assertEqual(len(self.art['counts']),11)
        self.assertEqual(self.art['counts']['facts'],144)
        self.assertEqual(self.art['counts']['bodies'],22)
        self.assertEqual(self.art['counts']['calls'],73)
        self.assertEqual(self.art['counts']['bl'],55)
        self.assertEqual(self.art['counts']['cluster_calls'],27)
        self.assertEqual(self.art['counts']['dispatch'],1)
        self.assertEqual(self.art['counts']['dispatch_rows_raw'],2)
        self.assertEqual(self.art['counts']['strings'],2)
        self.assertEqual(self.art['counts']['windows_bytes'],2716)
    def test_create_output(self):
        c=self.art['focus']['create_output']
        self.assertEqual(c['entry'],0x6b8054)
        self.assertEqual(c['alloc'],{'size':0xe0,'tag':0x5e,'align':8,'label':0x12da21,'line':0x56})
        self.assertEqual(c['ctor'],0x6ce464)
        self.assertEqual(c['list_anchor_offset'],0x78)
        self.assertEqual(c['call_targets'],[0x3c9298,0x6ce464])
        self.assertEqual(self.at(0x6b806c)[:4].hex(),'001c8052')
        self.assertEqual(self.at(0x6b807c)[:4].hex(),'8744f497')
        self.assertEqual(self.at(0x6b8090)[:4].hex(),'a9e20191')
    def test_playable_record(self):
        r=self.art['focus']['playable_record']
        self.assertEqual(r['stride'],0x28)
        self.assertEqual(r['base_field'],0x168)
        self.assertEqual(r['count_field'],0x178)
        self.assertEqual(r['aux_field'],0x20)
        self.assertEqual(r['push'],0x6bbae4)
        self.assertEqual(r['insert'],0x6b9994)
    def test_binding(self):
        b=self.art['focus']['playable_binding']
        self.assertEqual(b['bind'],0x6b97d0)
        self.assertEqual(b['unbind'],0x6b9638)
        self.assertEqual(b['setter'],0x6ce4b4)
        self.assertEqual(b['guard'],{'field':0x194,'bit':4})
        self.assertEqual(b['assert_bind']['hex'],'0xcf1dc')
        self.assertEqual(b['assert_unbind']['hex'],'0x126b27')
        self.assertEqual(len(b['strings']),2)
        self.assertTrue(b['strings'][0]['ascii'].startswith('Cannot bind playable while the Animator is being evaluated'))
        self.assertTrue(b['strings'][1]['ascii'].startswith('Cannot unbind playable while the Animator is being evaluated'))
        self.assertEqual([x['va'] for x in b['strings']],[0xcf1dc,0x126b27])
        self.assertEqual(b['refresh_rule'],{'guard_bit':7,'requires_initialized':0x188,'action':0x6b92c4})
        self.assertEqual(self.at(0x6b988c)[:4].hex(),'a0d0ffd0')
        self.assertEqual(self.at(0x6b970c)[:4].hex(),'60d3ffb0')
    def test_refresh_composite(self):
        r=self.art['focus']['refresh_composite']
        self.assertEqual(r['entry'],0x6b92c4)
        self.assertEqual(r['steps'],[0x6b2050,0x6b6d60,0x6b6dec,0x6b6fdc])
        self.assertEqual(r['tail'],[0x6b6fdc])
        self.assertEqual([c for c in r['steps'] if c not in r['tail']],[0x6b2050,0x6b6d60,0x6b6dec])
    def test_producer(self):
        p=self.art['focus']['producer']
        self.assertEqual(p['entry'],0x6cefdc)
        self.assertEqual(p['extent'],0x20)
        self.assertEqual(p['first_call'],0x6cf7b4)
        self.assertEqual(p['vtable_slot'],0xe0)
        self.assertTrue(p['tail_branch'])
        self.assertEqual(p['resolved_target'],0x6d017c)
        self.assertEqual(self.at(0x6ceff0)[:4].hex(),'017140f9')
        self.assertEqual(self.at(0x6ceff8)[:4].hex(),'20001fd6')
    def test_collector(self):
        c=self.art['focus']['collector']
        self.assertEqual(c['entry'],0x6b7c58)
        self.assertEqual(c['source_field'],0x208)
        self.assertEqual(c['stride'],0x20)
        self.assertEqual(c['type_tag'],0x16)
        self.assertEqual(c['value_field'],0x18)
        self.assertEqual(c['destination'],0x4e0)
        self.assertEqual(c['append'],0x6bb9ac)
        self.assertEqual(c['append_value_source'],'object+8')
        self.assertEqual(self.at(0x6b7ca8)[:4].hex(),'5f590071')
    def test_refresher(self):
        r=self.art['focus']['refresher']
        self.assertEqual(r['entry'],0x6b80e0)
        self.assertEqual(r['driver_vector'],0x498)
        self.assertEqual(r['entry_slot'],0xa8)
        self.assertEqual(r['accumulator'],0x4b8)
        self.assertEqual(r['per_record'],0x6d14d4)
        self.assertEqual(r['dispatch'],[0xa8])
        self.assertIsNone(self.art['bodies'][[b['entry'] for b in self.art['bodies']].index(0x6b80e0)]['dispatch'][0]['resolved_target'])
        self.assertEqual(self.at(0x6b8134)[:4].hex(),'085540f9')
    def test_destructors(self):
        d=self.art['focus']['destructors']
        self.assertEqual([x['entry'] for x in d],[0x6b753c,0x6b3e30])
        for x in d:
            self.assertEqual(x['sink'],[0x3c9438])
            self.assertEqual(x['line'],0x306)
            self.assertEqual(x['label'],0x12da21)
    def test_growth_thunks(self):
        g={x['entry']:x for x in self.art['focus']['growth_thunks']}
        self.assertEqual(sorted(g),[0x6b9f6c,0x6bba08])
        self.assertEqual(g[0x6bba08]['thunk'],3)
        self.assertEqual(g[0x6b9f6c]['thunk'],3)
        self.assertEqual(g[0x6bba08]['extent'],12);self.assertEqual(g[0x6b9f6c]['extent'],12)
        self.assertEqual(self.at(0x6bba08)[:4].hex(),'81008052')
        self.assertEqual(self.at(0x6bba10)[:4].hex(),'08d9f417')
    def test_correction_block(self):
        c=self.art['correction']
        self.assertEqual(c['previous_cycle'],'132')
        self.assertIn('growth',c['current_reading'])
        ev={x['address']:(x['element'],x['align'],x['target']) for x in c['evidence']}
        self.assertEqual(ev[0x6bba08],(4,4,0x3f1e30))
        self.assertEqual(ev[0x6b9f6c],(0x28,8,0x3f1cb4))
        self.assertEqual(len(c['prior_132_thunks']),3)
    def test_slot_resolution(self):
        s=self.art['slot_resolution']
        self.assertEqual(s['slots'],{'40':0x6ce4fc,'80':0x3e079c,'224':0x6d017c,'264':0x6b6ab8,'312':0x6d137c})
        self.assertIn('129',s['source'])
    def test_bodies_are_byte_consistent(self):
        for b in self.art['bodies']:
            self.assertEqual(b['words'],b['window_bytes']//4,hex(b['entry']))
            self.assertEqual(b['call_count'],len(b['calls']))
            self.assertLessEqual(b['window_bytes'],b['extent'])
            self.assertGreaterEqual(b['dispatch_rows_raw'],len(b['dispatch']))
    def test_render_deterministic(self):
        import tools.verify.owner133 as v
        one=v.render(v.build());two=v.render(v.build())
        self.assertEqual(one,two);self.assertEqual(one,self.raw)
        self.assertEqual(self.raw[:8].hex(),'1f8b080000000000')
    def test_check_mode(self):
        out=subprocess.run([sys.executable,'tools/verify/owner133.py','--check'],cwd=ROOT,capture_output=True,text=True)
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
