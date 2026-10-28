#!/usr/bin/env python3
"""Preserve controller declarations from APK dump; declarations are not bodies."""
import gzip
import json
import re
from pathlib import Path

s = gzip.open('reverse-engineering/il2cpp/dump.cs.gz', 'rt').read()
records = []
for m in re.finditer(r'^(?:public|internal) (?:sealed |abstract )?class ([\w_]+)\b[^\n]*\n\{.*?^}', s, re.M | re.S):
    name, block = m[1], m[0]
    if not (name.startswith(('Boss', 'MiniBoss', 'MB')) or name in ('Enemy_Movement', 'Enemy_Attack', 'Enemy_Display', 'Enemy_Rotate')):
        continue
    if not re.search(r'SkeletonAnimation|Animator\b|AnimationState|AnimationEvent|CallMixAnimation|PathFollow|RotateToTarget', block):
        continue
    records.append(dict(class_name=name, declaration=block,
                        evidence='metadata declarations only; method bodies not decompiled here'))
dest = Path('reverse-engineering/raw/animation-audit/script-declarations.json')
dest.write_text(json.dumps(dict(status='PROVISIONAL', classes=records), ensure_ascii=False, indent=1)+'\n')
print(len(records), 'animation/movement-related class declarations preserved')
