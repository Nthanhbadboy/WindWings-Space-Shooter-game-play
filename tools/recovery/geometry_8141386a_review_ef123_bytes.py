"""R1 independent original ELF/metadata byte read for ef123 review.
provenance: arena/8141386a-windwings-space-shooter-game-p
Read-only streamed ZIP→scratch, mmap each library, bounded selected spans. No original
code execution, whole bundle decode, SDK or peer-branch/tool modification.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import mmap
from pathlib import Path
import shutil
import struct
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tools.verify.geometry_8141386a_atlas_io import BRANCH,canonical,sha,sha_file,scratch
RAW=ROOT/'reverse-engineering/raw/geometry-8141386a/review-ef123'
XAPK='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
UNITY='d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7'
IL2CPP='9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99'
META='449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69'


class Elf:
    def __init__(self,path):
        self.file=path.open('rb');self.b=mmap.mmap(self.file.fileno(),0,access=mmap.ACCESS_READ);b=self.b
        if b[:6]!=b'\x7fELF\x02\x01' or struct.unpack_from('<H',b,18)[0]!=183:raise ValueError('not little-endian ELF64 AArch64')
        off=struct.unpack_from('<Q',b,32)[0];size,n=struct.unpack_from('<HH',b,54)
        self.programs=[struct.unpack_from('<IIQQQQQQ',b,off+i*size) for i in range(n)]
        self.segments=[dict(offset=p[2],va=p[3],filesz=p[5],memsz=p[6],flags=p[1]) for p in self.programs if p[0]==1]
        off=struct.unpack_from('<Q',b,40)[0];size,n=struct.unpack_from('<HH',b,58)
        self.sections=[struct.unpack_from('<IIQQQQIIQQ',b,off+i*size) for i in range(n)]
    def close(self):self.b.close();self.file.close()
    def offset(self,va,size=1):
        matches=[s['offset']+va-s['va'] for s in self.segments if s['va']<=va and va+size<=s['va']+s['filesz']]
        if len(matches)!=1:raise ValueError('VA extent not uniquely file-backed')
        return matches[0]
    def span(self,va,size):
        p=self.offset(va,size);b=self.b[p:p+size]
        return dict(va=va,file_offset=p,size=size,hex=b.hex(),sha256=sha(b))
    def relas(self):
        for section in self.sections:
            if section[1]!=4:continue
            if section[9]!=24:raise ValueError('unexpected ELF64 RELA entry width')
            for off in range(section[4],section[4]+section[5],24):
                address,info,addend=struct.unpack_from('<QQq',self.b,off)
                yield dict(address=address,info=info,type=info&0xffffffff,symbol=info>>32,addend=addend,file_offset=off,hex=self.b[off:off+24].hex())
    def selected_fdes(self,entries):
        result=[]
        for p in self.programs:
            if p[0]!=0x6474e550:continue
            off,va=p[2],p[3]
            if self.b[off:off+4]!=bytes([1,0x1b,3,0x3b]):raise ValueError('unsupported EH header pointer encodings')
            n=struct.unpack_from('<I',self.b,off+8)[0]
            for i in range(n):
                a,d=struct.unpack_from('<ii',self.b,off+12+i*8);start=va+a
                if start not in entries:continue
                fde=va+d;pos=self.offset(fde,16);delta,size=struct.unpack_from('<iI',self.b,pos+8)
                if fde+8+delta!=start:raise ValueError('FDE initial-location contradiction')
                result.append(dict(start=start,end_exclusive=start+size,fde_va=fde,fde_file_offset=pos,fde_hex=self.b[pos:pos+16].hex(),table_va=va+12+i*8,table_hex=self.b[off+12+i*8:off+20+i*8].hex()))
        return result


def recover(xapk):
    if sha_file(xapk)!=XAPK:raise ValueError('original XAPK mismatch')
    with scratch('review-original-') as directory:
        targets={'lib/arm64-v8a/libunity.so':('unity',UNITY),'lib/arm64-v8a/libil2cpp.so':('il2cpp',IL2CPP),'assets/bin/Data/Managed/Metadata/global-metadata.dat':('metadata',META)};paths={};inputs=[]
        with zipfile.ZipFile(xapk) as outer:
            for i,name in enumerate(sorted(n for n in outer.namelist() if n.endswith('.apk'))):
                part=directory/f'apk-{i}'
                with outer.open(name) as src,part.open('wb') as dst:shutil.copyfileobj(src,dst,1024*1024)
                with zipfile.ZipFile(part) as inner:
                    for entry,(key,expected) in targets.items():
                        if entry not in inner.namelist():continue
                        if key in paths:raise ValueError('ambiguous original library/metadata input')
                        path=directory/key
                        with inner.open(entry) as src,path.open('wb') as dst:shutil.copyfileobj(src,dst,1024*1024)
                        if sha_file(path)!=expected:raise ValueError('original library/metadata SHA mismatch')
                        paths[key]=path;inputs.append(dict(apk_member=name,entry=entry,sha256=expected,size=path.stat().st_size))
        peer=json.loads(gzip.decompress((RAW/'peer-vtable123-probe.json.gz').read_bytes()));unity=Elf(paths['unity']);il=Elf(paths['il2cpp'])
        try:
            relas=[];rela_count=relative_count=0;global_graph=[]
            for r in unity.relas():
                rela_count+=1
                if r['type']!=1027:continue
                relative_count+=1
                if 0x10b1000<=r['address']<0x10b1500:relas.append(r)
                if r['addend']==0x6d2950:global_graph.append(r)
            by_address={r['address']:r['addend'] for r in relas if 0x6d0000<=r['addend']<0x6d9000}
            candidates=[base for base in range(0x10b1000,0x10b1500-0x70,8) if all(base+s in by_address for s in (0x10,0x18,0x70))]
            raw_windows=[];seen=set()
            for w in peer['windows']:
                k=(w['va'],len(w['hex'])//2)
                if k in seen:continue
                seen.add(k);span=unity.span(*k)
                if span['hex']!=w['hex']:raise ValueError('fresh original bytes differ from pinned peer window')
                raw_windows.append(dict(va=span['va'],file_offset=span['file_offset'],size=span['size'],sha256=span['sha256']))
            graph_bls=[]
            for s in unity.segments:
                if not s['flags']&1:continue
                for off in range(s['offset'],s['offset']+s['filesz']-3,4):
                    w=struct.unpack_from('<I',unity.b,off)[0]
                    if w&0x7c000000!=0x14000000:continue
                    pc=s['va']+off-s['offset'];imm=w&0x3ffffff;imm=imm-(1<<26) if imm&(1<<25) else imm
                    if pc+(imm<<2)==0x6d2950:graph_bls.append(dict(pc=pc,word=w,is_link=bool(w&0x80000000),hex=unity.b[off:off+4].hex()))
            marker=[r for r in il.relas() if r['address']==0x2adfb48]
            if len(marker)!=1 or marker[0]['type']!=1027:raise ValueError('callback marker lacks unique original relative relocation')
            pointer=il.span(marker[0]['addend'],8);encoded=struct.unpack('<Q',bytes.fromhex(pointer['hex']))[0]
            meta=paths['metadata'].read_bytes()
            magic,version,table_offset,table_bytes,data_offset,data_bytes=struct.unpack_from('<6I',meta)
            if magic!=0xfab11baf or version!=31 or encoded>>32 or not encoded&1:raise ValueError('unsupported metadata/encoded-usage format')
            kind=encoded>>29;index=(encoded&0x1fffffff)>>1
            if kind!=5 or index*8+8>table_bytes:raise ValueError('usage does not identify an in-bounds metadata string literal')
            definition=meta[table_offset+index*8:table_offset+index*8+8];length,relative=struct.unpack('<II',definition)
            if relative+length>data_bytes:raise ValueError('literal payload outside metadata data table')
            literal=meta[data_offset+relative:data_offset+relative+length]
            result=dict(schema=1,item=119,provenance=BRANCH,xapk_sha256=XAPK,inputs=inputs,
                        unity=dict(segments=unity.segments,rela_total=rela_count,relative_rela_total=relative_count,vtable_window_relas=relas,
                                   band_filtered_entry_count=len(by_address),band_candidates=candidates,global_graph_relative_relas=global_graph,global_graph_direct_branches=graph_bls,
                                   peer_window_matches=raw_windows,selected_fdes=unity.selected_fdes({x['entry'] for x in peer['followed']})),
                        marker=dict(rela=marker[0],target_cell=pointer,encoded_usage=encoded,kind=kind,lowbit=encoded&1,index=index,
                                    metadata_version=version,string_literal_table_offset=table_offset,string_literal_table_bytes=table_bytes,string_literal_data_offset=data_offset,string_literal_data_bytes=data_bytes,
                                    definition_file_offset=table_offset+index*8,definition_hex=definition.hex(),payload_file_offset=data_offset+relative,payload_hex=literal.hex(),utf8=literal.decode('utf8')),
                        tool_pins={'tools/recovery/geometry_8141386a_review_ef123_bytes.py':sha_file(Path(__file__)),str((RAW/'peer-vtable123-probe.json.gz').relative_to(ROOT)):sha_file(RAW/'peer-vtable123-probe.json.gz')},
                        scope='Fresh read-only original libraries/metadata static bytes, no runtime/code execution. Native replay is separate and uses declared retained-byte fixture state.')
            (RAW/'fresh-original.json.gz').write_bytes(gzip.compress(canonical(result)+b'\n',mtime=0))
            print('fresh original:',len(candidates),'band candidates;',len(global_graph),'global graph RELAs;',len(graph_bls),'direct branches; marker kind/index/value',kind,index,literal.decode('utf8'),flush=True)
        finally:unity.close();il.close()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--xapk',type=Path,required=True);recover(p.parse_args().xapk)
