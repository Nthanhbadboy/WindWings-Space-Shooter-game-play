#!/usr/bin/env python3
"""Preserve static event/list and mission-array joins. No live-count inference."""
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
from early_ui_native import section
from ui_loader_analysis import metadata_loads
from ui_routing import direct_calls

ROOT=Path(__file__).resolve().parents[2]
SELECT={
 'GP_Datas':['ResetAlls','<ResetAlls>b__60_0','<ResetAlls>b__60_1','<ResetAlls>b__60_2'],
 'Enemy_Controller':['OnDieWhenZeroHp','OnDieWhenHitPlayer','OnMoveCompleted'],
 'Enemy_Destroy':['Destroy','Pool','OnDestroyByZeroHp','OnDestroyWhenHitPlayer','OnMoveCompleted','DestroyNoEvents'],
 'Board_Endgame':['GetMissionCompleted'],
 'Player_Get_Datas':['GetKillPercentMissionComplete'],
}
SLOTS={0:'0x2ae8b88',1:'0x2ae8b80',2:'0x2ae8b78'}


def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]


def normal_mission_result(count,max_count,coefficients):
    """Restricted nonbranch finite nonnegative-count model, not full ARM emulator."""
    assert count>=0 and max_count>=0
    return -1+sum(count>=int(f32(f32(max_count)*p)) for p in coefficients)


def build():
    audit=ROOT/'reverse-engineering/raw/ui-audit';dump=gzip.open(ROOT/'reverse-engineering/il2cpp/dump.cs.gz','rt').read()
    decl={};rv={};ix={};methods={};records=[]
    for b in re.split(r'(?=// Namespace:)',dump):
        c=re.search(r'(?:class|enum) ([^ :\n]+)',b)
        if not c:continue
        decl[c[1]]=b
        for m in re.finditer(r'// RVA: (0x[\dA-Fa-f]+)[^\n]*\n([^\n]+)',b):rv[int(m[1],16)]={'class':c[1],'signature':m[2].strip()}
    rel=json.load(gzip.open(audit/'native-relocations.json.gz','rt'))['relocations']
    for group,rows in json.load(gzip.open(audit/'metadata-index.json.gz','rt'))['tables'].items():
        for row in rows:ix.setdefault(row['Address'],[]).append(dict(row,group=group))
    for cls,names in SELECT.items():
        folder=ROOT/'reverse-engineering/raw/il2cpp-consts' if cls in ('Board_Endgame','Player_Get_Datas') else audit/'extra-native'
        p=folder/f'{cls}.asm.txt';inventory=json.loads((folder/f'{cls}.json').read_text())
        for name in names:
            asm=section(p.read_text(),name);methods[cls,name]=asm
            inv=next(m for m in inventory['methods'] if m['method']==name);assert not inv.get('size_capped')
            records.append({'class':cls,'method':name,'asm':asm,'inventory':inv,'source':str(p.relative_to(ROOT)),
                            'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'calls':direct_calls(asm,rv),'metadata_loads':metadata_loads(asm,rel,ix)})
    fields=json.loads((ROOT/'reverse-engineering/il2cpp/field-defaults.json').read_text())['fields'];arrays={}
    for mode,slot in SLOTS.items():
        row=next(r for r in ix[int(rel[slot],16)] if r.get('Name','').startswith('Field$'))
        key=row['Name'][6:];raw=fields[key];blob=bytes.fromhex(raw['raw'])[:12]
        assert hashlib.sha256(blob).hexdigest().upper()==key.rsplit('.',1)[1]
        arrays[str(mode)]={'slot':slot,'field':key,'metadata':row,'field_default':raw,'bytes_hex':blob.hex(),'float32':list(struct.unpack('<3f',blob))}
    def has(cls,name,*pieces):return all(p in methods[cls,name] for p in pieces)
    checks={
      'reset_subscribes_spawn78_pool79_death19':has('GP_Datas','ResetAlls','0x14cfd60: mov      w1, #0x4e','0x14cfd90: mov      w1, #0x4f','0x14cfdc0: mov      w1, #0x13'),
      'spawn_callback_contains_then_adds_to_active_list':has('GP_Datas','<ResetAlls>b__60_0','ldr      x0, [x20, #0x70]','#0x1bd81e0','0x14d00ec: tbnz','0x14d0144: str      w9, [x0, #0x18]','0x14d0148: str      x19, [x8, #0x20]'),
      'pool_callback_contains_then_removes_from_active_list':has('GP_Datas','<ResetAlls>b__60_1','ldr      x0, [x20, #0x70]','#0x1bd81e0','0x14d0200: tbz','#0x1bd91a0'),
      'pool_emits79_before_pool_manager':has('Enemy_Destroy','Pool','0x1584c40: mov      w1, #0x4f','0x1584c4c: bl       #0x1434cb4','0x1584d28: b        #0x123acd0'),
      'destroy_all_types_tail_pool':has('Enemy_Destroy','Destroy','cmp      w1, #1','cbnz     w1, #0x15815c8','0x15815d0: b        #0x1584bf0'),
      'movement_completed_requests_done2':has('Enemy_Controller','OnMoveCompleted','mov      w1, #2','br       x3'),
      'base_destroy_movement_hook_returns':has('Enemy_Destroy','OnMoveCompleted','0x1584bec: ret'),
      'zero_hp_and_hit_both_emit19_then79':all(has('Enemy_Destroy',name,'mov      w1, #0x13','mov      w1, #0x4f') for name in ('OnDestroyByZeroHp','OnDestroyWhenHitPlayer')),
      'death_callback_increments_kill_field':has('GP_Datas','<ResetAlls>b__60_2','0x14d0638: ldr      w9, [x8, #0x1c]','0x14d0640: str      w1, [x8, #0x1c]'),
      'normal_mission_calls_kill_percent_table':has('Board_Endgame','GetMissionCompleted','0x1273650: bl       #0x14e5618','0x1273738: fmul','0x127373c: fcvtzs','0x1273748: cmp      w26, w8','0x1273754: add      w8, w8, #1','0x1273760: cmp      x27, #0xb'),
      'mode_selects0_then1_then_fallback':has('Player_Get_Datas','GetKillPercentMissionComplete','0x14e5694: cmp      w19, #1','0x14e5698: csel     x8, x21, x20, eq','0x14e569c: cmp      w19, #0','0x14e56a4: csel     x19, x22, x8, eq','mov      w1, #3','#0x205b07c'),
      'all_3_array_hashes_match_field_names':len(arrays)==3,
    }
    assert all(checks.values()),checks
    return {'status':'PROVISIONAL — base native paths; no runtime replay, no stage kill denominator',
            'checks':checks,'methods':records,'normal_mission_arrays':arrays,
            'declarations':{k:decl[k] for k in ('GP_Datas','EventID','DestroyType','Enemy_Destroy','GameDatas','Stage_Datas')}}


if __name__=='__main__':
    d=build()
    with gzip.open(ROOT/'reverse-engineering/raw/ui-audit/enemy-exit-missions.json.gz','wt') as f:json.dump(d,f,indent=2)
    print(len(d['methods']),'methods;',len(d['checks']),'checks',d['checks'])
