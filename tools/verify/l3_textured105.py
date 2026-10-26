"""Bounded simple-sprite UV + decoded GLES arithmetic. NOT a rasterizer/render.
Mip-zero texel-center probes use actual decoded APK RGBA, no GPU precision/sRGB claim.
"""
import gzip,json,math,hashlib
from tools.verify.l3_chain_graph import ROOT,key,identity
from tools.verify.l3_visual_surface import load,digest
from tools.verify.l3_composition import merged_source
from tools.verify.l3_composition_math import sprite_geometry
from tools.verify.l3_layout_math import f32
from tools.verify.ui_composition import sequential_sum
from tools.verify.l3_pause105 import scenario
RAW=ROOT/'reverse-engineering/raw/l3-textured105'
F='data.unity3d/resources.assets'
def finite(v,n):
    if len(v)!=n or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in v):raise ValueError('finite vector required')
    return list(v)
def uv_geometry(renderer,geometry,uv_transform,width,height,settings_raw):
    if renderer['properties'].get('m_DrawMode')!=0:raise ValueError('only decoded simple sprite topology; no sliced/tiled UV fabrication')
    if settings_raw!=1:raise ValueError('only exact source settingsRaw1/unrotated affine UV case; other packing flags rejected')
    if any(isinstance(n,bool) or not isinstance(n,int) or n<=0 for n in (width,height)):raise ValueError('positive integer texture dimensions required')
    tr=finite([uv_transform[c] for c in 'xyzw'],4)
    if tr[0]<=0 or tr[2]<=0:raise ValueError('positive atlas affine scales required')
    out=sprite_geometry(renderer,geometry);source=geometry['geometry']['m_Vertices'];out['uvs']=[[(v[0]*tr[0]+tr[1])/width,(v[1]*tr[2]+tr[3])/height] for v in source]
    if len(out['uvs'])!=len(out['vertices']) or any(not all(math.isfinite(n) for n in uv) for uv in out['uvs']):raise ValueError('invalid mapped UVs')
    out['scope']='Decoded simple positions plus source-key atlas affine UV model; no live atlas override or engine geometry readback'
    out['uv_scope']='Source SpriteAtlas render-key uvTransform affine applied to ORIGINAL decoded local vertices; position flips do NOT flip UV indices. Zero-filled MeshHelper UV0 is retained as source evidence, not used as resolved atlas UV.'
    return out

def weights(p,vertices):
    x,y=finite(p,2);a,b,c=[finite(v,2) for v in vertices];d=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
    if abs(d)<1e-15:raise ValueError('degenerate UV triangle')
    u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/d;v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/d;return [u,v,1-u-v]
def texel_center_probe(mesh,texture,sample):
    w,h=texture['width'],texture['height'];x,y=sample['x'],sample['y']
    if any(type(n) is not int for n in (x,y)) or not 0<=x<w or not 0<=y<h:raise ValueError('in-bounds integer source texel required')
    if sample not in texture['samples']:raise ValueError('no evidence for this texel; do not synthesize missing pixels')
    uv=[(x+.5)/w,(y+.5)/h]
    for tri in mesh['triangles']:
        bary=weights(uv,[mesh['uvs'][i] for i in tri])
        if min(bary)>=-1e-12:
            local=[sequential_sum(bary[j]*mesh['vertices'][tri[j]][i] for j in range(3)) for i in range(3)]
            return dict(uv=uv,triangle=tri,barycentric=bary,local=local,rgba8=sample['rgba8'],sample_policy='Explicit mip0 texel center, decoded RGBA bytes/255. Not GPU bilinear/mip/sRGB readback')
    raise ValueError('texel center outside source triangles')

def shade(rgba8,vertex_color,material_color,renderer_color,external_alpha=None,enable_external_alpha=0.):
    if len(rgba8)!=4 or any(type(v) is not int or not 0<=v<=255 for v in rgba8):raise ValueError('RGBA8 source texel required')
    colors=[finite(c,4) for c in [vertex_color,material_color,renderer_color]]
    if any(not 0<=v<=1 for c in colors for v in c):raise ValueError('this bounded UNORM tint model requires0..1')
    if not math.isfinite(enable_external_alpha) or not 0<=enable_external_alpha<=1:raise ValueError('external alpha enable requires0..1')
    t=[v/255 for v in rgba8]
    if external_alpha is not None:
        if not math.isfinite(external_alpha) or not 0<=external_alpha<=1:raise ValueError('external alpha requires0..1')
        t[3]=enable_external_alpha*(external_alpha-t[3])+t[3]
    elif enable_external_alpha:raise ValueError('external alpha sample required')
    # Exact source operation order, explicit binary64 CPU arithmetic, not GLES mediump emulation.
    varying=[(colors[0][i]*colors[1][i])*colors[2][i] for i in range(4)];c=[t[i]*varying[i] for i in range(4)];return dict(varying_color=varying,fragment=[c[i]*c[3] for i in range(3)]+[c[3]])
def blend(src,dst):
    src=finite(src,4);dst=finite(dst,4)
    if any(not 0<=v<=1 for v in src+dst):raise ValueError('bounded normalized blend values required')
    return [src[i]+dst[i]*(1-src[3]) for i in range(4)]

def shader_contract(surface,analysis,shader_identity):
    shader=next(s for s in surface['sections']['shaders'] if key(s['identity'])==key(shader_identity));assert shader['name']=='Sprites/Default' and shader['raw_object_sha256']==analysis['shader_raw_sha256'];state=shader['subshaders'][0]['passes'][0]['state'];b=state['rtBlend0']
    assert [b[x]['val'] for x in ['srcBlend','destBlend','srcBlendAlpha','destBlendAlpha','blendOp','blendOpAlpha']]==[1.,10.,1.,10.,0.,0.]
    assert state['zWrite']['val']==0 and state['culling']['val']==0
    variants=[]
    for segment in analysis['segments']:
        for i,text in enumerate(segment['ascii_runs']):
            loc=segment['ascii_locations'][i];assert len(text.encode())==loc['bytes'] and hashlib.sha256(text.encode()).hexdigest()==loc['sha256']
            assert '#ifdef VERTEX' in text and '#ifdef FRAGMENT' in text
            assert 'u_xlat0 = in_COLOR0 * _Color;' in text and 'u_xlat0 = u_xlat0 * _RendererColor;' in text
            assert 'vs_TEXCOORD0.xy = in_TEXCOORD0.xy;' in text
            assert 'SV_Target0.xyz = u_xlat16_0.www * u_xlat16_0.xyz;' in text
            variants.append(dict(platform=segment['platform'],source_offset=loc['offset'],source_sha256=loc['sha256'],pixel_snap='roundEven(' in text,external_alpha='_EnableExternalAlpha' in text))
    return dict(shader=shader['identity'],shader_raw_sha256=shader['raw_object_sha256'],variants=variants,blend='One, OneMinusSrcAlpha / Add (same alpha factors)',z_write=False,cull='Off',scope='Exact byte-located GLSL arithmetic evidence, no compile/link/GPU execution. PixelSnap variants recovered but not executed. Explicit shader inputs are not observed renderer uniform uploads.')

def build():
    surface=load();s=surface['sections'];g=merged_source()[0];t=json.loads((RAW/'texture.json').read_bytes());analysis=json.loads((RAW/'gpu-analysis.json').read_bytes());assert digest(RAW/'gpu-analysis.json')==t['gpu_analysis_sha256'];assert digest(RAW/'objects.json')==t['objects_sha256']
    renderer=next(r for r in s['renderers'] if key(r['identity'])==(F,563997));geometry=next(r for r in s['geometry'] if key(r['identity'])==(F,2585));sprite=g.tree((F,2585));atlas=g.tree((F,580546));matches=[v for k,v in atlas['m_RenderDataMap'] if k==sprite['m_RenderDataKey']];assert len(matches)==1;rd=matches[0];assert rd['uvTransform']==t['render_data']['uv_transform'];assert g.target((F,580546),'.m_RenderDataMap['+str(next(i for i,(k,v) in enumerate(atlas['m_RenderDataMap']) if k==sprite['m_RenderDataKey']))+'][1].texture')==key(t['texture'])
    assert len(renderer['materials'])==1;material=next(m for m in s['materials'] if key(m['identity'])==key(renderer['materials'][0]));tints=dict(material['properties']['m_SavedProperties']['m_Colors']);tint=[tints['_Color'][c] for c in 'rgba']
    mesh=uv_geometry(renderer,geometry,rd['uvTransform'],t['width'],t['height'],rd['settingsRaw']);samples=[]
    for sample in t['samples']:
        probe=texel_center_probe(mesh,t,sample);out=shade(probe['rgba8'],[1,1,1,1],tint,[renderer['properties']['m_Color'][c] for c in 'rgba']);samples.append(dict(source=sample,probe=probe,shader=out,over_half_gray=blend(out['fragment'],[.5,.5,.5,1])))
    import capstone
    wrapper=t['sprite_setter_wrapper'];md=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);instructions=[dict(pc=hex(i.address),mnemonic=i.mnemonic,operands=i.op_str) for i in md.disasm(bytes.fromhex(wrapper['hex']),int(wrapper['va'],16))]
    native=json.load(gzip.open(ROOT/'reverse-engineering/raw/l3-ui-native/method-bytes.json.gz'));refresh=next(m for m in native['methods'] if m['cls']=='Board_Pause' and m['method']=='Refresh');start=int(refresh['va'],16);lo,hi=0x12c9c50,0x12c9cbc;guard=[dict(pc=hex(i.address),mnemonic=i.mnemonic,operands=i.op_str) for i in md.disasm(bytes.fromhex(refresh['hex'])[lo-start:hi-start],lo)]
    paths=['tools/verify/l3_textured105.py','tools/verify/l3_pause105.py','tools/verify/l3_frame.py','tools/verify/l3_layout_emulator.py','tools/recovery/l3_textured105.py','datas/l3_scene_chains.json.gz','datas/l3_visual_surface.json.gz','datas/l3_layout.json.gz','reverse-engineering/raw/l3-chain/index.json','reverse-engineering/raw/l3-ui-native/method-bytes.json.gz','reverse-engineering/raw/l3-ui-native/native/Board_Pause.json','reverse-engineering/raw/l3-ui-native/native/Board_Pause.asm.txt','reverse-engineering/raw/l3-textured105/texture.json','reverse-engineering/raw/l3-textured105/gpu-analysis.json','reverse-engineering/raw/l3-textured105/objects.json']
    return dict(provisional=True,provenance='arena/ef6b75ef',schema=1,inputs={p:digest(ROOT/p) for p in paths},xapk_sha256=t['xapk_sha256'],lib_sha256=t['lib_sha256'],metadata_sha256=t['metadata_sha256'],chain=scenario(),refresh_guard=dict(instructions=guard,scope='Bounded static guard evidence only: Refresh tests private align at+0x188, conditionally calls Align at0x12c9cb0, then stores1. Full Refresh/OnEnable not executed here; no cross-component scheduler proof.'),textured=dict(material=material,renderer=renderer['identity'],sprite=geometry['identity'],atlas=identity((F,580546)),texture=t['texture'],geometry=mesh,source_zero_uv0=geometry['geometry']['m_UV0'],texture_rgba_sha256=t['rgba_sha256'],crop_png_matches_pack=t['crop_png_sha256']==renderer['sprite_media'][0]['sha256'],shader_contract=shader_contract(surface,analysis,material['shader']),samples=samples,inputs_scope='Mip0 center probes; vertex input white, material tint white, renderer tint chosen explicitly from serialized m_Color; no observed GPU uniform binding or draw'),custom_binding=dict(status='UNPROVED',binding={'attribute':0,'customType':23,'typeID':212},animator=identity(('data.unity3d/level2',4695)),clip=identity((F,1609)),setter_instructions=instructions,search=t['native_search'],policy='Existing Frame rejects by default; per-binding explicit field policy remains mandatory. Setter icall bridge existence/string occurrences do NOT establish tag23 registration or field mapping.'),scope='Bounded native/model arithmetic, NOT Unity readback or render')
if __name__=='__main__':
    result=build();p=ROOT/'datas/l3_ef6b75ef105.json.gz';p.write_bytes(gzip.compress(json.dumps(result,separators=(',',':')).encode(),mtime=0));print(p)
