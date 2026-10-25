"""Narrow pinned ELF/metadata recovery: Invoke string and referenced TypeInfo cells."""
import argparse,hashlib,io,json,struct,zipfile
from pathlib import Path
from combat_coroutine_cells import APK_SHA,extract
META_SHA='449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69'


def recover(binary,metadata):
    assert hashlib.sha256(metadata).hexdigest()==META_SHA
    out=extract(binary,((0x2ae8560,8),(0x2ae82a0,8)))
    out['status']='PINNED_INVOKE_STRING_ELF_RELA_AND_METADATA_LITERAL_NOT_RUNTIME'
    shoff=struct.unpack_from('<Q',binary,40)[0];size,count=struct.unpack_from('<HH',binary,58)
    rel=[]
    for i in range(count):
        sh=struct.unpack_from('<IIQQQQIIQQ',binary,shoff+i*size)
        if sh[1]!=4:continue
        for p in range(sh[4],sh[4]+sh[5],sh[9] or 24):
            va,info,target=struct.unpack_from('<QQq',binary,p)
            if va not in (0x2ae8560,0x2ae82a0):continue
            assert info==1027
            c=extract(binary,((target,8),))['cells'][0]
            rel.append({'got':hex(va),'effective':hex(target),'rela_file_offset':p,'rela_hex':binary[p:p+24].hex(),'pointee_cell':c})
    assert len(rel)==2
    row=next(r for r in rel if r['got']=='0x2ae8560')
    encoded=struct.unpack('<Q',bytes.fromhex(row['pointee_cell']['hex']))[0]
    assert encoded>>32==0 and encoded>>29==5  # IL2CPP string literal usage
    index=(encoded&0x1ffffffe)>>1
    magic,version,start,bytecount,data_start,data_size=struct.unpack_from('<6I',metadata)
    assert magic==0xfab11baf and version==31 and index<bytecount//8
    definition=start+index*8
    length,offset=struct.unpack_from('<II',metadata,definition)
    assert offset+length<=data_size
    text=metadata[data_start+offset:data_start+offset+length]
    out.update(metadata_sha256=META_SHA,relocations=rel,
      metadata_header_hex=metadata[:24].hex(),string_literal={
        'encoded':hex(encoded),'index':index,'definition_file_offset':definition,
        'definition_hex':metadata[definition:definition+8].hex(),
        'data_file_offset':data_start+offset,'hex':text.hex(),'utf8':text.decode()})
    return out


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--xapk',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    data=Path(a.xapk).read_bytes();assert hashlib.sha256(data).hexdigest()==APK_SHA
    results=[]
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for n in z.namelist():
            if not n.endswith('.apk'):continue
            with zipfile.ZipFile(io.BytesIO(z.read(n))) as inner:
                if 'lib/arm64-v8a/libil2cpp.so' not in inner.namelist():continue
                results.append(recover(inner.read('lib/arm64-v8a/libil2cpp.so'),inner.read('assets/bin/Data/Managed/Metadata/global-metadata.dat')))
    assert len(results)==1
    p=Path(a.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(results[0],indent=2)+'\n')
