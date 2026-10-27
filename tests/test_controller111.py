import ast,gzip,json,unittest
from tools.verify.controller111 import build,OUT,RAW,ROOT,Envelope,sha
from tools.verify.unityfs111_binary import framing,decode,FormatError
class UnityFS111Evidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.saved=json.loads(gzip.decompress(OUT.read_bytes()));cls.raw=json.loads(gzip.decompress(RAW.read_bytes()))
    def test_01_full_regeneration(self):self.assertEqual(build(),self.saved)
    def test_02_input_pins(self):
        for p,h in self.saved['inputs'].items():self.assertEqual(sha((ROOT/p).read_bytes()),h,p)
    def test_03_no_codec_or_unitypy_import(self):
        t=ast.parse((ROOT/'tools/verify/unityfs111_binary.py').read_text());self.assertEqual([a.name for n in ast.walk(t) if isinstance(n,ast.Import) for a in n.names],['struct']);self.assertFalse(any(isinstance(n,ast.ImportFrom) for n in ast.walk(t)))
    def test_04_directory_reparse(self):self.assertEqual(framing(Envelope(self.raw['envelope'])),self.saved['frame'])
    def test_05_exact_two_source_nodes(self):self.assertEqual({f['node']['path'] for f in self.saved['files']},{'resources.assets','sharedassets2.assets'})
    def test_06_308_fresh_hashes(self):
        rs=[r for f in self.saved['files'] for r in f['ranges'] if r['kind']=='controller'];self.assertEqual(len(rs),308);self.assertTrue(all(r['sha256']==r['fresh_independent_sha256'] for r in rs))
    def test_07_two_original_prefixes(self):self.assertEqual(sorted(r['size'] for f in self.saved['files'] for r in f['ranges'] if r['kind']=='metadata_prefix'),[3344,16949184])
    def test_08_704961_object_rows(self):self.assertEqual(sum(f['object_count'] for f in self.saved['files']),704961)
    def test_09_three_original_codec_samples(self):
        self.assertEqual(len(self.raw['samples']),3);receipts={b['index']:b for b in self.raw['block_receipts']}
        for s in self.raw['samples']:
            b=receipts[s['block_index']];data=decode(bytes.fromhex(s['compressed_hex']),b['flags'],b['uncompressed_size']);self.assertEqual(sha(data),b['decoded_sha256'])
    def test_10_no_fake_missing_payload(self):
        e=Envelope(self.raw['envelope']);b=self.saved['frame']['blocks'][0]
        with self.assertRaises(ValueError):e[b['physical_start']:b['physical_start']+b['compressed_size']]
    def test_11_node_range_translation(self):
        for f in self.saved['files']:
            for r in f['ranges']:self.assertEqual(r['logical_start'],f['node']['offset']+r['offset'])
    def test_12_selected_block_receipts_unique(self):
        rs=self.saved['selected_block_receipts'];self.assertEqual(len(rs),len({r['index'] for r in rs}))
    def test_13_literal_hash_not_validation(self):self.assertTrue(any('not a validated checksum' in s for s in self.saved['limits']))
    def test_14_local_vs_recovery_limits(self):self.assertTrue(any('unpreserved blocks cannot be redecoded locally' in s for s in self.saved['limits']))
    def test_15_no_schema_or_runtime_closure(self):self.assertTrue(any('schema still UnityPy builtin' in s for s in self.saved['limits']))
    def test_16_sample_codec_truncation(self):
        s=self.raw['samples'][0];b=next(b for b in self.raw['block_receipts'] if b['index']==s['block_index'])
        with self.assertRaises(FormatError):decode(bytes.fromhex(s['compressed_hex'])[:1],b['flags'],b['uncompressed_size'])
if __name__=='__main__':unittest.main()
