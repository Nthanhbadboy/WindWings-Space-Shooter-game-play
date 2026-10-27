"""Disk-backed union of captured Sprite references and exact parent/root context.
provenance: arena/8141386a-windwings-space-shooter-game-p
Native census != captured-context completeness. No Graph/name-derived parenting.
"""
from __future__ import annotations
from collections import Counter
import gzip
import json
from tools.verify.geometry_8141386a_atlas_io import ROOT,canonical,full_file,key,identity
from tools.verify.geometry_8141386a_consumers_sources import SOURCES


def resolve(file,pointer,externals):
    if pointer is None:return None
    if not isinstance(pointer,dict) or 'm_FileID' not in pointer or 'm_PathID' not in pointer:raise ValueError('malformed captured context PPtr')
    if not pointer['m_PathID']:return None
    fid=pointer['m_FileID']
    if not 0<=fid<=len(externals[file]):raise ValueError('captured owning-file PPtr out of range')
    return (file if fid==0 else full_file(externals[file][fid-1]['path']),pointer['m_PathID'])


def ingest(db):
    db.executescript('''
    CREATE TABLE cap_objects(file TEXT,pid INTEGER,sha TEXT,kind TEXT,cls TEXT,go_file TEXT,go_pid INTEGER,name TEXT,parent_file TEXT,parent_pid INTEGER,context_error TEXT,PRIMARY KEY(file,pid));
    CREATE TABLE cap_refs(file TEXT,pid INTEGER,field TEXT,target_file TEXT,target_pid INTEGER,pointer TEXT,locations TEXT,PRIMARY KEY(file,pid,field));
    CREATE TABLE cap_aliases(file TEXT,pid INTEGER,kind TEXT,label TEXT,sources TEXT,PRIMARY KEY(file,pid,kind,label));
    ''')
    counts=Counter()
    for source in SOURCES:
        base=ROOT/'reverse-engineering/raw'/source;idx=json.loads((base/'index.json').read_bytes());externals={r['serialized_file']:r['externals'] for r in idx['files']}
        def rows(group):
            for part in idx[group]:
                n=0
                with gzip.open(base/part['path'],'rb') as h:
                    for i,line in enumerate(h):
                        n+=1;yield json.loads(line),dict(dataset=source,path=str((base/part['path']).relative_to(ROOT)),row=i)
                if n!=part['rows']:raise ValueError('captured context row count drift')
        for r,loc in rows('objects'):
            k=key(r);old=db.execute('SELECT sha,kind FROM cap_objects WHERE file=? AND pid=?',k).fetchone()
            if old:
                if old!=(r['raw_object_sha256'],r['type']):raise ValueError('cross-capture original hash/type conflict:'+str(k))
                counts['object_overlap_equal']+=1;continue
            t=dict(r.get('tree',{}));t.update(r.get('header',{}));go=parent=None;error=None
            try:
                if r['type'] not in ('GameObject','Sprite','SpriteAtlas','AnimationClip','Texture2D'):go=resolve(k[0],t.get('m_GameObject'),externals)
                if r['type']in ('Transform','RectTransform'):parent=resolve(k[0],t.get('m_Father'),externals)
            except ValueError as e:error=str(e)
            db.execute('INSERT INTO cap_objects VALUES(?,?,?,?,?,?,?,?,?,?,?)',(*k,r['raw_object_sha256'],r['type'],r.get('class_name'),go[0] if go else None,go[1] if go else None,t.get('m_Name') if r['type']=='GameObject' else None,parent[0] if parent else None,parent[1] if parent else None,error))
            counts['unique_captured_objects']+=1
        for r,loc in rows('links'):
            if r['status']!='resolved' or r['target']['type']!='Sprite':continue
            owner=key(r['owner']);target=key(r['target']);actual=resolve(owner[0],r['pointer'],externals)
            if actual!=target:raise ValueError('captured Sprite edge differs from exact owner-file PPtr')
            old=db.execute('SELECT target_file,target_pid,pointer,locations FROM cap_refs WHERE file=? AND pid=? AND field=?',(*owner,r['location'])).fetchone()
            if old:
                if old[:3]!=(target[0],target[1],canonical(r['pointer']).decode()):raise ValueError('cross-capture Sprite edge conflict')
                locations=json.loads(old[3]);locations.append(loc);db.execute('UPDATE cap_refs SET locations=? WHERE file=? AND pid=? AND field=?',(canonical(locations).decode(),*owner,r['location']));counts['sprite_edge_overlap_equal']+=1
            else:
                db.execute('INSERT INTO cap_refs VALUES(?,?,?,?,?,?,?)',(*owner,r['location'],*target,canonical(r['pointer']).decode(),canonical([loc]).decode()));counts['unique_captured_sprite_edges']+=1
        aliases=[]
        for r in idx['roots']:
            if r.get('target',{}).get('type')!='GameObject':continue
            label=r.get('label') or r.get('resource')
            if label:aliases.append((key(r['target']),r.get('kind','indexed_root'),label))
        for r in idx['resource_roots']:
            if r.get('status')=='resolved' and r.get('target',{}).get('type')=='GameObject':aliases.append((key(r['target']),'resource',r['resource']))
        for k,kind,label in aliases:
            old=db.execute('SELECT sources FROM cap_aliases WHERE file=? AND pid=? AND kind=? AND label=?',(*k,kind,label)).fetchone();sources=json.loads(old[0]) if old else []
            if source not in sources:sources.append(source)
            db.execute('INSERT OR REPLACE INTO cap_aliases VALUES(?,?,?,?,?)',(*k,kind,label,canonical(sources).decode()))
        db.commit()
    counts['root_aliases']=db.execute('SELECT count(*) FROM cap_aliases').fetchone()[0]
    return dict(counts)


def context(db,native_go):
    start=key(native_go['identity']);captured=db.execute('SELECT sha FROM cap_objects WHERE file=? AND pid=?',start).fetchone()
    if captured and captured[0]!=native_go['object_sha256']:raise ValueError('fresh GO hash differs from captured context')
    candidates=native_go['transform_candidates'];aliases=[];path=[];seen=set();alias_keys=set();status='CAPTURED_TRANSFORM_ABSENT';tr=None
    def add_aliases(go):
        for kind,label,sources in db.execute('SELECT kind,label,sources FROM cap_aliases WHERE file=? AND pid=? ORDER BY kind,label',go):
            k=(*go,kind,label)
            if k in alias_keys:continue
            alias_keys.add(k);aliases.append(dict(gameobject=identity(go),kind=kind,label=label,capture_sources=json.loads(sources)))
    add_aliases(start)
    if len(candidates)==1:tr=key(candidates[0])
    elif len(candidates)!=1:return dict(status='NATIVE_TRANSFORM_CARDINALITY_NOT_ONE',root_aliases=aliases,source_path=None)
    while tr is not None:
        if tr in seen:return dict(status='CAPTURED_PARENT_CYCLE',root_aliases=aliases,source_path=None)
        if len(seen)>=256:return dict(status='CAPTURED_PARENT_DEPTH_BUDGET',root_aliases=aliases,source_path=None)
        seen.add(tr);row=db.execute('SELECT go_file,go_pid,parent_file,parent_pid,context_error FROM cap_objects WHERE file=? AND pid=? AND kind IN (\'Transform\',\'RectTransform\')',tr).fetchone()
        if row is None:break
        if row[4]:status='CAPTURED_PARENT_POINTER_ERROR';break
        go=(row[0],row[1]);g=db.execute('SELECT name FROM cap_objects WHERE file=? AND pid=? AND kind=\'GameObject\'',go).fetchone()
        if not path and go!=start:raise ValueError('captured Transform GO differs from fresh native GO')
        path.append(dict(identity=identity(go),name=g[0] if g else None))
        add_aliases(go)
        tr=(row[2],row[3]) if row[2] is not None else None;status='COMPLETE_CAPTURED_PARENT_CHAIN' if tr is None else 'PARTIAL_CAPTURED_PARENT_CHAIN'
    return dict(status=status,root_aliases=aliases,source_path=list(reversed(path)) if path else None,
                scope='Captured exact PPtr ancestry/indexed aliases only; not runtime instantiation, Resource.Load, placement or visibility')


def reference_category(kind,go_file):
    if kind=='SpriteRenderer':return 'NATIVE_RENDERER_CROSSCHECK'
    if kind=='SpriteAtlas':return 'ATLAS_MEMBERSHIP_NOT_USAGE'
    if kind=='AnimationClip':return 'ANIMATION_MAPPING_NOT_ACTIVE_SELECTION'
    return 'SERIALIZED_COMPONENT_REFERENCE' if go_file is not None else 'SERIALIZED_ASSET_REFERENCE'
