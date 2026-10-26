"""#8 independently streamed report98 gap selection, no whole Graph.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
from __future__ import annotations
import argparse
from collections import Counter
import gzip
import json
import re
from tools.verify.geometry_8141386a_atlas_io import ROOT,BRANCH,canonical,key,identity,sha_file,sha

RAW=ROOT/'reverse-engineering/raw/geometry-8141386a/gaps'
CHAIN=ROOT/'reverse-engineering/raw/l3-chain'
SELECTED=RAW/'selected-inputs.json.gz'


def dump_classes(wanted):
    result=[];namespace='';active=None;level=0;opened=False
    with gzip.open(ROOT/'reverse-engineering/il2cpp/dump.cs.gz','rt') as h:
        for i,line in enumerate(h,1):
            if line.startswith('// Namespace:'):namespace=line.split(':',1)[1].strip()
            if active is None:
                m=re.search(r'\bclass (\w+)(?:\s|:)',line)
                if m and (namespace,m[1]) in wanted:
                    active=dict(namespace=namespace,class_name=m[1],first_line=i,lines=[]);level=0;opened=False
            if active is not None:
                active['lines'].append(line);level+=line.count('{')-line.count('}');opened=opened or '{' in line
                if opened and level==0:
                    body=''.join(active.pop('lines'));active.update(last_line=i,text=body,text_sha256=sha(body.encode()));result.append(active);active=None
    if {(r['namespace'],r['class_name']) for r in result}!=wanted:raise ValueError('exact requested C# declarations not found')
    return result


def select():
    idx=json.loads((CHAIN/'index.json').read_bytes());files={f['serialized_file']:f['externals'] for f in idx['files']}
    pins={str((CHAIN/'index.json').relative_to(ROOT)):sha_file(CHAIN/'index.json')};refs=[];records={};headers={key(r):r for r in idx['header_only']}
    def rows(group):
        for part in idx[group]:
            p=CHAIN/part['path']
            if sha_file(p)!=part['sha256']:raise ValueError('report98 compressed source SHA drift')
            pins[str(p.relative_to(ROOT))]=part['sha256'];n=0
            with gzip.open(p,'rb') as h:
                for i,line in enumerate(h):
                    n+=1;yield json.loads(line),dict(path=str(p.relative_to(ROOT)),row=i)
            if n!=part['rows']:raise ValueError('report98 source row count drift')
    for r,loc in rows('links'):
        if r['status']!='unresolved':continue
        owner=r['owner'];p=r['pointer'];external=files[owner['serialized_file']][p['m_FileID']-1]['path'] if p['m_FileID'] else owner['serialized_file']
        if r['location']!='.m_Mesh' or external!='Library/unity default resources':raise ValueError('unresolved group is not just the reported default mesh gap')
        refs.append(dict(record=r,external_path=external,raw_location=loc))
    wanted={key(r['record']['owner']) for r in refs}|set(headers);counts=Counter()
    for r,loc in rows('objects'):
        counts[r['type']]+=1
        if key(r) in wanted:records[key(r)]=dict(identity=identity(key(r)),record=r,raw_location=loc)
    if dict(counts)!=idx['counts'] or set(records)!=wanted:raise ValueError('captured report98 counts/target selection incomplete')
    header_rows=[]
    for k,declared in sorted(headers.items()):
        r=records[k]
        if r['record'].get('tree_error')!=declared['tree_error']:raise ValueError('header-only parser exception drift')
        header_rows.append(dict(**r,capture_exception=declared['tree_error']))
    mesh_rows=[]
    for ref in refs:
        r=records[key(ref['record']['owner'])];field=ref['record']['location'][1:]
        if r['record']['tree'][field]!=ref['record']['pointer']:raise ValueError('captured original owner/link PPtr disagreement')
        mesh_rows.append(dict(**r,reference=ref))
    previous_path=ROOT/'datas/l3_geometry_builtin_8141386a.json.gz';previous=json.loads(gzip.decompress(previous_path.read_bytes()));previous_keys={(*key(r['owner']),r['field']) for r in previous['references']}
    now={(*key(r['identity']),r['reference']['record']['location'][1:]) for r in mesh_rows};overlap=previous_keys&now
    old_rows={(*key(r['owner']),r['field']):r for r in previous['references']}
    for r in mesh_rows:
        k=(*key(r['identity']),r['reference']['record']['location'][1:])
        if k in overlap and (old_rows[k]['pointer']!=r['reference']['record']['pointer'] or old_rows[k]['renderer_object_sha256']!=r['record']['raw_object_sha256']):raise ValueError('actual cross-closure overlap disagrees')
    classes={(r['record'].get('namespace',''),r['record']['class_name']) for r in header_rows}
    classes.update({('SpaceShooter.Player','Player_Attack'),('SpaceShooter.EnemySystem','Boss_AttackTypes'),('UnityEngine.Events','UnityEventBase'),('UnityEngine.Events','PersistentCallGroup'),('UnityEngine.Events','PersistentCall'),('UnityEngine.Events','ArgumentCache')})
    snippets=dump_classes(classes)
    for p in (ROOT/'reverse-engineering/il2cpp/dump.cs.gz',previous_path):pins[str(p.relative_to(ROOT))]=sha_file(p)
    return dict(schema=1,item=8,provenance=BRANCH,xapk_sha256=idx['xapk_sha256'],files=idx['files'],
                scope=idx['scope'] if 'scope'in idx else idx['status'],header_records=header_rows,mesh_references=mesh_rows,csharp_declarations=snippets,
                summary=dict(captured_objects=sum(counts.values()),captured_links=sum(p['rows'] for p in idx['links']),header_only=len(header_rows),
                             header_class_counts=dict(Counter(r['record']['class_name'] for r in header_rows)),
                             default_mesh_refs=len(mesh_rows),mesh_owner_types=dict(Counter(r['record']['type'] for r in mesh_rows)),
                             target_path_id_histogram=dict(Counter(str(r['reference']['record']['pointer']['m_PathID']) for r in mesh_rows)),
                             overlap_closed7=len(overlap),closed7_outside_report98=len(previous_keys-now),additional_refs_beyond7=len(now-previous_keys)),
                source_pins=pins,lineage='Shared ef report98/raw l3-chain UnityPy capture and C# dump. Own streamed SHA/row/identity-qualified grep; no Graph or invented fields/default meshes.')


def load():
    v=json.loads(gzip.decompress(SELECTED.read_bytes()))
    for p,h in v['source_pins'].items():
        if sha_file(ROOT/p)!=h:raise ValueError('gaps source pin drift:'+p)
    return v


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args();v=select();body=gzip.compress(canonical(v)+b'\n',mtime=0)
    if a.check:
        if SELECTED.read_bytes()!=body:raise SystemExit('gaps selection drift')
    else:RAW.mkdir(parents=True,exist_ok=True);SELECTED.write_bytes(body)
    print(v['summary'])
