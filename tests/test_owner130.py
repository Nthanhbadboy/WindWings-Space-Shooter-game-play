import gzip,hashlib,json,unittest
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'datas/l3_ef6b75ef130_native_update_trigger.json.gz'
PROBE=ROOT/'reverse-engineering/raw/owner130/probe.json.gz'
PROBE_B=ROOT/'reverse-engineering/raw/owner130b/probe.json.gz'
TOOLS=('tools/recovery/owner130.py','tools/recovery/owner130b.py','tools/verify/owner130.py')
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.load(gzip.open(p))
class Owner130Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=ART.read_bytes();cls.art=load(ART)
        cls.a=load(PROBE);cls.b=load(PROBE_B)
        cls.win={}
        for r in (cls.a,cls.b):
            for w in r['windows']:
                code=bytes.fromhex(w['hex'])
                if w['va'] not in cls.win or len(code)>len(cls.win[w['va']]):cls.win[w['va']]=code
    def at(self,va):
        for base,code in self.win.items():
            if base<=va<base+len(code):return code[va-base:]
        return None
    def test_schema(self):
        self.assertEqual(sorted(self.art),['call_edges','chain','counts','facts','field_map','indirect','limits','provisional','related_offsets','sources','vtable'])
        self.assertIs(self.art['provisional'],True)
        self.assertTrue(self.art['limits'])
    def test_pins(self):
        s=self.art['sources']
        self.assertEqual(s['xapk_sha256'],'f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e')
        self.assertEqual(s['libunity_sha256'],'d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7')
        self.assertEqual(s['libunity_size'],17783496)
        self.assertEqual(s['probes']['owner130']['sha256'],sha(PROBE.read_bytes()))
        self.assertEqual(s['probes']['owner130b']['sha256'],sha(PROBE_B.read_bytes()))
        self.assertEqual(s['probes']['owner130']['size'],PROBE.stat().st_size)
        self.assertEqual(s['probes']['owner130b']['size'],PROBE_B.stat().st_size)
    def test_tool_pins(self):
        for t in TOOLS:
            self.assertEqual(self.art['sources']['tools'][t],sha((ROOT/t).read_bytes()))
    def test_fact_count(self):
        self.assertEqual(self.art['facts']['count'],177)
        self.assertEqual(self.art['counts']['facts'],177)
        self.assertEqual(self.art['counts']['annotated'],177)
    def test_every_fact_is_byte_verified(self):
        for r in self.art['facts']['rows']:
            self.assertTrue(r['verified'],hex(r['va']))
            code=self.at(r['va'])
            self.assertIsNotNone(code,hex(r['va']))
            self.assertEqual(code[:4].hex(),r['bytes_hex'],hex(r['va']))
    def test_gate_bytes(self):
        self.assertEqual(self.at(0x6b1a0c)[:4].hex(),'08504639')  # ldrb w8,[x0,#0x194]
        self.assertEqual(self.at(0x6b1a10)[:4].hex(),'e8072037')  # tbnz w8,#4
        self.assertEqual(self.at(0x6b1cb8)[:4].hex(),'08012037')  # tbnz w8,#4
        self.assertEqual(self.at(0x6b2260)[:4].hex(),'08032037')  # tbnz w8,#4
        self.assertEqual(self.at(0x6b4c00)[:4].hex(),'08204639')  # ldrb w8,[x0,#0x188]
        self.assertEqual(self.at(0x6b2830)[:4].hex(),'29011a32')  # orr w9,w9,#0x40
        self.assertEqual(self.at(0x6b2848)[:4].hex(),'08791912')  # and w8,w8,#0xffffffbf
        self.assertEqual(self.at(0x6b9ad8)[:4].hex(),'080000f9')  # str x8,[x0]
        self.assertEqual(self.at(0x6b22bc)[:4].hex(),'67160014')  # b 6b7c58
    def test_vtable_members(self):
        vt=self.art['vtable']
        self.assertEqual(vt['base'],0x10b0c80)
        self.assertEqual(vt['slot_count'],35)
        self.assertEqual(len(vt['members']),5)
        self.assertEqual({m['slot_index'] for m in vt['members']},{2,3,10,31,33})
        by={m['slot_index']:m['target'] for m in vt['members']}
        self.assertEqual(by[2],0x6b1914);self.assertEqual(by[3],0x6b1c5c)
        self.assertEqual(by[10],0x3e079c);self.assertEqual(by[31],0x6b947c);self.assertEqual(by[33],0x6b6ab8)
        for m in vt['members']:
            self.assertEqual(m['slot_count'],35)
            self.assertEqual(m['direct_code_refs'],0)
            self.assertTrue(m['role'])
    def test_virtual_slots_have_no_direct_callers(self):
        refs=Counter(c['target'] for c in self.art['call_edges']['rows'])
        for t in (0x6b1914,0x6b1c5c,0x3e079c,0x6b6ab8):
            self.assertEqual(refs[t],0,hex(t))
    def test_call_edges(self):
        ce=self.art['call_edges']
        self.assertEqual(ce['count'],70)
        self.assertEqual(len({(c['target'],c['pc']) for c in ce['rows']}),70)
        self.assertEqual(Counter(c['kind'] for c in ce['rows']),Counter({'bl':55,'b':15}))
        self.assertEqual(sum(1 for c in ce['rows'] if c['caller_start'] is None),14)
        self.assertEqual({c['target'] for c in ce['rows'] if c['caller_start'] is None},
                         {c['target'] for c in ce['rows'] if c['caller_start'] is None})
    def test_chain_shape(self):
        chain=self.art['chain']
        self.assertEqual(chain['count'],19)
        self.assertEqual(len({c['stage'] for c in chain['rows']}),19)
        entries={c['entry'] for c in chain['rows']}
        self.assertEqual(len(entries),19)
        fact_pcs={r['va'] for r in self.art['facts']['rows']}
        for c in chain['rows']:
            for p in c['fact_pcs']:self.assertIn(p,fact_pcs)
            self.assertLess(c['entry'],min(c['fact_pcs'])+0x1000)
    def test_chain_edges(self):
        chain={c['stage']:c for c in self.art['chain']['rows']}
        self.assertEqual(chain['rebuild']['calls'],[0x3df584,0x6b1a00,0x6b7158,0x6b7d58,0x6b81c4,0x6b6dec,0x6b6fdc,0x6b7c58])
        self.assertIn(0x6b2258,chain['flush']['calls']);self.assertIn(0x6b22c8,chain['flush']['calls'])
        self.assertIn(0x3d9648,chain['batch']['calls']);self.assertIn(0x6b1c98,chain['batch']['calls'])
        self.assertIn(0x571e64,chain['update']['calls']);self.assertIn(0x6b7d58,chain['update']['calls'])
        self.assertEqual(chain['parameter']['calls'],[0x572c60])
        self.assertEqual(chain['query-rebuild']['calls'],[0x6b2258])
    def test_field_map(self):
        fm=self.art['field_map']
        self.assertEqual(fm['count'],27)
        offs={o['offset']:o for o in fm['offsets']}
        self.assertEqual(offs[0x608]['total'],5)
        self.assertEqual(offs[0x188]['total'],6)
        self.assertEqual(offs[0x19c]['total'],6)
        self.assertEqual(offs[0x194]['total'],3)
        self.assertNotIn(0x20,offs)
        for o in fm['offsets']:
            self.assertEqual(o['total'],sum(a['count'] for a in o['accesses']))
    def test_related_offsets(self):
        rel=self.art['related_offsets']
        self.assertEqual(rel['count'],2)
        rows={(r['subject'],r['offset']):r['count'] for r in rel['rows']}
        self.assertEqual(rows[('element',0x194)],3)
        self.assertEqual(rows[('entry_obj',0x20)],1)
    def test_indirect(self):
        ind=self.art['indirect']
        self.assertEqual(ind['blr_sites'],[0x6b19cc,0x6b1b80,0x6b6e94,0x6b6f10,0x6b7048])
        self.assertEqual(ind['blr_count'],5)
        self.assertEqual(ind['virtual_slots'],[2,3,10,31,33])
        self.assertTrue(ind['unresolved'])
    def test_counts(self):
        c=self.art['counts']
        self.assertEqual(c['field_offsets'],27)
        self.assertEqual(c['vtable_members'],5)
        self.assertEqual(c['call_sites'],70)
        self.assertEqual(c['indirect_calls'],5)
        self.assertEqual(c['chain_stages'],19)
        self.assertEqual(c['related_offsets'],2)
        self.assertEqual(c['followed_a'],40)
        self.assertEqual(c['followed_b'],11)
        self.assertEqual(c['windows'],40)
    def test_probe_b_windows_subset(self):
        a={w['va']:(w['hex']) for w in self.a['windows']}
        for w in self.b['windows']:
            self.assertIn(w['va'],a)
            self.assertTrue(a[w['va']].startswith(w['hex']))
    def test_probe_pins_are_honoured(self):
        self.assertEqual(sha(PROBE.read_bytes()),'d3929b2e8d3302c47488eb69314e379c522355efb9133590b31c73e69b5c3466')
        self.assertEqual(sha(PROBE_B.read_bytes()),'7d5aacc5cae91f97e18a108c54d994e012cf662d4220967d2d1fee600c8adacb')
        self.assertEqual(self.a['libunity_sha256'],'d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7')
    def test_render_is_deterministic(self):
        import tools.verify.owner130 as v
        one=v.render(v.build());two=v.render(v.build())
        self.assertEqual(one,two)
        self.assertEqual(one,self.raw)
        self.assertEqual(self.raw[:8].hex(),'1f8b080000000000')
    def test_check_mode(self):
        import subprocess,sys
        out=subprocess.run([sys.executable,'tools/verify/owner130.py','--check'],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(out.returncode,0,out.stderr)
        self.assertIn('check ok',out.stdout)
    def test_no_floats_or_nan(self):
        def walk(x):
            if isinstance(x,dict):
                for v in x.values():walk(v)
            elif isinstance(x,list):
                for v in x:walk(v)
            elif isinstance(x,float):self.fail('float in artifact')
        walk(self.art)
if __name__=='__main__':unittest.main()
