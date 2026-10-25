"""Native-checked layout contracts and all APK anchor/scaler serialized bindings."""
import argparse,gzip,hashlib,json,math,re,struct
from collections import Counter
from functools import lru_cache
from pathlib import Path
from tools.verify.l3_chain_graph import ROOT,Graph,key,identity
from tools.verify.ui_composition import IDENTITY,trs,multiply
from tools.verify.l3_layout_math import anchor_step,scaler_step,point,f32,inverse_point
from tools.verify.l3_layout_emulator import execute
from tools.verify.camera_scaler_contracts import scaled_ortho
RAW=ROOT/'reverse-engineering/raw/l3-layout-native';OUT=ROOT/'datas/l3_layout.json.gz'

@lru_cache(maxsize=1)
def constants():
    c=json.loads((RAW/'anchor-cells.json').read_bytes());byva={int(v['va'],16):bytes.fromhex(v['hex']) for v in c['cells']}
    scalar=lambda va:struct.unpack('<f',byva[va])[0]
    base=dict(min_aspect=scalar(0x756ebc),half_h=scalar(0x756fb8),half_w=scalar(0x756f00),negative_half_h=scalar(0x756d60),clamp=0.)
    base['clamp']=execute(('ObjectScaler','cctor'),base,[0,0,0],IDENTITY)['clamp']
    base['roots']={str(a):execute(('UIObjectAnchors','GetRootAnchor'),base,[0,0,0],IDENTITY,anchor=a)['state']['root'] for a in range(10)}
    dump=gzip.decompress((ROOT/'reverse-engineering/il2cpp/dump.cs.gz').read_bytes()).decode();block=next(b for b in re.split(r'(?=// Namespace:)',dump) if re.search(r'// Namespace:\s*TuPro\n',b) and re.search(r'public enum Anchor\b',b))
    base['anchor_enum']={str(int(value)):name for name,value in re.findall(r'public const Anchor (\w+) = (\d+);',block)};assert set(base['anchor_enum'])=={str(i) for i in range(10)}
    base['jump_table_hex']=byva[0x77a39e].hex();base['jump_targets']=[hex(0x15b6a00+v*4) for v in byva[0x77a39e]]
    return base

def scenario_constants(viewport):
    c=dict(constants(),clamp=f32(viewport.get('clamp_value',constants()['clamp'])))
    if not math.isfinite(c['clamp']):raise ValueError('nonfinite static clamp not modeled')
    return c

def model_probe(case):
    c=scenario_constants(case);return anchor_step(case['anchor'],case['local'],case['parent'],case['ui_half_height'],case['ui_aspect'],case['fixed'],c,case.get('screen_height'),case.get('safe_rect'),case.get('main_half_height'),case.get('state'),case.get('cached_safe',(0.,0.)))
def native_probe(case):return execute(('UIObjectAnchors','ObjectAnchor'),constants(),**case)

def build():
    idx=json.loads((RAW/'index.json').read_bytes())
    for f in idx['files']:assert hashlib.sha256((RAW/f['path']).read_bytes()).hexdigest()==f['sha256']
    camera_contract=json.loads((ROOT/'datas/camera_scaler_contract.json').read_bytes())
    assert camera_contract['sources']['dump_sha256_decompressed']==hashlib.sha256(gzip.decompress((ROOT/'reverse-engineering/il2cpp/dump.cs.gz').read_bytes())).hexdigest()
    objects=json.load(gzip.open(RAW/'objects.json.gz'));g=Graph(objects['objects'],objects['links']);c=constants();memo={};pose_errors=[]
    def world(t,seen=None):
        if t in memo:return memo[t]
        seen=set() if seen is None else set(seen)
        if t in seen or t not in g.rows:return None
        seen.add(t);tt=g.tree(t)
        local=trs(dict(local_pos=[tt.get('m_LocalPosition',{}).get(k) for k in 'xyz'],rotation=[tt.get('m_LocalRotation',{}).get(k) for k in 'xyzw'],scale=[tt.get('m_LocalScale',{}).get(k) for k in 'xyz']))
        parent=g.target(t,'.m_Father');pm=world(parent,seen) if parent else list(IDENTITY)
        matrix=multiply(pm,local) if pm is not None and local is not None else None;memo[t]=matrix;return matrix
    drivers=json.load(gzip.open(ROOT/'datas/l3_ui_drivers.json.gz'));instances=[];camera_bank=[]
    start=next(m for m in drivers['methods'] if (m['namespace'],m['cls'],m['method'])==('TuPro','UIObjectAnchors','Start'));start_call,=[a for a in start['appearance_calls'] if any(d['method']=='ObjectAnchor' and d['class']=='UIObjectAnchors' for d in a['declarations'])];assert any(b.get('symbolic_operand',{}).get('offset')==0x4c for b in start['cfg']['branches'] if b.get('symbolic_operand'))
    start_contract=dict(method_rva=start['rva'],object_anchor_callsite=hex(start_call['pc']),guard_field_offset='0x4c',guard='playOnStart != 0',camera_binding='Start assigns Camera.main only if uiCamera fails Unity op_Implicit; direct ObjectAnchor does not run Start for you',scope='Class-body candidate for every exact typed instance; Unity scheduling/live flags NOT observed')
    catalog=json.load(gzip.open(ROOT/'reverse-engineering/raw/asset-pack-v2/catalog.json.gz'));assert catalog['xapk_sha256']==idx['xapk_sha256'];media={key(r):r for r in catalog['objects']}
    for row in objects['objects']:
        k=key(row);t=g.tree(k)
        if row['type']=='Camera':
            go=g.target(k,'.m_GameObject');go_tree=g.tree(go) if go in g.rows else {};tr=g.go_transform.get(go)
            camera_bank.append(dict(size_writers=[dict(component=sc['identity'],serialized_enabled=sc['serialized_component_enabled']) for sc in camera_contract['components'] if any(key(p)==k for p in sc['native_write_order'])],identity=identity(k),gameobject=identity(go),properties=t,gameobject_properties=go_tree,serialized_world_matrix=world(tr) if tr else None,main_tag_candidate=go_tree.get('m_Tag')==5))
        if row.get('class_name') not in ('UIObjectAnchors','ObjectScaler'):continue
        go=g.target(k,'.m_GameObject');tr=g.go_transform.get(go);tt=g.tree(tr) if tr else {};parent=g.target(tr,'.m_Father') if tr else None;wm=world(tr) if tr else None;pm=world(parent) if parent else list(IDENTITY)
        if wm is None:pose_errors.append(identity(k))
        local=[tt.get('m_LocalPosition',{}).get(v) for v in 'xyz']
        rec=dict(identity=identity(k),class_name=row['class_name'],namespace=row.get('namespace',''),raw_object_sha256=row['raw_object_sha256'],gameobject=identity(go),gameobject_properties=g.tree(go) if go in g.rows else {},components=[dict(field=loc,identity=identity(target),type=typ,snapshot_in_layout_context=target in g.rows) for loc,target,typ in g.refs.get(go,[]) if loc.startswith('.m_Component[')],transform=identity(tr),properties=t,serialized_active=g.tree(go).get('m_IsActive') if go in g.rows else None,serialized_local=local,serialized_world=point(wm,[0,0,0]) if wm else None,parent_matrix=pm,world_matrix=wm,native_callers=[dict(owner=e['owner'],method=e['method'],callsite=e['callsite']) for e in drivers['effects'] if e['receiver'] and key(e['receiver'])==k and any(d['method']=='ObjectAnchor' for d in e['declarations'])])
        try:
            if pm is None or wm is None:raise ValueError('parent/pose not available')
            inverse_point(pm,rec['serialized_world']);rec['affine_bridge_status']='invertible_model'
        except ValueError as e:rec['affine_bridge_status']='unmodeled';rec['affine_bridge_error']=str(e)
        if row['class_name']=='UIObjectAnchors':
            camera=g.target(k,'.uiCamera');rec.update(ui_camera=identity(camera),camera_binding='explicit_serialized_camera' if camera else 'runtime_Camera.main_fallback_NOT_selected',anchor=t['anchor'],anchor_name=c['anchor_enum'].get(str(t['anchor'])),play_on_start=t['playOnStart'],fixed=t['isFixedScreenMaxSize'])
        else:
            renderer=g.target(k,'.objectScale');sprite=g.target(renderer,'.m_Sprite') if renderer else None;match=media.get(sprite,{})
            rec.update(renderer=identity(renderer),renderer_properties=g.tree(renderer) if renderer in g.rows else None,sprite=identity(sprite),sprite_media=match.get('outputs',[]) if match.get('type')=='Sprite' else [],materials=[dict(field=loc,identity=identity(target)) for loc,target,typ in g.refs.get(renderer,[]) if loc.startswith('.m_Materials[')])
        instances.append(rec)
    samples=[]
    for fixed in (False,True):
        for a in range(10):
            case=dict(anchor=a,local=[1.,2.,3.],parent=list(IDENTITY),ui_half_height=14.,ui_aspect=.8,fixed=fixed,main_half_height=14.,screen_height=2400,safe_rect=[0.,96.,1920.,2208.])
            model=model_probe(case);native=native_probe(case)
            for name in ('state','world','local','writes'):assert model[name]==native[name],(a,fixed,name,model[name],native[name])
            assert model['safe']['bounds']==native['safe'];samples.append(dict(case=case,model=model,native=native))
    scalers=[]
    for full in (False,True):
        for clamp in (False,True):
            model=scaler_step([3.,4.],14.,full,clamp,c);native=execute(('ObjectScaler','Start'),c,[0,0,0],IDENTITY,main_half_height=14.,size=[3.,4.],full=full,clamp=clamp)
            assert model==native['size'];scalers.append(dict(full=full,clamp=clamp,model=model,native=native))
    counts=dict(raw_objects=len(objects['objects']),edge_status=dict(g.edge_status),unmodeled_affine_bridges=sum(i['affine_bridge_status']=='unmodeled' for i in instances),instances=len(instances),classes=dict(Counter(i['class_name'] for i in instances)),cameras=len(camera_bank),main_tag_candidates=sum(c['main_tag_candidate'] for c in camera_bank),camera_bindings=dict(Counter(i['camera_binding'] for i in instances if i['class_name']=='UIObjectAnchors')),anchor_native_checks=len(samples),scaler_native_checks=len(scalers),pose_errors=len(pose_errors),read_errors=len(objects['read_errors']),header_scan_errors=len(objects['header_errors']))
    inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [RAW/'index.json',ROOT/'reverse-engineering/raw/l3-ui-native/index.json',ROOT/'datas/l3_ui_drivers.json.gz',ROOT/'datas/camera_scaler_contract.json',ROOT/'reverse-engineering/il2cpp/dump.cs.gz',ROOT/'reverse-engineering/raw/asset-pack-v2/catalog.json.gz',Path(__file__),ROOT/'tools/verify/l3_layout_math.py',ROOT/'tools/verify/l3_layout_emulator.py',ROOT/'tools/verify/ui_composition.py',ROOT/'tools/verify/l3_chain_graph.py',ROOT/'tools/verify/camera_scaler_contracts.py']}
    profile=dict(width=1080,height=2400,safe_rect=[0.,96.,1080.,2208.])
    half=scaled_ortho(profile['width'],profile['height'],camera_contract['factor'],camera_contract['minimum'])
    top_instance=next(i for i in instances if key(i['identity'])==('data.unity3d/resources.assets',597593))
    probe=instance_probe(top_instance,dict(ui_half_height=half,ui_aspect=f32(profile['width']/profile['height']),main_half_height=half,screen_height=profile['height'],safe_rect=profile['safe_rect']))
    chain=dict(scope='Synthetic viewport, selected modeled main/UI camera same size and serialized Awake pose; NOT device/engine readback',profile=profile,predicted_half_height=half,probe=probe)
    return dict(anchor_start_contract=start_contract,camera_scaler_contract=dict(path='datas/camera_scaler_contract.json',formula=camera_contract['formula'],factor=camera_contract['factor'],minimum=camera_contract['minimum']),camera_chain_check=chain,schema=1,provisional=True,scope='All APK target-class headers/bindings and serialized parent poses. Explicit camera/safeArea inputs; native scalar/control-flow checked with stubbed engine/metadata and shared affine bridge, NOT Unity playback/render or actual device safeArea.',inputs=inputs,counts=counts,constants=c,source_scan=dict(headers=objects['scanned_headers'],header_errors=objects['header_errors'],read_errors=objects['read_errors']),instances=instances,cameras=camera_bank,pose_errors=pose_errors,anchor_checks=samples,scaler_checks=scalers)

def load():
    d=json.load(gzip.open(OUT));assert d['inputs']['datas/l3_ui_drivers.json.gz']==hashlib.sha256((ROOT/'datas/l3_ui_drivers.json.gz').read_bytes()).hexdigest();return d

def instance_probe(instance,viewport):
    if instance['class_name']=='ObjectScaler':
        p=instance['renderer_properties'];size=p['m_Size'];size=[size['x'],size['y']]
        c=scenario_constants(viewport)
        model=scaler_step(size,viewport['main_half_height'],bool(instance['properties']['isFullScreen']),bool(instance['properties']['clampSize']),c)
        native=execute(('ObjectScaler','Start'),constants(),instance['serialized_local'],instance['parent_matrix'],clamp_value=c['clamp'],main_half_height=viewport['main_half_height'],size=size,full=bool(instance['properties']['isFullScreen']),clamp=bool(instance['properties']['clampSize']))
        return dict(instance=instance['identity'],scope='Serialized pose/renderer + explicit modeled camera inputs, NOT current runtime viewport/readback',model=model,native=native)
    case=dict(anchor=instance['anchor'],fixed=instance['fixed'],local=instance['serialized_local'],parent=instance['parent_matrix'],**viewport)
    return dict(instance=instance['identity'],camera_binding=instance['camera_binding'],scope='Serialized pose + explicit modeled camera inputs, NOT runtime Camera.main selection or actual Awake cache',case=case,model=model_probe(case),native=native_probe(case))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',type=Path);p.add_argument('--instance',type=int);p.add_argument('--file',default='data.unity3d/resources.assets');p.add_argument('--viewport',type=Path);p.add_argument('--out',type=Path);a=p.parse_args()
    if a.instance is not None:
        if a.viewport is None:p.error('--instance requires --viewport with explicit numeric camera inputs')
        instance=next(i for i in load()['instances'] if key(i['identity'])==(a.file,a.instance));d=instance_probe(instance,json.loads(a.viewport.read_bytes()))
    elif a.case:
        case=json.loads(a.case.read_bytes());model=model_probe(case);native=native_probe(case);d=dict(provisional=True,model=model,native=native)
    else:d=build()
    b=json.dumps(d,ensure_ascii=True,separators=(',',':')).encode()
    if a.case or a.instance is not None:
        if a.out:a.out.write_bytes(b)
        else:print(b.decode())
    else:
        b=gzip.compress(b,mtime=0);assert len(b)<5_000_000;OUT.write_bytes(b);print(json.dumps(d['counts'],indent=2))
if __name__=='__main__':main()
