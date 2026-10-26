import gzip,json,struct,unittest,hashlib
from tools.verify import node120 as n
class Node120(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=n.standalone()
    def image(self):return bytes.fromhex(self.r['image_hex'])
    def test_regenerate(self):self.assertEqual(n.build(),json.load(gzip.open(n.OUT)))
    def test_original_constructor_fde(self):
        f=next(x for x in n.raw()['followed'] if x['entry']==0x6d353c);self.assertEqual(f['unwind']['end'],0x6d35f8)
    def test_tool_pin(self):self.assertEqual(n.raw()['tool_sha256'],hashlib.sha256((n.ROOT/'tools/recovery/node120.py').read_bytes()).hexdigest())
    def test_original_vtable(self):self.assertEqual(struct.unpack_from('<Q',self.image())[0],0x10b1240)
    def test_secondary_vtable(self):self.assertEqual(struct.unpack_from('<Q',self.image(),0x110)[0],0x10b1420)
    def test_ret(self):self.assertEqual(self.r['ret'],0x6d35f4)
    def test_native_bases(self):
        for pc in (0x57054c,0x57ef84,0x575e80,0x575c60,0x53f36c,0x6d6aa0,0x6a6ff4):self.assertIn(pc,self.r['run']['executed_addresses'])
    def test_no_allocator_branch(self):
        for pc in (0x575b34,0x573a1c):self.assertNotIn(pc,self.r['run']['executed_addresses'])
    def test_native_defaults(self):
        b=self.image()
        for a in (0x60,0x118,0x120,0x128,0x130,0x138,0x150,0x158,0x178,0x1d0):self.assertEqual(struct.unpack_from('<Q',b,a)[0],0)
        for a,v in ((0x184,0x3f800000),(0x194,0xbf800000),(0x198,0xbf800000),(0x1fc,0xbf800000),(0x3c,3)):self.assertEqual(struct.unpack_from('<I',b,a)[0],v)
    def test_label_passed(self):self.assertEqual(struct.unpack_from('<I',self.image(),0x18)[0],94)
    def test_label_variant(self):self.assertEqual(struct.unpack_from('<I',bytes.fromhex(n.standalone(label=7)['image_hex']),0x18)[0],7)
    def test_padding_preserved(self):
        for i in self.r['preserved_offsets']:self.assertEqual(self.image()[i],0xa5)
    def test_prefill_invariant_written_bytes_except_bitfield(self):
        b=bytes.fromhex(n.standalone(prefill=0)['image_hex'])
        for i in self.r['written_offsets']:
            if i not in (0x39,0x3a,0x3b):self.assertEqual(b[i],self.image()[i],hex(i))
    def test_native_pool_pop(self):self.assertEqual(self.r['pool']['queue_head_after'],0);self.assertEqual(self.r['pool']['queue_tag_after'],1)
    def test_pool_count_and_slot(self):self.assertEqual(self.r['pool']['acquired_count'],1);self.assertEqual(self.r['pool']['chunk_length_after'],1);self.assertEqual(self.r['pool']['slot0'],0)
    def test_chunk_old_count_reset(self):self.assertEqual(n.standalone(old_count=3)['pool']['chunk_length_after'],1)
    def test_pool_tag_increment(self):self.assertEqual(n.standalone(tag=41)['pool']['queue_tag_after'],42)
    def test_relocation(self):self.assertEqual(n.standalone(base=0x4000000)['ret'],0x6d35f4)
    def test_coverage_partition(self):self.assertEqual(len(self.r['written_offsets'])+len(self.r['preserved_offsets']),512)
    def test_no_external_constructor(self):self.assertEqual(self.r['external_calls'],[])
