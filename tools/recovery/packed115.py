"""Pinned original libunity interpolation discovery; references are candidates, not equivalence proof."""
import argparse,bisect,gzip,hashlib,io,json,struct,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
XAPK_SHA='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
NAMES=['m_StreamedClip','m_DenseClip','m_ConstantClip','m_MuscleClip','AnimationClip','StreamedClip','DenseClip','UnityEngine.AnimationClip::get_length','UnityEngine.AnimationClip::SampleAnimation','UnityEngine.AnimationClip::SampleAnimation_Injected']
RANGES=[(0x6ad7e4,0x6addac),(0x6c2000,0x6c4480),(0x6b0000,0x6b1300)]
TARGETS={0x6ad7e4:'compiler_parent',0x6deeb8:'compiled_data_builder',0xb922a8:'compiled_data_accessor'}
FOLLOW_ENTRIES=[0x6deeb8,0xb922a8,0x398600,0xb714c8,0xb76cf0]
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
    # Exact function extents from original EH frame records when present.
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
    strings=[];wanted=dict(TARGETS)
    for name in NAMES:
        needle=name.encode()+b'\0';positions=[];pos=b.find(needle)
        while pos>=0:
            address=va(pos);positions.append(dict(va=address,file_offset=pos,hex=needle.hex()));wanted[address]=name;pos=b.find(needle,pos+1)
        strings.append(dict(text=name,occurrences=positions))
    refs=[];branch_refs=[];starts=sorted(unwind)
    for s in segments:
        if not s['flags']&1:continue
        for pos in range(s['offset'],s['offset']+s['file_size']-3,4):
            word=struct.unpack_from('<I',b,pos)[0];pc=va(pos)
            if word&0x7c000000==0x14000000:
                target=pc+(signed(word&0x3ffffff,26)<<2)
                if target in (0x6ad7e4,0x6deeb8,0xb922a8):
                    j=bisect.bisect_right(starts,pc)-1;owner=unwind[starts[j]] if j>=0 and pc<unwind[starts[j]]['end'] else None
                    branch_refs.append(dict(pc=pc,target=target,unwind=owner))
            if word&0x9f000000!=0x90000000:continue
            rd=word&31;page=(pc&~4095)+(signed(((word>>5)&0x7ffff)<<2|((word>>29)&3),21)<<12)
            for p in range(pos+4,min(pos+36,s['offset']+s['file_size']-3),4):
                op=struct.unpack_from('<I',b,p)[0]
                if op&0xffc00000==0x91000000 and ((op>>5)&31)==rd:
                    address=page+((op>>10)&4095)
                    if address in wanted:refs.append(dict(field=wanted[address],va=pc,add_va=va(p),target=address))
    # Structural discovery only: native StreamedClip header candidates need both u16 counts.
    sampler_candidates=[]
    for start,rec in sorted(unwind.items()):
        length=rec['end']-start
        if length>0x10000:continue
        try:pos=offset(start)
        except StopIteration:continue
        code=b[pos:pos+length];counts=set();math_sites=[];count_sites=[]
        for j in range(0,len(code)-3,4):
            op=struct.unpack_from('<I',code,j)[0]
            if op&0xffc00000==0x79400000 and ((op>>10)&4095) in (8,9):
                displacement=((op>>10)&4095)*2;counts.add(displacement);count_sites.append(dict(pc=start+j,offset=displacement,base=(op>>5)&31))
            if op&0xffe0fc00 in (0x1e200800,0x1e202800,0x1e203800) or op&0xffe08000==0x1f000000:math_sites.append(start+j)
        if counts=={16,18}:
            sampler_candidates.append(dict(start=start,unwind=rec,count_sites=count_sites,math_sites=math_sites))
    candidate_ranges=[(c['start'],c['unwind']['end']) for c in sampler_candidates if c['math_sites']]
    ranges=list(RANGES)+candidate_ranges+[(r['va']-256,r['va']+512) for r in refs]+[(r['unwind']['start'],r['unwind']['end']) if r['unwind'] and r['unwind']['end']-r['unwind']['start']<=8192 else (r['pc']-128,r['pc']+128) for r in branch_refs];windows=[]
    for lo,hi in sorted(set(ranges)):
        pos=offset(lo);assert offset(hi-1)==pos+hi-lo-1
        windows.append(dict(va=lo,file_offset=pos,hex=b[pos:pos+hi-lo].hex()))
    followed=[];seen=set();queue=[(a,0,None) for a in FOLLOW_ENTRIES]
    while queue:
        a,depth,parent=queue.pop(0)
        if a in seen:continue
        assert len(seen)<160,'bounded native dependency count';seen.add(a)
        rec=unwind.get(a);length=rec['end']-a if rec else 0x300;pos=offset(a)
        w=dict(va=a,file_offset=pos,hex=b[pos:pos+length].hex());windows.append(w)
        followed.append(dict(entry=a,depth=depth,parent=parent,extent_source='original_FDE' if rec else 'bounded_window_not_function_extent',unwind=rec))
        if depth>=4:continue
        for i in range(0,length-3,4):
            op=struct.unpack_from('<I',b,pos+i)[0]
            if op&0x7c000000!=0x14000000:continue
            target=a+i+(signed(op&0x3ffffff,26)<<2)
            if a<=target<a+length:continue
            if any(s['flags']&1 and s['va']<=target<s['va']+s['file_size'] for s in segments):queue.append((target,depth+1,a+i))
    shoff=struct.unpack_from('<Q',b,40)[0];shsize,shcount=struct.unpack_from('<HH',b,58);relas=[];imports=[]
    sections=[struct.unpack_from('<IIQQQQIIQQ',b,shoff+i*shsize) for i in range(shcount)]
    for i in range(shcount):
        p=struct.unpack_from('<IIQQQQIIQQ',b,shoff+i*shsize)
        if p[1]!=4 or p[9]!=24:continue
        for pos in range(p[4],p[4]+p[5],24):
            address,info,addend=struct.unpack_from('<QQq',b,pos)
            if info&0xffffffff==1027:relas.append(dict(address=address,addend=addend))
            if info&0xffffffff==1026:
                symtab=sections[p[6]];sympos=symtab[4]+(info>>32)*symtab[9];nameoff=struct.unpack_from('<I',b,sympos)[0];strtab=sections[symtab[6]];namepos=strtab[4]+nameoff;end=b.index(b'\0',namepos)
                imports.append(dict(address=address,name=b[namepos:end].decode(),symbol_entry_offset=sympos,symbol_hex=b[sympos:sympos+24].hex(),name_file_offset=namepos,name_hex=b[namepos:end+1].hex()))
    # Preserve exact literal/direct ADRP+LDR cells accessed in selected instruction ranges.
    cells={}
    def cell(address,n):
        try:pos=offset(address);assert offset(address+n-1)==pos+n-1
        except (StopIteration,AssertionError):return
        cells[address]=dict(va=address,file_offset=pos,hex=b[pos:pos+n].hex())
    for w in windows:
        code=bytes.fromhex(w['hex']);pages={}
        for i in range(0,len(code)-3,4):
            op=struct.unpack_from('<I',code,i)[0];pc=w['va']+i
            if op&0x9f000000==0x90000000:pages[op&31]=((pc&~4095)+(signed(((op>>5)&0x7ffff)<<2|((op>>29)&3),21)<<12),i)
            # Scalar integer/FP/SIMD unsigned-offset LDR. Captured cells are candidates until executed.
            if op&0x3b000000==0x39000000 and (op>>22)&1:
                rn=(op>>5)&31
                if rn in pages and i-pages[rn][1]<=32:
                    scale=1<<((op>>30)&3)
                    if op&0x04000000 and (op>>23)&1:scale=16
                    cell(pages[rn][0]+((op>>10)&4095)*scale,max(16,scale))
            if op&0x3b000000==0x18000000:cell(pc+(signed((op>>5)&0x7ffff,19)<<2),16)
    selected_imports=[r for r in imports if any(w['va']<=r['address']<w['va']+len(w['hex'])//2 for w in list(cells.values()))]
    selected=[r for r in relas if any(w['va']<=r['address']<w['va']+len(w['hex'])//2 for w in windows+list(cells.values())) or r['addend'] in TARGETS]
    return dict(provisional=True,xapk_sha256=XAPK_SHA,apk_entry=apk,library_entry=lib,libunity_sha256=sha(b),libunity_size=len(b),tool_sha256=sha(Path(__file__).read_bytes()),segments=segments,unwind_header=unwind_header,followed=followed,sampler_candidates=sampler_candidates,strings=strings,references=refs,branch_references=branch_refs,windows=windows,cells=list(cells.values()),relocations=selected,imports=selected_imports,limits=['Adjacent ADRP/ADD and ADRP/LDR pairs are discovery candidates, not proven register dataflow.','Selected original byte spans only, not a whole library, engine bootstrap or interpolation equivalence.'])
def main():
    p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True);a=p.parse_args();r=recover(a.xapk);out=ROOT/'reverse-engineering/raw/packed115/probe.json.gz';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(gzip.compress((json.dumps(r,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0));print('saved',out,'strings',sum(len(s['occurrences']) for s in r['strings']),'refs',len(r['references']))
if __name__=='__main__':main()
