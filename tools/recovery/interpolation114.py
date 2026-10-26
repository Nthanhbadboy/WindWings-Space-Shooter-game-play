"""Pinned original libunity interpolation discovery; references are candidates, not equivalence proof."""
import argparse,gzip,hashlib,io,json,struct,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
XAPK_SHA='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
NAMES=['UnityEngine.AnimationCurve::Evaluate','UnityEngine.AnimationCurve::Evaluate(System.Single)','UnityEngine.AnimationCurve::AddKey','UnityEngine.AnimationCurve::AddKey_Injected','UnityEngine.AnimationCurve::Internal_Create','UnityEngine.AnimationCurve::get_keys','UnityEngine.AnimationCurve::GetKey_Injected','UnityEngine.AnimationCurve::set_preWrapMode','UnityEngine.AnimationClip::SampleAnimation']
RANGES=[]
TARGETS={}
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
    strings=[];wanted=dict(TARGETS)
    for name in NAMES:
        needle=name.encode()+b'\0';positions=[];pos=b.find(needle)
        while pos>=0:
            address=va(pos);positions.append(dict(va=address,file_offset=pos,hex=needle.hex()));wanted[address]=name;pos=b.find(needle,pos+1)
        strings.append(dict(text=name,occurrences=positions))
    refs=[]
    for s in segments:
        if not s['flags']&1:continue
        for pos in range(s['offset'],s['offset']+s['file_size']-3,4):
            word=struct.unpack_from('<I',b,pos)[0];pc=va(pos)
            if word&0x9f000000!=0x90000000:continue
            rd=word&31;page=(pc&~4095)+(signed(((word>>5)&0x7ffff)<<2|((word>>29)&3),21)<<12)
            for p in range(pos+4,min(pos+36,s['offset']+s['file_size']-3),4):
                op=struct.unpack_from('<I',b,p)[0]
                if op&0xffc00000==0x91000000 and ((op>>5)&31)==rd:
                    address=page+((op>>10)&4095)
                    if address in wanted:refs.append(dict(field=wanted[address],va=pc,add_va=va(p),target=address))
    ranges=list(RANGES)+[(r['va']-256,r['va']+512) for r in refs];windows=[]
    for lo,hi in sorted(set(ranges)):
        pos=offset(lo);assert offset(hi-1)==pos+hi-lo-1
        windows.append(dict(va=lo,file_offset=pos,hex=b[pos:pos+hi-lo].hex()))
    shoff=struct.unpack_from('<Q',b,40)[0];shsize,shcount=struct.unpack_from('<HH',b,58);relas=[]
    for i in range(shcount):
        p=struct.unpack_from('<IIQQQQIIQQ',b,shoff+i*shsize)
        if p[1]!=4 or p[9]!=24:continue
        for pos in range(p[4],p[4]+p[5],24):
            address,info,addend=struct.unpack_from('<QQq',b,pos)
            if info&0xffffffff==1027:relas.append(dict(address=address,addend=addend))
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
    selected=[r for r in relas if any(w['va']<=r['address']<w['va']+len(w['hex'])//2 for w in windows+list(cells.values())) or r['addend'] in TARGETS]
    return dict(provisional=True,xapk_sha256=XAPK_SHA,apk_entry=apk,library_entry=lib,libunity_sha256=sha(b),libunity_size=len(b),tool_sha256=sha(Path(__file__).read_bytes()),segments=segments,strings=strings,references=refs,windows=windows,cells=list(cells.values()),relocations=selected,limits=['Adjacent ADRP/ADD and ADRP/LDR pairs are discovery candidates, not proven register dataflow.','Selected original byte spans only, not a whole library, engine bootstrap or interpolation equivalence.'])
def main():
    p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True);a=p.parse_args();r=recover(a.xapk);out=ROOT/'reverse-engineering/raw/interpolation114/probe.json.gz';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(gzip.compress((json.dumps(r,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0));print('saved',out,'strings',sum(len(s['occurrences']) for s in r['strings']),'refs',len(r['references']))
if __name__=='__main__':main()
