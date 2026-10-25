#!/usr/bin/env python3
"""Direct native-call evidence for routing/persistence; no guessed callback targets."""
import gzip
import hashlib
import json
import re
from pathlib import Path
from early_ui_native import section

ROOT = Path(__file__).resolve().parents[2]
SELECT = {'Board_Endgame': ['OnPressedButtonContinue', 'Continue', 'LoadToLoading',
                            'LoadSceneHome', '<OnPressedButtonContinue>b__103_0',
                            'CheckPremiumPopup', '_2'],
          'GP_Tutorials': ['set_IndexTutorial'],
          'Board_Endgame.__c': ['<LoadSceneHome>b__129_0', '<LoadToLoading>b__130_0']}


def direct_calls(text, by_rva):
    result = []
    for line in text.splitlines():
        m = re.search(r'(0x[0-9a-f]+):\s+(bl|b)\s+#(0x[0-9a-f]+)\s*$', line)
        if m:
            rva = int(m[3], 16)
            result.append({'callsite': m[1], 'instruction': m[2], 'target_rva': m[3],
                           'declaration': by_rva.get(rva),
                           'status': 'resolved_from_dump' if rva in by_rva else 'unresolved_or_internal_branch'})
    return result


def main():
    dp = ROOT / 'reverse-engineering/il2cpp/dump.cs.gz'
    dump = gzip.open(dp, 'rt').read()
    by_rva = {}
    blocks = {}
    for b in re.split(r'(?=// Namespace:)', dump):
        cls = re.search(r'(?:class|enum) ([^ :\n]+)', b)
        if not cls:
            continue
        if cls[1] in ('ScenesManager.Scene', 'Stage_Datas', 'Board_Endgame', 'Home_Loader', 'GameMode', 'PlayMode', 'BoardID'):
            blocks[cls[1]] = b
        for m in re.finditer(r'// RVA: (0x[0-9A-F]+)[^\n]*\n([^\n]+)', b, re.I):
            by_rva[int(m[1], 16)] = {'class': cls[1], 'signature': m[2].strip()}
    records = []
    for cls, names in SELECT.items():
        p = ROOT / f'reverse-engineering/raw/il2cpp-consts/{cls}.asm.txt'
        text = p.read_text()
        for name in names:
            t = section(text, name)
            records.append({'class': cls, 'method': name, 'source': str(p.relative_to(ROOT)),
                            'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                            'asm': t, 'direct_calls': direct_calls(t, by_rva)})
    checks = {}
    method = {(r['class'], r['method']): r['asm'] for r in records}
    checks['tutorial_setter_calls_prefs_setint'] = '#0x13f1a04' in method['GP_Tutorials', 'set_IndexTutorial']
    for name, scene in [('LoadToLoading', 2), ('LoadSceneHome', 1)]:
        t = method['Board_Endgame', name]
        checks[name + '_fallback_scene'] = f'mov      w0, #{scene}' in t and '#0x141b488' in t
    t = method['Board_Endgame', 'Continue']
    checks['continue_has_both_scene_routes'] = '#0x126e5cc' in t and '#0x126f3c8' in t
    checks['continue_drone_fallback_id_20001'] = 'mov      w1, #0x4e21' in t and '#0x14db228' in t
    t = method['Board_Endgame', 'OnPressedButtonContinue']
    checks['continue_button_can_open_notice'] = '#0x13b83cc' in t and '[x19, #0x1a0]' in t
    metadata_path = ROOT / 'reverse-engineering/raw/ui-audit/metadata-slots.json'
    metadata = json.loads(metadata_path.read_text())
    resolved = {}
    for slot, effective in metadata.get('slot_effective_addresses', {}).items():
        resolved[slot] = [dict(r, group=group) for group, rows in metadata['rows'].items()
                          for r in rows if r.get('Address') == int(effective, 16)] if effective else []
    checks['victory_type_slot_resolved'] = any(r.get('Name') == 'Board_Endgame_TypeInfo' for r in resolved.get('0x2adc6b0', []))
    checks['tutorial_key_TUTORIAL_resolved'] = any(r.get('Value') == 'TUTORIAL' for r in resolved.get('0x2adc200', []))
    for name, scene in [('<LoadSceneHome>b__129_0', 1), ('<LoadToLoading>b__130_0', 2)]:
        t = method['Board_Endgame.__c', name]
        checks[name + '_loads_scene'] = f'mov      w0, #{scene}' in t and '#0x141b488' in t
    assert all(checks.values()), checks
    result = {'status': 'PROVISIONAL', 'checks': checks,
              'source_dump_sha256': hashlib.sha256(dp.read_bytes()).hexdigest(),
              'warning': 'metadata joins use ELF relocation and exact address; unrelated indirect calls remain unresolved',
              'metadata_source_sha256': hashlib.sha256(metadata_path.read_bytes()).hexdigest(),
              'resolved_slots': resolved, 'declarations': blocks, 'methods': records}
    out = ROOT / 'reverse-engineering/raw/ui-audit/routing-and-persistence.json.gz'
    with gzip.open(out, 'wt') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(checks, indent=2))


if __name__ == '__main__':
    main()
