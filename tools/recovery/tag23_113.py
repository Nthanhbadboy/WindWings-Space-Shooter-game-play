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
    source=ROOT/'datas/l3_ef6b75ef105.json.gz'
    names={'SpriteRenderer','m_Sprite','m_Color','m_Enabled','m_FlipX','m_FlipY','m_Materials','AnimationClip','AnimationBinding','AnimationBindings','CustomCurve','CustomCurveBinding','RegisterAnimationBindings','UnityEngine.SpriteRenderer::set_sprite','UnityEngine.SpriteRenderer::set_sprite(UnityEngine.Sprite)','UnityEngine.SpriteRenderer::get_sprite'}
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
    wanted.update({0x946d0c:'candidate_property_resolver',0x946ce4:'candidate_sprite_writer',0x946d00:'candidate_sprite_reader',0x10e8fe0:'candidate_binding_descriptor',0x10b9d80:'candidate_binding_vtable',0x10ead38:'sprite_native_type',0x492da8:'registry_getter',0x10f0628:'sprite_type_info_record'})
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
        if ref['field'] not in {'m_Sprite','SpriteRenderer','UnityEngine.SpriteRenderer::set_sprite','UnityEngine.SpriteRenderer::get_sprite','candidate_property_resolver','candidate_sprite_writer','candidate_sprite_reader','candidate_binding_descriptor','candidate_binding_vtable','sprite_native_type','registry_getter','sprite_type_info_record'}:continue
        off=ref['file_offset'];s=next(s for s in segments if s['offset']<=off<s['offset']+s['file_size']);lo=max(s['offset'],off-256);hi=min(s['offset']+s['file_size'],off+512);key=(lo,hi)
        if any(w['file_offset']==lo for w in windows):continue
        windows.append(dict(file_offset=lo,va=s['va']+lo-s['offset'],hex=b[lo:hi].hex()))
    # Source-level immediate candidates; co-location is not registration proof.
    immediate=[]
    for seg in segments:
        if not seg['flags']&1:continue
        for pos in range(seg['offset'],seg['offset']+seg['file_size']-3,4):
            op=struct.unpack_from('<I',b,pos)[0]
            if op&0x7f800000!=0x52800000 or ((op>>21)&3)!=0:continue
            value=(op>>5)&65535
            if value not in (23,212):continue
            immediate.append(dict(va=seg['va']+pos-seg['offset'],file_offset=pos,value=value,register=op&31,hex=b[pos:pos+4].hex()))
    paired=[]
    for v in immediate:
        if v['value']!=212:continue
        others=[w for w in immediate if w['value']==23 and abs(w['va']-v['va'])<=512]
        if not others:continue
        pos=v['file_offset'];seg=next(s for s in segments if s['offset']<=pos<s['offset']+s['file_size']);lo=max(seg['offset'],pos-256);hi=min(seg['offset']+seg['file_size'],pos+768)
        paired.append(dict(class212=v,nearby23=others,context=dict(va=seg['va']+lo-seg['offset'],file_offset=lo,hex=b[lo:hi].hex())))
    def offset_at(va,width=1):
        seg=next(s for s in segments if s['va']<=va and va+width<=s['va']+s['file_size']);return seg['offset']+va-seg['va']
    native=[]
    for lo,hi in [(0x946cd8,0x946db8),(0x93b000,0x93b500),(0x386894,0x386b7c),(0x10e8ee0,0x10e9200),(0x940218,0x940280),(0x492d80,0x492e40),(0x6a9400,0x6a9bcc),(0x10eacb8,0x10eae38)]:
        pos=offset_at(lo,hi-lo);native.append(dict(va=lo,file_offset=pos,hex=b[pos:pos+hi-lo].hex()))
    shoff=struct.unpack_from('<Q',b,40)[0];ss,sc=struct.unpack_from('<HH',b,58);relas=[]
    for i in range(sc):
        h=struct.unpack_from('<IIQQQQIIQQ',b,shoff+i*ss)
        if h[1]!=4:continue
        for pos in range(h[4],h[4]+h[5],h[9] or 24):
            address,kind,addend=struct.unpack_from('<QQq',b,pos)
            if kind==1027:relas.append(dict(address=address,addend=addend,file_offset=pos,hex=b[pos:pos+24].hex()))
    registry_vtable=next(r['addend'] for r in relas if r['address']==0x10e2a58)
    for lo,hi in [(0x10e2a40,0x10e2a68),(registry_vtable,registry_vtable+0x50)]+[(r['addend'],r['addend']+0x500) for r in relas if registry_vtable+0x10<=r['address']<registry_vtable+0x40]:
        pos=offset_at(lo);native.append(dict(va=lo,file_offset=pos,hex=b[pos:pos+hi-lo].hex()))
    anchors={0x946d0c,0x946ce4,0x946d00,0x946da0,0x10b9d80,0x10e8fe0,0x10ead38,0x142d9f,0x10f0628};backrefs=[r for r in relas if r['addend'] in anchors]
    data_regions=[(r['address']-128,r['address']+256) for r in backrefs]
    for lo,hi in data_regions:
        pos=offset_at(lo,hi-lo);native.append(dict(va=lo,file_offset=pos,hex=b[pos:pos+hi-lo].hex()))
    # Exact BL/B call sites to registry accessor, not speculative string address pairs.
    registry_calls=[]
    for seg in segments:
        if not seg['flags']&1:continue
        for pos in range(seg['offset'],seg['offset']+seg['file_size']-3,4):
            op=struct.unpack_from('<I',b,pos)[0]
            if op&0x7c000000!=0x14000000:continue
            pc=seg['va']+pos-seg['offset'];target=pc+(signed(op&0x3ffffff,26)<<2)
            if target not in (0x492da8,0x492db4):continue
            lo=max(seg['offset'],pos-64);hi=min(seg['offset']+seg['file_size'],pos+192);registry_calls.append(dict(pc=pc,target=target,context=dict(va=seg['va']+lo-seg['offset'],file_offset=lo,hex=b[lo:hi].hex())))
    selected_relas=[r for r in relas if any(n['va']<=r['address']<n['va']+len(n['hex'])//2 for n in native)]
    pointed_strings=[]
    for address in sorted({r['addend'] for r in selected_relas}):
        try:pos=offset_at(address)
        except StopIteration:continue
        end=b.find(b'\0',pos,min(len(b),pos+512))
        if end>=pos and end>pos and all(x in (9,10,13) or 32<=x<127 for x in b[pos:end]):pointed_strings.append(dict(va=address,file_offset=pos,hex=b[pos:end+1].hex()))
    class212_windows=[]
    for v in immediate:
        if v['value']!=212:continue
        pos=v['file_offset'];lo=max(0,pos-128);hi=pos+256;class212_windows.append(dict(va=v['va']-128,file_offset=lo,hex=b[lo:hi].hex()))
    out=dict(provisional=True,provenance='arena/ef6b75ef',xapk_sha256=XAPK_SHA,apk_entry=apk,library_entry=entry,libunity_sha256=sha(b),libunity_size=len(b),tool_sha256=sha(Path(__file__).read_bytes()),query_schema_sha256=sha(source.read_bytes()),query_source='Explicit SpriteRenderer registration/binding strings; scalar immediates are unvalidated candidates',elf_header_hex=b[:64].hex(),native_slices=native,registry_vtable=registry_vtable,registry_calls=registry_calls,pointed_strings=pointed_strings,relocations=selected_relas,callback_backrefs=backrefs,class212_windows=class212_windows,immediate_candidates=immediate,paired_immediates=paired,segments=segments,strings=strings,references=refs,windows=windows,limits=['Exact string presence/absence and instruction address candidates, NOT recovered type tree/field order/types.','ADRP+ADD scan does not track intervening register clobbers or control flow; candidates require disassembly review.','Bounded native windows are not complete function bodies or runtime execution.'])
    dest=ROOT/'reverse-engineering/raw/tag23-113';dest.mkdir(parents=True,exist_ok=True);blob=gzip.compress(canonical(out),mtime=0);assert len(blob)<5*1024*1024;(dest/'probe.json.gz').write_bytes(blob)
    print('libunity',len(b),sha(b),'immediates',len(immediate),'paired',len(paired),'queries',len(strings),'hits',sum(bool(s['occurrences']) for s in strings),'refs',len(refs),'windows',len(windows),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True)
    try:recover(p.parse_args().xapk)
    except Exception:
        import traceback
        print('::error::'+traceback.format_exc().replace('%','%25').replace('\n','%0A'),flush=True);raise
