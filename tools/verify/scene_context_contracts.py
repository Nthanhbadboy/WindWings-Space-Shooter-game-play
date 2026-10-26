"""Initial camera layer predicates and mask context; never a visible-object list."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
from scene_sprite_contracts import ancestor_chain,identity,key,serialized_activity,build as renderer_build
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'reverse-engineering/raw/scene-context'
KINDS={'Camera','SpriteMask','SortingGroup'}


def sha(blob):return hashlib.sha256(blob).hexdigest()
def layer_allowed(bits,layer):
    if not isinstance(layer,int) or not 0<=layer<32:raise ValueError('GameObject layer outside 0..31')
    return bool((int(bits)&0xffffffff)&(1<<layer))


def build():
    index_blob=(RAW/'index.json').read_bytes();index=json.loads(index_blob);rows=[]
    for c in index['chunks']:
        blob=gzip.decompress((RAW/c['path']).read_bytes());assert sha(blob)==c['sha256_decompressed']
        group=[json.loads(l) for l in blob.splitlines()];assert len(group)==c['rows'];rows.extend(group)
    objects={key(r):r for r in rows};assert len(objects)==len(rows)
    assert Counter(r['type'] for r in rows)==index['object_counts']
    assert all(r['status']=='recovered' for r in rows) and not index['read_errors'] and not index['unresolved_links'] and not index['gameobject_transform_errors']
    blob=gzip.decompress((RAW/'links.json.gz').read_bytes());assert sha(blob)==index['links_sha256_decompressed']
    edges={};files={f['serialized_file']:f for f in index['files']}
    for edge in json.loads(blob):
        owner=key(edge['owner']);assert owner in objects
        ekey=(owner,edge['location']);assert ekey not in edges;edges[ekey]=edge
        value=objects[owner]['tree']
        for field,n in re.findall(r'\.([^\[.]+)|\[(\d+)\]',edge['location']):value=value[field] if field else value[int(n)]
        assert value==edge['pointer'];ptr=edge['pointer']
        if not ptr['m_PathID']:assert edge['status']=='null';continue
        assert edge['status']=='resolved' and key(edge['target']) in objects
        expected=owner[0] if not ptr['m_FileID'] else 'data.unity3d/'+files[owner[0]]['externals'][ptr['m_FileID']-1]['path']
        assert (expected,ptr['m_PathID'])==(edge['target']['serialized_file'],edge['target']['path_id'])
    def linked(row,location):
        edge=edges[key(row),location]
        return None if edge['status']=='null' else objects[key(edge['target'])]
    def parent(k):
        row=linked(objects[k],'.m_Father');return None if row is None else key(row)
    def context(row):
        go=linked(row,'.m_GameObject');locations=go['transform_component_locations'];assert len(locations)==1
        tr=linked(go,locations[0]);chain=[]
        for k in ancestor_chain(key(tr),parent):
            transform=objects[k];obj=linked(transform,'.m_GameObject')
            chain.append(dict(identity=identity(transform),gameobject=identity(obj),name=obj['tree']['m_Name'],active_self=obj['tree']['m_IsActive'],transform_tree=transform['tree']))
        return dict(identity=identity(row),raw_object_sha256=row['raw_object_sha256'],gameobject=identity(go),name=go['tree']['m_Name'],
            gameobject_layer=go['tree']['m_Layer'],tree=row['tree'],transform_chain_leaf_to_root=chain,
            serialized_active_enabled=serialized_activity(row['tree']['m_Enabled'],[c['active_self'] for c in chain]))
    renderer_blob=gzip.decompress((ROOT/'datas/scene_sprite_contract.json.gz').read_bytes());renderers=json.loads(renderer_blob)
    assert renderer_build()==renderers
    source_index=json.loads((ROOT/'reverse-engineering/raw/scene-sprites/index.json').read_text());assert index['inputs']==source_index['inputs']
    overlap=0
    for c in source_index['chunks']:
        data=gzip.decompress((ROOT/'reverse-engineering/raw/scene-sprites'/c['path']).read_bytes());assert sha(data)==c['sha256_decompressed']
        for line in data.splitlines():
            r=json.loads(line)
            if key(r) in objects:assert r['raw_object_sha256']==objects[key(r)]['raw_object_sha256'];overlap+=1
    catalog_blob=gzip.decompress((ROOT/'reverse-engineering/raw/asset-pack-v2/catalog.json.gz').read_bytes());catalog=json.loads(catalog_blob)
    assert index['inputs']==catalog['inputs']
    counts={f['serialized_file']+'|'+kind:n for f in catalog['serialized_files'] for kind in KINDS if (n:=f['types'].get(kind,0))}
    assert counts==index['context_counts_all_serialized_files']
    roots={key(r) for r in index['roots']};assert len(roots)==len(index['roots'])
    assert roots=={key(r) for r in rows if r['type'] in KINDS}
    tags=next(r for r in rows if r['type']=='TagManager');assert set(tags['tree'])=={'layers','m_SortingLayers'}
    layers=tags['tree']['layers'];assert len(layers)==32
    cameras=[];masks=[];groups=[]
    mesh_blob=gzip.decompress((ROOT/'datas/sprite_mesh_contract.json.gz').read_bytes());meshes={key(r['identity']):r for r in json.loads(mesh_blob)['sprites']}
    for k in sorted(roots):
        row=objects[k];value=context(row)
        if row['type']=='Camera':
            bits=row['tree']['m_CullingMask']['m_Bits'];value['allowed_gameobject_layers']=[dict(index=i,name=layers[i]) for i in range(32) if layer_allowed(bits,i)];cameras.append(value)
        elif row['type']=='SpriteMask':
            sprite=linked(row,'.m_Sprite');value['sprite']=None if sprite is None else identity(sprite)
            if sprite:
                mesh=meshes[key(sprite)];assert mesh['raw']['object_sha256']==sprite['raw_object_sha256']
                value['mesh_reference']=dict(identity=mesh['identity'],raw=mesh['raw'],png=mesh['png'])
            masks.append(value)
        else:groups.append(value)
    predicates=[];sums=Counter()
    for r in renderers['renderers']:
        scene=r['identity']['serialized_file'];candidate_cameras=[]
        for camera in cameras:
            if camera['identity']['serialized_file']!=scene:continue
            allowed=layer_allowed(camera['tree']['m_CullingMask']['m_Bits'],r['gameobject_layer'])
            gate=allowed and camera['serialized_active_enabled'] and r['all_serialized_ancestor_gameobjects_active_and_renderer_enabled']
            candidate_cameras.append(dict(camera=camera['identity'],gameobject_layer_allowed=allowed,camera_serialized_active_enabled=camera['serialized_active_enabled'],passes_layer_and_serialized_activity_only=bool(gate)))
        sums['renderers_passing_any_same_scene_camera_layer_and_serialized_activity_only']+=any(c['passes_layer_and_serialized_activity_only'] for c in candidate_cameras)
        mask_state=r['renderer_tree']['m_MaskInteraction']
        if mask_state:sums['mask_dependent_renderers']+=1
        predicates.append(dict(renderer=r['identity'],gameobject_layer=r['gameobject_layer'],same_scene_camera_predicates=candidate_cameras,mask_interaction=mask_state,
            same_scene_mask_contexts=[m['identity'] for m in masks if m['identity']['serialized_file']==scene] if mask_state else [],
            warning='same_scene_mask_contexts are an inventory, not proven affecting-mask bindings'))
    sums.update(cameras=len(cameras),masks=len(masks),sorting_groups=len(groups),cameras_serialized_active_enabled=sum(c['serialized_active_enabled'] for c in cameras),masks_serialized_active_enabled=sum(m['serialized_active_enabled'] for m in masks),cross_capture_objects_equal=overlap)
    return dict(status='PROVISIONAL_SCENE_CONTEXT_AND_BIT_PREDICATES_NOT_VISIBILITY_OR_RENDER_APPROVAL',sources=dict(index_sha256=sha(index_blob),chunks=index['chunks'],links_sha256_decompressed=sha(blob),scene_renderer_contract_sha256_decompressed=sha(renderer_blob),sprite_mesh_contract_sha256_decompressed=sha(mesh_blob),catalog_sha256_decompressed=sha(catalog_blob)),
        scope=dict(root_files=index['root_files'],all_file_context_counts=counts,object_counts=index['object_counts']),
        tagmanager=dict(identity=identity(tags),layers=layers,sorting_layers=tags['tree']['m_SortingLayers']),cameras=cameras,masks=masks,sorting_groups=groups,renderer_predicates=predicates,summary=dict(sums),
        limits=['Only initial serialized level0..3 context; resources masks and sharedassets cameras are counted, not expanded as roots.',
                'Camera culling-mask bit test and activity AND are necessary serialized predicates, not frustum, occlusion, depth, clipping or visibility simulation.',
                'Same-scene masks are an inventory, not proven affecting-mask bindings; sorting-range application, alpha sampling and stencil rendering are not simulated.',
                'No serialized SortingGroup count is not proof of no runtime AddComponent or other sorting logic.',
                'Transforms/orthographic size/viewport/target/depth are source snapshots; native writers, runtime camera changes and world matrices are not executed.'])


if __name__=='__main__':
    result=build();(ROOT/'datas/scene_render_context_contract.json.gz').write_bytes(gzip.compress((json.dumps(result,ensure_ascii=True,indent=2)+'\n').encode(),mtime=0))
    print(json.dumps(result['summary'],indent=2))
