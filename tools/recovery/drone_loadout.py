"""Bounded drone loadout and resource-loader paths from pinned APK only."""
import argparse,bisect,gzip,hashlib,io,json,re,struct,sys,tempfile,zipfile
from pathlib import Path
from combat_coroutine_cells import APK_SHA,LIB_SHA,extract
ROOT=Path(__file__).resolve().parents[2]
ROOTS={'GP_Loader','GP_Setup','Drone_Saved_Datas'}
EXTRA=set()


def recover(binary,metadata,destination):
    assert hashlib.sha256(binary).hexdigest()==LIB_SHA
    destination.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(ROOT/'tools/apk-analyze'));import il2cpp_consts as native
    with tempfile.TemporaryDirectory() as td:
        temp=Path(td);dump=temp/'dump.cs';lib=temp/'libil2cpp.so'
        dump.write_bytes(gzip.decompress((ROOT/'reverse-engineering/il2cpp/dump.cs.gz').read_bytes()));lib.write_bytes(binary)
        rows=native.parse_dump(str(dump));eligible=lambda cls,rva:cls.split('.')[0] in ROOTS or rva in EXTRA
        selected={r[0] for r in rows if eligible(r[0],r[4])}
        native.parse_dump=lambda _:[(c if eligible(c,r) else '__not_selected__',ns,n,o,r,s) for c,ns,n,o,r,s in rows]
        native.TARGET_CLASSES.clear();native.TARGET_CLASSES.update({c:'Bounded drone attack recovery; selected RVAs for extra dependencies' for c in selected})
        native.OUT_RAW=str(destination/'native');native.OUT_MD=str(temp/'summary.md');native.OUT_CSV=str(temp/'values.csv')
        sys.argv=['native',str(dump),str(lib)];assert native.main()==0
    raw=extract(binary,())
    wanted=set()
    paths=list((destination/'native').glob('*.asm.txt'))+list((ROOT/'reverse-engineering/raw/combat-chain/native').glob('Player_Attack*.asm.txt'))+[ROOT/'reverse-engineering/raw/combat-chain/native/Player_Ingame.asm.txt']
    for p in paths:
        pages={}
        for line in p.read_text().splitlines():
            if line.startswith(';;;'):pages={}
            m=re.search(r': adrp\s+(x\d+), #0x([0-9a-f]+)',line)
            if m:pages[m[1]]=int(m[2],16);continue
            m=re.search(r': ldr\s+x\d+, \[(x\d+)(?:, #0x([0-9a-f]+))?\]',line)
            if m and m[1] in pages:wanted.add(pages[m[1]]+int(m[2] or '0',16))
    shoff=struct.unpack_from('<Q',binary,40)[0];size,count=struct.unpack_from('<HH',binary,58);rels=[]
    for i in range(count):
        sh=struct.unpack_from('<IIQQQQIIQQ',binary,shoff+i*size)
        if sh[1]!=4:continue
        for p in range(sh[4],sh[4]+sh[5],sh[9] or 24):
            va,info,target=struct.unpack_from('<QQq',binary,p)
            if va in wanted and info==1027:
                rels.append(dict(got=hex(va),effective=hex(target),rela_file_offset=p,rela_hex=binary[p:p+24].hex()))
    raw['relocations']=rels
    pool=set()
    for p in paths:
        pages={}
        for line in p.read_text().splitlines():
            if line.startswith(';;;'):pages={}
            m=re.search(r': adrp\s+(x\d+), #0x([0-9a-f]+)',line)
            if m:pages[m[1]]=int(m[2],16);continue
            m=re.search(r': ldr\s+([sdq])\d+, \[(x\d+)(?:, #0x([0-9a-f]+))?\]',line)
            if m and m[2] in pages:
                va=pages[m[2]]+int(m[3] or '0',16)
                if 0x750000<=va<0x780000:pool.add((va,{'s':4,'d':8,'q':16}[m[1]]))
    raw['float_load_candidates']=extract(binary,sorted(pool))['cells']
    assert hashlib.sha256(metadata).hexdigest()=='449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69'
    magic,version,ls,lc,ds,dc=struct.unpack_from('<6I',metadata);assert magic==0xfab11baf and version==31
    literals=[]
    for row in rels:
        target=int(row['effective'],16)
        if not 0x2ba0000<=target<0x2c00000:continue
        cell=extract(binary,((target,8),))['cells'][0];encoded=struct.unpack('<Q',bytes.fromhex(cell['hex']))[0]
        if encoded>>29!=5:continue
        idx=(encoded&0x1ffffffe)>>1;assert idx<lc//8
        length,index=struct.unpack_from('<II',metadata,ls+idx*8);assert index+length<=dc
        text=metadata[ds+index:ds+index+length]
        literals.append(dict(got=row['got'],pointee=cell,index=idx,definition_hex=metadata[ls+idx*8:ls+idx*8+8].hex(),data_file_offset=ds+index,hex=text.hex(),utf8=text.decode()))
    raw['metadata_header_hex']=metadata[:24].hex();raw['literals']=literals
    raw['status']='PINNED_HP_BOARD_CELLS_CANDIDATES_NOT_GENERAL_POINTER_FLOW'
    (destination/'cells.json').write_text(json.dumps(raw,indent=2)+'\n')
    manifest=dict(status='PINNED_DRONE_LOADOUT_AND_RESOURCE_LOADER',roots=sorted(ROOTS),xapk_sha256=APK_SHA,lib_sha256=LIB_SHA,files=[])
    for p in sorted((destination/'native').iterdir()):manifest['files'].append(dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (destination/'index.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--xapk',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    data=Path(a.xapk).read_bytes();assert hashlib.sha256(data).hexdigest()==APK_SHA
    binaries=[];metas=[]
    with zipfile.ZipFile(io.BytesIO(data)) as outer:
        for name in outer.namelist():
            if not name.endswith('.apk'):continue
            with zipfile.ZipFile(io.BytesIO(outer.read(name))) as part:
                p='lib/arm64-v8a/libil2cpp.so'
                if p in part.namelist():binaries.append(part.read(p))
                m='assets/bin/Data/Managed/Metadata/global-metadata.dat'
                if m in part.namelist():metas.append(part.read(m))
    assert len(binaries)==len(metas)==1;recover(binaries[0],metas[0],Path(a.output).resolve())
