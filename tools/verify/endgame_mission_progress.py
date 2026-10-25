#!/usr/bin/env python3
"""Static APK joins: result tiers -> mission rows / preference writes / Continue.

Restricted to ordinary nonbranch campaign missions (LevelCurrent0). Not a
runtime replay, disk-flush guarantee, or analysis of deferred Premium flows.
"""
import base64
import gzip
import hashlib
import json
from pathlib import Path
import re
from early_ui_native import section
from ui_loader_analysis import metadata_loads
from ui_routing import direct_calls

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'reverse-engineering/raw'
SELECT={
 'Board_Endgame':['Init','SetMissions','RunMissions','<SetMissions>b__158_0',
                 'OnPressedButtonContinue','<OnPressedButtonContinue>b__103_0','Continue','SkipUnbox'],
 'Board_Endgame._RunMissions_d__162':['MoveNext'],
 'GP_Endgame':['OpenBoardVictory'],
 'Stage_Get_Datas':['IsMissionCompleted'],
 'Stage_Datas':['GetStarStageMaster','SetStarStageMaster'],
 'Stage_Mission':['InitMission','ClearMission'],
 'GameDatas':['get_StarCount','set_StarCount'],
 'PlayerPreferences':['SetInt'],
}
CONSTS={'Board_Endgame','Board_Endgame._RunMissions_d__162','Stage_Get_Datas'}


def normal_progress(saved,result):
    """Restricted state model AFTER entering normal SetMissions scoring branch.

    Does not model incoming-defeat early exit, special missions3/4, rewards,
    user-input interleaving, corrupt saves or animation graph state.
    """
    assert 0<=saved<=3 and -1<=result<=2
    old_flags=[saved>i for i in range(3)]
    newly_completed=[i for i,old in enumerate(old_flags) if not old and i<=result]
    return {'old_flags':old_flags,'new_rows':newly_completed,
            'saved_after':max(saved,result+1),'global_star_delta':len(newly_completed)}


def build():
    audit=RAW/'ui-audit';dump=gzip.open(ROOT/'reverse-engineering/il2cpp/dump.cs.gz','rt').read();decl={};rv={};ix={};methods={};records=[]
    for b in re.split(r'(?=// Namespace:)',dump):
        c=re.search(r'(?:class|enum) ([^ :\n]+)',b)
        if not c:continue
        decl[c[1]]=b
        for m in re.finditer(r'// RVA: (0x[\dA-Fa-f]+)[^\n]*\n([^\n]+)',b):rv[int(m[1],16)]={'class':c[1],'signature':m[2].strip()}
    rel=json.load(gzip.open(audit/'native-relocations.json.gz','rt'))['relocations']
    for group,rows in json.load(gzip.open(audit/'metadata-index.json.gz','rt'))['tables'].items():
        for row in rows:ix.setdefault(row['Address'],[]).append(dict(row,group=group))
    for cls,names in SELECT.items():
        folder=RAW/'il2cpp-consts' if cls in CONSTS else audit/'extra-native'
        p=folder/f'{cls}.asm.txt';inventory=json.loads((folder/f'{cls}.json').read_text())
        for name in names:
            asm=section(p.read_text(),name);methods[cls,name]=asm
            inv=next(m for m in inventory['methods'] if m['method']==name);assert not inv.get('size_capped')
            records.append({'class':cls,'method':name,'asm':asm,'inventory':inv,'source':str(p.relative_to(ROOT)),
                            'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'calls':direct_calls(asm,rv),'metadata_loads':metadata_loads(asm,rel,ix)})
    index_path=RAW/'endgame-missions/index.json';index=json.loads(index_path.read_text())
    entry=next(e for e in index['entries'] if e['container_key']=='boards/board_endgame')
    p=RAW/'endgame-missions'/entry['export'];prefab=json.load(gzip.open(p,'rt'))
    components={};gos={}
    for n in prefab['nodes']:
        gos[n['gameobject']['serialized_file'],n['gameobject']['path_id']]=n
        for c in n['components']:
            components[c['serialized_file'],c['path_id']]=(n,c)
            if c['type']=='MonoBehaviour':
                assert hashlib.sha256(base64.b64decode(c['bytes_base64'])).hexdigest()==c['bytes_sha256']
    boards=[(n,c) for n in prefab['nodes'] for c in n['components'] if c.get('script_class')=='Board_Endgame']
    assert len(boards)==1;node,board=boards[0];tree=board['tree'];sf=board['serialized_file']
    def component(ptr):
        assert ptr['m_FileID']==0
        return components[sf,ptr['m_PathID']]
    def go(ptr):
        assert ptr['m_FileID']==0
        return gos[sf,ptr['m_PathID']]
    rows=[]
    for i,ptr in enumerate(tree['listMissions']):
        n,c=component(ptr);assert c['script_class']=='Stage_Mission'
        fields={}
        for name in ('anim','textInfo','textBonus'):
            target,comp=component(c['tree'][name]);fields[name]={'path':target['path'],'type':comp.get('script_class',comp['type']),
                                                             'serialized_file':comp['serialized_file'],'path_id':comp['path_id']}
        rows.append({'index':i,'path':n['path'],'component_path_id':c['path_id'],'fields':fields,'colors':c['tree']['colors']})
    btn=go(tree['btnContinue']);events=[c for c in btn['components'] if c.get('script_class')=='ButtonEvents'];assert len(events)==1
    calls=events[0]['tree']['eventClick']['m_PersistentCalls']['m_Calls']
    assert len(calls)==1
    target,button_board=component(calls[0]['m_Target']);assert button_board['path_id']==board['path_id']
    def has(cls,name,*parts):return all(p in methods[cls,name] for p in parts)
    opening=methods['GP_Endgame','OpenBoardVictory']
    advance=opening[opening.index('    0x14f08f4:'):opening.index('    0x14f09b8:')]
    checks={
      'exact_prefab_and_3_ordered_normal_rows':prefab['root']=={'serialized_file':'resources.assets','path_id':113205} and len(rows)==3 and [r['component_path_id'] for r in rows]==[648536,636132,696150],
      'continue_persistent_call_targets_this_board':calls[0]['m_MethodName']=='OnPressedButtonContinue' and calls[0]['m_CallState']==2,
      'board_initializes_real_mission_array':has('Board_Endgame','Init','0x126c538: bl       #0x1272714'),
      'endgame_snapshots_kill_count_and_denominator':has('GP_Endgame','OpenBoardVictory','0x14f0b20: str      w9, [x8, #0x14]','0x14f0b30: ldr      w9, [x0, #0x58]','0x14f0b38: str      w9, [x8, #0x18]'),
      'saved_mission_is_strict_star_count_greater_than_index':has('Stage_Get_Datas','IsMissionCompleted','0x12c5620: bl       #0x12b7860','0x12c5624: cmp      w0, w19','0x12c5630: cset     w0, gt'),
      'normal_score_uses_snapshot_and_sets_victory_sign':has('Board_Endgame','SetMissions','0x12730c0: ldp      w0, w1, [x8, #0x14]','0x12730c4: bl       #0x12734f8','0x12730e4: mvn      w9, w20','0x12730ec: strb     w9, [x8]'),
      'only_new_rows_increment_global_star_count':has('Board_Endgame','SetMissions','0x1273134: cmp      x21, x22','0x1273138: b.gt','0x1273144: cbnz','0x1273160: add      w0, w0, #1','0x1273168: bl       #0x13256f0'),
      'saved_star_count_is_result_plus1_only_if_improved':has('Board_Endgame','SetMissions','0x12731d4: add      w20, w20, #1','0x12731d8: cmp      w20, w26','0x12731dc: b.le     #0x1272c90','0x1273240: mov      w2, w20','0x1273248: bl       #0x12c4620','0x127324c: b        #0x1272c90'),
      'per_stage_preference_write_delegates_to_unity_set_int':has('Stage_Datas','SetStarStageMaster','#0x13f1a04') and has('PlayerPreferences','SetInt','0x13f1a08: b        #0x277cc10'),
      'global_star_setter_updates_cache_and_unity_pref':has('GameDatas','set_StarCount','0x132575c: str      w19, [x8, #0x4c]','0x132576c: b        #0x277cc10'),
      'run_missions_uses_snapshot_skips_old_and_clears_new':has('Board_Endgame._RunMissions_d__162','MoveNext','0x127a9f0: cbnz','0x127a9fc: b.ge     #0x127aa50','0x127ab0c: bl       #0x138c4d8'),
      'run_missions_yields_half_second_unscaled_after_each_new_row':has('Board_Endgame._RunMissions_d__162','MoveNext','0x127ac34: str      w8, [x20, #0x270]','0x127ac48: fmov     s0, #0.50000000','0x127ac54: bl       #0x2786604') and rv[0x2786604]['class']=='WaitForSecondsRealtime',
      'mission_initial_and_clear_are_animator_triggers':has('Stage_Mission','InitMission','#0x27583b0') and has('Stage_Mission','ClearMission','#0x27583b0') and rv[0x27583b0]['signature']=='public void SetTrigger(string name) { }',
      'continue_calls_skip_before_navigation':has('Board_Endgame','Continue','0x126ed50: bl       #0x126dd70','0x126f298: bl       #0x126f3c8') and has('Board_Endgame','<OnPressedButtonContinue>b__103_0','#0x126ec94'),
      'skip_stops_coroutines_and_uses_processed_row_index':has('Board_Endgame','SkipUnbox','0x126de48: bl       #0x2782b0c','0x126e2a4: ldrsw    x9, [x19, #0x270]','0x126e2f0: cmp      w20, w21','0x126e300: cbnz','0x126e3f0: bl       #0x138c4d8'),
      'target_advance_block_does_not_test_incoming_victory_w20':all(s in advance for s in ('0x14f0954: cmp      w0, w21','0x14f0988: add      w8, w8, #9','0x14f0990: b.le','0x14f09ac: add      w0, w0, #1','0x14f09b4: bl       #0x12bac5c')) and not re.search(r'\b[wx]20\b',advance),
    }
    assert all(checks.values()),checks
    return {'status':'PROVISIONAL — ordinary campaign missions, static preference writes not disk flush',
            'checks':checks,'methods':records,'sources':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()},
                                                      {'path':str(index_path.relative_to(ROOT)),'sha256':hashlib.sha256(index_path.read_bytes()).hexdigest()}],
            'prefab':{'resource_key':entry['container_key'],'root':prefab['root'],'node_count':len(prefab['nodes']),
                      'board_component_path_id':board['path_id'],'normal_rows':rows,
                      'continue':{'path':btn['path'],'active_in_prefab':btn['gameobject']['tree']['m_IsActive'],'persistent_call':calls[0]}},
            'target_advance_asm':advance,
            'declarations':{k:decl[k] for k in ('Board_Endgame','Stage_Mission','Stage_Datas','GameDatas')}}


if __name__=='__main__':
    d=build();(RAW/'endgame-missions/mission-progress-flow.json.gz').write_bytes(gzip.compress(json.dumps(d,indent=2).encode(),mtime=0))
    print(len(d['methods']),'methods;',len(d['checks']),'checks',d['checks'])
