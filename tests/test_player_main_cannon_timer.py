import unittest
from pathlib import Path
from tools.verify.player_main_cannon_timer import Timer, step, f32

ROOT = Path(__file__).resolve().parents[1]


class MainCannonTimerTests(unittest.TestCase):
    def test_deadline_equality_is_eligible(self):
        self.assertFalse(step(Timer(1), .5, 4, .25, 0)[1])
        self.assertEqual(step(Timer(1), 1, 4, .25, 0), (Timer(5), True))

    def test_two_extra_means_three_emitter_entries(self):
        state = Timer()
        for now, expected in [(0, Timer(0, .25, 1)), (.25, Timer(0, .5, 2)),
                              (.5, Timer(4.5, .75, 0))]:
            state, entered = step(state, now, 4, .25, 2)
            self.assertTrue(entered)
            self.assertEqual(state, expected)
        self.assertFalse(step(state, 1, 4, .25, 2)[1])

    def test_both_gates_required(self):
        self.assertFalse(step(Timer(0, 2, 1), 1, 4, .25, 2)[1])
        self.assertFalse(step(Timer(2, 0, 1), 1, 4, .25, 2)[1])

    def test_no_catchup_loop(self):
        self.assertEqual(step(Timer(1), 100, 4, .25, 0), (Timer(104), True))

    def test_zero_delay_still_one_entry_per_invocation(self):
        self.assertEqual(step(Timer(), 0, 0, 0, 2), (Timer(0, 0, 1), True))

    def test_f32_and_model_domain(self):
        state, _ = step(Timer(), 1, .2, .2, 0)
        self.assertEqual(state.deadline, f32(1 + f32(.2)))
        for now in [float('nan'), float('inf'), -1]:
            with self.assertRaises(ValueError):
                step(Timer(), now, 1, .2, 0)

    def test_native_branch_and_callback_anchors(self):
        text = (ROOT / 'reverse-engineering/raw/player-firing/native/Player_Attack_1.asm.txt').read_text()
        for pattern in [
            r'0x147a978: b.le\s+#0x147a994',
            r'0x147a980: str\s+wzr, \[x19, #0x120\]',
            r'0x147a970: str\s+s0, \[x19, #0x118\]',
            r'0x147acec: b\s+#0x147b608',
            r'0x147b67c: cmp\s+w8, #3',
            r'0x147b684: mov\s+w26, #2',
            r'0x147b694: mov\s+w26, #4',
            r'0x147c2f4: bl\s+#0x14e3e24',
            r'0x147c30c: fcsel\s+s9, s9, s0, hi',
            r'0x147c328: fmul\s+s0, s9, s8',
            r'0x147c338: bl\s+#0x123b7a4',
        ]:
            self.assertRegex(text, pattern)
