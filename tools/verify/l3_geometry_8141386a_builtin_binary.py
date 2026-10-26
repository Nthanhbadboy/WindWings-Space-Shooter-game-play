"""#7 pointer byte search and file-qualified packaged-source diagnosis.
provenance: arena/8141386a-windwings-space-shooter-game-p
A candidate byte match is disclosed as seeded corroboration, not schema discovery.
"""
import struct
from tools.verify.geometry_8141386a_atlas_io import full_file,sha


def pointer_spans(blob,pointer):
    expected=struct.pack('<iq',pointer['m_FileID'],pointer['m_PathID'])
    hits=[];start=0
    while True:
        offset=blob.find(expected,start)
        if offset<0:break
        if offset%4==0:hits.append(dict(offset=offset,size=12,hex=blob[offset:offset+12].hex(),sha256=sha(blob[offset:offset+12])))
        start=offset+1
    return dict(pointer=pointer,expected_hex=expected.hex(),aligned_candidates=hits,
                unique_aligned_match=len(hits)==1,
                scope='Seeded full12B PPtr match; ambiguous matches stay candidates, no invented field offset')


def packaged_target(external_path,path_id,nodes,files):
    logical=full_file(external_path)
    if logical not in {full_file(n['path']) for n in nodes}:
        return dict(target_file=logical,path_id=path_id,status='NOT_PRESENT_AS_BUNDLE_NODE',
                    geometry=None,missing='Matching engine builtin resource catalog/registration+mesh generation bytes or same-build object/vertex readback; package-object resolver cannot synthesize an absent file.')
    matching=[f for f in files if f['serialized_file']==logical]
    if len(matching)!=1:raise ValueError('packaged target file inventory missing/ambiguous')
    candidates=[e for e in matching[0]['mesh_objects'] if e['path_id']==path_id]
    if len(candidates)>1:raise ValueError('duplicate original mesh identity')
    if candidates:
        return dict(target_file=logical,path_id=path_id,status='PACKAGED_MESH_TARGET_REQUIRES_DECODE',geometry=None)
    return dict(target_file=logical,path_id=path_id,status='NO_MESH_AT_EXACT_FILE_AND_PATH_ID',geometry=None,
                missing='Mesh-class object bytes at the exact qualified target, not another file with the same pathID')
