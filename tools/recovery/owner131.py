"""Cycle 131 stage 1: who can reach and dispatch the animator-side vtable slots.

Pure static scan of the original libunity.so bytes. One bounded question: is there a
direct (non-virtual) code path that loads one of the four recovered vtable slots
{2, 3, 31, 33} and branches to it, and which FDE owns it?

No instruction is executed and no symbol is used.
"""
import argparse,bisect,gzip,hashlib,io,json,struct,zipfile
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
XAPK_SHA='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
FAMILY=(0x10b0c80,0x10b0f98,0x10b1100,0x10b1130,0x10b0f30,0x10b1240,0x10b1420,0x10b1150,0x10b1330)
SLOTS=(2,3,31,33)
SLOT_OFFSETS={2:0x10,3:0x18,31:0xf8,33:0x108}
GLOBALS=(0x10ecb08,0x10e18b0,0x10e19c8,0x10e19d0,0x10e18f8,0x10e18b8,0x10ec000)
CLUSTER=(0x6b0000,0x6c0000)
MAX_Q=64;MAX_OTHER=12;MAX_CALLERS=32;WIN=0x40

def sha(b):return hashlib.sha256(b).hexdigest()
def sg(v,n):return v-(1<<n) if v&(1<<(n-1)) else v

def ldr_imm(w):
    """(rt, rn, offset, width) for LDR immediate forms, else None."""
    if w&0xFFC00000==0xF9400000:return (w&31,(w>>5)&31,((w>>10)&0xFFF)*8,8)
    if w&0xFFC00000==0xB9400000:return (w&31,(w>>5)&31,((w>>10)&0xFFF)*4,4)
    if w&0xFFE00C00 in (0xF8400000,0xF8400400,0xF8400C00):return (w&31,(w>>5)&31,sg((w>>12)&0x1FF,9),8)
    if w&0xFFE00C00 in (0xB8400000,0xB8400400,0xB8400C00):return (w&31,(w>>5)&31,sg((w>>12)&0x1FF,9),4)
    return None

def is_blr(w):return w&0xFFFFFC1F==0xD63F0000
def blr_reg(w):return (w>>5)&31
def bl_target(w,pc):
    if w&0x7C000000!=0x14000000:return None
    return pc+(sg(w&0x3FFFFFF,26)<<2)
def adrp(w,pc):
    if w&0x9F000000!=0x90000000:return None
    return (w&31,(pc&~0xFFF)+(sg(((w>>5)&0x7FFFF)<<2|((w>>29)&3),21)<<12))
def add_imm(w):
    if w&0xFFC00000!=0x91000000:return None
    return ((w>>5)&31,w&31,((w>>10)&0xFFF)<<(12 if w&(1<<22) else 0))

def elf_segments(b):
    assert b[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',b,18)[0]==183
    phoff=struct.unpack_from('<Q',b,32)[0];phsize,phnum=struct.unpack_from('<HH',b,54)
    segs=[]
    for i in range(phnum):
        p=struct.unpack_from('<IIQQQQQQ',b,phoff+i*phsize)
        if p[0]==1:segs.append(dict(flags=p[1],offset=p[2],va=p[3],file_size=p[5],memory_size=p[6]))
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
    segs,phoff,phsize,phnum=elf_segments(b)
    def offset(addr):
        s=next(s for s in segs if s['va']<=addr<s['va']+s['file_size']);return s['offset']+addr-s['va']
    def in_text(a):return any(s['flags']&1 and s['va']<=a<s['va']+s['file_size'] for s in segs)
    text=[s for s in segs if s['flags']&1]
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
    slots=defaultdict(lambda:dict(matches=0,with_blr=0,qualified=[],other=[]))
    vtable_refs=defaultdict(list);globals_refs=defaultdict(list)
    for s in text:
        words=list(struct.unpack_from('<%dI'%(s['file_size']//4),b,s['offset']))
        base=s['va']
        for i,w in enumerate(words):
            pc=base+i*4
            dec=ldr_imm(w)
            if dec:
                rt,rn,off,width=dec
                if width==8:
                    for slot,moff in SLOT_OFFSETS.items():
                        if off!=moff:continue
                        slots[slot]['matches']+=1
                        blr_pc=None
                        for k in range(1,9):
                            if i+k>=len(words):break
                            if is_blr(words[i+k]) and blr_reg(words[i+k])==rt:blr_pc=base+(i+k)*4;break
                        if blr_pc is None:continue
                        slots[slot]['with_blr']+=1
                        kind='unknown'
                        for k in range(1,7):
                            if i-k<0:break
                            prev=ldr_imm(words[i-k])
                            if prev and prev[0]==rn and prev[1]==0 and prev[3]==8:kind='vptr_from_x0';break
                            a=adrp(words[i-k],base+(i-k)*4)
                            if a and a[0]==rn:kind='adrp_base';break
                        rec=dict(ldr_pc=pc,blr_pc=blr_pc,reg=rt,base_reg=rn,base_kind=kind,owner=owner(pc))
                        if kind!='unknown' or (owner(pc) and CLUSTER[0]<=owner(pc)<CLUSTER[1]):
                            if len(slots[slot]['qualified'])<MAX_Q:
                                try:rec['window_hex']=b[offset(pc-4):offset(pc-4)+WIN].hex()
                                except StopIteration:rec['window_hex']=''
                                slots[slot]['qualified'].append(rec)
                        elif len(slots[slot]['other'])<MAX_OTHER:
                            slots[slot]['other'].append(rec)
            a=adrp(w,pc)
            if a:
                rd,page=a
                for k in range(1,5):
                    if i+k>=len(words):break
                    add=add_imm(words[i+k])
                    if add and add[0]==rd:
                        tgt=page+add[2]
                        if tgt in FAMILY and len(vtable_refs[tgt])<MAX_Q:
                            vtable_refs[tgt].append(dict(pc=pc,add_pc=base+(i+k)*4,owner=owner(pc),
                                                         hex=b[offset(pc):offset(pc)+8].hex(),
                                                         add_hex=b[offset(base+(i+k)*4):offset(base+(i+k)*4)+4].hex()))
                        elif tgt in GLOBALS and len(globals_refs[tgt])<MAX_Q:
                            globals_refs[tgt].append(dict(pc=pc,add_pc=base+(i+k)*4,owner=owner(pc),
                                                           hex=b[offset(pc):offset(pc)+8].hex(),
                                                           add_hex=b[offset(base+(i+k)*4):offset(base+(i+k)*4)+4].hex()))
                        break
                    ld=ldr_imm(words[i+k])
                    if ld and ld[1]==rd and ld[3]==8:
                        tgt=page+ld[2]
                        if tgt in GLOBALS and len(globals_refs[tgt])<MAX_Q:
                            globals_refs[tgt].append(dict(pc=pc,ldr_pc=base+(i+k)*4,owner=owner(pc),hex=b[offset(pc):offset(pc)+12].hex()))
                        break
    owners=sorted({r['owner'] for slot in slots for r in slots[slot]['qualified']+slots[slot]['other'] if r['owner']})
    follow=owners[:MAX_CALLERS]
    windows=[]
    for o in follow:
        length=min(unwind.get(o,0x600),0x800)
        try:pos=offset(o)
        except StopIteration:continue
        windows.append(dict(va=o,file_offset=pos,extent=unwind.get(o),hex=b[pos:pos+length].hex()))
    target_set=set(follow);callers=[];seen=Counter();capped=[]
    for s in text:
        words=list(struct.unpack_from('<%dI'%(s['file_size']//4),b,s['offset']))
        base=s['va']
        for i,w in enumerate(words):
            t=bl_target(w,base+i*4)
            if t is None or t not in target_set:continue
            if seen[t]>=64:capped.append(t);continue
            seen[t]+=1
            callers.append(dict(callee=t,pc=base+i*4,kind='bl' if w>>31 else 'b',caller=owner(base+i*4)))
    return dict(provisional=True,xapk_sha256=XAPK_SHA,apk_entry=apk,library_entry=lib,libunity_sha256=sha(b),
        libunity_size=len(b),tool_sha256=sha(Path(__file__).read_bytes()),
        text=[dict(va=s['va'],size=s['file_size']) for s in text],
        family=list(FAMILY),slots=list(SLOTS),slot_offsets={str(k):v for k,v in SLOT_OFFSETS.items()},
        globals=[hex(g) for g in GLOBALS],cluster=list(CLUSTER),
        sites={str(k):dict(matches=v['matches'],with_blr=v['with_blr'],
                           qualified_count=len(v['qualified']),qualified=v['qualified'],
                           other_count=len(v['other']),other=v['other']) for k,v in slots.items()},
        vtable_refs={hex(k):v for k,v in vtable_refs.items()},
        global_refs={hex(k):v for k,v in globals_refs.items()},
        owners=[dict(entry=o,extent=unwind.get(o)) for o in owners],
        windows=windows,callers=callers,caller_capped=sorted(set(capped)),
        limits=['One .text pass only; sequences longer than 8 words between the slot load and BLR are missed.',
                'Base-register provenance looks back at most 6 words and only for LDR-from-x0 or ADRP.',
                'Qualified sites = known base provenance or owner inside 0x6b0000..0x6c0000; others are sampled.',
                'Loads of slots 2 and 3 are very common; match counts are exact, stored rows are capped.',
                'No instruction was executed; no symbol or class name is used.'])

def main():
    p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True);a=p.parse_args()
    out=ROOT/'reverse-engineering/raw/owner131/probe.json.gz';out.parent.mkdir(parents=True,exist_ok=True)
    try:r=recover(a.xapk)
    except Exception:
        import traceback
        (out.parent/'diagnostic.json').write_text(json.dumps(dict(error=traceback.format_exc()),indent=1)+'\n')
        raise
    out.write_bytes(gzip.compress((json.dumps(r,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
    print('saved',out,'matches',{k:v['matches'] for k,v in r['sites'].items()},
          'with_blr',{k:v['with_blr'] for k,v in r['sites'].items()},
          'qualified',{k:v['qualified_count'] for k,v in r['sites'].items()},
          'owners',len(r['owners']),'vtable_refs',sum(len(v) for v in r['vtable_refs'].values()),
          'global_refs',sum(len(v) for v in r['global_refs'].values()),'callers',len(r['callers']))

if __name__=='__main__':main()
