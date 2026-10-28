"""R1 addendum120 fresh original libunity spans/FDE/RELA, static read only.
provenance: arena/8141386a-windwings-space-shooter-game-p
Reuses frozen own119 ELF64 reader, not producer124 extraction code. Streamed ZIP,
read-only mmap; no SDK/native code execution/peer edits or APK modification.
"""
from __future__ import annotations
import argparse
import gzip
import json
from pathlib import Path
import shutil
import struct
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tools.verify.geometry_8141386a_atlas_io import BRANCH,canonical,sha_file,scratch
from tools.recovery.geometry_8141386a_review_ef123_bytes import Elf,XAPK,UNITY
RAW=ROOT/'reverse-engineering/raw/geometry-8141386a/review-ef124'
VTABLES=(0x10b1150,0x10b1440,0x10b1640,0x10b1730)
FACTORIES={0x6d25f4,0x6d2664,0x6d26d4,0x6d2744}


def recover(xapk):
    if sha_file(xapk)!=XAPK:raise ValueError('original XAPK SHA mismatch')
    with scratch('review124-original-') as d:
        lib=d/'libunity.so';input_info=None
        with zipfile.ZipFile(xapk) as outer:
            for i,name in enumerate(sorted(n for n in outer.namelist() if n.endswith('.apk'))):
                apk=d/f'part-{i}'
                with outer.open(name) as src,apk.open('wb') as dst:shutil.copyfileobj(src,dst,1024*1024)
                with zipfile.ZipFile(apk) as inner:
                    entry='lib/arm64-v8a/libunity.so'
                    if entry not in inner.namelist():continue
                    if input_info is not None:raise ValueError('ambiguous original libunity input')
                    with inner.open(entry) as src,lib.open('wb') as dst:shutil.copyfileobj(src,dst,1024*1024)
                    if sha_file(lib)!=UNITY:raise ValueError('original libunity SHA mismatch')
                    input_info=dict(apk_member=name,entry=entry,size=lib.stat().st_size,sha256=UNITY)
        e=Elf(lib)
        try:
            r=json.loads(gzip.decompress((RAW/'peer-nodefactories124-probe.json.gz').read_bytes()));spans=[];seen=set()
            for w in r['windows']+r['cells']:
                k=(w['va'],len(w['hex'])//2)
                if k in seen:continue
                seen.add(k);v=e.span(*k)
                if v['hex']!=w['hex']:raise ValueError('fresh original124 span differs from retained source')
                spans.append(dict(va=v['va'],size=v['size'],file_offset=v['file_offset'],sha256=v['sha256']))
            relas={};relative_total=0
            for x in e.relas():
                if x['type']!=1027:continue
                relative_total+=1
                if any(base<=x['address']<base+128 for base in VTABLES):relas[x['address']]=x
            groups=[]
            for base in VTABLES:
                slots=[]
                for n in range(16):
                    if base+n*8 not in relas:raise ValueError('vtable slot lacks original relative relocation')
                    slots.append(relas[base+n*8])
                groups.append(dict(vptr=base,slots=slots))
            builder=next(w for w in r['windows'] if w['va']==0x6cf7b4);blob=bytes.fromhex(builder['hex']);calls=[]
            for off in range(0,len(blob)-3,4):
                word=struct.unpack_from('<I',blob,off)[0]
                if word&0xfc000000!=0x94000000:continue
                imm=word&0x3ffffff;imm=imm-(1<<26) if imm&(1<<25) else imm;pc=builder['va']+off;target=pc+4*imm
                if target in FACTORIES:calls.append(dict(pc=pc,target=target,hex=blob[off:off+4].hex()))
            fdes=e.selected_fdes({x['entry'] for x in r['followed']})
            paths=['tools/recovery/geometry_8141386a_review_ef124_bytes.py','tools/recovery/geometry_8141386a_review_ef123_bytes.py',str((RAW/'peer-nodefactories124-probe.json.gz').relative_to(ROOT))]
            out=dict(schema=1,item=120,provenance=BRANCH,xapk_sha256=XAPK,library=input_info,relative_rela_total=relative_total,peer_span_matches=spans,selected_fdes=fdes,vtable_groups=groups,graph_factory_calls=calls,
                     tool_pins={p:sha_file(ROOT/p) for p in paths},scope='Fresh static original spans+FDE+64relative-vtable slots and seven graph BL instructions. No original graph-builder/allocator/game-state execution or runtime.')
            (RAW/'fresh-original.json.gz').write_bytes(gzip.compress(canonical(out)+b'\n',mtime=0));print('fresh124 spans',len(spans),'FDEs',len(fdes),'vtable groups',len(groups),'directBLs',len(calls),flush=True)
        finally:e.close()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--xapk',type=Path,required=True);recover(p.parse_args().xapk)
