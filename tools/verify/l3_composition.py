"""Source scene/template separation, world poses and explicit camera footprint probes."""
import argparse,gzip,json,math
from collections import Counter,defaultdict
from functools import lru_cache
from tools.verify.l3_chain_graph import ROOT,Graph,key,identity,bool_flag
from tools.verify.ui_composition import trs,multiply,IDENTITY,conjunction
from tools.verify.l3_visual_surface import read_source,load as surface_load,digest,clip_probe
from tools.verify.l3_composition_math import layer_gate,project_geometry,sprite_geometry
OUT=ROOT/'datas/l3_composition.json.gz'

def scene_file(file):return file in {f'data.unity3d/level{i}' for i in range(4)}

def merged_source():
    index,g,_,links=read_source();layout_path=ROOT/'reverse-engineering/raw/l3-layout-native/objects.json.gz';raw=json.load(gzip.open(layout_path));rows=dict(g.rows);overlap=0
    for r in raw['objects']:
        k=key(r)
        if k in rows:assert rows[k]['raw_object_sha256']==r['raw_object_sha256'];overlap+=1
        else:rows[k]=r
    unique={}
    for l in links+raw['links']:
        k=(key(l['owner']),l['location'])
        if k in unique:
            old=unique[k];assert old['status']==l['status'];assert old.get('target')==l.get('target')
        else:unique[k]=l
    return Graph(rows.values(),unique.values()),overlap

class Poses:
    def __init__(self,g):self.g=g;self.cache={}
    def get(self,t,seen=None):
        if t in self.cache:return self.cache[t]
        seen=set() if seen is None else seen
        if t is None or t not in self.g.rows:return dict(status='missing_transform',matrix=None,activity=None)
        if t in seen:return dict(status='parent_cycle',matrix=None,activity=None)
        tree=self.g.tree(t);go=self.g.target(t,'.m_GameObject');gt=self.g.tree(go) if go in self.g.rows else {};node=dict(local_pos=[tree.get('m_LocalPosition',{}).get(c) for c in 'xyz'],rotation=[tree.get('m_LocalRotation',{}).get(c) for c in 'xyzw'],scale=[tree.get('m_LocalScale',{}).get(c) for c in 'xyz']);local=trs(node)
        parent=self.g.target(t,'.m_Father');ptr=tree.get('m_Father');nonzero=ptr is not None and ptr.get('m_PathID')!=0
        if ptr is None or nonzero and parent is None:result=dict(status='unresolved_or_absent_parent',matrix=None,activity=None)
        elif local is None:result=dict(status='invalid_local_trs',matrix=None,activity=None)
        else:
            p=self.get(parent,seen|{t}) if parent else dict(matrix=list(IDENTITY),activity=True,status='known_serialized_affine')
            result=dict(status='known_serialized_affine' if p['matrix'] is not None else p['status'],matrix=multiply(p['matrix'],local) if p['matrix'] is not None else None,activity=conjunction(p['activity'],bool_flag(gt.get('m_IsActive'))))
        self.cache[t]=result;return result

def build():
    g,overlap=merged_source();poses=Poses(g);surface=surface_load();layout=json.load(gzip.open(ROOT/'datas/l3_layout.json.gz'));renderers=[]
    for r in surface['sections']['renderers']:
        k=key(r['identity']);go=key(r['gameobject']) if r['gameobject'] else None;p=poses.get(g.go_transform.get(go));t=r['properties']
        renderers.append(dict(identity=r['identity'],gameobject=r['gameobject'],source_context='serialized_scene' if scene_file(k[0]) else 'asset_template_NOT_placed',source_scene=k[0] if scene_file(k[0]) else None,layer=r['gameobject_properties'].get('m_Layer'),type=r['type'],serialized_enabled=r['serialized_enabled'],pose=p,sort_descriptors={f:t.get(f) for f in ('m_SortingLayerID','m_SortingLayer','m_SortingOrder','m_RendererPriority','m_SpriteSortPoint')},sprite=r['sprite'],mesh=r['mesh'],materials=r['materials'],raw_location=r['raw_location']))
    cameras=[]
    for c in layout['cameras']:
        k=key(c['identity']);go=key(c['gameobject']);p=poses.get(g.go_transform.get(go));assert p['matrix']==c['serialized_world_matrix'];cameras.append(dict(**c,source_context='serialized_scene' if scene_file(k[0]) else 'asset_template_NOT_placed',pose=p))
    groups=[]
    for file in sorted({c['identity']['serialized_file'] for c in cameras if scene_file(c['identity']['serialized_file'])}):
        depths=defaultdict(list)
        for c in cameras:
            if c['identity']['serialized_file']==file:depths[c['properties']['m_Depth']].append(dict(camera=c['identity'],clear_flags=c['properties']['m_ClearFlags'],mask=c['properties']['m_CullingMask'],target_display=c['properties']['m_TargetDisplay'],target_texture=c['properties']['m_TargetTexture']))
        groups.append(dict(scene=file,depth_groups=[dict(depth=d,cameras=rows) for d,rows in sorted(depths.items())],scope='Serialized depth groups, NOT observed loaded camera stack/render pipeline or tie-break order'))
    pairs=[]
    for c in cameras:
        ck=key(c['identity'])
        if not scene_file(ck[0]):continue
        for r in renderers:
            if r['source_scene']!=ck[0]:continue
            layer=r['layer'];pairs.append(dict(camera=c['identity'],renderer=r['identity'],layer=layer,mask_includes_layer=layer_gate(c['properties']['m_CullingMask']['m_Bits'],layer),serialized_renderer_active=conjunction(r['pose']['activity'],bool_flag(r['serialized_enabled'])),scope='Mask/activity preconditions only; no geometric or alpha visibility verdict'))
    inputs={str(p.relative_to(ROOT)):digest(p) for p in (ROOT/'reverse-engineering/raw/l3-visual-surface/index.json',ROOT/'reverse-engineering/raw/l3-layout-native/index.json',ROOT/'reverse-engineering/raw/l3-layout-native/objects.json.gz',ROOT/'datas/l3_layout.json.gz',ROOT/'datas/l3_visual_surface.json.gz',ROOT/'tools/verify/l3_composition.py',ROOT/'tools/verify/l3_composition_math.py',ROOT/'tools/verify/ui_composition.py',ROOT/'tools/verify/l3_chain_graph.py')}
    counts=dict(renderers=len(renderers),cameras=len(cameras),source_body_overlap_verified=overlap,merged_objects=len(g.rows),contexts=dict(Counter(r['source_context'] for r in renderers)),poses=dict(Counter(r['pose']['status'] for r in renderers)),scene_camera_renderer_pairs=len(pairs),layer_gate=dict(Counter(str(p['mask_includes_layer']) for p in pairs)))
    return dict(schema=1,provisional=True,scope='Serialized world hierarchy + mask/depth descriptors; explicit modeled projection/position geometry, NOT Unity render, actual scene loading or runtime visibility',inputs=inputs,counts=counts,cameras=cameras,renderers=renderers,scene_depth_groups=groups,scene_mask_pairs=pairs)

@lru_cache(maxsize=1)
def load():return json.load(gzip.open(OUT))

def probe(renderer,camera,width,height,half_height=None,size=None,world_override=None):
    d=load();rid=key(renderer);cid=key(camera);r=next(r for r in d['renderers'] if key(r['identity'])==rid);c=next(c for c in d['cameras'] if key(c['identity'])==cid)
    if world_override is None and (r['source_context']!='serialized_scene' or c['source_context']!='serialized_scene' or rid[0]!=cid[0]):raise ValueError('template/cross-scene projection requires explicit renderer world override; camera remains modeled selected snapshot')
    world=world_override if world_override is not None else r['pose']['matrix']
    if world is None:raise ValueError('world pose unavailable')
    surface=surface_load();rr=next(rr for rr in surface['sections']['renderers'] if key(rr['identity'])==rid);geometry=None
    if rr['type']=='SpriteRenderer' and rr['sprite']:
        gg=next((gg for gg in surface['sections']['geometry'] if key(gg['identity'])==key(rr['sprite'])),None)
        if gg:geometry=sprite_geometry(rr,gg,size)
    elif rr['type']=='MeshRenderer' and rr['mesh']:
        gg=next((gg for gg in surface['sections']['geometry'] if key(gg['identity'])==key(rr['mesh'])),None)
        if gg:geometry=dict(status='decoded_static_mesh_position_model',vertices=gg['geometry']['m_Vertices'],triangles=[f for submesh in gg['geometry']['triangles'] for f in submesh])
    result=dict(renderer=renderer,camera=camera,world_matrix=world,world_override_supplied=world_override is not None,layer_gate=layer_gate(c['properties']['m_CullingMask']['m_Bits'],r['layer']),serialized_renderer_activity=conjunction(r['pose']['activity'],bool_flag(r['serialized_enabled'])),serialized_camera_activity=conjunction(c['pose']['activity'],bool_flag(c['properties']['m_Enabled'])),geometry=geometry,scope='Explicit modeled camera/pose/position geometry; no actual visibility/UV/shader/stencil/occlusion or engine geometry claim')
    if geometry and geometry.get('vertices') is not None:result['projection']=project_geometry(geometry['vertices'],geometry['triangles'],world,c,width,height,half_height)
    else:result['projection']=dict(status='position_geometry_not_generated_for_this_renderer')
    return result

def alert_chain(width=1080,height=2400,time=.0625):
    from tools.verify.camera_scaler_contracts import scaled_ortho
    from tools.verify.l3_layout import instance_probe
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not float(v).is_integer() or not 0<v<2**31 for v in (width,height)):raise ValueError('positive int32 screen dimensions required for CameraScaler chain')
    contract=json.loads((ROOT/'datas/camera_scaler_contract.json').read_bytes());half=scaled_ortho(width,height,contract['factor'],contract['minimum']);layout=json.load(gzip.open(ROOT/'datas/l3_layout.json.gz'));scaler=next(i for i in layout['instances'] if key(i['identity'])==('data.unity3d/level2',6686));scaled=instance_probe(scaler,dict(main_half_height=half));assert scaled['model']==scaled['native']['size'];renderer=identity(('data.unity3d/level2',5105));surface=surface_load();clip=clip_probe(surface,identity(('data.unity3d/level2',4647)),identity(('data.unity3d/sharedassets2.assets',42)),time)
    return dict(provisional=True,scope='Synthetic viewport; modeled CameraScaler main/UI size, source Awake poses and explicit alert clip time. NOT device/Unity frame readback',viewport=[width,height],predicted_half_height=half,native_scaler=scaled,clip=clip,cameras=[probe(renderer,identity(('data.unity3d/level2',pid)),width,height,half,size=scaled['model']) for pid in (3975,3976)])

def recipe_composition(gameobjects):
    d=load();return dict(artifact=str(OUT.relative_to(ROOT)),sha256=digest(OUT),scope=d['scope'],renderers=[r for r in d['renderers'] if r['gameobject'] and key(r['gameobject']) in gameobjects],camera_candidates=d['cameras'],scene_depth_groups=d['scene_depth_groups'],camera_scope='Global source candidates grouped by serialized scene, NOT automatically loaded/selected for this prefab')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--alert',action='store_true');p.add_argument('--width',type=float,default=1080);p.add_argument('--height',type=float,default=2400);p.add_argument('--time',type=float,default=.0625);p.add_argument('--out',type=str);a=p.parse_args();d=alert_chain(a.width,a.height,a.time) if a.alert else build();out=ROOT/a.out if a.out else (None if a.alert else OUT)
    if out:
        blob=json.dumps(d,separators=(',',':')).encode();blob=gzip.compress(blob,mtime=0) if str(out).endswith('.gz') else blob;assert len(blob)<5_000_000;out.write_bytes(blob)
    print(json.dumps(d.get('counts',d),indent=2))
if __name__=='__main__':main()
