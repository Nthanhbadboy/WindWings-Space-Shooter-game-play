"""Pinned L3 typed graph: indexed UI + gameplay resource hierarchies + visual assets.
No original pixels/audio/font programs/shader bytecode are emitted.
"""
import argparse,gzip,hashlib,io,json,sys,zipfile
from collections import Counter,deque
from pathlib import Path
from asset_pack_v2 import extract_payload,serialized_files,sha,XAPK_SHA
from spine_identity import walk_pointers
ROOT=Path(__file__).resolve().parents[2]
ASSETS={'Sprite','SpriteAtlas','Material','Texture2D','AnimationClip','AnimatorController','AnimatorOverrideController','AudioClip','Shader','Mesh','Avatar','TextAsset'}
BUILTINS={'GameObject','Transform','RectTransform','SpriteRenderer','SpriteMask','MeshRenderer','SkinnedMeshRenderer','MeshFilter','ParticleSystem','ParticleSystemRenderer','Animator','Animation','AudioSource','Canvas','CanvasRenderer','Camera','SortingGroup','Light'}
CORE_UI={'Board_Home','Board_Maps','Board_Stage','Board_Players','Board_Drones','Board_Pause','Board_Reborn','Board_Reborn_IAP','Board_Endgame','GP_Tutorials'}
ASSET_CLASSES={'TMP_FontAsset','TMP_Settings','SkeletonDataAsset','SpineAtlasAsset','AtlasAsset','SoundClip'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--xapk',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);args=ap.parse_args()
    import UnityPy
    from UnityPy.classes.PPtr import PPtr
    from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
    work=args.work;inputs=extract_payload(args.xapk,work/'input')
    binaries={}
    with zipfile.ZipFile(args.xapk) as outer:
        for entry in outer.namelist():
            if not entry.endswith('.apk'):continue
            with zipfile.ZipFile(io.BytesIO(outer.read(entry))) as part:
                for path,expected in [('lib/arm64-v8a/libil2cpp.so','9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99'),('assets/bin/Data/Managed/Metadata/global-metadata.dat','449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69')]:
                    if path in part.namelist():
                        b=part.read(path);assert sha(b)==expected;binaries[Path(path).name]=b
    env=UnityPy.load(*(str(p) for p in sorted((work/'input').iterdir())))
    gen=TypeTreeGenerator('2022.3.62f3',generator='AssetStudio');gen.load_il2cpp(binaries['libil2cpp.so'],binaries['global-metadata.dat']);env.typetree_generator=gen
    files=serialized_files(env);names={id(sf):name for name,sf in files};byname=dict(files)
    out=ROOT/'reverse-engineering/raw/l3-chain';out.mkdir(parents=True,exist_ok=True)
    records={};links=[];roots=[];queue=deque();classes={};script_cache={};resource_rows=[]
    def key(obj):return(names[id(obj.assets_file)],int(obj.path_id))
    def ident(obj):return dict(serialized_file=names[id(obj.assets_file)],path_id=int(obj.path_id),type=obj.type.name)
    def enqueue(obj):
        if key(obj) not in records:records[key(obj)]=None;queue.append(obj)
    def classify(obj):
        k=key(obj)
        if k not in classes:
            try:
                h=obj.parse_monobehaviour_head();sk=(id(obj.assets_file),h.m_Script.m_FileID,h.m_Script.m_PathID)
                if sk not in script_cache:
                    s=h.m_Script.deref_parse_as_object();script_cache[sk]=dict(class_name=s.m_ClassName,namespace=s.m_Namespace)
                classes[k]=dict(**script_cache[sk],header=dict(m_GameObject=dict(m_FileID=h.m_GameObject.m_FileID,m_PathID=h.m_GameObject.m_PathID),m_Enabled=h.m_Enabled,m_Script=dict(m_FileID=h.m_Script.m_FileID,m_PathID=h.m_Script.m_PathID)))
            except Exception as e:classes[k]=dict(class_name='unknown',header_error=repr(e))
        return classes[k]
    def follow(obj,loc,ptr,force=False):
        edge=dict(owner=ident(obj),location=loc,pointer=ptr);links.append(edge)
        if not ptr['m_PathID']:edge['status']='null';return
        try:
            target=PPtr(m_FileID=ptr['m_FileID'],m_PathID=ptr['m_PathID'],assetsfile=obj.assets_file).deref();edge.update(status='resolved',target=ident(target))
            # Inspect referenced assets, not arbitrary gameplay-object pointers in scripts.
            if force or target.type.name in ASSETS or (target.type.name=='MonoBehaviour' and classify(target)['class_name'] in ASSET_CLASSES):enqueue(target)
        except Exception as e:edge.update(status='unresolved',error=repr(e))
    source_index=json.loads(gzip.decompress((ROOT/'datas/ui_l3_bindings.json.gz').read_bytes()))
    for s in source_index['sources']:
        if s['screen'] not in CORE_UI:continue
        candidates=[(n,sf) for n,sf in files if n==s['serialized_file'] or n.rsplit('/',1)[-1]==s['serialized_file']]
        assert len(candidates)==1,s;name,sf=candidates[0];obj=sf.objects[s['root_path_id']];assert obj.type.name=='GameObject'
        roots.append(dict(kind='ui',label=s['screen'],source_layout=s['path'],source_sha256=s['sha256'],target=ident(obj)));enqueue(obj)
    for name,sf in files:
        for obj in sf.objects.values():
            if obj.type.name!='ResourceManager':continue
            tree=obj.read_typetree()
            for resource,ptr in tree['m_Container']:
                selected=resource.startswith(('prefabs/players/','prefabs/drones/','prefabs/homeplayers/','poolingobjects/bullets/','poolingobjects/enemy/','poolingobjects/boss/','poolingobjects/effects/','poolingobjects/item_bonus/','audio/soundclips/'))
                if not selected:continue
                row=dict(owner=ident(obj),resource=resource,pointer=ptr);resource_rows.append(row)
                try:
                    dest=PPtr(m_FileID=ptr['m_FileID'],m_PathID=ptr['m_PathID'],assetsfile=sf).deref();row.update(status='resolved',target=ident(dest));roots.append(dict(kind='resource',label=resource,target=ident(dest)));enqueue(dest)
                except Exception as e:row.update(status='unresolved',error=repr(e))
    def process_queue():
        while queue:
            obj=queue.popleft();kind=obj.type.name;row=dict(**ident(obj),raw_object_sha256=sha(obj.get_raw_data()));records[key(obj)]=row
            if len(records)>300000:raise RuntimeError('explicit graph budget exceeded; do not silently truncate')
            try:
                cls=''
                if kind=='MonoBehaviour':row.update(classify(obj));cls=row['class_name']
                if kind in BUILTINS|{'MonoBehaviour','Sprite','SpriteAtlas','Material','AnimatorController','AnimatorOverrideController'}:
                    try:tree=obj.read_typetree();row.update(tree=tree,projection='full_typetree')
                    except Exception as e:
                        if kind!='MonoBehaviour':raise
                        row.update(tree=row.get('header',{}),projection='parsed_monobehaviour_header_only',tree_error=repr(e));tree=row['tree']
                    if kind=='MonoBehaviour' and row.get('header'):
                        row['header_tree_disagreements']={k:dict(parsed=v,generated=tree.get(k)) for k,v in row['header'].items() if tree.get(k)!=v}
                    for loc,ptr in walk_pointers(tree):
                        if kind=='MonoBehaviour' and loc in ('.m_Script','.m_GameObject'):ptr=row.get('header',{}).get(loc[1:],ptr)
                        force=(kind=='GameObject' and loc.startswith('.m_Component[')) or (kind in ('Transform','RectTransform') and (loc=='.m_GameObject' or loc.startswith('.m_Children[')))
                        follow(obj,loc,ptr,force)
                elif kind=='AnimationClip':
                    tree=obj.read_typetree();keep={'m_Name','m_SampleRate','m_WrapMode','m_Legacy','m_Events','m_ClipBindingConstant','m_AnimationClipSettings','m_StopTime','m_StartTime','m_FloatCurves','m_PositionCurves','m_RotationCurves','m_ScaleCurves','m_PPtrCurves','m_MuscleClip','m_EulerCurves','m_CompressedRotationCurves'}
                    row.update(tree={k:v for k,v in tree.items() if k in keep},projection='clip_metadata_numeric_curves_opaque_byte_buffers_hashed')
                    for loc,ptr in walk_pointers(row['tree']):follow(obj,loc,ptr)
                elif kind=='Texture2D':
                    d=obj.read();row.update(projection='texture_metadata_no_pixels',name=d.m_Name,width=d.m_Width,height=d.m_Height,texture_format=int(d.m_TextureFormat))
                elif kind=='TextAsset':
                    d=obj.read();v=d.m_Script;b=v.encode('utf-8','surrogateescape') if isinstance(v,str) else bytes(v);row.update(projection='textasset_name_payload_hash_only',name=d.m_Name,payload_bytes=len(b),payload_sha256=sha(b))
                elif kind=='AudioClip':
                    d=obj.read();row.update(projection='audio_metadata_no_samples',name=d.m_Name,channels=d.m_Channels,frequency=d.m_Frequency,length=d.m_Length,load_type=int(d.m_LoadType))
                else:row.update(projection='identity_and_object_hash_only')
                row['status']='recovered'
            except Exception as e:row.update(status='failed',error=repr(e))
    print('root-selection',len(roots),'unique queued',len(queue),flush=True)
    process_queue()
    def context_record(obj):
        k=key(obj)
        if k in records:return records[k]
        row=dict(**ident(obj),raw_object_sha256=sha(obj.get_raw_data()),traversal='scene_context_ancestors_only')
        records[k]=row
        try:
            tree=obj.read_typetree();row.update(tree=tree,status='recovered',projection='full_builtin_typetree')
            for loc,ptr in walk_pointers(tree):follow(obj,loc,ptr)
        except Exception as e:row.update(status='failed',error=repr(e))
        return row
    def deref(obj,ptr):return PPtr(m_FileID=ptr['m_FileID'],m_PathID=ptr['m_PathID'],assetsfile=obj.assets_file).deref()
    for name,sf in files:
        if name not in {f'data.unity3d/level{i}' for i in range(4)}:continue
        for obj in sf.objects.values():
            if obj.type.name not in ('Camera','Canvas','AudioSource','Light'):continue
            row=context_record(obj);roots.append(dict(kind='scene_context',label=obj.type.name,target=ident(obj)))
            ptr=row.get('tree',{}).get('m_GameObject',{})
            if not ptr.get('m_PathID'):continue
            go=deref(obj,ptr);gr=context_record(go)
            transforms=[]
            for loc,cp in walk_pointers(gr.get('tree',{})):
                if loc.startswith('.m_Component[') and cp['m_PathID']:
                    dest=deref(go,cp)
                    if dest.type.name in ('Transform','RectTransform'):transforms.append(dest)
            for tr in transforms:
                seen=set()
                while key(tr) not in seen:
                    seen.add(key(tr));rr=context_record(tr);tree=rr.get('tree',{})
                    if tree.get('m_GameObject',{}).get('m_PathID'):context_record(deref(tr,tree['m_GameObject']))
                    father=tree.get('m_Father',{})
                    if not father.get('m_PathID'):break
                    tr=deref(tr,father)
    process_queue()
    def safe_tree(value,location,redactions):
        if isinstance(value,(bytes,bytearray)):
            r=dict(location=location,bytes=len(value),sha256=sha(bytes(value)));redactions.append(r)
            return dict(binary_buffer_omitted=True,bytes=r['bytes'],sha256=r['sha256'])
        if isinstance(value,dict):return {k:safe_tree(v,location+'.'+str(k),redactions) for k,v in value.items()}
        if isinstance(value,(list,tuple)):return [safe_tree(v,location+f'[{i}]',redactions) for i,v in enumerate(value)]
        return value
    def chunks(rows,prefix,n=200):
        result=[]
        for start in range(0,len(rows),n):
            group=rows[start:start+n];b=''.join(json.dumps(r,ensure_ascii=True,separators=(',',':'))+'\n' for r in group).encode();p=out/f'{prefix}-{start//n:04d}.jsonl.gz';compressed=gzip.compress(b,mtime=0);assert len(compressed)<5_000_000,(p,len(compressed));p.write_bytes(compressed);result.append(dict(path=p.name,rows=len(group),sha256=sha(compressed)))
        return result
    rows=[]
    for _,r in sorted(records.items()):
        assert r is not None
        redactions=[];r=safe_tree(r,'',redactions)
        if redactions:r['binary_buffer_redactions']=redactions
        rows.append(r)
    index=dict(schema=1,provisional=True,status='PINNED_SERIALIZED_VISUAL_CHAIN_NOT_RENDER_OR_RUNTIME',ui_classes=sorted(CORE_UI),xapk_sha256=XAPK_SHA,inputs=inputs,tool_sha256=sha(Path(__file__).read_bytes()),toolchain=dict(UnityPy=UnityPy.__version__),roots=roots,resource_roots=resource_rows,files=[dict(serialized_file=n,externals=[dict(path=e.path,type=e.type) for e in sf.externals]) for n,sf in files],objects=chunks(rows,'objects'),links=chunks(links,'links',2000),counts=dict(Counter(r['type'] for r in rows)),read_failures=[{k:r[k] for k in ('serialized_file','path_id','type','error')} for r in rows if r['status']=='failed'],header_only=[{k:r[k] for k in ('serialized_file','path_id','class_name','tree_error')} for r in rows if 'tree_error' in r],unresolved_link_count=sum(l['status']=='unresolved' for l in links))
    (out/'index.json').write_text(json.dumps(index,indent=2)+'\n');print(json.dumps(dict(objects=len(rows),links=len(links),counts=index['counts'],read_failures=len(index['read_failures']),header_only=len(index['header_only']),unresolved=index['unresolved_link_count'])))
if __name__=='__main__':
    try:main()
    except Exception:
        import traceback
        detail=traceback.format_exc()
        print('::error::'+detail.replace('%','%25').replace('\r','%0D').replace('\n','%0A'),flush=True)
        raise

