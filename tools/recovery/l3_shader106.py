"""Decode genuine APK atlas neighborhoods for declared shader106 probes. No full media in Git."""
import argparse,json,hashlib,sys
from pathlib import Path
from attrs import asdict
from asset_pack_v2 import XAPK_SHA,extract_payload,serialized_files,sha
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.verify.l3_shader106 import requests,canonical
from tools.verify.l3_shader106_math import footprint

def recover(xapk,work):
    import UnityPy
    import PIL
    assert sha(xapk.read_bytes())==XAPK_SHA
    inputs=extract_payload(xapk,work/'input');env=UnityPy.load(*(str(p) for p in sorted((work/'input').iterdir())));files=dict(serialized_files(env));f='data.unity3d/resources.assets';obj=files[f].objects[785];t=obj.read();image=t.image.convert('RGBA');old=json.loads((ROOT/'reverse-engineering/raw/l3-textured105/texture.json').read_bytes())
    assert sha(obj.get_raw_data())==old['texture_raw_sha256'];assert sha(image.tobytes())==old['rgba_sha256'];assert [image.width,image.height]==[old['width'],old['height']]
    plan=requests();coordinates=set()
    for q in plan['queries']+plan['sampler_only']:
        if q['uv'] is not None:
            for tap in footprint(q['uv'],[image.width,image.height])['taps']:coordinates.add(tuple(tap['xy']))
    pixels=[dict(x=x,y=y,rgba8=list(image.getpixel((x,image.height-1-y)))) for x,y in sorted(coordinates)]
    result=dict(provisional=True,provenance='arena/ef6b75ef',xapk_sha256=XAPK_SHA,inputs=inputs,texture=dict(serialized_file=f,path_id=785),texture_raw_sha256=old['texture_raw_sha256'],rgba_sha256=old['rgba_sha256'],width=image.width,height=image.height,texture_format=int(t.m_TextureFormat),texture_settings=asdict(t.m_TextureSettings),color_space_metadata=getattr(t,'m_ColorSpace',None),mip_count=getattr(t,'m_MipCount',None),toolchain=dict(UnityPy=UnityPy.__version__,Pillow=PIL.__version__),tool_sha256=sha(Path(__file__).read_bytes()),request_generator_sha256=sha(ROOT/'tools/verify/l3_shader106.py'),math_tool_sha256=sha(ROOT/'tools/verify/l3_shader106_math.py'),previous_artifact_sha256=sha(ROOT/'datas/l3_ef6b75ef105.json.gz'),requests_sha256=sha(canonical(plan)),requests=plan,pixels=pixels,pixel_convention='Decoded Pillow top-left -> bottom-left at read: getpixel((x,height-1-y)). Only requested original RGBA8 neighborhoods retained; no invented neighbors.')
    out=ROOT/'reverse-engineering/raw/l3-shader106';out.mkdir(parents=True,exist_ok=True);(out/'samples.json').write_text(json.dumps(result,indent=2)+'\n');print('unique source pixels',len(pixels),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args()
    try:recover(a.xapk,a.work)
    except Exception:
        import traceback
        print('::error::'+traceback.format_exc().replace('%','%25').replace('\n','%0A'),flush=True)
        raise
