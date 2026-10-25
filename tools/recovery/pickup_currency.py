"""Bounded pickup/currency roots and exact dependencies from pinned APK only."""
import argparse,bisect,gzip,hashlib,io,json,re,struct,sys,tempfile,zipfile
from pathlib import Path
from combat_coroutine_cells import APK_SHA,LIB_SHA,extract
ROOT=Path(__file__).resolve().parents[2]
ROOTS={'Player_Physics','Sub_Item','Item_Movement'}
EXTRA={0x14efdec,0x14f0da0,0x13999ac,0x12546d0,0x1250134}


def recover(binary,metadata,destination):
    assert hashlib.sha256(binary).hexdigest()==LIB_SHA
    destination.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(ROOT/'tools/apk-analyze'));import il2cpp_consts as native
    with tempfile.TemporaryDirectory() as td:
        temp=Path(td);dump=temp/'dump.cs';lib=temp/'libil2cpp.so'
        dump.write_bytes(gzip.decompress((ROOT/'reverse-engineering/il2cpp/dump.cs.gz').read_bytes()));lib.write_bytes(binary)
        rows=native.parse_dump(str(dump))
        starts=sorted(set(r[4] for r in rows));posters=[];extra=set(EXTRA)
        import capstone
        md=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_LITTLE_ENDIAN)
        phoff=struct.unpack_from('<Q',binary,32)[0];ps,pc=struct.unpack_from('<HH',binary,54)
        for i in range(pc):
            seg=struct.unpack_from('<IIQQQQQQ',binary,phoff+i*ps)
            if seg[0]!=1 or not seg[1]&1:continue
            offset=seg[2]
            while True:
                off=binary.find(bytes.fromhex('41008052'),offset,seg[2]+seg[5]) # MOVZ w1,#2
                if off<0:break
                offset=off+4
                if (off-seg[2])%4:continue
                va=seg[3]+off-seg[2];idx=bisect.bisect_right(starts,va)-1
                if idx<0:continue
                end=starts[idx+1] if idx+1<len(starts) else va+128
                for at,size,op,args in md.disasm_lite(binary[off:off+min(128,end-va)],va):
                    if at==va:continue
                    if op in ('bl','b') and args=='#0x1434cb4':
                        owners=[dict(cls=r[0],namespace=r[1],method=r[2]) for r in rows if r[4]==starts[idx]]
                        posters.append(dict(start=hex(starts[idx]),mov=hex(va),post=hex(at),window_hex=binary[off:off+at-va+4].hex(),owners=owners))
                        extra.add(starts[idx]);break
                    if op in ('bl','blr','br','b','ret'):break
                    if not op.startswith(('st','b.')) and op not in ('cmp','tst','cbz','cbnz','tbz','tbnz') and args.split(',')[0] in ('w1','x1'):break
        eligible=lambda cls,rva:cls.split('.')[0] in ROOTS or rva in extra
        selected={r[0] for r in rows if eligible(r[0],r[4])}
        native.parse_dump=lambda _:[(c if eligible(c,r) else '__not_selected__',ns,n,o,r,s) for c,ns,n,o,r,s in rows]
        native.TARGET_CLASSES.clear();native.TARGET_CLASSES.update({c:'Bounded pickup/currency recovery; selected RVAs for extra dependencies' for c in selected})
        native.OUT_RAW=str(destination/'native');native.OUT_MD=str(temp/'summary.md');native.OUT_CSV=str(temp/'values.csv')
        sys.argv=['native',str(dump),str(lib)];assert native.main()==0
    raw=extract(binary,((0x756f3c,4),(0x756e50,4),(0x7570f0,4),(0x756fa4,4),(0x756de8,4),(0x77a000,4096)))
    raw['status']='PINNED_PICKUP_FLOAT_CELLS_AND_BOUNDED_DISPATCH_PAGE_NOT_RUNTIME'
    # Preserve exact RELA rows for metadata-address candidates in new roots and
    # existing controller Start/coin handlers, not a general pointer dataflow proof.
    wanted=set()
    paths=list((destination/'native').glob('*.asm.txt'))+[ROOT/'reverse-engineering/raw/combat-receivers/Player_Controller.asm.txt']
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
    assert hashlib.sha256(metadata).hexdigest()=='449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69'
    header=struct.unpack_from('<6I',metadata);magic,version,ls,lc,ds,dc=header
    assert magic==0xfab11baf and version==31
    literals=[]
    for got in ('0x2adf300','0x2adf3e0','0x2adcca0'):
        row=next(r for r in rels if r['got']==got);cell=extract(binary,((int(row['effective'],16),8),))['cells'][0]
        encoded=struct.unpack('<Q',bytes.fromhex(cell['hex']))[0];idx=(encoded&0x1ffffffe)>>1
        assert encoded>>29==5 and idx<lc//8
        length,index=struct.unpack_from('<II',metadata,ls+idx*8);assert index+length<=dc
        text=metadata[ds+index:ds+index+length]
        literals.append(dict(got=got,pointee=cell,index=idx,definition_hex=metadata[ls+idx*8:ls+idx*8+8].hex(),data_file_offset=ds+index,hex=text.hex(),utf8=text.decode()))
    raw['metadata_header_hex']=metadata[:24].hex();raw['literals']=literals
    raw['direct_event2_post_candidates']=posters
    (destination/'cells.json').write_text(json.dumps(raw,indent=2)+'\n')
    manifest=dict(status='PINNED_PICKUP_ROOTS_PLUS_SELECTED_DEPENDENCY_RVAS_NOT_FULL_DEPENDENCY_CLASSES',xapk_sha256=APK_SHA,lib_sha256=LIB_SHA,roots=sorted(ROOTS),extra_rvas=[hex(v) for v in sorted(EXTRA)],files=[])
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
