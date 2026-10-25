#!/usr/bin/env python3
"""Static APK evidence for trigger -> spawn-ended -> endgame, not a runtime replay."""
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
    'Call_Point':['OnEnable','FixedUpdate'],
    'Spawner':['Awake','SetSpawnEndedEventCallback'],
    'Path_Spawner':['OnSpawn'],
    'Path_Spawner._SpawnEnemies_d__1':['MoveNext'],
    'Waypoints_Spawner._SpawnEnemies_d__1':['MoveNext'],
    'Wave':['SetLastWave','CheckSpawnEnded'],
    'Wave._CheckSpawnEnded_d__7':['MoveNext'],
    'Wave.__c__DisplayClass7_0':['<CheckSpawnEnded>b__0','<CheckSpawnEnded>b__1',
                               '<CheckSpawnEnded>b__2','<CheckSpawnEnded>b__3'],
    'GP_Manager':['Start','<Start>b__11_7','<Start>b__11_11'],
    'GP_Endgame':['StartCheckEndgame','MoveOutPlayer'],
    'GP_Endgame._CheckEndgame_d__4':['MoveNext'],
    'GP_Endgame.__c__DisplayClass4_0':['<CheckEndgame>b__0'],
    'Board_Endgame':['GetMissionCompleted'],
}


def main():
    audit=ROOT/'reverse-engineering/raw/ui-audit'
    dump=gzip.open(ROOT/'reverse-engineering/il2cpp/dump.cs.gz','rt').read()
    decl={};rv={};index={};records=[];methods={}
    for b in re.split(r'(?=// Namespace:)',dump):
        c=re.search(r'(?:class|enum) ([^ :\n]+)',b)
        if not c:continue
        decl[c[1]]=b
        for m in re.finditer(r'// RVA: (0x[\dA-Fa-f]+)[^\n]*\n([^\n]+)',b):
            rv[int(m[1],16)]={'class':c[1],'signature':m[2].strip()}
    rel=json.load(gzip.open(audit/'native-relocations.json.gz','rt'))
    meta=json.load(gzip.open(audit/'metadata-index.json.gz','rt'))
    for group,rows in meta['tables'].items():
        for row in rows:index.setdefault(row['Address'],[]).append(dict(row,group=group))
    for cls,names in SELECT.items():
        folder=ROOT/'reverse-engineering/raw/il2cpp-consts' if cls=='Board_Endgame' else audit/'extra-native'
        p=folder/f'{cls}.asm.txt';inventory=json.loads((folder/f'{cls}.json').read_text())
        for name in names:
            asm=section(p.read_text(),name);methods[cls,name]=asm
            inv=next(m for m in inventory['methods'] if m['method']==name)
            assert not inv.get('size_capped'),(cls,name)
            records.append({'class':cls,'method':name,'asm':asm,'inventory':inv,
                'source':str(p.relative_to(ROOT)),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                'calls':direct_calls(asm,rv),'metadata_loads':metadata_loads(asm,rel['relocations'],index)})
    wave=methods['Wave._CheckSpawnEnded_d__7','MoveNext']
    end=methods['GP_Endgame._CheckEndgame_d__4','MoveNext']
    path=methods['Path_Spawner._SpawnEnemies_d__1','MoveNext']
    manager=methods['GP_Manager','Start']
    def has(asm,*parts):return all(p in asm for p in parts)
    trigger=methods['Call_Point','FixedUpdate']
    checks={
        'trigger_is_once_per_enable_and_blocks_endgame':has(trigger,
            'ldrb     w8, [x19, #0x40]','0x1465aac: cbnz     w8, #0x1465ce0',
            '0x1465ae4: cmp      w8, #3','0x1465ae8: b.eq     #0x1465ce0'),
        'trigger_checks_scroll_flag_and_y_threshold':has(trigger,
            'ldrb     w8, [x8, #0x78]','0x1465b08: cbz      w8, #0x1465ce0',
            '0x1465c9c: ldr      s0, [x8, #0x40]','0x1465ca0: fcmp     s1, s0',
            '0x1465cb0: strb     w9, [x19, #0x40]','0x1465cdc: br       x2'),
        'set_last_wave_starts_check_coroutine':has(methods['Wave','SetLastWave'],'#0x1417da4','#0x278276c'),
        'wave_gets_active_children_spawners':has(wave,'mov      w1, wzr','0x1418268: bl       #0x16f5a40','0x1418288: str      w9, [x8, #0x10]'),
        'wait_predicate_is_count_below_one':has(methods['Wave.__c__DisplayClass7_0','<CheckSpawnEnded>b__0'],
            'ldr      w8, [x0, #0x10]','cmp      w8, #1','cset     w0, lt'),
        'normal_callbacks_decrement_count':all(has(methods['Wave.__c__DisplayClass7_0',n],
            'sub      w8, w8, #1','str      w8, [x0, #0x10]') for n in ('<CheckSpawnEnded>b__1','<CheckSpawnEnded>b__3')),
        'normal_branch_distinguishes_end_and_start_markers':has(wave,
            '0x14182fc: cmp      w8, #5','0x1418304: cmp      w8, #6','0x1418394: str      x22, [x28, #0x28]'),
        'wait_then_wave_ended_then_last_spawn_ended':has(wave,'0x14183f4: bl       #0x2786670',
            'mov      w1, #0x4a','0x1418450: bl       #0x1434cb4','0x1418460: cbz      w8, #0x141847c',
            'mov      w1, #0x49','0x1418470: bl       #0x1434ce4'),
        'path_uses_number_and_scaled_rate_then_ended':has(path,'ldr      w10, [x9, #0x44]',
            '0x146653c: b.ge     #0x1466660','0x1466678: blr      x9','ldr      s8, [x8, #0x48]','#0x2786508'),
        'manager_subscribes_spawn_ended_event':has(manager,'0x14f393c: ldr      x24, [x24, #0xf50]',
            '0x14f3a68: ldr      x2, [x24]','0x14f3a7c: mov      w1, #0x49','#0x1434c84'),
        'spawn_ended_handler_starts_endgame_poll':has(methods['GP_Manager','<Start>b__11_7'],
            'ldr      x20, [x19, #0x50]','0x14f6188: b        #0x14f052c'),
        'poll_requires_empty_active_list_and_playing':has(end,'0x14f1510: ldr      x8, [x0, #0x70]',
            '0x14f1518: ldr      w8, [x8, #0x18]','0x14f151c: cbnz     w8, #0x14f1714',
            '0x14f1554: cmp      w8, #1','0x14f1558: b.ne     #0x14f1714'),
        'normal_outcome_uses_mission_result_not_all_kills_equality':has(end,
            '0x14f1818: ldr      w21, [x8, #0x1c]','0x14f182c: ldr      w22, [x0, #0x58]',
            '#0x12734f8','0x14f185c: mvn      w9, w0','0x14f1860: lsr      w9, w9, #0x1f'),
        'completion_waits_two_scaled_seconds_before_transition_callback':has(end,
            '0x14f19dc: fmov     s0, #2.00000000','0x14f19e8: bl       #0x2786508',
            '0x14f16cc: blr      x9','0x14f170c: bl       #0x14f0768'),
        'outcome_bool_reaches_open_board':has(methods['GP_Endgame.__c__DisplayClass4_0','<CheckEndgame>b__0'],
            'ldrb     w1, [x0, #0x10]','#0x14f0830'),
    }
    assert all(checks.values()),checks
    slots={s:{'effective_address':rel['relocations'][s],'records':index[int(rel['relocations'][s],16)]}
           for s in ('0x2ae7908','0x2ae7910','0x2ae6090','0x2ae8f50','0x2ae9030','0x2ae1a20','0x2ae1708')}
    for slot,rva in [('0x2ae8f50',0x14f6104),('0x2ae9030',0x14f6190)]:
        assert any(r.get('MethodAddress')==rva for r in slots[slot]['records'])
    classes=('Call_Point','Call_Data','Spawner','Wave','Wave.<>c__DisplayClass7_0',
             'Wave.<CheckSpawnEnded>d__7','GP_Datas','GP_Manager','GP_Endgame',
             'GP_Endgame.<>c__DisplayClass4_0','SpawnTypes','EventID','GP_States','GameState')
    out={'status':'PROVISIONAL — static APK evidence, no measured gameplay timing',
         'native_sha256':rel['native_sha256'],'dump_uncompressed_sha256':hashlib.sha256(dump.encode()).hexdigest(),
         'methods':records,'checks':checks,'slots':slots,'declarations':{c:decl[c] for c in classes},
         'warning':'Spawn-ended counter is not an enemy kill counter. Actual wave prefab counts, live enemy-list maintenance, mission thresholds and runtime chronology remain separate.'}
    with gzip.open(audit/'wave-spawn-flow.json.gz','wt') as f:json.dump(out,f,ensure_ascii=False,indent=2)
    print(json.dumps(checks,indent=2));print('preserved methods:',len(records))


if __name__=='__main__':main()
