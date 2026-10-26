#!/usr/bin/env python3
"""Reproducible static APK joins: fade callback, current stage, map wave consumer."""
import gzip
import hashlib
import json
import re
from pathlib import Path
from early_ui_native import section
from ui_loader_analysis import metadata_loads
from ui_routing import direct_calls

ROOT = Path(__file__).resolve().parents[2]
SELECT = {
    'Board_Endgame':['LoadToLoading'],
    'Board_Endgame.__c':['<LoadToLoading>b__130_0'],
    'ScenesManager':['LoadScene'],
    'FadeScreen':['FadeOut','FadeTo'],
    'FadeScreen._FadeTo_d__11':['MoveNext'],
    'GP_Setup':['Awake','get_stageIndex'],
    'GP_Spawner':['LoadPlayer'],
    'GP_Manager':['Start'],
    'MapController':['Start'],
    'Map_Get_Datas':['GetListWaves'],
}
BASE_CLASSES = {'Board_Endgame','Board_Endgame.__c','Map_Get_Datas'}


def asm_range(text, start, end):
    rows=[]
    for line in text.splitlines():
        m=re.match(r'\s*(0x[0-9a-f]+):',line)
        if m and start <= int(m[1],16) <= end:
            rows.append(line)
    if not rows:
        raise ValueError('No instructions in requested range')
    return '\n'.join(rows)+'\n'


def immediate_array(asm):
    """Decode only literal MOV + int stores through x1 in a small new-array span.

    Not an emulator. Refuse incomplete stores rather than invent default values.
    Caller preserves the span and separately checks list construction/append order.
    """
    m=re.search(r'mov\s+w1, #(0x[0-9a-f]+|\d+)\s*\n\s*0x[0-9a-f]+: bl\s+#0x110d09c',asm)
    if not m:
        raise ValueError('Missing immediate array allocation length')
    length=int(m[1],0)
    values=[None]*length
    regs={}
    for line in asm.splitlines():
        m=re.search(r':\s+(\w+)\s+(.*)',line)
        if not m:
            continue
        op,args=m.groups()
        literal=re.fullmatch(r'(w\d+), #(0x[0-9a-f]+|\d+)',args)
        if op=='mov' and literal:
            regs[literal[1]]=int(literal[2],0)
        elif op in ('ldr','ldrb','add','sub','mov','csel'):
            regs.pop(args.split(',')[0],None)
        if op=='str':
            store=re.fullmatch(r'(w\d+), \[x1, #(0x[0-9a-f]+|\d+)\]',args)
            if store:
                offset=int(store[2],0)-0x20
                if offset%4 or not 0 <= offset//4 < length or store[1] not in regs:
                    raise ValueError('Unresolved/invalid element store')
                values[offset//4]=regs[store[1]]
    if not values or None in values:
        raise ValueError('Incomplete immediate array evidence')
    return values


def main():
    audit=ROOT/'reverse-engineering/raw/ui-audit'
    dp=ROOT/'reverse-engineering/il2cpp/dump.cs.gz'
    dump=gzip.open(dp,'rt').read(); rv={};decl={};index={}
    for block in re.split(r'(?=// Namespace:)',dump):
        c=re.search(r'(?:class|enum) ([^ :\n]+)',block)
        if not c:continue
        decl[c[1]]=block
        for m in re.finditer(r'// RVA: (0x[\dA-Fa-f]+)[^\n]*\n([^\n]+)',block):
            rv[int(m[1],16)]={'class':c[1],'signature':m[2].strip()}
    meta=json.load(gzip.open(audit/'metadata-index.json.gz','rt'))
    rel=json.load(gzip.open(audit/'native-relocations.json.gz','rt'))
    for group,rows in meta['tables'].items():
        for row in rows:index.setdefault(row['Address'],[]).append(dict(row,group=group))
    records=[];methods={}
    for cls,names in SELECT.items():
        folder=ROOT/'reverse-engineering/raw/il2cpp-consts' if cls in BASE_CLASSES else audit/'extra-native'
        p=folder/f'{cls}.asm.txt';text=p.read_text()
        inventory=json.loads((folder/f'{cls}.json').read_text())
        for name in names:
            asm=section(text,name)
            inv=next(m for m in inventory['methods'] if m['method']==name)
            assert not inv.get('size_capped'),(cls,name)
            methods[cls,name]=asm
            records.append({'class':cls,'method':name,'source':str(p.relative_to(ROOT)),
                'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'asm':asm,'inventory':inv,
                'calls':direct_calls(asm,rv),'metadata_loads':metadata_loads(asm,rel['relocations'],index)})
    ccp=ROOT/'reverse-engineering/raw/il2cpp-consts/Map_Get_Datas.asm.txt'
    cc=section(ccp.read_text(),'cctor')
    spans=[asm_range(cc,0x1406c94,0x1406cb4),asm_range(cc,0x1406d08,0x1406d38)]
    values=[immediate_array(s) for s in spans]
    assert values==[[164],[113,5]],values
    start=methods['MapController','Start'];setup=methods['GP_Setup','get_stageIndex']
    callback=methods['Board_Endgame.__c','<LoadToLoading>b__130_0']
    slots={s:{'effective_address':rel['relocations'][s],
              'records':index[int(rel['relocations'][s],16)]} for s in
           ('0x2addcf0','0x2adf3e0','0x2adc6d8','0x2ae8fa0','0x2ae8f88','0x2adf9a0','0x2adf9a8','0x2adf9c0')}
    checks={
        'fade_callback_loads_game':all(s in callback for s in ('mov      w0, #2','b        #0x141b488')),
        'fade_callback_metadata_matches_rva':any(r.get('MethodAddress')==0x1276e1c for r in slots['0x2addcf0']['records']),
        'fade_factory_preserves_callback_field': 'str      x19, [x21, #0x38]' in methods['FadeScreen','FadeTo'],
        'fade_coroutine_has_callback_invocation':all(s in methods['FadeScreen._FadeTo_d__11','MoveNext'] for s in
            ('0x13bbb30: ldr      x8, [x19, #0x38]','0x13bbb44: blr      x9')),
        'scene_wrapper_calls_unity_build_index': '#0x27903b8' in methods['ScenesManager','LoadScene'] and rv[0x27903b8]['signature']=='public static void LoadScene(int sceneBuildIndex) { }',
        'normal_setup_reads_current_not_instance_copy':all(s in setup for s in
            ('ldrb     w9, [x8, #0x30]','add      x8, x8, #0x2c','add      x8, x8, #0x24','ldr      w0, [x8]')),
        'manager_start_calls_map_loader': '0x14f3460: bl       #0x14f3b14' in methods['GP_Manager','Start'],
        'normal_terrain_resource_uses_stage_index': all(s in methods['GP_Spawner','LoadPlayer'] for s in
            ('0x14f3d64: bl       #0x14f0da0','0x14f3d80: bl       #0x21033cc','0x14f3d88: ldr      x8, [x8, #0xfa0]',
             '0x14f3e04: bl       #0x174a654','0x14f3e60: bl       #0x173efb4','0x14f3e88: bl       #0x171d8c4')),
        'map_controller_passes_setup_index':all(s in start for s in
            ('0x132a84c: bl       #0x14f0da0','0x132a858: mov      w20, w0','0x132a870: mov      w0, w20','0x132a878: bl       #0x13fe86c')),
        'normal_list_field_and_index_clamp':all(s in methods['Map_Get_Datas','GetListWaves'] for s in
            ('0x13feb84: ldr      x0, [x8, #0x28]','0x13feba4: csel     w8, w8, w19, lt','0x13febac: csel     w1, wzr, w8, lt')),
        'wave_loop_instantiates_activates_in_array_order':all(s in start for s in
            ('add      x21, x20, #0x20','0x132ab40: bl       #0x174a654','0x132ab6c: bl       #0x173efb4',
             '0x132ac30: bl       #0x13fda20','0x132ac40: bl       #0x2781804','add      x26, x26, #1','add      x21, x21, #4')),
        'normal_chapter_path_is_separate':all(s in start for s in
            ('0x132aa2c: ldr      w8, [x8, #0x20]','cmp      w8, #1','0x132aa34: b.lt     #0x132ab30','0x132aa58: ldr      x8, [x8, #0x9a8]')),
        'campaign_list_store_preserved':'0x140e19c: str      x28, [x8, #0x28]' in cc,
    }
    assert all(checks.values()),checks
    out={'status':'PROVISIONAL — static APK joins, not runtime replay',
        'native_sha256':rel['native_sha256'],'dump_uncompressed_sha256':hashlib.sha256(dump.encode()).hexdigest(),
        'checks':checks,'methods':records,'slots':slots,
        'declarations':{c:decl[c] for c in ('MapController','Map_Get_Datas','GP_Setup','Stage_Datas','GameDatas','ScenesManager.Scene','FadeScreen','FadeScreen.<FadeTo>d__11')},
        'campaign_immediates':{'source':str(ccp.relative_to(ROOT)),'source_sha256':hashlib.sha256(ccp.read_bytes()).hexdigest(),
            'list_creation_and_first_three_appends':asm_range(cc,0x1406bec,0x1406d88),
            'list_field_store':asm_range(cc,0x140e194,0x140e19c),
            'rows':[{'internal_stage_index':i+1,'values':v,'literal_store_asm':spans[i]} for i,v in enumerate(values)]},
        'scope':'Resource naming join applies to GameMode0, nonbranch, ChapterCurrent0. Wave IDs/order are not enemy counts. Fade dispatch bytes/timing not decoded here.'}
    with gzip.open(audit/'scene-map-flow.json.gz','wt') as f:json.dump(out,f,ensure_ascii=False,indent=2)
    print(json.dumps(checks,indent=2));print('preserved methods:',len(records))


if __name__=='__main__':main()
