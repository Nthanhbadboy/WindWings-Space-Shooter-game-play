"""Recover pinned L3 UI script programs, not original assets or a full executable."""
import argparse,bisect,gzip,hashlib,io,json,struct,sys,tempfile,zipfile
from pathlib import Path
from combat_coroutine_cells import APK_SHA,LIB_SHA,extract
ROOT=Path(__file__).resolve().parents[2]
CLASSES={'Board_Home','Board_Maps','Board_Stage','Board_Players','Board_Drones','Board_Pause','Board_Reborn','Board_Reborn_IAP','Board_Endgame','GP_Tutorials','Popup','Popup_Notices','UIObjectAnchors'}

def recover(binary,out):
    assert hashlib.sha256(binary).hexdigest()==LIB_SHA
    sys.path.insert(0,str(ROOT/'tools/apk-analyze'));import il2cpp_consts as native
    with tempfile.TemporaryDirectory() as td:
        work=Path(td);dump=work/'dump.cs';lib=work/'libil2cpp.so';dump.write_bytes(gzip.decompress((ROOT/'reverse-engineering/il2cpp/dump.cs.gz').read_bytes()));lib.write_bytes(binary)
        methods=native.parse_dump(str(dump));eligible=lambda c,n:c.split('.')[0] in CLASSES and (not n or c=='UIObjectAnchors' and n=='TuPro')
        selected=[r for r in methods if eligible(r[0],r[1])];starts=sorted({r[4] for r in methods});rows=[]
        assert CLASSES<={r[0].split('.')[0] for r in selected}
        for cls,ns,name,offset,rva,sig in selected:
            end=starts[bisect.bisect_right(starts,rva)];assert 0<end-rva<262144
            rows.append(dict(cls=cls,namespace=ns,method=name,signature=sig,**extract(binary,[(rva,end-rva)])['cells'][0]))
        native.parse_dump=lambda _:[(c if eligible(c,n) else '__not_selected__',n,name,offset,rva,sig) for c,n,name,offset,rva,sig in methods]
        native.TARGET_CLASSES.clear();native.TARGET_CLASSES.update({r[0]:'Pinned L3 script UI state driver' for r in selected})
        native.OUT_RAW=str(out/'native');native.OUT_MD=str(work/'native.md');native.OUT_CSV=str(work/'native.csv');sys.argv=['native',str(dump),str(lib)];assert native.main()==0
        # Preserve exact relocation bytes; no guessed metadata pointer initialization.
        shoff=struct.unpack_from('<Q',binary,40)[0];size,count=struct.unpack_from('<HH',binary,58);relocations=[]
        for i in range(count):
            sh=struct.unpack_from('<IIQQQQIIQQ',binary,shoff+i*size)
            if sh[1]!=4:continue
            for p in range(sh[4],sh[4]+sh[5],sh[9] or 24):
                va,info,target=struct.unpack_from('<QQq',binary,p)
                if 0x2ad0000<=va<0x2b00000 and info==1027:relocations.append(dict(offset=hex(va),addend=hex(target),file_offset=p,hex=binary[p:p+24].hex()))
        out.mkdir(parents=True,exist_ok=True)
        blob=gzip.compress(json.dumps(dict(provisional=True,xapk_sha256=APK_SHA,lib_sha256=LIB_SHA,span_rule='next distinct dump RVA; may include padding; never minimum-eight-byte overlap',methods=rows,relocations=relocations),separators=(',',':')).encode(),mtime=0)
        assert len(blob)<5_000_000;(out/'method-bytes.json.gz').write_bytes(blob)
    files=[p for p in sorted(out.rglob('*')) if p.is_file() and p.name!='index.json']
    assert all(p.stat().st_size<5_000_000 for p in files)
    (out/'index.json').write_text(json.dumps(dict(provisional=True,xapk_sha256=APK_SHA,lib_sha256=LIB_SHA,tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),classes=sorted(CLASSES),methods=len(rows),files=[dict(path=str(p.relative_to(out)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]),indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--xapk',required=True);a=p.parse_args();blob=Path(a.xapk).read_bytes();assert hashlib.sha256(blob).hexdigest()==APK_SHA;binaries=[]
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for n in z.namelist():
            if not n.endswith('.apk'):continue
            with zipfile.ZipFile(io.BytesIO(z.read(n))) as apk:
                if 'lib/arm64-v8a/libil2cpp.so' in apk.namelist():binaries.append(apk.read('lib/arm64-v8a/libil2cpp.so'))
    assert len(binaries)==1;recover(binaries[0],ROOT/'reverse-engineering/raw/l3-ui-native')
