"""Original native schema-generator execution with explicit synthetic metadata sink.
Not Unity TypeTree readback: Only begin-node allocation/string interning is modeled; native end/align/setters execute.
"""
import struct
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn.arm64_const import UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X2,UC_ARM64_REG_X3,UC_ARM64_REG_X4,UC_ARM64_REG_X30,UC_ARM64_REG_PC,UC_ARM64_REG_SP,UC_ARM64_REG_TPIDR_EL0

def generate(raw,entry=0xb7e1bc,object_address=0x3000000):
    u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);mapped=set();code=[];source_spans=[];source_reads=set()
    def put(a,b,original=True):
        if original:source_spans.append((a,a+len(b)))
        for page in range(a&~4095,(a+len(b)+4095)&~4095,4096):
            if page not in mapped:u.mem_map(page,4096);mapped.add(page)
        u.mem_write(a,b)
    def q(a):return struct.unpack('<Q',u.mem_read(a,8))[0]
    def w(a):return struct.unpack('<i',u.mem_read(a,4))[0]
    def setq(a,v):u.mem_write(a,struct.pack('<Q',v))
    def seti(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
    for n in raw['native_evidence']['ranges']:
        b=bytes.fromhex(n['hex']);put(n['va'],b);code.append((n['va'],n['va']+len(b)))
    for n in raw['native_evidence']['cells']:put(n['va'],bytes.fromhex(n['hex']))
    string_addresses={r['target'] for r in raw['references'] if any(a<=r['va']<z for a,z in code)}|{c['va'] for c in raw['native_evidence']['cells']}
    for s in raw['strings']:
        for o in s['occurrences']:
            if o['va'] in string_addresses:put(o['va'],bytes.fromhex(o['hex']))
    for r in raw['native_evidence']['relocations']:put(r['address'],struct.pack('<Q',r['addend']))
    OBJ=object_address;BUILDER=0x3010000;HOLDER=0x3020000;NODES=0x3100000;STACK=0x4000000;STOP=0x5000000
    for a,n in [(OBJ,4096),(BUILDER,4096),(HOLDER,4096),(NODES,1024*1024),(STACK,65536),(STOP,4096),(0x6000000,4096)]:put(a,b'\0'*n,original=False)
    setq(HOLDER,NODES);setq(HOLDER+16,1);setq(HOLDER+0x20,NODES+0x90000);setq(HOLDER+0x40,NODES+0x80000);setq(BUILDER+0x40,HOLDER+256);setq(BUILDER+0x48,HOLDER)
    nodes=[dict(type='AnimatorController',name='Base',children=[],address=NODES,pc=None)];events=[];visited=set();count=0
    u.mem_write(NODES,struct.pack('<H',1))
    def text(a):
        assert a,'null native type/name pointer';b=bytearray()
        for _ in range(4096):
            assert any(lo<=a+len(b)<hi for lo,hi in source_spans),'uncaptured native string byte'
            x=u.mem_read(a+len(b),1)[0]
            if x==0:return b.decode()
            b.append(x)
        raise ValueError('unterminated native name')
    def ret():u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_X30))
    def hook(uc,pc,size,data):
        nonlocal count
        count+=1;visited.add(pc)
        assert count<1000000,'instruction budget'
        if pc==STOP:uc.emu_stop();return
        if pc==0x5eb544:
            assert uc.reg_read(UC_ARM64_REG_X0)==BUILDER
            name=text(uc.reg_read(UC_ARM64_REG_X1));typ=text(uc.reg_read(UC_ARM64_REG_X2));flag=uc.reg_read(UC_ARM64_REG_X4)&0xffffffff;parent_index=q(BUILDER+0x50);parent=nodes[parent_index];i=len(nodes);addr=NODES+i*32
            flag=(w(parent['address']+20)|flag)&~0x8000
            assert i<4096,'node capacity budget'
            node=dict(type=typ,name=name,children=[],address=addr,pc=uc.reg_read(UC_ARM64_REG_X30)-4);nodes.append(node);parent['children'].append(i)
            uc.mem_write(addr,struct.pack('<HBB',1,uc.mem_read(parent['address']+2,1)[0]+1,0));seti(addr+20,flag);uc.mem_write(NODES+0x80000,b'\xff'*(len(nodes)*4));uc.mem_write(NODES+0x90000+i,bytes(uc.mem_read(addr+2,1)));setq(HOLDER+16,len(nodes));setq(BUILDER+0x50,i);events.append(dict(op='begin',node=i,parent=parent_index,name=name,type=typ,flags=flag,name_va=uc.reg_read(UC_ARM64_REG_X1),type_va=uc.reg_read(UC_ARM64_REG_X2),pc=node['pc']));ret();return
        if pc in (0x5eb6b0,0x5eb84c):events.append(dict(op='end' if pc==0x5eb6b0 else 'align',node=q(BUILDER+0x50),pc=uc.reg_read(UC_ARM64_REG_X30)-4))
        assert any(a<=pc<a1 for a,a1 in code),f'uncaptured native call {pc:x}'
    def read_guard(uc,access,address,size,value,data):
        if any(a<=address and address+size<=a+n for a,n in [(OBJ,4096),(BUILDER,4096),(HOLDER,4096),(NODES,1024*1024),(STACK,65536),(0x6000000,4096)]):return
        assert any(a<=address and address+size<=b for a,b in source_spans),f'uncaptured native data read {address:x}+{size}'
        source_reads.add((address,size))
    u.hook_add(UC_HOOK_MEM_READ,read_guard)
    u.reg_write(UC_ARM64_REG_TPIDR_EL0,0x6000000);u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM64_REG_SP,STACK+65536-16);u.reg_write(UC_ARM64_REG_X0,OBJ);u.reg_write(UC_ARM64_REG_X1,BUILDER);u.reg_write(UC_ARM64_REG_X30,STOP)

    try:u.emu_start(entry,STOP+4,count=1000000)
    except Exception as e:raise ValueError(f'native fixture PC={u.reg_read(UC_ARM64_REG_PC):x}, last_events={events[-3:]}') from e
    assert u.reg_read(UC_ARM64_REG_PC)==STOP,'instruction budget exhausted before return'
    assert q(BUILDER+0x50)==0,('unbalanced metadata sink',q(BUILDER+0x50))
    def schema(i):
        n=nodes[i];return dict(type=n['type'],name=n['name'],byte_size=w(n['address']+12),meta_flag=w(n['address']+20),version=struct.unpack('<H',u.mem_read(n['address'],2))[0],type_flags=u.mem_read(n['address']+3,1)[0],children=[schema(c) for c in n['children']])
    return dict(schema=schema(0),events=events,executed_addresses=sorted(visited-{STOP,0x5eb544}),instruction_count=count-sum(e['op']=='begin' for e in events)-1,code_hook_visits=count,entry=entry,sink_hooks=[0x5eb544],source_reads=[dict(va=a,size=s) for a,s in sorted(source_reads)])
