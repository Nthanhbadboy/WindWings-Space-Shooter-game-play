"""L3 chain delivery: UI/gameplay root -> typed pose/renderer -> assets/motion/events/audio.
Static source data and decoded channels; not Unity playback or rendered screenshots.
"""
import gzip,hashlib,importlib.util,json,math,re,tempfile,zlib
from collections import Counter,defaultdict
from pathlib import Path
from tools.verify.l3_chain_graph import ROOT,RAW,Graph,key,identity,read_chunks,bool_flag
from tools.verify.balloon_animation import decode_stream,width
from tools.verify.combat_rate_consumers import class_text,fields
OUT=ROOT/'datas/l3_scene_chains.json.gz'
RENDER={'SpriteRenderer','SpriteMask','MeshRenderer','SkinnedMeshRenderer','ParticleSystemRenderer','LineRenderer','TrailRenderer','Camera','Canvas'}
VISUAL_MB={'TextMeshPro','TextMeshProUGUI','SkeletonAnimation','SkeletonGraphic','SkeletonRenderer'}
ASSETS={'Sprite','SpriteAtlas','Texture2D','Material','Shader','Mesh','TextAsset','AnimationClip','AnimatorController','AnimatorOverrideController','AudioClip','AudioMixerController','AudioMixerGroupController','AudioMixerSnapshotController','Avatar','Font'}
def methods(dump):
    spec=importlib.util.spec_from_file_location('l3_dump','tools/apk-analyze/il2cpp_consts.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    with tempfile.NamedTemporaryFile('w+') as f:
        f.write(dump);f.flush();rows=mod.parse_dump(f.name)
    out=defaultdict(list)
    for cls,ns,name,offset,rva,sig in rows:out[(ns,cls,name)].append(dict(namespace=ns,cls=cls,name=name,rva=hex(rva),signature=sig))
    return out

def persistent_calls(tree,path=''):
    if isinstance(tree,dict):
        if isinstance(tree.get('m_MethodName'),str) and 'm_Target' in tree:yield path,tree
        for k,v in tree.items():yield from persistent_calls(v,path+'.'+k)
    elif isinstance(tree,list):
        for i,v in enumerate(tree):yield from persistent_calls(v,path+f'[{i}]')
def scalar_fields(tree,path=''):
    if not isinstance(tree,dict) or 'm_FileID' in tree and 'm_PathID' in tree:return
    for field,value in tree.items():
        name=path+'.'+field if path else field
        if isinstance(value,dict):yield from scalar_fields(value,name)
        elif isinstance(value,(int,float,bool)):yield name,value

def decode_motion(row):
    t=row.get('tree',{});muscle=t.get('m_MuscleClip',{});data=muscle.get('m_Clip',{}).get('data',{});stream=data.get('m_StreamedClip');dense=data.get('m_DenseClip');constant=data.get('m_ConstantClip',{}).get('data',[]);bindings=t.get('m_ClipBindingConstant',{}).get('genericBindings',[])
    out=dict(identity=identity(key(row)),name=t.get('m_Name'),sample_rate=t.get('m_SampleRate'),start=muscle.get('m_StartTime'),stop=muscle.get('m_StopTime'),loop=muscle.get('m_LoopTime'),events=t.get('m_Events',[]),bindings=bindings,ordinary_curves={k:t[k] for k in ('m_PositionCurves','m_RotationCurves','m_ScaleCurves','m_FloatCurves','m_PPtrCurves','m_EulerCurves') if k in t})
    if stream is None or dense is None:out['status']='ordinary_curves_only_no_muscle_storage';return out
    try:
        stream_count=stream['curveCount']+stream.get('discreteCurveCount',0);frames=decode_stream(stream['data'],stream_count);assert len(dense['m_SampleArray'])==dense['m_FrameCount']*dense['m_CurveCount'],'dense sample array shape'
        out.update(status='numeric_stream_dense_constant_decoded_not_playback',streamed=frames,dense=dense,constants=constant,continuous_stream_curve_count=stream['curveCount'],discrete_curve_count=stream.get('discreteCurveCount',0),pptr_curve_mapping=t.get('m_ClipBindingConstant',{}).get('pptrCurveMapping',[]),channel_count=stream_count+dense['m_CurveCount']+len(constant),binding_channel_count=sum(width(b) for b in bindings))
        out['binding_coverage_exact']=out['channel_count']==out['binding_channel_count']
        cursor=0;pptr_keys=[]
        for bi,binding in enumerate(bindings):
            if binding.get('isPPtrCurve'):
                keys=[]
                for frame in frames:
                    for k in frame['keys']:
                        if k['index']==cursor:
                            v=k['value'];mi=int(v) if math.isfinite(v) and v.is_integer() else None
                            keys.append(dict(time=frame['time'],mapping_index=mi,reference=out['pptr_curve_mapping'][mi] if mi is not None and 0<=mi<len(out['pptr_curve_mapping']) else None))
                pptr_keys.append(dict(binding_index=bi,channel=cursor,keys=keys,interpolation='discrete mapping index; NEVER blend sprite pointers'))
            cursor+=width(binding)
        out['discrete_pptr_keys']=pptr_keys
    except Exception as e:out.update(status='decode_error',error=repr(e))
    return out

def build():
    index_blob=(RAW/'index.json').read_bytes();index=json.loads(index_blob);assert index['xapk_sha256']=='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
    rows=list(read_chunks(index,'objects'));raw_locations={};offset=0
    for chunk in index['objects']:
        for row_index,r in enumerate(rows[offset:offset+chunk['rows']]):raw_locations[key(r)]=dict(path=str((RAW/chunk['path']).relative_to(ROOT)),row=row_index)
        offset+=chunk['rows']
    g=Graph(rows,read_chunks(index,'links'));dump_blob=(ROOT/'reverse-engineering/il2cpp/dump.cs.gz').read_bytes();dump=gzip.decompress(dump_blob).decode();decl=methods(dump)
    catalog_blob=(ROOT/'reverse-engineering/raw/asset-pack-v2/catalog.json.gz').read_bytes();catalog=json.loads(gzip.decompress(catalog_blob));assert catalog['xapk_sha256']==index['xapk_sha256'];media={key(r):r for r in catalog['objects']}
    audio_blob=(ROOT/'reverse-engineering/raw/audio-rules/contracts.json.gz').read_bytes();audio=json.loads(gzip.decompress(audio_blob));enum_names={v:k for k,v in audio['clip_enum'].items()}
    assets=[];motion=[];registry={};callbacks=[];animators=[];bindings=[];nodes=[];roots=[];root_components=[];counts=Counter();errors=[];enum_fields={}
    def candidates(component,name):
        r=g.rows.get(component,{})
        if r.get('type')=='MonoBehaviour':ns,cls=r.get('namespace',''),r.get('class_name','')
        else:ns,cls='UnityEngine',r.get('type','')
        return decl.get((ns,cls,name),[])
    for r in rows:
        k=key(r);kind=r['type'];tree=g.tree(k);cls=r.get('class_name')
        if kind in ASSETS or cls in ('TMP_FontAsset','SkeletonDataAsset','SpineAtlasAsset','AtlasAsset'):
            match=media.get(k);outputs=match.get('outputs',[]) if match and match.get('type')==kind else []
            assets.append(dict(identity=identity(k),type=kind,class_name=cls,name=tree.get('m_Name',r.get('name')),raw_object_sha256=r['raw_object_sha256'],raw_location=raw_locations[k],projection=r.get('projection'),media_outputs=outputs,properties=tree if kind=='Material' else None,references=[dict(field=loc,target=identity(target),type=typ,snapshotted=target in g.rows) for loc,target,typ in g.refs.get(k,[]) if typ in ASSETS or typ=='MonoBehaviour']))
        if kind=='AnimationClip':
            m=decode_motion(r);m['pptr_targets']=[identity(g.target(k,f'.m_ClipBindingConstant.pptrCurveMapping[{i}]')) for i,_ in enumerate(tree.get('m_ClipBindingConstant',{}).get('pptrCurveMapping',[]))];motion.append(m)
        if cls=='SoundClip':
            clip=g.target(k,'.soundClip');registry[tree.get('m_Name','')]=dict(registry=identity(k),clip=identity(clip),clip_snapshot=g.rows.get(clip,{}).get('status'),media_outputs=media.get(clip,{}).get('outputs',[]))
        if kind=='MonoBehaviour':
            for path,call in persistent_calls(tree):
                target=g.target(k,path+'.m_Target');name=call['m_MethodName'];callbacks.append(dict(owner=identity(k),field=path,call=call,target=identity(target),object_argument=identity(g.target(k,path+'.m_Arguments.m_ObjectArgument')),method_candidates=candidates(target,name) if target else [],status='serialized_persistent_call_not_invoked'))
    # Serialized enum fields are selected by dump declaration, never by a field-name guess.
    sound_fields=[]
    for r in rows:
        if r['type']!='MonoBehaviour':continue
        cls=r.get('class_name','');tree=g.tree(key(r))
        if cls not in enum_fields:
            try:enum_fields[cls]=[f['name'] for f in fields(class_text(dump,cls)).values() if re.search(r'\bAllClipName(?:\[\])?\s',f['declaration'])]
            except (ValueError,AssertionError):enum_fields[cls]=[]
        for field in enum_fields[cls]:
            value=tree.get(field)
            if isinstance(value,int):sound_fields.append(dict(owner=identity(key(r)),class_name=cls,field=field,value=value,enum=enum_names.get(value),registry=registry.get(enum_names.get(value)),enabled=bool_flag(tree.get('m_Enabled')),native_rules=[rule for rule in audio['rules'] if rule.get('source_field','').split('+')[0]==field and any(m.startswith(cls+'.') for m in rule.get('evidence_method_ids',[]))]))
    for root in index['roots']:
        target=key(root['target'])
        if g.rows.get(target,{}).get('type')!='GameObject':continue
        descendants,issues=g.descendants(target);ri=len(roots);root_info=dict(kind=root['kind'],label=root['label'],gameobject=identity(target),nodes=len(descendants),issues=issues);roots.append(root_info);root_components.append({c for n in descendants for c in n['components']});errors.extend(issues)
        for n in descendants:
            go=n['gameobject'];comps=[]
            for c in n['components']:
                row=g.rows.get(c)
                if row is None:continue
                typ=row['type'];cls=row.get('class_name');tree=g.tree(c)
                if typ in RENDER|{'Animator','Animation','ParticleSystem','AudioSource'} or cls in VISUAL_MB:
                    comps.append(dict(identity=identity(c),type=typ,class_name=cls,enabled=bool_flag(tree.get('m_Enabled')),properties=tree if typ not in ('ParticleSystem',) and cls not in VISUAL_MB else None,raw_snapshot_only=typ=='ParticleSystem' or cls in VISUAL_MB,references=[dict(field=loc,target=identity(t),type=kind,snapshotted=t in g.rows) for loc,t,kind in g.refs.get(c,[]) if kind in ASSETS or kind=='MonoBehaviour']))
            nodes.append(dict(root=ri,gameobject=identity(go),transform=identity(n['transform']),parent=identity(n['parent']),component_identities=[dict(identity=identity(c),type=g.rows.get(c,{}).get('type'),class_name=g.rows.get(c,{}).get('class_name'),raw_location=raw_locations.get(c)) for c in n['components']],gameobject_properties=g.tree(go),transform_properties=g.tree(n['transform']),path=n['path'],activity_within_root=n['activity'],layout_frame_matrix=n['matrix'],components=comps))
    # Animation paths bind within the actual Animator GO subtree, never across prefab roots.
    field_cache={}
    for r in rows:
        if r['type'] not in ('Animator','Animation'):continue
        ak=key(r);go=g.target(ak,'.m_GameObject')
        if go not in g.go_transform:continue
        descendants,issues=g.descendants(go);paths=defaultdict(list)
        for n in descendants:paths[zlib.crc32(n['path'].encode())].append(n)
        clip_keys=sorted({target for _,target,kind in g.asset_closure(ak,{'AnimatorController','AnimatorOverrideController','AnimationClip'}) if kind=='AnimationClip'})
        animators.append(dict(animator=identity(ak),gameobject=identity(go),enabled=bool_flag(g.tree(ak).get('m_Enabled')),clips=[identity(c) for c in clip_keys],subtree_issues=issues))
        for ck in clip_keys:
            clip=g.rows.get(ck,{})
            for bi,b in enumerate(clip.get('tree',{}).get('m_ClipBindingConstant',{}).get('genericBindings',[])):
                found=paths.get(b['path'],[]);script=g.target(ck,f'.m_ClipBindingConstant.genericBindings[{bi}].script');targets=[]
                for n in found:
                    if b['typeID']==1:
                        targets.append(identity(n['gameobject']));continue
                    for comp in n['components']:
                        rr=g.rows.get(comp,{})
                        if b['typeID']==4:accept=rr.get('type') in ('Transform','RectTransform')
                        elif b['typeID']==114:accept=rr.get('type')=='MonoBehaviour' and script is not None and g.target(comp,'.m_Script')==script
                        else:accept=rr.get('class_id')==b['typeID']
                        if accept:targets.append(identity(comp))
                property_candidates=[]
                for target in targets:
                    tk=key(target)
                    if tk not in field_cache:
                        field_cache[tk]=defaultdict(list)
                        for name,value in scalar_fields(g.tree(tk)):field_cache[tk][zlib.crc32(name.encode())].append(dict(field=name,serialized_value=value))
                    for candidate in field_cache[tk].get(b['attribute'],[]):property_candidates.append(dict(target=target,**candidate))
                bindings.append(dict(property_crc32_candidates=property_candidates,animator=identity(ak),clip=identity(ck),binding_index=bi,binding=b,path_candidates=[dict(path=n['path'],gameobject=identity(n['gameobject'])) for n in found],component_targets=targets,status='unique_target' if len(targets)==1 else 'ambiguous_targets' if targets else 'unresolved_target'))
            for event in clip.get('tree',{}).get('m_Events',[]):
                receivers=[dict(component=identity(comp),methods=candidates(comp,event['functionName']),enabled=bool_flag(g.tree(comp).get('m_Enabled'))) for comp in g.components.get(go,[]) if candidates(comp,event['functionName'])]
                callbacks.append(dict(owner=identity(ak),gameobject=identity(go),clip=identity(ck),event=event,receiver_candidates=receivers,status='same_go_declared_method_candidate_not_runtime_delivery'))
    asset_keys={key(a['identity']) for a in assets}
    wing_path=ROOT/'datas/wing_emission_flow.json';wing_blob=wing_path.read_bytes();wing_contract=json.loads(wing_blob)
    assert wing_contract['sound']['clip']==5
    for ri,components in enumerate(root_components):
        roots[ri]['node_indices']=[i for i,n in enumerate(nodes) if n['root']==ri]
        roots[ri]['callback_indices']=[i for i,c in enumerate(callbacks) if key(c['owner']) in components]
        roots[ri]['sound_indices']=[i for i,c in enumerate(sound_fields) if key(c['owner']) in components]
        roots[ri]['animator_indices']=[i for i,a in enumerate(animators) if key(a['animator']) in components]
        seen=set();queue=list(components);root_assets=set()
        while queue:
            owner=queue.pop()
            if owner in seen:continue
            seen.add(owner)
            for _,target,_ in g.refs.get(owner,[]):
                if target in asset_keys:root_assets.add(target);queue.append(target)
        for i in roots[ri]['sound_indices']:
            reg=sound_fields[i]['registry']
            if reg and reg['clip']:root_assets.add(key(reg['clip']))
        roots[ri]['native_sound_links']=[]
        for component in sorted(components):
            cls=g.rows.get(component,{}).get('class_name')
            if cls in ('Player_Attack_13','Player_Attack_22','Player_Attack_23','Player_Attack_24'):
                roots[ri]['native_sound_links'].append(dict(component=identity(component),class_name=cls,sound_enum='Sfx_Shot1',clip_enum=5,registry=registry.get('Sfx_Shot1'),evidence='datas/wing_emission_flow.json: sound + dispatch; demo suppresses, normal/super gate differs; not actual mix'))
                reg=registry.get('Sfx_Shot1')
                if reg and reg['clip']:root_assets.add(key(reg['clip']))
        roots[ri]['asset_identities']=[identity(k) for k in sorted(root_assets)]
    counts.update(objects=len(rows),root_views=len(roots),logical_nodes=len(nodes),visual_nodes=sum(bool(n['components']) for n in nodes),assets=len(assets),animators=len(animators),clips=len(motion),bindings=len(bindings),callbacks=len(callbacks),serialized_sound_fields=len(sound_fields),sound_registry=len(registry))
    scene_context=[dict(identity=identity(key(r)),type=r['type'],class_name=r.get('class_name'),gameobject=identity(g.target(key(r),'.m_GameObject')),properties=g.tree(key(r)),raw_location=raw_locations[key(r)]) for r in rows if r['type'] in ('Camera','Canvas') or r.get('class_name')=='CanvasScaler']
    camera_blob=(ROOT/'datas/camera_scaler_contract.json').read_bytes();camera_contract=json.loads(camera_blob)
    assert camera_contract['sources']['dump_sha256_decompressed']==hashlib.sha256(gzip.decompress(dump_blob)).hexdigest()
    for context in scene_context:
        if context['type']=='Camera':
            context['native_size_writers']=[dict(component=c['identity'],serialized_enabled=c['serialized_component_enabled'],write_order=next(i for i,p in enumerate(c['native_write_order']) if key(p)==key(context['identity']))) for c in camera_contract['components'] if any(key(p)==key(context['identity']) for p in c['native_write_order'])]
    return dict(native_camera_contract=dict(path='datas/camera_scaler_contract.json',sha256=hashlib.sha256(camera_blob).hexdigest(),formula=camera_contract['formula'],factor=camera_contract['factor'],minimum=camera_contract['minimum']),scene_context=scene_context,schema=1,provisional=True,scope='Typed hierarchy + serialized enabled/activity + root-frame pose + media identities + motion channels/bindings/events + sound registry. No Unity rendering/layout/blending/physics or callback invocation. All shader/binary omissions and header-only failures remain in raw index.',counts=dict(counts),input_index_sha256=hashlib.sha256(index_blob).hexdigest(),evidence={'dump_sha256':hashlib.sha256(dump_blob).hexdigest(),'catalog_sha256':hashlib.sha256(catalog_blob).hexdigest(),'audio_rules_sha256':hashlib.sha256(audio_blob).hexdigest(),'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'wing_feedback_sha256':hashlib.sha256(wing_blob).hexdigest(),'graph_tool_sha256':hashlib.sha256((ROOT/'tools/verify/l3_chain_graph.py').read_bytes()).hexdigest()},source_counts=index['counts'],source_read_failures=index['read_failures'],source_header_only=index['header_only'],edge_status=dict(g.edge_status),transform_errors=g.transform_errors,hierarchy_errors=errors,roots=roots,registry=registry,sections=dict(nodes=nodes,assets=assets,motion=motion,callbacks=callbacks,animation_bindings=bindings,animators=animators,sounds=sound_fields))

def write(d):
    directory=ROOT/'datas/l3-scene-chains';directory.mkdir(exist_ok=True);sections=d.pop('sections');chunks={}
    for section,rows in sections.items():
        chunks[section]=[]
        for start in range(0,len(rows),3000):
            p=directory/f'{section}-{start//3000:03}.json.gz';b=gzip.compress(json.dumps(rows[start:start+3000],ensure_ascii=True,separators=(',',':')).encode(),mtime=0);assert len(b)<5_000_000,(p,len(b));p.write_bytes(b);chunks[section].append(dict(path=str(p.relative_to(ROOT)),rows=len(rows[start:start+3000]),sha256=hashlib.sha256(b).hexdigest()))
    d['chunks']=chunks;OUT.write_bytes(gzip.compress(json.dumps(d,ensure_ascii=True,separators=(',',':')).encode(),mtime=0));assert OUT.stat().st_size<5_000_000
    return d
if __name__=='__main__':
    d=write(build());print(json.dumps(dict(counts=d['counts'],edges=d['edge_status'],hierarchy_errors=len(d['hierarchy_errors'])),indent=2))
