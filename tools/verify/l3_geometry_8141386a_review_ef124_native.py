"""R1 addendum independent native factory harness; no producer verifier imports.
provenance: arena/8141386a-windwings-space-shooter-game-p
Retained original bytes + declared synthetic allocator/owner/pool/TLS/node state,
same Unicorn backend. Not game-state recovery or Android/Unity execution.
"""
from __future__ import annotations
from collections import Counter
import gzip
import json
import struct
from tools.verify.geometry_8141386a_atlas_io import ROOT
from tools.verify.l3_geometry_8141386a_review_ef123_native import source_image as source123

RAW=ROOT/'reverse-engineering/raw/geometry-8141386a/review-ef124'
FACTORIES={0x6d25f4:(0x6d6a1c,0x10b1440,0x178,0x6d2660),0x6d2664:(0x6d850c,0x10b1730,0x170,0x6d26d0),0x6d26d4:(0x6d2894,0x10b1150,0x180,0x6d2740),0x6d2744:(0x6d81f8,0x10b1640,0x120,0x6d27b0)}


def source_image():
    memory,relas,imports=source123();r=json.loads(gzip.decompress((RAW/'peer-nodefactories124-probe.json.gz').read_bytes()))
    for w in r['windows']+r['cells']:
        for i,b in enumerate(bytes.fromhex(w['hex'])):
            a=w['va']+i
            if a in memory and memory[a]!=b:raise ValueError('123/124 native-byte overlap conflict')
            memory[a]=b
    for x in r['relocations']:
        if x['address']in relas and relas[x['address']]!=x['addend']:raise ValueError('123/124 RELA overlap conflict')
        relas[x['address']]=x['addend']
    for x in r['imports']:
        if x['address']in imports and imports[x['address']]!=x['name']:raise ValueError('123/124 import conflict')
        imports[x['address']]=x['name']
    return memory,relas,imports


def replay(entry=0x6d25f4,prefill=0xa5,label=94,extra=0,tag=0,owner_count=41,base=0x3000000):
    from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_MEM_READ
    from unicorn import arm64_const as reg
    if entry not in FACTORIES or not 0<=extra<=0x100 or prefill not in range(256):raise ValueError('outside declared bounded factory inputs')
    constructor,vptr,size_offset,ret_pc=FACTORIES[entry];memory,relas,imports=source_image()
    u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);u.mem_map(0,0x1200000);u.mem_map(base,0x100000)
    start=prev=None;buf=bytearray()
    for a in sorted(memory):
        if prev is not None and a!=prev+1:u.mem_write(start,bytes(buf));buf.clear();start=None
        if start is None:start=a
        buf.append(memory[a]);prev=a
    if buf:u.mem_write(start,bytes(buf))
    allowed=set(memory)
    def put(a,b):u.mem_write(a,b)
    def q(a,v):put(a,struct.pack('<Q',v))
    def w(a,v):put(a,struct.pack('<I',v&0xffffffff))
    def rq(a):return struct.unpack('<Q',u.mem_read(a,8))[0]
    def rw(a):return struct.unpack('<I',u.mem_read(a,4))[0]
    for a,v in relas.items():q(a,v);allowed.update(range(a,a+8))
    node=base+0x4000;owner=base+0x80000;service=base+0x70000;tls=base+0x60000;stop=base+0x1fff0
    queue=service+0x1000;chunk=service+0x2000;slots=service+0x3000
    prepared=[(base,base+0x20000),(owner,owner+0x100),(service,service+0x10000),(tls,tls+0x100),(0x116cb40,0x116cb48)]
    for lo,hi in prepared:put(lo,b'\0'*(hi-lo))
    put(node,bytes([prefill])*0x400);q(owner+0x48,owner+0x40);w(owner+0x34,owner_count)
    q(tls+0x28,0x1122334455667788);u.reg_write(reg.UC_ARM64_REG_TPIDR_EL0,tls)
    q(0x116cb40,service);q(service+0x450,queue);q(queue,chunk);q(queue+8,tag);q(chunk+0x40,slots);q(chunk+0x58,8);put(slots,b'\xa5'*32)
    memset_sink=base+0x90000;fail_sink=base+0x90100
    if imports.get(0x10e3d10)!='memset' or imports.get(0x10e3d00)!='__stack_chk_fail':raise ValueError('original import binding differs')
    q(0x10e3d10,memset_sink);q(0x10e3d00,fail_sink)
    for a in (0x10e3d10,0x10e3d00):allowed.update(range(a,a+8))
    hits=Counter();visits=[];alloc=[];writes=[];static_reads=set()
    def x(i):return u.reg_read(getattr(reg,'UC_ARM64_REG_X'+str(i)))
    def code(cpu,pc,size,_):
        if pc==stop:cpu.emu_stop();return
        if pc==0x3c986c:
            args=[x(i) for i in range(6)]
            if args!=[extra+size_offset,16,94,0,0x12da21,0xab] or memory.get(0x12da21)!=0:raise ValueError('allocator request/empty original label differs')
            alloc.append(dict(args=args,result=node));u.reg_write(reg.UC_ARM64_REG_X0,node);u.reg_write(reg.UC_ARM64_REG_PC,x(30));return
        if pc==memset_sink:raise ValueError('unanticipated memset service reached in selected factory case')
        if pc==fail_sink:raise ValueError('stack-canary failure reached')
        if not all(pc+i in memory for i in range(size)):raise ValueError('uncaptured original instruction '+hex(pc))
        hits[pc]+=1;visits.append(pc)
    def mem(cpu,access,a,n,value,_):
        synthetic=any(lo<=a and a+n<=hi for lo,hi in prepared)
        if access==UC_MEM_READ:
            if not synthetic and not all(a+i in allowed for i in range(n)):raise ValueError('uncaptured/unprepared original data read '+hex(a))
            if not synthetic:static_reads.add((a,n))
        else:
            if not synthetic:raise ValueError('native write outside declared state '+hex(a))
            writes.append(dict(pc=u.reg_read(reg.UC_ARM64_REG_PC),address=a,size=n,value=value))
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem)
    u.reg_write(reg.UC_ARM64_REG_X0,owner);u.reg_write(reg.UC_ARM64_REG_X1,label);u.reg_write(reg.UC_ARM64_REG_X2,extra);u.reg_write(reg.UC_ARM64_REG_X30,stop);u.reg_write(reg.UC_ARM64_REG_SP,base+0x1f000)
    u.emu_start(entry,stop+4,count=10000)
    if u.reg_read(reg.UC_ARM64_REG_PC)!=stop or visits[-1]!=ret_pc or x(0)!=node:raise ValueError('factory entry/RET/return mismatch')
    if u.reg_read(reg.UC_ARM64_REG_SP)!=base+0x1f000 or rq(tls+0x28)!=0x1122334455667788:raise ValueError('stack/canary preservation mismatch')
    if rq(node)!=vptr:raise ValueError('constructor-installed vptr differs')
    return dict(entry=entry,prefill=prefill,label=label,extra=extra,tag=tag,owner_count=owner_count,base=base,ret=visits[-1],return_node=x(0),
                instruction_count=len(visits),unique_executed_addresses=sorted(hits),pc_counts={hex(p):n for p,n in sorted(hits.items())},allocator_calls=alloc,
                node=dict(address=node,vptr=rq(node),label=rw(node+0x18),owner=rq(node+0x20),chunk=rq(node+0x30),flags38=rw(node+0x38),halfword_a8=struct.unpack('<H',u.mem_read(node+0xa8,2))[0],
                          word118=rw(node+0x118),byte16c=bytes(u.mem_read(node+0x16c,1))[0],word16c=rw(node+0x16c),byte170=bytes(u.mem_read(node+0x170,1))[0],qword178=rq(node+0x178)),
                owner=dict(count=rw(owner+0x34),head=rq(owner+0x48),flags16=struct.unpack('<H',u.mem_read(owner+0xac,2))[0]),
                pool=dict(head=rq(queue),tag=rq(queue+8),acquired=rw(service+0x43c),chunk_length=rq(chunk+0x50),slot0=rq(slots)),
                native_writes=writes,static_reads=[dict(address=a,size=n) for a,n in sorted(static_reads)],
                evidence_tier='Own Unicorn harness/shared retained original bytes and explicit prepared allocator/owner/pool/TLS state. No producer124/Fixture import, native allocator/heap, serialized graph-builder execution, Android/Unity readback/runtime/render.')
