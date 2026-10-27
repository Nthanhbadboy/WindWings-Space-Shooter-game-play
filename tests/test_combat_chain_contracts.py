import gzip
import json
from pathlib import Path
import unittest
from tools.verify.combat_chain_contracts import build

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'reverse-engineering/raw/combat-chain'


class CombatChainContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build()

    def test_regeneration(self):
        stored = json.loads(gzip.decompress((ROOT/'datas/combat_chain_contract.json.gz').read_bytes()))
        self.assertEqual(stored, self.data)

    def test_full_attack_family_inventory_not_only_ship_one(self):
        self.assertEqual([r['implementation'] for r in self.data['ships']],
                         [f'Player_Attack_{n}' for n in range(1,25)])
        self.assertGreaterEqual(self.data['counts']['methods'],1500)
        self.assertEqual(self.data['counts']['capped'],0)
        # The 38 unclean and minimum-span overlaps are limitations, not erased exceptions.
        self.assertGreater(self.data['counts']['unclean'],0)
        self.assertGreater(self.data['counts']['clipped'],0)

    def test_source_ids_not_inferred_from_implementation_suffix(self):
        ships = self.data['ships']
        self.assertEqual({r['id'] for r in ships[0]['source_components']},{10003})
        self.assertEqual({r['id'] for r in ships[2]['source_components']},{10001})
        self.assertEqual({r['id'] for r in ships[1]['prefix_only_components']},{10002})
        self.assertEqual(len(ships[1]['prefix_only_components']),4)
        self.assertFalse(ships[1]['source_components'])  # no invented full typetrees
        self.assertEqual(self.data['prefix_validation_count'],101)

    def test_native_rate_index_candidates_all_twenty_four(self):
        for n, ship in enumerate(self.data['ships']):
            self.assertEqual(len(ship['main_rate_consumers']),1)
            call = ship['main_rate_consumers'][0]['call']
            self.assertEqual(call['last_straightline_w0_constant_candidate']['value'],n)

    def test_got_relative_usage_resolves_delegate_and_interfaces(self):
        rows = {r['got']:r['symbol'] for r in self.data['resolved_got']}
        self.assertIn('Player_Attack_1.OnBulletMainCannonCollided()', rows['0x2ae7c28']['Name'])
        self.assertEqual(rows['0x2ae7c28']['MethodAddress'],0x147c1ac)
        self.assertIn('Player_Attack_1.OnBulletMainCannonDestroyed()', rows['0x2ae7c30']['Name'])
        self.assertEqual(rows['0x2adcb88']['Name'],'IDamageable_TypeInfo')
        self.assertIn('GetComponent<IBullet>()',rows['0x2adcbe8']['Name'])
        self.assertEqual(rows['0x2adcbf0']['Name'],'SpaceShooter.IBullet_TypeInfo')
        self.assertIn('GetComponent<Obj_Collider>()',rows['0x2adcaa8']['Name'])

    def test_receiver_chain_direct_calls(self):
        records = self.data['methods']
        def contains(cls, method, target):
            return any(c['target']==target for r in records if r['class_name']==cls and r['method']==method
                       for c in r['direct_calls'])
        self.assertTrue(contains('Enemy_Sub','TakeDamage','0x1582938'))
        self.assertTrue(contains('Enemy_Controller','OnTakeDamage','0x158479c'))
        self.assertTrue(contains('Sub_Player','TakeDamage','0x14c6de4'))

    def test_bullet_callback_store_and_invoke(self):
        base = (RAW/'native/Bullet_Object.asm.txt').read_text()
        linear = (RAW/'native/Bullet_Linearly.asm.txt').read_text()
        self.assertRegex(base,r'0x158c108: stp\s+x4, x5, \[x0, #0x40\]')
        self.assertRegex(linear,r'0x1591ffc: ldr\s+x21, \[x19, #0x40\]')
        self.assertRegex(linear,r'0x159203c: blr\s+x8')
        self.assertRegex(linear,r'0x1592048: str\s+xzr, \[x19, #0x40\]')

    def test_armor_and_post_callback_order_anchors(self):
        asm=(RAW/'native/Enemy_Health.asm.txt').read_text()
        for pattern in [r'0x15847e8: fsub\s+s1, s2, s1',r'0x15847f4: fdiv\s+s1, s2, s1',
                        r'0x1584808: str\s+s0, \[x19\]',r'0x1584820: blr\s+x9',
                        r'0x158482c: ldr\s+s0, \[x19\]']:
            self.assertRegex(asm,pattern)

    def test_decoder_exit_is_not_hidden(self):
        evidence=json.loads(gzip.decompress((RAW/'symbols.json.gz').read_bytes()))
        self.assertIn('Press any key to exit',evidence['dumper_log_tail'])
        self.assertNotEqual(evidence['dumper_exit_code'],0)

    def test_pool_prefabs_are_plasma_and_homing_not_assumed_base(self):
        candidates = self.data['pool_bindings']
        for pool_id, expected in [(80003,'Bullet_Plasma'),(88004,'Homing_Missile')]:
            rows=[r for r in candidates if r['pool_entry'].get('tree',{}).get('id')==pool_id]
            self.assertEqual({r['class_name'] for r in rows},{expected})
            self.assertTrue(all(r['pointer']['m_FileID']==0 for r in rows))
        plasma=(RAW/'native/Bullet_Plasma.asm.txt').read_text()
        self.assertRegex(plasma,r'0x158d28c: bl\s+#0x158e0c0')
        self.assertRegex(plasma,r'0x158d300: br\s+x3')

    def test_collider_root_and_lazy_interface_cache(self):
        self.assertEqual(len(self.data['collider_roots']),1623)
        self.assertTrue(any(c['class_name']=='Enemy_Sub' for r in self.data['collider_roots']
                            for c in r['receiver_candidates']))
        lookup = next(r for r in self.data['resolved_got'] if r['got']=='0x2adcac0')
        self.assertIn('Component.GetComponent<IDamageable>()',lookup['symbol']['Name'])
        asm=(RAW/'native/Obj_Collider.asm.txt').read_text()
        self.assertRegex(asm,r'0x123b8a8: strb\s+w9, \[x19, #0x5c\]')
        self.assertRegex(asm,r'0x123b8f0: str\s+x0, \[x19, #0x28\]')

    def test_delegate_constructor_uses_supplied_target_and_method(self):
        helper=json.loads((RAW/'delegate-constructor.json').read_text())
        import hashlib
        self.assertEqual(hashlib.sha256(bytes.fromhex(helper['hex'])).hexdigest(),helper['sha256'])
        operations={r['address']:(r['mnemonic'],r['operands']) for r in helper['asm']}
        self.assertEqual(operations['0x19a9444'],('stp','x1, x2, [x0, #0x20]'))
        self.assertEqual(operations['0x19a9450'],('str','x8, [x0, #0x10]'))
