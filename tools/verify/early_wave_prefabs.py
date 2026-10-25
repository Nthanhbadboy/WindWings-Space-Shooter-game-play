#!/usr/bin/env python3
"""Exact resource identity and configured spawn slots; NOT observed gameplay counts."""
import base64
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'reverse-engineering/raw/early-waves'
EXPECTED={'0164':(148604,537,42,274),'0113':(21468,387,91,95),'0005':(38187,58,16,155)}


def build():
    index=json.loads((RAW/'index.json').read_text());waves=[];checks={}
    for wave,(root_id,nodes,count,slots) in EXPECTED.items():
        key='datas/maps/waves/wave_'+wave
        matches=[e for e in index['entries'] if e['container_key']==key]
        assert len(matches)==1,key
        entry=matches[0];p=RAW/entry['export'];d=json.load(gzip.open(p,'rt'))
        refs={(r['gameobject']['serialized_file'],r['gameobject']['path_id']):r['gameobject']['tree']['m_Name'] for r in d['enemy_references']}
        transforms={};rows=[]
        for n in d['nodes']:
            for c in n['components']:
                if 'bytes_base64' in c:
                    assert hashlib.sha256(base64.b64decode(c['bytes_base64'])).hexdigest()==c['bytes_sha256']
                if c['type']=='Transform':transforms[c['path_id']]=dict(c['tree'],node_path=n['path'])
        for n in d['nodes']:
            comp={c.get('script_class',c['type']):c for c in n['components']}
            if 'Call_Data' not in comp:continue
            c=comp['Call_Data'];t=c['tree'];prefabs=t['listPrefabEnemies']
            # This export's enemy references are same-file. Fail on any new
            # external reference rather than interpreting a global numeric ID.
            assert all(p['m_FileID']==0 for p in prefabs)
            names=[refs[c['serialized_file'],p['m_PathID']] for p in prefabs]
            points=t['parentPoints'];assert points['m_FileID']==0
            parent=transforms.get(points['m_PathID'])
            marker=t['spawnType'] in (5,6)
            rows.append({'path':n['path'],'component_identity':{k:c[k] for k in ('serialized_file','path_id')},
                         'spawn_type':t['spawnType'],'spawner_class':next(k for k in comp if k=='Spawner' or k.endswith('_Spawner')),
                         'serialized_number':t['number'],'serialized_enemy_ids':t['listIdEnemies'],
                         'prefab_length':len(prefabs),'configured_slots':0 if marker else max(t['number'],len(prefabs)),
                         'marker':marker,'rate_serialized':t['rate'],'trigger_y':t['ySpawn'],
                         'local_position':comp['Transform']['tree']['m_LocalPosition'],
                         'parent_points_path':parent['node_path'] if parent else None,
                         'point_children':len(parent['m_Children']) if parent else None,
                         'enemy_prefab_names':names,'bring_items_flags':t['listBringItems']})
        histogram=Counter(name for r in rows if not r['marker'] for name in r['enemy_prefab_names'])
        checks[wave+'_exact_resource_root']=(d['root']=={'serialized_file':'resources.assets','path_id':root_id} and d['container_key']==key)
        checks[wave+'_complete_nodes_and_calls']=(len(d['nodes'])==nodes and len(rows)==count)
        checks[wave+'_all_active_enabled']=all(n['gameobject']['tree']['m_IsActive'] and all(c['tree'].get('m_Enabled',True) for c in n['components']) for n in d['nodes'])
        checks[wave+'_number_zero_not_zero_spawns']=all(r['serialized_number']==0 and r['serialized_enemy_ids']==[] for r in rows)
        checks[wave+'_slot_sum_excludes_markers']=sum(r['configured_slots'] for r in rows)==slots
        checks[wave+'_prefab_array_not_shorter_than_number']=all(r['prefab_length']>=r['serialized_number'] for r in rows)
        waves.append({'resource_key':key,'root':d['root'],'source':str(p.relative_to(ROOT)),
                      'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'node_count':len(d['nodes']),
                      'call_data_count':len(rows),'configured_spawn_slots':slots,'prefab_histogram':dict(histogram),
                      'spawner_class_histogram':dict(Counter(r['spawner_class'] for r in rows)), 'rows':rows})
    assert all(checks.values()),checks
    return {'status':'PROVISIONAL — configured slots, not live enemy/kill counts or timeline',
            'checks':checks,'waves':waves,'container_index_source':str((RAW/'index.json').relative_to(ROOT))}


if __name__=='__main__':
    result=build()
    (RAW/'resolved-default-waves.json.gz').write_bytes(gzip.compress(json.dumps(result,ensure_ascii=False,indent=2).encode(),mtime=0))
    print(json.dumps({w['resource_key']:{k:w[k] for k in ('configured_spawn_slots','prefab_histogram','spawner_class_histogram')} for w in result['waves']},indent=2))
