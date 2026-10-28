#!/usr/bin/env python3
"""Static conditional false-result witness. Not whole-program execution/replay."""
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
 'GP_Endgame':['StartCheckEndgame','CheckEndgame','MoveOutPlayer','MovePlayer',
               'FixBugMovePlayerTimeOut','OpenBoardVictory','<VictoryNow>b__5_0'],
 'GP_Endgame._CheckEndgame_d__4':['MoveNext'],
 'GP_Endgame.__c__DisplayClass4_0':['<CheckEndgame>b__0'],
 'GP_Endgame._MovePlayer_d__10':['MoveNext'],
 'GP_Endgame._FixBugMovePlayerTimeOut_d__11':['MoveNext'],
 'GP_Manager':['<Start>b__11_7','<Start>b__11_11'],
 'Stage_Datas':['set_StageTarget'],
 'Board_Endgame':['SetMissions'],
}


def conditional_result(tier,health):
    """GameMode0 nonbranch after empty-list/Playing gate, valid components.

    Mirrors exact health==0 comparison, not <=0. Excludes NaN and state races.
    """
    assert -1<=tier<=2
    return tier>=0 and health!=0


def conditional_target(mode,stage,target,zone,max_stage):
    """At OpenBoardVictory entry; deliberately NO victory parameter.

    Stable getters, small nonnegative ints (no overflow), valid max/target.
    Does not claim those inputs are reachable in an actual playthrough.
    """
    assert 0<=stage<=max_stage and 0<=target<=max_stage and zone>=0
    return min(target+1,max_stage) if mode==0 and stage==target and target<zone*10+9 else target


def build():
    base=ROOT/'reverse-engineering/raw/ui-audit';dump_path=ROOT/'reverse-engineering/il2cpp/dump.cs.gz'
    dump=gzip.open(dump_path,'rt').read();decl={};rv={};ix={};records=[];methods={}
    for b in re.split(r'(?=// Namespace:)',dump):
        c=re.search(r'(?:class|enum|interface) ([^ :\n]+)',b)
        if not c:continue
        decl[c[1]]=b
        for m in re.finditer(r'// RVA: (0x[\dA-Fa-f]+)[^\n]*\n([^\n]+)',b):rv[int(m[1],16)]={'class':c[1],'signature':m[2].strip()}
    reloc_path=base/'native-relocations.json.gz';meta_path=base/'metadata-index.json.gz'
    relocation_data=json.load(gzip.open(reloc_path,'rt'));rel=relocation_data['relocations']
    ro_path=base/'endgame-rodata.json';ro=json.loads(ro_path.read_text())
    assert ro['native_sha256']==relocation_data['native_sha256']
    for group,rows in json.load(gzip.open(meta_path,'rt'))['tables'].items():
        for row in rows:ix.setdefault(row['Address'],[]).append(dict(row,group=group))
    sources={p for p in (dump_path,reloc_path,meta_path,ro_path)}
    for cls,names in SELECT.items():
        folder=ROOT/'reverse-engineering/raw/il2cpp-consts' if cls=='Board_Endgame' else base/'extra-native'
        p=folder/f'{cls}.asm.txt';inv_path=folder/f'{cls}.json';sources.update((p,inv_path))
        inv=json.loads(inv_path.read_text())
        for name in names:
            asm=section(p.read_text(),name);methods[cls,name]=asm
            item=next(m for m in inv['methods'] if m['method']==name);assert not item.get('size_capped')
            records.append({'class':cls,'method':name,'asm':asm,'inventory':item,'source':str(p.relative_to(ROOT)),
                            'calls':direct_calls(asm,rv),'metadata_loads':metadata_loads(asm,rel,ix)})
    def has(cls,name,*parts):return all(p in methods[cls,name] for p in parts)
    check='GP_Endgame._CheckEndgame_d__4';move='GP_Endgame._MovePlayer_d__10';fix='GP_Endgame._FixBugMovePlayerTimeOut_d__11'
    dispatch=ro['move_player_dispatch'];table=bytes.fromhex(dispatch['bytes_hex'])
    checks={
      'all_4_move_states_resolved_from_rodata':dispatch['table_va']=='0x77a13a' and dispatch['branch_base']=='0x14f1c00' and len(table)==4 and
          dispatch['entries']==[{'state':i,'target':hex(0x14f1c00+4*v)} for i,v in enumerate(table)] and
          [e['target'] for e in dispatch['entries']]==['0x14f1c00','0x14f1c58','0x14f1cb4','0x14f1e34'],
      'move_dispatch_asm_matches_recovered_table':has(move,'MoveNext','0x14f1bdc: cmp      w8, #3','0x14f1bec: add      x9, x9, #0x13a','0x14f1bf0: adr      x10, #0x14f1c00','0x14f1bf8: add      x10, x10, x11, lsl #2'),
      'movement_float_bytes_decode_and_phase_targets_are_spatial':all(struct.unpack('<f',bytes.fromhex(f['bytes_hex']))[0]==f['float32'] for f in ro['movement_floats']) and
          has(move,'MoveNext','0x14f1c9c: fmov     s0, #-2.00000000','0x14f1e78: mov      w8, #0x41700000','0x14f1d04: b.mi     #0x14f1e44','0x14f1ed0: b.mi     #0x14f200c'),
      'manager_passes_endgame_action_to_start_check':has('GP_Manager','<Start>b__11_7','0x14f6178: mov      x1, x21','0x14f6188: b        #0x14f052c'),
      'gate_active_list_empty_and_playing1':has(check,'MoveNext','0x14f1510: ldr      x8, [x0, #0x70]','0x14f151c: cbnz     w8, #0x14f1714','0x14f1554: cmp      w8, #1','0x14f1558: b.ne     #0x14f1714'),
      'closure_default_true_then_nonbranch_kill_score':has(check,'MoveNext','0x14f15fc: strb     w9, [x8, #0x10]','0x14f1624: cbz      w9, #0x14f1750','0x14f1788: cbz      w8, #0x14f17fc','0x14f1818: ldr      w21, [x8, #0x1c]','0x14f182c: ldr      w22, [x0, #0x58]','0x14f1850: bl       #0x12734f8','0x14f185c: mvn      w9, w0','0x14f1860: lsr      w9, w9, #0x1f','0x14f1864: strb     w9, [x8, #0x10]'),
      'health_slot1_zero_forces_false_then_joins_summary':has(check,'MoveNext','0x14f18d4: add      w9, w9, #1','0x14f18e8: blr      x8','0x14f18ec: fcmp     s0, #0.0','0x14f18f0: b.ne     #0x14f1904','0x14f18fc: strb     wzr, [x8, #0x10]','0x14f1900: b        #0x14f1984'),
      'health_nonzero_does_not_filter_false_result':has(check,'MoveNext','0x14f1980: blr      x8','0x14f19c0: ldrb     w1, [x8, #0x10]','0x14f19c8: bl       #0x14d49fc'),
      'delay2_is_scaled_and_resume_invokes_endgame_action':has(check,'MoveNext','0x14f19dc: fmov     s0, #2.00000000','0x14f19e8: bl       #0x2786508','0x14f14bc: b.eq     #0x14f16b0','0x14f16cc: blr      x9'),
      'same_false_or_true_closure_bound_to_moveout':has(check,'MoveNext','0x14f16d4: ldr      x22, [x19, #0x30]','0x14f16ec: mov      x1, x22','0x14f16fc: bl       #0x20bc330','0x14f1708: mov      x1, x21','0x14f170c: bl       #0x14f0768'),
      'closure_forwards_bool_without_gate_to_openboard':has('GP_Endgame.__c__DisplayClass4_0','<CheckEndgame>b__0','0x14f13b8: ldrb     w1, [x0, #0x10]','0x14f13c4: b        #0x14f0830'),
      'moveout_restores_timescale_and_starts_move_coroutine':has('GP_Endgame','MoveOutPlayer','0x14f0780: bl       #0x2786ed8','0x14f07a0: bl       #0x14f07c4','0x14f07b0: bl       #0x278276c'),
      'move_factory_stores_same_callback':has('GP_Endgame','MovePlayer','0x14f07e0: mov      x19, x1','0x14f0818: stp      x20, x19, [x21, #0x20]'),
      'move_starts_watchdog_with_callback_before_initial1_scaled_wait':has(move,'MoveNext','0x14f1c0c: ldr      x1, [x19, #0x28]','0x14f1c14: bl       #0x14f127c','0x14f1c24: bl       #0x278276c','0x14f1c38: fmov     s0, #1.00000000','0x14f1c44: bl       #0x2786508'),
      'move_normal_completion_invokes_same_callback':has(move,'MoveNext','0x14f200c: ldr      x8, [x19, #0x28]','0x14f2020: blr      x9'),
      'watchdog_4_unscaled_invokes_callback_then_stops_move':has(fix,'MoveNext','0x14f1ae0: fmov     s0, #4.00000000','0x14f1aec: bl       #0x2786604','0x14f1b1c: blr      x9','0x14f1b24: ldr      x1, [x20, #0x38]','0x14f1b34: bl       #0x27829d8'),
      'openboard_updates_target_before_consuming_victory':has('GP_Endgame','OpenBoardVictory','0x14f09b4: bl       #0x12bac5c','0x14f09c4: and      w24, w20, #1','0x14f09e4: strb     w24, [x8]'),
      'target_setter_min_maxstage_and_pref_write':has('Stage_Datas','set_StageTarget','0x12baccc: ldr      w9, [x8, #4]','0x12bacd4: csel     w19, w19, w9, gt','0x12bacd8: str      w19, [x8, #0x3c]','0x12bad04: b        #0x13f1a04'),
      'force_victory_callback_separately_passes_true':has('GP_Endgame','<VictoryNow>b__5_0','0x14f1318: mov      w1, #1','0x14f131c: b        #0x14f0830'),
      'endgame_action_sets_state3_not_victory_override':has('GP_Manager','<Start>b__11_11','0x14f6260: mov      w9, #3','0x14f6268: str      w9, [x8]'),
      'false_board_skips_normal_scoring_entry':has('Board_Endgame','SetMissions','0x127287c: ldrb     w8, [x8]','0x1272880: cbz      w8, #0x127289c','0x12728c4: b        #0x1272c90'),
    }
    assert all(checks.values()),checks
    return {'status':'PROVISIONAL conditional static reachability; no runtime replay or complete caller census',
            'scope':'GameMode0, IsBranchfalse, LevelCurrent0, valid components, stable getters/coroutines alive',
            'checks':checks,'methods':records,'move_rodata':ro,
            'sources':[{'path':str(p.relative_to(ROOT)),'hash_bytes':'gzip-decompressed' if p.suffix=='.gz' else 'file',
                        'sha256':hashlib.sha256(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes()).hexdigest()} for p in sorted(sources)],
            'declarations':{c:decl[c] for c in ('IHealth','IPlayer','GP_Datas','GP_States','GameState','Stage_Datas','GP_Endgame.<>c__DisplayClass4_0')},
            'limitations':['external/interface calls not emulated','event handlers can affect runtime state','watchdog assumes owner survives and no cancellation','input witness is not demonstrated gameplay','not ordinary mid-wave player-death/reborn path']}

if __name__=='__main__':
    d=build();p=ROOT/'reverse-engineering/raw/endgame-missions/false-result-reachability.json.gz'
    p.write_bytes(gzip.compress(json.dumps(d,indent=2).encode(),mtime=0));print(len(d['methods']),'methods;',len(d['checks']),'checks')
