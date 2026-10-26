"""#7 exact original standalone builtin Mesh resolution, not constructed primitives.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
from __future__ import annotations
import argparse
from collections import Counter
import gzip
import json
from tools.verify.geometry_8141386a_atlas_io import ROOT,BRANCH,canonical,sha,sha_file,key
from tools.verify.geometry_8141386a_builtin_sources import RAW,SELECTED,DEFAULT_PATH,load
from tools.verify.l3_geometry_8141386a_builtin_binary import pointer_spans
from tools.verify.l3_geometry_8141386a_builtin_mesh import corroborate

WITNESS=RAW/'byte-witness.json.gz'
SOURCE_CI=RAW/'source-ci-receipt.json.gz'
OUTPUT=ROOT/'datas/l3_geometry_builtin_8141386a.json.gz'


def build():
    source=load();w=json.loads(gzip.decompress(WITNESS.read_bytes()))
    if w['provenance']!=BRANCH or w['schema']!=2:raise ValueError('require fresh standalone-file original witness')
    for p,h in w['tool_pins'].items():
        if sha_file(ROOT/p)!=h:raise ValueError('original builtin tool/query pin drift: '+p)
    ci=json.loads(gzip.decompress(SOURCE_CI.read_bytes()))
    run=ci['run']
    if run['head_sha']!='368e5ee29f346a571303d18f9f6e91127b673655' or run['conclusion']!='success' or run['status']!='completed':raise ValueError('original source CI receipt is not the actual successful standalone recovery')
    if ci['witness_sha256']!=sha_file(WITNESS):raise ValueError('source CI witness hash mismatch')
    external=w['external_resource']
    if external['apk_entry']!='assets/bin/Data/unity default resources':raise ValueError('wrong standalone source')
    hits=[[p['apk_member'],e] for p in w['package_inventory'] for e in p['default_resource_name_hits']]
    if len(hits)!=1 or hits[0][1]!=external['apk_entry']:raise ValueError('standalone file path ambiguous')
    meshes={}
    for m in external['selected_meshes']:
        if m['class_id']!=43 or m['path_id'] in meshes:raise ValueError('duplicate/wrong-class original builtin')
        proof=corroborate(m)
        meshes[m['path_id']]=dict(path_id=m['path_id'],serialized_file=DEFAULT_PATH,name=m['tree']['m_Name'],
                                 source_apk_entry=external['apk_entry'],resource_sha256=external['sha256'],
                                 byte_start=m['byte_start'],byte_size=m['byte_size'],object_sha256=m['object_sha256'],**proof)
    original={key(o['identity']):o for o in w['objects']};rows=[]
    resources=[f for f in w['files'] if f['serialized_file']=='data.unity3d/resources.assets']
    if len(resources)!=1:raise ValueError('ambiguous renderer owner metadata')
    for q in source['records']:
        k=key(q['identity']);o=original[k];blob=bytes.fromhex(o['original_hex'])
        if sha(blob)!=q['record']['raw_object_sha256'] or sha(blob)!=o['object_sha256']:raise ValueError('original renderer object SHA disagreement')
        for ref in q['refs']:
            p=ref['pointer'];m=meshes[p['m_PathID']]
            if resources[0]['externals'][p['m_FileID']-1]['path']!=DEFAULT_PATH:raise ValueError('original external PPtr owner mismatch')
            candidate=pointer_spans(blob,p)
            if not candidate['unique_aligned_match']:raise ValueError('cannot claim a unique original PPtr byte span')
            original_ref=[r for r in o['references'] if r['field']==ref['field']]
            if len(original_ref)!=1 or original_ref[0]['byte_search']!=candidate:raise ValueError('original PPtr span disagreement')
            rows.append(dict(owner=q['identity'],field=ref['field'],pointer=p,owning_external_path=DEFAULT_PATH,
                             renderer_object_sha256=o['object_sha256'],renderer_object_size=len(blob),
                             original_pointer_span=candidate['aligned_candidates'][0],
                             serialized_render_mode=ref['render_mode'],raw_location=q['raw_location'],
                             resolution=dict(status='RESOLVED_ORIGINAL_STANDALONE_MESH',mesh_path_id=m['path_id'],
                                             mesh_name=m['name'],mesh_object_sha256=m['object_sha256'],resource_sha256=external['sha256']),
                             runtime_use=None,scene_vertices=None,runtime_bounds=None))
    if set(meshes)!={r['pointer']['m_PathID'] for r in rows}:raise ValueError('selected Mesh set differs from exact refs')
    paths=['tools/verify/l3_geometry_8141386a_builtin.py','tools/verify/l3_geometry_8141386a_builtin_mesh.py',
           'tools/verify/controller109_binary.py',str(WITNESS.relative_to(ROOT)),str(SOURCE_CI.relative_to(ROOT)),
           str(SELECTED.relative_to(ROOT)),str((RAW/'inventory-byte-witness-v1.json.gz').relative_to(ROOT)),
           str((RAW/'inventory-ci-v1.json.gz').relative_to(ROOT))]
    pins=dict(source['source_pins'],**w['tool_pins']);pins.update({p:sha_file(ROOT/p) for p in paths})
    summary=dict(source['summary'],resolved_original_builtin_refs=len(rows),original_renderer_hashes=len(original),
                 unique_original_pointer_spans=len(rows),unique_builtin_meshes=len(meshes),
                 mesh_fully_consumed_bytes=sum(m['shared_schema_decode']['fully_consumed_bytes'] for m in meshes.values()),
                 mesh_vertices=sum(m['geometry']['vertex_count'] for m in meshes.values()),
                 mesh_indices=sum(m['geometry']['index_count'] for m in meshes.values()),
                 target_path_id_histogram=dict(Counter(str(r['pointer']['m_PathID']) for r in rows)),
                 serialized_mode_histogram=dict(Counter(str(r['serialized_render_mode']) for r in rows)),
                 standalone_resource_size=external['size'],standalone_object_count=external['object_count'],
                 standalone_mesh_metadata_count=len(external['mesh_objects']),
                 original_bundle_node_count=len(w['bundle_nodes']),original_bundle_serialized_files=len(w['files']),
                 original_bundle_object_metadata_count=sum(f['object_count'] for f in w['files']),differences=0)
    return dict(schema=1,item=7,provenance=BRANCH,status='BYTE_PROVEN_ORIGINAL_BUILTIN_MESH_REFS_NOT_RUNTIME_USE',
                summary=summary,source=dict(xapk_sha256=w['xapk_sha256'],apk_sha256=w['apk_sha256'],bundle_sha256=w['bundle_sha256'],
                                           standalone_sha256=external['sha256'],standalone_apk_entry=external['apk_entry'],
                                           standalone_declared_unity_version=external['unity_version'],source_recovery_run_id=run['id']),
                references=rows,meshes=[meshes[p] for p in sorted(meshes)],
                initial_hypothesis=dict(raw102_unresolved_links=source['original_unresolved_links'],
                                        bundle_node_lookup='NOT_PRESENT_AS_BUNDLE_NODE is only a bundle lookup; it is NOT APK-file absence.',
                                        counterexample=hits,conclusion='FALSIFIED missing-package-source hypothesis; actual standalone file and two Mesh payloads resolve all7refs.'),
                source_pins=pins,lineage='Own raw102 streamed grep + original ZIP inventory/query; UnityPy1.25.4 standalone framing/schema capture; inherited stdlib109 schema reader; own Mesh Float32 stream/index decoder with consulted UnityPy alignment conventions. Not clean-room schema discovery/native execution.',
                limits=['Reference resolution/static Mesh-local vertices do not prove active ParticleSystem mesh-mode draw or runtime billboard/particle generator.',
                        'Preserve original tiny Quad Z coordinates, UVs, winding and duplicated Cube vertices; no idealized primitive substitution.',
                        'No APK modification, runtime session, instance transform/world/pixel bounds, live remap/deformation or render approval. #8 not part of item7.'])


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
    value=build();body=gzip.compress(canonical(value)+b'\n',mtime=0)
    if a.check:
        if OUTPUT.read_bytes()!=body:raise SystemExit('builtin artifact drift')
    else:OUTPUT.write_bytes(body)
    print(value['summary']);print('artifact',len(body),'SHA256',sha(body))


if __name__=='__main__':main()
