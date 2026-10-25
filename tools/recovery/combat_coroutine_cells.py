"""Extract two byte jump tables, not another full APK analysis/export."""
import argparse
import hashlib
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


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--xapk',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    data=Path(args.xapk).read_bytes();assert hashlib.sha256(data).hexdigest()==APK_SHA
    found=[]
    with zipfile.ZipFile(io.BytesIO(data)) as outer:
        for name in outer.namelist():
            if name.endswith('.apk'):
                with zipfile.ZipFile(io.BytesIO(outer.read(name))) as inner:
                    path='lib/arm64-v8a/libil2cpp.so'
                    if path in inner.namelist():found.append(extract(inner.read(path)))
    assert len(found)==1
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(found[0],indent=2)+'\n')
