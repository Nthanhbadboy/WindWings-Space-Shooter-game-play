#!/usr/bin/env python3
"""Exact prefab + callback joins for early enemy movement exits. Static only."""
import base64
from collections import Counter
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
RAW=ROOT/'reverse-engineering/raw'
SELECT={
 'Enemy_Controller':['OnEnable','Appear','Appeared','OnMoveCompleted'],
 'Enemy_Appear':['Appear'],
 'Enemy_Sub':['SetPathFollower','SetWaypoints','SetPosition','SetAngle'],
 'Enemy_Movement':['SetEventMoveEnded','<SetEventMoveEnded>b__22_0','OnPathEnded',
  'Update','FixedUpdate','PathFollow','MovePointToPoint','SetPathFollower','SetWaypoints',
  'SetPosition','SetPositionAndAngle','MoveLinearly'],
 'VertexPath':['GetPointAtDistance','GetPoint','CalculatePercentOnPathData'],
 'Enemy_Destroy':['Destroy','Pool'],
 'GP_Datas':['<ResetAlls>b__60_1'],
 'AirFree_Spawner':['OnSpawn'],
}
CONSTS={'Enemy_Appear','Enemy_Sub'}


def path_callback_gate(interpolation,endpoint_distance_squared,epsilon,callback=True):
    """Only GetPoint's event predicate, not the complete curve evaluator."""
    return bool(callback and interpolation==1.0 and endpoint_distance_squared<epsilon)


def fixed_exit_requested(moving,is_turret,move_type,movein,x,y,border=(-10,10,-15,15)):
    """Restricted finite input predicate; intentionally NOT callback invocation count.

    The turret branch falls through and a callback can mutate state before the
    linear branch. This model does not promise exactly-once or emulate listeners.
    """
    if not moving:return False
    left,right,bottom,top=border
    return bool((is_turret and y<bottom) or (movein and move_type==2 and (y>top or y<bottom or x<left or x>right)))


def completion_chain(type_move_ended,controller_callback=True):
    return ['stop_moving','unity_event']+(['controller_destroy_when_done','pool_event79'] if type_move_ended==0 and controller_callback else [])


def pool_without_kill(active,enemy,kill_count):
    """Models Contains/Remove branch; no claim about external event listeners."""
    result=list(active)
    if enemy in result:result.remove(enemy)
    return result,kill_count


def build():
    audit=RAW/'ui-audit';dump_path=ROOT/'reverse-engineering/il2cpp/dump.cs.gz'
    dump=gzip.open(dump_path,'rt').read();decl={};rv={};ix={};records=[];methods={}
    for b in re.split(r'(?=// Namespace:)',dump):
        c=re.search(r'(?:class|enum|interface) ([^ :\n]+)',b)
        if not c:continue
        ns=re.match(r'// Namespace:([^\n]*)',b)[1].strip()
        qualified=ns+'.'+c[1] if ns else c[1]
        decl.setdefault(c[1],b)
        decl[qualified]=b
        for m in re.finditer(r'// RVA: (0x[\dA-Fa-f]+)[^\n]*\n([^\n]+)',b):rv[int(m[1],16)]={'class':c[1],'signature':m[2].strip()}
    reloc=audit/'native-relocations.json.gz';metadata=audit/'metadata-index.json.gz'
    rel_data=json.load(gzip.open(reloc,'rt'));rel=rel_data['relocations']
    for group,rows in json.load(gzip.open(metadata,'rt'))['tables'].items():
        for row in rows:ix.setdefault(row['Address'],[]).append(dict(row,group=group))
    sources={dump_path,reloc,metadata}
    for cls,names in SELECT.items():
        folder=RAW/'il2cpp-consts' if cls in CONSTS else audit/'extra-native'
        p=folder/f'{cls}.asm.txt';ip=folder/f'{cls}.json';sources.update((p,ip));inventory=json.loads(ip.read_text())
        for name in names:
            asm=section(p.read_text(),name);methods[cls,name]=asm
            inv=next(m for m in inventory['methods'] if m['method']==name);assert not inv.get('size_capped')
            records.append({'class':cls,'method':name,'asm':asm,'inventory':inv,'source':str(p.relative_to(ROOT)),
                            'calls':direct_calls(asm,rv),'metadata_loads':metadata_loads(asm,rel,ix)})
    ep=RAW/'early-waves/default-enemy-components.json.gz';enemies=json.load(gzip.open(ep,'rt'));sources.add(ep)
    assert enemies['inputs_sha256']['libil2cpp.so']==rel_data['native_sha256']
    roots=[];lookup={}
    def blob(c):
        b=base64.b64decode(c['bytes_base64']);assert hashlib.sha256(b).hexdigest()==c['bytes_sha256'];return b
    for e in enemies['enemy_roots']:
        go=e['gameobject'];byid={c['path_id']:c for c in e['components']}
        c=next(c for c in e['components'] if c.get('script_class')=='Enemy_Controller')
        def linked(field,expected,offset):
            ptr=c['tree'][field];assert ptr['m_FileID']==0
            v=byid[ptr['m_PathID']];assert v['serialized_file']==c['serialized_file'] and v['script_class']==expected
            assert struct.unpack_from('<iq',blob(c),offset)==(0,v['path_id'])
            return v
        m=linked('movementScript','Enemy_Movement',32+4*12)
        appear=linked('appearScript','Enemy_Appear',32+2*12)
        destroy=linked('destroyScript','Enemy_Destroy',32+6*12)
        t=m['tree'];b=blob(m)
        assert struct.unpack_from('<3i',b,32)==(t['endOfPathInstruction'],t['typeMoveEnded'],0)
        assert t['moveEndedEvent']['m_PersistentCalls']['m_Calls']==[]
        assert bool(struct.unpack_from('<i',b,48)[0])==t['isTurret']
        n=struct.unpack_from('<i',b,64)[0];assert n==len(t['listSpeeds'])
        assert list(struct.unpack_from('<'+'f'*n,b,68))==t['listSpeeds']
        assert dict(zip(('x','y','z','w'),struct.unpack_from('<4f',b,68+4*n)))==t['border']
        row={'name':go['tree']['m_Name'],'identity':{k:go[k] for k in ('serialized_file','path_id')},
             'controller_path_id':c['path_id'],'movement_path_id':m['path_id'],'appear_path_id':appear['path_id'],
             'destroy_path_id':destroy['path_id'],'movement_class':m['script_class'],
             'typeMoveEnded':t['typeMoveEnded'],'endOfPathInstruction':t['endOfPathInstruction'],
             'isTurret':t['isTurret'],'listSpeeds':t['listSpeeds'],'border':t['border'],
             'persistent_move_event_calls':[],'isNoPool':destroy['tree']['isNoPool'],
             'root_animators':[{'path_id':a['path_id'],'tree':a['tree']} for a in e['components'] if a['type']=='Animator']}
        roots.append(row);lookup[go['serialized_file'],go['path_id']]=row
    index_path=RAW/'early-waves/index.json';sources.add(index_path);index=json.loads(index_path.read_text());waves=[]
    for wid in ('0164','0113','0005'):
        entry=next(e for e in index['entries'] if e['container_key']=='datas/maps/waves/wave_'+wid)
        p=RAW/'early-waves'/entry['export'];sources.add(p);wave=json.load(gzip.open(p,'rt'))
        assert wave['inputs_sha256']==enemies['inputs_sha256'];rows=[];counts=Counter()
        for node in wave['nodes']:
            for c in node['components']:
                if c.get('script_class')!='Call_Data':continue
                t=c['tree'];blob(c)
                if t['spawnType'] in (5,6):continue
                spawners=[a['script_class'] for a in node['components'] if a.get('script_class','').endswith('Spawner')];assert len(spawners)==1
                joins=[]
                for ptr in t['listPrefabEnemies']:
                    assert ptr['m_FileID']==0
                    e=lookup[c['serialized_file'],ptr['m_PathID']];joins.append(e['identity']);counts[spawners[0]]+=1
                rows.append({'path':node['path'],'call_data_path_id':c['path_id'],'spawner':spawners[0],'spawn_type':t['spawnType'],'enemy_roots':joins})
        waves.append({'resource_key':entry['container_key'],'root':wave['root'],'slots_by_spawner':dict(counts),'rows':rows})
    ro_path=audit/'endgame-rodata.json';sources.add(ro_path);ro=json.loads(ro_path.read_text());assert ro['native_sha256']==rel_data['native_sha256']
    epsilon=next(f for f in ro['movement_floats'] if f['va']=='0x756a58')
    assert struct.unpack('<f',bytes.fromhex(epsilon['bytes_hex']))[0]==epsilon['float32']
    def has(cls,name,*parts):return all(p in methods[cls,name] for p in parts)
    checks={
      'global_itransform_is_not_uielements_namesake': 'public abstract void SetAngle(float angle);' in decl['ITransform'] and 'get_scale' not in decl['ITransform'],
      '14_exact_roots_all_base_movement_appear_destroy_with_verified_pptrs':len(roots)==14,
      'all_serialized_destroy_on_end_stop_at_path_end_empty_persistent_events':all(r['typeMoveEnded']==0 and r['endOfPathInstruction']==2 and not r['persistent_move_event_calls'] and not r['isNoPool'] for r in roots),
      'controller_onenable_enters_appear':has('Enemy_Controller','OnEnable','0x15826e0: b        #0x15826e4'),
      'appear_binds_move_callback_before_appearance':has('Enemy_Controller','Appear','0x1582834: bl       #0x1583be8','0x15828a0: br       x3'),
      'base_appear_invokes_callback_immediately':has('Enemy_Appear','Appear','0x1582120: br       x2'),
      'appeared_sets_moving_true':has('Enemy_Controller','Appeared','0x1584874: mov      w9, #1','0x1584878: strb     w9, [x8, #0x5c]'),
      'setevent_clears_old_delegate_then_appends_controller_only_for_type0':has('Enemy_Movement','SetEventMoveEnded','0x1583c3c: str      xzr, [x23, #0x68]!','0x1583c68: bl       #0x2146010','0x1583ca0: ldr      w8, [x20, #0x28]','0x1583ca4: cbnz     w8, #0x1583ce0','0x1583cb0: bl       #0x2146010'),
      'first_delegate_stops_movement_then_unity_event':has('Enemy_Movement','<SetEventMoveEnded>b__22_0','0x15869ec: strb     wzr, [x8, #0x5c]','0x15869f8: b        #0x278ef98'),
      'path_distance_uses_speed_times_delta_and_onended':has('Enemy_Movement','PathFollow','0x1586204: bl       #0x2786de8','0x158620c: fmul     s0, s9, s0','0x158621c: ldr      x2, [x19, #0x68]','0x1586228: bl       #0x143db50'),
      'vertex_distance_normalizes_by_length':has('VertexPath','GetPointAtDistance','0x143db50: ldr      s1, [x0, #0x38]','0x143db54: fdiv     s0, s0, s1'),
      'stop_mode_clamps_path_t':has('VertexPath','CalculatePercentOnPathData','0x143dd98: cmp      w1, #2','0x143dd9c: b.eq     #0x143de24','0x143de34: fmin     s8, s9, s0'),
      'vertex_callback_checks_final_lerp_and_squared_endpoint_distance':has('VertexPath','GetPoint','0x143dbfc: fcmp     s1, s3','0x143dc00: b.ne     #0x143dc5c','0x143dc20: ldr      s4, [x8, #0xa58]','0x143dc40: b.pl     #0x143dc5c','0x143dc50: blr      x8'),
      'point_final_segment_invokes_onended':has('Enemy_Movement','MovePointToPoint','0x1586568: b.ge     #0x1586588','0x1586588: ldr      x8, [x19, #0x68]','0x15865b4: br       x2'),
      'turret_below_border_z_invokes_onended':has('Enemy_Movement','FixedUpdate','0x158608c: cbz      w8, #0x1586198','0x1586098: cbz      w8, #0x15860d8','0x15860b4: ldr      s0, [x19, #0x88]','0x15860bc: b.pl     #0x15860d8','0x15860d4: blr      x9'),
      'controller_requests_when_done2':has('Enemy_Controller','OnMoveCompleted','0x1584788: mov      w1, #2','0x1584794: br       x3'),
      'destroy2_bypasses_death_handlers_goes_straight_to_pool':has('Enemy_Destroy','Destroy','0x15815a8: cbnz     w1, #0x15815c8','0x15815d0: b        #0x1584bf0'),
      'pool_posts79_and_active_callback_contains_removes':has('Enemy_Destroy','Pool','0x1584c40: mov      w1, #0x4f','0x1584c4c: bl       #0x1434cb4') and has('GP_Datas','<ResetAlls>b__60_1','#0x1bd81e0','0x14d0200: tbz','#0x1bd91a0'),
      'setposition_does_not_select_path_or_waypoints':has('Enemy_Sub','SetPosition','0x1587ff0: b        #0x1584070') and has('Enemy_Movement','SetPosition','0x15840d0: b        #0x2781804'),
      'spawner_slot_partitions_match_exact_roots':[{k:v for k,v in w['slots_by_spawner'].items()} for w in waves]==[
          {'PinMap_Spawner':19,'Path_Spawner':150,'Waypoints_Spawner':104,'AirFree_Spawner':1},
          {'PinMap_Spawner':15,'PointToPoint_Spawner':80}, {'PinMap_Spawner':15,'Path_Spawner':140}],
    }
    assert all(checks.values()),checks
    return {'status':'PROVISIONAL — conditional static movement exits, not a kill-count runtime witness',
            'inputs_sha256':enemies['inputs_sha256'],'checks':checks,'methods':records,'enemy_roots':roots,'waves':waves,
            'endpoint_epsilon':epsilon,
            'sources':[{'path':str(p.relative_to(ROOT)),'hash_bytes':'gzip-decompressed' if p.suffix=='.gz' else 'file',
                        'sha256':hashlib.sha256(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes()).hexdigest()} for p in sorted(sources)],
            'declarations':{k:decl[k] for k in ('Enemy_Movement','Enemy_Movement.TypeMove','Enemy_Movement.TypeMoveEnded','EndOfPathInstruction','DestroyType','ITransform','UnityEngine.UIElements.ITransform','Enemy_Sub')},
            'limitations':['no actual elapsed movement time from path geometry','no proof every configured slot spawned or every enemy escaped',
                           'AirFree BB-36001 root Animator behavior not resolved','UnityEvent runtime listeners can mutate state','no Premium/reborn analysis']}

if __name__=='__main__':
    d=build();p=RAW/'early-waves/movement-completion.json.gz';p.write_bytes(gzip.compress(json.dumps(d,indent=2).encode(),mtime=0))
    print(len(d['methods']),'methods;',len(d['checks']),'checks')
