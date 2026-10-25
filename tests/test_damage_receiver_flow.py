import json
import unittest
from tools.verify.damage_receiver_flow import OUT,build


class DamageNativeAnchors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.audit=build()

    def test_exact_regeneration_and_source_counts(self):
        self.assertEqual(self.audit,json.loads(OUT.read_text()))
        self.assertEqual(len(self.audit['methods']),44)
        self.assertGreater(sum(m['instruction_count'] for m in self.audit['methods']),3400)

    def test_mb_all_four_state_targets_are_exact_byte_table_not_textual_guess(self):
        self.assertEqual(self.audit['mb_death_state_targets'],
            {'0':'0x1574b8c','1':'0x1574bdc','2':'0x1574c28','3':'0x1574c74'})

    def test_receiver_ability_arguments_proved_on_cfg(self):
        rows={m['class']+'.'+m['method']:m for m in self.audit['methods']}
        self.assertEqual({c['ability_id'] for c in rows['Player_Health.TakeDamage']['ability_calls']},
                         {8,9,10,16,22,28,30,35})
        self.assertEqual({c['ability_id'] for c in rows['Enemy_Controller.OnTakeDamage']['ability_calls']},{31,34})
        self.assertEqual({c['ability_id'] for c in rows['Enemy_Destroy.Destroyed']['ability_calls']},{32})

    def test_exact_threshold_and_burn_literals(self):
        cells={c['va']:c for c in self.audit['literal_cells']}
        self.assertEqual(cells['0x7570e0']['hex'],'9a99993e')
        self.assertEqual(cells['0x756fbc']['hex'],'cdcccc3e')

    def test_named_events_not_assumed_numbers(self):
        self.assertEqual(self.audit['event_names'],{'18':'OnPlayerDie','19':'OnEnemyDie','21':'OnPlayerUpdateHp',
            '39':'OnPlayerTakeDamage','79':'OnPoolEnemy','86':'OnExtraLife'})

    def test_field_identity_for_reductions_and_chances(self):
        f=self.audit['ability_coefficient_fields']
        self.assertEqual(f['0x31c']['name'],'abi9ReduceREDDmg')
        self.assertEqual(f['0x364']['name'],'abi32Rate')
