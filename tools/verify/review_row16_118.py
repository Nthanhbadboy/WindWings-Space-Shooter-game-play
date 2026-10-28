"""R2 independent review artifact for AI-3 row16/report118, built from retained raw receipts."""
import argparse,gzip,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'reverse-engineering/raw/l3-ef6b75ef125-review-row16-118'
VER=ROOT/'reverse-engineering/raw/l3-ef6b75ef125-verification'
OUT=ROOT/'datas/l3_ef6b75ef_review_row16_118.json.gz'
TARGET_COMMIT='e3fbb4dbc679c5d07ff8c520f8e13827baeae53c'
def sha(b):return hashlib.sha256(b).hexdigest()
def load():
    report=(RAW/'peer-report.md').read_bytes();artifact=(RAW/'peer-artifact.json.gz').read_bytes();manifest=json.loads(gzip.decompress((RAW/'source-verification.json.gz').read_bytes()))
    peer=json.loads(gzip.decompress(artifact));ci=json.loads((VER/'ci-runs.json').read_text());source_run=json.loads((VER/'source-run.json').read_text())
    return report,artifact,manifest,peer,ci,source_run
def recompute_catalog(peer):
    catalog=peer['sprites'];coverage={};native_refs=0;additional_refs=0;overlap=0;union=0;categories={};root_rows=0;root_records=0;root_tuples=set();no_ref=0;no_ref_clean=0;no_ref_atlas=0
    for s in catalog:
        c=s['coverage'];coverage[c]=coverage.get(c,0)+1
        n=s['native_renderer_count']>0;a=len(s['captured_additional_references'])>0;native_refs+=n;additional_refs+=a;overlap+=n and a;union+=n or a
        for z in s['captured_additional_references']+s['atlas_memberships_not_usage']:categories[z['category']]=categories.get(z['category'],0)+1
        if s['captured_root_associations']:
            root_rows+=1;root_records+=len(s['captured_root_associations'])
            for z in s['captured_root_associations']:root_tuples.add((z['kind'],z['label'],json.dumps(z['root'],sort_keys=True)))
        if c=='NO_REFERENCE_IN_QUERIED_NATIVE_AND_CAPTURED_SLICES_NOT_GLOBAL_UNUSED':
            no_ref+=1;clean=(s['native_renderer_count']==0 and not s['captured_additional_references'] and not s['captured_root_associations']);no_ref_clean+=clean;no_ref_atlas+=bool(s['atlas_memberships_not_usage'])
    return dict(catalog_total=len(catalog),coverage_counts=coverage,native_ref_sprites=native_refs,additional_ref_sprites=additional_refs,overlap_sprites=overlap,union_sprites=union,additional_category_counts=categories,root_sprite_rows=root_rows,root_association_records=root_records,root_distinct_tuples=len(root_tuples),no_reference_rows=no_ref,no_reference_clean=no_ref_clean,no_reference_with_atlas_membership=no_ref_atlas)
def build():
    report,artifact,manifest,peer,ci,source_run=load();checks=manifest['checks'];cat=recompute_catalog(peer)
    assert manifest['target_commit']==TARGET_COMMIT
    assert sha(report)==manifest['target_report']['sha256'] and sha(artifact)==manifest['target_artifact']['sha256']=='c33ad8a80c35990cf5dd94165234878a62785a5bb39ddef5f2bb73752408019d'
    assert checks['source_pins']==1587 and checks['source_pin_mismatches']==0 and all(x['match'] for x in manifest['source_pins_verified'])
    assert checks['shards']==252 and checks['shard_compressed_bytes']==14813405 and checks['rows']==62815 and checks['row_count_histogram']=={'250':251,'65':1} and checks['last_shard_rows']==65
    assert checks['renderer_unique']==checks['gameobject_unique']==62815 and checks['object_size_total']==12311740
    assert checks['nonnull_sprites']==61864 and checks['null_sprites']==951 and checks['enabled_true']==checks['native_index_enabled_true']==62426
    assert checks['scene_rows']==1377 and checks['asset_rows']==61438
    assert checks['source_context_counts']=={'SERIALIZED_SCENE_NOT_RUNTIME':1377,'ASSET_FILE_NOT_RUNTIME_PLACEMENT':61438}
    for k,v in cat.items():assert checks[k]==v,(k,checks[k],v)
    assert checks['class_id_field_present'] is False and checks['supplied_schema_class_ids']==['1','212']
    assert all(checks['report_checks'].values())
    assert checks['source_pin_dataset_counts']=={'new_native_renderer_shards':252,'geometry_8141386a_other':6,'l3_chain_context':901,'l3_visual_surface_context':411,'sprite_geometry_catalog':7,'tool_pins':10,'other':0}
    notes=manifest['description_precision_notes'];assert [x['id'] for x in notes]==['D3','D1','D2'] and len(notes)==3
    assert all(x['status']=='completed' and x['conclusion']=='success' for x in ci)
    assert source_run['head_sha']=='2beef6d63aba60732eb5b726ae4281f06f0c41bd' and source_run['conclusion']=='success'
    exact=[x for x in ci if x['run'] in (40369514934,40369514990,40369528335,40369528435)];assert all(x['head_sha']==TARGET_COMMIT for x in exact)
    paths=[RAW/'peer-report.md',RAW/'peer-artifact.json.gz',RAW/'source-verification.json.gz',VER/'claim.json',VER/'spec-lane98.json',VER/'spec-lane100.json',VER/'target-handoff.json',VER/'ci-runs.json',VER/'source-run.json',ROOT/'tools/review/generate_row16_118_raw.py',Path(__file__),ROOT/'tests/test_review_row16_118.py']
    return dict(schema=1,provisional=True,review='R2 independent review of AI-3 row16/report118',provenance='arena/ef6b75ef',claim=6423892767,assignment=[6423276716,6423721976,6424044328],target_handoff=6423177428,target_ack=6423276716,target_branch='arena/8141386a-windwings-space-shooter-game-p',target_commit=TARGET_COMMIT,target_report=manifest['target_report'],target_artifact=manifest['target_artifact'],inputs={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths},checks=checks,independent_catalog=cat,description_precision_notes=notes,not_independently_recomputed=manifest['not_independently_recomputed'],ci_runs=ci,source_recovery=dict(run=source_run['id'],head_sha=source_run['head_sha'],conclusion=source_run['conclusion']),verdict='SUPPORTED_IN_VERIFIED_SCOPE_WITH_3_WORDING_PRECISION_NOTES_AND_BOUNDED_GAPS',counts=dict(source_pins=checks['source_pins'],source_pin_mismatches=checks['source_pin_mismatches'],native_renderer_shards=checks['shards'],shard_compressed_bytes=checks['shard_compressed_bytes'],native_renderers=checks['rows'],unique_gameobjects=checks['gameobject_unique'],nonnull_sprite_refs=checks['nonnull_sprites'],null_sprite_refs=checks['null_sprites'],catalog_sprites=checks['catalog_total'],scoped_references=checks['union_sprites'],scoped_no_reference=checks['no_reference_rows'],description_precision_notes=len(notes)),scope='Static independent review of fixed peer commit/report/artifact and retained raw source pins/shards. No runtime, Unity readback/render, native execution, APK modification or peer branch edit. Verified byte/count claims and exact source-pin SHAs; artifact-only context-summary counts remain not independently recomputed. Three wording/precision notes do not change numeric results. No selfACK or #27-full closure.',limits=manifest['limits'])
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();x=build();b=gzip.compress((json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
    if a.check:assert OUT.read_bytes()==b
    else:OUT.write_bytes(b)
    print(json.dumps(dict(path=str(OUT.relative_to(ROOT)),bytes=len(b),sha256=sha(b),verdict=x['verdict'],counts=x['counts'])))
if __name__=='__main__':main()
