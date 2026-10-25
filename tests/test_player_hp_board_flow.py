import json,unittest
from tools.verify.player_hp_board_models import *
from tools.verify.player_hp_board_flow import OUT,build


class Evidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=build()
    def test_contract_regenerated(self):self.assertEqual(self.r,json.loads(OUT.read_text()))
    def test_native_ranges(self):self.assertEqual((len(self.r['methods']),sum(x['instructions'] for x in self.r['methods']),len(self.r['anchors'])),(20,1589,80))
    def test_separate_arrays(self):self.assertEqual([x['length'] for x in self.r['arrays']],[24,12,12])
    def test_ui_basic_not_combat_base(self):self.assertEqual(self.r['arrays'][1]['values'][:3],[500,600,800])
    def test_ui_delta_point16(self):self.assertEqual(self.r['arrays'][2]['values'],[f32(.16)]*12)
    def test_repeat_literal(self):self.assertEqual(self.r['literals'][0]['utf8'],'AutoGainHealth')
    def test_bindings(self):self.assertEqual([x['MethodAddress'] for x in self.r['joins'] if 'MethodAddress' in x],[0x14c7d28,0x14c7fe8])
    def test_direct_census_not_helper_assumption(self):self.assertEqual(self.r['board_direct_GetBaseDamage_sites'],[])


class HP(unittest.TestCase):
    def refresh(self,s,mode=0,wave=0,new=2500,post=lambda *_:None,schedule=lambda *_:None,recover=.01,now=10,immune=50):
        return refresh64(s,mode=mode,wave=wave,get_start=lambda:new,get_recover=lambda:recover,post=post,schedule=schedule,now=lambda:now,get_immune=lambda:immune)
    def test_ctor_static_is_not_gameplay_formula(self):self.assertEqual((SharedHP().start,SharedHP().current),(2000,0))
    def test_zero_modifier_formula2500(self):self.assertEqual(get_start_hp(lambda _:0,lambda _:0),2500)
    def test_hp_uses_points0_and_ability7(self):
        c=[];get_start_hp(lambda i:c.append(('points',i)) or 1,lambda i:c.append(('ability',i)) or 0);self.assertEqual(c,[('points',0),('ability',7)])
    def test_point18_per_point(self):self.assertEqual(get_start_hp(lambda _:1,lambda _:0),f32(2500*f32(1+f32(.18))))
    def test_ability7_one_is_full_base_bonus(self):self.assertEqual(get_start_hp(lambda _:0,lambda _:1),5000)
    def test_per_op_float_order(self):
        expected=f32(2500*f32(f32(f32(f32(.18)*f32(3))+f32(2))+f32(1)))
        self.assertEqual(get_start_hp(lambda _:3,lambda _:2),expected)
    def test_no_lower_clamp_formula(self):self.assertLess(get_start_hp(lambda _:-10,lambda _:0),0)
    def test_reset_copies_start(self):
        s=SharedHP(start=3000,current=-10);reset_hp(s);self.assertEqual(s.current,3000)
    def test36_updates_max_only(self):
        s=SharedHP(start=5000,current=4800,tech_heal=50);ability_changed36(s,7,lambda:2500);self.assertEqual((s.start,s.current,s.tech_heal),(2500,4800,50))
    def test36_other_ability_skips_getter(self):
        s=SharedHP();ability_changed36(s,25,lambda:(_ for _ in ()).throw(RuntimeError()));self.assertEqual(s.start,2000)
    def test36_type_must_be_int32_not_bool(self):
        with self.assertRaises(TypeError):ability_changed36(SharedHP(),True,lambda:0)
    def test36_null(self):
        with self.assertRaises(ValueError):ability_changed36(SharedHP(),None,lambda:0)
    def test64_normal_resets_and_no_hp_event(self):
        c=[];s=SharedHP(current=900);self.refresh(s,post=lambda *x:c.append(x));self.assertEqual((s.start,s.current),(2500,2500));self.assertEqual(c,[])
    def test64_mode1_wave0_still_resets(self):
        s=SharedHP(current=500);self.refresh(s,mode=1,wave=0);self.assertEqual(s.current,2500)
    def test64_other_mode_nonzero_wave_resets(self):
        s=SharedHP(current=500);self.refresh(s,mode=4,wave=8);self.assertEqual(s.current,2500)
    def test64_mode1_nonzero_preserves_ratio(self):
        s=SharedHP(start=2000,current=500);c=[];self.refresh(s,mode=1,wave=2,post=lambda *x:c.append(x));self.assertEqual((s.start,s.current),(2500,625));self.assertEqual(c,[(21,625)])
    def test64_ratio_not_clamped(self):
        s=SharedHP(start=2000,current=4000);self.refresh(s,mode=1,wave=-1);self.assertEqual(s.current,5000)
    def test64_zero_current_stays_dead_in_preserve_branch(self):
        s=SharedHP();self.refresh(s,mode=1,wave=1);self.assertEqual(s.current,0)
    def test64_post_callback_before_recover_base_read(self):
        s=SharedHP(current=500)
        self.refresh(s,mode=1,wave=1,post=lambda *_:setattr(s,'start',1000));self.assertEqual(s.tech_heal,10)
    def test64_schedules_five_then_sets_immune(self):
        c=[];s=SharedHP();self.refresh(s,schedule=lambda *x:c.append((x,s.immune_deadline)));self.assertEqual(c,[(('AutoGainHealth',5,5),0)]);self.assertEqual(s.immune_deadline,60)
    def test_recover_level_bands(self):
        for lv,extra in ((0,None),(1,0),(2,.03),(3,.06),(4,.06),(5,.08),(7,.08),(8,.1)):
            self.assertEqual(recover_fraction(lv),0 if extra is None else f32(f32(.01)*f32(1+f32(extra))))
    def test_immune_bands(self):self.assertEqual([immune_interval(i) for i in (1,3,4,6,7,8,9,10)],[50,50,45,40,35,35,30,25])
    def test_immune_zero_uses_max_finite_not_infinity(self):self.assertEqual(immune_interval(0),f32(float.fromhex('0x1.fffffep+127')))
    def test_gain_only_upper_clamp(self):
        s=SharedHP(current=10);gain_health(s,-100,post=lambda *_:None);self.assertEqual(s.current,-90)
    def test_gain_fx_before_event_rereads_current(self):
        s=SharedHP(current=100);c=[];gain_health(s,10,post=lambda *x:c.append(x),has_fx=True,fx=lambda:setattr(s,'current',99));self.assertEqual(c,[(21,99)])
    def test_auto_dead_no_event(self):
        s=SharedHP(current=0,tech_heal=50);c=[];self.assertFalse(auto_gain(s,lambda *x:c.append(x)));self.assertEqual(c,[])
    def test_auto_chunk_not_delta_time_scaled(self):
        s=SharedHP(start=2500,current=1000,tech_heal=25,device_heal=50);auto_gain(s,lambda *_:None);self.assertEqual(s.current,1075)
    def test_auto_at_full_still_events(self):
        s=SharedHP(current=2000,tech_heal=25);c=[];auto_gain(s,lambda *x:c.append(x));self.assertEqual(c,[(21,2000)])
    def test_auto_can_reduce_overfull_current(self):
        s=SharedHP(start=2500,current=4800);auto_gain(s,lambda *_:None);self.assertEqual(s.current,2500)


class Device(unittest.TestCase):
    def apply(self,s,ids,devices,stat=lambda d:d['stat']):return change_devices(s,10003,get_ids=lambda _:ids,get_device=lambda i:devices.get(i),get_stat1=stat)
    def test_device_definition_id_not_instance_range(self):
        s=SharedHP();self.apply(s,[90000],{90000:dict(id=1000,stat=20)});self.assertEqual(s.device_reduction,f32(.2))
    def test_minus_one_skipped_only(self):
        s=SharedHP();self.apply(s,[-1,-2],{-2:dict(id=1001,stat=10)});self.assertEqual(s.device_reduction,f32(.1))
    def test_ranges_inclusive(self):
        for id in (1000,1999):
            s=SharedHP();self.apply(s,[3],{3:dict(id=id,stat=20)});self.assertEqual(s.device_reduction,f32(.2))
        for id in (999,2000,4999,6000):
            s=SharedHP();self.apply(s,[3],{3:dict(id=id,stat=20)});self.assertEqual((s.device_reduction,s.device_heal),(0,0))
    def test_device_heal_uses_shared_start(self):
        s=SharedHP(start=2500);self.apply(s,[1],{1:dict(id=5000,stat=2)});self.assertEqual(s.device_heal,50)
    def test_device_no_write_hp_max_or_current(self):
        s=SharedHP(start=2500,current=123);self.apply(s,[1],{1:dict(id=5999,stat=2)});self.assertEqual((s.start,s.current),(2500,123))
    def test_reduction_no_clamp1(self):
        s=SharedHP();self.apply(s,[1,2],{1:dict(id=1000,stat=80),2:dict(id=1001,stat=80)});self.assertGreater(s.device_reduction,1)
    def test_reset_before_null_array_error(self):
        s=SharedHP(device_heal=25,device_reduction=.5)
        with self.assertRaises(ValueError):self.apply(s,None,{})
        self.assertEqual((s.device_heal,s.device_reduction),(0,0))
    def test_helper_throw_before_reset(self):
        s=SharedHP(device_heal=25)
        def fail(_):raise RuntimeError()
        with self.assertRaises(RuntimeError):change_devices(s,1,get_ids=fail,get_device=lambda _:None,get_stat1=lambda _:0)
        self.assertEqual(s.device_heal,25)
    def test_partial_updates_not_rollback(self):
        s=SharedHP()
        with self.assertRaises(ValueError):self.apply(s,[1,2],{1:dict(id=1000,stat=20)})
        self.assertEqual(s.device_reduction,f32(.2))
    def test_start_snapshotted_before_stat_callback(self):
        s=SharedHP(start=2500)
        self.apply(s,[1],{1:dict(id=5000,stat=2)},stat=lambda _:(setattr(s,'start',5000) or 2));self.assertEqual(s.device_heal,50)


class Board(unittest.TestCase):
    basic=[500,600,800,1250,1500,1800,2300,2800,2535,2500,1251,2680]
    def power(self,source=20001,level=0,**kw):return board_power(source,get_level=kw.pop('get_level',lambda _:level),basic=kw.pop('basic',self.basic),delta=kw.pop('delta',[f32(.16)]*12),**kw)
    def test_source20001_not_combat450(self):self.assertEqual(self.power()['rounded'],500)
    def test_source20003_not_combat6000(self):self.assertEqual(self.power(20003)['rounded'],800)
    def test_level_modifier_point16(self):self.assertEqual(self.power(level=1)['power'],580)
    def test_clamp_below(self):self.assertEqual(self.power(19999)['rounded'],500)
    def test_clamp_above(self):self.assertEqual(self.power(20099)['rounded'],2680)
    def test_round_half_even(self):
        for base,result in ((2.5,2),(3.5,4),(-2.5,-2),(-3.5,-4)):
            self.assertEqual(self.power(basic=[base],delta=[0])['rounded'],result)
    def test_array_lengths_clamp_independent(self):self.assertEqual(self.power(20099,basic=[500],delta=[.1,.2],level=1)['power'],600)
    def test_level_getter_before_bad_array(self):
        c=[]
        with self.assertRaises(ValueError):self.power(get_level=lambda i:c.append(i) or 0,basic=None)
        self.assertEqual(c,[20001])
    def test_empty_array_throws_not_fake_zero(self):
        with self.assertRaises(IndexError):self.power(basic=[])


if __name__=='__main__':unittest.main()
