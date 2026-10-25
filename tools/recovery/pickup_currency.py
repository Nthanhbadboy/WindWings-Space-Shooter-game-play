"""Bounded pickup/currency roots and exact dependencies from pinned APK only."""
import argparse,gzip,hashlib,io,json,re,struct,sys,tempfile,zipfile
from pathlib import Path
from combat_coroutine_cells import APK_SHA,LIB_SHA,extract
ROOT=Path(__file__).resolve().parents[2]
ROOTS={'Player_Physics','Sub_Item','Item_Movement'}
EXTRA={0x14efdec,0x14f0da0,0x13999ac}


def recover(binary,destination):
    assert hashlib.sha256(binary).hexdigest()==LIB_SHA
    destination.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(ROOT/'tools/apk-analyze'));import il2cpp_consts as native
    with tempfile.TemporaryDirectory() as td:
        temp=Path(td);dump=temp/'dump.cs';lib=temp/'libil2cpp.so'
        dump.write_bytes(gzip.decompress((ROOT/'reverse-engineering/il2cpp/dump.cs.gz').read_bytes()));lib.write_bytes(binary)
        rows=native.parse_dump(str(dump));eligible=lambda cls,rva:cls.split('.')[0] in ROOTS or rva in EXTRA
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
    (destination/'cells.json').write_text(json.dumps(raw,indent=2)+'\n')
    manifest=dict(status='PINNED_PICKUP_ROOTS_PLUS_SELECTED_DEPENDENCY_RVAS_NOT_FULL_DEPENDENCY_CLASSES',xapk_sha256=APK_SHA,lib_sha256=LIB_SHA,roots=sorted(ROOTS),extra_rvas=[hex(v) for v in sorted(EXTRA)],files=[])
    for p in sorted((destination/'native').iterdir()):manifest['files'].append(dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (destination/'index.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--xapk',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    data=Path(a.xapk).read_bytes();assert hashlib.sha256(data).hexdigest()==APK_SHA
    binaries=[]
    with zipfile.ZipFile(io.BytesIO(data)) as outer:
        for name in outer.namelist():
            if not name.endswith('.apk'):continue
            with zipfile.ZipFile(io.BytesIO(outer.read(name))) as part:
                p='lib/arm64-v8a/libil2cpp.so'
                if p in part.namelist():binaries.append(part.read(p))
    assert len(binaries)==1;recover(binaries[0],Path(a.output).resolve())
