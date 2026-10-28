"""Cycle 134 stage 1: the leaf layer of the refresh / producer chain.

Cycle 133 decoded the builder helpers but could only name their callees as targets. This stage
recovers those leaves from the pinned original bytes: the slot `+0xe0` implementation the per-node
producer tail-branches into (`6d017c`), the per-record word folded into the `+0x4b8` maximum
(`6d14d4`), the three steps of the full refresh `6b92c4`, the three partners of `6b6d60`, the
post-bind step `6b22c8`, and the handle / vector helpers behind them.

Bytes only: nothing is executed, no symbol and no class name is used.
"""
import argparse,bisect,gzip,hashlib,io,json,struct,zipfile
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
XAPK_SHA='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
CLUSTER=(0x6b0000,0x6c0000)
SEEDS=(0x6d017c,0x6d14d4,0x6b2050,0x6b6dec,0x6b6fdc,0x6b82e8,0x6b2a0c,0x6b832c,
       0x6b22c8,0x572a9c,0x572834,0x5707c4,0x576c70,0x5770fc,0x49fe68)
FOLLOW_CAP=24
CAP=0x800
STR_CAP=64
MAX_STR=24

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
    return (w>>5)&31,((w>>10)&0xFFF)<<(12 if w&(1<<22) else 0)
def ldr_off(w):
    if w&0xFFC00000==0xF9400000:return (w&31,(w>>5)&31,((w>>10)&0xFFF)*8)
    if w&0xFFC00000==0xB9400000:return (w&31,(w>>5)&31,((w>>10)&0xFFF)*4)
    if w&0xFFE00C00 in (0xF8400000,0xF8400400,0xF8400C00):return (w&31,(w>>5)&31,sg((w>>12)&0x1FF,9))
    if w&0xFFE00C00 in (0xB8400000,0xB8400400,0xB8400C00):return (w&31,(w>>5)&31,sg((w>>12)&0x1FF,9))
    return None
def store_off(w):
    if w&0xFFC00000==0xF9000000:return (w&31,((w>>5)&31)&31,((w>>10)&0xFFF)*8)
    if w&0xFFC00000==0xB9000000:return (w&31,(w>>5)&31,((w>>10)&0xFFF)*4)
    if w&0xFFE00C00 in (0xF8000000,0xF8000400,0xF8000C00):return (w&31,(w>>5)&31,sg((w>>12)&0x1FF,9))
    if w&0xFFE00C00 in (0xB8000000,0xB8000400,0xB8000C00):return (w&31,(w>>5)&31,sg((w>>12)&0x1FF,9))
    return None
def is_blr(w):return w&0xFFFFFC1F==0xD63F0000
def is_ret(w):return w==0xD65F03C0

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
    phoff=struct.unpack_from('<Q',b,32)[0];phsize,phnum=struct.unpack_from('<HH',b,54)
    segs=[]
    for i in range(phnum):
        p=struct.unpack_from('<IIQQQQQQ',b,phoff+i*phsize)
        if p[0]==1:segs.append(dict(flags=p[1],offset=p[2],va=p[3],file_size=p[5],memory_size=p[6]))
    def offset(a):
        s=next(s for s in segs if s['va']<=a<s['va']+s['file_size']);return s['offset']+a-s['va']
    def readable(a):return any(s['va']<=a<s['va']+min(s['file_size'],s['memory_size']) for s in segs)
    def in_text(a):return any(s['flags']&1 and s['va']<=a<s['va']+s['file_size'] for s in segs)
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
    queue=[dict(entry=s,group='seed',depth=0) for s in SEEDS]
    seen={}
    order=[]
    while queue:
        rec=queue.pop(0)
        e=rec['entry']
        if e in seen or len(seen)>=FOLLOW_CAP:continue
        if e not in unwind:continue
        length=min(unwind[e],CAP)
        try:pos=offset(e)
        except StopIteration:continue
        code=b[pos:pos+length]
        words=list(struct.unpack_from('<%dI'%(len(code)//4),code))
        calls=[];strings=[];fields=[];dispatch=[]
        for i,w in enumerate(words):
            pc=e+i*4
            t=bl_target(w,pc)
            if t is not None:
                intra=e<=t<e+unwind[e]
                calls.append(dict(pc=pc,target=t,kind='bl' if w>>31 else 'b',intra=intra,
                                  in_cluster=(not intra) and CLUSTER[0]<=t<CLUSTER[1]))
                if (not intra) and CLUSTER[0]<=t<CLUSTER[1] and t not in seen and len(seen)+len(queue)<FOLLOW_CAP:
                    queue.append(dict(entry=t,group='cluster_callee',depth=1,parent=e))
                continue
            a=adrp(w,pc)
            if a:
                for k in range(1,5):
                    if i+k>=len(words):break
                    add=add_imm(words[i+k])
                    if add and add[0]==a[0]:
                        tgt=a[1]+add[1]
                        if readable(tgt) and not in_text(tgt) and len(strings)<MAX_STR:
                            q=offset(tgt);raw=b[q:q+STR_CAP];end=raw.find(b'\x00')
                            raw=raw[:end if end>=0 else STR_CAP]
                            if len(raw)>=3 and all(32<=x<127 for x in raw):
                                strings.append(dict(va=tgt,ascii=raw.decode('latin-1'),pc=pc))
                        break
            ld=ldr_off(w);st=store_off(w)
            if ld and ld[1] in (0,19,20) and abs(ld[2])<0x800:
                fields.append(dict(pc=pc,kind='load',base=f'x{ld[1]}',offset=ld[2]))
            if st and st[1] in (0,19,20) and abs(st[2])<0x800:
                fields.append(dict(pc=pc,kind='store',base=f'x{st[1]}',offset=st[2]))
            if ld:
                rt,rn,off=ld
                for k in range(1,9):
                    if i+k>=len(words):break
                    if is_blr(words[i+k]) and ((words[i+k]>>5)&31)==rt:
                        dispatch.append(dict(ldr_pc=pc,blr_pc=e+(i+k)*4,slot=off,base_reg=f'x{rn}'))
                        break
        seen[e]=dict(entry=e,group=rec['group'],depth=rec['depth'],parent=rec.get('parent'),
                     extent=unwind[e],window_bytes=len(code),file_offset=pos,hex=code.hex(),
                     ret_count=sum(1 for w in words if is_ret(w)),
                     calls=calls,strings=strings,fields=fields,dispatch=dispatch)
        order.append(e)
    return dict(provisional=True,xapk_sha256=XAPK_SHA,apk_entry=apk,library_entry=lib,
        libunity_sha256=sha(b),libunity_size=len(b),tool_sha256=sha(Path(__file__).read_bytes()),
        cluster=list(CLUSTER),seeds=list(SEEDS),order=order,
        functions=[seen[e] for e in order],
        limits=['One follow level for in-cluster callees, at most %d functions, bodies capped at 0x%x.'%(FOLLOW_CAP,CAP),
                'Only BL/B and ADRP+ADD are decoded; register-indirect flow is not followed.',
                'Strings are original .rodata bytes read by resolved address.',
                'Field rows are raw bracket accesses on x0/x19/x20 and are not class evidence.',
                'No instruction was executed; no symbol or class name is used.'])

def main():
    p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True);a=p.parse_args()
    out=ROOT/'reverse-engineering/raw/owner134/probe.json.gz';out.parent.mkdir(parents=True,exist_ok=True)
    try:r=recover(a.xapk)
    except Exception:
        import traceback
        (out.parent/'diagnostic.json').write_text(json.dumps(dict(error=traceback.format_exc()),indent=1)+'\n')
        raise
    out.write_bytes(gzip.compress((json.dumps(r,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
    print('saved',out,'functions',len(r['functions']),
          'calls',sum(len(f['calls']) for f in r['functions']),
          'cluster_calls',sum(1 for f in r['functions'] for c in f['calls'] if c['in_cluster']),
          'strings',sum(len(f['strings']) for f in r['functions']),
          'dispatch',sum(len(f['dispatch']) for f in r['functions']))
    for f in r['functions']:
        print(f"  {f['entry']:#x} {f['group']} ext={f['extent']:#x} win={f['window_bytes']} calls={len(f['calls'])} str={[s['ascii'] for s in f['strings']][:4]}")

if __name__=='__main__':main()
