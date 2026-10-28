"""Explicit ordered source-write application to one shared modeled scene state.
This is a transaction/probe tool, NOT Unity scheduling, transition blending or rendering.
"""
import argparse,copy,gzip,json,math,zlib
from pathlib import Path
from tools.verify.l3_chain_graph import ROOT,key,identity
from tools.verify.ui_composition import IDENTITY,multiply,trs
from tools.verify.l3_composition import merged_source,Poses,load as composition_load,scene_file
from tools.verify.l3_composition_math import inverse,sprite_geometry,project_geometry
from tools.verify.l3_visual_surface import load as surface_load,clip_probe,digest
from tools.verify.l3_layout import load as layout_load,constants,model_probe,native_probe
from tools.verify.l3_layout_math import f32,scaler_step
from tools.verify.l3_layout_emulator import execute

class View:
    def __init__(self,frame):self.f=frame;self.rows=frame.g.rows;self.go_transform=frame.g.go_transform
    def tree(self,k):return self.f.trees.get(k,self.f.g.tree(k))
    def target(self,k,field):return self.f.refs.get((k,field),self.f.g.target(k,field))

class Frame:
    def __init__(self,width,height,main_camera=None,source=None):
        if any(isinstance(v,bool) or type(v) is not int or not 0<v<2**31 for v in (width,height)):raise ValueError('positive int32 screen dimensions required')
        self.width=width;self.height=height;self.g=source or merged_source()[0];self.surface=surface_load();self.layout=layout_load();self.composition=composition_load();self.trees={};self.refs={};self.states={};self.safe=[0.,0.];self.bindings={key(i['identity']):key(i['ui_camera']) if i.get('ui_camera') else None for i in self.layout['instances'] if i['class_name']=='UIObjectAnchors'};self.clamp=constants()['clamp'];self.log=[];self.mounts={};self.view=View(self);self.main=key(main_camera) if main_camera else None
        if self.main:self.camera(self.main)
    @property
    def clamp(self):return self._clamp
    @clamp.setter
    def clamp(self,value):
        value=f32(value)
        if not math.isfinite(value):raise ValueError('finite static clamp required')
        self._clamp=value
    def camera(self,k):
        c=next((c for c in self.composition['cameras'] if key(c['identity'])==k),None)
        if c is None:raise ValueError('camera outside source bank')
        return c
    def poses(self):
        frame=self
        class Mounted(Poses):
            def get(self,t,seen=None):
                if t in frame.mounts:
                    go=self.g.target(t,'.m_GameObject');active=self.g.tree(go).get('m_IsActive')
                    tree=self.g.tree(t);local=trs(dict(local_pos=[tree['m_LocalPosition'][c] for c in 'xyz'],rotation=[tree['m_LocalRotation'][c] for c in 'xyzw'],scale=[tree['m_LocalScale'][c] for c in 'xyz']))
                    return dict(matrix=multiply(frame.mounts[t],local) if local else None,activity=bool(active) if active in (0,1) else None,status='explicit_mounted_root')
                return super().get(t,seen)
        return Mounted(self.view)
    def matrix(self,tr):
        p=self.poses().get(tr)
        if p['matrix'] is None:raise ValueError('current modeled parent/world matrix unavailable')
        return p['matrix']
    def mount(self,gameobject,world):
        go=key(gameobject);tr=self.g.go_transform.get(go)
        if tr is None:raise ValueError('mount root transform missing')
        inverse(world);tree=self.view.tree(tr);local=trs(dict(local_pos=[tree['m_LocalPosition'][c] for c in 'xyz'],rotation=[tree['m_LocalRotation'][c] for c in 'xyzw'],scale=[tree['m_LocalScale'][c] for c in 'xyz']));self.mounts[tr]=multiply(world,inverse(local));self.log.append(dict(kind='explicit_mount',gameobject=gameobject,world=world))
    def resize_camera(self,camera):
        from tools.verify.camera_scaler_contracts import scaled_ortho
        k=key(camera);c=self.camera(k)
        if not c['size_writers']:raise ValueError('source CameraScaler writer not joined')
        contract=json.loads((ROOT/'datas/camera_scaler_contract.json').read_bytes());h=scaled_ortho(self.width,self.height,contract['factor'],contract['minimum']);pending={};self._set(k,'orthographic size',h,pending);self.trees.update(pending);self.log.append(dict(kind='explicit_CameraScaler_contract_application',camera=camera,half_height=h))
    def cam_values(self,k):
        self.camera(k);t=self.view.tree(k);r=t['m_NormalizedViewPortRect'];return t['orthographic size'],f32((self.width*r['width'])/(self.height*r['height']))
    def instance(self,component,cls):
        i=next((i for i in self.layout['instances'] if key(i['identity'])==key(component) and i['class_name']==cls),None)
        if i is None:raise ValueError('typed component outside layout bank')
        return i
    def _set(self,owner,path,value,trees):
        tree=trees.setdefault(owner,copy.deepcopy(self.view.tree(owner)));parts=path.split('.');target=tree
        for p in parts[:-1]:target=target[p]
        old=target[parts[-1]]
        if isinstance(old,bool):
            if value not in (0,1):raise ValueError('boolean write must be0/1')
            value=bool(value)
        elif isinstance(old,int):
            if not math.isfinite(value) or not float(value).is_integer():raise ValueError('integer write must be integral')
            value=int(value)
        elif isinstance(old,float):
            if not math.isfinite(value):raise ValueError('finite scalar required')
            value=f32(value)
        target[parts[-1]]=value
    def anchor(self,component,safe_rect,start=False):
        i=self.instance(component,'UIObjectAnchors');k=key(component);tr=key(i['transform']);parent=self.view.target(tr,'.m_Father');pm=self.mounts[tr] if tr in self.mounts else self.matrix(parent) if parent else list(IDENTITY);tree=self.view.tree(tr);local=[tree['m_LocalPosition'][c] for c in 'xyz'];bound=self.bindings[k];props=self.view.tree(k)
        if start and bound is None:
            if self.main is None:raise ValueError('Start fallback requires explicitly selected modeled Camera.main')
            bound=self.main
        if bound is None:raise ValueError('direct ObjectAnchor requires prior binding; it does not execute Start')
        h,aspect=self.cam_values(bound);mh=self.cam_values(self.main)[0] if self.main else None
        case=dict(anchor=props['anchor'],local=local,parent=pm,ui_half_height=h,ui_aspect=aspect,fixed=bool(props['isFixedScreenMaxSize']),main_half_height=mh,screen_height=self.height,safe_rect=safe_rect,state=self.states.get(k),cached_safe=self.safe,clamp_value=self.clamp)
        play=bool(props['playOnStart']) if start else True
        n=execute(('UIObjectAnchors','Start'),constants(),**case,play_on_start=play,ui_camera_null=self.bindings[k] is None) if start else native_probe(case)
        if play:
            m=model_probe(case)
            for f in ('state','local','world','writes'):assert m[f]==n[f],f
            assert m['safe']['bounds']==n['safe'];pending={};self._set(tr,'m_LocalPosition.x',n['local'][0],pending);self._set(tr,'m_LocalPosition.y',n['local'][1],pending);self._set(tr,'m_LocalPosition.z',n['local'][2],pending);self.trees.update(pending);self.states[k]=copy.deepcopy(n['state']);self.safe=list(n['safe'])
        self.bindings[k]=bound;self.refs[k,'.uiCamera']=bound;self.log.append(dict(kind='native_Start' if start else 'native_ObjectAnchor',component=component,explicit_camera_binding=identity(bound),applied_position=play,case=case,native=n));return n
    def scaler(self,component):
        if self.main is None:raise ValueError('explicit modeled Camera.main required')
        i=self.instance(component,'ObjectScaler');rk=key(i['renderer']);tree=self.view.tree(rk);size=[tree['m_Size'][c] for c in 'xy'];h=self.cam_values(self.main)[0];t=self.view.tree(key(component));m=scaler_step(size,h,bool(t['isFullScreen']),bool(t['clampSize']),dict(constants(),clamp=self.clamp));n=execute(('ObjectScaler','Start'),constants(),[0,0,0],list(IDENTITY),main_half_height=h,size=size,full=bool(t['isFullScreen']),clamp=bool(t['clampSize']),clamp_value=self.clamp);assert m==n['size'];pending={}
        for c,v in zip('xy',m):self._set(rk,'m_Size.'+c,v,pending)
        self.trees.update(pending);self.log.append(dict(kind='native_ObjectScaler_Start',component=component,before=size,after=m,native=n));return m
    def clip(self,animator,clip,time,pointer_fields=None):
        sampled=clip_probe(self.surface,animator,clip,time);pending={};refs={};writes=[]
        def pointers(tree,path=''):
            if isinstance(tree,dict):
                if 'm_FileID' in tree and 'm_PathID' in tree:yield path;return
                for k,v in tree.items():yield from pointers(v,path+'.'+k if path else k)
        for entry in sampled['bindings']:
            b=entry['binding'];raw=b['binding'];values=[v['value'] for v in entry['channels']]
            if b['status']!='unique_target' or len(b['targets'])!=1:raise ValueError('unresolved/ambiguous clip target; transaction not applied')
            owner=key(b['targets'][0])
            if raw.get('isPPtrCurve'):
                motion=next(m for m in self.surface['sections']['motion'] if key(m['identity'])==key(clip));v=values[0] if len(values)==1 else None
                if v is None or not math.isfinite(v) or not float(v).is_integer() or not 0<=int(v)<len(motion['pptr_targets']):raise ValueError('unknown/invalid pointer mapping index, not a null write')
                rawptr=motion['pptr_curve_mapping'][int(v)]
                if entry['pptr_target'] is None and rawptr.get('m_PathID',0)!=0:raise ValueError('unresolved nonnull pointer, not a null write')
                fields=[p for p in pointers(self.g.tree(owner)) if zlib.crc32(p.encode())==raw['attribute']]
                explicit=(pointer_fields or {}).get(b['binding_index'])
                if explicit is not None:
                    if raw['attribute']!=0 or explicit not in list(pointers(self.g.tree(owner))):raise ValueError('invalid explicit custom pointer binding')
                    fields=[explicit]
                if len(fields)!=1 or '.' in fields[0]:raise ValueError('pointer field hash not uniquely supported; encoded custom bindings require explicit field policy')
                target=entry['pptr_target'];tk=key(target) if target else None
                if tk is not None and tk not in self.g.rows:raise ValueError('pointer target body outside recovered bank')
                if fields[0] not in ('m_Sprite','m_Mesh','uiCamera'):raise ValueError('pointer writer outside bounded sprite/mesh/camera fields')
                expected={'m_Sprite':'Sprite','m_Mesh':'Mesh','m_Shader':'Shader','m_sharedMaterial':'Material','uiCamera':'Camera'}.get(fields[0])
                if tk and expected and self.g.rows[tk]['type']!=expected:raise ValueError('runtime reference type mismatch')
                refs[owner,'.'+fields[0]]=tk;writes.append(dict(target=identity(owner),field=fields[0],runtime_reference=target,resolution='explicit_custom_binding_field_policy' if explicit is not None else 'unique_source_field_crc'));continue
            if any(v is None or not math.isfinite(v) for v in values):raise ValueError('unknown/nonfinite clip channel; transaction not applied')
            if raw['typeID']==4:
                field={1:('m_LocalPosition','xyz'),2:('m_LocalRotation','xyzw'),3:('m_LocalScale','xyz')}.get(raw['attribute'])
                if field is None or len(values)!=len(field[1]):raise ValueError('transform channel outside bounded writer')
                for axis,v in zip(field[1],values):self._set(owner,field[0]+'.'+axis,v,pending)
                writes.append(dict(target=identity(owner),field=field[0],values=values))
            else:
                candidates=[p for p in b['property_candidates'] if key(p['target'])==owner]
                if len(candidates)!=1 or len(values)!=1:raise ValueError('scalar property hash not unique/supported')
                path=candidates[0]['field'];self._set(owner,path,values[0],pending);writes.append(dict(target=identity(owner),field=path,value=values[0]))
        # Validate affected local TRS before commit. This is TOOL atomicity, not Unity exception semantics.
        from tools.verify.ui_composition import trs
        for k,t in pending.items():
            if self.g.rows[k]['type'] in ('Transform','RectTransform'):
                node=dict(local_pos=[t['m_LocalPosition'][c] for c in 'xyz'],rotation=[t['m_LocalRotation'][c] for c in 'xyzw'],scale=[t['m_LocalScale'][c] for c in 'xyz'])
                if trs(node) is None:raise ValueError('invalid resulting local TRS; transaction not applied')
        self.trees.update(pending);self.refs.update(refs)
        for (owner,field),target in refs.items():
            if field=='.uiCamera' and owner in self.bindings:self.bindings[owner]=target
        self.log.append(dict(kind='explicit_clip_write_transaction',sample=sampled,writes=writes));return writes
    def project(self,renderer,camera):
        rk=key(renderer);ck=key(camera);r=next(r for r in self.surface['sections']['renderers'] if key(r['identity'])==rk);tr=key(r['transform']);chain=set();cursor=tr
        while cursor and cursor not in chain:chain.add(cursor);cursor=self.view.target(cursor,'.m_Father')
        mounted=bool(chain&set(self.mounts))
        if not mounted and (not scene_file(rk[0]) or not scene_file(ck[0]) or rk[0]!=ck[0]):raise ValueError('template/cross-scene renderer requires explicit root mount')
        cam=copy.deepcopy(self.camera(ck));cg=key(cam['gameobject']);cam['serialized_world_matrix']=self.matrix(self.g.go_transform[cg]);ct=self.view.tree(ck);cam['properties']=ct;props=self.view.tree(rk);sprite=self.view.target(rk,'.m_Sprite');geometry=next((g for g in self.surface['sections']['geometry'] if sprite and key(g['identity'])==sprite),None);generated=sprite_geometry(dict(properties=props),geometry) if r['type']=='SpriteRenderer' and geometry else None;mesh=None
        if r['type']=='MeshRenderer':
            filters=[k for k in self.g.components[key(r['gameobject'])] if self.g.rows.get(k,{}).get('type')=='MeshFilter'];mesh=self.view.target(filters[0],'.m_Mesh') if len(filters)==1 else None;gg=next((g for g in self.surface['sections']['geometry'] if mesh and key(g['identity'])==mesh),None)
            if gg:generated=dict(status='decoded_current_static_mesh_position_model',vertices=gg['geometry']['m_Vertices'],triangles=[f for group in gg['geometry']['triangles'] for f in group])
        pose=self.poses().get(tr)
        from tools.verify.l3_composition_math import layer_gate
        result=dict(renderer=renderer,camera=camera,mounted=mounted,world_matrix=pose['matrix'],current_color=props.get('m_Color'),current_size=props.get('m_Size'),current_sprite=identity(sprite),current_mesh=identity(mesh),layer_gate=layer_gate(ct['m_CullingMask']['m_Bits'],self.view.tree(key(r['gameobject']))['m_Layer']),serialized_chain_activity=pose['activity'],renderer_enabled=props.get('m_Enabled'),geometry=generated,scope='Shared modeled state after explicitly ordered writes; NOT actual Unity scheduling/rendered visibility')
        result['projection']=project_geometry(generated['vertices'],generated['triangles'],pose['matrix'],cam,self.width,self.height,ct['orthographic size']) if generated and generated.get('vertices') is not None else dict(status='position_geometry_not_generated')
        return result

def scenarios():
    source=merged_source()[0];main=identity(('data.unity3d/level2',3976));f=Frame(1080,2400,main,source);f.resize_camera(main);alert=identity(('data.unity3d/level2',5105));before=f.project(alert,main);f.scaler(identity(('data.unity3d/level2',6686)));f.clip(identity(('data.unity3d/level2',4647)),identity(('data.unity3d/sharedassets2.assets',42)),.0625);after=f.project(alert,main);f.clip(identity(('data.unity3d/level2',4647)),identity(('data.unity3d/sharedassets2.assets',43)),.25);faded=f.project(alert,main)
    b=Frame(1080,2400,main,source);b.resize_camera(main);anchor=identity(('data.unity3d/level2',7048));renderer=identity(('data.unity3d/level2',5739));i=b.instance(anchor,'UIObjectAnchors');nodes,_=source.descendants(key(i['gameobject']));children=[n['transform'] for n in nodes if n['transform']!=key(i['transform'])];poses_before=[dict(transform=identity(t),matrix=b.matrix(t)) for t in children];before_b=b.project(renderer,main);b.anchor(anchor,[0.,96.,1080.,2208.],start=True);after_start=b.project(renderer,main);b.anchor(anchor,[0.,96.,1080.,2208.]);after_align=b.project(renderer,main);poses_after=[dict(transform=identity(t),matrix=b.matrix(t)) for t in children]
    childset={source.target(t,'.m_GameObject') for t in children};child_renderer=next(r for r in b.surface['sections']['renderers'] if r['type']=='SpriteRenderer' and r['gameobject'] and key(r['gameobject']) in childset and r['properties']['m_DrawMode']==0);child_before=Frame(1080,2400,main,source);child_before.resize_camera(main);child_projection_before=child_before.project(child_renderer['identity'],main);child_projection_after=b.project(child_renderer['identity'],main)
    paths=['datas/l3_layout.json.gz','datas/l3_visual_surface.json.gz','datas/l3_composition.json.gz','datas/camera_scaler_contract.json','tools/verify/l3_frame.py','tools/verify/l3_layout.py','tools/verify/l3_layout_math.py','tools/verify/l3_layout_emulator.py','tools/verify/l3_visual_surface.py','tools/verify/l3_composition_math.py']
    return dict(schema=1,provisional=True,scope='Explicit ordered source write application on shared modeled instances; no Unity scheduling/transition/blending or rendering. Private anchor and static safeArea caches persist within each Frame. Tool transactions are not engine exception semantics.',inputs={p:digest(ROOT/p) for p in paths},cases=dict(alert=dict(before=before,after=after,faded=faded,log=f.log),border_info=dict(before=before_b,after_start=after_start,after_align=after_align,descendants_before=poses_before,descendants_after=poses_after,child_projection_before=child_projection_before,child_projection_after=child_projection_after,log=b.log)))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=ROOT/'datas/l3_frame_cases.json.gz');a=p.parse_args();d=scenarios();blob=json.dumps(d,separators=(',',':')).encode();blob=gzip.compress(blob,mtime=0) if a.out.suffix=='.gz' else blob;assert len(blob)<5_000_000;a.out.write_bytes(blob);print(json.dumps({k:dict(steps=len(v['log'])) for k,v in d['cases'].items()},indent=2))
if __name__=='__main__':main()
