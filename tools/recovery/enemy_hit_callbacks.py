"""Pinned direct metadata-reference census and bounded callback-producer exports.

Candidates are ADRP/LDR address references, NOT whole-program pointer/write closure.
"""
import argparse,bisect,gzip,hashlib,io,json,re,struct,sys,tempfile,zipfile
from pathlib import Path
from combat_coroutine_cells import APK_SHA,LIB_SHA,extract,recover_delegates
ROOT=Path(__file__).resolve().parents[2]


def recover(binary,out):
    assert hashlib.sha256(binary).hexdigest()==LIB_SHA
    symbols=json.loads(gzip.decompress((ROOT/'reverse-engineering/raw/combat-chain/symbols.json.gz').read_bytes()))['records']
    selected={r['Address']:r for kind in ('ScriptMetadata','ScriptMetadataMethod') for r in symbols[kind] if 'Enemy_Health' in r['Name']}
    shoff=struct.unpack_from('<Q',binary,40)[0];size,count=struct.unpack_from('<HH',binary,58)
    got={}
    for i in range(count):
        sh=struct.unpack_from('<IIQQQQIIQQ',binary,shoff+i*size)
        if sh[1]!=4:continue
        for p in range(sh[4],sh[4]+sh[5],sh[9] or 24):
            va,info,target=struct.unpack_from('<QQq',binary,p)
            if target in selected and info==1027:
                got[va]=dict(got=hex(va),target=hex(target),symbol=selected[target],rela_file_offset=p,rela_hex=binary[p:p+24].hex())
    assert got
    sys.path.insert(0,str(ROOT/'tools/apk-analyze'));import il2cpp_consts as native
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/'dump.cs';p.write_bytes(gzip.decompress((ROOT/'reverse-engineering/il2cpp/dump.cs.gz').read_bytes()))
        rows=native.parse_dump(str(p))
    by_start={}
    for cls,ns,name,off,rva,sig in rows:
        by_start.setdefault(rva,[]).append(dict(cls=cls,namespace=ns,method=name,signature=sig))
    starts=sorted(by_start)
    # Only decode short windows for ADRP pages that contain an exact wanted GOT.
    import capstone
    md=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_LITTLE_ENDIAN)
    phoff=struct.unpack_from('<Q',binary,32)[0];psize,pcount=struct.unpack_from('<HH',binary,54)
    refs=[];pages={a&~4095 for a in got};scanned=0
    for j in range(pcount):
        seg=struct.unpack_from('<IIQQQQQQ',binary,phoff+j*psize)
        if seg[0]!=1 or not seg[1]&1:continue
        for off in range(seg[2],seg[2]+seg[5]-3,4):
            w=struct.unpack_from('<I',binary,off)[0];scanned+=1
            if w&0x9f000000!=0x90000000:continue
            va=seg[3]+off-seg[2];imm=((w>>5&0x7ffff)<<2)|(w>>29&3)
            if imm&(1<<20):imm-=1<<21
            page=(va&~4095)+(imm<<12)
            if page not in pages:continue
            reg='x'+str(w&31);idx=bisect.bisect_right(starts,va)-1
            if idx<0:continue
            end=starts[idx+1] if idx+1<len(starts) else va+512
            window=min(512,end-va,seg[2]+seg[5]-off)
            for at,sz,op,args in md.disasm_lite(binary[off+4:off+window],va+4):
                m=re.fullmatch(r'x\d+, \['+reg+r'(?:, #0x([0-9a-f]+))?\]',args)
                if op=='ldr' and m and page+int(m[1] or '0',16) in got:
                    g=page+int(m[1] or '0',16)
                    refs.append(dict(adrp=hex(va),load=hex(at),got=hex(g),method_rva=hex(starts[idx]),owners=by_start[starts[idx]],window_hex=binary[off:off+(at-va)+4].hex()))
                if op.startswith('b.') or op in ('b','br','ret','cbz','cbnz','tbz','tbnz'):break
                if op in ('bl','blr'):
                    if int(reg[1:])<19:break
                    continue
                if op.startswith(('st','b.')) or op in ('cmp','cmn','tst','fcmp','ccmp','nop'):continue
                dest=args.split(',')[:2 if op.startswith('ldp') else 1]
                if any(d.strip() in (reg,'w'+reg[1:]) for d in dest):break
    roots=sorted({o['cls'].split('.')[0] for r in refs for o in r['owners']})
    assert 'Enemy_Controller' in roots and 'Test_Enemy' in roots,(roots,refs)
    out.mkdir(parents=True,exist_ok=True)
    recover_delegates(binary,out/'native',tuple(roots))
    result=dict(status='DIRECT_METADATA_ADDRESS_REFERENCE_CANDIDATES_NOT_WHOLE_PROGRAM_WRITER_CLOSURE',
      xapk_sha256=APK_SHA,lib_sha256=LIB_SHA,scan_words=scanned,window_limit_bytes=512,
      scope='Executable PT_LOAD; wanted Enemy_Health metadata symbols; stop at branches/register clobber/method boundary. Does not cover propagated pointers, indirect/reflection/native writes.',
      metadata_bindings=list(got.values()),references=refs,exported_roots=roots)
    (out/'references.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--xapk',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    data=Path(a.xapk).read_bytes();assert hashlib.sha256(data).hexdigest()==APK_SHA
    found=[]
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for n in z.namelist():
            if not n.endswith('.apk'):continue
            with zipfile.ZipFile(io.BytesIO(z.read(n))) as inner:
                p='lib/arm64-v8a/libil2cpp.so'
                if p in inner.namelist():found.append(inner.read(p))
    assert len(found)==1
    recover(found[0],Path(a.output).resolve())
