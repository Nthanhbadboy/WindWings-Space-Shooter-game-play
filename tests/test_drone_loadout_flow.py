import json,unittest
from tools.verify.drone_loadout_flow import build,OUT
from tools.verify.drone_loadout_models import get_used,set_used,indices,load_plan,fix_duplicate

class Evidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.result=build()
    def test_reproducible(self):self.assertEqual(self.result,json.loads(OUT.read_text()))
    def test_methods(self):self.assertEqual(len(self.result['native_ranges']),5)
    def test_no_selected_component_errors(self):
        self.assertTrue(all('resource' in e or e.get('phase')=='header' for e in self.result['recovery_errors']))
    def test_actual_drone3_serialized_override(self):
        x=self.result['bindings'][2]['serialized'];self.assertEqual((x['turnRate'],x['shotRate'],x['turnNumber'],x['idBlt']),(1.,2.,3,80084))

class Fixtures(unittest.TestCase):
    def test_default_none(self):
        reads=[];self.assertEqual(get_used(0,lambda k,d:reads.append((k,d)) or d,self.fail),0);self.assertEqual(reads,[('DroneUsed0',0)]*2)
    def test_positive_reread(self):
        values=iter([20001,20003]);self.assertEqual(get_used(1,lambda *_:next(values),self.fail),20003)
    def test_negative_repaired(self):
        store={'DroneUsed1':-2};writes=[]
        def write(k,v):writes.append((k,v));store[k]=v
        self.assertEqual(get_used(1,lambda k,d:store.get(k,d),write),0);self.assertEqual(writes,[('DroneUsed1',0)])
    def test_setter_not_validation(self):
        calls=[];set_used(-3,-8,lambda *args:calls.append(args));self.assertEqual(calls,[('DroneUsed-3',-8)])
    def test_mode4_no_saved_reads(self):self.assertEqual(indices(4,self.fail),[0,0])
    def test_fresh_array(self):
        a=indices(4,self.fail);a[0]=20012;self.assertEqual(indices(4,self.fail),[0,0])
    def test_other_modes(self):
        for mode in [-1,0,1,2,3,5,6,100]:self.assertEqual(indices(mode,lambda s:20001+s),[20001,20002])
    def test_two_getters_not_snapshot(self):
        values=iter([[20001,20002],[20004,20003]]);p=load_plan(lambda:next(values));self.assertEqual([x['source_id'] for x in p],[20001,20003])
    def test_both_empty(self):self.assertEqual(load_plan(lambda:[0,0]),[])
    def test_signed_skip(self):self.assertEqual(load_plan(lambda:[-1,0]),[])
    def test_second_slot_not_reindexed(self):
        p=load_plan(lambda:[0,20003]);self.assertEqual((p[0]['slot'],p[0]['parent_child'],p[0]['local_position']),(1,1,[20.,-20.,0.]))
    def test_first_slot_geometry(self):
        p=load_plan(lambda:[20003,0])[0];self.assertEqual(p['local_position'],[-20.,-20.,0.]);self.assertEqual(p['scale'],[0.800000011920929,0.800000011920929,1.]);self.assertTrue(p['active'])
    def test_no_upper_id_validation_in_loader(self):self.assertEqual(load_plan(lambda:[20099,0])[0]['path'],'Prefabs/Drones/Drone_20099')
    def test_loader_no_deduplication(self):self.assertEqual(len(load_plan(lambda:[20001,20001])),2)
    def test_duplicate_fixes_slot_zero(self):
        writes=[];fix_duplicate(lambda _:20001,lambda i:i in (20001,20003),lambda *a:writes.append(a));self.assertEqual(writes,[(0,20003)])
    def test_duplicate_zero_no_scan(self):fix_duplicate(lambda _:0,self.fail,self.fail)
    def test_not_duplicate_no_scan(self):fix_duplicate(lambda slot:20001+slot,self.fail,self.fail)
    def test_duplicate_checks_flag_low_bit(self):
        writes=[];fix_duplicate(lambda _:20001,lambda i:3 if i==20004 else 2,lambda *a:writes.append(a));self.assertEqual(writes,[(0,20004)])
    def test_native_has_no_recovered_loop_cap(self):
        with self.assertRaisesRegex(RuntimeError,'fixture safety'):fix_duplicate(lambda _:20001,lambda _:0,self.fail,3)

def binding_test(source_id):
    def test(self):
        x=self.result['bindings'][source_id-20001];self.assertEqual((x['source_id'],x['cls']),(source_id,'Drone_Attack'+str(source_id-20000)));self.assertEqual(x['container_key'],x['resource_path'].lower());self.assertEqual(len(x['contexts']),3)
    return test
for sid in range(20001,20013):setattr(Evidence,'test_binding_'+str(sid),binding_test(sid))
