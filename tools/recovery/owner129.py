"""Pinned original libunity owner-side linkage recovery for the graph-builder dispatch.

Recovers, from the pinned XAPK CI cache only:
  - direct BL/B references to the two dispatch entries 6cef64 / 6cefdc,
  - a bounded caller BFS (depth<=3, <=64 functions),
  - RELA/vtable membership of every followed entry,
  - ADRP+ADD function-pointer references,
  - the known node vtable cluster for class-family context,
  - bounded instruction context around every call site (defines the owner argument).
No execution, no symbols, no inferred class names.
"""
import argparse,bisect,gzip,hashlib,io,json,struct,zipfile
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
XAPK_SHA='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
TARGETS=(0x6cef64,0x6cefdc)
CLUSTER=(0x10b1000,0x10b1900)
MAX_FUNCS=64;MAX_DEPTH=3;MAX_SITES=8;CTX=0x60;CAP_WIN=0x800;MAX_SLOTS=128
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
    def in_exec(a):
        return any(s['flags']&1 and s['va']<=a<s['va']+s['file_size'] for s in segments)
    unwind={};unwind_header=None
    for i in range(count):
        ph=struct.unpack_from('<IIQQQQQQ',b,off+i*size)
        if ph[0]!=0x6474e550:continue
        h=ph[2];base=ph[3];enc=b[h:h+4];assert enc==bytes([1,0x1b,3,0x3b]),enc.hex()
        n=struct.unpack_from('<I',b,h+8)[0];unwind_header=dict(va=base,file_offset=h,hex=b[h:h+12].hex(),entry_count=n)
        for j in range(n):
            a,d=struct.unpack_from('<ii',b,h+12+j*8);start=base+a;fde=base+d;pos=offset(fde)
            delta,length=struct.unpack_from('<iI',b,pos+8)
            if fde+8+delta!=start:continue
            if not 0<length<=0x20000:continue
            unwind[start]=dict(start=start,end=start+length,fde_va=fde,fde_hex=b[pos:pos+16].hex())
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
    starts=sorted(unwind)
    def owner(pc):
        j=bisect.bisect_right(starts,pc)-1
        if j<0:return None
        f=unwind[starts[j]]
        return f if pc<f['end'] else None
    # One .text pass: keep branch references only into known function entries, bounded per target.
    refs_by_target=defaultdict(list);refs_truncated=set()
    for s in segments:
        if not s['flags']&1:continue
        for pos in range(s['offset'],s['offset']+s['file_size']-3,4):
            word=struct.unpack_from('<I',b,pos)[0]
            if word&0x7c000000!=0x14000000:continue
            pc=va(pos);target=pc+(signed(word&0x3ffffff,26)<<2)
            if target not in unwind:continue
            lst=refs_by_target[target]
            if len(lst)>=MAX_SITES:
                refs_truncated.add(target);continue
            f=owner(pc)
            lst.append(dict(pc=pc,kind='bl' if word>>31 else 'b',word_hex=b[pos:pos+4].hex(),caller_start=f['start'] if f else None,caller_end=f['end'] if f else None))
    followed={};frontier=[(t,0,None) for t in TARGETS];callsites=[]
    while frontier and len(followed)<MAX_FUNCS:
        a,depth,parent=frontier.pop(0)
        if a in followed:continue
        rec=unwind.get(a)
        followed[a]=dict(entry=a,depth=depth,parent=parent,extent_source='original_FDE' if rec else 'bounded_window_not_function_extent',unwind=rec)
        for x in refs_by_target.get(a,[]):
            lo=max(0,offset(x['pc'])-CTX);hi=min(len(b),offset(x['pc'])+0x10)
            ctx=dict(va=va(lo),file_offset=lo,hex=b[lo:hi].hex())
            callsites.append(dict(target=a,pc=x['pc'],kind=x['kind'],word_hex=x['word_hex'],caller_start=x['caller_start'],caller_end=x['caller_end'],context=ctx))
            if depth<MAX_DEPTH and x['caller_start'] is not None and x['caller_start'] not in followed:
                frontier.append((x['caller_start'],depth+1,a))
    windows=[];seen=set()
    for a,rec in followed.items():
        length=min((rec['unwind']['end']-a) if rec['unwind'] else 0x400,CAP_WIN)
        try:pos=offset(a);assert offset(a+length-1)==pos+length-1
        except (StopIteration,AssertionError):continue
        if a in seen:continue
        seen.add(a);windows.append(dict(va=a,file_offset=pos,hex=b[pos:pos+length].hex()))
    def table(addr):
        start=addr
        steps=0
        while addr-8*steps-8 in rela_index and steps<MAX_SLOTS:
            prev=rela_index[addr-8*steps-8]
            if not (prev==0 or in_exec(prev)):break
            start=addr-8*steps-8;steps+=1
        end=addr+8;steps=0
        while end in rela_index and steps<MAX_SLOTS:
            nxt=rela_index[end]
            if not (nxt==0 or in_exec(nxt)):break
            end+=8;steps+=1
        idx=(addr-start)//8;n=(end-start)//8
        if n<2:return None
        slots=[dict(address=start+i*8,addend=rela_index.get(start+i*8)) for i in range(min(n,MAX_SLOTS))]
        return dict(table_start=start,table_end=end,slot_index=idx,slot_count=n,slots=slots,slot_address=addr)
    rela_by_addend=defaultdict(list)
    for rec in relas:rela_by_addend[rec['addend']].append(rec)
    membership=[]
    for t in list(TARGETS)+[a for a in followed if a not in TARGETS]:
        for rec in rela_by_addend.get(t,[]):
            tb=table(rec['address'])
            if tb:membership.append(dict(target=t,**tb,rela_file_offset=rec['file_offset']))
    adrp=[]
    for s in segments:
        if not s['flags']&1:continue
        for pos in range(s['offset'],s['offset']+s['file_size']-3,4):
            word=struct.unpack_from('<I',b,pos)[0]
            if word&0x9f000000!=0x90000000:continue
            rd=word&31;pc=va(pos)
            imm=signed(((word>>5)&0x7ffff)<<2|((word>>29)&3),21)<<12;page=(pc&~4095)+imm
            for nxt in range(pos+4,min(pos+36,s['offset']+s['file_size']-3),4):
                op=struct.unpack_from('<I',b,nxt)[0]
                if op&0xffc00000==0x91000000 and ((op>>5)&31)==rd:
                    target=page+((op>>10)&4095)
                    if target in TARGETS:
                        adrp.append(dict(target=target,pc=pc,add_va=va(nxt),hex=b[pos:nxt+4].hex()))
    cluster_lo,cluster_hi=CLUSTER
    try:
        pos=offset(cluster_lo);assert offset(cluster_hi-1)==pos+cluster_hi-cluster_lo-1
        cluster=dict(va=cluster_lo,file_offset=pos,hex=b[pos:pos+cluster_hi-cluster_lo].hex(),relas=[r for r in relas if cluster_lo<=r['address']<cluster_hi])
    except (StopIteration,AssertionError):cluster=None
    spans=[(m['table_start'],m['table_end']) for m in membership]
    selected=[r for r in relas if any(lo<=r['address']<hi for lo,hi in spans)]
    return dict(provisional=True,xapk_sha256=XAPK_SHA,apk_entry=apk,library_entry=lib,libunity_sha256=sha(b),libunity_size=len(b),tool_sha256=sha(Path(__file__).read_bytes()),
        segments=segments,unwind_header=unwind_header,targets=list(TARGETS),cluster=cluster,
        followed=[dict(entry=a,**{k:v for k,v in rec.items() if k!='entry'}) for a,rec in sorted(followed.items())],
        windows=windows,callsites=callsites,vtable_membership=membership,adrp_refs=adrp,refs_truncated=[t for t in sorted(refs_truncated)],
        relocations=selected,root_entries=[a for a,rec in sorted(followed.items()) if rec['depth']==0],
        limits=['Bounded caller BFS only (depth<=3, <=64 functions, <=8 call-site contexts per function).','RELATIVE relocations only; vtable walks stop at the first non-code/non-null slot.','No symbols, no typeinfo/RTTI names and no class identity are asserted.','Selected original bytes only, not whole library or runtime.'])
def main():
    p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True);a=p.parse_args();r=recover(a.xapk)
    out=ROOT/'reverse-engineering/raw/owner129/probe.json.gz';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(gzip.compress((json.dumps(r,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
    print('saved',out,'followed',len(r['followed']),'callsites',len(r['callsites']),'vtable',len(r['vtable_membership']),'adrp',len(r['adrp_refs']),'windows',len(r['windows']))
if __name__=='__main__':main()
