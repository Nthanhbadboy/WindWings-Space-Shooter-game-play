"""Read-only full original native SpriteRenderer census, streamed250-row shards.
provenance: arena/8141386a-windwings-space-shooter-game-p
Bounded compressed mmap/one metadata table, disk SQLite, one renderer/GO at a time.
Supplied native schemas + full inverse equality, not native execution/schema discovery.
"""
from __future__ import annotations
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tools.verify.geometry_8141386a_atlas_io import BRANCH,canonical,sha,sha_file,scratch,identity,full_file
from tools.verify.geometry_8141386a_atlas_sources import XAPK,APK,DATA,APK_MEMBER
from tools.verify.geometry_8141386a_consumers_sources import RAW,SCHEMAS,INPUTS,CATALOG,load_inputs,catalog
from tools.recovery.geometry_8141386a_atlas_bytes import Bundle
from tools.verify.serialized110_binary import header,parse
from tools.verify.controller109_binary import Reader
from tools.verify.l3_geometry_8141386a_gaps_binary import encode


def recovered(blob,schema):
    r=Reader(blob,max_items=100000);tree=r.decode(schema)
    if encode(schema,tree)!=blob:raise ValueError('native supplied-schema inverse does not equal complete original object')
    spans={s['field']:dict(offset=s['start'],size=s['end']-s['start'],sha256=sha(blob[s['start']:s['end']])) for s in r.root_spans}
    return tree,spans


def recover(xapk):
    inputs=load_inputs();schemas=json.loads(gzip.decompress(SCHEMAS.read_bytes()))
    if sha_file(xapk)!=XAPK:raise ValueError('original XAPK SHA mismatch')
    with scratch('consumer-original-') as directory:
        apk=directory/'base.apk';bundle_path=directory/'data.unity3d'
        with zipfile.ZipFile(xapk) as outer,outer.open(APK_MEMBER) as src,apk.open('wb') as dst:shutil.copyfileobj(src,dst,1024*1024)
        if sha_file(apk)!=APK:raise ValueError('original base APK SHA mismatch')
        with zipfile.ZipFile(apk) as inner,inner.open('assets/bin/Data/data.unity3d') as src,bundle_path.open('wb') as dst:shutil.copyfileobj(src,dst,1024*1024)
        if sha_file(bundle_path)!=DATA:raise ValueError('original bundle SHA mismatch')
        db=sqlite3.connect(directory/'native.sqlite');db.execute('PRAGMA cache_size=-4096')
        db.execute('CREATE TABLE objects(file TEXT,pid INTEGER,class INTEGER,offset INTEGER,size INTEGER,PRIMARY KEY(file,pid))')
        db.execute('CREATE TABLE gameobjects(file TEXT,pid INTEGER,value TEXT,PRIMARY KEY(file,pid))')
        db.execute('CREATE TABLE sprites(file TEXT,pid INTEGER,sha TEXT,PRIMARY KEY(file,pid))')
        db.executemany('INSERT INTO sprites VALUES(?,?,?)',[(r['identity']['serialized_file'],r['identity']['path_id'],r['original_object_sha256']) for r in catalog()])
        bundle=Bundle(bundle_path)
        try:
            files={};native_counts={};metadata_total=0
            for n in sorted(bundle.frame['nodes'],key=lambda n:n['path']):
                file='data.unity3d/'+n['path']
                if file not in inputs['expected_original_sprite_renderer_counts']:continue
                h=header(bundle.read(n['offset'],48))
                if h['data_offset']>32*1024*1024 or h['file_size']!=n['size'] or h['endian']!='<':raise ValueError('unsupported metadata extent/budget/endian')
                prefix=bundle.read(n['offset'],h['data_offset']);t=parse(prefix)
                if t['unity_version']!=schemas['version']:raise ValueError('native schema version differs from original file declaration')
                files[file]=dict(serialized_file=file,node=n,header=h,unity_version=t['unity_version'],externals=t['externals'],metadata_prefix_sha256=sha(prefix),object_count=len(t['objects']))
                native_counts[file]=sum(e['class_id']==212 for e in t['objects']);metadata_total+=len(t['objects'])
                for first in range(0,len(t['objects']),250):
                    db.executemany('INSERT INTO objects VALUES(?,?,?,?,?)',[(file,e['path_id'],e['class_id'],n['offset']+e['byte_start'],e['byte_size']) for e in t['objects'][first:first+250]])
                db.commit();del t,prefix
            if native_counts!=inputs['expected_original_sprite_renderer_counts']:raise ValueError('fresh complete original class212 metadata census differs')
            counts=Counter();target_files=Counter();shards=[];batch=[]
            def resolve(owner,p):
                if not p['m_PathID']:return None
                fid=p['m_FileID']
                if not 0<=fid<=len(files[owner]['externals']):raise ValueError('invalid original owning-file PPtr ID')
                return (owner if fid==0 else full_file(files[owner]['externals'][fid-1]['path']),p['m_PathID'])
            def entry(k):
                row=db.execute('SELECT class,offset,size FROM objects WHERE file=? AND pid=?',k).fetchone()
                if row is None:raise ValueError('original PPtr object target not in pinned bundle metadata:'+str(k))
                return row
            def gameobject(k):
                cached=db.execute('SELECT value FROM gameobjects WHERE file=? AND pid=?',k).fetchone()
                if cached:return json.loads(cached[0])
                cls,offset,size=entry(k)
                if cls!=1:raise ValueError('renderer original m_GameObject target class is not GameObject')
                blob=bundle.read(offset,size);t,spans=recovered(blob,schemas['classes']['1']);transforms=[]
                for c in t['m_Component']:
                    p=c['component'];target=resolve(k[0],p)
                    if target is not None and entry(target)[0] in (4,224):transforms.append(identity(target))
                value=dict(identity=identity(k),name=t['m_Name'],layer=t['m_Layer'],active_self=t['m_IsActive'],object_sha256=sha(blob),object_size=size,
                           transform_candidates=transforms,typed_name_span=spans['m_Name'],complete_inverse_equal=True)
                db.execute('INSERT INTO gameobjects VALUES(?,?,?)',(*k,canonical(value).decode()));return value
            def flush():
                if not batch:return
                name=f'native-renderers-{len(shards):04d}.jsonl.gz';p=RAW/name
                with p.open('wb') as h,gzip.GzipFile(fileobj=h,filename='',mode='wb',mtime=0,compresslevel=9) as out:
                    for r in batch:out.write(canonical(r)+b'\n')
                if p.stat().st_size>=5_000_000:raise ValueError('native renderer shard exceeds5MB')
                shards.append(dict(path=name,rows=len(batch),sha256=sha_file(p),first=batch[0]['identity'],last=batch[-1]['identity']));batch.clear();db.commit()
            rows=db.execute('SELECT file,pid,offset,size FROM objects WHERE class=212 ORDER BY file,pid')
            for file,pid,offset,size in rows:
                blob=bundle.read(offset,size);t,spans=recovered(blob,schemas['classes']['212']);go=resolve(file,t['m_GameObject']);target=resolve(file,t['m_Sprite'])
                if go is None:raise ValueError('native SpriteRenderer has null GameObject; do not invent context')
                g=gameobject(go);sprite=None;status='NULL_SPRITE'
                if target is not None:
                    e=entry(target)
                    if e[0]!=213:raise ValueError('native m_Sprite target is not actual class213')
                    expected=db.execute('SELECT sha FROM sprites WHERE file=? AND pid=?',target).fetchone()
                    if expected is None:raise ValueError('native Sprite target outside complete captured Sprite inventory')
                    sprite=dict(identity=identity(target),original_sprite_sha256=expected[0]);status='EXACT_ORIGINAL_SPRITE_IDENTITY';target_files[target[0]]+=1
                counts['renderers']+=1;counts[status]+=1;counts['enabled_true']+=bool(t['m_Enabled'])
                r=dict(identity=identity((file,pid)),object_sha256=sha(blob),object_size=size,complete_inverse_equal=True,
                       gameobject_pointer=t['m_GameObject'],gameobject=g,sprite_pointer=t['m_Sprite'],sprite=sprite,status=status,
                       original_sprite_pointer_span=spans['m_Sprite'],original_gameobject_pointer_span=spans['m_GameObject'],
                       serialized_enabled=t['m_Enabled'],serialized_draw_mode=t['m_DrawMode'],serialized_color=t['m_Color'],
                       source_context='SERIALIZED_SCENE_NOT_RUNTIME' if file in {f'data.unity3d/level{i}' for i in range(4)} else 'ASSET_FILE_NOT_RUNTIME_PLACEMENT')
                batch.append(r)
                if len(batch)==250:flush()
            flush()
            counts['unique_gameobjects']=db.execute('SELECT count(*) FROM gameobjects').fetchone()[0]
            if counts['renderers']!=sum(native_counts.values()):raise ValueError('complete renderer decode count differs from metadata')
            paths=['tools/recovery/geometry_8141386a_consumers_bytes.py','tools/verify/geometry_8141386a_consumers_sources.py','tools/verify/geometry_8141386a_atlas_io.py',
                   'tools/recovery/geometry_8141386a_atlas_bytes.py','tools/verify/controller109_binary.py','tools/verify/l3_geometry_8141386a_gaps_binary.py','tools/verify/serialized110_binary.py','tools/verify/unityfs111_binary.py',
                   str(INPUTS.relative_to(ROOT)),str(CATALOG.relative_to(ROOT)),str(SCHEMAS.relative_to(ROOT))]
            value=dict(schema=1,item=118,provenance=BRANCH,xapk_sha256=XAPK,apk_sha256=APK,bundle_sha256=DATA,files=list(files.values()),
                       original_class212_counts=native_counts,metadata_objects=metadata_total,summary=dict(counts),target_files=dict(target_files),shards=shards,
                       schema_sha256=sha_file(SCHEMAS),tool_pins={p:sha_file(ROOT/p) for p in paths},
                       scope='All class212 objects in all original bundle SerializedFiles, exact native m_Sprite/GO fields and supplied-schema full inverse bytes. Fresh GO names are literal source context, not semantic asset labels. No world hierarchy/placement/runtime/render claim.',
                       memory='Compressed mmap<=16blocks; one metadata file/one renderer/oneGO;SQLite4MiB cache;250-row output shards, no Graph/all-Sprite fixture.')
            (RAW/'native-index.json').write_bytes(canonical(value)+b'\n');print(value['summary'],'shards',len(shards),flush=True)
        finally:bundle.close();db.close()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--xapk',type=Path,required=True);recover(p.parse_args().xapk)
