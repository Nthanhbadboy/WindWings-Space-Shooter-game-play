"""APK shader vertex/PixelSnap -> varying -> genuine mip0 bilinear samples.
No render, GPU readback, live atlas remap, transition or lifecycle claim.
"""
import gzip,json,hashlib,math
from tools.verify.l3_chain_graph import ROOT,key
from tools.verify.ui_composition import multiply,sequential_sum
from tools.verify.l3_composition import load as composition_load
from tools.verify.l3_composition_math import viewport_parameters
from tools.verify.l3_textured105 import weights,blend
from tools.verify.l3_shader106_math import vertex,interpolate,footprint,bilinear,fragment
RAW=ROOT/'reverse-engineering/raw/l3-shader106'
PREVIOUS=ROOT/'datas/l3_ef6b75ef105.json.gz'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def requests():
    d=json.load(gzip.open(PREVIOUS));t=d['textured'];mesh=t['geometry'];screen=[1080,2400]
    camera=next(c for c in composition_load()['cameras'] if key(c['identity'])==('data.unity3d/level2',3976));half=next(l['half_height'] for l in d['chain']['log'] if l['kind']=='explicit_CameraScaler_contract_application');params=viewport_parameters(camera,*screen,half_height=half)
    assert params['pixel_rect']==[0,0,*screen]
    w,h,n,f=params['half_width'],params['half_height'],params['near'],params['far'];projection=[1/w,0,0,0,0,1/h,0,0,0,0,2/(f-n),-(f+n)/(f-n),0,0,0,1];vp=multiply(projection,params['view']);world=d['chain']['after_clip']['563997']['world_matrix'];saved=t['material']['properties']['m_SavedProperties'];colors=dict(saved['m_Colors']);material=[colors['_Color'][c] for c in 'rgba'];renderer=[d['chain']['after_clip']['563997']['m_Color'][c] for c in 'rgba'];flip=[colors['_Flip'][c] for c in 'rg']
    vertices={str(snap):[vertex(p+[1.],uv,[1]*4,material,renderer,flip,world,vp,screen,snap) for p,uv in zip(mesh['vertices'],mesh['uvs'])] for snap in [False,True]};queries=[]
    for i,sample in enumerate(t['samples']):
        seed_uv=sample['probe']['uv'];tri=sample['probe']['triangle'];b=sample['probe']['barycentric'];vs=vertices['False'];seed=[sequential_sum(b[j]*vs[tri[j]]['window'][k] for j in range(3)) for k in range(2)];pixel=[math.floor(v)+.5 for v in seed]
        for snap in [False,True]:
            vs=vertices[str(snap)];row=dict(name=f'source_seed{i}_snap{int(snap)}',seed_uv=seed_uv,seed_window=seed,window=pixel,pixel_snap=snap,status='outside_source_triangles_after_variant',uv=None)
            for tri in mesh['triangles']:
                b=weights(pixel,[vs[j]['window'] for j in tri])
                if min(b)>=-1e-10:
                    result=interpolate([vs[j] for j in tri],b);row.update(status='bounded_point_in_source_triangle',triangle=tri,screen_barycentric=b,varying=result,uv=result['uv']);break
            queries.append(row)
    # Sampler-only boundary probes are explicit inputs, NOT scene coverage assertions.
    probes=[dict(name='four_equal_weights',uv=[1438/2048,190/1024]),dict(name='atlas_rect_left_neighbor',uv=[1310.25/2048,190.375/1024]),dict(name='fractional_inside',uv=[1374.125/2048,159.875/1024]),dict(name='texture_clamp_low',uv=[-.25,-.5]),dict(name='texture_clamp_high',uv=[1.25,1.5])]
    return dict(provenance='arena/ef6b75ef',profile=dict(screen=screen,camera=camera['identity'],half_height=half,object_to_world=world,matrix_vp=vp,vertex_color=[1]*4,material_color=material,renderer_color=renderer,flip=flip,scope='Explicit synthetic full-viewport conventional +Z orthographic MatrixVP and shader inputs; NOT engine uniform upload or frame readback'),vertices=vertices,queries=queries,sampler_only=probes)

def source_contract():
    analysis=json.loads((ROOT/'reverse-engineering/raw/l3-textured105/gpu-analysis.json').read_bytes());out=[]
    common=['u_xlat0.xy = in_POSITION0.xy * _Flip.xy;','u_xlat1 = u_xlat0.yyyy * hlslcc_mtx4x4unity_ObjectToWorld[1];','u_xlat0 = hlslcc_mtx4x4unity_ObjectToWorld[0] * u_xlat0.xxxx + u_xlat1;','u_xlat0 = hlslcc_mtx4x4unity_ObjectToWorld[2] * in_POSITION0.zzzz + u_xlat0;','u_xlat0 = u_xlat0 + hlslcc_mtx4x4unity_ObjectToWorld[3];','u_xlat1 = u_xlat0.yyyy * hlslcc_mtx4x4unity_MatrixVP[1];','u_xlat1 = hlslcc_mtx4x4unity_MatrixVP[0] * u_xlat0.xxxx + u_xlat1;','u_xlat1 = hlslcc_mtx4x4unity_MatrixVP[2] * u_xlat0.zzzz + u_xlat1;','u_xlat0 = in_COLOR0 * _Color;','u_xlat0 = u_xlat0 * _RendererColor;','vs_TEXCOORD0.xy = in_TEXCOORD0.xy;']
    for seg in analysis['segments']:
        for text,loc in zip(seg['ascii_runs'],seg['ascii_locations']):
            assert hashlib.sha256(text.encode()).hexdigest()==loc['sha256']
            for line in common:assert line in text,line
            snap='_ScreenParams' in text
            if snap:
                for line in ['u_xlat0.xy = u_xlat0.xy / u_xlat0.ww;','u_xlat1.xy = _ScreenParams.xy * vec2(0.5, 0.5);','u_xlat0.xy = u_xlat0.xy * u_xlat1.xy;','u_xlat0.xy = u_xlat0.xy / u_xlat1.xy;','gl_Position.xy = u_xlat0.ww * u_xlat0.xy;','gl_Position.zw = u_xlat0.zw;']:assert line in text,line
                assert 'unity_roundEven(u_xlat0.xy)' in text or 'roundEven(u_xlat0.xy)' in text
                if seg['platform']==5:assert 'float unity_roundEven(float x) { float y = floor(x + 0.5); return (y - x == 0.5) ? floor(0.5*y) * 2.0 : y; }' in text
            else:assert 'gl_Position = hlslcc_mtx4x4unity_MatrixVP[3] * u_xlat0.wwww + u_xlat1;' in text
            out.append(dict(platform=seg['platform'],offset=loc['offset'],sha256=loc['sha256'],pixel_snap=snap,external_alpha='_EnableExternalAlpha' in text))
    return dict(variants=out,scope='Statement-presence/hash pin audit of recovered source; procedural CPU reference, NOT arbitrary GLSL interpreter/compiler/GPU precision proof')

def build():
    raw=json.loads((RAW/'samples.json').read_bytes());plan=requests();assert canonical(plan)==canonical(raw['requests']);assert hashlib.sha256(canonical(plan)).hexdigest()==raw['requests_sha256']
    previous=json.loads((ROOT/'reverse-engineering/raw/l3-textured105/texture.json').read_bytes());assert raw['rgba_sha256']==previous['rgba_sha256'];assert raw['texture_raw_sha256']==previous['texture_raw_sha256'];settings=raw['texture_settings'];assert settings['m_FilterMode']==1 and settings['m_WrapU']==settings['m_WrapV']==1
    pixels={(p['x'],p['y']):p['rgba8'] for p in raw['pixels']};assert len(pixels)==len(raw['pixels']);rows=[]
    for q in plan['queries']:
        if q['uv'] is None:rows.append(dict(**q,filtered=None));continue
        filtered=bilinear(q['uv'],[raw['width'],raw['height']],pixels,settings['m_WrapU'],settings['m_WrapV']);output=fragment(filtered['rgba'],q['varying']['varying_color']);rows.append(dict(**q,filtered=filtered,fragment=output,over_half_gray=blend(output,[.5,.5,.5,1.])))
    extra=[dict(**q,filtered=bilinear(q['uv'],[raw['width'],raw['height']],pixels,settings['m_WrapU'],settings['m_WrapV'])) for q in plan['sampler_only']]
    paths=['tools/verify/l3_shader106.py','tools/verify/l3_shader106_math.py','tools/verify/l3_textured105.py','tools/verify/ui_composition.py','tools/recovery/l3_shader106.py','datas/l3_ef6b75ef105.json.gz','datas/l3_composition.json.gz','reverse-engineering/raw/l3-textured105/texture.json','reverse-engineering/raw/l3-textured105/gpu-analysis.json','reverse-engineering/raw/l3-shader106/samples.json']
    return dict(provisional=True,provenance='arena/ef6b75ef',schema=1,scope='Bounded source vertex/PixelSnap/varying/mip0 bilinear and premultiplied fragment arithmetic; NOT Unity readback or render',inputs={p:sha(ROOT/p) for p in paths},xapk_sha256=raw['xapk_sha256'],source=source_contract(),profile=plan['profile'],vertices=plan['vertices'],queries=rows,sampler_only=extra,pixels=raw['pixels'],texture=dict(identity=raw['texture'],width=raw['width'],height=raw['height'],settings=settings,rgba_sha256=raw['rgba_sha256'],color_space_metadata=raw['color_space_metadata'],mip_count=raw['mip_count'],scope='Actual APK decode and original metadata. Sampling executes raw-UNORM mip0 only; no inferred sRGB conversion/LOD/derivatives/anisotropy or external-alpha texture.'),counts=dict(vertices_per_variant=len(plan['vertices']['False']),vertex_variants=len(plan['vertices']),source_variants=len(source_contract()['variants']),fixed_pixel_queries=len(rows),inside_queries=len([r for r in rows if r['uv'] is not None]),sampler_only=len(extra),unique_decoded_pixels=len(pixels)),custom_binding_status='UNPROVED from105 unchanged; default rejection/explicit policy still required',uniform_scope='Source saved properties/explicit input policy, not actual runtime renderer-color/flip/keyword/MatrixVP bindings')
if __name__=='__main__':
    d=build();p=ROOT/'datas/l3_ef6b75ef106.json.gz';p.write_bytes(gzip.compress(json.dumps(d,separators=(',',':')).encode(),mtime=0));print(p)
