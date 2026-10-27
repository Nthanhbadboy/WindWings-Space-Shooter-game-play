#!/usr/bin/env python3
"""Evidence-checked Boss1 phase interpretation; not a replacement game script."""
import hashlib
import json
from pathlib import Path

path = Path('reverse-engineering/raw/il2cpp-consts/Boss1_Director.asm.txt')
text = path.read_text()
blocks = {}
current = None
for line in text.splitlines():
    if line.startswith(';;; '):
        current = line[4:].split('  ')[0]
        blocks[current] = []
    elif current and line.strip():
        blocks[current].append(line.strip())

def evidence(method, addr, expected):
    line = next(l for l in blocks[method] if l.startswith(addr + ':'))
    assert expected in ' '.join(line.split()), (method, addr, line)
    return dict(method=method, instruction=line)

checks = [
    evidence('OnGunDie', '0x150052c', 'ldr w8, [x19, #0xc0]'),
    evidence('OnGunDie', '0x1500530', 'subs w8, w8, #1'),
    evidence('OnGunDie', '0x1500534', 'b.lt #0x150053c'),
    evidence('OnGunDie', '0x1500598', 'ldr w8, [x19, #0xc4]'),
    evidence('OnGunDie', '0x15005a0', 'b.eq #0x15005fc'),
    evidence('OnGunDie', '0x15008e0', 'bl #0x1500d28'),
    evidence('OnGunDie', '0x15008ec', 'add w8, w8, #1'),
    evidence('ClearGuns', '0x1500db0', 'ldr x2, [x19, #0x58]'),
    evidence('ClearGuns', '0x1500dcc', 'ldr x2, [x19, #0x60]'),
    evidence('ClearGuns', '0x1500de0', 'mov w3, wzr'),
    evidence('ClearGuns', '0x1500e10', 'ldr x2, [x19, #0x38]'),
]
obj = dict(status='PROVISIONAL static control-flow interpretation; callback caller identity unresolved',
           prefab='Boss-39002', class_name='Boss1_Director',
           asm_source=str(path), asm_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
           counter_update='if countGunCanHit - 1 >= 0: countGunCanHit -= 1; not the phase gate in OnGunDie',
           turn_update='ClearGuns(old_countTurn); countTurn = old_countTurn + 1 on normal return',
           transitions=[dict(turn=0, animation='Chuyensangattack2', loop=False, on_complete='Attack2 then loop Attack2'),
                        dict(turn=1, animation='Chuyensangattack3', loop=False, on_complete='Attack3 then loop Attack3'),
                        dict(turn='other', animation='Dead', loop=False, on_complete='Defeat')],
           evidence=checks,
           unresolved=['Exact death event/interface dispatch and delegate target must be verified',
                       'Do not apply to other bosses or assume HP percentage thresholds',
                       'Double/reentrant death callbacks not excluded by the inspected method'])
Path('reverse-engineering/raw/animation-audit/boss1-conditions.json').write_text(json.dumps(obj, ensure_ascii=False, indent=1)+'\n')
print(f'{len(checks)} instruction checks passed; condition trace saved')
