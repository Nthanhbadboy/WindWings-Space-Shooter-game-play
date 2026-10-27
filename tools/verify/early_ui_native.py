#!/usr/bin/env python3
"""Preserve selected native UI branches and check the numeric gates, not playback."""
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def section(text, method):
    for s in text.split(';;; ')[1:]:
        if s.split('  ', 1)[0] == method:
            return ';;; ' + s
    raise ValueError(method)


def main():
    selections = {'DataTutorials': ['get_hasTutStage1', 'get_hasTutStage2', 'get_hasTutStage3'],
                  'GP_Tutorials': ['CheckRunTutorialNew'], 'Board_Endgame': ['SetupTut', 'CheckPremiumPopup', '_2', '<CheckPremiumPopup>b__91_0', '<CheckPremiumPopup>b__91_1']}
    sources = {}
    for cls, methods in selections.items():
        p = ROOT / f'reverse-engineering/raw/il2cpp-consts/{cls}.asm.txt'
        text = p.read_text()
        sources[cls] = {'source': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                        'sections': {m: section(text, m) for m in methods}}
    dump = gzip.open(ROOT / 'reverse-engineering/il2cpp/dump.cs.gz', 'rt').read()
    targets = {}
    for rva in ('14EFDEC', '14F0DA0', '14F4A14', '14FA7B0', '1397438', '2781804'):
        m = re.search(r'// RVA: 0x' + rva + r'[^\n]*\n([^\n]+)', dump, re.I)
        assert m, rva
        targets['0x' + rva.lower()] = m[1].strip()
    checks = {}
    for name, fragments in {
        'get_hasTutStage1': ['#0x14f0da0', '#0x14f4a14', 'cmp      w0, #0', 'cset     w0, eq'],
        'get_hasTutStage2': ['#0x14f0da0', '#0x14f4a14', 'cmp      w0, #1', 'cset     w0, eq'],
        'get_hasTutStage3': ['#0x14f0da0', 'cmp      w0, #2', '#0x14fa7b0', 'eor      w8, w0, #1'],
    }.items():
        checks[name] = all(f in sources['DataTutorials']['sections'][name] for f in fragments)
    t = sources['GP_Tutorials']['sections']['CheckRunTutorialNew']
    checks['tutorial_branches_present'] = all(f in t for f in ('#0x1327e90', '#0x14faa94', '#0x14faaf4',
                                                               '#0x1327f08', '#0x14fab88',
                                                               '#0x1327f8c', '#0x14fac18'))
    t = sources['Board_Endgame']['sections']['SetupTut']
    checks['endgame_hides_buttons_for_early_index'] = all(f in t for f in
        ('cmp      w0, #1', 'b.le', '[x19, #0x88]', '[x19, #0x80]', '[x19, #0x78]', '#0x2781804'))
    t = sources['Board_Endgame']['sections']['_2']
    checks['endgame_callback_reveals_continue_and_increments_tutorial'] = all(f in t for f in
        ('0x126d4e8: ldr      x0, [x19, #0x80]', '0x126d4f0: mov      w1, wzr',
         '0x126d4fc: ldr      x0, [x19, #0x88]', '0x126d514: mov      w1, #1',
         '0x126d538: add      w0, w0, #1', '#0x14f9f84'))
    assert all(checks.values()), checks
    out = {'status': 'PROVISIONAL', 'checks': checks, 'resolved_direct_calls_from_dump': targets,
           'sources': sources, 'warning': 'numeric stageIndex gates; not proof of first-clear queue or displayed stage numbering'}
    p = ROOT / 'reverse-engineering/raw/ui-audit/early-native-gates.json'
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(checks, indent=2))


if __name__ == '__main__':
    main()
