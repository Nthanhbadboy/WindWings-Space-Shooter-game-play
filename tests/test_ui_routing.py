import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/verify'))
from ui_routing import direct_calls


class RoutingTests(unittest.TestCase):
    def test_internal_branch_is_not_a_resolved_method(self):
        calls = direct_calls('    0x10: bl       #0x20\n    0x14: b        #0x18\n    0x18: blr      x9', {32: {'class': 'A'}})
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0]['status'], 'resolved_from_dump')
        self.assertEqual(calls[1]['status'], 'unresolved_or_internal_branch')


if __name__ == '__main__':
    unittest.main()
