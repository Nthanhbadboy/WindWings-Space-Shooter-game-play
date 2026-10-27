#!/usr/bin/env python3
"""Native direct calls resolved by RVA, retaining aliases and raw instructions."""
import gzip
import importlib.util
import json
import re
import tempfile
from collections import defaultdict
from pathlib import Path

spec = importlib.util.spec_from_file_location('consts', 'tools/apk-analyze/il2cpp_consts.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
with tempfile.NamedTemporaryFile(mode='w+', suffix='.cs') as tmp:
    tmp.write(gzip.open('reverse-engineering/il2cpp/dump.cs.gz', 'rt').read())
    tmp.flush()
    methods = mod.parse_dump(tmp.name)
lookup = defaultdict(list)
for cls, ns, method, offset, rva, sig in methods:
    lookup[rva].append(dict(class_name=cls, namespace=ns, method=method, signature=sig))
result = []
for path in sorted(Path('reverse-engineering/raw/il2cpp-consts').glob('*.json')):
    jd = json.loads(path.read_text())
    cls = jd['class']
    if not cls.startswith(('Boss', 'Enemy_Movement', 'Enemy_Display')):
        continue
    asm = path.with_suffix('.asm.txt')
    blocks = {}
    current = None
    for line in asm.read_text().splitlines():
        if line.startswith(';;; '):
            current = line[4:].split('  ')[0]
            blocks[current] = []
        elif current:
            blocks[current].append(line)
    for method in jd['methods']:
        calls = []
        for line in blocks.get(method['method'], []):
            m = re.match(r'\s*(0x[0-9a-f]+):\s+(bl|b)\s+#(0x[0-9a-f]+)\s*$', line)
            if m:
                target = int(m[3], 16)
                calls.append(dict(addr=m[1], instruction=m[2], target=m[3],
                                  candidates=lookup.get(target, [])))
        result.append(dict(class_name=cls, method=method['method'], rva=method['rva'],
                           ends_clean=method['ends_clean'], calls=calls,
                           float_evidence=[c for c in method['constants'] if c['kind']=='float']))
out = Path('reverse-engineering/raw/animation-audit/native-calls.json')
out.write_text(json.dumps(dict(status='PROVISIONAL: direct calls only; aliases retained; no inferred indirect calls', methods=result), ensure_ascii=False, indent=1)+'\n')
print(len(result), 'methods traced')
for r in result:
    if r['class_name'] == 'Boss1_Director' and r['method'] in ('Start','SkeletonAnimation_AnimationState_Complete'):
        print(r['method'], [(c['addr'], [x['class_name']+'.'+x['method'] for x in c['candidates']]) for c in r['calls']])
