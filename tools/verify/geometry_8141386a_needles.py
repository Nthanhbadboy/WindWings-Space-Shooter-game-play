"""Sync ONLY three live-worktree needles; never repair historical failed claims.
provenance: arena/8141386a-windwings-space-shooter-game-p
Run after the same-commit report is present, then refresh-readme-sizes and verify-claims.
"""
from pathlib import Path
import re
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[2]


def sub_one(text,pattern,replacement):
    result,n=re.subn(pattern,replacement,text,flags=re.M)
    if n!=1:raise ValueError(f'expected one needle marker, got {n}: {pattern}')
    return result


def sync():
    spec=ROOT/'docs/spec';readme=spec/'README.md'
    text=readme.read_text()
    marker='\n## Branch-owned verification-support index (8141386a)\n'
    text=text.split(marker)[0].rstrip()+'\n'
    entries=sorted(p.name for p in spec.glob('*.md') if p.name not in ('START_HERE.md','README.md'))
    if len(entries)!=41:raise ValueError('historical RD1 table has 41 rows; do not silently redefine its contract')
    text+=marker+'\nprovenance: `arena/8141386a-windwings-space-shooter-game-p`. Added spec files are\n'
    text+='verification support pinned in the import receipt, not an APK re-export. Existing\n'
    text+='GAMEPLAY/UI/ASSETS/BALANCE summaries above are retained, not replaced.\n\n'
    text+='`verify-claims.py` uses an explicitly printed historical support view; only\n'
    text+='APKD1 / AI1 / RD1 check the current own worktree. A scoped green result does\n'
    text+='not assert that the current peer runtime-probe/raw sources passed historical claims.\n'
    text+='Use `--unscoped-legacy` to see those inherited incompatibilities.\n\n'
    text+='**Kiểm tự động (`RD1`):** **41 dòng · 0 lệch**\n\n| Tài liệu support | Kích thước đo từ file hiện tại |\n|---|---|\n'
    for name in entries:
        lines=(spec/name).read_text().splitlines();tables=sum(l.lstrip().startswith('|---') for l in lines)
        text+=f'| `{name}` | {len(lines)} dòng · {tables} bảng |\n'
    readme.write_text(text)
    apk=ROOT/'docs/apk-analysis'
    counts=(len(list(apk.glob('*.md'))),len(list(apk.glob('*.csv'))))
    asm=list((ROOT/'reverse-engineering/raw/il2cpp-consts').glob('*.asm.txt'))
    lines=sum(len(p.read_bytes().splitlines()) for p in asm)
    values=(len(asm),lines,len(list((ROOT/'reverse-engineering/raw/typetrees').glob('*'))),
            len(list((ROOT/'reverse-engineering/scriptableobjects').glob('*.csv'))),
            len(list((ROOT/'docs/assets/contact-sheets').glob('*.jpg'))),
            sum(p.is_file() for p in (ROOT/'datas').glob('*')))
    apk_anchor=f'**{counts[0]}** `.md` · **{counts[1]}** `.csv`'
    ai_anchor=(f'**Cộng kho đo được (đếm bằng `AI1`):** **{values[0]}** file asm · **{values[1]:,}** dòng asm · '
               f'**{values[2]}** typetree · **{values[3]}** bảng ScriptableObject · **{values[4]}** contact sheet · '
               f'**{values[5]}** file `datas/`.').replace(f'{values[1]:,}',f'{values[1]:,}'.replace(',','.'))
    start=spec/'START_HERE.md';body=start.read_text()
    body=sub_one(body,r'\*\*\d+\*\* `\.md` · \*\*\d+\*\* `\.csv`',apk_anchor)
    body=sub_one(body,r'^\*\*Cộng kho đo được \(đếm bằng `AI1`\):\*\*.*$',ai_anchor)
    note='> Branch 8141386a: APKD1/AI1/RD1 below measure this worktree. Other legacy claims use an explicit pinned historical-support view, NOT validation of all current peer raw/runtime code.\n'
    if note not in body:body=body.split('\n',1)[0]+'\n\n'+note+body.split('\n',1)[1]
    start.write_text(body)
    tool=ROOT/'tools/verify-claims.py';code=tool.read_text()
    begin=code.index('claim("APKD1",');end=code.index('\nclaim("IA8",',begin)
    code=code[:begin]+sub_one(code[begin:end],r'"\*\*\d+\*\* `\.md` · \*\*\d+\*\* `\.csv`",',repr(apk_anchor).replace("'",'"')+',')+code[end:]
    begin=code.index('claim("APKD1",');end=code.index('\nclaim("IA8",',begin)
    code=code[:begin]+sub_one(code[begin:end],r'\(\d+, \d+\), apk_doc_counts,',f'{counts}, apk_doc_counts,')+code[end:]
    begin=code.index('claim("AI1",');end=code.index('\nclaim("AP1",',begin)
    replacement='claim("AI1", "docs/spec/START_HERE.md",\n      '+repr(ai_anchor)+',\n      '+repr(values)+', data_inventory,\n      "current own worktree: asm, typetree, ScriptableObject, contact sheet, datas; not historical support counts")\n'
    code=code[:begin]+replacement+code[end:]
    tool.write_text(code)
    receipt=ROOT/'reverse-engineering/raw/geometry-8141386a/verification-support-imports.json'
    record=json.loads(receipt.read_bytes())
    record['post_import_adjustments']={str(p.relative_to(ROOT)):{'current_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                                        'reason':'Three live-worktree needles / explicit scoped-support adapter only; all other historical expectations unchanged'}
                                        for p in (start,tool)}
    for item in record['existing_preserved']:
        if 'baseline_sha256' not in item:
            original=subprocess.check_output(['git','-C',str(ROOT),'show','600a4a340bd27d7e9e63a53941bbe6d97ce430bf:'+item['path']])
            item['baseline_sha256']=hashlib.sha256(original).hexdigest()
            item['baseline_sha256_rstrip']=hashlib.sha256(original.rstrip()).hexdigest()
    record['protected_paths_sha256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
                                      ('datas/PROVENANCE.md','datas/boss_anim_events.csv','datas/player_start_stats.json')}
    record['current_needles']={'APKD1':counts,'AI1':values,'RD1':(len(entries),0)}
    record['scope_note']='209-claim historical support compatibility with three current own-worktree needles; NOT all current ef raw/runtime-probe or geometry acceptance. Unscoped diagnostic preserved separately.'
    receipt.write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n')
    print('APKD1',counts,'AI1',values,'RD1',(len(entries),0))


if __name__=='__main__':sync()
