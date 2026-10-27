"""Cycle 132 stage 1: do the dispatch-candidate owners actually touch the animator?

Cycle 131 found 16 distinct FDE owners of `ldr xN,[vptr,#0xf8]; blr xN` sites and 10 owners of
references to the batch container `0x10ecb08`, but none of the slot-31 owners sat inside the
animator cluster. This stage recovers the original bytes of all of those owners, plus the one
in-cluster dispatch site (owner `6b7d58`, slot `+0x108`), and answers with bytes only:

  * which direct `BL`/`B` targets of each owner land inside `0x6b0000..0x6c0000`,
  * which owners touch the animator's signature field offsets,
  * which vtable slots each owner dispatches and where the vptr comes from,
  * what `6b7d58` does around its `+0x108` dispatch.

No instruction is executed; no symbol or class name is used.
"""
import argparse,bisect,gzip,hashlib,io,json,struct,zipfile
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
XAPK_SHA='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
CLUSTER=(0x6b0000,0x6c0000)
SEEDS_31=(0x47f5f0,0x555524,0x5fc17c,0x60a324,0x66cde8,0x6f29c0,0x8b3644,0x8b5e5c,
          0x8e1ecc,0x90adc4,0xb9db1c,0xba0980,0xe4515c,0xed70bc,0xef4c68,0xf1d6bc)
SEEDS_BATCH=(0x5d4fd0,0x6a74b8,0x6a88f0,0x6a9674,0x6b23b8,0x6b27dc,0x6b9b90,0x94cf10,0xb6aaa8,0xb6ab88)
SEEDS_EXTRA=(0x6b7d58,)
GLOBALS=(0x10ecb08,0x10e18b0,0x10e19c8,0x10e19d0,0x10e18f8,0x10e18b8)
FIELDS=(0x188,0x194,0x19c,0x1b8,0x208,0x488,0x608,0x618,0x4a8,0x498)
SLOT_OFFSETS={2:0x10,3:0x18,10:0x50,31:0xf8,33:0x108}
CAP=0x1000

def sha(b):return hashlib.sha256(b).hexdigest()
def sg(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def bl_target(w,pc):
    if w&0x7C000000!=0x14000000:return None
    return pc+(sg(w&0x3FFFFFF,26)<<2)
def adrp(w,pc):
    if w&0x9F000000!=0x90000000:return None
    return (w&31,(pc&~0xFFF)+(sg(((w>>5)&0x7FFFF)<<2|((w>>29)&3),21)<<12))
def add_imm(w):
    if w&0xFFC00000!=0x91000000:return None
    return ((w>>5)&31,(w>>10)&0xFFF)
def ldr_off(w):
    """(rt, rn, offset) for the 64-bit LDR immediate forms, else None."""
    if w&0xFFC00000==0xF9400000:return (w&31,(w>>5)&31,((w>>10)&0xFFF)*8)
    if w&0xFFE00C00 in (0xF8400000,0xF8400400,0xF8400C00):return (w&31,(w>>5)&31,sg((w>>12)&0x1FF,9))
    return None
def is_blr(w):return w&0xFFFFFC1F==0xD63F0000
def blr_reg(w):return (w>>5)&31

def parse(b):
    assert b[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',b,18)[0]==183
    phoff=struct.unpack_from('<Q',b,32)[0];phsize,phnum=struct.unpack_from('<HH',b,54)
    segs=[]
    for i in range(phnum):
        p=struct.unpack_from('<IIQQQQQQ',b,phoff+i*phsize)
        if p[0]==1:segs.append(dict(flags=p[1],offset=p[2],va=p[3],file_size=p[5]))
    return segs,phoff,phsize,phnum

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
    segs,phoff,phsize,phnum=parse(b)
    def offset(addr):
        s=next(s for s in segs if s['va']<=addr<s['va']+s['file_size']);return s['offset']+addr-s['va']
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
    seeds=[]
    for group,name in ((SEEDS_31,'slot31_dispatch_owner'),(SEEDS_BATCH,'batch_container_owner'),(SEEDS_EXTRA,'incluster_slot33_owner')):
        for s in group:
            if all(x['entry']!=s for x in seeds):seeds.append(dict(entry=s,group=name))
    rows=[]
    for rec in seeds:
        e=rec['entry'];length=min(unwind.get(e,0x600),CAP)
        try:pos=offset(e)
        except StopIteration:continue
        code=b[pos:pos+length]
        words=list(struct.unpack_from('<%dI'%(len(code)//4),code))
        calls=[];glob=[];fields=defaultdict(int);dispatch=[]
        for i,w in enumerate(words):
            pc=e+i*4
            t=bl_target(w,pc)
            if t is not None:
                calls.append(dict(pc=pc,target=t,kind='bl' if w>>31 else 'b',
                                  in_cluster=CLUSTER[0]<=t<CLUSTER[1]))
                continue
            a=adrp(w,pc)
            if a:
                for k in range(1,5):
                    if i+k>=len(words):break
                    add=add_imm(words[i+k])
                    if add and add[0]==a[0]:
                        tgt=a[1]+add[1]
                        if tgt in GLOBALS:glob.append(dict(pc=pc,add_pc=e+(i+k)*4,target=tgt,hex=code[i*4:(i+k+1)*4].hex()))
                        break
                continue
            ld=ldr_off(w)
            if ld:
                rt,rn,off=ld
                if off in FIELDS:fields[off]+=1
                for slot,moff in SLOT_OFFSETS.items():
                    if off!=moff:continue
                    blr_pc=None
                    for k in range(1,9):
                        if i+k>=len(words):break
                        if is_blr(words[i+k]) and blr_reg(words[i+k])==rt:blr_pc=e+(i+k)*4;break
                    if blr_pc is None:continue
                    prov='unknown';prov_pc=None
                    for k in range(1,7):
                        if i-k<0:break
                        p2=ldr_off(words[i-k])
                        if p2 and p2[0]==rn:
                            prov=f'vptr_from_x{p2[1]}';prov_pc=e+(i-k)*4;break
                        a2=adrp(words[i-k],e+(i-k)*4)
                        if a2 and a2[0]==rn:prov='adrp_base';prov_pc=e+(i-k)*4;break
                    dispatch.append(dict(slot=slot,ldr_pc=pc,blr_pc=blr_pc,reg=rt,base_reg=rn,
                                         base_kind=prov,provenance_pc=prov_pc,
                                         window_hex=code[max(0,i*4-4):max(0,i*4-4)+0x30].hex()))
        rows.append(dict(entry=e,group=rec['group'],extent=unwind.get(e),window_bytes=len(code),
                         file_offset=pos,hex=code.hex(),calls=calls,
                         cluster_calls=[c for c in calls if c['in_cluster']],
                         globals=glob,fields={hex(k):v for k,v in sorted(fields.items())},
                         dispatch=dispatch,
                         callers=None))
    wanted={r['entry']:[] for r in rows};capped=set()
    for s in segs:
        if not s['flags']&1:continue
        words=list(struct.unpack_from('<%dI'%(s['file_size']//4),b,s['offset']))
        base=s['va']
        for i,w in enumerate(words):
            pc=base+i*4
            t=bl_target(w,pc)
            if t is None or t not in wanted:continue
            if len(wanted[t])>=32:capped.add(t);continue
            wanted[t].append(dict(pc=pc,kind='bl' if w>>31 else 'b',caller=owner(pc)))
    for r in rows:r['callers']=wanted[r['entry']]
    for r in rows:r['callers_capped']=r['entry'] in capped
    return dict(provisional=True,xapk_sha256=XAPK_SHA,apk_entry=apk,library_entry=lib,libunity_sha256=sha(b),
        libunity_size=len(b),tool_sha256=sha(Path(__file__).read_bytes()),
        cluster=list(CLUSTER),fields=list(FIELDS),slot_offsets={str(k):v for k,v in SLOT_OFFSETS.items()},
        globals=[hex(g) for g in GLOBALS],seeds=[dict(entry=x['entry'],group=x['group']) for x in seeds],
        owners=rows,
        callers_total=sum(len(r['callers']) for r in rows),
        callers_capped=sorted(capped),
        limits=['Bodies come from the original FDE extents, capped at 0x1000 bytes.',
                'Direct BL/B only; indirect flow and virtual dispatch are not followed.',
                'Field-offset hits are generic loads/stores and are not class evidence on their own.',
                'Caller lists are capped at 32 per seed.'])

def main():
    p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True);a=p.parse_args()
    out=ROOT/'reverse-engineering/raw/owner132/probe.json.gz';out.parent.mkdir(parents=True,exist_ok=True)
    try:r=recover(a.xapk)
    except Exception:
        import traceback
        (out.parent/'diagnostic.json').write_text(json.dumps(dict(error=traceback.format_exc()),indent=1)+'\n')
        raise
    out.write_bytes(gzip.compress((json.dumps(r,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
    print('saved',out,'owners',len(r['owners']),
          'cluster_calls',sum(len(o['cluster_calls']) for o in r['owners']),
          'globals',sum(len(o['globals']) for o in r['owners']),
          'dispatch',sum(len(o['dispatch']) for o in r['owners']))

if __name__=='__main__':main()
