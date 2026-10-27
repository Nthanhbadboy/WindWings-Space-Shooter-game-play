"""Layout-owner visual construction data, not Unity draw calls, text shaping or VFX playback."""
import argparse,gzip,hashlib,json,zlib,math
from collections import Counter,defaultdict
from functools import lru_cache
from pathlib import Path
from tools.verify.l3_chain_graph import ROOT,Graph,key,identity
from tools.verify.l3_scene_chains import decode_motion,scalar_fields
from tools.verify.l3_animator_programs import controller_program,probe_channels
RAW=ROOT/'reverse-engineering/raw/l3-visual-surface'
OUT=ROOT/'datas/l3_visual_surface.json.gz'
RENDER={'SpriteRenderer','MeshRenderer','SkinnedMeshRenderer','ParticleSystemRenderer','TrailRenderer','LineRenderer','SpriteMask','CanvasRenderer'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def read_source():
    index=json.loads((RAW/'index.json').read_bytes());tables={};locations={}
    for name in ('objects','links'):
        rows=[]
        for chunk in index[name]:
            p=RAW/chunk['path'];assert digest(p)==chunk['sha256'];part=[json.loads(l) for l in gzip.decompress(p.read_bytes()).splitlines()];assert len(part)==chunk['rows']
            if name=='objects':
                for i,row in enumerate(part):locations[key(row)]=dict(path=str(p.relative_to(ROOT)),row=i)
            rows.extend(part)
        tables[name]=rows
    assert len(locations)==len(tables['objects'])
    return index,Graph(tables['objects'],tables['links']),locations,tables['links']

def animation_bindings(g,animator,clips,field_cache):
    go=g.target(animator,'.m_GameObject');nodes,issues=g.descendants(go);paths=defaultdict(list);out=[]
    for n in nodes:paths[zlib.crc32(n['path'].encode())].append(n)
    for ck in clips:
        for bi,b in enumerate(g.tree(ck).get('m_ClipBindingConstant',{}).get('genericBindings',[])):
            matches=paths.get(b['path'],[]);script=g.target(ck,f'.m_ClipBindingConstant.genericBindings[{bi}].script');targets=[];properties=[]
            for n in matches:
                if b['typeID']==1:targets.append(n['gameobject']);continue
                for c in n['components']:
                    r=g.rows.get(c,{})
                    accept=r.get('type') in ('Transform','RectTransform') if b['typeID']==4 else r.get('type')=='MonoBehaviour' and script is not None and g.target(c,'.m_Script')==script if b['typeID']==114 else r.get('class_id')==b['typeID']
                    if accept:targets.append(c)
            for target in targets:
                if target not in field_cache:
                    h=defaultdict(list)
                    for name,value in scalar_fields(g.tree(target)):h[zlib.crc32(name.encode())].append(dict(field=name,serialized_value=value))
                    field_cache[target]=h
                properties.extend(dict(target=identity(target),**p) for p in field_cache[target].get(b['attribute'],[]))
            out.append(dict(animator=identity(animator),clip=identity(ck),binding_index=bi,binding=b,path_candidates=[dict(path=n['path'],gameobject=identity(n['gameobject'])) for n in matches],targets=[identity(t) for t in targets],property_candidates=properties,status='unique_target' if len(targets)==1 else 'ambiguous_targets' if targets else 'unresolved_target'))
    return out,issues

def build():
    index,g,locations,links=read_source();assert index['layout_artifact_sha256']==digest(ROOT/'datas/l3_layout.json.gz')
    catalog=json.load(gzip.open(ROOT/'reverse-engineering/raw/asset-pack-v2/catalog.json.gz'));assert catalog['xapk_sha256']==index['xapk_sha256'];media={key(r):r for r in catalog['objects']}
    source_fonts=json.load(gzip.open(ROOT/'datas/font_language_contract.json.gz'));known_fonts={key(f['identity']):f for f in source_fonts['fonts']}
    def refs(k):return [dict(field=loc,target=identity(t),type=typ,snapshotted=t in g.rows) for loc,t,typ in g.refs.get(k,[])]
    def base(k):return dict(identity=identity(k),raw_location=locations[k],raw_object_sha256=g.rows[k]['raw_object_sha256'])
    def exports(k):return media.get(k,{}).get('outputs',[])
    renderers=[];materials=[];shaders=[];fonts=[];texts=[];geometry=[];particles=[];attachments=[];controllers=[];motion=[];bindings=[];field_cache={}
    for k,r in sorted(g.rows.items()):
        typ=r['type'];t=g.tree(k);cls=r.get('class_name');go=g.target(k,'.m_GameObject')
        if typ in RENDER:
            mesh=g.target(k,'.m_Mesh')
            if typ=='MeshRenderer':
                filters=[c for c in g.components.get(go,[]) if g.rows.get(c,{}).get('type')=='MeshFilter'];mesh=g.target(filters[0],'.m_Mesh') if len(filters)==1 else None
            sprite=g.target(k,'.m_Sprite');tr=g.go_transform.get(go)
            renderers.append(dict(**base(k),type=typ,gameobject=identity(go),transform=identity(tr),gameobject_properties=g.tree(go) if go in g.rows else {},transform_properties=g.tree(tr) if tr in g.rows else {},serialized_enabled=t.get('m_Enabled'),properties={f:v for f,v in t.items() if f not in ('m_GameObject','m_Materials')},materials=[identity(target) for loc,target,tt in g.refs.get(k,[]) if loc.startswith('.m_Materials[')],sprite=identity(sprite),mesh=identity(mesh),sprite_media=exports(sprite),sprite_source_texture=identity(g.target(sprite,'.m_RD.texture')) if sprite else None,sprite_source_atlas=identity(g.target(sprite,'.m_SpriteAtlas')) if sprite else None,references=refs(k),scope='Serialized state, not actual visibility/draw order or property-block runtime state'))
        if typ=='Material':
            shader=g.target(k,'.m_Shader');materials.append(dict(**base(k),name=t['m_Name'],shader=identity(shader),properties=t,references=refs(k),scope='Saved overrides; custom queue -1 is not a resolved GPU queue; no automatic shader keyword/platform selection'))
        if typ=='Shader':
            parsed=t.get('m_ParsedForm',{});shaders.append(dict(**base(k),name=parsed.get('m_Name') or t.get('m_Name'),serialized_object_name=t.get('m_Name'),platforms=t.get('platforms'),properties=parsed.get('m_PropInfo'),subshaders=[dict(index=si,tags=s.get('m_Tags'),lod=s.get('m_LOD'),passes=[dict(index=pi,type=p.get('m_Type'),name=p.get('m_Name'),state=p.get('m_State'),tags=p.get('m_Tags'),platforms=p.get('m_Platforms')) for pi,p in enumerate(s.get('m_Passes',[]))]) for si,s in enumerate(parsed.get('m_SubShaders',[]))],analysis={f:v for f,v in r.get('shader_analysis',{}).items() if f!='text'},binary_buffer_redactions=r.get('binary_buffer_redactions',[]),scope='Serialized pass states + decompiler analysis, NOT GPU execution/valid replacement shader'))
        if 'geometry' in r:
            geometry.append(dict(**base(k),type=typ,name=t.get('m_Name'),geometry=r['geometry'],sprite_properties={f:t.get(f) for f in ('m_Rect','m_Offset','m_Border','m_PixelsToUnits','m_Pivot','m_Extrude','m_IsPolygon')} if typ=='Sprite' else None,references=refs(k),media=exports(k),scope='Decoded local vertices/UVs/indices; live atlas overrides, sliced/tiled sprite, skinning, shader displacement and runtime deformation not applied'))
        if cls=='TMP_FontAsset':
            old=known_fonts[k];assert t['m_GlyphTable']==old['glyph_table'] and t['m_CharacterTable']==old['character_table'];atlases=[]
            for i,_ in enumerate(t['m_AtlasTextures']):
                a=g.target(k,f'.m_AtlasTextures[{i}]');ar=g.rows.get(a,{});atlases.append(dict(identity=identity(a),width=ar.get('width'),height=ar.get('height'),media=exports(a)))
            glyphs={v['m_Index']:v for v in t['m_GlyphTable']};assert len(glyphs)==len(t['m_GlyphTable'])
            for ch in t['m_CharacterTable']:assert ch['m_GlyphIndex'] in glyphs
            for glyph in glyphs.values():
                a=atlases[glyph['m_AtlasIndex']];rect=glyph['m_GlyphRect'];assert 0<=rect['m_X']<=rect['m_X']+rect['m_Width']<=a['width'] and 0<=rect['m_Y']<=rect['m_Y']+rect['m_Height']<=a['height']
            fonts.append(dict(**base(k),name=t['m_Name'],face=t['m_FaceInfo'],characters=t['m_CharacterTable'],glyphs=t['m_GlyphTable'],atlases=atlases,material=identity(g.target(k,'.material')),fallbacks=[identity(g.target(k,f'.m_FallbackFontAssetTable[{i}]')) for i in range(len(t['m_FallbackFontAssetTable']))],population_mode=t['m_AtlasPopulationMode'],references=refs(k)))
        if cls in ('TextMeshPro','TextMeshProUGUI'):
            texts.append(dict(**base(k),class_name=cls,gameobject=identity(go),text=t.get('m_text'),font=identity(g.target(k,'.m_fontAsset')),material=identity(g.target(k,'.m_sharedMaterial')),properties={f:v for f,v in t.items() if f not in ('m_Script','m_GameObject')},scope='Serialized text/style, NOT localized live string, markup parsing, shaping or generated glyph mesh'))
        if typ=='ParticleSystem':
            particles.append(dict(**base(k),gameobject=identity(go),properties={f:v for f,v in t.items() if not isinstance(v,dict)},modules=[dict(field=f,enabled=v.get('enabled'),raw_keys=list(v)) for f,v in t.items() if isinstance(v,dict)],renderers=[identity(c) for c in g.components.get(go,[]) if g.rows.get(c,{}).get('type')=='ParticleSystemRenderer'],references=refs(k),scope='Full serialized numeric modules via raw_location, not simulation, random seed scheduling or generated particle vertices'))
        if typ=='AnimatorController':controllers.append(controller_program(dict(identity=identity(k),raw_location=locations[k],references=refs(k)),r))
        if typ=='AnimationClip':
            m=decode_motion(r);m['raw_location']=locations[k];m['pptr_targets']=[identity(g.target(k,f'.m_ClipBindingConstant.pptrCurveMapping[{i}]')) for i,_ in enumerate(t.get('m_ClipBindingConstant',{}).get('pptrCurveMapping',[]))];motion.append(m)
        if typ=='Animator':
            clips=sorted({target for _,target,kind in g.asset_closure(k,{'AnimatorController','AnimatorOverrideController','AnimationClip'}) if kind=='AnimationClip'});bb,issues=animation_bindings(g,k,clips,field_cache);bindings.extend(bb)
            attachments.append(dict(**base(k),gameobject=identity(go),properties=t,controllers=[identity(target) for loc,target,kind in g.refs.get(k,[]) if loc=='.m_Controller'],clips=[identity(c) for c in clips],subtree_issues=issues))
    sections=dict(renderers=renderers,materials=materials,shaders=shaders,geometry=geometry,fonts=fonts,texts=texts,particles=particles,animators=attachments,controllers=controllers,motion=motion,bindings=bindings)
    counts={name:len(rows) for name,rows in sections.items()};counts.update(objects=len(g.rows),roots=len(index['roots']),read_failures=len(index['read_failures']),header_only=len(index['header_only']),unresolved_edges=index['unresolved_link_count'],shader_analysis_status=dict(Counter(s['analysis'].get('status','not_attempted') for s in shaders)),geometry_status=dict(Counter(v['geometry']['status'] for v in geometry)),motion_status=dict(Counter(m['status'] for m in motion)),binding_status=dict(Counter(b['status'] for b in bindings)))
    inputs={str(p.relative_to(ROOT)):digest(p) for p in (RAW/'index.json',ROOT/'datas/l3_layout.json.gz',ROOT/'datas/font_language_contract.json.gz',ROOT/'reverse-engineering/raw/asset-pack-v2/catalog.json.gz',Path(__file__),ROOT/'tools/verify/l3_chain_graph.py',ROOT/'tools/verify/l3_scene_chains.py',ROOT/'tools/verify/l3_animator_programs.py')}
    return dict(schema=1,provisional=True,scope=index['scope']+'; construction data and explicit clip/glyph probes, NOT Unity render/VFX/shaping execution',inputs=inputs,counts=counts,source_read_failures=index['read_failures'],source_header_only=index['header_only'],unresolved_edges=[l for l in links if l['status']=='unresolved'],roots=index['roots'],source_gameobjects=[identity(k) for k,r in sorted(g.rows.items()) if r['type']=='GameObject'],default_font=source_fonts['settings']['default_font'],sections=sections)

def write(data):
    folder=ROOT/'datas/l3-visual-surface';folder.mkdir(exist_ok=True);header={k:v for k,v in data.items() if k!='sections'};header['chunks']={}
    for name,rows in data['sections'].items():
        chunks=[]
        for start in range(0,len(rows),400):
            p=folder/f'{name}-{start//400:03d}.json.gz';blob=gzip.compress(json.dumps(rows[start:start+400],separators=(',',':')).encode(),mtime=0);assert len(blob)<5_000_000;p.write_bytes(blob);chunks.append(dict(path=str(p.relative_to(ROOT)),rows=min(400,len(rows)-start),sha256=digest(p)))
        header['chunks'][name]=chunks
    OUT.write_bytes(gzip.compress(json.dumps(header,separators=(',',':')).encode(),mtime=0))

@lru_cache(maxsize=1)
def load():
    header=json.load(gzip.open(OUT));sections={}
    for name,chunks in header.pop('chunks').items():
        rows=[]
        for c in chunks:
            p=ROOT/c['path'];assert digest(p)==c['sha256'];part=json.load(gzip.open(p));assert len(part)==c['rows'];rows.extend(part)
        sections[name]=rows
    return dict(**header,sections=sections)

def glyph_probe(data,font,text):
    """Static exact-codepoint/ordered asset fallback lookup, not TMP rendering or shaping."""
    fonts={key(f['identity']):f for f in data['sections']['fonts']};start=key(font);out=[]
    def lookup(k,cp,seen):
        if k in seen or k not in fonts:return None
        seen=seen|{k};f=fonts[k];ch=next((c for c in f['characters'] if c['m_Unicode']==cp),None)
        if ch:
            glyph=next(g for g in f['glyphs'] if g['m_Index']==ch['m_GlyphIndex']);return dict(font=f['identity'],character=ch,glyph=glyph,atlas=f['atlases'][glyph['m_AtlasIndex']],face=f['face'])
        for fallback in f['fallbacks']:
            found=lookup(key(fallback),cp,seen) if fallback else None
            if found:return found
        return None
    if start not in fonts:raise ValueError('font outside recovered static bank')
    for char in text:
        found=lookup(start,ord(char),set());out.append(dict(character=char,codepoint=ord(char),status='static_glyph_and_atlas' if found else 'absent_in_selected_static_asset_chain',match=found))
    return dict(scope='Literal string, no rich-text parsing/case/style/font weights/global fallbacks/dynamic population/shaping/layout',glyphs=out)

def clip_probe(data,animator,clip,time):
    if not math.isfinite(time):raise ValueError('finite clip-local time required')
    a=next((a for a in data['sections']['animators'] if key(a['identity'])==key(animator)),None)
    if a is None or key(clip) not in {key(c) for c in a['clips']}:raise ValueError('clip not attached through this source animator controller closure')
    m=next(m for m in data['sections']['motion'] if key(m['identity'])==key(clip))
    if m['status']!='numeric_stream_dense_constant_decoded_not_playback':raise ValueError('clip storage not in supported numeric model')
    values=probe_channels(m,time);bybinding={v['binding_index']:v for v in values};out=[]
    from tools.verify.balloon_animation import width
    bb=[b for b in data['sections']['bindings'] if key(b['animator'])==key(animator) and key(b['clip'])==key(clip)]
    for b in sorted(bb,key=lambda v:v['binding_index']):
        v=bybinding[b['binding_index']]['channels'];entry=dict(binding=b,channels=v)
        if b['binding'].get('isPPtrCurve'):
            value=v[0]['value'];i=int(value) if value is not None and math.isfinite(value) and float(value).is_integer() else None;entry['pptr_target']=m['pptr_targets'][i] if i is not None and 0<=i<len(m['pptr_targets']) else None
        out.append(entry)
    return dict(scope='Explicit source-attached clip-local probe; no engine state selection/transition/blending/event delivery or whole-frame render',animator=animator,clip=clip,time=time,bindings=out)

def recipe_surface(gameobjects):
    d=load();sec=d['sections'];renderers=[r for r in sec['renderers'] if r['gameobject'] and key(r['gameobject']) in gameobjects];texts=[r for r in sec['texts'] if r['gameobject'] and key(r['gameobject']) in gameobjects];animators=[a for a in sec['animators'] if a['gameobject'] and key(a['gameobject']) in gameobjects]
    animator_ids={key(a['identity']) for a in animators};clip_ids={key(c) for a in animators for c in a['clips']};controller_ids={key(c) for a in animators for c in a['controllers']}
    motion=[m for m in sec['motion'] if key(m['identity']) in clip_ids];pptr_ids={key(t) for m in motion for t in m['pptr_targets'] if t}
    geometry_ids={key(r[field]) for r in renderers for field in ('sprite','mesh') if r[field]}|pptr_ids
    material_ids={key(m) for r in renderers for m in r['materials']}|{key(t['material']) for t in texts if t['material']}|{key(f['material']) for f in sec['fonts'] if f['material']}|pptr_ids
    materials=[m for m in sec['materials'] if key(m['identity']) in material_ids];shader_ids={key(m['shader']) for m in materials if m['shader']}
    covered={key(g) for g in d['source_gameobjects']}
    return dict(coverage=dict(requested_gameobjects=len(gameobjects),snapshotted_in_this_surface_scope=len(gameobjects & covered),outside_this_surface_scope=[identity(k) for k in sorted(gameobjects-covered)]),artifact='datas/l3_visual_surface.json.gz',sha256=digest(OUT),scope=d['scope'],renderers=renderers,texts=texts,materials=materials,shaders=[s for s in sec['shaders'] if key(s['identity']) in shader_ids],geometry=[g for g in sec['geometry'] if key(g['identity']) in geometry_ids],fonts=sec['fonts'],font_bank_scope='Global recovered static font candidates, NOT automatically selected for null component fonts',particles=[p for p in sec['particles'] if p['gameobject'] and key(p['gameobject']) in gameobjects],animators=animators,controllers=[c for c in sec['controllers'] if key(c['identity']) in controller_ids],motion=motion,bindings=[b for b in sec['bindings'] if key(b['animator']) in animator_ids])

def selected_raw_objects(surface):
    data=load();assert digest(RAW/'index.json')==data['inputs']['reverse-engineering/raw/l3-visual-surface/index.json']
    index=json.loads((RAW/'index.json').read_bytes());chunks={str((RAW/c['path']).relative_to(ROOT)):c for c in index['objects']};wanted={}
    for name in ('renderers','materials','shaders','geometry','fonts','texts','particles','animators','controllers','motion'):
        for row in surface[name]:wanted[key(row['identity'])]=row['raw_location']
    grouped=defaultdict(list)
    for k,loc in wanted.items():grouped[loc['path']].append((k,loc['row']))
    out=[]
    for path,selected in sorted(grouped.items()):
        p=ROOT/path;c=chunks[path];assert digest(p)==c['sha256'];rows=[json.loads(l) for l in gzip.decompress(p.read_bytes()).splitlines()];assert len(rows)==c['rows']
        for k,i in selected:assert key(rows[i])==k;out.append(rows[i])
    return sorted(out,key=key)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--font',type=int);p.add_argument('--file',default='data.unity3d/resources.assets');p.add_argument('--text');p.add_argument('--animator',type=int);p.add_argument('--clip',type=int);p.add_argument('--clip-file');p.add_argument('--time',type=float);p.add_argument('--out',type=Path);a=p.parse_args()
    if a.font is not None:
        if a.text is None:p.error('--font requires --text')
        d=glyph_probe(load(),dict(serialized_file=a.file,path_id=a.font),a.text)
    elif a.animator is not None:
        if a.clip is None or a.clip_file is None or a.time is None:p.error('--animator requires --clip, --clip-file and --time')
        d=clip_probe(load(),dict(serialized_file=a.file,path_id=a.animator),dict(serialized_file=a.clip_file,path_id=a.clip),a.time)
    else:d=build()
    if a.font is None and a.animator is None and a.out is None:
        write(d);print(json.dumps(d['counts'],indent=2));return
    out=a.out or (OUT if a.font is None and a.animator is None else None);blob=json.dumps(d,separators=(',',':')).encode()
    if out:
        if out.suffix=='.gz':blob=gzip.compress(blob,mtime=0)
        assert len(blob)<5_000_000;out.write_bytes(blob)
    print(json.dumps(d.get('counts',d),indent=2,ensure_ascii=True))
if __name__=='__main__':main()
