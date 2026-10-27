import importlib.util
from pathlib import Path
import unittest

path = Path('tools/apk-probe/player_loadout_native.py')
spec = importlib.util.spec_from_file_location('player_loadout_native', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PlayerLoadoutRecoveryTests(unittest.TestCase):
    def test_mask_keeps_all_method_boundaries(self):
        rows = [('Player_Saved_Datas', '', 'GetPlayerUsed', 16, 32, 'int GetPlayerUsed(int slot)'),
                ('GP_Tutorials.Nested', '', 'MoveNext', 44, 60, 'bool MoveNext()'),
                ('Player_Device_Saved_Datas', '', 'GetPlayerDevices', 80, 96, 'int[] GetPlayerDevices(int id)')]
        masked = module.mask_unselected(rows)
        self.assertEqual(len(rows), len(masked))
        self.assertEqual([row[1:] for row in rows], [row[1:] for row in masked])
        self.assertEqual(masked[0], rows[0])
        self.assertEqual(masked[2], rows[2])
        self.assertEqual(masked[1][0], '__not_selected__')

    def test_only_two_classes_and_strict_original_hashes(self):
        self.assertEqual(set(module.CLASSES), {'Player_Saved_Datas', 'Player_Device_Saved_Datas'})
        self.assertEqual(module.APK_SHA, 'f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e')
        self.assertEqual(len(module.INPUTS), 2)
        self.assertIn('lib/arm64-v8a/libil2cpp.so', module.INPUTS)

    def test_scoped_workflow_not_full_analyze(self):
        workflow = Path('.github/workflows/recover-player-loadout.yml').read_text()
        self.assertIn('fail-on-cache-miss: true', workflow)
        self.assertIn('Regression gate before publishing raw', workflow)
        self.assertNotIn('analyze-apk.yml', workflow)
        self.assertNotIn('version=latest', workflow)
        self.assertIn("test \"$GITHUB_REF_NAME\" = 'arena/ef6b75ef-windwings-space-shooter-game-p'", workflow)


if __name__ == '__main__':
    unittest.main()
