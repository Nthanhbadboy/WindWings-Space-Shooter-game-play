"""Cycle 130 stage 1: pinned original bytes for the animator-side update/trigger chain.

Recovers the trigger functions' callers, the three participating slots of the animator
class table 10b0c80, the class installers, a bounded two-level caller BFS, per-window
memory-access listings, resolved vtable slot membership and referenced rodata strings.
Static bytes only: no execution, no symbols, no class names.
"""
import argparse,bisect,gzip,hashlib,io,json,struct,zipfile
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
XAPK_SHA='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
ROOTS=(0x6b1c5c,0x6b27dc,0x6b3e78,0x6b4820,0x6b72e4,0x6b2050,0x6b1b1c,0x6b1f04,
       0x6b6dec,0x6b6fdc,0x6b7c58,0x6b1538,0x3e079c,0x6b6ab8,0x6b9ac4,0x6b9acc,
       0x6b15f8,0x6b9294,0x6b947c,0x6b2258,0x6b4bfc,0x6b1c98)
SLOT_TARGETS=(0x6b947c,0x6b6ab8,0x3e079c)
VTABLES=(0x10b0c80,)
MAX_FUNCS=40;MAX_DEPTH=2;MAX_SITES=8;CAP_WIN=0x1000;MAX_RODATA=400;STR_CAP=48
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
    def in_text(a):return any(s['flags']&1 and s['va']<=a<s['va']+s['file_size'] for s in segments)
    def readable(a):return any(s['va']<=a<s['va']+min(s['file_size'],s['memory_size']) for s in segments)
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
        f=unwind[starts[j]]
        return f['start'] if pc<f['end'] else None
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
    rela_by_addend=defaultdict(list)
    for rec in relas:rela_by_addend[rec['addend']].append(rec)
    def text_scan(targets,cap=MAX_SITES):
        refs=defaultdict(list);trunc=set();rodata={}
        for s in segments:
            if not s['flags']&1:continue
            for pos in range(s['offset'],s['offset']+s['file_size']-3,4):
                word=struct.unpack_from('<I',b,pos)[0];pc=va(pos)
                if word&0x7c000000==0x14000000:
                    target=pc+(signed(word&0x3ffffff,26)<<2)
                    if target not in targets:continue
                    lst=refs[target]
                    if len(lst)>=cap:trunc.add(target);continue
                    lst.append(dict(pc=pc,kind='bl' if word>>31 else 'b',word_hex=b[pos:pos+4].hex()))
                elif word&0x9f000000==0x90000000 and len(rodata)<MAX_RODATA:
                    rd=word&31
                    imm=signed(((word>>5)&0x7ffff)<<2|((word>>29)&3),21)<<12;page=(pc&~4095)+imm
                    for nxt in range(pos+4,min(pos+36,s['offset']+s['file_size']-3),4):
                        op=struct.unpack_from('<I',b,nxt)[0]
                        if op&0xffc00000==0x91000000 and ((op>>5)&31)==rd:
                            tgt=page+((op>>10)&4095)
                            if tgt in rodata:break
                            if readable(tgt) and not in_text(tgt):
                                q=offset(tgt);raw=b[q:q+STR_CAP];end=raw.find(b'\x00')
                                raw=raw[:end if end>=0 else STR_CAP]
                                if len(raw)>=3 and all(32<=x<127 for x in raw):
                                    rodata[tgt]=dict(va=tgt,length=len(raw),ascii=raw.decode('latin-1'))
                            break
        return refs,trunc,rodata
    def table(addr):
        start=addr;steps=0
        while addr-8*steps-8 in rela_index and steps<256:
            prev=rela_index[addr-8*steps-8]
            if not (prev==0 or in_text(prev)):break
            start=addr-8*steps-8;steps+=1
        end=addr+8;steps=0
        while end in rela_index and steps<256:
            nxt=rela_index[end]
            if not (nxt==0 or in_text(nxt)):break
            end+=8;steps+=1
        n=end-start>>3
        if n<2:return None
        return dict(table_start=start,table_end=end,slot_index=(addr-start)//8,slot_count=n,
                    slots=[dict(offset=i*8,address=start+i*8,addend=rela_index.get(start+i*8)) for i in range(min(n,256))])
    followed={};frontier=[(t,0,None) for t in ROOTS];callsites=[];passes=[];rodata={}
    while frontier and len(followed)<MAX_FUNCS:
        batch=[x for x in frontier if x[0] not in followed][:MAX_FUNCS-len(followed)]
        if not batch:break
        targets={x[0] for x in batch}
        refs,trunc,rod=text_scan(targets)
        rodata.update({k:v for k,v in rod.items() if k not in rodata})
        passes.append(dict(depth=batch[0][1],targets=sorted(targets),sites=sum(len(v) for v in refs.values()),truncated=sorted(trunc)))
        for a,depth,parent in batch:
            rec=unwind.get(a)
            followed[a]=dict(entry=a,depth=depth,parent=parent,extent_source='original_FDE' if rec else 'bounded_window',unwind=rec)
            for s in refs.get(a,[]):
                callsites.append(dict(target=a,pc=s['pc'],kind=s['kind'],word_hex=s['word_hex']))
        nxt=[]
        if any(d<MAX_DEPTH for _,d,_ in batch):
            for c in callsites:
                if c['target'] not in targets:continue
                o=owner(c['pc'])
                depth=min(d for a,d,_ in batch if a==c['target'])
                if o is None or o in followed or len(followed)+len(nxt)>=MAX_FUNCS:continue
                if all(x[0]!=o for x in nxt):nxt.append((o,depth+1,c['target']))
        frontier=nxt
    windows=[];seenw=set()
    for a in sorted(followed):
        rec=followed[a]['unwind'];length=min((rec['end']-a) if rec else 0x400,CAP_WIN)
        if a in seenw:continue
        try:pos=offset(a);assert offset(a+length-1)==pos+length-1
        except (StopIteration,AssertionError):continue
        seenw.add(a);windows.append(dict(va=a,file_offset=pos,extent_source=followed[a]['extent_source'],hex=b[pos:pos+length].hex()))
    slot_membership=[]
    for t in SLOT_TARGETS:
        for rec in rela_by_addend.get(t,[]):
            tb=table(rec['address'])
            if tb:slot_membership.append(dict(target=t,**tb,rela_file_offset=rec['file_offset']))
    vts=[dict(base=v,**tb) for v in VTABLES if (tb:=table(v))]
    return dict(provisional=True,xapk_sha256=XAPK_SHA,apk_entry=apk,library_entry=lib,libunity_sha256=sha(b),
        libunity_size=len(b),tool_sha256=sha(Path(__file__).read_bytes()),segments=segments,roots=list(ROOTS),
        followed=[dict(entry=a,**{k:v for k,v in rec.items() if k!='entry'}) for a,rec in sorted(followed.items())],
        windows=windows,callsites=callsites,passes=passes,slot_membership=slot_membership,vtables=vts,
        rodata=[rodata[k] for k in sorted(rodata)],
        limits=['Two caller levels only, <=40 followed functions, FDE windows capped at 0x1000 bytes.',
                'Direct BL/B references and ADRP+ADD pairs only; no indirect flow, no execution.',
                'Strings are original .rodata bytes read by resolved address, not symbols.',
                'No class names, no runtime arrays, no manager instance.'])
def main():
    p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True);a=p.parse_args();r=recover(a.xapk)
    out=ROOT/'reverse-engineering/raw/owner130/probe.json.gz';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(gzip.compress((json.dumps(r,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
    print('saved',out,'followed',len(r['followed']),'windows',len(r['windows']),'callsites',len(r['callsites']),'slots',len(r['slot_membership']),'rodata',len(r['rodata']))
if __name__=='__main__':main()
