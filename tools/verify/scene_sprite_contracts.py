"""File-scoped initial-scene renderer state, never a runtime visibility verdict."""
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'reverse-engineering/raw/scene-sprites'


def sha(blob):return hashlib.sha256(blob).hexdigest()
def key(row):return(row['serialized_file'],row['type'],row['path_id'])
def identity(row):return{k:row[k] for k in ('serialized_file','type','path_id')}

def ancestor_chain(start,parent):
    seen=set();chain=[];current=start
    while current is not None:
        if current in seen:raise ValueError('cycle in serialized transform ancestors')
        seen.add(current);chain.append(current);current=parent(current)
    return chain


def serialized_activity(enabled,ancestor_active_flags):
    return bool(enabled and all(ancestor_active_flags))


def build():
    index_blob=(RAW/'index.json').read_bytes();index=json.loads(index_blob);rows=[];sources=[]
    for c in index['chunks']:
        blob=gzip.decompress((RAW/c['path']).read_bytes());assert sha(blob)==c['sha256_decompressed']
        group=[json.loads(l) for l in blob.splitlines()];assert len(group)==c['rows'];rows.extend(group);sources.append(c)
    objects={key(r):r for r in rows};assert len(objects)==len(rows)
    assert Counter(r['type'] for r in rows)==index['object_counts']
    assert all(r['status']=='recovered' for r in rows) and not index['read_errors'] and not index['unresolved_links'] and not index['gameobject_transform_errors']
    link_blob=gzip.decompress((RAW/'links.json.gz').read_bytes());assert sha(link_blob)==index['links_sha256_decompressed'];links=json.loads(link_blob)
    externals={f['serialized_file']:f['externals'] for f in index['files']};edges={}
    for link in links:
        owner=key(link['owner']);assert owner in objects
        edge_key=(owner,link['location']);assert edge_key not in edges;edges[edge_key]=link
        value=objects[owner]['tree']
        for field,n in re.findall(r'\.([^\[.]+)|\[(\d+)\]',link['location']):value=value[field] if field else value[int(n)]
        assert value==link['pointer']
        ptr=link['pointer']
        if not ptr['m_PathID']:assert link['status']=='null';continue
        assert link['status']=='resolved' and key(link['target']) in objects
        expected=owner[0] if ptr['m_FileID']==0 else 'data.unity3d/'+externals[owner[0]][ptr['m_FileID']-1]['path']
        assert expected==link['target']['serialized_file'] and ptr['m_PathID']==link['target']['path_id']
    def linked(row,location):
        edge=edges[key(row),location]
        return None if edge['status']=='null' else objects[key(edge['target'])]
    def parent(k):
        target=linked(objects[k],'.m_Father')
        return None if target is None else key(target)
    meshes_blob=gzip.decompress((ROOT/'datas/sprite_mesh_contract.json.gz').read_bytes());meshes=json.loads(meshes_blob)
    sprites={key(r['identity']):r for r in meshes['sprites']}
    catalog_blob=gzip.decompress((ROOT/'reverse-engineering/raw/asset-pack-v2/catalog.json.gz').read_bytes());catalog=json.loads(catalog_blob)
    assert index['inputs']==catalog['inputs']
    counts={f['serialized_file']:f['types'].get('SpriteRenderer',0) for f in catalog['serialized_files'] if f['types'].get('SpriteRenderer',0)}
    assert counts==index['renderer_counts_all_serialized_files']
    settings=next(r for r in rows if r['type']=='BuildSettings')
    assert set(settings['tree'])=={'scenes','m_Version','enableDynamicBatching','m_GraphicsAPIs'}
    scene_paths=settings['tree']['scenes'];assert len(scene_paths)==4
    roots={key(r) for r in index['roots']};assert len(roots)==len(index['roots'])
    assert roots=={key(r) for r in rows if r['type']=='SpriteRenderer'}
    out=[];stats=Counter();draw=Counter();sorting=Counter();materials=Counter();mask=Counter();sort_points=Counter();by_scene={}
    for k in sorted(roots):
        r=objects[k];t=r['tree'];go=linked(r,'.m_GameObject');assert go['type']=='GameObject'
        locations=go['transform_component_locations'];assert len(locations)==1
        transform=linked(go,locations[0]);chain_keys=ancestor_chain(key(transform),parent);chain=[]
        for ck in chain_keys:
            tr=objects[ck];trgo=linked(tr,'.m_GameObject');tt=tr['tree'];assert tr['type'] in ('Transform','RectTransform')
            for field in ('m_LocalPosition','m_LocalRotation','m_LocalScale'):
                assert all(math.isfinite(v) for v in tt[field].values())
            chain.append(dict(identity=identity(tr),gameobject=identity(trgo),name=trgo['tree']['m_Name'],
                active_self=trgo['tree']['m_IsActive'],transform_tree=tt))
        assert chain[0]['gameobject']==identity(go)
        sprite=linked(r,'.m_Sprite');mesh=None
        if sprite:
            assert sprite['type']=='Sprite';mesh=sprites[key(sprite)]
            assert sprite['raw_object_sha256']==mesh['raw']['object_sha256']
        mats=[]
        for i in range(len(t['m_Materials'])):
            mat=linked(r,f'.m_Materials[{i}]')
            if mat:assert mat['type']=='Material';materials[key(mat)]+=1
            mats.append(None if mat is None else identity(mat))
        active=serialized_activity(t['m_Enabled'],[c['active_self'] for c in chain])
        stats['all_serialized_ancestor_gameobjects_active_and_renderer_enabled']+=bool(active)
        stats['disabled_renderer']+=not t['m_Enabled'];stats['null_sprite']+=sprite is None
        stats['flip_x_true']+=bool(t['m_FlipX']);stats['flip_y_true']+=bool(t['m_FlipY'])
        stats['ancestor_chain_contains_recttransform']+=any(c['identity']['type']=='RectTransform' for c in chain)
        stats['ancestor_chain_negative_scale_component']+=any(v<0 for c in chain for v in c['transform_tree']['m_LocalScale'].values())
        stats['ancestor_chain_zero_scale_component']+=any(v==0 for c in chain for v in c['transform_tree']['m_LocalScale'].values())
        draw[str(t['m_DrawMode'])]+=1;sorting[str(t['m_SortingLayerID'])]+=1
        mask[str(t['m_MaskInteraction'])]+=1;sort_points[str(t['m_SpriteSortPoint'])]+=1
        stats['serialized_renderer_color_alpha_zero']+=t['m_Color']['a']==0
        scene_index=int(r['serialized_file'].removeprefix('data.unity3d/level'))
        aggregate=by_scene.setdefault(r['serialized_file'],dict(source_scene_path=scene_paths[scene_index],renderers=0,serialized_active_enabled=0))
        aggregate['renderers']+=1;aggregate['serialized_active_enabled']+=bool(active)
        out.append(dict(identity=identity(r),raw_object_sha256=r['raw_object_sha256'],gameobject=identity(go),name=go['tree']['m_Name'],gameobject_layer=go['tree']['m_Layer'],
            source_scene_path=scene_paths[scene_index],renderer_tree=t,sprite=None if sprite is None else identity(sprite),materials=mats,
            mesh_reference=None if mesh is None else dict(identity=mesh['identity'],raw=mesh['raw'],png=mesh['png'],pixels_to_units=mesh['pixels_to_units']),
            transform_chain_leaf_to_root=chain,all_serialized_ancestor_gameobjects_active_and_renderer_enabled=bool(active)))
    for f in index['root_files']:assert by_scene[f]['renderers']==counts[f]
    dump_blob=gzip.decompress((ROOT/'reverse-engineering/il2cpp/dump.cs.gz').read_bytes())
    enum_block=re.search(r'\benum SpriteMaskInteraction[^}]+}',dump_blob.decode())[0]
    mask_enum={m[1]:int(m[2]) for m in re.finditer(r'public const SpriteMaskInteraction (\w+) = (-?\d+);',enum_block)}
    return dict(status='PROVISIONAL_INITIAL_SERIALIZED_SCENE_RENDERERS_NOT_RUNTIME_VISIBILITY_OR_PLACEMENT_APPROVAL',
        sources=dict(dump_sha256_decompressed=sha(dump_blob),index_sha256=sha(index_blob),chunks=sources,links_sha256_decompressed=sha(link_blob),sprite_mesh_contract_sha256_decompressed=sha(meshes_blob),catalog_sha256_decompressed=sha(catalog_blob)),
        scope=dict(root_files=index['root_files'],all_serialized_file_renderer_counts=counts,excluded_root_renderer_count=sum(n for f,n in counts.items() if f not in index['root_files']),object_counts=index['object_counts']),
        buildsettings=identity(settings),source_scene_paths=scene_paths,mask_interaction_enum_from_dump=mask_enum,
        summary=dict(renderers=len(out),scenes=by_scene,statistics=dict(stats),draw_mode_counts=dict(draw),sorting_layer_id_counts=dict(sorting),mask_interaction_counts=dict(mask),sprite_sort_point_counts=dict(sort_points),unique_sprite_refs=len({key(r['sprite']) for r in out if r['sprite']}),unique_material_refs=len(materials),max_ancestor_chain=max(len(r['transform_chain_leaf_to_root']) for r in out)),
        materials=[objects[k] for k in sorted(materials)],renderers=out,
        limits=['Initial serialized level0..3 roots only. Dynamic resources/sharedassets prefab renderers are not expanded, activated or spawned.',
                'Scene path labels map BuildSettings.scenes indices to levelN serialized filenames; raw scene paths are retained.',
                'Activity conjunction is not visibility: no camera, clipping/masks, SortingGroup, occlusion, draw order, runtime scripts or animation is executed.',
                'Transform chain is retained verbatim without flattening matrices, applying RectTransform anchors, renderer flip, source pivot or sliced/tiled draw behavior.',
                'Sorting layer IDs/orders and materials are serialized fields, not proof of final draw order or GPU appearance.'])


def main():
    result=build();path=ROOT/'datas/scene_sprite_contract.json.gz'
    path.write_bytes(gzip.compress((json.dumps(result,ensure_ascii=True,indent=2)+'\n').encode(),mtime=0))
    print(json.dumps(result['summary'],indent=2))


if __name__=='__main__':main()
