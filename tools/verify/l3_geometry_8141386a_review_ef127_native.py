"""R1/123 separate original entry-to-RET null-domain harness.
provenance: arena/8141386a-windwings-space-shooter-game-p
Own fresh bytes only, no producer graph127/Fixture import or execution. Shared
Unicorn and explicit node/TLS/stack protocol; one null-deallocator synthetic sink.
Single emu_start, no staged intervals or fabricated non-null object. Only host PC
write is the explicit deallocator's return to the original LR.
"""
from __future__ import annotations

from collections import Counter
import gzip
import json
import struct
from tools.verify.geometry_8141386a_atlas_io import ROOT, sha, sha_file

RAW = ROOT / 'reverse-engineering/raw/geometry-8141386a/review-ef127'
SOURCE_HEAD = '6d7de553ae66a57dd8d880a536aa4dd6751bdb2d'
SOURCE_RUN = 40404773695
UNITY = 'd827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7'
GB = 0x6cf7b4
CLEANUP = 0x6ceeb0
FREE = 0x3c9438
EPILOGUE = 0x6cff0c
RET = 0x6cff3c
CANARY = 0x1122334455667788
VARIANTS = ((0xa5, 0x3000000), (0, 0x3000000), (0xa5, 0x4000000))
FIELDS = {'slot118': (0x118,8), 'slot1a0': (0x1a0,8), 'slot1c0': (0x1c0,8),
          'count1c8': (0x1c8,4), 'category_c8': (0xc8,4),
          'slot128': (0x128,8), 'slot130': (0x130,8), 'slot138': (0x138,8),
          'slot140': (0x140,8), 'slot180': (0x180,8)}


def read(name):
    return json.loads(gzip.decompress((RAW/name).read_bytes()))


def source_image():
    fresh = read('fresh-original.json.gz'); ci = read('source-ci-receipt.json.gz')
    r = ci['run']
    if (r['id'],r['head_sha'],r['status'],r['conclusion']) != (SOURCE_RUN,SOURCE_HEAD,'completed','success'):
        raise ValueError('own original127 source is not actual exact-head GREEN')
    if sha_file(RAW/'fresh-original.json.gz') != ci['fresh_original_sha256'] or fresh['libunity_sha256'] != UNITY:
        raise ValueError('own fresh original127 identity differs')
    memory = {}
    for row in fresh['peer_selected_spans']:
        b = bytes.fromhex(row['hex'])
        if len(b) != row['size'] or sha(b) != row['sha256']:
            raise ValueError('original127 span hash/size differs')
        for i,v in enumerate(b):
            a = row['va']+i
            if a in memory and memory[a] != v:
                raise ValueError('conflicting original127 overlap')
            memory[a] = v
    fdes = {r['start']:r for r in fresh['selected_fdes']}
    allowed = {pc for a in (GB,CLEANUP) for pc in range(a,fdes[a]['end_exclusive'],4)}
    return memory, allowed, fresh


def replay(prefill=0xa5, base=0x3000000, *, drop_instruction=None, free_sink=True,
           fault_canary=False, fault_unprepared_tls=False):
    from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE, UC_MEM_READ
    from unicorn import arm64_const as reg
    if (prefill,base) not in VARIANTS:
        raise ValueError('outside three declared null-domain variants')
    original, allowed_pcs, _ = source_image()
    if drop_instruction is not None:
        for i in range(4): original.pop(drop_instruction+i,None)
    u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);u.mem_map(0,0x1200000);u.mem_map(base,0x100000)
    begin = old = None; block=bytearray()
    for a in sorted(original):
        if old is not None and a != old+1:
            u.mem_write(begin,bytes(block));block.clear();begin=None
        if begin is None: begin=a
        block.append(original[a]);old=a
    if block: u.mem_write(begin,bytes(block))
    node=base+0x4000;tls=base+0x6000;sp=base+0x1f000;stop=base+0x1fff0
    prepared=[(node,node+0x200,'PREPARED_NODE'),(tls,tls+0x100,'PREPARED_TLS'),
              (base+0x1c000,base+0x20000,'PREPARED_STACK')]
    for lo,hi,_ in prepared:u.mem_write(lo,bytes(hi-lo))
    u.mem_write(node,bytes([prefill])*0x200)
    for off,n in ((0x118,8),(0x1a0,8),(0x1c0,8),(0x1c8,4)):
        u.mem_write(node+off,bytes(n))
    u.mem_write(tls+0x28,struct.pack('<Q',CANARY))
    def x(i):return u.reg_read(getattr(reg,'UC_ARM64_REG_X'+str(i)))
    def q(a):return struct.unpack('<Q',u.mem_read(a,8))[0]
    def fields():return {name:int.from_bytes(u.mem_read(node+off,n),'little') for name,(off,n) in FIELDS.items()}
    before=fields()
    saved_before={f'x{i}':0x1900000000000000+i for i in range(19,30)}
    saved_before.update(d8=0x1100000000000008,d9=0x2200000000000009)
    for name,value in saved_before.items():u.reg_write(getattr(reg,'UC_ARM64_REG_'+name.upper()),value)
    u.reg_write(reg.UC_ARM64_REG_TPIDR_EL0,0x100000 if fault_unprepared_tls else tls)
    u.reg_write(reg.UC_ARM64_REG_X0,node);u.reg_write(reg.UC_ARM64_REG_X30,stop);u.reg_write(reg.UC_ARM64_REG_SP,sp)
    for i in range(1,8):u.reg_write(getattr(reg,'UC_ARM64_REG_X'+str(i)),0)
    visits=[];reads=[];writes=[];services=[];host_pc_writes=[];canary_checks=[];stopped=False

    def code(cpu,pc,size,_):
        nonlocal stopped
        if pc==stop:
            stopped=True;cpu.emu_stop();return
        if pc==FREE:
            if not free_sink:raise ValueError('original heap prohibited: null-deallocator sink disabled')
            if not visits or visits[-1]!=0x6cef44 or x(30)!=0x6cef48 or x(0)!=0:
                raise ValueError('deallocator outside declared null-call protocol')
            category=int.from_bytes(bytes([prefill])*4,'little')
            if (x(1)&0xffffffff,x(2),x(3))!=(category,0x12da21,0x24) or original.get(0x12da21)!=0:
                raise ValueError('original null-deallocator argument/label contract differs')
            services.append(dict(symbol='dealloc_3c9438',object=x(0),category=x(1)&0xffffffff,
                call_pc=visits[-1],label_va=x(2),line=x(3),boundary='SYNTHETIC_NULL_DEALLOCATOR_ONLY'))
            host_pc_writes.append(dict(origin='SYNTHETIC_FREE_RETURN_TO_ORIGINAL_LR',from_pc=pc,to_pc=x(30)))
            cpu.reg_write(reg.UC_ARM64_REG_PC,x(30));return
        if pc==0x6cff40:
            raise ValueError('original canary-failure branch reached; excluded PLT not executed')
        if 0x6cf7f0<=pc<EPILOGUE:
            raise ValueError('non-null build path outside declared domain')
        if pc not in allowed_pcs:
            raise ValueError('outside original graph/cleanup FDE domain: '+hex(pc))
        if size!=4 or not all(pc+i in original for i in range(4)):
            raise ValueError('uncaptured original127 instruction: '+hex(pc))
        if pc==EPILOGUE:
            if fault_canary:u.mem_write(tls+0x28,struct.pack('<Q',CANARY^1))
            frame_sp=cpu.reg_read(reg.UC_ARM64_REG_SP)
            canary_checks.append(dict(load_tls_pc=pc,load_saved_pc=0x6cff10,compare_pc=0x6cff14,
                branch_pc=0x6cff18,tls_address=tls+0x28,saved_address=frame_sp+0xc8,
                tls_value=q(tls+0x28),saved_value=q(frame_sp+0xc8)))
        visits.append(pc)

    def memory(cpu,access,a,n,value,_):
        tier=next((name for lo,hi,name in prepared if lo<=a and a+n<=hi),None)
        pc=cpu.reg_read(reg.UC_ARM64_REG_PC)
        if access==UC_MEM_READ:
            if tier is None and not all(a+i in original for i in range(n)):
                raise ValueError('uncaptured/unprepared original127 native data: '+hex(a))
            reads.append(dict(pc=pc,address=a,size=n,tier=tier or 'CAPTURED_ORIGINAL_BYTES'))
        else:
            if tier is None:raise ValueError('native127 write outside declared prepared state')
            writes.append(dict(pc=pc,address=a,size=n,value=value&((1<<(n*8))-1),tier=tier))
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,memory)
    # One original entry, no staged intervals. The declared sink returns to original LR.
    u.emu_start(GB,stop+4,count=10000)
    saved_after={name:u.reg_read(getattr(reg,'UC_ARM64_REG_'+name.upper())) for name in saved_before}
    if not stopped or u.reg_read(reg.UC_ARM64_REG_PC)!=stop or u.reg_read(reg.UC_ARM64_REG_SP)!=sp or visits[-1]!=RET:
        raise ValueError('original127 did not execute entry-to-RET with restored stack')
    if saved_after!=saved_before or q(tls+0x28)!=CANARY:
        raise ValueError('original callee-saved/TLS preservation differs')
    hits=Counter(visits)
    edges=[dict(from_pc=a,to_pc=b) for a,b in zip(visits,visits[1:]) if b!=a+4]
    coverage={hex(a):dict(executed_unique=sum(a<=pc<end for pc in hits),fde_instruction_words=(end-a)//4,
              end_exclusive=end) for a,end in ((GB,0x6cff44),(CLEANUP,0x6cef64))}
    return dict(prefill=prefill,base=base,entry=GB,entry_count=hits[GB],emu_start_calls=1,
        addresses=dict(node=node,tls=tls,stack_pointer=sp,stop=stop),native_instruction_count=len(visits),
        executed_addresses=sorted(hits),chronological_native_pcs=visits,pc_counts={hex(pc):n for pc,n in sorted(hits.items())},
        original_nonsequential_edges=edges,body_coverage=coverage,service_calls=services,host_pc_writes=host_pc_writes,
        node_before=before,node_after=fields(),native_memory_reads=reads,native_memory_writes=writes,
        canary_checks=canary_checks,callee_saved_before=saved_before,callee_saved_after=saved_after,
        last_native_pc=visits[-1],return_value=x(0),stack_pointer_after=u.reg_read(reg.UC_ARM64_REG_SP),stop_pc=u.reg_read(reg.UC_ARM64_REG_PC),
        boundary='Original whole-FDE entry-to-RET path, NOT complete FDE instruction coverage or build-path execution. Prepared null node/TLS/stack/register state and one uncounted null-deallocator sink. No original heap, non-null owner/motion object, Unity/game instance, serialized rediscovery or runtime.')
