"""Pinned executable bytes for all24 player attack classes/nested state machines.
Not an APK copy: bounded methods plus their already-identified numeric pool cells.
"""
import argparse,bisect,gzip,hashlib,io,json,sys,tempfile,zipfile
from pathlib import Path
from combat_coroutine_cells import APK_SHA,LIB_SHA,extract
ROOT=Path(__file__).resolve().parents[2]

def recover(binary,out):
    assert hashlib.sha256(binary).hexdigest()==LIB_SHA
    sys.path.insert(0,str(ROOT/'tools/apk-analyze'));import il2cpp_consts as native
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'dump.cs';p.write_bytes(gzip.decompress((ROOT/'reverse-engineering/il2cpp/dump.cs.gz').read_bytes()));rows=native.parse_dump(str(p))
    starts=sorted({r[4] for r in rows});roots={f'Player_Attack_{i}' for i in range(1,25)};selected=[]
    for cls,ns,name,offset,a,sig in rows:
        if cls.split('.')[0] not in roots:continue
        b=starts[bisect.bisect_right(starts,a)];assert 0<b-a<65536
        cell=extract(binary,[(a,b-a)])['cells'][0]
        selected.append(dict(cls=cls,method=name,signature=sig,**cell))
    pool=json.load(gzip.open(ROOT/'reverse-engineering/raw/combat-chain/referenced-cells.json.gz'))['cells']
    pool=[x for x in pool if 0x750000<=int(x['va'],16)<0x780000]
    for x in pool:assert extract(binary,[(int(x['va'],16),x['width'])])['cells'][0]==x
    out.mkdir(parents=True,exist_ok=True);payload=dict(xapk_sha256=APK_SHA,lib_sha256=LIB_SHA,methods=selected,pool=pool)
    p=out/'method-bytes.json.gz';p.write_bytes(gzip.compress(json.dumps(payload,indent=2).encode(),mtime=0));assert p.stat().st_size<5_000_000
    (out/'index.json').write_text(json.dumps(dict(status='PINNED_ALL24_PLAYER_ATTACK_METHOD_BYTES_NOT_LIVE_UNITY',methods=len(selected),roots=sorted(roots),sha256=hashlib.sha256(p.read_bytes()).hexdigest()),indent=2)+'\n')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--xapk',required=True);ap.add_argument('--output',required=True);a=ap.parse_args();data=Path(a.xapk).read_bytes();assert hashlib.sha256(data).hexdigest()==APK_SHA
    binaries=[]
    with zipfile.ZipFile(io.BytesIO(data)) as outer:
        for n in outer.namelist():
            if not n.endswith('.apk'):continue
            with zipfile.ZipFile(io.BytesIO(outer.read(n))) as part:
                p='lib/arm64-v8a/libil2cpp.so'
                if p in part.namelist():binaries.append(part.read(p))
    assert len(binaries)==1;recover(binaries[0],Path(a.output))
