"""Pinned original-bytes recovery of the producer side of the graph-builder owner field.

Stage 2 of cycle 129: recovers the bodies of the functions that create the graph node and
resolve the owner (6bba20 / 6b6c40), the neighbouring setup/teardown helpers, every
ADRP+ADD reference to the 12 pin-resolved vtables in 10b1000..10b1900, and RELA membership
for the node-family vtables. Static bytes only; no execution, no symbols, no class names.
"""
import argparse,bisect,gzip,hashlib,io,json,struct,zipfile
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
XAPK_SHA='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
ROOTS=(0x6bba20,0x6b6c40,0x6b81c4,0x6b7d58,0x6b2258,0x6b4bfc,0x6b1c98,0x6b947c,
       0x6b80e0,0x6b8054,0x6b6dec,0x6b1a00,0x6b7158,0x6b2050,0x6b1b1c,
       0x6d353c,0x6d2894,0x6d26d4,0x6d5e58,0x6d2950,0x6cf768,0x5710ec,0x5718cc,0x6cf7b4)
VTABLES=(0x10b1000,0x10b1100,0x10b1130,0x10b1150,0x10b1240,0x10b1330,0x10b1420,
         0x10b1440,0x10b1550,0x10b1640,0x10b1730,0x10b1820)
MAX_SITES=12;CTX=0x40;CAP_WIN=0x1000
def sha(b):return hashlib.sha256(b).hexdigest()
def signed(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
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
    starts=sorted(unwind)
    def owner(pc):
        j=bisect.bisect_right(starts,pc)-1
        if j<0:return None
        f=unwind[starts[j]];return f if pc<f['end'] else None
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
    # full .text pass, one shot: branch refs to every known entry, and ADRP page bases
    refs=defaultdict(list);truncated=set();adrp_pages=[];stored=[]
    rootset=set(ROOTS)
    for s in segments:
        if not s['flags']&1:continue
        for pos in range(s['offset'],s['offset']+s['file_size']-3,4):
            word=struct.unpack_from('<I',b,pos)[0]
            pc=va(pos)
            if word&0x7c000000==0x14000000:
                target=pc+(signed(word&0x3ffffff,26)<<2)
                if target not in rootset and target not in unwind:continue
                if target not in rootset:continue
                lst=refs[target]
                if len(lst)>=MAX_SITES:truncated.add(target);continue
                f=owner(pc)
                lst.append(dict(pc=pc,kind='bl' if word>>31 else 'b',word_hex=b[pos:pos+4].hex(),caller_start=f['start'] if f else None,caller_end=f['end'] if f else None))
            elif word&0x9f000000==0x90000000:
                rd=word&31;imm=signed(((word>>5)&0x7ffff)<<2|((word>>29)&3),21)<<12
                adrp_pages.append((pos,pc,rd,(pc&~4095)+imm))
    # pair ADRP with the next ADD (same reg) inside 36 bytes
    adrp=[]
    page_index=defaultdict(list)
    for pos,pc,rd,page in adrp_pages:page_index[pos].append((rd,page))
    for s in segments:
        if not s['flags']&1:continue
        for pos in range(s['offset'],s['offset']+s['file_size']-3,4):
            if pos not in page_index:continue
            for rd,page in page_index[pos]:
                pc=va(pos)
                for nxt in range(pos+4,min(pos+36,s['offset']+s['file_size']-3),4):
                    op=struct.unpack_from('<I',b,nxt)[0]
                    if op&0xffc00000==0x91000000 and ((op>>5)&31)==rd:
                        target=page+((op>>10)&4095)
                        if target in VTABLES:
                            f=owner(pc)
                            rec=dict(target=target,pc=pc,add_va=va(nxt),hex=b[pos:nxt+4].hex(),
                                     caller_start=f['start'] if f else None)
                            # capture the first store of this register within 0x30 bytes after the ADD
                            rd2=op&31;st=None
                            for k in range(nxt+4,min(nxt+4+0x30,s['offset']+s['file_size']-3),4):
                                w2=struct.unpack_from('<I',b,k)[0]
                                if w2&0xffc00000==0xf9000000 and ((w2>>5)&31)==rd2:
                                    st=dict(pc=va(k),hex=b[k:k+4].hex());break
                            if st:rec['store']=st
                            adrp.append(rec)
                        break
    windows=[];seen=set()
    for a in ROOTS:
        if a in seen:continue
        seen.add(a)
        rec=unwind.get(a);length=min((rec['end']-a) if rec else 0x400,CAP_WIN)
        try:pos=offset(a);assert offset(a+length-1)==pos+length-1
        except (StopIteration,AssertionError):continue
        windows.append(dict(va=a,file_offset=pos,extent_source='original_FDE' if rec else 'bounded_window',hex=b[pos:pos+length].hex()))
    def table(addr):
        start=addr;steps=0
        while addr-8*steps-8 in rela_index and steps<256:
            prev=rela_index[addr-8*steps-8]
            if not (prev==0 or in_exec(prev)):break
            start=addr-8*steps-8;steps+=1
        end=addr+8;steps=0
        while end in rela_index and steps<256:
            nxt=rela_index[end]
            if not (nxt==0 or in_exec(nxt)):break
            end+=8;steps+=1
        n=(end-start)//8
        if n<2:return None
        return dict(table_start=start,table_end=end,slot_index=(addr-start)//8,slot_count=n,
                    slots=[dict(offset=i*8,address=start+i*8,addend=rela_index.get(start+i*8)) for i in range(min(n,256))])
    vts={}
    for v in VTABLES:
        t=table(v)
        if t:vts[v]=t
    addend_refs=[]
    for v in VTABLES:
        addend_refs.append(dict(target=v,hits=[dict(address=r['address'],file_offset=r['file_offset']) for r in relas if r['addend']==v][:8]))
    return dict(provisional=True,xapk_sha256=XAPK_SHA,apk_entry=apk,library_entry=lib,libunity_sha256=sha(b),
        libunity_size=len(b),tool_sha256=sha(Path(__file__).read_bytes()),segments=segments,
        roots=list(ROOTS),windows=windows,root_refs=[dict(target=t,**{'sites':refs.get(t,[])}) for t in ROOTS],
        refs_truncated=[t for t in sorted(truncated)],adrp_refs=adrp,vtables=[dict(base=v,**vts[v]) for v in sorted(vts)],
        vtable_addend_refs=addend_refs,
        limits=['Bounded windows only: original FDE extents capped at 0x1000 bytes per root.','Direct BL/B references and ADRP+ADD pairs only; no indirect data-flow, no execution.','No symbols, RTTI names or class identity asserted.','Vtable slot count is the RELA-backed dense run; unrelocated slots are unknown, not null.'])
def main():
    p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True);a=p.parse_args();r=recover(a.xapk)
    out=ROOT/'reverse-engineering/raw/owner129b/probe.json.gz';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(gzip.compress((json.dumps(r,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
    print('saved',out,'roots',len(r['windows']),'adrp',len(r['adrp_refs']),'vtables',len(r['vtables']))
if __name__=='__main__':main()
