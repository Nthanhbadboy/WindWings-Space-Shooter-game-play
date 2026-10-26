import gzip,hashlib,json,unittest
from tools.verify import nodefactories124 as v
class NodeFactories124(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=v.standalone(0x6d26d4);cls.a=json.load(gzip.open(v.OUT))
    def test_regenerate(self):self.assertEqual(v.build(),self.a)
    def test_claim(self):self.assertEqual(json.load(open(v.ROOT/'reverse-engineering/raw/l3-ef6b75ef124-verification/claim.json'))['id'],6423259070)
    def test_tool_pin(self):self.assertEqual(v.raw()['tool_sha256'],hashlib.sha256((v.ROOT/'tools/recovery/nodefactories124.py').read_bytes()).hexdigest())
    def test_factory_entries(self):self.assertEqual(v.raw()['known_factories'],[0x6d25f4,0x6d2664,0x6d26d4,0x6d2744])
    def test_constructor_entries(self):self.assertEqual(v.raw()['known_constructors'],[0x6d6a1c,0x6d850c,0x6d2894,0x6d81f8])
    def test_vtable_groups(self):self.assertEqual([x['vptr'] for x in self.a['vtable_groups']],[0x10b1150,0x10b1440,0x10b1640,0x10b1730])
    def test_factory_metadata(self):
        m=self.a['factory_metadata'];self.assertEqual(m[str(0x6d25f4)]['vptr'],0x10b1440);self.assertEqual(m[str(0x6d2664)]['vptr'],0x10b1730);self.assertEqual(m[str(0x6d26d4)]['vptr'],0x10b1150);self.assertEqual(m[str(0x6d2744)]['vptr'],0x10b1640)
        self.assertEqual([m[str(e)]['size_offset'] for e in v.FACTORIES],[0x178,0x170,0x180,0x120])
    def test_fde_rets(self):
        m=self.a['factory_metadata'];self.assertEqual([m[str(e)]['ret'] for e in v.FACTORIES],[0x6d2660,0x6d26d0,0x6d2740,0x6d27b0])
    def test_constructor_vptr_literals(self):
        m=self.a['factory_metadata'];self.assertEqual(m[str(0x6d26d4)]['constructor_vptr_literal']['offset'],0x150);self.assertEqual(m[str(0x6d2664)]['constructor_vptr_literal']['offset'],0x730)
    def test_graph_builder_callsites(self):
        c=self.a['graph_builder_callsites'];self.assertEqual(len(c),7)
        from collections import Counter
        self.assertEqual(dict(Counter(x['target'] for x in c)),{0x6d25f4:1,0x6d2664:1,0x6d26d4:2,0x6d2744:3})
        self.assertEqual([x['pc'] for x in c],[0x6cf86c,0x6cfae4,0x6cfb44,0x6cfb60,0x6cfb7c,0x6cfc54,0x6cfc98])
    def test_default_standalone_cases(self):
        c=self.a['standalone'][:4];self.assertEqual([x['entry'] for x in c],[0x6d25f4,0x6d2664,0x6d26d4,0x6d2744]);self.assertEqual([x['node']['vptr'] for x in c],[0x10b1440,0x10b1730,0x10b1150,0x10b1640])
    def test_factory_c_ret_and_vptr(self):
        self.assertEqual(self.r['ret'],0x6d2740);self.assertEqual(self.r['node']['vptr'],0x10b1150)
    def test_allocator_request(self):
        x=self.r['allocator_records'][0];self.assertEqual(x,dict(size=0x180,alignment=16,category=94,flag=0,label=0x12da21,aux=0xab,expected_size=0x180))
    def test_plt_bindings(self):
        x=self.r['plt_bindings'];self.assertEqual([y['symbol'] for y in x],['memset','__stack_chk_fail']);self.assertEqual([y['plt'] for y in x],[0x109ace0,0x109acc0])
    def test_no_service_calls(self):self.assertEqual(self.r['service_calls'],[]);self.assertEqual(self.r['failure_calls'],[])
    def test_pc_hits(self):
        h=self.r['pc_hits'];self.assertEqual(h['0x6d2894'],1);self.assertEqual(h['0x572a38'],1);self.assertEqual(h['0x57054c'],1);self.assertEqual(h['0x6d2740'],1)
    def test_no_cleanup_or_failure_paths(self):
        p=set(self.r['run']['executed_addresses'])
        for a in (0x570ff0,0x3c986c,0x109acc0,0x109ace0,0x573a1c,0x575b34):self.assertNotIn(a,p)
    def test_common_node_fields(self):
        n=self.r['node'];self.assertEqual(n['label_field'],94);self.assertEqual(n['owner_field'],self.r['owner']);self.assertEqual(n['chunk_field'],self.r['service']+0x2000);self.assertTrue(n['bitfield_38']&1);self.assertEqual(n['halfword_a8'],0)
    def test_constructor_specific_fields(self):
        s=[x['node']['specific'] for x in self.a['standalone'][:4]]
        self.assertEqual(s[0],dict(type_dword=0x4b,flag_170=1));self.assertEqual(s[1],dict(flag_16c=0));self.assertEqual(s[2],dict(float_bits_16c=0x3f800000,previous_zero=True));self.assertEqual(s[3],dict(type_dword=0))
    def test_owner_fields(self):
        o=self.r['owner_after'];self.assertEqual((o['count'],o['list_head'],o['flags_halfword']),(42,self.r['node']['address']+8,0xc8))
    def test_pool_fields(self):
        p=self.r['pool_after'];self.assertEqual((p['queue_head'],p['queue_tag'],p['acquired_count'],p['chunk_length'],p['slot0']),(0,1,1,1,0))
    def test_variant_prefill_label_size_tag(self):
        x=self.a['standalone'][4];self.assertEqual(x['prefill'],0);self.assertEqual(x['label'],7);self.assertEqual(x['extra'],0x40);self.assertEqual(x['tag'],41);self.assertEqual(x['allocator_records'][0]['size'],0x1b8);self.assertEqual(x['pool_after']['queue_tag'],42);self.assertEqual(x['node']['label_field'],7)
    def test_variant_relocation(self):
        x=self.a['standalone'][5];self.assertEqual(x['base'],0x4000000);self.assertEqual(x['ret'],0x6d27b0);self.assertEqual(x['node']['vptr'],0x10b1640)
    def test_extra_size_variant(self):
        x=v.standalone(0x6d2744,extra=0x100);self.assertEqual(x['allocator_records'][0]['size'],0x220)
    def test_tag_variant(self):self.assertEqual(v.standalone(0x6d25f4,tag=7)['pool_after']['queue_tag'],8)
    def test_owner_count_variant(self):self.assertEqual(v.standalone(0x6d26d4,owner_count=99)['owner_after']['count'],100)
    def test_source_factory(self):self.assertEqual(self.a['source']['factory'],0x6d26d4)
    def test_source_integration(self):
        s=self.a['source'];self.assertEqual(len(s['calls']),10);self.assertEqual(self.a['counts']['source_dwords'],930);self.assertTrue(all(x['native']['completion_byte']==1 for x in s['calls']))
    def test_source_node(self):self.assertEqual(self.a['source']['source_node'],self.a['source']['factory_run']['node']['address'])
    def test_post_factory_bindings(self):self.assertEqual(self.a['source']['post_factory_bindings'],[0x118,0x128,0x130,0x1d0])
    def test_counts_partition(self):
        c=self.a['counts'];self.assertEqual(c['standalone_cases'],6);self.assertEqual(c['standalone_factory_calls'],6);self.assertEqual(c['factory_entries'],4);self.assertEqual(c['graph_builder_callsites'],7);self.assertEqual(c['source_factory_calls'],1);self.assertEqual(c['source_calls'],10)
    def test_spec_ack123_receipt(self):
        x=json.loads((v.ROOT/'reverse-engineering/raw/l3-ef6b75ef124-verification/spec-ack123.json').read_text());self.assertEqual(x['id'],6423047661)
    def test_scope_not_runtime(self):self.assertIn('NOT original heap',self.r['scope'])
