"""R1 independent harness for retained original ef123 graph bytes.
provenance: arena/8141386a-windwings-space-shooter-game-p
Does not import producer vtable123/graph122/Fixture. Same Unicorn implementation,
retained source bytes and explicitly shared fixture contract: NOT Android/Unity.
"""
from __future__ import annotations
from collections import Counter
import gzip
import json
import struct
from tools.verify.geometry_8141386a_atlas_io import ROOT,sha

RAW=ROOT/'reverse-engineering/raw/geometry-8141386a/review-ef123'
PROBES=('peer-vtable123-probe.json.gz','peer-graph122-probe.json.gz','peer-factory121-probe.json.gz','peer-node120-probe.json.gz','peer-caller119-probe.json.gz')


def source_image():
    memory={};relas={};imports={}
    for name in PROBES:
        r=json.loads(gzip.decompress((RAW/name).read_bytes()))
        for w in r['windows']+r['cells']:
            b=bytes.fromhex(w['hex'])
            for i,v in enumerate(b):
                a=w['va']+i
                if a in memory and memory[a]!=v:raise ValueError('retained native source bytes disagree')
                memory[a]=v
        for r in r['relocations']:
            if r['address'] in relas and relas[r['address']]!=r['addend']:raise ValueError('retained RELA overlap disagrees')
            relas[r['address']]=r['addend']
        for r in json.loads(gzip.decompress((RAW/name).read_bytes()))['imports']:
            if r['address'] in imports and imports[r['address']]!=r['name']:raise ValueError('retained import identity disagrees')
            imports[r['address']]=r['name']
    return memory,relas,imports


def replay(count=3,prefill=0xa5):
    from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_MEM_READ
    from unicorn import arm64_const as reg
    if not 0<=count<=8:raise ValueError('declared bounded loop domain')
    original,relas,imports=source_image();u=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
    u.mem_map(0,0x1200000);base=0x3000000;u.mem_map(base,0x100000)
    # Sparse bytes only. Every native instruction/data read is checked below;
    # mapped zero pages do NOT authorize uncaptured instructions or metadata.
    addresses=sorted(original);start=old=None;buf=bytearray()
    for a in addresses:
        if old is not None and a!=old+1:u.mem_write(start,bytes(buf));buf.clear();start=None
        if start is None:start=a
        buf.append(original[a]);old=a
    if buf:u.mem_write(start,bytes(buf))
    allowed_original=set(original)
    def put(a,b):u.mem_write(a,b)
    def q(a,v):put(a,struct.pack('<Q',v))
    def w(a,v):put(a,struct.pack('<I',v&0xffffffff))
    def rq(a):return struct.unpack('<Q',u.mem_read(a,8))[0]
    def rw(a):return struct.unpack('<I',u.mem_read(a,4))[0]
    for a,v in relas.items():q(a,v);allowed_original.update(range(a,a+8))
    manager=base+0x80000;owner=base+0x81000;service=base+0x70000;tls=base+0x60000;stop=base+0x1fff0
    nodes=[base+0x14000+i*0x1000 for i in range(count)];queue=service+0x1000;chunks=[service+0x2000+i*0x100 for i in range(count)];slots=[service+0x3000+i*0x80 for i in range(count)];array=service+0x5000;chunk=service+0x4000
    prepared=[(base,base+0x20000),(manager,manager+0x200),(owner,owner+0x100),(service,service+0x10000),(tls,tls+0x100),(0x116cb40,0x116cb48)]
    for lo,hi in prepared:put(lo,b'\0'*(hi-lo))
    q(manager,0x10b1150);q(manager+0x20,owner);q(manager+0x30,chunk);put(manager+0x100,b'\xa5');q(manager+0x140,2*count);q(manager+0x160,2*count)
    w(owner+0x34,41);q(owner+0x48,owner+0x40)
    for node in nodes:put(node,bytes([prefill])*0x400)
    q(tls+0x28,0x1122334455667788);u.reg_write(reg.UC_ARM64_REG_TPIDR_EL0,tls)
    q(0x116cb40,service);q(service+0x450,queue);q(queue,chunks[0] if chunks else 0)
    for i,c in enumerate(chunks):q(c,chunks[i+1] if i+1<count else 0);q(c+0x40,slots[i]);q(c+0x58,8)
    q(chunk+0x20,array);q(chunk+0x38,2*count);put(array,b'\xa5'*max(16,count*16))
    memset_sink=base+0x84000;fail_sink=base+0x84100
    if imports.get(0x10e3d10)!='memset' or imports.get(0x10e3d00)!='__stack_chk_fail':raise ValueError('original PLT import identity mismatch')
    q(0x10e3d10,memset_sink);q(0x10e3d00,fail_sink)
    allowed_original.update(range(0x10e3d10,0x10e3d18));allowed_original.update(range(0x10e3d00,0x10e3d08))
    hits=Counter();visits=[];allocations=[];services=[];virtual=[];writes=[];static_reads=set();node_iter=iter(nodes)
    def x(i):return u.reg_read(getattr(reg,'UC_ARM64_REG_X'+str(i)))
    def ret(v=None):
        if v is not None:u.reg_write(reg.UC_ARM64_REG_X0,v)
        u.reg_write(reg.UC_ARM64_REG_PC,x(30))
    def code(cpu,pc,size,_):
        if pc==stop:cpu.emu_stop();return
        if pc==0x3c986c:
            args=[x(i) for i in range(6)]
            if args!=[0x200,16,94,0,0x12da21,0xab] or original.get(0x12da21)!=0:raise ValueError('allocator contract not pinned original/fixture values')
            address=next(node_iter);allocations.append(dict(args=args,result=address));ret(address);return
        if pc==memset_sink:
            dest,value,n=x(0),x(1)&255,x(2)
            if (dest,value,n)!=(array,0,count*16):raise ValueError('memset service outside declared contract')
            put(dest,b'\0'*n);services.append(dict(symbol='memset',dest=dest,size=n,value=value));ret(dest);return
        if pc==fail_sink:raise ValueError('native canary failure branch reached')
        if not all(pc+i in original for i in range(size)):raise ValueError('uncaptured original native instruction '+hex(pc))
        hits[pc]+=1;visits.append(pc)
        if pc in (0x6d2974,0x5710b0,0x6d29c4):virtual.append(dict(pc=pc,target=x(8),manager=x(0),a1=x(1),a2=x(2),s0_bits=u.reg_read(reg.UC_ARM64_REG_S0)))
    def memory(cpu,access,a,n,value,_):
        synthetic=any(lo<=a and a+n<=hi for lo,hi in prepared)
        if access==UC_MEM_READ:
            if not synthetic and not all(a+i in allowed_original for i in range(n)):raise ValueError('uncaptured/unprepared native data read '+hex(a))
            if not synthetic:static_reads.add((a,n))
        else:
            if not synthetic:raise ValueError('native write outside prepared declared state '+hex(a))
            if n==1 and (a==manager+0x100 or a in {node+0x100 for node in nodes}):writes.append(dict(pc=u.reg_read(reg.UC_ARM64_REG_PC),address=a,size=n,value=value))
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,memory)
    u.reg_write(reg.UC_ARM64_REG_X0,manager);u.reg_write(reg.UC_ARM64_REG_X1,owner);u.reg_write(reg.UC_ARM64_REG_X2,count);u.reg_write(reg.UC_ARM64_REG_X30,stop);u.reg_write(reg.UC_ARM64_REG_SP,base+0x1f000)
    u.emu_start(0x6d2950,stop+4,count=20000)
    if u.reg_read(reg.UC_ARM64_REG_PC)!=stop or visits[-1]!=0x6d29e0:raise ValueError('not original entry-to-RET termination')
    if u.reg_read(reg.UC_ARM64_REG_SP)!=base+0x1f000 or rq(tls+0x28)!=0x1122334455667788:raise ValueError('stack/canary preservation failed')
    return dict(count=count,prefill=prefill,instruction_count=len(visits),pc_counts={hex(pc):n for pc,n in sorted(hits.items())},unique_executed_addresses=sorted(hits),
                virtual_calls=virtual,allocator_calls=allocations,service_calls=services,byte_writes=writes,
                manager=dict(byte100=bytes(u.mem_read(manager+0x100,1))[0],flags38=rw(manager+0x38),length=rq(chunk+0x30),capacity=rq(chunk+0x38),
                             array=[dict(node=rq(array+i*16),float_bits=rw(array+i*16+8),slot=rw(array+i*16+12)) for i in range(count)]),
                owner=dict(count=rw(owner+0x34),head=rq(owner+0x48),flags16=struct.unpack('<H',u.mem_read(owner+0xac,2))[0]),
                queue=dict(head=rq(queue),tag=rq(queue+8),acquired=rw(service+0x43c)),
                node_states=[dict(address=node,byte100=bytes(u.mem_read(node+0x100,1))[0],vptr=rq(node),owner=rq(node+0x20),chunk=rq(node+0x30),type=rw(node+0x3c),b0=rq(node+0xb0),b8=rq(node+0xb8),flags38=rw(node+0x38)) for node in nodes],
                static_reads=[dict(address=a,size=n) for a,n in sorted(static_reads)],
                evidence_tier='Own harness/retained original bytes on declared producer fixture state, same Unicorn backend. Explicit allocator/memset/canary sinks; NOT independent game-state source, original allocator/heap or Unity/Android runtime.')
