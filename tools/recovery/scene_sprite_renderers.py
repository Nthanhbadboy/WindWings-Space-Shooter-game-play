"""Pinned built-in scene SpriteRenderer/ancestor census; no dynamic prefab expansion."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
from asset_pack_v2 import extract_payload,serialized_files,sha
from spine_identity import walk_pointers
ROOT=Path(__file__).resolve().parents[2]
SCENE_FILES={f'data.unity3d/level{i}' for i in range(4)}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--xapk',type=Path,required=True);parser.add_argument('--work',type=Path,required=True);args=parser.parse_args()
    import UnityPy
    from UnityPy.classes.PPtr import PPtr
    inputs=extract_payload(args.xapk,args.work/'input');env=UnityPy.load(*(str(p) for p in sorted((args.work/'input').iterdir())))
    files=serialized_files(env);names={id(sf):name for name,sf in files}
    out=ROOT/'reverse-engineering/raw/scene-sprites';out.mkdir(parents=True,exist_ok=True)
    records={};links=[];roots=[];counts=Counter();go_errors=[]
    def identity(obj):return dict(serialized_file=names[id(obj.assets_file)],type=obj.type.name,path_id=int(obj.path_id))
    def key(obj):return(names[id(obj.assets_file)],int(obj.path_id))
    def target(obj,ptr):return PPtr(m_FileID=ptr['m_FileID'],m_PathID=ptr['m_PathID'],assetsfile=obj.assets_file).deref()
    def follow(obj,location,ptr):
        edge=dict(owner=identity(obj),location=location,pointer=ptr);links.append(edge)
        if not ptr['m_PathID']:edge['status']='null';return
        try:
            dest=target(obj,ptr);edge.update(status='resolved',target=identity(dest));record(dest)
        except Exception as error:edge.update(status='unresolved',error=repr(error))
    def record(obj):
        k=key(obj)
        if k in records:return
        row=dict(**identity(obj),raw_object_sha256=sha(obj.get_raw_data()));records[k]=row;kind=obj.type.name
        try:
            if kind in ('SpriteRenderer','Transform','RectTransform','GameObject','Material','BuildSettings'):
                tree=obj.read_typetree()
                if kind=='BuildSettings':tree={k:v for k,v in tree.items() if k in ('scenes','m_Version','enableDynamicBatching','m_GraphicsAPIs')}
                row.update(tree=tree,projection='buildsettings_scene_projection' if kind=='BuildSettings' else 'full_builtin_typetree')
                if kind=='SpriteRenderer':
                    for location,ptr in walk_pointers(tree):
                        if location in ('.m_GameObject','.m_Sprite') or location.startswith('.m_Materials['):follow(obj,location,ptr)
                elif kind in ('Transform','RectTransform'):
                    for field in ('m_GameObject','m_Father'):follow(obj,'.'+field,tree[field])
                elif kind=='GameObject':
                    candidates=[]
                    for location,ptr in walk_pointers(tree):
                        if not location.startswith('.m_Component[') or not ptr['m_PathID']:continue
                        dest=target(obj,ptr)
                        if dest.type.name in ('Transform','RectTransform'):candidates.append((location,ptr))
                    row['transform_component_locations']=[location for location,_ in candidates]
                    if len(candidates)!=1:go_errors.append(dict(identity=identity(obj),transform_count=len(candidates)))
                    for location,ptr in candidates:follow(obj,location,ptr)
                elif kind=='Material':
                    for location,ptr in walk_pointers(tree):
                        if location=='.m_Shader' or location.startswith('.m_SavedProperties.m_TexEnvs'):follow(obj,location,ptr)
            elif kind=='Texture2D':
                data=obj.read();row.update(projection='texture_metadata_no_pixels',name=data.m_Name,width=data.m_Width,height=data.m_Height,texture_format=int(data.m_TextureFormat))
            else:row['projection']='identity_and_object_hash_only'
            row['status']='recovered'
        except Exception as error:row.update(status='failed',error=repr(error))
    for name,sf in files:
        for obj in sf.objects.values():
            if obj.type.name=='SpriteRenderer':
                counts[name]+=1
                if name in SCENE_FILES:roots.append(obj)
            elif obj.type.name=='BuildSettings':record(obj)
    for obj in roots:record(obj)
    chunks=[];rows=sorted(records.values(),key=lambda r:(r['type'],r['serialized_file'],r['path_id']))
    for start in range(0,len(rows),100):
        group=rows[start:start+100];blob=''.join(json.dumps(r,ensure_ascii=True)+'\n' for r in group).encode();name=f'objects-{start//100:03}.jsonl.gz'
        (out/name).write_bytes(gzip.compress(blob,mtime=0));assert (out/name).stat().st_size<5_000_000
        chunks.append(dict(path=name,rows=len(group),sha256_decompressed=sha(blob)))
    blob=(json.dumps(links,indent=2)+'\n').encode();(out/'links.json.gz').write_bytes(gzip.compress(blob,mtime=0))
    index=dict(status='PROVISIONAL_INITIAL_SCENE_RENDERERS_NOT_RUNTIME_SPAWN_OR_RENDER_APPROVAL',inputs=inputs,toolchain=dict(UnityPy=UnityPy.__version__),
        root_files=sorted(SCENE_FILES),renderer_counts_all_serialized_files=dict(counts),roots=[identity(o) for o in roots],
        files=[dict(serialized_file=name,externals=[dict(path=e.path,type=e.type) for e in sf.externals]) for name,sf in files],
        chunks=chunks,links_sha256_decompressed=sha(blob),object_counts=dict(Counter(r['type'] for r in rows)),
        read_errors=[{k:r[k] for k in ('serialized_file','type','path_id','error')} for r in rows if r['status']=='failed'],
        unresolved_links=[l for l in links if l['status']=='unresolved'],gameobject_transform_errors=go_errors,
        limits=['Only level0..level3 SpriteRenderer roots; resources/sharedassets renderers are counted, not expanded as roots.',
                'Parent chains only; Transform children and other GameObject components are retained as raw pointers, not recursively followed.',
                'No native consumers, runtime spawn, animation transforms, camera projection, shader code or renderer pixels are executed.'])
    (out/'index.json').write_text(json.dumps(index,indent=2)+'\n')
    print('::notice::'+json.dumps(dict(roots=len(roots),objects=len(rows),counts=index['object_counts'],read_errors=len(index['read_errors']),unresolved=len(index['unresolved_links']),go_errors=len(go_errors))))
    assert not index['read_errors'] and not index['unresolved_links'] and not go_errors


if __name__=='__main__':main()
