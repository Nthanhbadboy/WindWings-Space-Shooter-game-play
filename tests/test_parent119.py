import unittest,gzip,json
from tools.verify import parent119 as p
class Parent119(unittest.TestCase):
    def test_regeneration(self):
        self.assertEqual(p.build(),json.load(gzip.open(p.OUT)))
    def test_parent_ret_and_completion(self):
        f=p.fixture();r=f.parent();self.assertEqual(r['last_native_pc'],0x6d46f0);self.assertEqual(r['completion_byte'],1)
        self.assertIn(0x6d4424,r['run']['executed_addresses'])
    def test_null_parent(self):
        r=p.fixture().parent(missing=True);self.assertEqual(r['completion_byte'],1);self.assertEqual(r['external_calls'],[])
    def test_guard_missing(self):
        r=p.fixture().second_guard(True,0,1);self.assertNotIn(0x6d3eec,r['run']['executed_addresses'])
    def test_guard_mode(self):
        r=p.fixture().second_guard(False,-1,1);self.assertNotIn(0x6d3f00,r['run']['executed_addresses'])
    def test_guard_flag(self):
        r=p.fixture().second_guard(False,0,0);self.assertNotIn(0x6d3f08,r['run']['executed_addresses'])
    def test_reject_active(self):
        with self.assertRaises(ValueError):p.fixture().second_guard(False,0,1)
    def test_reject_parent_pose(self):
        f=p.fixture();f.put(f.parameters+0x28,b'\1',False)
        with self.assertRaises(ValueError):f.parent()
    def test_relocation(self):
        r=p.fixture(base=0x4000000).parent();self.assertEqual(r['completion_byte'],1)
    def test_stack_prefill(self):
        a=p.fixture().parent();b=p.fixture(stack_prefill=0xa5).parent();self.assertEqual(a['output_bits'],b['output_bits']);self.assertEqual(a['context'],b['context'])
