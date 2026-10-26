"""Pinned original libunity vtable/RELA discovery around graph-populator virtual slots."""
import argparse,bisect,gzip,hashlib,io,json,struct,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
XAPK_SHA='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
RANGES=[(0x10b1000,0x10b1500),(0x6d2950,0x6d29e4)]
TARGETS={0x6d2950:'graph_populator'}
VTABLE_LO,VTABLE_HI=0x10b1000,0x10b1500
CODE_LO,CODE_HI=0x6d0000,0x6d9000
SLOTS=(0x10,0x18,0x70)
KNOWN_VPTRS=(0x10b1150,0x10b1240,0x10b1330,0x10b1420)
KNOWN_SLOTS=tuple(range(0,0x80,8))
def sha(b):return hashlib.sha256(b).hexdigest()
def signed(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def recover(path):
    data=path.read_bytes();assert sha(data)==XAPK_SHA;found=[]
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for name in z.namelist():
            if not name.endswith('.apk'):continue
            with zipfile.ZipFile(io.BytesIO(z.read(name))) as a:
                lib='lib/arm64-v8a/libunity.so'
                if lib in a.namelist():found.append((name,lib,a.read(lib)))
    assert len(found)==1;apk,lib,b=found[0];assert b[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',b,18)[0]==183
    off=struct.unpack_from('<Q',b,32)[0];size,count=struct.unpack_from('<HH',b,54);segments=[]
    for i in range(count):
        p=struct.unpack_from('<IIQQQQQQ',b,off+i*size)
        if p[0]==1:segments.append(dict(flags=p[1],offset=p[2],va=p[3],file_size=p[5],memory_size=p[6]))
    def va(pos):
        s=next(s for s in segments if s['offset']<=pos<s['offset']+s['file_size']);return s['va']+pos-s['offset']
    def offset(addr):
        s=next(s for s in segments if s['va']<=addr<s['va']+s['file_size']);return s['offset']+addr-s['va']
    unwind={};unwind_header=None
    for i in range(count):
        ph=struct.unpack_from('<IIQQQQQQ',b,off+i*size)
        if ph[0]!=0x6474e550:continue
        h=ph[2];base=ph[3];enc=b[h:h+4];assert enc==bytes([1,0x1b,3,0x3b]),enc.hex()
        n=struct.unpack_from('<I',b,h+8)[0];unwind_header=dict(va=base,file_offset=h,hex=b[h:h+12].hex(),entry_count=n)
        for j in range(n):
            a,d=struct.unpack_from('<ii',b,h+12+j*8);start=base+a;fde=base+d;pos=offset(fde);delta,length=struct.unpack_from('<iI',b,pos+8)
            if fde+8+delta!=start:continue
            if not 0<length<=0x20000:continue
            unwind[start]=dict(start=start,end=start+length,fde_va=fde,fde_hex=b[pos:pos+16].hex(),table_va=base+12+j*8,table_hex=b[h+12+j*8:h+20+j*8].hex())
    shoff=struct.unpack_from('<Q',b,40)[0];shsize,shcount=struct.unpack_from('<HH',b,58);sections=[struct.unpack_from('<IIQQQQIIQQ',b,shoff+i*shsize) for i in range(shcount)]
    relas=[];imports=[]
    for i in range(shcount):
        p=sections[i]
        if p[1]!=4 or p[9]!=24:continue
        for pos in range(p[4],p[4]+p[5],24):
            address,info,addend=struct.unpack_from('<QQq',b,pos)
            if info&0xffffffff==1027:relas.append(dict(address=address,addend=addend))
            if info&0xffffffff==1026:
                symtab=sections[p[6]];sympos=symtab[4]+(info>>32)*symtab[9];nameoff=struct.unpack_from('<I',b,sympos)[0];strtab=sections[symtab[6]];namepos=strtab[4]+nameoff;end=b.index(b'\0',namepos)
                imports.append(dict(address=address,name=b[namepos:end].decode(),symbol_entry_offset=sympos,symbol_hex=b[sympos:sympos+24].hex(),name_file_offset=namepos,name_hex=b[namepos:end+1].hex()))
    by_address={r['address']:r['addend'] for r in relas if VTABLE_LO<=r['address']<VTABLE_HI and CODE_LO<=r['addend']<CODE_HI}
    candidates=[]
    for base in range(VTABLE_LO,VTABLE_HI-0x70,8):
        if all(base+s in by_address for s in SLOTS):
            slots={hex(s):dict(address=base+s,addend=by_address[base+s],unwind=unwind.get(by_address[base+s])) for s in SLOTS}
            candidates.append(dict(vptr=base,slots=slots,slot_addends=[by_address[base+s] for s in SLOTS],graph_populator_relas=[r for r in relas if r['addend']==0x6d2950 and VTABLE_LO<=r['address']<VTABLE_HI]))
    candidates.sort(key=lambda x:x['vptr'])
    graph_relas=[r for r in relas if r['addend']==0x6d2950]
    rela_by_address={r['address']:r['addend'] for r in relas}
    known_vtables=[]
    for vptr in KNOWN_VPTRS:
        slots={hex(off):dict(address=vptr+off,addend=rela_by_address.get(vptr+off),unwind=unwind.get(rela_by_address.get(vptr+off))) for off in KNOWN_SLOTS}
        known_vtables.append(dict(vptr=vptr,slots=slots,addends=[rela_by_address.get(vptr+off) for off in KNOWN_SLOTS]))
    known_addends=[a for v in known_vtables for a in v['addends'] if a in unwind]
    direct_refs=[];graph_thunk_refs=[];starts=sorted(unwind)
    target_set=set(TARGETS)|{a for c in candidates for a in c['slot_addends']}|set(known_addends)
    for s in segments:
        if not s['flags']&1:continue
        for pos in range(s['offset'],s['offset']+s['file_size']-3,4):
            word=struct.unpack_from('<I',b,pos)[0];pc=va(pos)
            if word&0x7c000000==0x14000000:
                target=pc+(signed(word&0x3ffffff,26)<<2)
                if target==0x6d2950:
                    j=bisect.bisect_right(starts,pc)-1;owner=unwind[starts[j]] if j>=0 and pc<unwind[starts[j]]['end'] else None
                    graph_thunk_refs.append(dict(pc=pc,target=target,owner_start=owner['start'] if owner else None,owner_end=owner['end'] if owner else None))
                if target in target_set and 0x500000<=pc<0x6d9000:
                    j=bisect.bisect_right(starts,pc)-1;owner=unwind[starts[j]] if j>=0 and pc<unwind[starts[j]]['end'] else None
                    direct_refs.append(dict(pc=pc,target=target,owner_start=owner['start'] if owner else None,owner_end=owner['end'] if owner else None))
    entries=[]
    thunk_owners=[x['owner_start'] for x in graph_thunk_refs if x['owner_start'] in unwind]
    for a in [0x6d2950]+[a for c in candidates for a in c['slot_addends']]+known_addends+thunk_owners:
        if a in unwind and a not in entries:entries.append(a)
    windows=[];followed=[];seen=set();queue=[(a,0,None) for a in entries]
    for lo,hi in sorted(set(RANGES)):
        pos=offset(lo);assert offset(hi-1)==pos+hi-lo-1
        windows.append(dict(va=lo,file_offset=pos,hex=b[pos:pos+hi-lo].hex()))
    while queue:
        a,depth,parent=queue.pop(0)
        if a in seen:continue
        assert len(seen)<240,'bounded vtable root count';seen.add(a)
        rec=unwind.get(a);length=rec['end']-a if rec else 0x300;pos=offset(a)
        w=dict(va=a,file_offset=pos,hex=b[pos:pos+length].hex());windows.append(w)
        followed.append(dict(entry=a,depth=depth,parent=parent,extent_source='original_FDE' if rec else 'bounded_window_not_function_extent',unwind=rec))
        if depth>=0:continue
        for i in range(0,length-3,4):
            op=struct.unpack_from('<I',b,pos+i)[0]
            if op&0x7c000000!=0x14000000:continue
            target=a+i+(signed(op&0x3ffffff,26)<<2)
            if a<=target<a+length:continue
            if any(s['flags']&1 and s['va']<=target<s['va']+s['file_size'] for s in segments):queue.append((target,depth+1,a+i))
    cells={}
    def cell(address,n):
        try:pos=offset(address);assert offset(address+n-1)==pos+n-1
        except (StopIteration,AssertionError):return
        cells[address]=dict(va=address,file_offset=pos,hex=b[pos:pos+n].hex())
    for w in windows:
        if not CODE_LO<=w['va']<CODE_HI:continue
        code=bytes.fromhex(w['hex']);pages={}
        for i in range(0,len(code)-3,4):
            op=struct.unpack_from('<I',code,i)[0];pc=w['va']+i
            if op&0x9f000000==0x90000000:pages[op&31]=((pc&~4095)+(signed(((op>>5)&0x7ffff)<<2|((op>>29)&3),21)<<12),i)
            if op&0x3b000000==0x39000000 and (op>>22)&1:
                rn=(op>>5)&31
                if rn in pages and i-pages[rn][1]<=32:
                    scale=1<<((op>>30)&3)
                    if op&0x04000000 and (op>>23)&1:scale=16
                    cell(pages[rn][0]+((op>>10)&4095)*scale,max(16,scale))
            if op&0x3b000000==0x18000000:cell(pc+(signed((op>>5)&0x7ffff,19)<<2),16)
    selected_imports=[r for r in imports if any(w['va']<=r['address']<w['va']+len(w['hex'])//2 for w in list(cells.values()))]
    selected=[r for r in relas if r['address'] in by_address or r['addend']==0x6d2950 or any(w['va']<=r['address']<w['va']+len(w['hex'])//2 for w in windows+list(cells.values()))]
    return dict(provisional=True,xapk_sha256=XAPK_SHA,apk_entry=apk,library_entry=lib,libunity_sha256=sha(b),libunity_size=len(b),tool_sha256=sha(Path(__file__).read_bytes()),segments=segments,unwind_header=unwind_header,followed=followed,strings=[],references=[],branch_references=direct_refs,windows=windows,cells=list(cells.values()),relocations=selected,imports=selected_imports,vtable_candidates=candidates,known_vtables=known_vtables,graph_populator_relas=graph_relas,graph_thunk_refs=graph_thunk_refs,thunk_owner_entries=thunk_owners,vtable_rela_count=len(by_address),limits=['Vtable slot inference is based on exact original RELA addends at +0x10/+0x18/+0x70; semantic class/method names are NOT assigned.','Selected original byte spans and FDEs only, not a whole library, game runtime, Unity TypeTree/readback or render.'])
def main():
    p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True);a=p.parse_args();out=ROOT/'reverse-engineering/raw/vtable123/probe.json.gz';out.parent.mkdir(parents=True,exist_ok=True)
    try:
        r=recover(a.xapk)
    except Exception as e:
        import traceback
        (out.parent/'diagnostic.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc()),indent=2)+'\n')
        raise
    out.write_bytes(gzip.compress((json.dumps(r,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0));print('saved',out,'candidates',len(r['vtable_candidates']),'known',len(r['known_vtables']),'graph_relas',len(r['graph_populator_relas']),'graph_thunk_refs',len(r['graph_thunk_refs']),'refs',len(r['branch_references']))
if __name__=='__main__':main()
