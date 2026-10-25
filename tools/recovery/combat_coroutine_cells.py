"""Extract two byte jump tables, not another full APK analysis/export."""
import argparse
import hashlib
import gzip
import sys
import tempfile
import io
import json
from pathlib import Path
import struct
import zipfile

APK_SHA = 'f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
LIB_SHA = '9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99'


def extract(binary):
    assert hashlib.sha256(binary).hexdigest() == LIB_SHA
    assert binary[:6] == b'\x7fELF\x02\x01'
    phoff = struct.unpack_from('<Q', binary, 32)[0]
    entsize, count = struct.unpack_from('<HH', binary, 54)
    segments = [struct.unpack_from('<IIQQQQQQ',binary,phoff+i*entsize) for i in range(count)]
    cells=[]
    for va,width in ((0x77a07d,4),(0x77a081,5)):
        segment=next(s for s in segments if s[0]==1 and s[3]<=va and va+width<=s[3]+s[5])
        offset=segment[2]+va-segment[3]
        cells.append({'va':hex(va),'file_offset':offset,'width':width,'hex':binary[offset:offset+width].hex()})
    return {'status':'PINNED_ELF_BYTE_JUMP_TABLES_NOT_GUESSED_CONTROL_FLOW','xapk_sha256':APK_SHA,'lib_sha256':LIB_SHA,'cells':cells}


def recover_delegates(binary, destination):
    root=Path(__file__).resolve().parents[2]
    sys.path.insert(0,str(root/'tools/apk-analyze'))
    import il2cpp_consts as native
    with tempfile.TemporaryDirectory() as folder:
        temp=Path(folder);dump=temp/'dump.cs';lib=temp/'libil2cpp.so'
        dump.write_bytes(gzip.decompress((root/'reverse-engineering/il2cpp/dump.cs.gz').read_bytes()))
        lib.write_bytes(binary)
        rows=native.parse_dump(str(dump))
        selected={r[0] for r in rows if r[0].split('.')[0] in ('Player9_Clone','Player23_Pumpkin')}
        assert {'Player9_Clone','Player23_Pumpkin'}<=selected
        masked=[(cls if cls in selected else '__not_selected__',ns,name,offset,rva,sig) for cls,ns,name,offset,rva,sig in rows]
        native.parse_dump=lambda _:masked
        native.TARGET_CLASSES.clear();native.TARGET_CLASSES.update({c:'Delegated clone/pumpkin combat control' for c in selected})
        native.OUT_RAW=str(destination);native.OUT_MD=str(temp/'summary.md');native.OUT_CSV=str(temp/'floats.csv')
        sys.argv=['native',str(dump),str(lib)];assert native.main()==0
    manifest={'status':'PINNED_DELEGATED_COMBAT_NATIVE_NOT_RUNTIME','xapk_sha256':APK_SHA,'lib_sha256':LIB_SHA,'classes':sorted(selected),'files':[]}
    for path in sorted(destination.iterdir()):
        if path.name=='index.json':continue
        manifest['files'].append({'path':str(path.relative_to(root)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    (destination/'index.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--xapk',required=True);parser.add_argument('--output',required=True);parser.add_argument('--delegates-dir');args=parser.parse_args()
    data=Path(args.xapk).read_bytes();assert hashlib.sha256(data).hexdigest()==APK_SHA
    found=[]
    with zipfile.ZipFile(io.BytesIO(data)) as outer:
        for name in outer.namelist():
            if name.endswith('.apk'):
                with zipfile.ZipFile(io.BytesIO(outer.read(name))) as inner:
                    path='lib/arm64-v8a/libil2cpp.so'
                    if path in inner.namelist():
                        binary=inner.read(path);found.append(extract(binary))
                        if args.delegates_dir:recover_delegates(binary,Path(args.delegates_dir).resolve())
    assert len(found)==1
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(found[0],indent=2)+'\n')
