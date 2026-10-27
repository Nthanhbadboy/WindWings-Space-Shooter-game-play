#!/usr/bin/env python3
"""Join authoritative stage gates, coroutine bodies, callbacks and prefab panels."""
import csv
import gzip
import hashlib
import json
import re
from pathlib import Path
from early_ui_native import section
from ui_loader_analysis import metadata_loads
from ui_routing import direct_calls

ROOT=Path(__file__).resolve().parents[2]
SELECT={
    'DataTutorials':['get_hasTutStage1','get_hasTutStage2','get_hasTutStage3'],
    'GP_Tutorials':['Start','GameStarted','CheckRunTutorialNew','IsTutTouchSkillDone',
                    'OnDroneAppear','OnUseDroneSkill','OnTouchBurst','SetActiveBtnPause',
                    '<TutDrones>b__48_0','<TutDrones>b__48_1','<TutTalents>b__52_0'],
    'GP_Tutorials._TutDrones_d__48':['MoveNext'],
    'GP_Tutorials._TutTalents_d__52':['MoveNext'],
    'GP_Tutorials.__c__DisplayClass39_0':['<CheckRunTutorialNew>b__1'],
    'Board_Endgame':['SetupTut','_2','Continue'],
    'GP_Setup':['get_stageIndex','get_indexDrones'],
    'Board_Begin':['Start'],
    'Map_Get_Datas':['GetListWaves'],
}


def compare_after_call(asm,rva):
    """First numeric cmp after a direct call; extraction only, not emulation."""
    pattern=r'\bbl\s+#'+re.escape(rva)+r'\s*\n\s*0x[\da-f]+:\s+cmp\s+w0, #(\d+)'
    m=re.search(pattern,asm)
    if not m:raise ValueError(f'No immediate w0 compare after {rva}')
    return int(m[1])


def decode_byte_dispatch(bytes_hex,base):
    return [{'state':i,'target':hex(base+4*b)} for i,b in enumerate(bytes.fromhex(bytes_hex))]


def main():
    dp=ROOT/'reverse-engineering/il2cpp/dump.cs.gz'
    dump=gzip.open(dp,'rt').read();by_rva={};decl={}
    for block in re.split(r'(?=// Namespace:)',dump):
        cls=re.search(r'(?:class|enum) ([^ :\n]+)',block)
        if not cls:continue
        decl[cls[1]]=block
        for m in re.finditer(r'// RVA: (0x[\dA-Fa-f]+)[^\n]*\n([^\n]+)',block):
            by_rva[int(m[1],16)]={'class':cls[1],'signature':m[2].strip()}
    audit=ROOT/'reverse-engineering/raw/ui-audit'
    meta=json.load(gzip.open(audit/'metadata-index.json.gz','rt'))
    rel=json.load(gzip.open(audit/'native-relocations.json.gz','rt'));index={}
    for group,rows in meta['tables'].items():
        for row in rows:index.setdefault(row['Address'],[]).append(dict(row,group=group))
    records=[];methods={}
    for cls,names in SELECT.items():
        folder=audit/'extra-native' if cls in ('Board_Begin','GP_Setup') else ROOT/'reverse-engineering/raw/il2cpp-consts'
        p=folder/f'{cls}.asm.txt';text=p.read_text()
        inventory=json.loads(p.with_name(cls+'.json').read_text())
        for name in names:
            asm=section(text,name);methods[cls,name]=asm
            inv=next(m for m in inventory['methods'] if m['method']==name)
            assert not inv.get('size_capped'),(cls,name)
            records.append({'class':cls,'method':name,'source':str(p.relative_to(ROOT)),
                            'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                            'asm':asm,'export_inventory':inv,'calls':direct_calls(asm,by_rva),
                            'metadata_loads':metadata_loads(asm,rel['relocations'],index)})
    a=methods['DataTutorials','get_hasTutStage2'];b=methods['DataTutorials','get_hasTutStage3']
    assert compare_after_call(a,'0x14f4a14')==1
    assert compare_after_call(a,'0x14f0da0')==1
    assert compare_after_call(b,'0x14f0da0')==2
    check=methods['GP_Tutorials','CheckRunTutorialNew']
    cb=methods['GP_Tutorials.__c__DisplayClass39_0','<CheckRunTutorialNew>b__1']
    checks={
        'stage3_gate_is_touch_flag_not_index_tutorial':'#0x14fa7b0' in b and '#0x14f4a14' not in b,
        'stage2_selects_drone_panel_and_delay':all(x in check for x in
            ('ldr      x1, [x19, #0x68]','fmov     s0, #2.00000000','#0x14fab88')),
        'stage3_selects_talent_panel_and_delay':all(x in check for x in
            ('ldr      x21, [x19, #0x70]','fmov     s0, #3.00000000','#0x14fac18')),
        'stage3_no_talent_bypass_present':all(x in check for x in
            ('#0x1397438','cmn      w0, #1','b.eq     #0x14fa424','0x14fa4a0: b        #0x13f1a04')),
        'display_number_is_internal_plus_one':all(x in methods['Board_Begin','Start'] for x in
            ('0x15dcfb8: bl       #0x14f0da0','0x15dcfc4: add      w9, w0, #1','0x15dcff8: bl       #0x1fed434')),
        'drone_wait_for_appear_flag':'[x0, #0x94]' in methods['GP_Tutorials','<TutDrones>b__48_0'],
        'drone_wait_for_skill_flag':'[x0, #0x96]' in methods['GP_Tutorials','<TutDrones>b__48_1'],
        'talent_wait_for_touch_flag':'[x0, #0x97]' in methods['GP_Tutorials','<TutTalents>b__52_0'],
        'talent_completion_conditionally_increments_index':all(x in cb for x in
            ('cmp      w0, #2','ldr      w8, [x8, #0x24]','cmp      w8, #2','add      w0, w0, #1','#0x14f9f84')),
    }
    assert all(checks.values()),checks
    lp=ROOT/'reverse-engineering/raw/ui/GP_Tutorials__1902.json.gz'
    layout=json.load(gzip.open(lp,'rt'))
    panels=[p for p in layout['linked_panels'] if p['field'] in ('tutobjUseDroneSkill','tutobjTouchSkill','coverObject')]
    tp=audit/'tutorial-texts.csv'
    texts=[r for r in csv.DictReader(tp.open()) if r['owner_field'] in ('tutobjUseDroneSkill','tutobjTouchSkill')]
    stage_fields=[]
    for name in ('tutobjUseDroneSkill','tutobjTouchSkill','btnSkillDrone','btnSkillDrone2','btnTalent','coverObject'):
        m=re.search(r'(?m)^\s*(?:private|public|protected) (\w+) '+name+r'; // (0x[\da-fA-F]+)',decl['GP_Tutorials'])
        assert m,name
        stage_fields.append({'name':name,'type':m[1],'offset':m[2]})
    relevant_decl={k:decl[k] for k in ('GP_Tutorials','GP_Setup','GP_Datas','GP_Controller','Stage_Datas','Board_Begin',
                                  'GP_Tutorials.<TutDrones>d__48','GP_Tutorials.<TutTalents>d__52')}
    out={'status':'PROVISIONAL — static APK evidence, not runtime replay','checks':checks,
         'native_sha256':rel['native_sha256'],'dump_uncompressed_sha256':hashlib.sha256(dump.encode()).hexdigest(),
         'methods':records,'declarations':relevant_decl,
         'panel_source':{'source':str(lp.relative_to(ROOT)),'sha256':hashlib.sha256(lp.read_bytes()).hexdigest(),
                         'serialized_file':layout['serialized_file'],'fields':stage_fields,'panels':panels},
         'text_source':{'source':str(tp.relative_to(ROOT)),'sha256':hashlib.sha256(tp.read_bytes()).hexdigest(),'rows':texts},
         'stage_gates':[
             {'display_stage':2,'internal_stage_index':1,'tutorial_index_required':1,'panel':'tutobjUseDroneSkill','start_delay_scaled_seconds':2},
             {'display_stage':3,'internal_stage_index':2,'done_key':'TUT_TOUCH_SKILL','done_value':1,'requires_talent_index_not_minus_one':True,'panel':'tutobjTouchSkill','start_delay_scaled_seconds':3}],
         'warning':'Displayed-number join applies to normal/non-branch label path. EventState integer callbacks are not EventID enum. Scaled delays are not wall-clock seconds.'}
    rp=audit/'stage23-rodata.json'
    if rp.exists():
        ro=json.loads(rp.read_text());assert ro['native_sha256']==rel['native_sha256']
        assert decode_byte_dispatch(ro['drone_dispatch']['bytes_hex'],int(ro['drone_dispatch']['branch_base'],16))==ro['drone_dispatch']['entries']
        out['rodata']=ro
    else:out['rodata_status']='PENDING native dispatch bytes; no claim of verified drone state-order'
    dest=audit/'stage23-ui-flow.json.gz'
    with gzip.open(dest,'wt') as f:json.dump(out,f,ensure_ascii=False,indent=2)
    print(json.dumps(checks,indent=2));print('preserved methods:',len(records))


if __name__=='__main__':main()
