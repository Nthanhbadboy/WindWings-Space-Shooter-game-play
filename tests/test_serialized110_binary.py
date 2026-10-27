import struct,unittest
from tools.verify.serialized110_binary import parse,header,FormatError

def fixture(endian='<',version=22,class_id=91,type_id=0,path_id=17,relative=0,size=4,tree=0):
 p=lambda f,*v:struct.pack(endian+f,*v)
 b=b'2022.3.62f3\0'+p('iB',13,tree)+p('i',1)+p('iBh',class_id,0,-1)
 if class_id==114:b+=b'S'*16
 b+=b'H'*16+p('i',1);b+=b'\0'*((-(48+len(b)))%4);object_start=48+len(b);b+=p('qqIi',path_id,relative,size,type_id);b+=p('iii',0,0,0)+b'\0';meta=len(b);data_offset=(48+meta+15)&~15
 h=struct.pack('>4I',0,0,version,0)+bytes([endian=='>'])+b'\0'*3+struct.pack('>IQQQ',meta,data_offset+4,data_offset,0)
 return h+b+b'\0'*(data_offset-48-meta),object_start
class Serialized110(unittest.TestCase):
 def test_01_header(self):b,_=fixture();self.assertEqual(header(b)['version'],22)
 def test_02_parse_object(self):b,_=fixture();o=parse(b)['objects'][0];self.assertEqual((o['path_id'],o['class_id'],o['byte_size']),(17,91,4))
 def test_03_object_absolute_offset(self):b,_=fixture();r=parse(b);self.assertEqual(r['objects'][0]['byte_start'],r['header']['data_offset'])
 def test_04_big_endian(self):b,_=fixture('>');self.assertEqual(parse(b)['objects'][0]['path_id'],17)
 def test_05_monobehaviour_script_hash(self):b,_=fixture(class_id=114);self.assertEqual(parse(b)['types'][0]['script_id'],'53'*16)
 def test_06_metadata_end(self):b,_=fixture();r=parse(b);self.assertEqual(r['metadata_end'],48+r['header']['metadata_size'])
 def test_07_reject_other_version(self):
  with self.assertRaisesRegex(FormatError,'v22'):header(fixture(version=21)[0])
 def test_08_reject_type_tree(self):
  with self.assertRaisesRegex(FormatError,'type tree'):parse(fixture(tree=1)[0])
 def test_09_type_index_bounds(self):
  with self.assertRaisesRegex(FormatError,'type index'):parse(fixture(type_id=1)[0])
 def test_10_negative_object_offset(self):
  with self.assertRaisesRegex(FormatError,'bounds'):parse(fixture(relative=-1)[0])
 def test_11_outside_file(self):
  with self.assertRaisesRegex(FormatError,'bounds'):parse(fixture(size=5)[0])
 def test_12_short_header(self):
  with self.assertRaisesRegex(FormatError,'header'):header(b'\0'*47)
 def test_13_prefix_size_exact(self):
  with self.assertRaisesRegex(FormatError,'exactly'):parse(fixture()[0][:-1])
 def test_14_invalid_endian(self):
  b,_=fixture();b=bytearray(b);b[16]=2
  with self.assertRaisesRegex(FormatError,'endian'):header(b)
 def test_15_negative_pathid_is_signed_not_invalid(self):self.assertEqual(parse(fixture(path_id=-7)[0])['objects'][0]['path_id'],-7)
 def test_16_metadata_size_exact(self):
  b,_=fixture();b=bytearray(b);struct.pack_into('>I',b,20,header(b)['metadata_size']-1)
  with self.assertRaisesRegex(FormatError,'metadata_size'):parse(b)
 def test_17_64bit_relative_offset(self):
  b,_=fixture(relative=1<<33);b=bytearray(b);h=header(b);struct.pack_into('>Q',b,24,h['data_offset']+(1<<33)+4);self.assertEqual(parse(b)['objects'][0]['byte_start'],h['data_offset']+(1<<33))
if __name__=='__main__':unittest.main()
