import json,unittest
from tools.verify.pickup_currency_flow import build,OUT
from tools.verify.pickup_currency_models import *

class CurrencyFormulaTests(unittest.TestCase):
    def pair(self,stage,coins,tech=0,device=0):return tuple(currency_delta(k,stage,tech,coins,device)['delta'] for k in (1,2))
    def test_stage1_low_band(self):self.assertEqual(self.pair(1,0),(3,12))
    def test_stage40_41_gate(self):
        self.assertEqual(self.pair(40,0),(8,23));self.assertEqual(self.pair(41,0),(10,27))
    def test_stage_group_boundary(self):
        self.assertEqual(self.pair(9,0),(3,12));self.assertEqual(self.pair(10,0),(4,15))
    def test_caps_are_separate(self):
        self.assertEqual(self.pair(90,0),(17,35));self.assertEqual(self.pair(100,0),(18,35));self.assertEqual(self.pair(1000,0),(18,35))
    def test_all_threshold_equalities_and_successors(self):
        expected={2500:(10,27),2501:(5,13),3300:(5,13),3301:(3,6),4300:(3,6),4301:(2,4),5500:(2,4),5501:(1,2)}
        for coins,pair in expected.items():
            with self.subTest(coins=coins):self.assertEqual(self.pair(41,coins),pair)
    def test_fcmp_operand_direction(self):
        self.assertEqual(currency_delta(1,41,0,0)['band'],'atMost2500')
        self.assertEqual(currency_delta(1,41,0,6000)['band'],'above5500')
    def test_small_coin_can_add_zero(self):
        self.assertEqual(self.pair(1,4301),(0,2));self.assertEqual(self.pair(1,5501),(0,1))
    def test_tech14_no_bonus(self):self.assertEqual(self.pair(41,3000,14),(5,13))
    def test_tech15_float_factor(self):
        d=currency_delta(1,41,15,3301);self.assertEqual(d['lab_factor'],f32(f32(1/3)+1));self.assertEqual(d['delta'],10)
    def test_tech17_doubles_thresholds(self):
        for v,pair in [(5000,(10,27)),(5001,(5,13)),(6600,(5,13)),(6601,(3,6)),(8600,(3,6)),(8601,(2,4)),(11000,(2,4)),(11001,(1,2))]:
            with self.subTest(coins=v):self.assertEqual(self.pair(41,v,17),pair)
    def test_device_factor_before_final_truncation(self):
        self.assertEqual(self.pair(1,0,0,.25),(4,16));self.assertEqual(self.pair(41,0,0,.25),(12,33))
    def test_86_cell_exact(self):self.assertEqual(currency_delta(1,1,0,0)['untruncated'],f32(f32(4)*f32(.86)))
    def test_invalid_fixture_kind(self):
        with self.assertRaises(ValueError):currency_delta(5,1,0,0)
    def test_nonfinite_and_outside_conversion_domain(self):
        for args in [(1,1,0,0,float('nan')),(1,2**31-1,0,0,0),(1,1,-2**31,0,0)]:
            with self.subTest(args=args),self.assertRaises(ValueError):currency_delta(*args)

class CurrencyStateTests(unittest.TestCase):
    def test_write_before_post_and_getter_order(self):
        s=Currency();seen=[]
        def stage():seen.append('stage');return 1
        def tech():seen.append('tech');return 0
        collect_coin(1,s,get_stage=stage,get_tech=tech,post=lambda event,payload:seen.append((event,payload,s.coin_count)))
        self.assertEqual(seen,['stage','tech',(48,None,3)])
    def test_post_failure_keeps_coin_write(self):
        s=Currency()
        with self.assertRaises(RuntimeError):collect_coin(1,s,get_stage=lambda:1,get_tech=lambda:0,post=lambda *_:(_ for _ in ()).throw(RuntimeError()))
        self.assertEqual(s.coin_count,3)
    def test_stage_failure_no_write(self):
        s=Currency(40)
        with self.assertRaises(RuntimeError):collect_coin(1,s,get_stage=lambda:(_ for _ in ()).throw(RuntimeError()),get_tech=lambda:0,post=lambda *_:None)
        self.assertEqual(s.coin_count,40)
    def test_native_add_wrap(self):
        s=Currency(2**31-1)
        collect_coin(1,s,get_stage=lambda:41,get_tech=lambda:0,post=lambda *_:None)
        self.assertEqual(s.coin_count,-2**31)
    def test_synchronous_reentry_sees_stored_balance(self):
        s=Currency(2500);calls=[]
        def post(*_):
            calls.append(s.coin_count)
            if len(calls)==1:collect_coin(2,s,get_stage=lambda:41,get_tech=lambda:0,post=post)
        collect_coin(1,s,get_stage=lambda:41,get_tech=lambda:0,post=post)
        self.assertEqual(calls,[2510,2523]);self.assertEqual(s.coin_count,2523)
    def test_burst28_is_not_denomination28(self):
        for stage,total in [(1,69),(41,165)]:
            s=Currency()
            for k in [1]*3+[2]*5:collect_coin(k,s,get_stage=lambda:stage,get_tech=lambda:0,post=lambda *_:None)
            self.assertEqual(s.coin_count,total)
    def test_pickup_order_can_change_sum(self):
        results=[]
        for order in ([1]*3+[2]*5,[2]*5+[1]*3):
            s=Currency(2490)
            for k in order:collect_coin(k,s,get_stage=lambda:41,get_tech=lambda:0,post=lambda *_:None)
            results.append(s.coin_count-2490)
        self.assertEqual(results,[90,94])
    def test_zero_delta_still_posts(self):
        s=Currency(5501);seen=[]
        collect_coin(1,s,get_stage=lambda:1,get_tech=lambda:0,post=lambda *a:seen.append(a))
        self.assertEqual(s.coin_count,5501);self.assertEqual(seen,[(48,None)])

class PickupDispatchTests(unittest.TestCase):
    def item(self,item,seen,callbacks):
        return coin_item_collected(item,get_index=lambda x:x,get_callback=callbacks.get,play_sound=lambda:seen.append('sound'))
    def test_aliases_and_callback_sound_order(self):
        for id,kind in COIN_KIND.items():
            seen=[];self.item(id,seen,{kind:lambda x:seen.append(x)})
            self.assertEqual(seen,[id,'sound'])
    def test_missing_callback_still_sound(self):
        seen=[];self.item(70001,seen,{});self.assertEqual(seen,['sound'])
    def test_direct_assignment_not_combine(self):
        cb={1:'old',2:'old'};bind_coin_callbacks(cb,'new1','new2');self.assertEqual(cb,{1:'new1',2:'new2'})
    def test_callback_exception_skips_sound(self):
        seen=[]
        with self.assertRaises(RuntimeError):self.item(70001,seen,{1:lambda x:(_ for _ in ()).throw(RuntimeError())})
        self.assertEqual(seen,[])
    def test_items_ignore_enemy_damage_gates(self):
        for active,invisible in [(False,True),(False,False),(True,True),(True,False)]:
            seen=[];trigger_enter(lambda:'coin','Item',active_hit_enemy=active,invisible=invisible,item_collected=lambda x:seen.append('collect'),pool=lambda x:seen.append('pool'),non_item=lambda:seen.append('hit'))
            self.assertEqual(seen,['collect','pool'])
    def test_trigger_rereads_object_after_callback(self):
        target=['first'];seen=[]
        def collected(x):seen.append(x);target[0]='second'
        trigger_enter(lambda:target[0],'Item',active_hit_enemy=False,invisible=True,item_collected=collected,pool=seen.append)
        self.assertEqual(seen,['first','second'])
    def test_event_receiver_never_pools(self):
        seen=[];on_collect_event('coin',is_exact_gameobject=lambda x:True,get_tag=lambda x:'Item',item_collected=seen.append)
        self.assertEqual(seen,['coin'])
    def test_event_receiver_tag_and_type(self):
        seen=[];on_collect_event('coin',is_exact_gameobject=lambda x:True,get_tag=lambda x:'Player',item_collected=seen.append)
        self.assertEqual(seen,[])
        with self.assertRaises(ValueError):on_collect_event(None,is_exact_gameobject=lambda x:False,get_tag=lambda x:'Item',item_collected=seen.append)
    def test_repeated_explicit_calls_not_artificially_deduplicated(self):
        seen=[]
        for _ in range(2):self.item(70011,seen,{1:lambda x:seen.append('callback')})
        self.assertEqual(seen,['callback','sound','callback','sound'])
    def test_exception_stops_pool(self):
        seen=[]
        with self.assertRaises(RuntimeError):trigger_enter(lambda:70001,'Item',active_hit_enemy=True,invisible=False,item_collected=lambda x:(_ for _ in ()).throw(RuntimeError()),pool=seen.append)
        self.assertEqual(seen,[])

class DeviceAndSourceTests(unittest.TestCase):
    def test_device_reset_skip_filter_and_duplicates(self):
        s=Currency(device_percent=9);resolved=[];stats=[]
        devices={1:dict(id=4999),2:dict(id=5000),3:dict(id=5999),4:dict(id=6000)}
        def get(i):resolved.append(i);return devices[i]
        def stat(d):stats.append(d['id']);return 10
        apply_device_coin_bonus(s,0,get_devices=lambda _: [-1,1,2,3,4,2],get_device=get,get_stat_value2=stat)
        self.assertEqual(resolved,[1,2,3,4,2]);self.assertEqual(stats,[5000,5999,5000]);self.assertEqual(s.device_percent,f32(f32(.2)+f32(.1)))
    def test_device_failure_before_vs_after_reset(self):
        s=Currency(device_percent=.5)
        with self.assertRaises(RuntimeError):apply_device_coin_bonus(s,0,get_devices=lambda _:(_ for _ in ()).throw(RuntimeError()),get_device=lambda _:None,get_stat_value2=lambda _:0)
        self.assertEqual(s.device_percent,.5)
        with self.assertRaises(ValueError):apply_device_coin_bonus(s,0,get_devices=lambda _:None,get_device=lambda _:None,get_stat_value2=lambda _:0)
        self.assertEqual(s.device_percent,0)
    def test_stat_value2_zero_short_circuit(self):
        self.assertEqual(stat_value2(dict(id=5001,rank=0,lv=99),{9:[0]},[]),0)
    def test_stat_value2_formula_with_explicit_synthetic_tables(self):
        self.assertEqual(stat_value2(dict(id=5001,rank=1,lv=4),{9:[0,12]},[0,0,0,0,2]),22)
    def test_stat_value2_bounds(self):
        for rank in [-1,2]:
            with self.assertRaises(IndexError):stat_value2(dict(id=5001,rank=rank,lv=4),{9:[0,12]},[0]*5)
    def test_stage_getter_test_override_and_branch(self):
        self.assertEqual(stage_index('Test',True,99,True,7,1),99)
        self.assertEqual(stage_index('Other',True,99,True,7,1),7)
        self.assertEqual(stage_index('Test',False,99,False,7,1),1)
    def test_tech_mode4_scene_game_zero(self):
        seen=[]
        def saved():seen.append(1);return 17
        self.assertEqual(tech_lab_level(4,'Game',saved),0);self.assertEqual(seen,[])
        self.assertEqual(tech_lab_level(3,'Game',saved),17);self.assertEqual(tech_lab_level(4,'Other',saved),17)

class DroidSuffixTests(unittest.TestCase):
    def call(self,distance,force,reset=False):
        seen=[];target=['first']
        def post(e,p):seen.append(('post',e,p));target[0]='second'
        result=droid_pickup_suffix(distance,force,collect_to=lambda:seen.append('force'),get_gameobject=lambda:target[0],post=post,pool=lambda x:seen.append(('pool',x)),reset_target=lambda:seen.append('reset') if reset else None)
        return result,seen
    def test_unforced_near_item_is_forced_first(self):self.assertEqual(self.call(.1,False),('force-to-player',['force']))
    def test_forced_close_post_pool_reset_order(self):self.assertEqual(self.call(.49,True,True),('collected',[('post',2,'first'),('pool','second'),'reset']))
    def test_strict_half_radius(self):self.assertEqual(self.call(.5,True),('move-or-continue',[]))
    def test_strict_five_radius(self):self.assertEqual(self.call(5,False),('move-or-continue',[]))
    def test_event_exception_skips_pool_reset(self):
        seen=[]
        with self.assertRaises(RuntimeError):droid_pickup_suffix(.1,True,collect_to=lambda:None,get_gameobject=lambda:1,post=lambda *_:(_ for _ in ()).throw(RuntimeError()),pool=seen.append,reset_target=lambda:seen.append('reset'))
        self.assertEqual(seen,[])

class EndToEndCoinFixtureTests(unittest.TestCase):
    def pipeline(self,coin_id,initial=0):
        state=Currency(initial);seen=[];callbacks={}
        def controller(kind):
            return lambda _:collect_coin(kind,state,get_stage=lambda:1,get_tech=lambda:0,post=lambda e,p:seen.append(('event',e,state.coin_count)))
        bind_coin_callbacks(callbacks,controller(1),controller(2))
        item=dict(id=coin_id,tag='Item')
        def collected(payload):coin_item_collected(payload,get_index=lambda x:x['id'],get_callback=callbacks.get,play_sound=lambda:seen.append('sound-helper'))
        def post(e,p):
            seen.append(('post',e))
            on_collect_event(p,is_exact_gameobject=lambda x:x is item,get_tag=lambda x:x['tag'],item_collected=collected)
        droid_pickup_suffix(.1,True,collect_to=lambda:None,get_gameobject=lambda:item,post=post,pool=lambda x:seen.append('pool'),reset_target=lambda:seen.append('reset-target'))
        return state.coin_count,seen
    def test_droid_to_receiver_to_currency_to_pool(self):
        self.assertEqual(self.pipeline(70012),(12,[('post',2),('event',48,12),'sound-helper','pool','reset-target']))
    def test_zero_small_delta_does_not_cancel_outer_chain(self):
        self.assertEqual(self.pipeline(70011,5501),(5501,[('post',2),('event',48,5501),'sound-helper','pool','reset-target']))

class PickupContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=build()
    def test_generated_contract_matches(self):self.assertEqual(self.data,json.loads(OUT.read_text()))
    def test_scope_and_evidence_counts(self):
        self.assertEqual(len(self.data['methods']),20);self.assertEqual(len(self.data['dispatch']),13);self.assertEqual(len(self.data['bindings']),4)
    def test_dispatch_exact_alias_targets(self):
        table={r['id']:r for r in self.data['dispatch']}
        self.assertEqual(table[70001]['target'],table[70011]['target']);self.assertEqual(table[70002]['target'],table[70012]['target'])
    def test_source_literals_not_assumed(self):self.assertEqual([x['text'] for x in self.data['literals']],['Item','Test','Game'])

if __name__=='__main__':unittest.main()
