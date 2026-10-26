import gzip,hashlib,json,unittest
from tools.verify import vtable123 as v
class Vtable123(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=v.standalone(count=3);cls.a=json.load(gzip.open(v.OUT))
    def test_regenerate(self):self.assertEqual(v.build(),self.a)
    def test_claim(self):self.assertEqual(json.load(open(v.ROOT/'reverse-engineering/raw/l3-ef6b75ef123-verification/claim.json'))['id'],6420235916)
    def test_tool_pin(self):self.assertEqual(v.raw()['tool_sha256'],hashlib.sha256((v.ROOT/'tools/recovery/vtable123.py').read_bytes()).hexdigest())
    def test_naive_candidates(self):self.assertEqual(len(v.raw()['vtable_candidates']),53)
    def test_matched_vtables(self):
        x=v.raw()['matched_vtables'];self.assertEqual([y['vptr'] for y in x],[0x10b1150,0x10b1240,0x10b1330])
        self.assertTrue(all(y['addends'][2:4]==[0x571b3c,0x571a80] for y in x))
    def test_selected_vptr(self):self.assertEqual(self.a['original_vtable']['vptr'],0x10b1150);self.assertEqual(self.a['original_vtable']['slots'],{'16':0x571b3c,'24':0x571a80,'112':0x6d5134})
    def test_constructor_and_caller(self):
        x=self.a['original_vtable'];self.assertEqual((x['constructor'],x['factory'],x['graph_caller']),(0x6d2894,0x6d26d4,0x6cf7b4));self.assertEqual(x['graph_call_pcs'],[0x6cfc34,0x6cfc44])
    def test_graph_thunk_refs(self):
        x=v.raw()['graph_thunk_refs'];self.assertEqual([y['pc'] for y in x],[0x6cfc34,0x6cfc44]);self.assertTrue(all(y['owner_start']==0x6cf7b4 for y in x))
    def test_no_graph_populator_rela(self):self.assertEqual(v.raw()['graph_populator_relas'],[])
    def test_plt_imports(self):
        names={x['name'] for x in v.raw()['imports']};self.assertIn('memset',names);self.assertIn('__stack_chk_fail',names)
    def test_constructor_sets_vptr(self):
        from capstone import Cs,CS_ARCH_ARM64,CS_MODE_ARM
        w=next(w for w in v.raw()['windows'] if w['va']==0x6d2894);ops=[(i.mnemonic,i.op_str) for i in Cs(CS_ARCH_ARM64,CS_MODE_ARM).disasm(bytes.fromhex(w['hex']),w['va'])]
        self.assertIn(('adrp','x9, #0x10b1000'),ops);self.assertIn(('add','x9, x9, #0x150'),ops);self.assertIn(('str','x9, [x19]'),ops)
    def test_ret_and_stack(self):
        self.assertEqual(self.r['ret'],0x6d29e0);self.assertEqual(self.r['stack_pointer_after'],0x3000000+0x1f000);self.assertEqual(self.r['stop_pc'],0x3000000+0x1fff0)
    def test_original_vtable_slots_loaded(self):
        x=self.r['vtable'];self.assertEqual(x['vptr'],0x10b1150);self.assertEqual(x['slots'],{'0x10':0x571b3c,'0x18':0x571a80,'0x70':0x6d5134})
    def test_plt_bindings(self):
        x=self.r['plt_bindings'];self.assertEqual([y['symbol'] for y in x],['memset','__stack_chk_fail']);self.assertEqual([y['plt'] for y in x],[0x109ace0,0x109acc0]);self.assertEqual([y['slot'] for y in x],[0x10e3d10,0x10e3d00])
    def test_virtual_call_targets(self):
        x=self.r['virtual_calls'];res=[y for y in x if y['kind']=='reserve'];notifies=[y for y in x if y['kind']=='notify'];regs=[y for y in x if y['kind']=='register']
        self.assertEqual([y['target'] for y in res],[0x571b3c]);self.assertEqual([y['target'] for y in notifies],[0x571a80]*3);self.assertEqual([y['target'] for y in regs],[0x6d5134]*3)
        self.assertEqual([y['index'] for y in notifies],[0,1,2]);self.assertEqual([y['index'] for y in regs],[0,1,2]);self.assertEqual([y['node'] for y in regs],self.r['node_blocks']);self.assertTrue(all(y['s0_bits']==0 for y in notifies));self.assertTrue(all(y['slot']==0 for y in regs))
    def test_pc_hit_counts(self):
        h=self.r['pc_hits'];expected={'0x6d2974':1,'0x6d2990':3,'0x6d5e58':3,'0x6d81b0':3,'0x57104c':3,'0x570abc':3,'0x5710b0':3,'0x6d29c4':3,'0x6d353c':3,'0x572a38':3,'0x6d29e0':1,'0x571b3c':1,'0x571b58':1,'0x571a80':3,'0x6d5134':3,'0x6d6c88':3,'0x57095c':3,'0x6d6c9c':3,'0x570a70':6}
        for k,n in expected.items():self.assertEqual(h[k],n,k)
    def test_memset_plt_executed(self):self.assertGreaterEqual(self.r['pc_hits'].get('0x109ace0',0),1)
    def test_no_resize_or_failure_paths(self):
        p=set(self.r['run']['executed_addresses'])
        for a in (0x573a34,0x3f1d78,0x570ff0,0x3c986c,0x52e15c,0xb2e604,0x3c9438,0x109acc0,0x575b34,0x573a1c):self.assertNotIn(a,p)
    def test_service_calls(self):
        x=self.r['service_calls'];self.assertEqual(len(x),1);self.assertEqual(x[0]['symbol'],'memset');self.assertEqual(x[0]['length'],48);self.assertEqual(x[0]['value'],0);self.assertEqual(self.r['failure_calls'],[])
    def test_allocator_requests(self):
        x=self.r['allocator_records'];self.assertEqual(len(x),3)
        for y in x:self.assertEqual(y,dict(size=0x200,alignment=16,category=94,flag=0,label=0x12da21,aux=0xab))
    def test_manager_array(self):
        x=self.r['manager_array'];self.assertEqual(len(x),3)
        for i,y in enumerate(x):self.assertEqual((y['node_field'],y['float_bits'],y['slot_field']),(self.r['node_blocks'][i],0,0))
    def test_manager_chunk(self):
        x=self.r['manager_chunk_after'];self.assertEqual((x['data'],x['length'],x['capacity']),(self.r['service']+0x5000,3,6))
    def test_manager_after(self):
        x=self.r['manager_after'];self.assertEqual((x['vptr'],x['owner_field'],x['chunk_field'],x['flags_38'],x['byte_100'],x['capacity_140'],x['capacity_160']),(0x10b1150,self.r['list_owner'],self.r['service']+0x4000,0x100,0,6,6))
    def test_zero_writes(self):
        z=self.r['zero_writes'];self.assertEqual({y['address'] for y in z},{self.r['manager']+0x100}|{n+0x100 for n in self.r['node_blocks']});self.assertEqual({y['pc'] for y in z},{0x6d6c9c,0x6d81c4,0x6d81c8})
    def test_nodes(self):
        for i,n in enumerate(self.r['nodes']):
            self.assertEqual(n['vptr'],0x10b1240);self.assertEqual(n['owner_field'],self.r['list_owner']);self.assertEqual(n['chunk_field'],self.r['pool_after']['chunks'][i]['address']);self.assertEqual(n['type_field'],7);self.assertEqual(n['b8_pointer'],n['address']+0x200);self.assertEqual(n['byte_100'],0);self.assertTrue(n['flags_38']&0x100);self.assertEqual(n['slot0'],self.r['manager'])
    def test_list_owner_and_pool(self):
        o=self.r['list_owner_after'];p=self.r['pool_after'];self.assertEqual((o['count'],o['list_head'],o['flags_halfword']),(44,self.r['node_blocks'][-1]+8,0xc8));self.assertEqual((p['queue_head'],p['queue_tag'],p['acquired_count']),(0,3,3));self.assertEqual([c['length'] for c in p['chunks']],[1,1,1]);self.assertEqual([c['slot0'] for c in p['chunks']],[self.r['manager']]*3)
    def test_zero_case(self):
        x=v.standalone(count=0);self.assertEqual(len(x['allocator_records']),0);self.assertEqual(x['service_calls'],[]);self.assertEqual(x['manager_after']['flags_38'],0);self.assertEqual(x['manager_after']['byte_100'],0xa5);self.assertEqual(x['manager_chunk_after']['length'],0);self.assertEqual(len(x['virtual_calls']),1)
    def test_one_case(self):
        x=v.standalone(count=1);self.assertEqual(len(x['allocator_records']),1);self.assertEqual(len(x['service_calls']),1);self.assertEqual(len(x['virtual_calls']),3);self.assertEqual(x['manager_array'][0]['node_field'],x['node_blocks'][0])
    def test_zero_prefill_case(self):
        x=v.standalone(count=3,prefill=0);self.assertEqual(x['prefill'],0);self.assertEqual(x['manager_after']['byte_100'],0);self.assertEqual(x['nodes'][0]['vptr'],0x10b1240)
    def test_tag_variant(self):self.assertEqual(v.standalone(count=2,tag=41)['pool_after']['queue_tag'],43)
    def test_relocation(self):self.assertEqual(v.standalone(count=1,base=0x4000000)['ret'],0x6d29e0)
    def test_source_integration(self):
        s=self.a['source'];self.assertEqual(len(s['calls']),10);self.assertEqual(self.a['counts']['source_dwords'],930);self.assertTrue(all(c['native']['completion_byte']==1 for c in s['calls']))
    def test_source_node_is_third_factory_node(self):self.assertEqual(self.a['source']['source_node'],self.a['source']['graph']['nodes'][-1]['address'])
    def test_post_graph_bindings(self):self.assertEqual(self.a['source']['post_graph_bindings'],[0x118,0x128,0x130,0x1d0])
    def test_counts_partition(self):
        c=self.a['counts'];self.assertEqual(c['standalone_cases'],4);self.assertEqual(c['standalone_loop_counts'],[0,1,3,3]);self.assertEqual(c['standalone_factory_calls'],7);self.assertEqual(c['source_loop_count'],3);self.assertEqual(c['source_factory_calls'],3);self.assertEqual(c['source_calls'],10)
    def test_scope_not_runtime(self):self.assertIn('NOT original heap',self.r['scope'])
