import struct,unittest
from tools.verify.unityfs111_binary import framing,read_range,decode,lz4,FormatError

def literal(b):
    n=len(b);out=bytes([min(n,15)<<4]);extra=n-15
    if extra>=0:
        while extra>=255:out+=b'\xff';extra-=255
        out+=bytes([extra])
    return out+b

def bundle(payload=b'abcdefghij',end=False,pad=False,version=7,codec=2,nodes=None):
    packed=literal(payload) if codec in (2,3) else payload
    nodes=nodes if nodes is not None else [(0,len(payload),0,'resources.assets')]
    info=b'\0'*16+struct.pack('>iIIH',1,len(payload),len(packed),codec)+struct.pack('>i',len(nodes))
    for a,z,f,p in nodes:info+=struct.pack('>qqI',a,z,f)+p.encode()+b'\0'
    ci=literal(info);flags=64+2+(128 if end else 0)+(512 if pad else 0)
    prefix=b'UnityFS\0'+struct.pack('>I',version)+b'5.x.x\0'+b'2022.3.62f3\0'
    header=prefix+struct.pack('>qIII',0,len(ci),len(info),flags)
    start=(len(header)+15)//16*16 if version==7 else len(header)
    h=header+b'\0'*(start-len(header));body=(b'' if end else ci)
    if pad:body+=b'\0'*((-(len(h)+len(body)))%16)
    blob=h+body+packed+(ci if end else b'');blob=blob[:len(prefix)]+struct.pack('>q',len(blob))+blob[len(prefix)+8:];return blob

class UnityFS111(unittest.TestCase):
    def test_literal(self):self.assertEqual(lz4(literal(b'abc'),3),b'abc')
    def test_long_literal(self):self.assertEqual(lz4(literal(b'x'*600),600),b'x'*600)
    def test_overlapping_match(self):self.assertEqual(lz4(b'\x1fA\x01\x00\x01',21),b'A'*21)
    def test_nonoverlapping_match(self):self.assertEqual(lz4(b'\x40abcd\x04\x00',8),b'abcdabcd')
    def test_zero_distance(self):
        with self.assertRaisesRegex(FormatError,'distance'):lz4(b'\x10A\0\0',5)
    def test_far_distance(self):
        with self.assertRaisesRegex(FormatError,'distance'):lz4(b'\x10A\x02\0',5)
    def test_truncated_literal(self):
        with self.assertRaises(FormatError):lz4(b'\x40ab',4)
    def test_truncated_extension(self):
        with self.assertRaises(FormatError):lz4(b'\xf0\xff',600)
    def test_wrong_size(self):
        with self.assertRaises(FormatError):lz4(literal(b'ab'),3)
    def test_output_overflow(self):
        with self.assertRaises(FormatError):lz4(b'\x10A\x01\0',4)
    def test_lz4hc(self):self.assertEqual(decode(literal(b'ab'),3,2),b'ab')
    def test_uncompressed(self):self.assertEqual(decode(b'ab',0,2),b'ab')
    def test_unknown_codec(self):
        with self.assertRaises(FormatError):decode(b'ab',1,2)
    def test_flags_unknown(self):
        with self.assertRaises(FormatError):decode(b'ab',256,2)
    def test_begin_info(self):
        b=bundle();f=framing(b);self.assertEqual(read_range(b,f,2,4),b'cdef');self.assertEqual(f['nodes'][0]['path'],'resources.assets')
    def test_end_info(self):
        b=bundle(end=True);self.assertEqual(read_range(b,framing(b),0,10),b'abcdefghij')
    def test_padding_begin(self):
        b=bundle(pad=True);self.assertEqual(read_range(b,framing(b),0,10),b'abcdefghij')
    def test_padding_end(self):
        b=bundle(end=True,pad=True);self.assertEqual(read_range(b,framing(b),0,10),b'abcdefghij')
    def test_v6(self):
        b=bundle(version=6);self.assertEqual(read_range(b,framing(b),0,10),b'abcdefghij')
    def test_raw_block(self):
        b=bundle(codec=0);self.assertEqual(read_range(b,framing(b),0,10),b'abcdefghij')
    def test_duplicate_node(self):
        with self.assertRaisesRegex(FormatError,'duplicate'):framing(bundle(nodes=[(0,5,0,'a'),(5,5,0,'a')]))
    def test_overlapping_nodes(self):
        with self.assertRaisesRegex(FormatError,'overlapping'):framing(bundle(nodes=[(0,6,0,'a'),(5,5,0,'b')]))
    def test_node_bounds(self):
        with self.assertRaisesRegex(FormatError,'bounds'):framing(bundle(nodes=[(0,11,0,'a')]))
    def test_unsafe_path(self):
        with self.assertRaisesRegex(FormatError,'unsafe'):framing(bundle(nodes=[(0,10,0,'../a')]))
    def test_size_mismatch(self):
        with self.assertRaisesRegex(FormatError,'physical'):framing(bundle()+b'\0')
    def test_signature(self):
        with self.assertRaisesRegex(FormatError,'signature'):framing(b'Wrong\0')
    def test_version(self):
        with self.assertRaisesRegex(FormatError,'version'):framing(bundle(version=8))
    def test_truncated(self):
        with self.assertRaises(FormatError):framing(bundle()[:32])
    def test_negative_range(self):
        b=bundle()
        with self.assertRaises(FormatError):read_range(b,framing(b),-1,3)
    def test_empty_range(self):
        b=bundle();self.assertEqual(read_range(b,framing(b),10,0),b'')
if __name__=='__main__':unittest.main()
