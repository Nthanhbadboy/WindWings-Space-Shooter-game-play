import gzip,hashlib,json,struct,unittest
from tools.verify import graph122 as g
class Graph122(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=g.standalone(count=3);cls.a=json.load(gzip.open(g.OUT))
    def test_regenerate(self):self.assertEqual(g.build(),self.a)
    def test_original_fde_extents(self):
        f={x['entry']:x['unwind']['end'] for x in g.raw()['followed'] if x['unwind']};self.assertEqual(f[0x6d2950],0x6d29e4);self.assertEqual(f[0x6d81b0],0x6d81dc);self.assertEqual(f[0x57104c],0x5710ec);self.assertEqual(f[0x570abc],0x570c14);self.assertEqual(f[0x570a70],0x570abc)
    def test_tool_pin(self):self.assertEqual(g.raw()['tool_sha256'],hashlib.sha256((g.ROOT/'tools/recovery/graph122.py').read_bytes()).hexdigest())
    def test_claim_retained(self):self.assertEqual(json.load(open(g.ROOT/'reverse-engineering/raw/l3-ef6b75ef122-verification/claim.json'))['id'],6418915726)
    def test_ret_and_stack(self):
        self.assertEqual(self.r['ret'],0x6d29e0);self.assertEqual(self.r['stack_pointer_after'],0x3000000+0x1f000);self.assertEqual(self.r['stop_pc'],0x3000000+0x1fff0)
    def test_pc_hit_counts(self):
        h=self.r['pc_hits'];expected={'0x6d2974':1,'0x6d2990':3,'0x6d5e58':3,'0x6d81b0':3,'0x57104c':3,'0x570abc':3,'0x570a70':3,'0x5710b0':3,'0x6d29c4':3,'0x6d353c':3,'0x572a38':3,'0x6d29e0':1}
        for k,v in expected.items():self.assertEqual(h[k],v,k)
    def test_no_error_helpers_or_sink_allocator(self):
        p=set(self.r['run']['executed_addresses'])
        for a in (0x52e15c,0xb2e604,0x3c9438,0x570ff0,0x3c986c,0x575b34,0x573a1c,0x109acc0):self.assertNotIn(a,p)
    def test_original_null_slot_branch(self):
        p=set(self.r['run']['executed_addresses']);self.assertIn(0x570be0,p);self.assertIn(0x570a70,p)
    def test_vtable_slots(self):self.assertEqual(self.a['vtable_service_slots'],dict(reserve=0x10,notify=0x18,register=0x70))
    def test_reserve_service(self):
        x=[z for z in self.r['virtual_records'] if z['kind']=='reserve'];self.assertEqual(len(x),1);self.assertEqual(x[0]['count'],3);self.assertEqual(x[0]['manager'],self.r['manager'])
    def test_notify_service(self):
        x=[z for z in self.r['virtual_records'] if z['kind']=='notify'];self.assertEqual([z['index'] for z in x],[0,1,2]);self.assertTrue(all(z['s0_bits']==0 for z in x))
    def test_register_service(self):
        x=[z for z in self.r['virtual_records'] if z['kind']=='register'];self.assertEqual([z['index'] for z in x],[0,1,2]);self.assertEqual([z['node'] for z in x],self.r['node_blocks']);self.assertTrue(all(z['slot']==0 for z in x))
    def test_allocator_requests(self):
        x=self.r['allocator_records'];self.assertEqual(len(x),3)
        for z in x:self.assertEqual(z,dict(size=0x200,alignment=16,category=94,flag=0,label=0x12da21,aux=0xab))
    def test_original_empty_label(self):
        self.assertEqual(bytes.fromhex(self.r['allocator_label_hex'])[0],0);self.assertEqual(bytes.fromhex(self.r['allocator_label_hex'])[1:5],b'Unit')
    def test_zero_writes(self):
        z=self.r['zero_writes'];self.assertEqual({x['address'] for x in z},{self.r['manager']+0x100}|{n+0x100 for n in self.r['node_blocks']});self.assertEqual({x['pc'] for x in z},{0x6d81c4,0x6d81c8})
    def test_manager_byte_zero(self):self.assertEqual(self.r['manager_after']['byte_100'],0)
    def test_node_fields(self):
        for i,n in enumerate(self.r['nodes']):
            self.assertEqual(n['vptr'],0x10b1240);self.assertEqual(n['owner_field'],self.r['list_owner']);self.assertEqual(n['chunk_field'],self.r['pool_after']['chunks'][i]['address']);self.assertEqual(n['type_field'],7);self.assertEqual(n['b8_pointer'],n['address']+0x200);self.assertEqual(n['byte_100'],0);self.assertTrue(n['flags_38']&0x100);self.assertEqual(n['slot0'],self.r['manager'])
    def test_list_owner(self):
        o=self.r['list_owner_after'];self.assertEqual(o['count'],44);self.assertEqual(o['list_head'],self.r['node_blocks'][-1]+8);self.assertEqual(o['flags_halfword'],0xc8)
    def test_pool_chain(self):
        p=self.r['pool_after'];self.assertEqual((p['queue_head'],p['queue_tag'],p['acquired_count']),(0,3,3));self.assertEqual([c['length'] for c in p['chunks']],[1,1,1]);self.assertEqual([c['slot0'] for c in p['chunks']],[self.r['manager']]*3)
    def test_zero_case(self):
        x=g.standalone(count=0);self.assertEqual(x['count'],0);self.assertEqual(len(x['allocator_records']),0);self.assertEqual(x['manager_after']['byte_100'],0xa5);self.assertEqual(x['list_owner_after']['count'],41)
    def test_one_case(self):
        x=g.standalone(count=1);self.assertEqual(len(x['allocator_records']),1);self.assertEqual(len(x['virtual_records']),3);self.assertEqual(x['list_owner_after']['count'],42)
    def test_zero_prefill_case(self):
        x=g.standalone(count=3,prefill=0);self.assertEqual(x['prefill'],0);self.assertEqual(x['manager_after']['byte_100'],0);self.assertEqual(x['nodes'][0]['vptr'],0x10b1240)
    def test_tag_variant(self):self.assertEqual(g.standalone(count=2,tag=41)['pool_after']['queue_tag'],43)
    def test_relocation(self):self.assertEqual(g.standalone(count=1,base=0x4000000)['ret'],0x6d29e0)
    def test_no_direct_upstream_refs(self):self.assertEqual(g.raw()['branch_references'],[])
    def test_source_integration(self):
        s=self.a['source'];self.assertEqual(len(s['calls']),10);self.assertEqual(self.a['counts']['source_dwords'],930);self.assertTrue(all(c['native']['completion_byte']==1 for c in s['calls']))
    def test_source_node_is_third_factory_node(self):self.assertEqual(self.a['source']['source_node'],self.a['source']['graph']['nodes'][-1]['address'])
    def test_post_graph_bindings(self):self.assertEqual(self.a['source']['post_graph_bindings'],[0x118,0x128,0x130,0x1d0])
    def test_counts_partition(self):
        c=self.a['counts'];self.assertEqual(c['standalone_cases'],4);self.assertEqual(c['standalone_loop_counts'],[0,1,3,3]);self.assertEqual(c['standalone_factory_calls'],7);self.assertEqual(c['source_loop_count'],3);self.assertEqual(c['source_factory_calls'],3);self.assertEqual(c['source_calls'],10)
    def test_scope_not_runtime(self):self.assertIn('NOT original virtual implementations',self.r['scope'])
