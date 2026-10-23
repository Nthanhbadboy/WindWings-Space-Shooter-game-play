#!/usr/bin/env python3
"""Preserve checked native lifecycle evidence; do not infer delegate targets."""
import hashlib
import json
from pathlib import Path

root = Path('reverse-engineering/raw/il2cpp-consts')
checks = {
    'Enemy_Appear': [('0x158210c', 'cbz x1, #0x1582124'),
                     ('0x1582120', 'br x2'), ('0x1582124', 'bl #0x110d250')],
    'Enemy_Destroy': [('0x15856fc', 'ldr x20, [x19, #0x28]'),
                      ('0x1585724', 'blr x9'), ('0x1585728', 'ldr x8, [x19, #0x20]'),
                      ('0x1585744', 'blr x9')],
}
out = {}
for cls, expected in checks.items():
    p = root / (cls + '.asm.txt')
    lines = {l.strip().split(':', 1)[0]: l.strip() for l in p.read_text().splitlines() if l.strip().startswith('0x')}
    evidence = []
    for address, instruction in expected:
        assert instruction in ' '.join(lines[address].split()), (address, lines[address])
        evidence.append(lines[address])
    out[cls] = dict(source=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), evidence=evidence)
Path('reverse-engineering/raw/animation-audit/enemy-lifecycle.json').write_text(json.dumps(dict(status='PROVISIONAL static evidence; delegate targets not resolved', classes=out), ensure_ascii=False, indent=1)+'\n')
print('7 lifecycle instruction checks passed')
