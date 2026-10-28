"""Generate bounded raw verification receipt for R2 review of AI-3 row16/report118."""
import argparse,gzip,hashlib,json,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
COMMIT='e3fbb4dbc679c5d07ff8c520f8e13827baeae53c'
REPORT='docs/apk-analysis/118-geometry-sprite-consumers-arena-8141386a-windwings-space-shooter-game-p.md'
ARTIFACT='datas/l3_geometry_sprite_consumers_8141386a.json.gz'
SCHEMAS='reverse-engineering/raw/geometry-8141386a/sprite-consumers/native-schemas.json.gz'
INDEX='reverse-engineering/raw/geometry-8141386a/sprite-consumers/native-index.json'
RAW=ROOT/'reverse-engineering/raw/l3-ef6b75ef125-review-row16-118'
def sha(b):return hashlib.sha256(b).hexdigest()
def git_show(path):return subprocess.check_output(['git','show',f'{COMMIT}:{path}'])
def tree():
    out=subprocess.check_output(['git','ls-tree','-r','-z',COMMIT]);m={}
    for e in out.split(b'\0'):
        if not e:continue
        meta,path=e.split(b'\t',1);mode,typ,oid=meta.split()
        if typ==b'blob':m[path.decode()]=oid.decode()
    return m
def batch_blobs(oids):
    data=subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(oids)+'\n').encode())
    pos=0;out={}
    for oid in oids:
        e=data.index(b'\n',pos);h=data[pos:e].split();assert h[0].decode()==oid and h[1]==b'blob',(oid,h)
        size=int(h[2]);blob=data[e+1:e+1+size];out[oid]=blob;pos=e+1+size+1
    assert pos==len(data),(pos,len(data))
    return out
def identity(x):return (x['serialized_file'],x['path_id'])
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    assert subprocess.check_output(['git','rev-parse',COMMIT]).decode().strip()==COMMIT
    RAW.mkdir(parents=True,exist_ok=True)
    report=git_show(REPORT);artifact=git_show(ARTIFACT)
    assert sha(artifact)=='c33ad8a80c35990cf5dd94165234878a62785a5bb39ddef5f2bb73752408019d'
    (RAW/'peer-report.md').write_bytes(report);(RAW/'peer-artifact.json.gz').write_bytes(artifact)
    peer=json.loads(gzip.decompress(artifact))
    pins=peer['source_pins'];m=tree();missing=sorted(set(pins)-set(m))
    assert not missing,missing[:5]
    oid_paths={}
    for path in pins:oid_paths.setdefault(m[path],[]).append(path)
    blobs=batch_blobs(sorted(oid_paths))
    by_path={path:blobs[m[path]] for path in pins}
    verified=[]
    for path in sorted(pins):
        h=sha(by_path[path]);verified.append(dict(path=path,expected_sha256=pins[path],observed_sha256=h,git_blob_oid=m[path],size=len(by_path[path]),match=pins[path]==h))
    assert all(x['match'] for x in verified) and len(verified)==len(pins)
    dataset_counts=dict(new_native_renderer_shards=0,geometry_8141386a_other=0,l3_chain_context=0,l3_visual_surface_context=0,sprite_geometry_catalog=0,tool_pins=0,other=0)
    for path in pins:
        if 'sprite-consumers/native-renderers-' in path and path.endswith('.jsonl.gz'):dataset_counts['new_native_renderer_shards']+=1
        elif path.startswith('reverse-engineering/raw/geometry-8141386a/'):dataset_counts['geometry_8141386a_other']+=1
        elif path.startswith('reverse-engineering/raw/l3-chain/'):dataset_counts['l3_chain_context']+=1
        elif path.startswith('reverse-engineering/raw/l3-visual-surface/'):dataset_counts['l3_visual_surface_context']+=1
        elif path.startswith('reverse-engineering/raw/sprite-geometry/'):dataset_counts['sprite_geometry_catalog']+=1
        elif path.startswith('tools/'):dataset_counts['tool_pins']+=1
        else:dataset_counts['other']+=1
    assert dataset_counts==dict(new_native_renderer_shards=252,geometry_8141386a_other=6,l3_chain_context=901,l3_visual_surface_context=411,sprite_geometry_catalog=7,tool_pins=10,other=0)
    shard_paths=sorted(k for k in pins if 'sprite-consumers/native-renderers-' in k and k.endswith('.jsonl.gz'))
    assert len(shard_paths)==252
    shards=[];renderer_ids=set();go_ids=set();file_counts={};status_counts={};context_counts={};context_by_file={};total_rows=0;total_bytes=0;total_object_size=0;null_sprites=0;nonnull_sprites=0;enabled_true=0;scene_rows=0;asset_rows=0;class_id_field_present=False;row_keys_sample=None;gameobject_keys_sample=None
    for path in shard_paths:
        blob=by_path[path];total_bytes+=len(blob);rows=[json.loads(x) for x in gzip.decompress(blob).splitlines()];total_rows+=len(rows)
        if row_keys_sample is None:
            row_keys_sample=sorted(rows[0].keys());gameobject_keys_sample=sorted(rows[0]['gameobject'].keys())
        complete=sum(bool(r.get('complete_inverse_equal')) for r in rows);go_complete=sum(bool((r.get('gameobject') or {}).get('complete_inverse_equal')) for r in rows)
        size196=sum(r.get('object_size')==196 for r in rows);total_object_size+=sum(r.get('object_size',0) for r in rows)
        sc={};fc={};cc={}
        for r in rows:
            renderer_ids.add(identity(r['identity']));go_ids.add(identity(r['gameobject']['identity']))
            if 'class_id' in r or 'class_id' in r['gameobject']:class_id_field_present=True
            f=r['identity']['serialized_file'];fc[f]=fc.get(f,0)+1;file_counts[f]=file_counts.get(f,0)+1
            if f.startswith('data.unity3d/level'):scene_rows+=1
            else:asset_rows+=1
            s=r['status'];sc[s]=sc.get(s,0)+1;status_counts[s]=status_counts.get(s,0)+1
            c=r['source_context'];cc[c]=cc.get(c,0)+1;context_counts[c]=context_counts.get(c,0)+1;context_by_file[f]=c
            if r.get('serialized_enabled'):enabled_true+=1
            sr=r.get('sprite');ptr=r.get('sprite_pointer') or {}
            if sr is None or ptr.get('m_PathID')==0:null_sprites+=1
            else:nonnull_sprites+=1
            assert (s=='NULL_SPRITE')==(sr is None)
        shards.append(dict(path=path,sha256=sha(blob),compressed_size=len(blob),row_count=len(rows),complete_inverse_equal=complete,gameobject_inverse_equal=go_complete,object_size_196=size196,status_counts=sc,file_counts=fc,context_counts=cc))
    hist={}
    for s in shards:hist[str(s['row_count'])]=hist.get(str(s['row_count']),0)+1
    catalog=peer['sprites'];coverage={};native_refs=0;additional_refs=0;overlap=0;union=0;additional_categories={};root_rows=0;root_assoc=0;root_tuples=set();no_ref=0;no_ref_clean=0;no_ref_with_atlas=0
    for s in catalog:
        c=s['coverage'];coverage[c]=coverage.get(c,0)+1
        n=s['native_renderer_count']>0;a=len(s['captured_additional_references'])>0;native_refs+=n;additional_refs+=a;overlap+=n and a;union+=n or a
        for z in s['captured_additional_references']+s['atlas_memberships_not_usage']:additional_categories[z['category']]=additional_categories.get(z['category'],0)+1
        if s['captured_root_associations']:
            root_rows+=1;root_assoc+=len(s['captured_root_associations'])
            for z in s['captured_root_associations']:root_tuples.add((z['kind'],z['label'],json.dumps(z['root'],sort_keys=True)))
        if c=='NO_REFERENCE_IN_QUERIED_NATIVE_AND_CAPTURED_SLICES_NOT_GLOBAL_UNUSED':
            no_ref+=1;clean=(s['native_renderer_count']==0 and not s['captured_additional_references'] and not s['captured_root_associations']);no_ref_clean+=clean;no_ref_with_atlas+=bool(s['atlas_memberships_not_usage'])
    summary=peer['summary'][0];schemas=json.loads(gzip.decompress(by_path[SCHEMAS]));index=json.loads(by_path[INDEX])
    supplied_schema_class_ids=sorted(schemas['classes'].keys())
    text=report.decode('utf-8','replace')
    report_checks=dict(contains_62815='62815' in text,contains_252='252' in text,contains_1897='1897' in text,contains_288='288' in text,contains_14813405='14813405' in text,contains_1377='1377' in text,contains_61438='61438' in text,contains_62426='62426' in text,contains_not_global_unused='NOT_GLOBAL_UNUSED' in text,contains_scoped_negative='scoped negative results' in text,contains_new_branch_owned='new branch-owned byte witnesses' in text,contains_not_reexport='not a reformat/re-export of peer trees' in text)
    checks=dict(source_pins=len(verified),source_pin_mismatches=sum(not x['match'] for x in verified),source_pin_dataset_counts=dataset_counts,shards=len(shards),shard_compressed_bytes=total_bytes,rows=total_rows,row_count_histogram=hist,last_shard_rows=shards[-1]['row_count'],renderer_unique=len(renderer_ids),gameobject_unique=len(go_ids),native_file_counts=file_counts,status_counts=status_counts,source_context_counts=context_counts,source_context_by_file=context_by_file,scene_rows=scene_rows,asset_rows=asset_rows,enabled_true=enabled_true,native_index_enabled_true=index['summary']['enabled_true'],object_size_total=total_object_size,null_sprites=null_sprites,nonnull_sprites=nonnull_sprites,catalog_total=len(catalog),coverage_counts=coverage,native_ref_sprites=native_refs,additional_ref_sprites=additional_refs,overlap_sprites=overlap,union_sprites=union,additional_category_counts=additional_categories,root_sprite_rows=root_rows,root_association_records=root_assoc,root_distinct_tuples=len(root_tuples),no_reference_rows=no_ref,no_reference_clean=no_ref_clean,no_reference_with_atlas_membership=no_ref_with_atlas,row_keys_sample=row_keys_sample,gameobject_keys_sample=gameobject_keys_sample,class_id_field_present=class_id_field_present,supplied_schema_class_ids=supplied_schema_class_ids,report_checks=report_checks,
        expected=dict(rows=summary['counts']['original_native_renderers'],nonnull=summary['counts']['nonnull_native_sprite_refs'],null=summary['counts']['null_native_sprite_refs'],bytes=summary['native_original_bytes'],files=summary['native_by_file'],scoped=summary['counts']['sprites_with_any_scoped_reference'],native_ref=summary['counts']['sprites_with_native_renderer_refs'],additional_ref=summary['counts']['sprites_with_captured_additional_refs'],categories=summary['captured_additional_reference_categories'],catalog=peer['sprite_catalog_count'],root_rows=1250,root_tuples=720,no_ref=288,compressed_bytes=14813405,enabled=62426,scene=1377,asset=61438))
    assert total_rows==62815 and total_bytes==14813405 and hist=={'250':251,'65':1},(total_rows,total_bytes,hist)
    assert shards[-1]['row_count']==65
    assert total_object_size==12311740 and nonnull_sprites==61864 and null_sprites==951
    assert len(renderer_ids)==62815 and len(go_ids)==62815
    assert file_counts==summary['native_by_file']
    assert status_counts=={'EXACT_ORIGINAL_SPRITE_IDENTITY':61864,'NULL_SPRITE':951}
    assert context_counts=={'SERIALIZED_SCENE_NOT_RUNTIME':1377,'ASSET_FILE_NOT_RUNTIME_PLACEMENT':61438}
    assert scene_rows==1377 and asset_rows==61438 and enabled_true==62426 and index['summary']['enabled_true']==62426
    assert all(v=='SERIALIZED_SCENE_NOT_RUNTIME' for k,v in context_by_file.items() if k.startswith('data.unity3d/level'))
    assert all(v=='ASSET_FILE_NOT_RUNTIME_PLACEMENT' for k,v in context_by_file.items() if not k.startswith('data.unity3d/level'))
    assert not class_id_field_present and supplied_schema_class_ids==['1','212']
    assert all(s['complete_inverse_equal']==s['row_count'] and s['gameobject_inverse_equal']==s['row_count'] and s['object_size_196']==s['row_count'] for s in shards)
    assert len(catalog)==2185 and coverage['SCOPED_STATIC_REFERENCE_FOUND']==1897 and no_ref==288 and no_ref_clean==288 and no_ref_with_atlas==115
    assert native_refs==1802 and additional_refs==210 and overlap==115 and union==1897
    assert additional_categories==summary['captured_additional_reference_categories']
    assert root_rows==1250 and len(root_tuples)==720
    assert all(report_checks.values()),report_checks
    description_precision_notes=[
        dict(id='D3',severity='wording',finding='The 288 `NO_REFERENCE...` rows are clean w.r.t. native renderer refs, captured additional references and root associations, but 115 of them still retain `atlas_memberships_not_usage` records. Report explicitly excludes atlas membership from `has scoped reference` coverage, so this is not a contradiction; clarify that no-reference means no active scoped reference, not absence of every related record.'),
        dict(id='D1',severity='wording',finding='Report says the252 shards are new branch-owned byte witnesses, not a reformat/re-export of peer trees. This is true for the252 native-renderer shards, but the artifact source_pins also include inherited context/catalog/tool pins: 901 l3-chain +411 l3-visual-surface +7 sprite-geometry +10 tool pins. Report lineage already says shared raw98/raw102 context union; scope the sentence to the252 shards or state the inherited pins explicitly.'),
        dict(id='D2',severity='precision',finding='Report says every referenced GameObject is independently checked as original class1. Shard rows do not carry a per-row class_id; they carry supplied-schema inverse equality and GameObject identity. native-schemas.json.gz supplies class1 and class212 schemas. Read class1 as supplied-schema selection plus inverse byte corroboration, not independently discovered class metadata per row.')
    ]
    receipt=dict(schema=1,provisional=True,review='R2',target_branch='arena/8141386a-windwings-space-shooter-game-p',target_commit=COMMIT,target_report=dict(path=REPORT,sha256=sha(report),bytes=len(report)),target_artifact=dict(path=ARTIFACT,sha256=sha(artifact),bytes=len(artifact)),source_pins_verified=verified,shards=shards,checks=checks,description_precision_notes=description_precision_notes,not_independently_recomputed=['captured_context_status counts','captured_union object/edge overlap counts','captured_native_owner_hash_matches and captured_native_sprite_edge_matches','content of l3-chain/l3-visual-surface context shards beyond source-pin SHA','original XAPK/bundle bytes beyond pinned source hashes','per-row GameObject class1 metadata beyond supplied schema'],limits=['Static review of fixed peer commit and retained raw shards; no runtime, Unity readback or render.','Source shard blobs were read from fixed peer commit but not copied into this branch; only exact SHA/size/row/aggregate receipts are retained.','Artifact-only context-summary counts are not promoted to independently verified; two description precision notes do not change measured byte/count results.'])
    blob=gzip.compress((json.dumps(receipt,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
    out=RAW/'source-verification.json.gz'
    if args.check:assert out.read_bytes()==blob
    else:out.write_bytes(blob)
    print(json.dumps(dict(path=str(out.relative_to(ROOT)),bytes=len(blob),sha256=sha(blob),checks=checks,description_precision_notes=description_precision_notes),default=str))
if __name__=='__main__':main()
