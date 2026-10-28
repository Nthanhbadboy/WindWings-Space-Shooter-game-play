"""Cycle 130 stage 2: upward closure of the update/flush callers and the global registry.

Seeds the batch/flush entries and follows their callers two levels up, captures the
global containers those callers use, and resolves which vtables hold the trigger entries.
Static bytes only: no execution, no symbols, no class names.
"""
import argparse,bisect,gzip,hashlib,io,json,struct,zipfile
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
XAPK_SHA='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
SEEDS=(0x6b27dc,0x6b3e78,0x6b4820,0x6b72e4,0x6b1c5c,0x6b9ac4,0x6b1c98,0x6b2258,0x6b4bfc)
GLOBALS=(0x10ecb08,0x10e1000+0x9c8,0x10e1000+0x9d0,0x10e1000+0x8f8,0x10e1000+0x8b0,0x10e1000+0x8b8)
SLOT_TARGETS=(0x6b1c5c,0x6b1c98,0x6b2258,0x6b4bfc,0x6b1914,0x6b1a00,0x6b947c,0x6b6ab8)
VTABLES=(0x10b0c80,)
MAX_CALLERS=32
MAX_FUNCS=32;MAX_DEPTH=2;MAX_SITES=8;CAP_WIN=0x800;STR_CAP=48
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
    def scan(targets,cap=MAX_SITES):
        refs=defaultdict(list);trunc=set();glob=[]
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
                elif word&0x9f000000==0x90000000:
                    rd=word&31
                    imm=signed(((word>>5)&0x7ffff)<<2|((word>>29)&3),21)<<12;page=(pc&~4095)+imm
                    for nxt in range(pos+4,min(pos+36,s['offset']+s['file_size']-3),4):
                        op=struct.unpack_from('<I',b,nxt)[0]
                        if op&0xffc00000==0x91000000 and ((op>>5)&31)==rd:
                            tgt=page+((op>>10)&4095)
                            if tgt in GLOBALS:glob.append(dict(target=tgt,pc=pc,add_va=va(nxt),hex=b[pos:nxt+4].hex()))
                            break
        return refs,trunc,glob
    followed={};frontier=[];callsites=[];passes=[]
    # seed: find callers of the seeds (depth 1), then their callers (depth 2)
    targets=set(SEEDS);depth=1
    while targets and depth<=MAX_DEPTH and len(followed)<MAX_FUNCS:
        refs,trunc,glob=scan(targets)
        passes.append(dict(depth=depth,targets=sorted(targets),sites=sum(len(v) for v in refs.values()),truncated=sorted(trunc)))
        nxt=set()
        for t in targets:
            for s in refs.get(t,[]):
                callsites.append(dict(target=t,pc=s['pc'],kind=s['kind'],word_hex=s['word_hex']))
                o=owner(s['pc'])
                if o is None or o in followed or len(followed)>=MAX_FUNCS:continue
                if o not in followed and o not in nxt and len(followed)+len(nxt)<MAX_FUNCS:
                    nxt.add(o);followed[o]=dict(entry=o,depth=depth,seed=t,extent_source='original_FDE' if o in unwind else 'bounded_window',unwind=unwind.get(o))
        targets=nxt;depth+=1
    windows=[];seen=set()
    for a in sorted(followed):
        rec=followed[a]['unwind'];length=min((rec['end']-a) if rec else 0x600,CAP_WIN)
        if a in seen:continue
        try:pos=offset(a);assert offset(a+length-1)==pos+length-1
        except (StopIteration,AssertionError):continue
        seen.add(a);windows.append(dict(va=a,file_offset=pos,extent_source=followed[a]['extent_source'],hex=b[pos:pos+length].hex()))
    globals_refs=[]
    # second pass over the followed windows only: which of them touch the global containers
    for w in windows:
        code=bytes.fromhex(w['hex']);base=w['va']
        for i in range(0,len(code)-4,4):
            word=struct.unpack_from('<I',code,i)[0]
            if word&0x9f000000!=0x90000000:continue
            rd=word&31;pc=base+i
            imm=signed(((word>>5)&0x7ffff)<<2|((word>>29)&3),21)<<12;page=(pc&~4095)+imm
            for k in range(i+4,min(i+36,len(code)-3),4):
                op=struct.unpack_from('<I',code,k)[0]
                if op&0xffc00000==0x91000000 and ((op>>5)&31)==rd:
                    tgt=page+((op>>10)&4095)
                    if tgt in GLOBALS:globals_refs.append(dict(target=tgt,pc=pc,add_va=base+k,hex=code[i:k+4].hex(),window=w['va']))
                    break
    slot_membership=[]
    for t in SLOT_TARGETS:
        for rec in rela_by_addend.get(t,[]):
            tb=table(rela_index,rec['address'],in_text)
            if tb:slot_membership.append(dict(target=t,**tb,rela_file_offset=rec['file_offset']))
    return dict(provisional=True,xapk_sha256=XAPK_SHA,apk_entry=apk,library_entry=lib,libunity_sha256=sha(b),
        libunity_size=len(b),tool_sha256=sha(Path(__file__).read_bytes()),segments=segments,seeds=list(SEEDS),
        globals=[hex(g) for g in GLOBALS],followed=[dict(entry=a,**{k:v for k,v in rec.items() if k!='entry'}) for a,rec in sorted(followed.items())],
        windows=windows,callsites=callsites,passes=passes,slot_membership=slot_membership,global_refs=globals_refs,
        limits=['Caller closure only, depth<=2, <=32 followed functions, windows capped at 0x800 bytes.',
                'Direct BL/B references and ADRP+ADD pairs only; no indirect flow, no execution.',
                'Global addresses are raw VA targets of ADRP+ADD pairs, not container contents.',
                'No class names, no runtime arrays, no scheduler instance.'])

def table(rela_index,addr,in_text):
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

def main():
    p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True);a=p.parse_args();r=recover(a.xapk)
    out=ROOT/'reverse-engineering/raw/owner130b/probe.json.gz';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(gzip.compress((json.dumps(r,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
    print('saved',out,'followed',len(r['followed']),'windows',len(r['windows']),'callsites',len(r['callsites']),'globals',len(r['global_refs']),'slots',len(r['slot_membership']))
if __name__=='__main__':main()
