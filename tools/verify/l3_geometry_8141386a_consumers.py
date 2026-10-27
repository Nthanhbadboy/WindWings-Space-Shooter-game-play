"""Report118 reverse Sprite index: full native renderer census + captured context.
provenance: arena/8141386a-windwings-space-shooter-game-p
No Graph, guessed asset semantics, runtime placement/use or all-consumer claim.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import gzip
import json
import sqlite3
from tools.verify.geometry_8141386a_atlas_io import ROOT,BRANCH,canonical,key,identity,sha_file,sha,scratch,write_document,iter_arrays,full_file
from tools.verify.geometry_8141386a_consumers_sources import RAW,INPUTS,CATALOG,SCHEMAS,catalog,load_inputs
from tools.verify.geometry_8141386a_consumers_context import ingest,context,reference_category

INDEX=RAW/'native-index.json'
CI=RAW/'source-ci-receipt.json.gz'
OUTPUT=ROOT/'datas/l3_geometry_sprite_consumers_8141386a.json.gz'


def native_rows(index):
    for part in index['shards']:
        p=RAW/part['path']
        if sha_file(p)!=part['sha256']:raise ValueError('native renderer source shard SHA drift')
        n=0
        with gzip.open(p,'rb') as h:
            for i,line in enumerate(h):
                n+=1;yield json.loads(line),dict(path=str(p.relative_to(ROOT)),row=i)
        if n!=part['rows']:raise ValueError('native renderer source row count drift')


def build(output):
    inputs=load_inputs();index=json.loads(INDEX.read_bytes());ci=json.loads(gzip.decompress(CI.read_bytes()))
    if index['provenance']!=BRANCH or index['summary']['renderers']!=inputs['expected_original_sprite_renderers']:raise ValueError('native complete class212 provenance/count mismatch')
    if ci['native_index_sha256']!=sha_file(INDEX) or ci['run']['head_sha']!='2beef6d63aba60732eb5b726ae4281f06f0c41bd' or ci['run']['conclusion']!='success' or ci['run']['status']!='completed':raise ValueError('require actual original-source completed GREEN receipt')
    for p,h in index['tool_pins'].items():
        if sha_file(ROOT/p)!=h:raise ValueError('native original source code/schema pin drift:'+p)
    with scratch('consumer-join-') as directory:
        db=sqlite3.connect(directory/'join.sqlite');db.execute('PRAGMA cache_size=-4096')
        db.executescript('''
        CREATE TABLE sprites(file TEXT,pid INTEGER,value TEXT,PRIMARY KEY(file,pid));
        CREATE TABLE native(file TEXT,pid INTEGER,sprite_file TEXT,sprite_pid INTEGER,go_file TEXT,go_pid INTEGER,location TEXT,PRIMARY KEY(file,pid));
        CREATE TABLE roots(sprite_file TEXT,sprite_pid INTEGER,root_file TEXT,root_pid INTEGER,kind TEXT,label TEXT,renderer_file TEXT,renderer_pid INTEGER,PRIMARY KEY(sprite_file,sprite_pid,root_file,root_pid,kind,label,renderer_file,renderer_pid));
        ''')
        for r in catalog():db.execute('INSERT INTO sprites VALUES(?,?,?)',(*key(r['identity']),canonical(r).decode()))
        captured=ingest(db);counts=Counter();context_status=Counter();file_counts=Counter();native_bytes=0
        for r,loc in native_rows(index):
            rk=key(r['identity']);s=key(r['sprite']['identity']) if r['sprite'] else None;g=r['gameobject'];gk=key(g['identity'])
            if not r['complete_inverse_equal'] or not g['complete_inverse_equal']:raise ValueError('native row not whole original inverse-equal')
            if s:
                cat=db.execute('SELECT value FROM sprites WHERE file=? AND pid=?',s).fetchone()
                if cat is None or json.loads(cat[0])['original_object_sha256']!=r['sprite']['original_sprite_sha256']:raise ValueError('native Sprite target SHA/catalog identity mismatch')
            old=db.execute('SELECT sha FROM cap_objects WHERE file=? AND pid=?',rk).fetchone()
            if old:
                if old[0]!=r['object_sha256']:raise ValueError('captured/native renderer whole hash differs')
                counts['captured_native_owner_hash_matches']+=1
            edge=db.execute('SELECT target_file,target_pid FROM cap_refs WHERE file=? AND pid=? AND field=\'.m_Sprite\'',rk).fetchone()
            if edge:
                if s!=tuple(edge):raise ValueError('captured/native renderer m_Sprite differs')
                counts['captured_native_sprite_edge_matches']+=1
            c=context(db,g);context_status[c['status']]+=1
            if s:
                for a in c['root_aliases']:
                    root=key(a['gameobject']);db.execute('INSERT OR IGNORE INTO roots VALUES(?,?,?,?,?,?,?,?)',(*s,*root,a['kind'],a['label'],*rk))
            db.execute('INSERT INTO native VALUES(?,?,?,?,?,?,?)',(*rk,s[0] if s else None,s[1] if s else None,*gk,canonical(loc).decode()))
            counts['original_native_renderers']+=1;counts['nonnull_native_sprite_refs' if s else 'null_native_sprite_refs']+=1;file_counts[rk[0]]+=1;native_bytes+=r['object_size']
            if counts['original_native_renderers']%250==0:db.commit()
        db.executescript('CREATE INDEX native_sprite ON native(sprite_file,sprite_pid);CREATE INDEX cap_target ON cap_refs(target_file,target_pid);CREATE INDEX root_sprite ON roots(sprite_file,sprite_pid);');db.commit()
        other_categories=Counter();source_pins=dict(inputs['source_pins'],**index['tool_pins'])
        paths=[INPUTS,CATALOG,SCHEMAS,INDEX,CI,ROOT/'tools/verify/l3_geometry_8141386a_consumers.py',ROOT/'tools/verify/geometry_8141386a_consumers_context.py']
        paths += [RAW/p['path'] for p in index['shards']]
        source_pins.update({str(p.relative_to(ROOT)):sha_file(p) for p in paths})
        def sprite_rows():
            for file,pid,value in db.execute('SELECT file,pid,value FROM sprites ORDER BY file,pid'):
                r=json.loads(value);byfile=defaultdict(list)
                target=db.execute('SELECT sha,kind FROM cap_objects WHERE file=? AND pid=?',(file,pid)).fetchone()
                if target is not None and target!=(r['original_object_sha256'],'Sprite'):raise ValueError('captured Sprite target identity/hash disagrees with original catalog')
                for owner_file,owner_pid in db.execute('SELECT file,pid FROM native WHERE sprite_file=? AND sprite_pid=? ORDER BY file,pid',(file,pid)):byfile[owner_file].append(owner_pid)
                extra=[];membership=[]
                for owner,oid,field,pointer,locations,kind,cls,go_file,owner_sha in db.execute('SELECT r.file,r.pid,r.field,r.pointer,r.locations,o.kind,o.cls,o.go_file,o.sha FROM cap_refs r JOIN cap_objects o ON r.file=o.file AND r.pid=o.pid WHERE r.target_file=? AND r.target_pid=? ORDER BY r.file,r.pid,r.field',(file,pid)):
                    category=reference_category(kind,go_file)
                    if category=='NATIVE_RENDERER_CROSSCHECK':
                        if field!='.m_Sprite':raise ValueError('native renderer unexpected captured Sprite field')
                        continue
                    item=dict(owner=identity((owner,oid)),owner_type=kind,class_name=cls,field=field,pointer=json.loads(pointer),owner_captured_sha256=owner_sha,source_locations=json.loads(locations),category=category)
                    (membership if category=='ATLAS_MEMBERSHIP_NOT_USAGE' else extra).append(item);other_categories[category]+=1
                roots=[];group=None;entry=None
                for rf,rp,kind,label,of,op in db.execute('SELECT root_file,root_pid,kind,label,renderer_file,renderer_pid FROM roots WHERE sprite_file=? AND sprite_pid=? ORDER BY root_file,root_pid,kind,label,renderer_file,renderer_pid',(file,pid)):
                    k=(rf,rp,kind,label)
                    if k!=group:
                        entry=dict(root=identity((rf,rp)),kind=kind,label=label,native_renderer_ids_by_file={});roots.append(entry);group=k
                    entry['native_renderer_ids_by_file'].setdefault(of,[]).append(op)
                n=sum(len(v) for v in byfile.values());counts['sprites_with_native_renderer_refs']+=bool(n);counts['sprites_with_captured_additional_refs']+=bool(extra);counts['sprites_with_any_scoped_reference']+=bool(n or extra)
                yield dict(**r,native_renderer_count=n,native_renderer_ids_by_file=dict(byfile),captured_additional_references=extra,atlas_memberships_not_usage=membership,
                           captured_root_associations=roots,meaning_label=None,
                           coverage='SCOPED_STATIC_REFERENCE_FOUND' if n or extra else 'NO_REFERENCE_IN_QUERIED_NATIVE_AND_CAPTURED_SLICES_NOT_GLOBAL_UNUSED')
        # The writer consumes the generator before the final summary trailer, so
        # every count is measured rather than computed from unconsumed generators.
        def summary_rows():
            yield dict(counts=dict(counts),native_by_file=dict(file_counts),native_original_bytes=native_bytes,captured_union=captured,captured_context_status=dict(context_status),
                       captured_additional_reference_categories=dict(other_categories),native_gameobjects=index['summary']['unique_gameobjects'])
        header=dict(schema=1,item=118,task='MISSING-row16 sprite-consumer follow-up',provenance=BRANCH,status='ORIGINAL_NATIVE_SPRITERENDERER_CENSUS_PLUS_CAPTURED_OTHER_REFERENCE_CONTEXT_NOT_RUNTIME',
                    source=dict(xapk_sha256=index['xapk_sha256'],apk_sha256=index['apk_sha256'],bundle_sha256=index['bundle_sha256'],original_source_run=ci['run']['id'],native_index_sha256=sha_file(INDEX)),
                    sprite_catalog_count=inputs['sprite_count'],source_pins=source_pins,
                    limits=['Full original class212 census is not all consumer classes. MonoBehaviour/UI/asset/animation references and ancestors are only queried captured closures.',
                            'GO names and resource/UI aliases are literal serialized labels, not guessed asset meanings, loaded prefab instances or runtime visibility.',
                            'Atlas membership is not consumer use; AnimationClip mapping is not active selection. No-reference here is not globally unused.',
                            'Supplied native schema/full inverse equality is byte corroboration, not independently discovered schema or native/Unity readback/render.'],
                    lineage='Frozen own#6 native Sprite catalog/original corroboration, ef111/110 framing, own bounded mmap+SQLite collector, native TPK schema/std109 Reader/own#8 inverse writer; captured raw98/raw102 context union, no Graph.')
        write_document(output,header,[('sprites',sprite_rows()),('summary',summary_rows())]);db.close()
    if output.stat().st_size>=5_000_000:raise ValueError('compact consumer artifact exceeds5MB; split output before commit')


def sprite_probe(file,pid):
    target=(full_file(file),pid)
    for _,_,r in iter_arrays(OUTPUT,{'sprites'}):
        if key(r['identity'])==target:return r
    raise ValueError('exact native Sprite identity absent')


def renderer_probe(file,pid):
    k=(full_file(file),pid);index=json.loads(INDEX.read_bytes())
    for part in index['shards']:
        if key(part['first'])<=k<=key(part['last']):
            if sha_file(RAW/part['path'])!=part['sha256']:raise ValueError('renderer proof shard SHA drift')
            with gzip.open(RAW/part['path'],'rb') as h:
                for i,line in enumerate(h):
                    row=json.loads(line)
                    if key(row['identity'])==k:
                        row['raw_location']=dict(path=str((RAW/part['path']).relative_to(ROOT)),row=i);return row
    raise ValueError('exact native renderer identity absent; no name/PID-only fallback')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');p.add_argument('--sprite-file');p.add_argument('--sprite-id',type=int);p.add_argument('--renderer-file');p.add_argument('--renderer-id',type=int);a=p.parse_args()
    if a.renderer_file is not None:
        if a.renderer_id is None:p.error('--renderer-id required')
        print(json.dumps(renderer_probe(a.renderer_file,a.renderer_id),indent=2));return
    if a.sprite_file is not None:
        if a.sprite_id is None:p.error('--sprite-id required')
        print(json.dumps(sprite_probe(a.sprite_file,a.sprite_id),indent=2));return
    with scratch('consumer-output-') as d:
        out=d/'result.gz';build(out)
        if a.check:
            if sha_file(out)!=sha_file(OUTPUT):raise SystemExit('sprite-consumer artifact drift')
        else:out.replace(OUTPUT)
    for _,_,r in iter_arrays(OUTPUT,{'summary'}):print(r)
    print('artifact',OUTPUT.stat().st_size,'SHA256',sha_file(OUTPUT))


if __name__=='__main__':main()
