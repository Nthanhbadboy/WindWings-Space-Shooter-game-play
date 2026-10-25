import json,unittest
from tools.verify.wing_implementations import build,OUT
from tools.verify.wing_config_models import CONFIG,count_index,configure
from tools.verify.wing_native_fixture import SetBarrelsFixture,NativeFault

class Evidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.contract=build();cls.rows={int(x['implementation'].split('_')[-1]):x for x in cls.contract['implementations']}
    def test_reproducible(self):self.assertEqual(self.contract,json.loads(OUT.read_text()))
    def test_24_classes(self):self.assertEqual(set(self.rows),set(range(1,25)))
    def test_17_native_config_functions(self):self.assertEqual({i for i,x in self.rows.items() if x['normal_set_barrels']},set(CONFIG))
    def test_seven_nonprojectile_methods_named(self):self.assertEqual({i for i,x in self.rows.items() if x['special_path']},{2,4,6,8,10,12,15})
    def test_id2_proven_not_false_full_tree(self):self.assertEqual((self.rows[2]['source_id'],self.rows[2]['identity_provenance']),(10002,'raw_prefix_id_not_full_particle_curve_tree'))
    def test_source_id_swap(self):self.assertEqual((self.rows[1]['source_id'],self.rows[3]['source_id']),(10003,10001))

class NativeConfigurations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.rows={int(x['implementation'].split('_')[-1]):x for x in json.loads(OUT.read_text())['implementations']}
    def fixture(self,i):
        row=self.rows[i];return SetBarrelsFixture(row['implementation'],row['fields'])
    def numbers(self,i):
        arr=self.rows[i]['numeric_array'];return tuple(arr['values']) if arr else tuple(range(100,110))
    def compare(self,i,*,rate=1.,speed=10.):
        vm=self.fixture(i)
        for level in range(11):
            got=vm.run(level,start_rate=rate,start_speed=speed,numbers=self.numbers(i))
            expected=configure(i,level=level,start_rate=rate,start_speed=speed)
            for key,value in expected.items():self.assertEqual(got[key],value,(i,level,key,got,expected))
            if i!=19:
                idx=count_index(i,level,level,len(self.numbers(i)))
                if i in (3,18):self.assertEqual(got['barrel_list_index'],idx)
                else:self.assertEqual(got['numberNormal'],self.numbers(i)[idx])
    def super_branch(self,i):
        vm=self.fixture(i);got=vm.run(10,super_mode=True,numbers=self.numbers(i));self.assertEqual(got['shotRate'],-7.)
        if 'btlSpeed' in got:self.assertEqual(got['btlSpeed'],-8.)
        if 'angleDelta' in got:self.assertEqual(got['angleDelta'],2. if i==20 else -9.)
    def null_branch(self,i):
        with self.assertRaisesRegex(NativeFault,'null'):self.fixture(i).run(has_player=False)
    def test_level_rereads_not_cache(self):
        got=self.fixture(1).run(levels=[10,2,20,3],numbers=self.numbers(1));self.assertEqual(got['level_reads'],[10,2,20,3]);self.assertEqual(got['numberNormal'],self.numbers(1)[2]);self.assertEqual(got['angleDelta'],11.)
    def test_linear_index_no_silent_upper_cap(self):
        with self.assertRaisesRegex(NativeFault,'bounds'):self.fixture(5).run(100,numbers=self.numbers(5))
    def test_compressed_index_caps(self):self.assertEqual(self.fixture(1).run(100,numbers=self.numbers(1))['numberNormal'],self.numbers(1)[-1])
    def test_empty_array_is_exception(self):
        with self.assertRaisesRegex(NativeFault,'bounds'):self.fixture(1).run(0,numbers=())

def make_test(fn,i,**kw):
    def test(self):getattr(self,fn)(i,**kw)
    return test
for i in CONFIG:
    for tag,fn,kw in [('normal','compare',{}),('floors_caps','compare',{'rate':0.,'speed':100.}),('super','super_branch',{}),('null','null_branch',{})]:setattr(NativeConfigurations,f'test_{tag}_{i}',make_test(fn,i,**kw))
