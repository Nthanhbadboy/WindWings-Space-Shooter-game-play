import gzip,hashlib,json,unittest
from tools.verify import graph127 as g
class Graph127(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.a=json.load(gzip.open(g.OUT))
    def test_regenerate(self):self.assertEqual(g.build(),self.a)
    def test_claim(self):self.assertEqual(self.a['claim'],6425979864)
    def test_tool_pin(self):self.assertEqual(self.a['inputs']['tools/verify/graph127.py'],hashlib.sha256((g.ROOT/'tools/verify/graph127.py').read_bytes()).hexdigest())
    def test_fde(self):
        x=self.a['graph_builder'];self.assertEqual((x['entry'],x['fde_end'],x['ret'],x['epilogue']),(0x6cf7b4,0x6cff44,0x6cff3c,0x6cff0c))
    def test_callee_rets(self):
        c=self.a['graph_builder']['callees']
        self.assertEqual(c['0x6ceeb0'],dict(ret=0x6cef60,fde_end=0x6cef64))
        self.assertEqual(c['0xb98c98']['ret'],0xb98d68);self.assertEqual(c['0x6f15cc']['fde_end'],0x6f16bc);self.assertEqual(c['0x6cff44']['ret'],0x6d0068)
        self.assertEqual(len(c),6)
    def test_witnesses(self):self.assertEqual(len(self.a['witnesses']),33);self.assertTrue(all(len(w['word_hex'])==8 for w in self.a['witnesses']))
    def test_required_fields(self):
        f={x['offset']:x for x in self.a['required_fields']};self.assertIn('0x118',f);self.assertIn('0x1c8',f);self.assertEqual(len(f),11)
    def test_missing_x(self):self.assertEqual([x['id'] for x in self.a['missing_x']],['M1','M2','M3','M4','M5'])
    def test_cases(self):
        c=self.a['cases'];self.assertEqual(len(c),3);self.assertEqual([x['prefill'] for x in c],[0xa5,0,0xa5]);self.assertEqual(c[2]['base'],0x4000000)
    def test_all_cases_ret_and_stack(self):
        for c in self.a['cases']:self.assertEqual(c['ret'],0x6cff3c);self.assertEqual(c['stack_pointer_after'],c['base']+0x1f000)
    def test_pc_hits(self):
        h=self.a['cases'][0]['pc_hits'];self.assertEqual(h['0x6cf7b4'],1);self.assertEqual(h['0x6ceeb0'],1);self.assertEqual(h['0x6cff0c'],1);self.assertEqual(h['0x6cff3c'],1);self.assertNotIn('0x6cefc0',h)
    def test_build_path_not_executed(self):
        h=self.a['cases'][0]['pc_hits'];self.assertNotIn('0x6cef18',h);self.assertNotIn('0x6cef04',h)
    def test_dealloc_service(self):
        for c in self.a['cases']:self.assertEqual(len(c['service_calls']),1);self.assertEqual(c['service_calls'][0]['symbol'],'dealloc_3c9438');self.assertEqual(c['service_calls'][0]['object'],0)
    def test_node_cleanup(self):
        n=self.a['cases'][0]['node_after'];self.assertEqual((n['slot118'],n['slot1a0'],n['slot1c0'],n['count1c8']),(0,0,0,0))
    def test_counts(self):
        c=self.a['counts'];self.assertEqual((c['cases'],c['callees'],c['witnesses'],c['missing_x']),(3,6,33,5));self.assertEqual(len(c['native_instructions']),3)
    def test_relocation_case(self):self.assertEqual(self.a['cases'][2]['base'],0x4000000)
    def test_scope_not_build_path(self):
        s=self.a['scope'];self.assertIn('NOT the build path',s);self.assertIn('mapped, not fabricated',s)
