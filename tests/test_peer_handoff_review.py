import gzip
import json
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path('tools/verify').resolve()))
from peer_handoff_review import build, PEER


class PeerHandoffReviewTests(unittest.TestCase):
    def test_hermetic_raw_rebuild(self):
        with patch('subprocess.check_output', side_effect=AssertionError('no git/network required')):
            result = build()
        saved = json.load(gzip.open('reverse-engineering/raw/peer-review/handoff-cf27b9755.json.gz', 'rt'))
        self.assertEqual(saved, result)
        self.assertEqual(result['peer_commit'], PEER)
        self.assertEqual(len(result['checks']), 16)
        self.assertTrue(all(result['checks'].values()))

    def test_peer_fixes_credit_without_endorsing_new_claims(self):
        result = build()
        self.assertEqual(result['classifier_no_eye']['Coda_A']['category'], 'font')
        self.assertEqual(result['classifier_no_eye']['XVideo']['category'], 'ui')
        self.assertTrue(result['checks']['errors_no_longer_silently_skip'])
        self.assertTrue(result['checks']['unsupported_ship_inference_still_present'])
        self.assertTrue(result['checks']['player_index_addresses_base_array'])

    def test_current_entrypoint_and_local_links(self):
        for filename in ['README.md', 'docs/START_HERE_NEW_GAME.md', 'docs/spec/README.md',
                         'docs/HANDOFF_AI_TASKS.md', 'docs/HANDOFF_REVIEW_cf27b9755.md']:
            path = Path(filename)
            text = path.read_text()
            for link in re.findall(r'\]\(([^)]+)\)', text):
                if '://' in link or link.startswith('#'):
                    continue
                self.assertTrue((path.parent / link.split('#')[0]).exists(), (filename, link))
        self.assertIn('START_HERE_NEW_GAME.md', Path('README.md').read_text())
        self.assertIn('snapshot local cũ', Path('README.md').read_text())

    def test_split_zip_instructions_do_not_overwrite_inputs(self):
        for filename in ['README.md', '.github/workflows/analyze-apk.yml']:
            text = Path(filename).read_text()
            self.assertNotIn('cat assets.z01 assets.zip > assets.zip', text)
            self.assertNotIn('cat windwings-assets.zip.z*', text)
            self.assertIn('zip -s 0 assets.zip --out assets-full.zip', text)
