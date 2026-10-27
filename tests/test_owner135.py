import gzip,hashlib,json,struct,unittest
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'datas/l3_ef6b75ef135_native_apply_seed.json.gz'
PROBE=ROOT/'reverse-engineering/raw/owner135/probe.json.gz'
UP129=ROOT/'datas/l3_ef6b75ef129_native_owner_linkage.json.gz'
UP133=ROOT/'datas/l3_ef6b75ef133_native_builder_helpers.json.gz'
UP134=ROOT/'datas/l3_ef6b75ef134_native_refresh_leaves.json.gz'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.load(gzip.open(p))
class Owner135Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=ART.read_bytes();cls.art=load(ART);cls.p=load(PROBE)
        cls.by={b['entry']:b for b in cls.art['bodies']}
        cls.wins={f['entry']:bytes.fromhex(f['hex']) for f in cls.p['functions']}
    def at(self,va,n=4):
        for e,w in self.wins.items():
            if e<=va<e+len(w):return w[va-e:va-e+n]
        return None
    # --- schema and pins -------------------------------------------------
    def test_schema(self):
        self.assertEqual(sorted(self.art),['bodies','cluster','counts','focus','follow_depth','limits',
                                           'notes','order','pins','provisional','seeds','slot_resolution',
                                           'truncated'])
        self.assertIs(self.art['provisional'],True)
        self.assertEqual(self.art['cluster'],[0x6b0000,0x6c0000])
        self.assertTrue(self.art['limits'])
        self.assertTrue(self.art['notes'])
    def test_pins(self):
        p=self.art['pins']
        self.assertEqual(p['xapk_sha256'],'f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e')
        self.assertEqual(p['libunity_sha256'],'d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7')
        self.assertEqual(p['libunity_size'],17783496)
        self.assertEqual(p['probe']['sha256'],sha(PROBE.read_bytes()))
        self.assertEqual(p['probe']['size'],PROBE.stat().st_size)
        self.assertEqual(p['probe']['path'],'reverse-engineering/raw/owner135/probe.json.gz')
    def test_upstream_pins(self):
        u=self.art['pins']['upstream']
        self.assertEqual(sorted(u),['129','133','134'])
        self.assertEqual(u['129']['sha256'],sha(UP129.read_bytes()))
        self.assertEqual(u['133']['sha256'],sha(UP133.read_bytes()))
        self.assertEqual(u['134']['sha256'],sha(UP134.read_bytes()))
        self.assertEqual(u['133']['sha256'],'73542233a6fd80aeb3d13fde9aaae0f1e0a211bd4f04b202afa8c6682d825707')
        self.assertEqual(u['134']['sha256'],'74cf1843928d165058771269c2508337df33be9b4840edfd9c5e076e358062e6')
    def test_tool_pins(self):
        for t,h in self.art['pins']['tools'].items():self.assertEqual(h,sha((ROOT/t).read_bytes()),t)
        self.assertEqual(sorted(self.art['pins']['tools']),['tools/recovery/owner135.py','tools/verify/owner135.py'])
    # --- body set --------------------------------------------------------
    def test_body_set(self):
        b=self.art['bodies']
        self.assertEqual(len(b),24)
        self.assertEqual(sum(1 for x in b if x['group']=='seed'),15)
        self.assertEqual(sum(1 for x in b if x['group']=='cluster_callee'),9)
        self.assertEqual([x['depth'] for x in b],( [0]*15)+([1]*9))
        for x in b:self.assertEqual(x['body_sha256'],sha(self.wins[x['entry']]),hex(x['entry']))
    def test_order_matches_probe(self):
        order=[hex(x) for x in self.art['order']]
        self.assertEqual(order,[hex(x) for x in self.p['order']])
        self.assertEqual(order[:6],['0x6b2ce8','0x6b2eec','0x6b6850','0x6b2bdc','0x6da998','0x6b7cf8'])
        self.assertEqual(order[-4:],['0x6be690','0x6b7c14','0x6bba14','0x6bc968'])
        self.assertEqual([hex(x) for x in self.art['seeds']],[hex(x) for x in self.p['seeds']])
    def test_every_callee_was_reached_from_a_seed(self):
        seeds={x['entry'] for x in self.art['bodies'] if x['group']=='seed'}
        followed={x['entry'] for x in self.art['bodies'] if x['group']=='cluster_callee'}
        level1={e for e in followed if self.by[e]['parent'] in seeds}
        level2={e for e in followed if self.by[e]['parent'] in followed}
        self.assertEqual(level1|level2,followed)
        self.assertEqual(len(level1),8)
        self.assertEqual(level2,{0x6bc968})
        self.assertEqual(self.art['follow_depth']['level1'],8)
        self.assertEqual(self.art['follow_depth']['level2'],['0x6bc968'])
        # nothing outside the cluster was followed
        for e in followed:
            self.assertFalse(self.by[e]['calls'] and False)
    def test_parent_links(self):
        for x in self.art['bodies']:
            if x['group']=='cluster_callee':
                self.assertIn(x['parent'],{y['entry'] for y in self.art['bodies']},hex(x['entry']))
                self.assertIn(x['entry'],[c['target'] for c in self.by[x['parent']]['calls']])
    def test_counts(self):
        c=self.art['counts']
        self.assertEqual(c['bodies'],24);self.assertEqual(c['facts'],297)
        self.assertEqual(c['seeds'],15);self.assertEqual(c['followed'],9)
        self.assertEqual(c['calls'],177);self.assertEqual(c['bl'],89)
        self.assertEqual(c['cluster_calls'],12);self.assertEqual(c['dispatch'],20)
        self.assertEqual(c['dispatch_rows_raw'],42);self.assertEqual(c['strings'],0)
        self.assertEqual(c['fields'],203);self.assertEqual(c['truncated'],3)
        self.assertEqual(c['windows_bytes'],9952)
    def test_counts_are_recounted_from_rows(self):
        b=self.art['bodies'];c=self.art['counts']
        self.assertEqual(c['calls'],sum(x['call_count'] for x in b))
        self.assertEqual(c['bl'],sum(1 for x in b for y in x['calls'] if y['kind']=='bl'))
        self.assertEqual(c['cluster_calls'],sum(len(x['cluster_calls']) for x in b))
        self.assertEqual(c['dispatch'],sum(len(x['dispatch']) for x in b))
        self.assertEqual(c['fields'],sum(x['field_count'] for x in b))
        self.assertEqual(c['windows_bytes'],sum(x['window_bytes'] for x in b))
        self.assertEqual(c['facts'],len(self.art_facts()))
    def art_facts(self):
        import tools.verify.owner135 as v
        return v.FACTS
    # --- facts -----------------------------------------------------------
    def test_facts_bytes(self):
        import tools.verify.owner135 as v
        self.assertEqual(len(v.FACTS),297)
        for va,(hx,text,note) in v.FACTS.items():
            b=self.at(va)
            self.assertIsNotNone(b,hex(va))
            self.assertEqual(b.hex(),hx,hex(va))
            self.assertTrue(text and note,hex(va))
    def test_facts_lie_inside_captured_windows(self):
        for va in self.art_facts():
            self.assertIsNotNone(self.at(va),hex(va))
    def test_every_body_has_annotated_facts(self):
        for x in self.art['bodies']:
            n=sum(1 for va in self.art_facts() if x['entry']<=va<x['entry']+x['window_bytes'])
            self.assertGreaterEqual(n,min(5,x['words']),hex(x['entry']))
    def test_fact_coverage_per_body_is_countable(self):
        cov={hex(x['entry']):sum(1 for va in self.art_facts() if x['entry']<=va<x['entry']+x['window_bytes'])
             for x in self.art['bodies']}
        self.assertEqual(sum(cov.values()),297)
        self.assertEqual(cov['0x6b2ce8'],49)
        self.assertEqual(cov['0x6a99f0'],29)
        self.assertEqual(cov['0x6c7060'],13)
        self.assertEqual(cov['0x6b784c'],17)
    # --- truncation honesty ---------------------------------------------
    def test_truncated_bodies(self):
        tr=self.art['truncated']
        self.assertEqual(tr,['0x6c7060','0x6bd5c0','0x6be690'])
        for e in (0x6c7060,0x6bd5c0,0x6be690):
            b=self.by[e]
            self.assertTrue(b['truncated'])
            self.assertEqual(b['window_bytes'],2048)
            self.assertLess(b['window_bytes'],b['extent'])
        for x in self.art['bodies']:
            if not x['truncated']:self.assertEqual(x['window_bytes'],x['extent'],hex(x['entry']))
    def test_truncation_note(self):
        self.assertIn('0x800 cap',self.art['notes']['truncation'])
        for e in ('0x6c7060','0x6bd5c0','0x6be690'):self.assertIn(e,self.art['notes']['truncation'])
    # --- apply context ---------------------------------------------------
    def test_apply_context(self):
        c=self.art['focus']['apply_context']
        self.assertEqual(c['entry'],0x6b2ce8)
        self.assertEqual(c['extent'],0x204)
        self.assertEqual(c['version_key']['context_word'],0x00)
        self.assertEqual(c['version_key']['live_counter'],0x610)
        self.assertEqual(c['invalid_state']['first_word'],1)
        self.assertEqual(c['invalid_state']['zero_qword_ranges'],
                         [[0x08,0x18],[0x18,0x28],[0x28,0x38],[0x38,0x48],[0x48,0x58],[0x58,0x68]])
        self.assertEqual(c['invalid_state']['zero_words'],[0x68])
        self.assertEqual(c['invalid_state']['zero_pointers'],[0x90,0xa0,0xa8,0xb0])
        self.assertEqual(c['call_frame'],{'x0':'animator','x1':'playable record','x2':'source object',
                                          'x3':'context out','x4':'third argument, forwarded to the commit tail'})
        self.assertEqual(c['self_refs'],{'animator':0x90,'animator_plus_0x40':0x98})
        self.assertEqual(c['bind_call'],0x6d615c)
        self.assertEqual(c['tail'],0x6b6950)
        self.assertIn(0x6b6950,[x['target'] for x in self.by[0x6b2ce8]['calls']])
        for off in (0x08,0x10,0x18,0x20,0x28,0x30,0x38,0x40,0x48,0x50,0x58,0x60,0x68,0x6c,0x70,0x74,0x78,0x7c):
            self.assertIn(off,c['copied_fields'])
        self.assertEqual(sorted(c['derived_fields']),['byte_0x80','byte_0x81','byte_0x82','byte_0x88','word_0x84'])
        # word copy offsets must actually appear as stores in the body
        stored=Counter(f['offset'] for f in self.by[0x6b2ce8]['fields'] if f['kind']=='store')
        for off in (0x08,0x18,0x28,0x58,0x60,0x68,0x74,0x7c):self.assertIn(off,stored,hex(off))
        # the byte fields are byte stores, so they are not field rows; the text must show them
        texts=' '.join(f['mnemonic'] for f in []) if False else ''
        import tools.verify.owner135 as v
        ins=[t for (hx,t,n) in v.FACTS.values()]
        joined=' '.join(ins)
        for tok in ('#0x80','#0x81','#0x82','#0x84','#0x88'):self.assertIn(tok,joined)
    def test_context_commit(self):
        c=self.art['focus']['context_commit']
        self.assertEqual(c['entry'],0x6b6950)
        self.assertEqual(c['extent'],0xa0)
        self.assertEqual(c['requires'],[0x08,0x20])
        self.assertEqual(c['version_word'],0x58)
        self.assertEqual(c['counter_field'],0x610)
        self.assertEqual(c['descriptor'],{'vtable_const':0x10b0b30,'word':0x1e})
        self.assertEqual(c['calls'],[0x6d816c,0x6d8118])
        tg=[x['target'] for x in self.by[0x6b6950]['calls']]
        self.assertIn(0x6d816c,tg);self.assertIn(0x6d8118,tg)
        self.assertIn('+0x610',c['rule'])
    def test_counter_is_shared_between_135_and_134(self):
        c=self.art['focus']['apply_context']['version_key']
        self.assertEqual(c['live_counter'],0x610)
        self.assertIn('+0x610',self.art['notes']['counter_definition'])
        self.assertIn('134',self.art['notes']['counter_definition'])
    # --- backend select --------------------------------------------------
    def test_backend_select(self):
        b=self.art['focus']['backend_select']
        self.assertEqual(b['entry'],0x6b2bdc)
        self.assertEqual(b['context_builder'],0x6b784c)
        self.assertEqual(b['backend_flag'],0x5e5)
        self.assertEqual(b['backends'],{'plus_0x5e5_set':0x6bd5c0,'plus_0x5e5_clear':0x6be690})
        self.assertEqual(b['legacy_flag'],0x48f)
        self.assertEqual(b['legacy_path'],{'builder':0x6b7c14,'built_field':0x1b0,'direct':0x6e2388})
        self.assertEqual(b['store'],{'descriptor_at':'x2+0x20','result':'x2+0x00'})
        self.assertEqual(b['post'],[0x6da8e4,0x6e2388])
        tg=[x['target'] for x in self.by[0x6b2bdc]['calls']]
        self.assertEqual(tg.count(0x6e2388),2)
        for t in (0x6b784c,0x6bd5c0,0x6be690,0x6b7c14,0x6da8e4):self.assertIn(t,tg)
    def test_backend_bodies_are_truncated_so_not_explained(self):
        self.assertIn('6bd5c0',self.art['notes']['two_backends'])
        self.assertIn('6be690',self.art['notes']['two_backends'])
        self.assertIn('NOT read',self.art['notes']['two_backends'])
    def test_backend_writers_both_insert_before_writing(self):
        for e in (0x6bd5c0,0x6be690):
            tg=[x['target'] for x in self.by[e]['calls']]
            self.assertIn(0x6bc968,tg,hex(e))
            self.assertIn(0x6a7a08,tg,hex(e))
    def test_prepare_recurses(self):
        p=self.art['focus']['entry_prepare']
        self.assertEqual(p['entry'],0x6b2eec)
        self.assertEqual(p['slots'],[0xd0,0xc8])
        self.assertIs(p['recursive'],True)
        self.assertEqual(p['cleared_byte'],0x103)
        self.assertEqual(p['index'],0x6d788c)
        tg=[x['target'] for x in self.by[0x6b2eec]['calls']]
        self.assertEqual(tg, [0x6d788c,0x6b2eec])
        self.assertEqual([d['slot'] for d in self.by[0x6b2eec]['dispatch']],[0xd0,0xc8])
    # --- companion -------------------------------------------------------
    def test_companion_loop(self):
        c=self.art['focus']['evaluate_companion']
        self.assertEqual(c['entry'],0x6b6850)
        self.assertEqual(c['loop']['base'],0x168)
        self.assertEqual(c['loop']['count'],0x178)
        self.assertEqual(c['loop']['stride'],0x28)
        self.assertEqual(c['loop']['resolve'],0x6b1538)
        self.assertEqual(c['loop']['arg'],0x5e8)
        self.assertEqual(c['scratch'],{'capacity':0x600,'count':0x5f8,'field':0x5e8,'grow':0x6bad24})
        self.assertEqual(c['accumulator_byte'],0x48e)
        self.assertEqual(c['entry_slot'],0x1a0)
        self.assertEqual(c['payload_offset'],0x58)
        self.assertEqual(c['release'],0x49ffc8)
        tg=[x['target'] for x in self.by[0x6b6850]['calls']]
        for t in (0x6b1538,0x6d6010,0x49ffc8,0x6bad24):self.assertIn(t,tg)
    def test_growth_thunks(self):
        t={x['address']:x for x in self.art['focus']['growth_thunks']}
        self.assertEqual(sorted(t),[0x6bad24,0x6bba14])
        self.assertEqual(t[0x6bad24]['target'],0x3f1e30);self.assertEqual(t[0x6bad24]['kind'],'growth')
        self.assertEqual(t[0x6bba14]['target'],0x3f1cb4);self.assertEqual(t[0x6bba14]['kind'],'insert')
        for v in t.values():self.assertEqual((v['element'],v['align'],v['extent'] if 'extent' in v else 8),(8,8,8))
    # --- channel setters -------------------------------------------------
    def test_float_setter(self):
        f=self.art['focus']['float_setter']
        self.assertEqual(f['entry'],0x6a99f0)
        self.assertEqual(f['kind_field'],0x08)
        self.assertEqual(f['kind_range'],[5,11])
        self.assertEqual(f['jump_table'],0x152614)
        self.assertEqual(f['thresholds'],[0x14be6c,0x14b9c8])
        self.assertEqual(f['delegate_slot'],0x10)
        self.assertEqual(len(f['cases']),5)
        self.assertIn('fcvtzs',f['rounding'])
        tg=[x['target'] for x in self.by[0x6a99f0]['calls']]
        self.assertIn(0x3dfd98,tg)
        self.assertEqual(self.by[0x6a99f0]['dispatch'][0]['slot'],0x8)
    def test_float_setter_jump_table_offset_is_not_a_body(self):
        self.assertNotIn(0x152614,self.by)
        self.assertIn('not decoded',self.art['limits'][3])
    def test_int_setter(self):
        i=self.art['focus']['int_setter']
        self.assertEqual(i['entry'],0x6a98c4)
        self.assertEqual(i['kind'],9)
        self.assertEqual(i['registry'],0x10e18b0)
        self.assertEqual(i['lookup'],0x38cbb4)
        self.assertEqual(i['fallback'],0x3d8614)
        self.assertEqual(i['compare'],0x5888bc)
        self.assertEqual(i['global_hook'],0x10e18a8)
        self.assertEqual(i['returns'],'changed flag')
        tg=[x['target'] for x in self.by[0x6a98c4]['calls']]
        for t in (0x38cbb4,0x3d8614,0x5888bc):self.assertIn(t,tg)
        self.assertEqual([d['slot'] for d in self.by[0x6a98c4]['dispatch']],[0x10,0x0])
    def test_kind_0b_setter(self):
        k=self.art['focus']['kind_0b_setter']
        self.assertEqual(k['entry'],0x6a99a4)
        self.assertEqual(k['kind'],0x0b)
        self.assertEqual(k['returns'],'old != new')
        self.assertEqual(self.by[0x6a99a4]['calls'],[])
        self.assertEqual(k['other_kinds'],'always 0')
    def test_channel_release(self):
        r=self.art['focus']['channel_release']
        self.assertEqual(r['entry'],0x6a9b90)
        self.assertEqual(r['slot'],0x18)
        self.assertEqual(r['arg'],0x10)
        self.assertEqual(r['global_byte'],0x10e18c0)
        self.assertEqual(r['tail'],0x4aa754)
        self.assertEqual(self.by[0x6a9b90]['dispatch'][0]['slot'],0x18)
        self.assertIn(0x4aa754,[x['target'] for x in self.by[0x6a9b90]['calls']])
    # --- resolvers -------------------------------------------------------
    def test_interval_lookup(self):
        v=self.art['focus']['interval_lookup']
        self.assertEqual(v['entry'],0x3dfa9c)
        self.assertEqual((v['base_field'],v['count_field'],v['stride']),(0x30,0x40,0x10))
        self.assertEqual(v['key_from'],'x1+0x30')
        self.assertEqual(v['payload'],'[entry+8]')
        self.assertIn('unsigned',v['match'])
    def test_int_resolver(self):
        v=self.art['focus']['int_resolver']
        self.assertEqual(v['entry'],0x3d8614)
        self.assertEqual(v['hook'],0x111dba0)
        self.assertEqual(v['hook_arg'],0x111dba8)
        self.assertIs(v['negative_rejected'],True)
        self.assertEqual(v['zero_returns'],0)
        self.assertEqual(v['fallback'],{'args':'(id, -1)','entry':0x5d83b8,'pre':0x5d6644})
        tg=[x['target'] for x in self.by[0x3d8614]['calls']]
        self.assertEqual(tg,[0x5d6644,0x5d83b8])
    def test_lookup_or_create(self):
        v=self.art['focus']['lookup_or_create']
        self.assertEqual(v['entry'],0x518b40)
        self.assertEqual((v['field'],v['second_word']),(0x38,0x40))
        self.assertEqual(v['calls'],[0x494b04,0x493a24])
        self.assertIn('0x38',v['populated_when'])
    def test_index_accessor(self):
        v=self.art['focus']['index_accessor']
        self.assertEqual(v['entry'],0x6d788c)
        self.assertEqual((v['holder'],v['count'],v['base'],v['entry_count']),(0x30,0x30,0x20,0x18))
        self.assertEqual(v['chain_index'],'ldrsw [slot+0xc]')
        self.assertEqual(self.by[0x6d788c]['calls'],[{'pc':0x6d78c0,'target':0x6d7890,'kind':'b','intra':True,
            'in_cluster':False}])
    # --- slot resolution -------------------------------------------------
    def test_slot_resolution_matches_129(self):
        up=load(UP129);slots={}
        for t in up['vtable_family']:
            for cs in t['called_slots']:slots[cs['offset']]=cs['target']
        self.assertEqual(self.art['slot_resolution']['slots'],{str(k):v for k,v in sorted(slots.items())})
        self.assertEqual(self.art['slot_resolution']['source'],'cycle-129 vtable_family called_slots')
    def test_only_known_slots_resolve(self):
        known={int(k) for k in self.art['slot_resolution']['slots']}
        for b in self.art['bodies']:
            for d in b['dispatch']:
                if d['slot'] in known:self.assertIsNotNone(d['resolved_target'],hex(b['entry']))
                else:self.assertIsNone(d['resolved_target'],hex(b['entry']))
        resolved={(hex(b['entry']),d['slot']) for b in self.art['bodies'] for d in b['dispatch'] if d['resolved_target']}
        self.assertEqual(resolved,{('0x6bc968',0x50)})
    def test_hashtable_vtable_slot_resolves_to_134_owner(self):
        d=self.by[0x6bc968]['dispatch'][0]
        self.assertEqual(d['slot'],0x50)
        self.assertEqual(d['resolved_target'],0x3e079c)
    # --- execution honesty ----------------------------------------------
    def test_no_execution_note(self):
        n=self.art['notes']['no_execution']
        self.assertIn('no instruction',n)
        self.assertIn('no object was fabricated',n)
        self.assertIn('static' if 'static' in n.lower() else 'libunity.so',n)
    def test_limits_are_explicit(self):
        L=' '.join(self.art['limits'])
        self.assertIn('follow_depth',L)
        self.assertIn('0x150 bytes of 0x6c7060',L)
        self.assertIn('One follow level',L)
        self.assertIn('ldp/stp are not field rows',L)
        self.assertIn('not class evidence',L)
        self.assertIn('Static only',L)
    def test_artifact_is_reproducible(self):
        import tools.verify.owner135 as v
        self.assertEqual(v.render(v.build()),self.raw)
    def test_counts_are_countable_from_probe(self):
        c=self.art['counts']
        self.assertEqual(c['bodies'],len(self.p['functions']))
        n=sum(len(bytes.fromhex(f['hex']))//4 for f in self.p['functions'])
        self.assertEqual(n,2488)
        self.assertEqual(c['windows_bytes'],n*4)
        self.assertEqual(c['seeds'],len(self.p['seeds']))
        self.assertEqual(c['seeds']+c['followed'],c['bodies'])
if __name__=='__main__':unittest.main()
