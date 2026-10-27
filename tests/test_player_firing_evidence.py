"""Bounded native evidence checks, not a combat simulator."""
import gzip
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'reverse-engineering/raw/player-firing'


class PlayerFiringEvidenceTests(unittest.TestCase):
    def test_pinned_manifest_and_raw_hashes(self):
        index = json.loads((RAW / 'index.json').read_text())
        self.assertEqual(index['inputs_sha256']['lib/arm64-v8a/libil2cpp.so'],
                         '9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99')
        self.assertEqual(index['dump_sha256_decompressed'], hashlib.sha256(gzip.decompress(
            (ROOT / 'reverse-engineering/il2cpp/dump.cs.gz').read_bytes())).hexdigest())
        self.assertEqual(len(index['files']), 6)
        for row in index['files']:
            self.assertEqual(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest(),
                             row['sha256_decompressed'])

    def test_getter_and_timer_evidence(self):
        # Match address-qualified operations; do not mistake a similarly named spawn rate.
        text = (RAW / 'native/Player_Attack_1.asm.txt').read_text()
        for pattern in (
            r'0x147a364: bl\s+#0x14e3cd8',
            r'0x147a380: str\s+s0, \[x19, #0xa8\]',
            r'0x147a920: bl\s+#0x2786dc0',
            r'0x147a924: ldr\s+s1, \[x19, #0x10c\]',
            r'0x147a928: fcmp\s+s0, s1',
            r'0x147a92c: b.mi\s+#0x147acf0',
            r'0x147a988: ldr\s+s1, \[x19, #0xa8\]',
            r'0x147a98c: fadd\s+s0, s0, s1',
            r'0x147a990: str\s+s0, \[x19, #0x10c\]',
        ):
            self.assertRegex(text, pattern)
        getters = (RAW / 'native/Player_Get_Datas.asm.txt').read_text()
        self.assertRegex(getters, r'0x14e3d28: ldr\s+x8, \[x8, #0x80\]')
        self.assertRegex(getters, r'0x14e3d54: fsub\s+s0, s1, s0')
        self.assertRegex(getters, r'0x14e3d58: fmul\s+s0, s8, s0')

    def test_scope_and_no_capped_methods(self):
        for cls in ('Player_Get_Datas', 'Player_Attack', 'Player_Attack_1'):
            methods = json.loads((RAW / f'native/{cls}.json').read_text())['methods']
            self.assertTrue(methods)
            self.assertFalse(any(m['size_capped'] for m in methods))
        # Absence of cap does NOT establish exact method boundaries (minimum spans/shared RVAs).
