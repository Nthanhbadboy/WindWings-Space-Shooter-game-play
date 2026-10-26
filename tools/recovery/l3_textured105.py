"""Recover one actual APK atlas + decoded GPU-program analysis; pixels stay external."""
import argparse,gzip,hashlib,io,json,zipfile,re
from attrs import asdict
from pathlib import Path
from asset_pack_v2 import XAPK_SHA,extract_payload,serialized_files,sha
ROOT=Path(__file__).resolve().parents[2]
def recover(xapk,work):
    assert sha(xapk.read_bytes())==XAPK_SHA
    import UnityPy
    from UnityPy.export.ShaderConverter import ShaderProgram
    from UnityPy.helpers import CompressionHelper
    from UnityPy.streams import EndianBinaryReader
    inputs=extract_payload(xapk,work/'input');env=UnityPy.load(*(str(p) for p in sorted((work/'input').iterdir())))
    files=dict(serialized_files(env));f='data.unity3d/resources.assets';sf=files[f];sprite=sf.objects[2585].read();atlas=sprite.m_SpriteAtlas.deref_parse_as_object();matches=[v for k,v in atlas.m_RenderDataMap if k==sprite.m_RenderDataKey];assert len(matches)==1
    rd=matches[0];texture=rd.texture.deref();t=texture.read();im=t.image.convert('RGBA');external=work/'external';external.mkdir();im.save(external/'atlas.png');sprite.image.save(external/'sprite.png')
    samples=[]
    # Exact texel coordinates in bottom-left convention; no resampling or screenshot.
    for dx,dy in [(0,0),(128,61),(255,122),(64,30),(192,92),(1,61),(254,61)]:
        x=int(rd.textureRect.x)+dx;y=int(rd.textureRect.y)+dy;samples.append(dict(x=x,y=y,rgba8=list(im.getpixel((x,im.height-1-y)))))
    out=ROOT/'reverse-engineering/raw/l3-textured105';out.mkdir(parents=True,exist_ok=True)
    shader=files['data.unity3d/Resources/unity_builtin_extra'].objects[10753];s=shader.read();programs=[];segments=[]
    for i,platform in enumerate(s.platforms):
        def first(a):return a[i][0] if isinstance(a[i],list) else a[i]
        off,n,z=first(s.offsets),first(s.compressedLengths),first(s.decompressedLengths);b=CompressionHelper.decompress_lz4(bytes(s.compressedBlob)[off:off+n],z);segments.append(dict(platform=platform,sha256=sha(b),bytes=len(b),ascii_runs=[v.decode('ascii') for v in re.findall(rb'[\x09\x0a\x0d\x20-\x7e]{32,}',b)],ascii_locations=[dict(offset=m.start(),bytes=len(m.group()),sha256=sha(m.group())) for m in re.finditer(rb'[\x09\x0a\x0d\x20-\x7e]{32,}',b)]));p=ShaderProgram(EndianBinaryReader(b,endian='<'),shader.version)
        for j,sub in enumerate(p.m_SubPrograms):
            code=bytes(sub.m_ProgramCode)
            try:text=sub.Export();status='UnityPy_exported_analysis'
            except UnicodeDecodeError:
                start=code.find(b'#version');text=code[start:].decode('utf8',errors='replace') if start>=0 else '';status='binary_prefix_GLSL_suffix_NOT_validated'
            text=text.encode('utf8',errors='replace').decode('utf8')
            programs.append(dict(platform=platform,index=j,program_type=int(sub.m_ProgramType),version=sub.m_Version,keywords=sub.m_Keywords,code_sha256=sha(code),code_bytes=len(code),prefix_hex=code[:48].hex(),status=status,text=text,sha256=sha(text.encode())))
    analysis=dict(parser_scope='UnityPy ShaderProgram entries diagnostic only: new-format keyword/program parser not validated. Execution model uses exact ASCII runs from LZ4-decoded pinned segments, not malformed entries.',shader_raw_sha256=sha(shader.get_raw_data()),compressed_blob_sha256=sha(bytes(s.compressedBlob)),programs=programs,segments=segments)
    objects=[dict(serialized_file=f,path_id=pid,type=sf.objects[pid].type.name,class_id=int(sf.objects[pid].type),raw_object_sha256=sha(sf.objects[pid].get_raw_data()),tree=sf.objects[pid].read_typetree()) for pid in [493280,492598]]
    (out/'objects.json').write_text(json.dumps(objects,indent=2)+'\n')
    (out/'gpu-analysis.json').write_text(json.dumps(analysis,indent=2)+'\n')
    lib=metadata=None
    with zipfile.ZipFile(xapk) as outer:
        for n in outer.namelist():
            if not n.endswith('.apk'):continue
            with zipfile.ZipFile(io.BytesIO(outer.read(n))) as apk:
                for p in apk.namelist():
                    if p=='lib/arm64-v8a/libil2cpp.so':lib=apk.read(p)
                    if p.endswith('/global-metadata.dat'):metadata=apk.read(p)
    assert sha(lib)=='9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99'
    assert sha(metadata)=='449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69'
    needles=[b'UnityEngine.SpriteRenderer::set_sprite',b'customType',b'm_Sprite'];search=[]
    for name,blob in [('libil2cpp.so',lib),('global-metadata.dat',metadata)]:
        for needle in needles:
            positions=[];pos=0
            while True:
                pos=blob.find(needle,pos)
                if pos<0:break
                positions.append(pos);pos+=len(needle)
            search.append(dict(input=name,needle=needle.decode(),file_offsets=positions))
    def ident(o):return dict(serialized_file=next(n for n,v in files.items() if v is o.assets_file),path_id=o.path_id)
    from combat_coroutine_cells import extract
    literal=extract(lib,[(0x756dd8,4)])['cells'][0]
    wrapper=extract(lib,[(0x278ad60,0x44)])['cells'][0]
    data=dict(objects_sha256=sha((out/'objects.json').read_bytes()),sprite_setter_wrapper=wrapper,align_literal=literal,provisional=True,xapk_sha256=XAPK_SHA,tool_sha256=sha(Path(__file__).read_bytes()),toolchain=dict(UnityPy=UnityPy.__version__),inputs=inputs,sprite=ident(sf.objects[2585]),sprite_raw_sha256=sha(sf.objects[2585].get_raw_data()),atlas=ident(sprite.m_SpriteAtlas.deref()),texture=ident(texture),texture_raw_sha256=sha(texture.get_raw_data()),width=im.width,height=im.height,rgba_sha256=sha(im.tobytes()),png_sha256=sha((external/'atlas.png').read_bytes()),crop_png_sha256=sha((external/'sprite.png').read_bytes()),texture_format=int(t.m_TextureFormat),texture_settings=asdict(t.m_TextureSettings),render_data=dict(texture_rect=asdict(rd.textureRect),uv_transform=asdict(rd.uvTransform),settings_raw=rd.settingsRaw),samples=samples,gpu_analysis_sha256=sha((out/'gpu-analysis.json').read_bytes()),lib_sha256=sha(lib),metadata_sha256=sha(metadata),native_search=search,binding_status='UNPROVED: string occurrence is not a tag23 registration table; explicit policy still required',pixels='external Actions artifact only; never committed')
    (out/'texture.json').write_text(json.dumps(data,indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args()
    try:recover(a.xapk,a.work)
    except Exception:
        import traceback
        print('::error::'+traceback.format_exc().replace('%','%25').replace('\n','%0A'),flush=True)
        raise
