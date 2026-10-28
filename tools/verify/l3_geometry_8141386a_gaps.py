"""#8 original refs + complete supplied-schema MB models, no guessed default mesh.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
from __future__ import annotations
import argparse
from collections import Counter
import gzip
import json
from tools.verify.geometry_8141386a_atlas_io import ROOT,BRANCH,canonical,key,sha_file,sha,full_file
from tools.verify.geometry_8141386a_gaps_sources import RAW,SELECTED,CHAIN,load as source_load
from tools.verify.geometry_8141386a_gaps_models import MODEL,load as model_load
from tools.verify.l3_geometry_8141386a_gaps_binary import decode_object
from tools.verify.l3_geometry_8141386a_builtin_mesh import corroborate
from tools.verify.l3_geometry_8141386a_builtin_binary import pointer_spans

OUTPUT=ROOT/'datas/l3_geometry_gaps_8141386a.json.gz'
WITNESS=RAW/'byte-witness.json.gz'
SCHEMAS=RAW/'schema-witness.json.gz'
CI=RAW/'source-ci-receipt.json.gz'


def model_pointers(schema,value,path=''):
    if schema['type'].startswith('PPtr<'):
        yield dict(field=path,expected_type=schema['type'][5:-1],pointer=value);return
    children=schema['children']
    if schema['type']=='Array':
        for i,v in enumerate(value):yield from model_pointers(children[1],v,path+f'[{i}]')
    elif len(children)==1 and children[0]['type']=='Array':yield from model_pointers(children[0],value,path)
    elif isinstance(value,dict):
        for c in children:yield from model_pointers(c,value[c['name']],path+'.'+c['name'])


def build():
    src=source_load();models=model_load();w=json.loads(gzip.decompress(WITNESS.read_bytes()));s=json.loads(gzip.decompress(SCHEMAS.read_bytes()));ci=json.loads(gzip.decompress(CI.read_bytes()))
    for doc in (w,s):
        if doc['provenance']!=BRANCH or doc['item']!=8:raise ValueError('wrong original source provenance')
        for p,h in doc['tool_pins'].items():
            if sha_file(ROOT/p)!=h:raise ValueError('original-source code/query pin drift:'+p)
    if ci['run']['head_sha']!='839d78c8f8af138132f267a1a5749fc5ebd2bda5' or ci['run']['conclusion']!='success' or ci['run']['status']!='completed':raise ValueError('need actual restored600MiB source CI, not raised-budget source')
    if ci['byte_witness_sha256']!=sha_file(WITNESS) or ci['schema_witness_sha256']!=sha_file(SCHEMAS):raise ValueError('original CI witness pin drift')
    if any(r['budget_stop']!='CHILD_RSS_BUDGET_600MiB' or r['status']!='SCHEMA_CAPTURE_BLOCKED' for r in s['results']):raise ValueError('SDK diagnostics must remain budget-stopped, not parsed field evidence')
    schemas={(r['namespace'],r['class_name']):r for r in models['schemas']};files={f['serialized_file']:f for f in w['files']}
    scripts={key(r['identity']):r for r in w['script_objects']};header_original={key(r['identity']):r for r in w['header_objects']};headers=[];pointers=[]
    for q in src['header_records']:
        o=header_original[key(q['identity'])]
        if o['object_sha256']!=q['record']['raw_object_sha256']:raise ValueError('original header-only object differs from capture')
        p=o['native_header']['fields']['m_Script'];owner=q['identity']['serialized_file'];target=(full_file(files[owner]['externals'][p['m_FileID']-1]['path']) if p['m_FileID'] else owner,p['m_PathID'])
        script=scripts[target];t=script['tree']
        if (t['m_Namespace'],t['m_ClassName'])!=(o['namespace'],o['class_name']):raise ValueError('fresh original MonoScript class disagrees')
        model=schemas[o['namespace'],o['class_name']];proof=decode_object(o,model)
        proof['script_binding']=dict(identity=script['identity'],object_sha256=script['object_sha256'],class_name=t['m_ClassName'],namespace=t['m_Namespace'],assembly=t['m_AssemblyName'])
        proof['original_capture_exception']=q['capture_exception'];headers.append(proof)
        for ref in model_pointers(model['schema'],proof['tree']):
            p=ref['pointer'];owner=proof['identity']['serialized_file']
            if p['m_PathID']==0:ref['status']='NULL_SERIALIZED_POINTER'
            else:
                if not 0<=p['m_FileID']<=len(files[owner]['externals']):raise ValueError('modeled PPtr owning-file ID out of range')
                target_file=full_file(files[owner]['externals'][p['m_FileID']-1]['path']) if p['m_FileID'] else owner
                ref['target_identity']=dict(serialized_file=target_file,path_id=p['m_PathID']);ref['status']='TARGET_NOT_IN_CAPTURE'
                if (target_file,p['m_PathID']) in scripts:
                    ref.update(status='FRESH_ORIGINAL_MONOSCRIPT_IDENTITY',target_type='MonoScript',target_object_sha256=scripts[target_file,p['m_PathID']]['object_sha256'])
            pointers.append(dict(owner=proof['identity'],**ref))
    wanted={key(r['target_identity']) for r in pointers if r['status']=='TARGET_NOT_IN_CAPTURE'};targets={}
    index=json.loads((CHAIN/'index.json').read_bytes())
    for part in index['objects']:
        with gzip.open(CHAIN/part['path'],'rb') as h:
            for row,line in enumerate(h):
                v=json.loads(line)
                if key(v) in wanted:targets[key(v)]=(v,dict(path=str((CHAIN/part['path']).relative_to(ROOT)),row=row))
    for ref in pointers:
        if ref['status']!='TARGET_NOT_IN_CAPTURE' or key(ref['target_identity']) not in targets:continue
        target,loc=targets[key(ref['target_identity'])];actual=target.get('class_name') if target['type']=='MonoBehaviour' else target['type'];expected=ref['expected_type']
        compatible=expected=='Object' or actual==expected or (expected=='Transform' and actual=='RectTransform') or (expected=='MonoBehaviour' and target['type']=='MonoBehaviour')
        ref.update(status='CAPTURED_TYPE_COMPATIBLE' if compatible else 'CAPTURED_TYPE_REQUIRES_HIERARCHY_REVIEW',target_type=target['type'],target_class=actual,target_raw_location=loc,target_object_sha256=target['raw_object_sha256'])
    resource=w['external_resource'];meshes={}
    for m in resource['selected_meshes']:
        if m['class_id']!=43:raise ValueError('default target is not actual Mesh')
        meshes[m['path_id']]=dict(path_id=m['path_id'],name=m['tree']['m_Name'],object_sha256=m['object_sha256'],byte_start=m['byte_start'],byte_size=m['byte_size'],
                                 resource_sha256=resource['sha256'],source_apk_entry=resource['apk_entry'],**corroborate(m))
    refs=[];owners={key(o['identity']):o for o in w['mesh_owner_objects']}
    for q in src['mesh_references']:
        o=owners[key(q['identity'])];p=q['reference']['record']['pointer'];blob=bytes.fromhex(o['original_hex']);mesh=meshes[p['m_PathID']]
        if sha(blob)!=o['object_sha256'] or o['object_sha256']!=q['record']['raw_object_sha256']:raise ValueError('fresh default-mesh owner hash disagreement')
        match=pointer_spans(blob,p)
        if match!=o['pointer'] or not match['unique_aligned_match']:raise ValueError('original default-mesh PPtr span disagreement')
        if files[q['identity']['serialized_file']]['externals'][p['m_FileID']-1]['path']!='Library/unity default resources':raise ValueError('wrong original owning-file external')
        refs.append(dict(owner=q['identity'],owner_type=q['record']['type'],original_owner_sha256=o['object_sha256'],owner_object_size=len(blob),field=q['reference']['record']['location'],
                         pointer=p,original_pointer_span=match['aligned_candidates'][0],external_path=o['external_path'],serialized_render_mode=q['record']['tree'].get('m_RenderMode'),
                         resolution=dict(status='RESOLVED_ORIGINAL_STANDALONE_MESH',path_id=mesh['path_id'],name=mesh['name'],object_sha256=mesh['object_sha256']),
                         runtime_use=None,world_bounds=None))
    if len(headers)!=5 or len(refs)!=52:raise ValueError('requested report98 groups incomplete')
    paths=[str(p.relative_to(ROOT)) for p in (SELECTED,MODEL,WITNESS,SCHEMAS,CI,RAW/'schema-budget600-v1.json.gz',RAW/'source-ci-budget600-v1.json.gz',RAW/'schema-budget-policy-correction.json',RAW/'schema-budget850-superseded.json.gz',RAW/'model-build-performance-local.json')]
    paths+=['tools/verify/l3_geometry_8141386a_gaps.py','tools/verify/l3_geometry_8141386a_gaps_binary.py','tools/verify/controller109_binary.py','tools/verify/l3_geometry_8141386a_builtin_mesh.py','tools/verify/l3_geometry_8141386a_builtin_binary.py']
    pins={}
    for group in (src['source_pins'],models['source_pins'],w['tool_pins'],s['tool_pins']):
        for p,h in group.items():
            if p in pins and pins[p]!=h:raise ValueError('source pin disagreement:'+p)
            pins[p]=h
    pins.update({p:sha_file(ROOT/p) for p in paths})
    summary=dict(src['summary'],fresh_original_component_hashes=len(w['header_objects'])+len(owners),fresh_monobehaviour_bytes=sum(r['object_size'] for r in headers),
                 complete_supplied_model_roundtrips=len(headers),custom_payload_bytes=sum(r['custom_payload_size'] for r in headers),typed_mb_root_spans=sum(len(r['typed_root_spans']) for r in headers),
                 fresh_original_monoscripts=len(scripts),fresh_original_monoscript_bytes=sum(s['fully_consumed'] for s in scripts.values()),
                 resolved_original_mesh_refs=len(refs),original_mesh_owner_bytes=sum(r['owner_object_size'] for r in refs),original_mesh_pointer_bytes=sum(r['original_pointer_span']['size'] for r in refs),
                 unique_meshes=len(meshes),mesh_bytes=sum(r['byte_size'] for r in meshes.values()),mesh_vertices=sum(r['geometry']['vertex_count'] for r in meshes.values()),mesh_indices=sum(r['geometry']['index_count'] for r in meshes.values()),
                 explicit_csharp_declarations=len(models['csharp_declarations']),modeled_pointer_status=dict(Counter(r['status'] for r in pointers)),
                 all_whole_mb_inverse_byte_equal=all(r['inverse_byte_equal'] for r in headers))
    return dict(schema=1,item=8,provenance=BRANCH,status='ORIGINAL_MESH_REFS_AND_BYTE_CORROBORATED_EXPLICIT_CSHARP_NATIVE_MODELS_NOT_ENGINE_SCHEMA_DISCOVERY',summary=summary,
                source=dict(xapk_sha256=w['xapk_sha256'],apk_sha256=w['apk_sha256'],bundle_sha256=w['bundle_sha256'],default_resource_sha256=resource['sha256'],default_resource_version=resource['unity_version'],
                            component_file_version=models['native_template_version'],accepted_original_source_run=ci['run']['id']),
                header_models=headers,header_model_pointer_crosschecks=pointers,meshes=[meshes[k] for k in sorted(meshes)],default_mesh_references=refs,
                group_conclusions=[dict(group='52default_mesh_refs',status='RESOLVED_ACTUAL_ORIGINAL_MESH_BYTES',runtime_use=None),
                                   dict(group='5header_only_MonoBehaviours',status='COMPLETE_BYTE_ROUNDTRIP_UNDER_EXPLICIT_SUPPLIED_CSHARP_NATIVE_SCHEMA_MODELS',native_schema_discovery=False,runtime_state=None),
                                   dict(group='managed_SDK_schema_capture',status='BUDGET_STOPPED_NOT_ACCEPTED_PARSED_FIELDS',missing_X='Validated engine/schema evidence beyond supplied-model tier if native field-layout discovery/consumer closure is required; no memory-limit increase or runtime probe.')],
                budget_boundary=dict(threshold_mib=600,sampling_seconds=.2,accepted_diagnostics=[{k:r[k] for k in ('fullname','status','budget_stop','observed_child_peak_rss_kib')} for r in s['results']],
                                     raised_budget_attempt='SUPERSEDED/quarantined, not used in schemas/models; exact original600MiB script restored and fresh source CI verified'),
                lineage='Shared report98/raw l3-chain capture + original bounded own#6/7 readers, ef111/110 framing, UnityPy1.25.4 native/standalone schema capture, inherited stdlib109 Reader, own C#declared/supplied native schema model +inverse writer/static Mesh layout. Not clean-room/native field-layout discovery/readback.',
                limits=['Complete inverse original-byte equality corroborates the explicitly stated field-order model; not independently discovered game serialization schema or executed engine deserializer.',
                        'Serialized UnityEvent method strings/PPTr joins are not invocation, lifecycle activation, native116cb40 binding or runtime values.',
                        'Only requested report98 groups; actual overlap with closed#7 is2, not an assumed nested corpus. No all-APK render/mesh closure.',
                        'No default primitive construction, original APK modifications, full Graph/all-Sprite fixture, runtime/device session or render approval.'],source_pins=pins)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args();value=build();body=gzip.compress(canonical(value)+b'\n',mtime=0)
    if a.check:
        if OUTPUT.read_bytes()!=body:raise SystemExit('gaps artifact drift')
    else:OUTPUT.write_bytes(body)
    print(value['summary']);print('artifact',len(body),'SHA256',sha(body),'pins',len(value['source_pins']))


if __name__=='__main__':main()
