import json,unittest
from tools.verify.wing_drone_flow import ROOT,OUT,build
from tools.verify.wing_drone_models import *


class Evidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=build()
    def test_regeneration(self):self.assertEqual(json.loads(OUT.read_text()),self.r)
    def test_current_all12(self):self.assertEqual({m['cls'] for m in self.r['methods'] if m['cls'].startswith('Drone_Attack')}, {'Drone_Attack'}|{f'Drone_Attack{i}' for i in range(1,13)})
    def test_native_ranges_and_anchors(self):self.assertEqual(len(self.r['methods']),73);self.assertEqual(len(self.r['native_anchors']),68)
    def test_static_numeric_all44(self):self.assertEqual(len(self.r['drone_numeric_fields']),44)
    def test_projectile_loops_all9(self):self.assertEqual(len(self.r['projectile_scheduler_proofs']),9)
    def test_abi25_not_one_plus(self):self.assertEqual(self.r['abi25']['value'],2.5)
    def test_base_damage_array(self):self.assertEqual(self.r['drone_base_damage']['values'],[450,600,6000,135,935,315,650,1200,248,650,1200,2650])
    def test_ctor_laser7(self):self.assertEqual(self.r['laser_defaults']['drone7_timeAttack'],f32(.2));self.assertEqual(self.r['laser_defaults']['drone7_timeCharge'],1)


class Wing(unittest.TestCase):
    table=[3,4,5,6,7,8,9,12,13,14]
    def test_lazy_once(self):
        p=PlayerLevel();calls=[]
        self.assertEqual(p.get(lambda:calls.append(1) or 4),4);self.assertEqual(p.get(lambda:9),4);self.assertEqual(calls,[1])
    def test_level_setter_unclamped(self):
        p=PlayerLevel();p.set(-8);self.assertEqual(p.get(lambda:1),-8)
    def test_sentinel_repeats_if_source_minus_one(self):
        p=PlayerLevel();calls=[]
        for _ in range(2):p.get(lambda:calls.append(1) or -1)
        self.assertEqual(len(calls),2)
    def test_start_tech_tiers(self):
        self.assertEqual([start_power_points(lambda:v,lambda _:0,[False]*4) for v in range(10)],[0,0,0,1,1,2,2,3,4,4])
    def test_use_item_consumed(self):
        a=[False]*3+[True];self.assertEqual(start_power_points(lambda:0,lambda _:0,a),3);self.assertFalse(a[3])
    def test_consume_before_cap_helper_exception(self):
        a=[False]*3+[True]
        def fail(_):raise RuntimeError()
        with self.assertRaises(RuntimeError):start_power_points(lambda:0,fail,a)
        self.assertFalse(a[3])
    def test_start_tech_reread(self):
        it=iter((8,0));self.assertEqual(start_power_points(lambda:next(it),lambda _:0,[False]*3+[True]),6)
    def test_cap_tiers(self):self.assertEqual([max_power_points(v,0,0) for v in range(8)],[6,7,8,8,9,9,10,10])
    def test_cap_ability13_double(self):self.assertEqual(max_power_points(0,0,1),8);self.assertEqual(max_power_points(0,5,5),10)
    def test_cap_no_lower_clamp(self):self.assertEqual(max_power_points(0,-9,0),-3)
    def test_numbers_level0to10(self):
        out=[]
        for lv in range(11):
            s=Wing1();configure_wing1(s,lambda:lv,lambda:False,self.table);out.append(s.number)
        self.assertEqual(out,[3,4,5,5,6,6,7,7,8,8,9])
    def test_four_getter_reads_normal(self):
        c=[];configure_wing1(Wing1(),lambda:c.append(1) or 10,lambda:False,self.table);self.assertEqual(len(c),4)
    def test_super_still_two_getters_and_count_reset(self):
        c=[];s=Wing1(rate=.06,speed=20,angle=33,count=7);configure_wing1(s,lambda:c.append(1) or 10,lambda:True,self.table)
        self.assertEqual((len(c),s.number,s.count,s.rate,s.speed,s.angle),(2,9,0,.06,20,33))
    def test_distinct_first_second_getter(self):
        it=iter((3,0));s=Wing1();configure_wing1(s,lambda:next(it),lambda:True,self.table);self.assertEqual(s.number,4)
    def test_normal_level10(self):
        s=Wing1();configure_wing1(s,lambda:10,lambda:False,self.table)
        self.assertEqual((s.number,s.angle,s.speed),(9,8,25));self.assertEqual(s.rate,f32(f32(.12)+f32(f32(10)*f32(-.0035))))
    def test_high_level_no_rate_floor(self):
        s=Wing1();configure_wing1(s,lambda:100,lambda:False,self.table);self.assertLess(s.rate,0);self.assertEqual((s.speed,s.angle,s.number),(42,15,14))
    def packet(self,s,number=3,t=1,super=False,attempt=None):
        calls=[];wing1_packet(s,number,now=lambda:t,is_super=lambda:super,attempt=attempt or calls.append);return calls
    def test_packet_normal_two_attempts(self):self.assertEqual(self.packet(Wing1(rate=.12)),[0,1])
    def test_packet_super_three_attempts(self):self.assertEqual(self.packet(Wing1(rate=.06),super=True),[0,1,2])
    def test_packet_spacing_divides_table_length10(self):
        s=Wing1(rate=f32(.12));self.packet(s,number=9)
        self.assertEqual(s.time_barrel,f32(1+f32(f32(f32(s.rate+f32(-.01))*f32(.3))/f32(10))))
    def test_main_deadline_equality_passes(self):self.assertEqual(self.packet(Wing1(rate=.12,time_shot=1)),[0,1])
    def test_future_barrel_gate(self):self.assertEqual(self.packet(Wing1(time_barrel=2)),[])
    def test_equal_number_not_greater(self):
        s=Wing1(rate=.12,count=3);self.packet(s,number=3);self.assertEqual(s.count,4);self.assertEqual(s.time_shot,0)
    def test_scheduler_writes_before_failed_emission(self):
        s=Wing1(rate=.12,count=2)
        def fail(_):raise RuntimeError()
        with self.assertRaises(RuntimeError):self.packet(s,attempt=fail)
        self.assertEqual(s.count,0);self.assertEqual(s.time_shot,f32(1+.12));self.assertGreater(s.time_barrel,1)


class Projectile(unittest.TestCase):
    def fire(self,s,t=1,barrels=(1,2),attempt=lambda _:None,charged=True):
        return projectile_drone_shoot(s,now=lambda:t,get_barrels=lambda:barrels,attempt=attempt,charged=charged)
    def test_no_ability_uses_base(self):self.assertEqual(drone_rate(.3,lambda _:0,lambda:(_ for _ in ()).throw(RuntimeError())),f32(.3))
    def test_first_point_divides_by2point5(self):self.assertEqual(drone_rate(1,lambda _:1,lambda:2.5),f32(.4))
    def test_points_are_reread(self):
        it=iter((1,2));self.assertEqual(drone_rate(1,lambda _:next(it),lambda:2.5),f32(.2))
    def test_ability_amount_before_second_points(self):
        c=[];drone_rate(1,lambda i:c.append(i) or 1,lambda:c.append('amount') or 2.5);self.assertEqual(c,[25,'amount',25])
    def test_single_drone_counts_no_charge(self):
        s=ProjectileDrone(shot_rate=.3,charge_deadline=99);self.assertTrue(self.fire(s,charged=False));self.assertEqual((s.count,s.charge_deadline),(0,99))
    def test_both_gate_equality(self):self.assertTrue(self.fire(ProjectileDrone(shot_deadline=1,charge_deadline=1)))
    def test_charge_future_blocks(self):self.assertFalse(self.fire(ProjectileDrone(charge_deadline=2)))
    def test_shot_future_blocks(self):self.assertFalse(self.fire(ProjectileDrone(shot_deadline=2)))
    def test_per_barrel_not_per_volley(self):
        s=ProjectileDrone(number=3);self.fire(s,barrels=(1,2));self.assertEqual(s.count,2)
    def test_no_midloop_charge_gate(self):
        s=ProjectileDrone(number=1,charge_rate=8);c=[];self.fire(s,barrels=(1,2,3),attempt=c.append);self.assertEqual(c,[0,1,2]);self.assertEqual(s.charge_deadline,9)
    def test_incomplete_new_mag_inside_same_loop(self):
        s=ProjectileDrone(number=2,charge_rate=8);self.fire(s,barrels=(1,2,3));self.assertEqual((s.count,s.charge_deadline),(1,9))
    def test_missing_component_attempt_still_counts(self):
        s=ProjectileDrone(number=2);self.fire(s,attempt=lambda _:None);self.assertEqual(s.count,0)
    def test_deadline_before_null_barrels(self):
        s=ProjectileDrone(shot_rate=.5)
        with self.assertRaises(ValueError):self.fire(s,barrels=None)
        self.assertEqual(s.shot_deadline,1.5)
    def test_empty_barrels_consume_deadline(self):
        s=ProjectileDrone(shot_rate=.5);self.fire(s,barrels=[]);self.assertEqual((s.shot_deadline,s.count),(1.5,0))
    def test_count_after_attempt_so_throw_not_increment(self):
        s=ProjectileDrone(shot_rate=.5)
        def fail(_):raise RuntimeError()
        with self.assertRaises(RuntimeError):self.fire(s,attempt=fail)
        self.assertEqual((s.count,s.shot_deadline),(0,1.5))
    def test_length_snapshotted(self):
        b=[1];s=ProjectileDrone(number=9);c=[];self.fire(s,barrels=b,attempt=lambda i:(c.append(i),b.append(2)));self.assertEqual(c,[0])
    def test_base_poll_strict_gt(self):
        c=[];s={'time_to_check':1};drone_base_fixed(s,is_attack=lambda:True,now=lambda:1,find=lambda:c.append(1));self.assertEqual(c,[])
    def test_base_poll_write_before_find(self):
        c=[];s={'time_to_check':0};drone_base_fixed(s,is_attack=lambda:True,now=lambda:1,find=lambda:c.append(s['time_to_check']));self.assertEqual(c,[1.5])
    def test_base_stopped_no_poll(self):
        s={'time_to_check':0};drone_base_fixed(s,is_attack=lambda:False,now=lambda:1,find=lambda:(_ for _ in ()).throw(RuntimeError()));self.assertEqual(s['time_to_check'],0)


class Laser(unittest.TestCase):
    def tick(self,s,f,t=1,**kw):return laser_drone_tick(s,f,now=lambda:t,attack=kw.pop('attack',lambda:None),**kw)
    def test_activation_no_attack(self):
        for f in (7,9):
            c=[];s=LaserDrone(time_attack=.2);self.assertEqual(self.tick(s,f,attack=lambda:c.append(1)),'activated');self.assertEqual(c,[])
    def test_inactive_equality_no_activation(self):
        for f in (7,9):self.assertEqual(self.tick(LaserDrone(time_to_active=1),f),'idle')
    def test_active_equality_attacks(self):
        for f in (7,9):self.assertEqual(self.tick(LaserDrone(actived=True,time_to_deactive=1),f),'attack')
    def test7_expired_still_calls_attack_with_active_false(self):
        c=[];s=LaserDrone(actived=True,time_charge=1);self.tick(s,7,attack=lambda:c.append(s.actived));self.assertEqual(c,[False]);self.assertEqual(s.time_to_active,2)
    def test9_expired_no_attack(self):
        c=[];s=LaserDrone(actived=True,time_charge=1);self.assertEqual(self.tick(s,9,attack=lambda:c.append('bad'),deactivate=lambda:c.append('hide')),'deactivated');self.assertEqual(c,['hide'])
    def test9_inactive_fades(self):
        c=[];self.tick(LaserDrone(time_to_active=1),9,fade=lambda:c.append(1));self.assertEqual(c,[1])
    def test7_inactive_not_fade(self):
        c=[];self.tick(LaserDrone(time_to_active=1),7,fade=lambda:c.append(1));self.assertEqual(c,[])
    def test_stop_does_not_clear_active_timer(self):
        s=LaserDrone(actived=True,time_to_deactive=.5);self.assertEqual(self.tick(s,9,is_attack=lambda:False),'stopped');self.assertTrue(s.actived);self.assertEqual(s.time_to_deactive,.5)


class Sweep(unittest.TestCase):
    def tick(self,s,t=1,delta=1,fx=lambda _:None,rotation=lambda _:None):return sweep_drone_tick(s,now=lambda:t,delta=lambda:delta,set_rotation=rotation,set_fx=fx)
    def test_start_no_rotate_or_fx(self):
        c=[];s=SweepDrone(target_angle=9);self.assertEqual(self.tick(s,fx=c.append,rotation=c.append),'started');self.assertEqual(c,[]);self.assertEqual(s.target_angle,9)
    def test_four_arrivals_targets(self):
        s=SweepDrone(shooting=True);c=[];out=[]
        for _ in range(4):self.tick(s,delta=20,fx=c.append);out.append(s.target_angle)
        self.assertEqual(out,[-16,16,0,0]);self.assertEqual(c,[True,False]);self.assertFalse(s.shooting);self.assertEqual(s.count,1)
    def test_speed_twenty_degrees(self):
        s=SweepDrone(shooting=True,target_angle=90);self.tick(s,delta=.1);self.assertEqual(s.rotation,2);self.assertEqual(s.phase,0)
    def test_deadline_only_at_finish(self):
        s=SweepDrone(shooting=True);self.tick(s);self.assertEqual(s.shot_deadline,0)
    def test_finish_deadline3(self):
        s=SweepDrone(shooting=True,phase=3);self.tick(s);self.assertEqual(s.shot_deadline,4)
    def test_number3_resets_and_charge0(self):
        s=SweepDrone(shooting=True,phase=3,count=2);self.tick(s);self.assertEqual((s.count,s.turn_deadline),(0,1))
    def test_gate_equality_starts(self):self.assertEqual(self.tick(SweepDrone(shot_deadline=1,turn_deadline=1)),'started')
    def test_gate_future_waits(self):self.assertEqual(self.tick(SweepDrone(shot_deadline=2)),'wait')
    def test_wrapped_angle_can_arrive_equivalent_not_exact(self):self.assertEqual(move_towards_angle(359,1,1),360)
    def test_small_delta_uses_exact_target(self):self.assertEqual(move_towards_angle(359,1,3),1)
    def test_callback_mutates_phase_before_target_choice(self):
        s=SweepDrone(shooting=True)
        self.tick(s,fx=lambda _ :setattr(s,'phase',1));self.assertEqual((s.phase,s.target_angle),(2,16))


class Legacy(unittest.TestCase):
    def auto(self,s,children=(10,20),shoot=None,audio=lambda _:None,mag_end=None,t=1):
        c=[];legacy_auto(s,now=lambda:t,child_count=lambda:len(children),get_child=lambda i:children[i],parent=99,shoot=shoot or c.append,audio=audio,mag_end=mag_end);return c
    def test_sync_does_not_clear_start_or_stun(self):
        s=LegacyDroidGun(time_to_start=8,is_stunned=True,count_of_mags=3,count_of_blts=2,time_to_rounds=5);legacy_start_sync(s,True)
        self.assertEqual((s.time_to_start,s.is_stunned,s.count_of_mags,s.count_of_blts,s.time_to_rounds,s.infinity_rounds),(8,True,0,0,0,True))
    def test_mag_start_before_shot_gate(self):
        c=[];s=LegacyDroidGun(time_shot=.2,time_to_shot=4,mag_start=lambda:c.append('start'));self.assertEqual(self.auto(s),[]);self.assertEqual(c,['start'])
    def test_positive_count_shots_reuses_child0(self):
        s=LegacyDroidGun(time_shot=.2,count_shots=2);self.assertEqual(self.auto(s),[10]);self.assertEqual(self.auto(s,t=2),[10])
    def test_zero_count_advances_children(self):
        s=LegacyDroidGun(time_shot=.2);self.assertEqual(self.auto(s),[10]);self.assertEqual(self.auto(s,t=2),[20]);self.assertEqual(s.count_of_blts,0)
    def test_zero_time_positive_count_all_child0(self):self.assertEqual(self.auto(LegacyDroidGun(count_shots=3)),[10,10,10])
    def test_zero_time_zero_count_all_children(self):self.assertEqual(self.auto(LegacyDroidGun()),[10,20])
    def test_zero_time_no_children_parent(self):self.assertEqual(self.auto(LegacyDroidGun(),children=[]),[99])
    def test_audio_once_for_simultaneous(self):
        c=[];self.auto(LegacyDroidGun(count_shots=3,audio_clip=7),audio=c.append);self.assertEqual(c,[7])
    def test_mag_end_reload_before_callback(self):
        c=[];s=LegacyDroidGun(time_reload=.5);s.mag_ended=lambda:c.append(s.time_to_reload);legacy_mag_end(s,lambda:1);self.assertEqual(c,[1.5])
    def test_round_callback_suppressed_but_deadline_infinite(self):
        c=[];s=LegacyDroidGun(count_mags=1,infinity_rounds=True,round_ended=lambda:c.append(1));legacy_mag_end(s,lambda:1);self.assertEqual(c,[]);self.assertEqual((s.count_of_mags,s.time_to_rounds),(0,4))
    def test_mag_callback_live_count_change(self):
        s=LegacyDroidGun(count_mags=1);s.mag_ended=lambda:setattr(s,'count_mags',3);legacy_mag_end(s,lambda:1);self.assertEqual((s.count_of_mags,s.time_to_rounds),(1,0))
    def test_stun_not_scheduler_gate(self):
        c=[];legacy_fixed(LegacyDroidGun(is_stunned=True),now=lambda:1,can_attack=lambda:True,run_auto=lambda:c.append(1));self.assertEqual(c,[1])
    def test_round_gate_only_if_positive(self):
        c=[];s=LegacyDroidGun(time_rounds=0,time_to_rounds=99);legacy_fixed(s,now=lambda:1,can_attack=lambda:True,run_auto=lambda:c.append(1));self.assertEqual(c,[1])


class Damage(unittest.TestCase):
    def damage(self,source=20001,rank=1,level=0,ability=0,get_rank=lambda _:1,get_level=None,values=None):return drone_base_damage(source,rank,get_rank=get_rank,get_level=get_level or (lambda _:level),base_values=values or [450,600,6000,135,935,315,650,1200,248,650,1200,2650],get_ability=lambda _:ability,ability_amount=lambda:2.5)
    def test_rank1_no_rank_bonus(self):self.assertEqual(self.damage(),450)
    def test_level_rate_point16_not_point01(self):self.assertEqual(self.damage(level=1),f32(f32(f32(1)+f32(.16))*450))
    def test_source_array_offset(self):self.assertEqual(self.damage(source=20003),6000)
    def test_low_source_bounds(self):
        with self.assertRaises(IndexError):self.damage(source=20000)
    def test_high_source_bounds(self):
        with self.assertRaises(IndexError):self.damage(source=20013)
    def test_default_rank_helper(self):self.assertEqual(self.damage(rank=-1,get_rank=lambda _:2),self.damage(rank=2))
    def test_explicit_rank_skips_getter(self):self.assertEqual(self.damage(get_rank=lambda _:(_ for _ in ()).throw(RuntimeError())),450)
    def test_rank_table_and_fallback(self):
        for rank,bonus in ((1,0),(2,.2),(3,.35),(4,.5),(5,.56),(0,.56)):
            self.assertEqual(self.damage(rank=rank),f32(450*f32(f32(1)+f32(bonus))))
    def test_ability21_additive2point5(self):self.assertEqual(self.damage(ability=1),1575)
    def test_rank_before_level_before_array(self):
        c=[]
        with self.assertRaises(IndexError):self.damage(rank=-1,source=20000,get_rank=lambda i:c.append(('rank',i)) or 1,get_level=lambda i:c.append(('level',i)) or 0)
        self.assertEqual(c,[('rank',20000),('level',20000)])


if __name__=='__main__':unittest.main()
