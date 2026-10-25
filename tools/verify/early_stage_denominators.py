#!/usr/bin/env python3
"""Join original APK resource prefabs -> IPooling IDs -> mission denominator.

Static normal chapter0 snapshot only. No prediction of runtime victory or kills.
"""
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
from enemy_exit_missions import f32

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'reverse-engineering/raw'
SELECT={'Stage_Get_Datas':['cctor','GetCountEnemies'], 'MapController':['Start'], 'Sub_Object':['GetID']}


def ident(row):return row['serialized_file'],row['path_id']


def raw_bytes(c):
    b=base64.b64decode(c['bytes_base64']);assert hashlib.sha256(b).hexdigest()==c['bytes_sha256'];return b


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
        folder=RAW/'il2cpp-consts' if cls=='Stage_Get_Datas' else audit/'extra-native'
        p=folder/f'{cls}.asm.txt';inv=json.loads((folder/f'{cls}.json').read_text())
        for name in names:
            asm=section(p.read_text(),name);methods[cls,name]=asm
            method=next(m for m in inv['methods'] if m['method']==name);assert not method.get('size_capped')
            records.append({'class':cls,'method':name,'asm':asm,'inventory':method,'source':str(p.relative_to(ROOT)),
                            'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'calls':direct_calls(asm,rv),'metadata_loads':metadata_loads(asm,rel,ix)})
    cctor=methods['Stage_Get_Datas','cctor']
    fast=re.findall(r'(0x[0-9a-f]+): mov      w(?:12|10), #(0x[0-9a-f]+)',cctor)
    fallback=re.findall(r'(0x[0-9a-f]+): mov      w1, #(0x[0-9a-f]+)',cctor)
    # First two array lengths (5 and4) precede the List<int> initializer.
    assert [v for _,v in fast]==[v for _,v in fallback if int(v,16)>10000]
    ignored=[{'instruction':a,'id':int(v,16)} for a,v in fast];ignore_ids={r['id'] for r in ignored}
    enemy_path=RAW/'early-waves/default-enemy-components.json.gz'
    enemies=json.load(gzip.open(enemy_path,'rt'));lookup={};enemy_rows=[]
    for e in enemies['enemy_roots']:
        byclass={c.get('script_class',c['type']):c for c in e['components']}
        sub=byclass['Enemy_Sub'];pool=byclass['ObjectPool'];ctrl=byclass['Enemy_Controller'];destroy=byclass['Enemy_Destroy']
        assert sub['tree']['m_OPScript']=={'m_FileID':0,'m_PathID':pool['path_id']}
        assert sub['tree']['controller']=={'m_FileID':0,'m_PathID':ctrl['path_id']}
        assert ctrl['tree']['destroyScript']=={'m_FileID':0,'m_PathID':destroy['path_id']}
        assert all(c['serialized_file']==e['gameobject']['serialized_file'] for c in (sub,pool,ctrl,destroy))
        for c in byclass.values():
            if c['type']=='MonoBehaviour':raw_bytes(c)
        # Custom fields start at32 in these pinned root components. Verify the
        # critical ID and PPtr joins directly, not generated header.m_Script.
        pid=pool['tree']['id'];assert struct.unpack_from('<i',raw_bytes(pool),32)[0]==pid
        assert struct.unpack_from('<iq',raw_bytes(sub),32)==(0,pool['path_id'])
        assert struct.unpack_from('<iq',raw_bytes(ctrl),32+6*12)==(0,destroy['path_id'])
        row={'name':e['gameobject']['tree']['m_Name'],'pooling_id':pid,
             'ignored_by_denominator':pid in ignore_ids,'enemy_sub_identity':{k:sub[k] for k in ('serialized_file','path_id')},
             'object_pool_identity':{k:pool[k] for k in ('serialized_file','path_id')},
             'controller_identity':{k:ctrl[k] for k in ('serialized_file','path_id')},
             'destroy_identity':{k:destroy[k] for k in ('serialized_file','path_id')},'destroy_class':destroy['script_class']}
        row['identity']={k:e['gameobject'][k] for k in ('serialized_file','path_id')}
        lookup[ident(e['gameobject'])]=row;enemy_rows.append(row)
    index=json.loads((RAW/'early-waves/index.json').read_text());waves=[];sources=[]
    for wid in ('0164','0113','0005'):
        entry=next(e for e in index['entries'] if e['container_key']=='datas/maps/waves/wave_'+wid)
        p=RAW/'early-waves'/entry['export'];data=json.load(gzip.open(p,'rt'));assert data['inputs_sha256']==enemies['inputs_sha256']
        hist=Counter();excluded=Counter();calls=[]
        assert all(n['gameobject']['tree']['m_IsActive'] for n in data['nodes'])
        for node in data['nodes']:
            for c in node['components']:
                if c.get('script_class')!='Call_Data':continue
                t=c['tree'];raw_bytes(c)
                if t['spawnType']==5:continue
                ids=[]
                for ptr in t['listPrefabEnemies']:
                    assert ptr['m_FileID']==0
                    e=lookup[c['serialized_file'],ptr['m_PathID']];pid=e['pooling_id'];ids.append(pid)
                    (excluded if pid in ignore_ids else hist)[pid]+=1
                calls.append({'path':node['path'],'spawn_type':t['spawnType'],'pooling_ids':ids,'number_serialized':t['number']})
        waves.append({'wave':wid,'resource_key':entry['container_key'],'root':data['root'],
                      'denominator':sum(hist.values()),'included_ids':{str(k):v for k,v in hist.items()},'excluded_ids':{str(k):v for k,v in excluded.items()},'calls':calls})
        sources.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    missions=json.load(gzip.open(audit/'enemy-exit-missions.json.gz','rt'))['normal_mission_arrays']
    stage_path=audit/'scene-map-flow.json.gz'
    campaign=json.load(gzip.open(stage_path,'rt'))['campaign_immediates']
    original=(ROOT/campaign['source']).read_bytes()
    assert hashlib.sha256(original).hexdigest()==campaign['source_sha256']
    stages=[]
    for map_row in campaign['rows']:
        assert map_row['literal_store_asm'] in original.decode()
        internal=map_row['internal_stage_index'];used=[f'{v:04d}' for v in map_row['values']]

        denominator=sum(w['denominator'] for w in waves if w['wave'] in used)
        thresholds={mode:[int(f32(f32(denominator)*p)) for p in row['float32']] for mode,row in missions.items()}
        stages.append({'display_stage':internal+1,'internal_stage':internal,'waves':used,'denominator':denominator,'normal_thresholds_by_mode':thresholds})
    def has(cls,name,*parts):return all(p in methods[cls,name] for p in parts)
    checks={
      'ignore_list_31_literal_ids_stored_static18':len(ignored)==31 and len(ignore_ids)==31 and has('Stage_Get_Datas','cctor','0x12c8364: str      x19, [x8, #0x18]'),
      'count_loads_list_waves_and_active_call_data':has('Stage_Get_Datas','GetCountEnemies','#0x13fe86c','mov      w1, wzr','0x12c6290: bl       #0x171e564'),
      'count_skips_end_marker5_not_generic_number0':has('Stage_Get_Datas','GetCountEnemies','0x12c62c4: cmp      w10, #5','0x12c62c8: b.ne     #0x12c62dc','0x12c62e8: ldr      x9, [x9, #0x30]'),
      'count_reads_get_id_then_negated_ignore_contains':has('Stage_Get_Datas','GetCountEnemies','0x12c6370: blr      x8','0x12c6394: ldr      x0, [x8, #0x18]','0x12c63a4: bl       #0x1b95084','0x12c63bc: and      w10, w10, #1','0x12c63c4: add      w20, w20, w10'),
      'map_setup_count_is_stored_in_gp_datas58':has('MapController','Start','0x132a5b0: bl       #0x14c78cc','0x132a5c8: bl       #0x14f0da0','0x132a5ec: bl       #0x12c5f60','0x132a5f4: str      w0, [x19, #0x58]'),
      'get_id_reads_sub_object_pool_reference_then_pool_id':has('Sub_Object','GetID','0x123bb58: ldr      x8, [x0, #0x20]','0x123bb60: ldr      w0, [x8, #0x20]'),
      'all_14_enemy_root_links_and_bytes_verified':len(enemy_rows)==14,
      'only_38001_is_ignored_in_these_waves':all(set(w['excluded_ids'])=={'38001'} for w in waves),
      'denominators_262_87_151':[w['denominator'] for w in waves]==[262,87,151],
      'stage_denominators_262_238':[s['denominator'] for s in stages]==[262,238],
      'all_destroy_components_are_base':all(r['destroy_class']=='Enemy_Destroy' for r in enemy_rows),
    }
    assert all(checks.values()),checks
    for p in (enemy_path,stage_path,audit/'enemy-exit-missions.json.gz',RAW/'early-waves/index.json'):
        sources.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    return {'status':'PROVISIONAL — static normal chapter0 denominator and thresholds, not victory guarantee',
            'checks':checks,'methods':records,'sources':sources,'ignored_ids':ignored,'campaign_rows':campaign['rows'],'enemy_roots':enemy_rows,'waves':waves,'stages':stages,
            'declarations':{k:decl[k] for k in ('Stage_Get_Datas','GP_Datas','Enemy_Sub','Sub_Character','Sub_Object','ObjectPool','Enemy_Controller','Enemy_Destroy')}}


if __name__=='__main__':
    d=build();(RAW/'early-waves/mission-denominators.json.gz').write_bytes(gzip.compress(json.dumps(d,indent=2).encode(),mtime=0))
    print(json.dumps({'checks':d['checks'],'stages':d['stages']},indent=2))
