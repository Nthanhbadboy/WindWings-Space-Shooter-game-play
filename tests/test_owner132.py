import gzip,hashlib,json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'datas/l3_ef6b75ef132_native_dispatch_owners.json.gz'
PROBE=ROOT/'reverse-engineering/raw/owner132/probe.json.gz'
PROBE_B=ROOT/'reverse-engineering/raw/owner132b/probe.json.gz'
UP130=ROOT/'datas/l3_ef6b75ef130_native_update_trigger.json.gz'
UP131=ROOT/'datas/l3_ef6b75ef131_native_vtable_dispatch.json.gz'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.load(gzip.open(p))
class Owner132Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.art=load(ART);cls.p=load(PROBE);cls.pb=load(PROBE_B)
        cls.by={o['entry']:o for o in cls.p['owners']}
    def body(self,entry):
        return bytes.fromhex(self.by[entry]['hex'])
    def test_schema(self):
        self.assertEqual(sorted(self.art),['aggregate','callees','cluster','counts','fields','graph_builder','limits','negative','owners','pins','provisional','slot_offsets','vtable_slots'])
        self.assertIs(self.art['provisional'],True)
        self.assertTrue(self.art['limits'])
    def test_pins(self):
        p=self.art['pins']
        self.assertEqual(p['xapk_sha256'],'f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e')
        self.assertEqual(p['libunity_sha256'],'d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7')
        self.assertEqual(p['libunity_size'],17783496)
        self.assertEqual(p['probe']['sha256'],sha(PROBE.read_bytes()))
        self.assertEqual(p['probe_stage2']['sha256'],sha(PROBE_B.read_bytes()))
        for name in ('130','131'):
            src=UP130 if name=='130' else UP131
            self.assertEqual(p['upstream'][name]['sha256'],sha(src.read_bytes()))
    def test_tool_pins(self):
        for t,h in self.art['pins']['tools'].items():
            self.assertEqual(h,sha((ROOT/t).read_bytes()),t)
        self.assertEqual(len(self.art['pins']['tools']),3)
    def test_owner_set(self):
        self.assertEqual(len(self.art['owners']),27)
        groups={}
        for o in self.art['owners']:groups.setdefault(o['group'],[]).append(o['entry'])
        self.assertEqual(len(groups['slot31_dispatch_owner']),16)
        self.assertEqual(len(groups['batch_container_owner']),10)
        self.assertEqual(groups['incluster_slot33_owner'],[0x6b7d58])
    def test_body_hashes(self):
        for o in self.art['owners']:
            if o['group']=='incluster_slot33_owner':continue
            self.assertEqual(o['body_sha256'],sha(self.body(o['entry'])),hex(o['entry']))
            self.assertEqual(o['body_words'],len(self.body(o['entry']))//4)
    def test_slot31_negative(self):
        g=self.art['aggregate']['slot31']
        self.assertEqual(g['owners'],16)
        self.assertEqual(g['cluster_calls'],0)
        self.assertEqual(g['cluster_targets'],[])
        self.assertEqual(g['global_refs'],0)
        self.assertEqual(g['field_hit_owners'],[0xe4515c])
        self.assertEqual(g['dispatch_by_slot'],{'2':3,'3':2,'10':2,'31':24,'33':21})
        self.assertEqual(self.art['negative']['slot31_cluster_calls'],0)
    def test_batch_group(self):
        g=self.art['aggregate']['batch']
        self.assertEqual(g['owners'],10)
        self.assertEqual(g['cluster_calls'],8)
        self.assertEqual([hex(x) for x in g['cluster_targets']],['0x6b08c0','0x6b08d8','0x6b08e4','0x6b1c98','0x6b753c'])
        self.assertEqual(g['global_refs'],10)
        self.assertEqual(g['dispatch_by_slot'],{'10':2})
        self.assertEqual(g['field_hit_owners'],[])
    def test_incluster_group(self):
        g=self.art['aggregate']['incluster']
        self.assertEqual(g['owners'],1)
        self.assertEqual([hex(x) for x in g['cluster_targets']],['0x6b8054','0x6b80e0'])
        self.assertEqual(g['cluster_calls'],2)
        self.assertEqual(g['dispatch_by_slot'],{'10':1,'33':1})
        self.assertEqual(g['field_hit_owners'],[0x6b7d58])
    def test_builder_facts(self):
        g=self.art['graph_builder']
        self.assertEqual(len(g['facts']),43)
        code=self.body(0x6b7d58)
        for f in g['facts']:
            self.assertTrue(f['verified'],hex(f['va']))
            off=f['va']-0x6b7d58
            self.assertEqual(code[off:off+4].hex(),f['bytes_hex'],hex(f['va']))
    def test_builder_key_bytes(self):
        code=self.body(0x6b7d58)
        def at(va,n=4):return code[va-0x6b7d58:va-0x6b7d58+n].hex()
        self.assertEqual(at(0x6b7e00),'680240f9')
        self.assertEqual(at(0x6b7e0c),'082940f9')
        self.assertEqual(at(0x6b7f48),'680240f9')
        self.assertEqual(at(0x6b7f50),'088540f9')
        self.assertEqual(at(0x6b7f54),'00013fd6')
        self.assertEqual(at(0x6b7e1c),'00383f91')
        self.assertEqual(at(0x6b7ec4),'21441091')
        self.assertEqual(at(0x6b8010),'f35b0094')
    def test_builder_edges(self):
        e={x['slot']:x for x in self.art['graph_builder']['edges']}
        self.assertEqual(sorted(e),[10,33,40])
        self.assertEqual(e[10]['resolved_target'],0x3e079c)
        self.assertEqual(e[33]['resolved_target'],0x6b6ab8)
        self.assertIsNone(e[40]['resolved_target'])
        self.assertEqual(e[10]['ldr_pc'],0x6b7e0c)
        self.assertEqual(e[33]['ldr_pc'],0x6b7f50)
        self.assertEqual(e[40]['ldr_pc'],0x6b7f04)
        self.assertEqual(self.art['vtable_slots'],{'2':0x6b1914,'3':0x6b1c5c,'10':0x3e079c,'31':0x6b947c,'33':0x6b6ab8})
    def test_builder_callers(self):
        b=self.by[0x6b7d58]
        callers={c['caller'] for c in b['callers']}
        self.assertEqual(callers,{0x6b2258,0x6b81c4,0x6b947c})
        self.assertEqual(self.art['graph_builder']['extent'],0x2fc)
    def test_callee_attribution(self):
        c=self.art['callees']
        self.assertEqual(len(c['rows']),16)
        self.assertEqual(c['interior'],[0x6b7fe8])
        self.assertEqual(c['unattributed'],[0x109acc0])
        self.assertIn(0x6ce4b4,c['own_fde'])
        self.assertIn(0x6ce464,c['own_fde'])
        o={r['address']:r for r in c['rows']}
        self.assertEqual(o[0x6ce4b4]['extent'],0x48)
        self.assertEqual(o[0x6ce464]['extent'],0x34)
        self.assertEqual(o[0x6ce4fc]['extent'],0x5c)
        self.assertEqual(o[0x6b7fe8]['owner'],0x6b7d58)
        self.assertEqual(o[0x6b7fe8]['offset_in_fde'],656)
        for a in (0x6b08c0,0x6b08d8,0x6b08e4):
            self.assertEqual(o[a]['extent'],0xc)
            self.assertTrue(o[a]['thunk'].startswith('mov w1, #8'))
    def test_stage2_matches_stage1(self):
        # every stage-2 address that lies in a stage-1 body must agree on the FDE owner
        owners={o['entry']:o for o in self.p['owners']}
        for r in self.art['callees']['rows']:
            a=r['address']
            for e,o in owners.items():
                ext=o['extent'] or 0
                if e<=a<e+ext:
                    self.assertEqual(r['owner'],e if r['owner'] is None or a<e+ext else r['owner'],hex(a))
    def test_counts(self):
        c=self.art['counts']
        self.assertEqual(c['owners'],27)
        self.assertEqual(c['facts'],43)
        self.assertEqual(c['edges'],3)
        self.assertEqual(c['slot31_owners'],16)
        self.assertEqual(c['batch_owners'],10)
        self.assertEqual(c['cluster_calls_total'],10)
        self.assertEqual(c['dispatch_sites'],56)
        self.assertEqual(c['callers'],86)
        self.assertEqual(c['callees'],16)
        self.assertEqual(c['bl_total'],442)
        self.assertEqual(c['b_external_total'],6)
        self.assertEqual(c['intra_total'],169)
    def test_transfer_split(self):
        for o in self.art['owners']:
            self.assertEqual(o['call_count'],o['bl_count']+o['b_external_count']+o['intra_branch_count'],hex(o['entry']))
            self.assertEqual(o['bl_count'],sum(1 for c in o['calls'] if c['kind']=='bl'),hex(o['entry']))
    def test_limits_are_honest(self):
        text=' '.join(self.art['limits']).lower()
        self.assertIn('no indirect flow',text)
        self.assertIn('not class evidence',text)
        self.assertIn('capped at 0x1000',text)
    def test_render_deterministic(self):
        import tools.verify.owner132 as v
        one=v.render(v.build());two=v.render(v.build())
        self.assertEqual(one,two)
        self.assertEqual(one,ART.read_bytes())
        self.assertEqual(ART.read_bytes()[:8].hex(),'1f8b080000000000')
    def test_check_mode(self):
        out=subprocess.run([sys.executable,'tools/verify/owner132.py','--check'],cwd=ROOT,capture_output=True,text=True)
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
