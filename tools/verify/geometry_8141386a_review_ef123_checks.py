"""Independent R1 arithmetic/static-byte checks for ef123, not producer code.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
from __future__ import annotations
import gzip
import json
import struct
from tools.verify.geometry_8141386a_atlas_io import JsonStream,sha


def sign(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value


def branch(word,pc):
    if word&0x7c000000!=0x14000000:return None
    return dict(pc=pc,target=pc+sign(word&0x3ffffff,26)*4,link=bool(word&0x80000000),word=word)


def adrp(word,pc):
    if word&0x9f000000!=0x90000000:return None
    return word&31,(pc&~4095)+(sign((((word>>5)&0x7ffff)<<2)|((word>>29)&3),21)<<12)


def add_imm(word):
    if word&0xff800000!=0x91000000:return None
    return word&31,(word>>5)&31,((word>>10)&0xfff)<<(12 if word&(1<<22) else 0)


def constant_stores(blob,va):
    regs={};stores=[]
    for off in range(0,len(blob)-3,4):
        w=struct.unpack_from('<I',blob,off)[0];p=adrp(w,va+off);a=add_imm(w)
        if p:regs[p[0]]=p[1]
        elif a:
            rd,rn,n=a
            if rn in regs:regs[rd]=regs[rn]+n
            else:regs.pop(rd,None)
        elif w&0xffc00000==0xf9000000:
            rt,rn=w&31,(w>>5)&31
            if rt in regs:stores.append(dict(pc=va+off,value=regs[rt],base_register=rn,offset=((w>>10)&4095)*8,hex=blob[off:off+4].hex()))
        elif w&0xfc000000==0x94000000:
            for r in range(19):regs.pop(r,None)
    return stores


def candidate_sets(relocations):
    r={x['address']:x['addend'] for x in relocations};band={a:v for a,v in r.items() if 0x10b1000<=a<0x10b1500 and 0x6d0000<=v<0x6d9000}
    naive=[base for base in range(0x10b1000,0x10b1500-0x70,8) if all(base+s in band for s in (0x10,0x18,0x70))]
    exact=[base for base in range(0x10b1000,0x10b1500-0x70,8) if r.get(base+0x10)==0x571b3c and r.get(base+0x18)==0x571a80 and base+0x70 in r]
    return dict(band_entry_count=len(band),naive=naive,exact_reserve_notify=exact,intersection=sorted(set(naive)&set(exact)),
                exact_slots=[dict(vptr=base,reserve=r[base+0x10],notify=r[base+0x18],register=r[base+0x70]) for base in exact])


def decode_rela(hex_value):
    b=bytes.fromhex(hex_value)
    if len(b)!=24:raise ValueError('ELF64 RELA must be24bytes')
    addr,info,addend=struct.unpack('<QQq',b)
    return dict(address=addr,info=info,type=info&0xffffffff,symbol=info>>32,addend=addend,hex=hex_value)


def decode_usage(cell_hex):
    b=bytes.fromhex(cell_hex)
    if len(b)!=8:raise ValueError('retained usage cell width')
    encoded=struct.unpack('<Q',b)[0]
    if encoded>>32 or not encoded&1:raise ValueError('not the declared uninitialized v31 usage token')
    return dict(encoded=encoded,kind=encoded>>29,index=(encoded&0x1fffffff)>>1,lowbit=encoded&1,
                cell_is_utf8_literal=False)


def stream_relocations(path,marker):
    count=0;matches=[];metadata={}
    with gzip.open(path,'rt',encoding='utf8') as h:
        s=JsonStream(h);s.take('{')
        while s.peek()!='}':
            name=s.value();s.take(':')
            if name=='relocations':
                s.take('{')
                while s.peek()!='}':
                    k=s.value();s.take(':');v=s.value();count+=1
                    if int(k,0)==marker:matches.append(dict(address=int(k,0),addend=int(v,0)))
                    if s.peek()==',':s.take(',')
                    else:break
                s.take('}')
            else:metadata[name]=s.value()
            if s.peek()==',':s.take(',')
            else:break
        s.take('}')
        if s.peek():raise ValueError('native relocation trailing data')
    return dict(entries=count,matches=matches,metadata=metadata)


def table_literal(path,address):
    # The15054-row string index is small metadata, not an asset/Graph fixture.
    rows=json.loads(path.read_bytes());matches=[r for r in rows if int(r['address'],0)==address]
    return dict(entry_count=len(rows),matches=matches)
