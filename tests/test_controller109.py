import copy,gzip,json,struct,unittest
from tools.verify.controller109 import ROOT,RAW,OUT,build,sha
from tools.verify.controller109_binary import Reader,DecodeError
class Controller109(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.saved=json.load(gzip.open(OUT));cls.idx=json.loads((RAW/'index.json').read_bytes());cls.row=json.load(gzip.open(RAW/cls.idx['chunks'][0]['path']))[0];cls.data=bytes.fromhex(cls.row['hex']);cls.schema=cls.idx['schemas'][cls.row['schema_sha256']]
 def test_01_regenerate(self):self.assertEqual(build(),self.saved)
 def test_02_input_pins(self):
  for p,h in self.saved['inputs'].items():self.assertEqual(sha(ROOT/p),h,p)
 def test_03_independent_code_no_unitypy_import(self):
  import ast
  t=ast.parse((ROOT/'tools/verify/controller109_binary.py').read_text());names=[n.module or '' for n in ast.walk(t) if isinstance(n,ast.ImportFrom)]+[a.name for n in ast.walk(t) if isinstance(n,ast.Import) for a in n.names];self.assertEqual(names,['struct'])
 def test_04_all308_fully_consumed(self):self.assertEqual(sum(r['byte_size']==r['consumed_bytes'] for r in self.saved['results']),308)
 def test_05_full_tree_digest(self):self.assertTrue(all(r['decoded_tree_sha256']==r['unitypy_tree_sha256'] for r in self.saved['results']))
 def test_06_232_qualified_identity_joins(self):self.assertEqual(len({(r['serialized_file'],r['path_id']) for r in self.saved['previous232_joins']}),232)
 def test_07_old232_states_and_transitions(self):
  c=self.saved['previous232_counts'];self.assertEqual((c['states'],c['any_transitions'],c['state_transitions'],c['selector_transitions'],c['conditions']),(667,343,125,464,376))
 def test_08_selector_presence_preserved(self):self.assertEqual(self.saved['previous232_counts']['selectors_without_interruption_field'],464)
 def test_09_all_schema_dependency_explicit(self):self.assertEqual({r['schema_source'] for r in self.saved['results']},{'UnityPy builtin type database'})
 def test_10_shared_schema_not_independent_discovery(self):self.assertIn('NOT independent schema discovery',self.saved['scope'])
 def test_11_ControllerSize_not_disk_length(self):self.assertTrue(any(r['declared_ControllerSize_literal']!=r['controller_disk_span_bytes'] for r in self.saved['results']))
 def test_12_real_payload_truncation(self):
  with self.assertRaises(DecodeError):Reader(self.data[:-1],self.row['endian']).decode(self.schema)
 def test_13_real_payload_trailing_junk(self):
  with self.assertRaisesRegex(DecodeError,'unconsumed'):Reader(self.data+b'\0',self.row['endian']).decode(self.schema)
 def test_14_corrupt_name_count(self):
  with self.assertRaisesRegex(DecodeError,'count'):Reader(struct.pack('<i',-1)+self.data[4:]).decode(self.schema)
 def test_15_real_schema_missing_field_fails_closed(self):
  s=copy.deepcopy(self.schema);s['children'].pop()
  with self.assertRaisesRegex(DecodeError,'unconsumed'):Reader(self.data,self.row['endian']).decode(s)
 def test_16_boolean_flip_decodes_but_differential_detects(self):
  r=Reader(self.data,self.row['endian']);r.decode(self.schema);span=next(s for s in r.root_spans if s['field']=='m_MultiThreadedStateMachine');b=bytearray(self.data);b[span['start']]^=1;self.assertNotEqual(Reader(b,self.row['endian']).decode(self.schema),self.row['unitypy_tree'])
if __name__=='__main__':unittest.main()
