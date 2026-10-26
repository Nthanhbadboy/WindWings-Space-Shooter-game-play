import gzip,hashlib,json,struct,unittest
from tools.verify import factory121 as f
class Factory121(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=f.standalone();cls.a=json.load(gzip.open(f.OUT))
    def test_regenerate(self):self.assertEqual(f.build(),self.a)
    def test_original_factory_fde(self):
        x=next(y for y in f.raw()['followed'] if y['entry']==0x6d5e58);self.assertEqual(x['unwind']['end'],0x6d5ec8)
    def test_tool_pin(self):self.assertEqual(f.raw()['tool_sha256'],hashlib.sha256((f.ROOT/'tools/recovery/factory121.py').read_bytes()).hexdigest())
    def test_factory_ret(self):self.assertEqual(self.r['ret'],0x6d5ec4)
    def test_allocator_sink_only(self):
        p=self.r['run']['executed_addresses'];self.assertNotIn(0x3c986c,p)
        self.assertIn(0x3cd56c,[x['entry'] for x in f.raw()['followed']])
    def test_allocator_request(self):
        q=self.r['allocator_requests'][0];self.assertEqual(q,dict(size=0x200,alignment=16,category=94,flag=0,label=0x12da21,aux=0xab,expected_size=0x200))
    def test_original_empty_label(self):self.assertEqual(bytes.fromhex(self.r['allocator_string'])[0],0)
    def test_original_string_span(self):self.assertEqual(bytes.fromhex(self.r['allocator_string'])[1:5],b'Unit')
    def test_constructor_executed(self):self.assertIn(0x6d353c,self.r['run']['executed_addresses'])
    def test_handle_service_executed(self):self.assertIn(0x572a38,self.r['run']['executed_addresses'])
    def test_cleanup_not_executed(self):self.assertNotIn(0x570ff0,self.r['run']['executed_addresses'])
    def test_returned_node(self):self.assertEqual(self.r['returned_node'],self.r['node'])
    def test_vtable_and_rela(self):
        self.assertEqual(self.r['node_after']['vptr'],0x10b1240)
        rr=f.merged()['relocations'];self.assertIn(dict(address=0x10b12c0,addend=0x6d46a8),rr)
    def test_owner_count(self):self.assertEqual(self.r['owner_after']['count'],42)
    def test_list_links(self):
        d=self.r['node_after'];self.assertEqual(d['owner_field'],self.r['owner']);self.assertEqual(d['list_next'],self.r['owner_after']['list_sentinel']);self.assertEqual(self.r['owner_after']['list_head'],self.r['node']+8)
    def test_flags_or(self):self.assertEqual(self.r['owner_after']['flags_halfword'],0xc8);self.assertEqual(self.r['node_after']['flags_halfword'],0xa5a5)
    def test_zero_prefill_flags(self):self.assertEqual(f.standalone(prefill=0,label=7,extra=0x40)['owner_after']['flags_halfword'],0xc8)
    def test_ff_prefill_flags(self):self.assertEqual(f.standalone(prefill=0xff,label=94,extra=0x100)['owner_after']['flags_halfword'],0xc8)
    def test_size_variant(self):self.assertEqual(f.standalone(prefill=0,label=7,extra=0x40)['allocator_requests'][0]['size'],0x240)
    def test_label_variant(self):self.assertEqual(struct.unpack_from('<I',bytes.fromhex(f.standalone(prefill=0,label=7,extra=0x40)['node_after']['image_hex']),0x18)[0],7)
    def test_pool_native_effects(self):
        s=self.r['service'];self.assertEqual((s['tag_before'],s['tag_after'],s['acquired_count'],s['chunk_length']),(0,1,1,1))
    def test_tag_variant(self):self.assertEqual(f.standalone(tag=41)['service']['tag_after'],42)
    def test_relocation(self):self.assertEqual(f.standalone(base=0x4000000)['ret'],0x6d5ec4)
    def test_upstream_caller(self):
        u=self.a['upstream_caller'];self.assertEqual((u['start'],u['end'],u['direct_call_pc']),(0x6d2950,0x6d29e4,0x6d2990));self.assertNotIn(0x6d2990,self.r['run']['executed_addresses'])
    def test_source_integration(self):
        s=self.a['source'];self.assertEqual(len(s['calls']),10);self.assertEqual(self.a['counts']['source_dwords'],930)
        for c in s['calls']:self.assertEqual(c['native']['completion_byte'],1)
    def test_source_bindings(self):self.assertEqual(self.a['source']['post_factory_bindings'],[0x118,0x128,0x130,0x1d0])
    def test_counts_partition(self):
        c=self.a['counts'];self.assertEqual((c['standalone_cases'],c['source_calls'],c['source_factory_instructions']>0,c['source_allocator_requests'],c['standalone_allocator_requests']),(3,10,True,1,3))
