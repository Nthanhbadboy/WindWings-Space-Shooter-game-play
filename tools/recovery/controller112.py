"""Original libunity field/type-string and AArch64 address-reference probe, not schema proof."""
import argparse,gzip,hashlib,io,json,struct,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
XAPK_SHA='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def recover(xapk):
    data=xapk.read_bytes();assert sha(data)==XAPK_SHA;found=[]
    with zipfile.ZipFile(io.BytesIO(data)) as outer:
        for name in outer.namelist():
            if not name.endswith('.apk'):continue
            with zipfile.ZipFile(io.BytesIO(outer.read(name))) as z:
                path='lib/arm64-v8a/libunity.so'
                if path in z.namelist():found.append((name,path,z.read(path)))
    assert len(found)==1;apk,entry,b=found[0];assert b[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',b,18)[0]==183
    phoff=struct.unpack_from('<Q',b,32)[0];ps,pc=struct.unpack_from('<HH',b,54);segments=[]
    for i in range(pc):
        p=struct.unpack_from('<IIQQQQQQ',b,phoff+i*ps)
        if p[0]==1:segments.append(dict(flags=p[1],offset=p[2],va=p[3],file_size=p[5],memory_size=p[6]))
    def va_at(off):
        s=next(s for s in segments if s['offset']<=off<s['offset']+s['file_size']);return s['va']+off-s['offset']
    source=ROOT/'reverse-engineering/raw/controller109/index.json';idx=json.loads(source.read_bytes());schema=next(iter(idx['schemas'].values()));names=set(['AnimatorController','RuntimeAnimatorController','ControllerConstant'])
    def visit(n):
        names.add(n['type']);names.add(n['name'])
        for c in n['children']:visit(c)
    visit(schema);names|={'m_InterruptionSource','m_OrderedInterruption','m_CanTransitionToSelf','m_Atomic','Transfer','AnimationClip'}
    # Exact NUL-terminated byte pattern occurrences; predecessor need not be NUL (suffix pooling).
    strings=[];wanted={}
    for name in sorted(names):
        needle=name.encode()+b'\0';positions=[];start=0
        while True:
            pos=b.find(needle,start)
            if pos<0:break
            try:v=va_at(pos)
            except StopIteration:start=pos+1;continue
            positions.append(dict(file_offset=pos,va=v,hex=needle.hex(),preceding_hex=b[max(0,pos-16):pos].hex()));wanted[v]=name;start=pos+1
        strings.append(dict(text=name,occurrences=positions))
    # Enumerate adjacent (up to8 instructions) ADRP+ADD/ADR literal references. Candidate only.
    refs=[]
    def signed(v,bits):return v-(1<<bits) if v&(1<<(bits-1)) else v
    for s in segments:
        if not s['flags']&1:continue
        lo=s['offset'];hi=lo+s['file_size']
        for off in range(lo,hi-3,4):
            word=struct.unpack_from('<I',b,off)[0];pc=s['va']+off-lo
            if word&0x9f000000==0x10000000:
                imm=signed(((word>>5)&0x7ffff)<<2|((word>>29)&3),21);target=pc+imm
                if target in wanted:refs.append(dict(kind='adr',field=wanted[target],target=target,va=pc,file_offset=off,word_hex=b[off:off+4].hex()))
            if word&0x9f000000!=0x90000000:continue
            rd=word&31;imm=signed(((word>>5)&0x7ffff)<<2|((word>>29)&3),21)<<12;page=(pc&~4095)+imm
            for nxt in range(off+4,min(off+36,hi-3),4):
                op=struct.unpack_from('<I',b,nxt)[0]
                if op&0xffc00000==0x91000000 and ((op>>5)&31)==rd:
                    target=page+((op>>10)&4095)
                    if target in wanted:refs.append(dict(kind='adrp_add_candidate',field=wanted[target],target=target,va=pc,add_va=s['va']+nxt-lo,file_offset=off,add_file_offset=nxt,pair_hex=b[off:nxt+4].hex()))
    # Bounded original machine-code windows, no inferred function boundaries.
    windows=[]
    for ref in refs:
        if ref['field'] not in {c['name'] for c in schema['children']}|{'AnimatorController','ControllerConstant','m_InterruptionSource','m_OrderedInterruption'}:continue
        off=ref['file_offset'];s=next(s for s in segments if s['offset']<=off<s['offset']+s['file_size']);lo=max(s['offset'],off-256);hi=min(s['offset']+s['file_size'],off+512);key=(lo,hi)
        if any(w['file_offset']==lo for w in windows):continue
        windows.append(dict(file_offset=lo,va=s['va']+lo-s['offset'],hex=b[lo:hi].hex()))
    # Preserve original native generator region and common metadata sinks for bounded review.
    ranges=[(0xb7e1bc,0xb80978),(0x6af000,0x6b0200),(0x5eb400,0x5eb900),(0x3b4200,0x3b4400),(0x3da000,0x3da300),(0x5e0800,0x5e0e80),(0x6df800,0x6dfc00),(0x6e0800,0x6e0c00)]
    def offset_at(va,width=1):
        seg=next(s for s in segments if s['va']<=va and va+width<=s['va']+s['file_size']);return seg['offset']+va-seg['va']
    native=[]
    for lo,hi in ranges:
        p=offset_at(lo,hi-lo);native.append(dict(va=lo,file_offset=p,hex=b[p:p+hi-lo].hex()))
    # Original RELA records, then follow only generator-referenced address cells.
    shoff=struct.unpack_from('<Q',b,40)[0];ss,sc=struct.unpack_from('<HH',b,58);relas={}
    for i in range(sc):
        h=struct.unpack_from('<IIQQQQIIQQ',b,shoff+i*ss)
        if h[1]!=4:continue
        for pos in range(h[4],h[4]+h[5],h[9] or 24):
            address,kind,addend=struct.unpack_from('<QQq',b,pos)
            if kind==1027:relas[address]=dict(address=address,addend=addend,file_offset=pos,hex=b[pos:pos+24].hex())
    targets=set()
    for raw in native:
        code=bytes.fromhex(raw['hex'])
        for p in range(0,len(code)-3,4):
            w=struct.unpack_from('<I',code,p)[0]
            if w&0x9f000000!=0x90000000:continue
            reg=w&31;page=((raw['va']+p)&~4095)+(signed(((w>>5)&0x7ffff)<<2|((w>>29)&3),21)<<12)
            for q in range(p+4,min(p+36,len(code)-3),4):
                x=struct.unpack_from('<I',code,q)[0]
                if x&0xffc00000==0xf9400000 and (x>>5)&31==reg:targets.add(page+((x>>10)&4095)*8)
    cells=[];selected_relas=[];todo=list(targets);seen=set()
    while todo:
        address=todo.pop()
        if address in seen:continue
        seen.add(address)
        try:pos=offset_at(address,16)
        except StopIteration:continue
        cells.append(dict(va=address,file_offset=pos,hex=b[pos:pos+16].hex()))
        if address in relas:
            rel=relas[address];selected_relas.append(rel);todo.append(rel['addend'])
        else:
            v=struct.unpack_from('<Q',b,pos)[0]
            if any(s['va']<=v<s['va']+s['file_size'] and not s['flags']&1 for s in segments):todo.append(v)
    native_evidence=dict(ranges=native,cells=cells,relocations=selected_relas,scope='Bounded original code/data/RELA, no full function-boundary or initialized-runtime claim')
    out=dict(provisional=True,provenance='arena/ef6b75ef',xapk_sha256=XAPK_SHA,apk_entry=apk,library_entry=entry,libunity_sha256=sha(b),libunity_size=len(b),tool_sha256=sha(Path(__file__).read_bytes()),query_schema_sha256=sha(source.read_bytes()),query_source='109 shared builtin schema used ONLY to choose search strings, not evidence of APK schema',elf_header_hex=b[:64].hex(),native_evidence=native_evidence,segments=segments,strings=strings,references=refs,windows=windows,limits=['Exact string presence/absence and instruction address candidates, NOT recovered type tree/field order/types.','ADRP+ADD scan does not track intervening register clobbers or control flow; candidates require disassembly review.','Bounded native windows are not complete function bodies or runtime execution.'])
    dest=ROOT/'reverse-engineering/raw/controller112';dest.mkdir(parents=True,exist_ok=True);blob=gzip.compress(canonical(out),mtime=0);assert len(blob)<5*1024*1024;(dest/'probe.json.gz').write_bytes(blob)
    print('libunity',len(b),sha(b),'queries',len(strings),'hits',sum(bool(s['occurrences']) for s in strings),'refs',len(refs),'windows',len(windows),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True)
    try:recover(p.parse_args().xapk)
    except Exception:
        import traceback
        print('::error::'+traceback.format_exc().replace('%','%25').replace('\n','%0A'),flush=True);raise
