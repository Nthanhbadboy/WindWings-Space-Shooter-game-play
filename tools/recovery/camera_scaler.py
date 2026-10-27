"""Recover CameraScaler serialized camera refs and narrow native consumers."""
import argparse
import gzip
import io
import json
from pathlib import Path
import sys
import struct
import zipfile
from asset_pack_v2 import extract_payload,serialized_files,sha
from audio_native import INPUTS
ROOT=Path(__file__).resolve().parents[2]
NATIVE={'CameraScaler'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--xapk',type=Path,required=True);parser.add_argument('--work',type=Path,required=True);args=parser.parse_args()
    import UnityPy
    from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
    from UnityPy.classes.PPtr import PPtr
    work=args.work;inputs=extract_payload(args.xapk,work/'input');found={}
    with zipfile.ZipFile(args.xapk) as outer:
        for name in outer.namelist():
            if not name.endswith('.apk'):continue
            with zipfile.ZipFile(io.BytesIO(outer.read(name))) as part:
                for entry in INPUTS.keys() & set(part.namelist()):
                    blob=part.read(entry);assert sha(blob)==INPUTS[entry];found[entry]=sha(blob);(work/Path(entry).name).write_bytes(blob)
    assert found==INPUTS
    env=UnityPy.load(*(str(p) for p in sorted((work/'input').iterdir())))
    gen=TypeTreeGenerator('2022.3.62f3',generator='AssetStudio');gen.load_il2cpp((work/'libil2cpp.so').read_bytes(),(work/'global-metadata.dat').read_bytes());env.typetree_generator=gen
    files=serialized_files(env);names={id(sf):name for name,sf in files};scripts={};rows=[];errors=[];scanned=0
    def identity(obj):return dict(serialized_file=names[id(obj.assets_file)],type=obj.type.name,path_id=int(obj.path_id))
    for name,sf in files:
        for obj in sf.objects.values():
            if obj.type.name!='MonoBehaviour':continue
            scanned+=1
            try:
                head=obj.parse_monobehaviour_head();p=head.m_Script;k=(id(sf),p.m_FileID,p.m_PathID)
                if k not in scripts:
                    script=p.deref_parse_as_object();scripts[k]=(script.m_Namespace,script.m_ClassName)
                namespace,cls=scripts[k]
            except Exception as error:errors.append(dict(**identity(obj),error=repr(error)));continue
            if cls!='CameraScaler':continue
            tree=obj.read_typetree();refs=[]
            for pointer in tree['orthographicCameras']:
                if not pointer['m_PathID']:refs.append(dict(pointer=pointer,status='null'));continue
                camera=PPtr(m_FileID=pointer['m_FileID'],m_PathID=pointer['m_PathID'],assetsfile=obj.assets_file).deref()
                assert camera.type.name=='Camera'
                refs.append(dict(pointer=pointer,status='resolved',identity=identity(camera),raw_object_sha256=sha(camera.get_raw_data()),tree=camera.read_typetree()))
            go=head.m_GameObject.deref();assert go.type.name=='GameObject'
            rows.append(dict(**identity(obj),namespace=namespace,class_name=cls,raw_object_sha256=sha(obj.get_raw_data()),
                parsed_script_pointer=dict(m_FileID=p.m_FileID,m_PathID=p.m_PathID),tree=tree,cameras=refs,
                gameobject=dict(**identity(go),tree=go.read_typetree(),raw_object_sha256=sha(go.get_raw_data()))))
    out=ROOT/'reverse-engineering/raw/camera-scaler';out.mkdir(parents=True,exist_ok=True)
    projection=dict(status='PROVISIONAL_CAMERA_SCALER_SNAPSHOT_NOT_EXECUTED',inputs=inputs,binary_inputs_sha256=found,scanned_headers=scanned,header_errors=errors,
        files=[dict(serialized_file=name,externals=[dict(path=e.path,type=e.type) for e in sf.externals]) for name,sf in files],components=rows)
    blob=(json.dumps(projection,indent=2)+'\n').encode();(out/'components.json.gz').write_bytes(gzip.compress(blob,mtime=0))
    sys.path.insert(0,str(ROOT/'tools/apk-analyze'));import il2cpp_consts as native
    dump=work/'dump.cs';dump.write_bytes(gzip.decompress((ROOT/'reverse-engineering/il2cpp/dump.cs.gz').read_bytes()))
    methods=native.parse_dump(str(dump));native.parse_dump=lambda _:[(cls if cls in NATIVE else '__not_selected__',ns,name,offset,rva,sig) for cls,ns,name,offset,rva,sig in methods]
    native.TARGET_CLASSES.clear();native.TARGET_CLASSES.update({c:'Camera size runtime writer recovery' for c in NATIVE})
    native.OUT_RAW=str(out/'native');native.OUT_MD=str(work/'native.md');native.OUT_CSV=str(work/'native.csv');sys.argv=['native',str(dump),str(work/'libil2cpp.so')];assert native.main()==0
    slices=[]
    for va in (0x756f00,0x756fb8):
        segment=next(s for s in native.elf_segments(str(work/'libil2cpp.so')) if s[0]<=va and va+4<=s[0]+s[2])
        offset=segment[1]+va-segment[0]
        with (work/'libil2cpp.so').open('rb') as binary:
            binary.seek(offset);data=binary.read(4)
        slices.append(dict(va=hex(va),file_offset=offset,hex=data.hex(),sha256=sha(data),float32=struct.unpack('<f',data)[0]))
    (out/'native-data.json').write_text(json.dumps(dict(native_sha256=found['lib/arm64-v8a/libil2cpp.so'],slices=slices),indent=2)+'\n')
    paths=[out/'native-data.json',out/'components.json.gz',*sorted((out/'native').iterdir())]
    (out/'index.json').write_text(json.dumps(dict(dump_sha256_decompressed=sha(dump.read_bytes()),files=[dict(path=p.relative_to(out).as_posix(),sha256_decompressed=sha(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())) for p in paths]),indent=2)+'\n')
    print('::notice::'+json.dumps(dict(components=len(rows),camera_refs=sum(len(r['cameras']) for r in rows),header_errors=len(errors))))


if __name__=='__main__':main()
