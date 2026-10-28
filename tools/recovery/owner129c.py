"""Cycle 129 stage 3: pinned original-bytes recovery of the node constructor, the
owner registry lookup, the animator-side vtable region and the referenced rodata strings.

Static bytes only. No execution, no symbols, no class names asserted.
"""
import argparse,gzip,hashlib,io,json,struct,zipfile
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
XAPK_SHA='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
ROOTS=(0x6ceb88,0x3d8614,0x49ffc8,0x572a38,0x570ff0,0x6ce464,0x572a9c,0x572834,
       0x6d14d4,0x3c986c,0x6b947c,0x6cf7b4,0x6cef64,0x6cefdc,0x6bba20,0x6b6c40)
STRINGS=(0xc0fce,0x101411,0x12da21)
VT_REGION=(0x10b0a00,0x10b1900)
STORE_TARGETS=(0x6cf7b4,0x6cef64,0x6cefdc,0x6b81c4,0x6bba20,0x6ceb88)
CAP_WIN=0x1000;STR_CAP=96
def sha(b):return hashlib.sha256(b).hexdigest()
def recover(path):
    data=path.read_bytes();assert sha(data)==XAPK_SHA,'XAPK pin mismatch'
    found=[]
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for name in z.namelist():
            if not name.endswith('.apk'):continue
            with zipfile.ZipFile(io.BytesIO(z.read(name))) as a:
                lib='lib/arm64-v8a/libunity.so'
                if lib in a.namelist():found.append((name,lib,a.read(lib)))
    assert len(found)==1;apk,lib,b=found[0]
    assert b[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',b,18)[0]==183
    off=struct.unpack_from('<Q',b,32)[0];size,count=struct.unpack_from('<HH',b,54)
    segments=[]
    for i in range(count):
        p=struct.unpack_from('<IIQQQQQQ',b,off+i*size)
        if p[0]==1:segments.append(dict(flags=p[1],offset=p[2],va=p[3],file_size=p[5],memory_size=p[6]))
    def va(pos):
        s=next(s for s in segments if s['offset']<=pos<s['offset']+s['file_size']);return s['va']+pos-s['offset']
    def offset(addr):
        s=next(s for s in segments if s['va']<=addr<s['va']+s['file_size']);return s['offset']+addr-s['va']
    def in_exec(a):return any(s['flags']&1 and s['va']<=a<s['va']+s['file_size'] for s in segments)
    unwind={}
    for i in range(count):
        ph=struct.unpack_from('<IIQQQQQQ',b,off+i*size)
        if ph[0]!=0x6474e550:continue
        h=ph[2];base=ph[3];assert b[h:h+4]==bytes([1,0x1b,3,0x3b])
        n=struct.unpack_from('<I',b,h+8)[0]
        for j in range(n):
            a,d=struct.unpack_from('<ii',b,h+12+j*8);start=base+a;fde=base+d;pos=offset(fde)
            delta,length=struct.unpack_from('<iI',b,pos+8)
            if fde+8+delta!=start or not 0<length<=0x20000:continue
            unwind[start]=dict(start=start,end=start+length)
    shoff=struct.unpack_from('<Q',b,40)[0];shsize,shcount=struct.unpack_from('<HH',b,58)
    sections=[struct.unpack_from('<IIQQQQIIQQ',b,shoff+i*shsize) for i in range(shcount)]
    relas=[];rela_index={}
    for i in range(shcount):
        p=sections[i]
        if p[1]!=4 or p[9]!=24:continue
        for pos in range(p[4],p[4]+p[5],24):
            address,info,addend=struct.unpack_from('<QQq',b,pos)
            if info&0xffffffff==1027:
                rec=dict(address=address,addend=addend,file_offset=pos);relas.append(rec);rela_index[address]=addend
    windows=[];seen=set()
    for a in ROOTS:
        if a in seen:continue
        seen.add(a)
        rec=unwind.get(a);length=min((rec['end']-a) if rec else 0x400,CAP_WIN)
        try:pos=offset(a);assert offset(a+length-1)==pos+length-1
        except (StopIteration,AssertionError):continue
        windows.append(dict(va=a,file_offset=pos,extent_source='original_FDE' if rec else 'bounded_window',
                            unwind=rec,hex=b[pos:pos+length].hex()))
    strings=[]
    for s in STRINGS:
        pos=offset(s);raw=b[pos:pos+STR_CAP];end=raw.find(b'\x00')
        raw=raw[:end if end>=0 else STR_CAP]
        strings.append(dict(va=s,file_offset=pos,length=len(raw),ascii=raw.decode('latin-1')))
    lo,hi=VT_REGION
    pos=offset(lo);assert offset(hi-1)==pos+hi-lo-1
    region=dict(va=lo,file_offset=pos,hex=b[pos:pos+hi-lo].hex(),
                relas=[r for r in relas if lo<=r['address']<hi])
    # dense RELA runs = candidate tables
    tables=[];cur=[]
    for r in region['relas']:
        if in_exec(r['addend']):
            if cur and r['address']!=cur[-1]['address']+8:tables.append(cur);cur=[]
            cur.append(r)
        else:
            if cur:tables.append(cur);cur=[]
    if cur:tables.append(cur)
    table_recs=[dict(table_start=t[0]['address'],table_end=t[-1]['address']+8,slot_count=len(t),
                     slots=[dict(offset=i*8,address=x['address'],addend=x['addend']) for i,x in enumerate(t)]) for t in tables if len(t)>=2]
    # every ADRP+ADD reference to a table base in the region
    bases=set()
    for t in table_recs:bases.update(x['address'] for x in t['slots'])
    refs=[]
    for s in segments:
        if not s['flags']&1:continue
        for p in range(s['offset'],s['offset']+s['file_size']-3,4):
            w=struct.unpack_from('<I',b,p)[0]
            if w&0x9f000000!=0x90000000:continue
            rd=w&31;pc=va(p)
            imm=(((w>>5)&0x7ffff)<<2|((w>>29)&3))<<12
            page=(pc&~4095)+imm
            for q in range(p+4,min(p+36,s['offset']+s['file_size']-3),4):
                op=struct.unpack_from('<I',b,q)[0]
                if op&0xffc00000==0x91000000 and ((op>>5)&31)==rd:
                    target=page+((op>>10)&4095)
                    if target in bases:
                        refs.append(dict(target=target,pc=pc,add_va=va(q),hex=b[p:q+4].hex()))
                    break
    # store sites into [reg + 0x118] and [+0x19c] loads inside the pinned windows
    stores=[]
    for w in windows:
        code=bytes.fromhex(w['hex'])
        for i in range(0,len(code)-3,4):
            wd=struct.unpack_from('<I',code,i)[0]
            if wd&0xffc00000==0xf9000000:
                imm=((wd>>10)&0xfff)*8
                if imm==0x118:
                    stores.append(dict(window=w['va'],pc=w['va']+i,hex=code[i:i+4].hex(),
                                       rt=wd&31,rn=(wd>>5)&31))
    return dict(provisional=True,xapk_sha256=XAPK_SHA,apk_entry=apk,library_entry=lib,libunity_sha256=sha(b),
        libunity_size=len(b),tool_sha256=sha(Path(__file__).read_bytes()),segments=segments,roots=list(ROOTS),
        windows=windows,strings=strings,region=region,tables=table_recs,code_refs=refs,stores_118=stores,
        rela_to_targets=[dict(target=t,n=sum(1 for r in relas if r['addend']==t),
                              hits=[dict(address=r['address'],file_offset=r['file_offset']) for r in relas if r['addend']==t][:8]) for t in (0x6cf7b4,0x6cef64,0x6cefdc,0x6bba20,0x6b6c40,0x6ceb88)],
        limits=['Bounded windows only: FDE extents capped at 0x1000 bytes.','Strings are decoded from original .rodata bytes by address, not from symbols.','Table slot counts are RELA-backed dense runs; unrelocated slots stay unknown, not null.','Static bytes only; no execution, no class names.'])
def main():
    p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True);a=p.parse_args();r=recover(a.xapk)
    out=ROOT/'reverse-engineering/raw/owner129c/probe.json.gz';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(gzip.compress((json.dumps(r,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
    print('saved',out,'windows',len(r['windows']),'tables',len(r['tables']),'refs',len(r['code_refs']),'stores118',len(r['stores_118']))
if __name__=='__main__':main()
