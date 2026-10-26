import gzip,json,struct,unittest
from tools.verify.board_power107 import ROOT,RAW,OUT,build,sha
from tools.verify.board_power107_native import run
from tools.verify.player_hp_board_models import board_power
class BoardPower107(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.saved=json.load(gzip.open(OUT));cls.basic,cls.delta=[a['values'] for a in cls.saved['arrays']]
 def native(self,source=10001,level=0,**kw):return run(source,level,kw.pop('basic',self.basic),kw.pop('delta',self.delta),**kw)
 def test_01_regenerate(self):self.assertEqual(build(),self.saved)
 def test_02_input_pins(self):
  for p,h in self.saved['inputs'].items():self.assertEqual(sha(ROOT/p),h,p)
 def test_03_recovery_pin(self):self.assertEqual(json.loads((RAW/'cells.json').read_bytes())['tool_sha256'],sha(ROOT/'tools/recovery/board_power107.py'))
 def test_04_two_attack24_not_drone12(self):self.assertEqual([a['count'] for a in self.saved['arrays']],[24,24])
 def test_05_delta_literal_bits(self):self.assertEqual(self.saved['arrays'][1]['hex'],'31082c3e'*24)
 def test_06_basic_exact(self):self.assertEqual(self.basic,[4640,5120,5040,6160,8896,6880,8889,5680,5500,9100,6750,7589,6000,7588,9100,10050,7590,5550,10045,7588,10048,7589,10048,7589])
 def test_07_method_census(self):self.assertEqual((len(self.saved['methods']),sum(m['instructions'] for m in self.saved['methods'])),(5,1016))
 def test_08_fixture_census(self):self.assertEqual(len(self.saved['fixtures']),98)
 def test_09_first_level0(self):self.assertEqual(self.native()['rounded'],4640)
 def test_10_first_level1(self):self.assertEqual(self.native(level=1)['rounded'],5420)
 def test_11_last_level1(self):self.assertEqual(self.native(10024,1)['rounded'],8864)
 def test_12_below_clamp(self):self.assertEqual(self.native(10000,1)['rounded'],5420)
 def test_13_above_clamp(self):self.assertEqual(self.native(10025,1)['rounded'],8864)
 def test_14_original_source_to_level_hook_not_clamped(self):self.assertEqual(self.native(10025)['calls'][0],{'operation':'GetPlayerLevel','x0':10025})
 def test_15_positive_ties_even(self):
  for n,w in [(.5,0),(1.5,2),(2.5,2),(3.5,4)]:self.assertEqual(self.native(basic=[n],delta=[0])['rounded'],w)
 def test_16_negative_ties_even(self):
  for n,w in [(-.5,0),(-1.5,-2),(-2.5,-2),(-3.5,-4)]:self.assertEqual(self.native(basic=[n],delta=[0])['rounded'],w)
 def test_17_independent_delta_clamp(self):self.assertEqual(self.native(10099,1,basic=[500],delta=[.1,.2])['rounded'],600)
 def test_18_independent_basic_clamp(self):self.assertEqual(self.native(10099,1,basic=[500,1000],delta=[.1])['rounded'],1100)
 def test_19_null_basic(self):
  with self.assertRaisesRegex(ValueError,'native null'):self.native(basic=None)
 def test_20_null_delta(self):
  with self.assertRaisesRegex(ValueError,'native null'):self.native(delta=None)
 def test_21_empty_basic(self):
  with self.assertRaisesRegex(IndexError,'native array bounds'):self.native(basic=[])
 def test_22_empty_delta(self):
  with self.assertRaisesRegex(IndexError,'native array bounds'):self.native(delta=[])
 def test_23_external_hooks_explicit(self):self.assertEqual([c['operation'] for c in self.native()['calls']],['GetPlayerLevel','modf','Int32.ToString','Concat'])
 def test_24_model_negative_level(self):
  n=self.native(level=-1);m=board_power(10001,get_level=lambda _:-1,basic=self.basic,delta=self.delta,index_default=10001);self.assertEqual(n['pre_round_f32'],m['power']);self.assertEqual(n['rounded'],m['rounded'])
 def test_25_fixture_rejects_wrapping_source(self):
  with self.assertRaisesRegex(ValueError,'fixture signed'):self.native(-(1<<31))
 def test_26_sink_qualified(self):
  s=self.saved['ui_sink'];self.assertEqual({x['serialized_file'] for x in s},{'data.unity3d/resources.assets'});b=next(x for x in s if x['path_id']==650952);self.assertEqual(b['tree']['textPlayerPower'],{'m_FileID':0,'m_PathID':619564})
 def test_27_not_drone_coefficient(self):self.assertNotEqual(self.delta[0],struct.unpack('<f',struct.pack('<f',.16))[0])
 def test_28_source_not_damage(self):self.assertIn('NOT live Unity, DPS',self.saved['scope'])
if __name__=='__main__':unittest.main()
