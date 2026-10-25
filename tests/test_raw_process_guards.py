import gzip
import json
from pathlib import Path
import unittest


class RawProcessGuards(unittest.TestCase):
    def test_main_analysis_enforces_pin_before_extract(self):
        text = Path('.github/workflows/analyze-apk.yml').read_text()
        pin_check = "echo 'f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e  /tmp/apk/windwings.xapk' | sha256sum --check --strict"
        self.assertIn(pin_check, text)
        self.assertLess(text.index(pin_check), text.index('- name: Extract Unity payload'))
        self.assertIn("- '!tools/apk-analyze/early_wave_prefabs.py'", text)

    def test_raw_triggers_and_producer_regressions(self):
        text = Path('.github/workflows/verify-extracted-tables.yml').read_text()
        self.assertIn("'reverse-engineering/raw/**'", text)
        self.assertIn("'reverse-engineering/il2cpp/**'", text)
        for name in ('recover-early-waves', 'recover-ui-metadata'):
            text = Path('.github/workflows/' + name + '.yml').read_text()
            self.assertIn('python3 -m unittest discover -s tests -q', text)
            self.assertLess(text.index('python3 -m unittest discover -s tests -q'), text.index('git commit -m'))

    def test_scope_snapshot_does_not_label_unindexed_as_trash(self):
        # Historical process snapshot: don't require its index SHA to track future exports.
        p = Path('reverse-engineering/raw/process-audit/scope-inventory.json.gz')
        x = json.loads(gzip.decompress(p.read_bytes()))['ui']
        self.assertEqual(x['files_on_disk'], len(x['files']))
        self.assertEqual(x['unindexed_files'], sum(not r['in_current_index'] for r in x['files']))
        self.assertEqual(x['compressed_bytes'], sum(r['compressed_bytes'] for r in x['files']))
        self.assertIn('no deletion', x['warning'])
        self.assertEqual(x['missing_indexed_files'], [])


if __name__ == '__main__':
    unittest.main()
