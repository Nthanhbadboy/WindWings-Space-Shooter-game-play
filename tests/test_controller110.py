import ast,gzip,json,struct,unittest
from tools.verify.controller110 import ROOT,RAW,OUT,build,sha
from tools.verify.serialized110_binary import parse,FormatError
class Framing110(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.saved=json.load(gzip.open(OUT));idx=json.loads((RAW/'index.json').read_bytes());f=next(f for f in idx['files'] if f['serialized_file'].endswith('sharedassets2.assets'));cls.prefix=bytes.fromhex(''.join(json.load(gzip.open(RAW/c['path']))['hex'] for c in f['prefix_chunks']));cls.parsed=parse(cls.prefix)
 def test_01_regenerate(self):self.assertEqual(build(),self.saved)
 def test_02_input_pins(self):
  for p,h in self.saved['inputs'].items():self.assertEqual(sha(ROOT/p),h,p)
 def test_03_parser_imports_stdlib_only(self):
  tree=ast.parse((ROOT/'tools/verify/serialized110_binary.py').read_text());imports=[a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names];self.assertEqual(imports,['struct'])
 def test_04_full_table_counts(self):self.assertEqual(sorted(f['object_count'] for f in self.saved['files']),[118,704843]);self.assertEqual(self.saved['independent_table_objects'],704961)
 def test_05_controller_count308(self):self.assertEqual(self.saved['controller_count'],308)
 def test_06_both_table_digests_equal(self):self.assertTrue(all(f['unitypy_digest_equal'] for f in self.saved['files']))
 def test_07_metadata_consumption_exact(self):
  for f in self.saved['files']:self.assertEqual(f['metadata_end'],48+f['header']['metadata_size'])
 def test_08_793_refs_791_distinct(self):
  refs=self.saved['clip_references'];self.assertEqual(len(refs),793);self.assertEqual(len({(r['target']['serialized_file'],r['target']['path_id']) for r in refs}),791)
 def test_09_all_clip_class74(self):self.assertEqual({r['status'] for r in self.saved['clip_references']},{'resolved_class74_from_independent_table'})
 def test_10_crossfile_is_fourth_external_not_local(self):
  refs=[r for r in self.saved['clip_references'] if r['pointer']['m_FileID']];self.assertEqual(len(refs),1);r=refs[0];self.assertEqual((r['controller']['serialized_file'],r['controller']['path_id'],r['pointer']['m_FileID'],r['target']['serialized_file'],r['target']['path_id']),('data.unity3d/sharedassets2.assets',91,4,'data.unity3d/resources.assets',970))
 def test_11_duplicate_real_pathid_fail(self):
  b=bytearray(self.prefix);a,z=self.parsed['objects'][:2];struct.pack_into('<q',b,z['record_start'],a['path_id'])
  with self.assertRaisesRegex(FormatError,'duplicate'):parse(b)
 def test_12_invalid_real_type_index_fail(self):
  b=bytearray(self.prefix);struct.pack_into('<i',b,self.parsed['objects'][0]['record_start']+20,999999)
  with self.assertRaisesRegex(FormatError,'type index'):parse(b)
 def test_13_real_metadata_size_mismatch_fail(self):
  b=bytearray(self.prefix);struct.pack_into('>I',b,20,self.parsed['header']['metadata_size']-1)
  with self.assertRaisesRegex(FormatError,'metadata_size'):parse(b)
 def test_14_version_exact(self):self.assertEqual({f['unity_version'] for f in self.saved['files']},{'2022.3.62f3'})
 def test_15_bundle_and_schema_limits(self):self.assertIn('UnityFS bundle decompression/file naming',self.saved['scope']);self.assertIn('not clean-room',self.saved['common_mode_limits'][2])
if __name__=='__main__':unittest.main()
