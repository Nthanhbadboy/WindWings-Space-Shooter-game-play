#!/usr/bin/env python3
"""Evidence for Home loader consumer and preference wrapper; provisional."""
import gzip
import hashlib
import json
import re
from pathlib import Path
from early_ui_native import section
from ui_routing import direct_calls

ROOT=Path(__file__).resolve().parents[2]
SELECT={'Home_Loader._Start_d__5':['MoveNext'], 'Home_Loader':['Awake','CheckSpecPopup'],
        'PlayerPreferences':['SetInt','GetInt','SaveToDisk','OnApplicationQuit','OnApplicationFocus']}


def metadata_loads(text,relocations,metadata):
    pages={};result=[]
    for line in text.splitlines():
        m=re.search(r'(0x[0-9a-f]+):\s+(\S+)\s*(.*)',line)
        if not m:continue
        site,op,args=m.groups()
        adrp=re.fullmatch(r'(x\d+), #?(0x[0-9a-f]+)',args)
        if op=='adrp' and adrp:
            pages[adrp[1]]=int(adrp[2],16);continue
        load=re.fullmatch(r'(x\d+), \[(x\d+)(?:, #(0x[0-9a-f]+|\d+))?\]',args)
        if op=='ldr' and load and load[2] in pages:
            slot=pages[load[2]]+int(load[3] or '0',0)
            effective=relocations.get(hex(slot))
            if effective and int(effective,16) in metadata:
                result.append({'callsite':site,'slot':hex(slot),'effective_address':effective,
                               'records':metadata[int(effective,16)]})
        if op in ('bl','blr'):
            pages={r:v for r,v in pages.items() if int(r[1:])>18}
        elif op in ('mov','add','sub','ldr','ldrb','ldrh','ldrsw','ldp','csel','csinc','and','orr'):
            dest=args.split(',',1)[0]
            pages.pop(dest,None)
    return result


def main():
    base=ROOT/'reverse-engineering/raw/ui-audit'
    meta=json.load(gzip.open(base/'metadata-index.json.gz','rt'))
    reloc=json.load(gzip.open(base/'native-relocations.json.gz','rt'))
    index={}
    for group,rows in meta['tables'].items():
        for row in rows:index.setdefault(row['Address'],[]).append(dict(row,group=group))
    dump=gzip.open(ROOT/'reverse-engineering/il2cpp/dump.cs.gz','rt').read()
    by_rva={};decl={}
    for b in re.split(r'(?=// Namespace:)',dump):
        cls=re.search(r'(?:class|enum) ([^ :\n]+)',b)
        if not cls:continue
        if cls[1] in ('Home_Loader','BoardEvent','LoadBoardMode','EventID','PlayerPreferences'):
            decl[cls[1]]=b
        for m in re.finditer(r'// RVA: (0x[0-9a-f]+)[^\n]*\n([^\n]+)',b,re.I):
            by_rva[int(m[1],16)]={'class':cls[1],'signature':m[2].strip()}
    records=[]
    for cls,methods in SELECT.items():
        p=base/'extra-native'/f'{cls}.asm.txt'
        text=p.read_text()
        for name in methods:
            t=section(text,name)
            records.append({'class':cls,'method':name,'source':str(p.relative_to(ROOT)),
                            'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'asm':t,
                            'calls':direct_calls(t,by_rva),
                            'metadata_loads':metadata_loads(t,reloc['relocations'],index)})
    methods={(r['class'],r['method']):r['asm'] for r in records}
    t=methods['Home_Loader._Start_d__5','MoveNext']
    checks={'home_loader_posts_openboard':all(x in t for x in
            ('cmp      w8, #6','mov      w20, #6','mov      w1, w20','mov      w2, wzr',
             '#0x123eac8','mov      w1, #0x38','#0x1434cb4')),
            'preference_setint_is_unity_tailcall':'#0x277cc10' in methods['PlayerPreferences','SetInt'],
            'preference_getint_is_unity_tailcall':'#0x277cca0' in methods['PlayerPreferences','GetInt']}
    assert all(checks.values()),checks
    out={'status':'PROVISIONAL','source_run':meta['source_run'],'native_sha256':reloc['native_sha256'],
         'checks':checks,'declarations':decl,'methods':records,
         'warning':'ADRP/LDR scanner is conservative, not full control-flow/dataflow reconstruction'}
    with gzip.open(base/'loader-and-prefs.json.gz','wt') as f:json.dump(out,f,ensure_ascii=False,indent=2)
    print(json.dumps(checks,indent=2))
    for r in records:
        print(r['class'],r['method'],[(m['slot'],[s.get('Name',s.get('Value')) for s in m['records']]) for m in r['metadata_loads']])


if __name__=='__main__': main()
