"""Cycle 132 stage 2: attribute the callees the dispatch scan just revealed.

Stage 1 showed two things it could not finish with bytes alone:
  * `6b7d58` calls `6ce4b4`, not the `6ce464` output ctor recovered in 129 — is that the same FDE?
  * the batch-container owner `b6ab88` calls `6b08c0` / `6b08d8` / `6b08e4`, three addresses at the
    very start of the animator cluster that no earlier cycle looked at.

This stage reports, for a fixed address list, the owning FDE (start + extent), whether the address
is an FDE entry point or an interior address, and the first bytes of that FDE. Bytes only; nothing
is executed, no symbol is used.
"""
import argparse,bisect,gzip,hashlib,io,json,struct,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
XAPK_SHA='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
WANT=(0x6ce4b4,0x6ce464,0x6ce4fc,0x109acc0,0x6b753c,0x6b08c0,0x6b08d8,0x6b08e4,
      0x6b80e0,0x6b7fe8,0x6b8054,0x6b1c98,0x572c7c,0x572c60,0x6b6ab8,0x3e079c)
CAP=0x180
def sha(b):return hashlib.sha256(b).hexdigest()
def parse(b):
    phoff=struct.unpack_from('<Q',b,32)[0];phsize,phnum=struct.unpack_from('<HH',b,54)
    segs=[]
    for i in range(phnum):
        p=struct.unpack_from('<IIQQQQQQ',b,phoff+i*phsize)
        if p[0]==1:segs.append(dict(flags=p[1],offset=p[2],va=p[3],file_size=p[5]))
    return segs,phoff,phsize,phnum
def recover(path):
    data=path.read_bytes();assert sha(data)==XAPK_SHA,'XAPK pin mismatch'
    hits=[]
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for name in z.namelist():
            if not name.endswith('.apk'):continue
            with zipfile.ZipFile(io.BytesIO(z.read(name))) as a:
                lib='lib/arm64-v8a/libunity.so'
                if lib in a.namelist():hits.append((name,lib,a.read(lib)))
    assert len(hits)==1;apk,lib,b=hits[0]
    assert b[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',b,18)[0]==183
    segs,phoff,phsize,phnum=parse(b)
    def offset(a):
        s=next(s for s in segs if s['va']<=a<s['va']+s['file_size']);return s['offset']+a-s['va']
    unwind={}
    for i in range(phnum):
        ph=struct.unpack_from('<IIQQQQQQ',b,phoff+i*phsize)
        if ph[0]!=0x6474e550:continue
        h=ph[2];base=ph[3]
        if b[h:h+4]!=bytes([1,0x1b,3,0x3b]):continue
        for j in range(struct.unpack_from('<I',b,h+8)[0]):
            a,d=struct.unpack_from('<ii',b,h+12+j*8);start=base+a;fde=base+d;pos=offset(fde)
            delta,length=struct.unpack_from('<iI',b,pos+8)
            if fde+8+delta!=start or not 0<length<=0x20000:continue
            unwind[start]=length
    starts=sorted(unwind)
    def owner(pc):
        j=bisect.bisect_right(starts,pc)-1
        if j<0:return None
        a=starts[j]
        return a if pc<a+unwind[a] else None
    rows=[]
    for a in WANT:
        o=owner(a)
        rec=dict(address=a,owner=o,interior=(o is not None and o!=a),
                 extent=unwind.get(o) if o else None,
                 offset_in_fde=(a-o) if o else None)
        if o is not None:
            try:
                pos=offset(o);n=min(unwind[o],CAP)
                if a+8<=o+n:rec['head_hex']=b[pos:pos+16].hex()
                if a!=o:rec['at_hex']=b[offset(a):offset(a)+16].hex()
            except StopIteration:pass
        rows.append(rec)
    return dict(provisional=True,xapk_sha256=XAPK_SHA,apk_entry=apk,library_entry=lib,
        libunity_sha256=sha(b),libunity_size=len(b),tool_sha256=sha(Path(__file__).read_bytes()),
        fde_count=len(unwind),targets=rows,
        limits=['FDE table only; no execution and no symbol resolution.',
                'An interior address means the call target is not an FDE entry point.',
                'Head bytes are the first 16 bytes of the owning FDE, not a full disassembly.'])
def main():
    p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True);a=p.parse_args()
    out=ROOT/'reverse-engineering/raw/owner132b/probe.json.gz';out.parent.mkdir(parents=True,exist_ok=True)
    try:r=recover(a.xapk)
    except Exception:
        import traceback
        (out.parent/'diagnostic.json').write_text(json.dumps(dict(error=traceback.format_exc()),indent=1)+'\n')
        raise
    out.write_bytes(gzip.compress((json.dumps(r,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
    print('saved',out,'fdes',r['fde_count'],'interior',sum(1 for t in r['targets'] if t['interior']))
    for t in r['targets']:
        print(f"  {t['address']:#x} owner={t['owner'] and hex(t['owner'])} extent={t['extent'] and hex(t['extent'])} interior={t['interior']} head={t.get('head_hex','')}")
if __name__=='__main__':main()
