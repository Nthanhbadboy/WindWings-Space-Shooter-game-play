import struct,unittest
from tools.verify.controller109_binary import Reader,DecodeError

def node(t,n='data',children=None,flag=0):return dict(type=t,name=n,children=children or [],meta_flag=flag,byte_size=-1)
def array(t='int'):return node('vector',children=[node('Array','Array',[node('int','size'),node(t)])])
class Binary109(unittest.TestCase):
 def test_01_signed32(self):self.assertEqual(Reader(struct.pack('<i',-7)).decode(node('int')),-7)
 def test_02_uint32(self):self.assertEqual(Reader(struct.pack('<I',0xffffffff)).decode(node('UInt32')),0xffffffff)
 def test_03_uint64_exact(self):self.assertEqual(Reader(struct.pack('<Q',2**63+19)).decode(node('UInt64')),2**63+19)
 def test_04_big_endian(self):self.assertEqual(Reader(struct.pack('>i',123),'>').decode(node('int')),123)
 def test_05_bool(self):self.assertIs(Reader(b'\1').decode(node('bool')),True)
 def test_06_noncanonical_bool(self):
  with self.assertRaisesRegex(DecodeError,'boolean'):Reader(b'\2').decode(node('bool'))
 def test_07_string_unicode_alignment(self):self.assertEqual(Reader(struct.pack('<i',2)+b'\xc3\xa9\x00\x00').decode(node('string')),'é')
 def test_08_padding_preserved_not_assumed_zero(self):
  r=Reader(b'\1abc');self.assertIs(r.decode(node('bool',flag=0x4000)),True);self.assertEqual(r.padding,[{'offset':1,'hex':'616263'}])
 def test_09_vector(self):self.assertEqual(Reader(struct.pack('<3i',2,100,-2)).decode(array()),[100,-2])
 def test_10_empty_array(self):self.assertEqual(Reader(b'\0'*4).decode(array()),[])
 def test_11_negative_count(self):
  with self.assertRaisesRegex(DecodeError,'count'):Reader(struct.pack('<i',-1)).decode(array())
 def test_12_large_count(self):
  with self.assertRaisesRegex(DecodeError,'count'):Reader(struct.pack('<i',1000001)).decode(array())
 def test_13_pair_map(self):
  p=node('pair',children=[node('UInt32','first'),node('int','second')]);s=node('map',children=[node('Array','Array',[node('int','size'),p])]);self.assertEqual(Reader(struct.pack('<3i',1,7,-9)).decode(s),[[7,-9]])
 def test_14_struct(self):self.assertEqual(Reader(struct.pack('<if',8,.5)).decode(node('Thing',children=[node('int','x'),node('float','y')])),{'x':8,'y':.5})
 def test_15_trailing_bytes(self):
  with self.assertRaisesRegex(DecodeError,'unconsumed'):Reader(b'\0'*5).decode(node('int'))
 def test_16_truncation(self):
  with self.assertRaisesRegex(DecodeError,'truncated'):Reader(b'\0'*3).decode(node('int'))
 def test_17_unsupported_leaf(self):
  with self.assertRaisesRegex(DecodeError,'unsupported leaf'):Reader(b'').decode(node('NoGuesses'))
 def test_18_duplicate_fields(self):
  with self.assertRaisesRegex(DecodeError,'duplicate'):Reader(b'\0'*8).decode(node('Thing',children=[node('int','x'),node('int','x')]))
 def test_19_depth_budget(self):
  with self.assertRaisesRegex(DecodeError,'nesting'):Reader(b'\0'*4,max_depth=0).decode(node('Thing',children=[node('int','x')]))
 def test_20_invalid_utf8(self):
  with self.assertRaisesRegex(DecodeError,'UTF8'):Reader(b'\1\0\0\0\xff\0\0\0').decode(node('string'))
if __name__=='__main__':unittest.main()
