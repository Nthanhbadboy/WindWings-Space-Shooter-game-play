import gzip
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('early_ui', Path(__file__).resolve().parents[1] / 'tools/verify/early_ui_flows.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class EarlyUICoverageTest(unittest.TestCase):
    def test_presence_never_resolves_stage_gate_and_duplicate_layouts_are_not_screens(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dump = root / 'reverse-engineering/il2cpp/dump.cs.gz'
            dump.parent.mkdir(parents=True)
            with gzip.open(dump, 'wt') as f:
                f.write('// Namespace: \npublic class DataTutorials\n{\npublic static bool hasTutStage1 { get; }\n}\n')
            ui = root / 'reverse-engineering/raw/ui'
            ui.mkdir(parents=True)
            layout = {'class': 'Board_Home', 'nodes': [{'path': 'Board_Home/Tut', 'components': [{'class': 'GP_Tutorials'}]}]}
            for name in ('Board_Home__1.json.gz', 'Board_Home__2.json.gz'):
                with gzip.open(ui / name, 'wt') as f:
                    json.dump(layout, f)
            d = mod.audit(root)
            home = next(c for c in d['classes'] if c['class'] == 'Board_Home')
            self.assertEqual((home['layout_exports'], home['distinct_node_hashes']), (2, 1))
            self.assertIn('DataTutorials', d['declarations'])
            self.assertTrue(all(g['tutorial'] == 'UNRESOLVED' for g in d['stage_gates']))
            self.assertFalse(home['native_export_available'])


if __name__ == '__main__':
    unittest.main()
