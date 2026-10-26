import unittest
from tools.verify.enemy_damage_model import calculate


class EnemyDamageModelTests(unittest.TestCase):
    def test_positive_armor(self):
        self.assertEqual(calculate(100, 40, 100)['hp'], 80)

    def test_negative_armor_not_same_formula(self):
        self.assertEqual(calculate(100, 40, -100)['hp'], 40)

    def test_overkill_loss_is_clipped(self):
        result = calculate(10, 100, 0)
        self.assertEqual(result['hp'], 0)
        self.assertEqual(result['pre_callback_loss'], 10)

    def test_no_damage_and_ignore(self):
        self.assertFalse(calculate(100, 20, 0, True)['accepted'])
        self.assertEqual(calculate(100, 20, 0, True, True)['hp'], 80)

    def test_dead_ignored_even_if_ignore(self):
        self.assertFalse(calculate(0, 100, 0, False, True)['accepted'])

    def test_zero_damage_still_accepted_before_hit_callback(self):
        result = calculate(100, 0, 0)
        self.assertTrue(result['accepted'])
        self.assertEqual(result['pre_callback_loss'], 0)

    def test_negative_damage_not_native_clamped_to_zero(self):
        self.assertEqual(calculate(100, -20, 0)['hp'], 120)

    def test_nonfinite_not_in_model(self):
        with self.assertRaises(ValueError):
            calculate(1, float('nan'), 0)
