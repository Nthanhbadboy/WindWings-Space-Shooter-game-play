"""Original vtable-backed graph populator: real virtual methods, explicit allocator/memset services."""
import argparse,gzip,hashlib,json,struct
from collections import Counter
from pathlib import Path
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import UC_ARM64_REG_PC,UC_ARM64_REG_S0,UC_ARM64_REG_SP,UC_ARM64_REG_TPIDR_EL0,UC_ARM64_REG_X4,UC_ARM64_REG_X5,UC_ARM64_REG_X8
from tools.verify import graph122,factory121,node120,parent119,caller118,packed115
from tools.verify.caller118_native import combine
from tools.verify.tag23_113_native import Fixture
ROOT=Path(__file__).resolve().parents[2];RAW=ROOT/'reverse-engineering/raw/vtable123/probe.json.gz';OUT=ROOT/'datas/l3_ef6b75ef123_native_vtable_graph.json.gz'
CANARY=0x1122334455667788;VPTR=0x10b1150;SLOTS={0x10:0x571b3c,0x18:0x571a80,0x70:0x6d5134}
def raw():return json.load(gzip.open(RAW))
def merged():return combine(graph122.merged(),raw())
def fixture_raw(r):return dict(windows=r['windows'],native_slices=r['cells'],strings=r['strings'],relocations=r['relocations'],imports=r.get('imports',[]),pointed_strings=r.get('pointed_strings',[]))
def plt_binding(f,raw,plt,symbol,sink):
    w0,w1,_,w3=struct.unpack('<4I',f.source(plt,16))
    assert w0&0x9f00001f==0x90000010 and w1&0xffc003ff==0xf9400211 and w3==0xd61f0220,(hex(plt),w0,w1,w3)
    imm=((w0>>5)&0x7ffff)<<2|((w0>>29)&3);imm=imm-(1<<21) if imm&(1<<20) else imm
    slot=(plt&~4095)+(imm<<12)+((w1>>10)&4095)*8
    names={x['name'] for x in raw['imports'] if x['address']==slot}
    assert names=={symbol},(hex(plt),hex(slot),names)
    f.put(sink,b'\0'*4,False);f.sq(slot,sink)
    return dict(plt=plt,slot=slot,symbol=symbol,sink=sink,original_plt_hex=f.source(plt,16).hex())
def prepare(f,count,node_blocks,manager,list_owner,service,tls,prefill=0xa5,tag=0,owner_count=41):
    assert len(node_blocks)==count and 0<=count<=8
    r=merged();service_calls=[];failures=[];allocator_records=[];node_iter=iter(node_blocks)
    sinks=(f.base+0x84000,f.base+0x84100)
    bindings=[plt_binding(f,r,0x109ace0,'memset',sinks[0]),plt_binding(f,r,0x109acc0,'__stack_chk_fail',sinks[1])]
    f.put(manager,bytes(0x200),False);f.sq(manager,VPTR);f.sq(manager+0x20,list_owner);f.sq(manager+0x30,service+0x4000);f.sw(manager+0x38,0);f.sq(manager+0x50,0);f.put(manager+0x100,b'\xa5',False);f.sq(manager+0x128,0);f.sq(manager+0x140,2*count);f.sq(manager+0x148,0);f.sq(manager+0x160,2*count)
    f.put(list_owner,bytes(0x100),False);f.sq(list_owner+0x20,0);f.sw(list_owner+0x34,owner_count);f.sq(list_owner+0x48,list_owner+0x40);f.sw(list_owner+0xac,0)
    for node in node_blocks:f.put(node,bytes([prefill])*0x400,False)
    f.put(tls,bytes(0x100),False);f.sq(tls+0x28,CANARY);f.u.reg_write(UC_ARM64_REG_TPIDR_EL0,tls)
    f.put(service,bytes(0x10000),False);f.sq(0x116cb40,service);queue=service+0x1000;f.sq(service+0x450,queue);f.sq(queue,service+0x2000 if count else 0);f.sq(queue+8,tag)
    chunks=[service+0x2000+i*0x100 for i in range(count)];slots=[service+0x3000+i*0x80 for i in range(count)]
    for i,chunk in enumerate(chunks):
        f.sq(chunk,chunks[i+1] if i+1<count else 0);f.sq(chunk+0x40,slots[i]);f.sq(chunk+0x50,0);f.sq(chunk+0x58,8);f.sq(slots[i],0)
    mgr_chunk=service+0x4000;mgr_array=service+0x5000
    f.sq(mgr_chunk,0);f.sq(mgr_chunk+0x20,mgr_array);f.sq(mgr_chunk+0x30,0);f.sq(mgr_chunk+0x38,2*count);f.sq(mgr_chunk+0x40,0);f.sq(mgr_chunk+0x50,0)
    f.put(mgr_array,bytes([0xa5])*max(16,count*16),False)
    def memset(f):
        dest,value,length=f.reg(0),f.reg(1)&0xff,f.reg(2);assert value==0 and dest==mgr_array and length==count*16
        f.put(dest,bytes(length),False);service_calls.append(dict(symbol='memset',dest=dest,value=value,length=length));f.ret()
    def fail(f):
        failures.append(dict(symbol='__stack_chk_fail',pc=f.u.reg_read(UC_ARM64_REG_PC)));raise RuntimeError('original stack canary failure reached')
    def allocate(f):
        x4=f.u.reg_read(UC_ARM64_REG_X4);x5=f.u.reg_read(UC_ARM64_REG_X5)&0xffffffff
        rec=dict(size=f.reg(0),alignment=f.reg(1),category=f.reg(2)&0xffffffff,flag=f.reg(3)&0xffffffff,label=x4,aux=x5)
        allocator_records.append(rec);assert rec==dict(size=0x200,alignment=16,category=94,flag=0,label=0x12da21,aux=0xab);assert bytes(f.source(x4,1))==b'\0'
        f.ret(next(node_iter))
    f.sinks[sinks[0]]=memset;f.sinks[sinks[1]]=fail;f.sinks[0x3c986c]=allocate
    assert not any(a in f.sinks for a in SLOTS.values())
    watch={manager+0x100}|{node+0x100 for node in node_blocks}
    return dict(manager=manager,list_owner=list_owner,service=service,tls=tls,queue=queue,chunks=chunks,slots=slots,mgr_chunk=mgr_chunk,mgr_array=mgr_array,node_blocks=node_blocks,count=count,prefill=prefill,tag=tag,owner_count=owner_count,service_calls=service_calls,failures=failures,allocator_records=allocator_records,bindings=bindings,watch=watch,virtual_calls=[],zero_writes=[])
def execute(f,p):
    count=p['count'];watch=p['watch'];p['virtual_calls'].clear();p['zero_writes'].clear()
    def code_hook(u,pc,size,data):
        if pc not in (0x6d2974,0x6d29c4,0x5710b0):return
        target=u.reg_read(UC_ARM64_REG_X8)
        if pc==0x6d2974:rec=dict(kind='reserve',pc=pc,target=target,manager=f.reg(0),count=f.reg(1)&0xffffffff)
        elif pc==0x6d29c4:rec=dict(kind='notify',pc=pc,target=target,manager=f.reg(0),index=f.reg(1)&0xffffffff,s0_bits=u.reg_read(UC_ARM64_REG_S0)&0xffffffff)
        else:rec=dict(kind='register',pc=pc,target=target,manager=f.reg(0),node=f.reg(1),index=f.reg(2)&0xffffffff,slot=f.reg(3)&0xffffffff)
        p['virtual_calls'].append(rec)
    def mem_hook(u,access,a,n,value,data):
        if a in watch and n==1:p['zero_writes'].append(dict(pc=u.reg_read(UC_ARM64_REG_PC),address=a,size=n))
    h1=f.u.hook_add(UC_HOOK_CODE,code_hook);h2=f.u.hook_add(UC_HOOK_MEM_WRITE,mem_hook)
    try:run=f.call(0x6d2950,(p['manager'],p['list_owner'],count))
    finally:f.u.hook_del(h1);f.u.hook_del(h2)
    hits=Counter(f.visits)
    assert f.visits[-1]==0x6d29e0 and f.u.reg_read(UC_ARM64_REG_PC)==f.stop and f.u.reg_read(UC_ARM64_REG_SP)==f.base+0x1f000 and f.q(p['tls']+0x28)==CANARY
    assert f.q(p['manager'])==VPTR and all(f.q(VPTR+s)==a for s,a in SLOTS.items())
    expected={0x6d2974:1,0x6d2990:count,0x6d5e58:count,0x6d81b0:count,0x57104c:count,0x570abc:count,0x5710b0:count,0x6d29c4:count,0x6d353c:count,0x572a38:count,0x6d29e0:1,0x571b3c:1,0x571b58:1,0x571a80:count,0x6d5134:count,0x6d6c88:count,0x57095c:count,0x6d6c9c:count,0x570a70:2*count}
    for pc,n in expected.items():assert hits[pc]==n,(hex(pc),hits[pc],n)
    if count:assert hits[0x109ace0]>=1
    for pc in (0x573a34,0x3f1d78,0x570ff0,0x3c986c,0x52e15c,0xb2e604,0x3c9438,0x109acc0,0x575b34,0x573a1c):assert pc not in hits,hex(pc)
    assert len(p['allocator_records'])==count and len(p['service_calls'])==(1 if count else 0) and not p['failures'] and len(p['virtual_calls'])==1+2*count
    reserves=[x for x in p['virtual_calls'] if x['kind']=='reserve'];notifies=[x for x in p['virtual_calls'] if x['kind']=='notify'];registers=[x for x in p['virtual_calls'] if x['kind']=='register']
    assert len(reserves)==1 and reserves[0]['target']==SLOTS[0x10] and reserves[0]['count']==count
    assert [x['target'] for x in notifies]==[SLOTS[0x18]]*count and [x['index'] for x in notifies]==list(range(count)) and all(x['s0_bits']==0 for x in notifies)
    assert [x['target'] for x in registers]==[SLOTS[0x70]]*count and [x['index'] for x in registers]==list(range(count)) and [x['node'] for x in registers]==p['node_blocks'] and all(x['slot']==0 for x in registers)
    assert all(x['manager']==p['manager'] for x in p['virtual_calls'])
    nodes=[]
    for i,node in enumerate(p['node_blocks']):
        d=dict(address=node,vptr=f.q(node),owner_field=f.q(node+0x20),chunk_field=f.q(node+0x30),type_field=f.w(node+0x3c),b0_qword=f.q(node+0xb0),b8_pointer=f.q(node+0xb8),byte_100=bytes(f.u.mem_read(node+0x100,1))[0],flags_38=f.w(node+0x38),chunk_length=f.q(p['chunks'][i]+0x50),slot0=f.q(p['slots'][i]))
        assert d['vptr']==0x10b1240 and d['owner_field']==p['list_owner'] and d['chunk_field']==p['chunks'][i] and d['type_field']==7 and d['b0_qword']==0 and d['b8_pointer']==node+0x200 and d['byte_100']==0 and d['flags_38']&0x100 and d['chunk_length']==1 and d['slot0']==p['manager'];nodes.append(d)
    manager_array=[]
    for i,node in enumerate(p['node_blocks']):
        rec=dict(index=i,node_field=f.q(p['mgr_array']+i*16),float_bits=f.w(p['mgr_array']+i*16+8),slot_field=f.w(p['mgr_array']+i*16+0xc))
        assert rec['node_field']==node and rec['float_bits']==0 and rec['slot_field']==0;manager_array.append(rec)
    assert f.q(p['mgr_chunk']+0x20)==p['mgr_array'] and f.q(p['mgr_chunk']+0x30)==count and f.q(p['mgr_chunk']+0x38)==2*count
    assert f.w(p['manager']+0x38)==(0x100 if count else 0) and bytes(f.u.mem_read(p['manager']+0x100,1))[0]==(0 if count else 0xa5)
    assert f.w(p['list_owner']+0x34)==p['owner_count']+count and f.q(p['list_owner']+0x48)==(p['node_blocks'][-1]+8 if count else p['list_owner']+0x40) and struct.unpack_from('<H',f.u.mem_read(p['list_owner']+0xac,2))[0]==(0xc8 if count else 0)
    assert f.q(p['queue'])==0 and f.q(p['queue']+8)==p['tag']+count and f.w(p['service']+0x43c)==count
    if count:
        assert {x['address'] for x in p['zero_writes']}==p['watch'] and {x['pc'] for x in p['zero_writes']}=={0x6d6c9c,0x6d81c4,0x6d81c8}
    return dict(entry=0x6d2950,ret=f.visits[-1],stack_pointer_after=f.u.reg_read(UC_ARM64_REG_SP),stop_pc=f.u.reg_read(UC_ARM64_REG_PC),run=run,pc_hits={hex(k):v for k,v in sorted(hits.items()) if k in set(expected)|{0x109ace0,0x109acc0,0x6d81c4,0x6d81c8,0x6d6c9c}},virtual_calls=list(p['virtual_calls']),service_calls=list(p['service_calls']),failure_calls=list(p['failures']),allocator_records=list(p['allocator_records']),plt_bindings=p['bindings'],zero_writes=list(p['zero_writes']),nodes=nodes,manager_array=manager_array,manager_after=dict(vptr=f.q(p['manager']),owner_field=f.q(p['manager']+0x20),chunk_field=f.q(p['manager']+0x30),flags_38=f.w(p['manager']+0x38),byte_100=bytes(f.u.mem_read(p['manager']+0x100,1))[0],capacity_140=f.q(p['manager']+0x140),capacity_160=f.q(p['manager']+0x160)),manager_chunk_after=dict(data=f.q(p['mgr_chunk']+0x20),length=f.q(p['mgr_chunk']+0x30),capacity=f.q(p['mgr_chunk']+0x38)),list_owner_after=dict(count=f.w(p['list_owner']+0x34),list_head=f.q(p['list_owner']+0x48),flags_halfword=struct.unpack_from('<H',f.u.mem_read(p['list_owner']+0xac,2))[0]),pool_after=dict(queue_head=f.q(p['queue']),queue_tag=f.q(p['queue']+8),acquired_count=f.w(p['service']+0x43c),chunks=[dict(address=c,length=f.q(c+0x50),slot0=f.q(s)) for c,s in zip(p['chunks'],p['slots'])]),vtable=dict(vptr=VPTR,slots={hex(s):f.q(VPTR+s) for s in SLOTS}),scope='Original graph-populator dispatch through original vtable10b1150 and original reserve/notify/register methods, with native factory/constructor/helper/list code. Explicit synthetic allocator at3c986c, original PLT memset service, stack-check failure sink, TLS/pool/manager/list/node storage. NOT original heap, game manager construction, serialized controller graph, clip/clock writers, active pose/apply, Unity readback or render.')
def standalone(count=3,prefill=0xa5,base=0x3000000,owner_count=41,tag=0):
    f=Fixture(fixture_raw(merged()),base);manager=base+0x80000;list_owner=base+0x81000;service=base+0x70000;tls=base+0x60000;node_blocks=[base+0x14000+i*0x1000 for i in range(count)]
    p=prepare(f,count,node_blocks,manager,list_owner,service,tls,prefill,owner_count=owner_count,tag=tag);r=execute(f,p)
    return dict(**r,count=count,prefill=prefill,manager=manager,list_owner=list_owner,service=service,tls=tls,node_blocks=node_blocks,owner_count=owner_count,tag=tag)
def source_fixture():
    args,r119=parent119.raws();row,s,data=packed115.source_stream();extra=merged()
    f=parent119.ParentFixture(*args,raw119=combine(r119,extra),packed=data,continuous=s['curveCount'],discrete=s['discreteCurveCount'])
    manager=f.base+0x80000;list_owner=f.base+0x81000;service=f.base+0x70000;node_blocks=[f.base+0x14000,f.base+0x15000,f.node]
    p=prepare(f,3,node_blocks,manager,list_owner,service,f.tls);graph=execute(f,p)
    for offset,pointer in ((0x118,f.blob),(0x128,f.cache),(0x130,f.holder),(0x1d0,f.native_clip)):f.sq(f.node+offset,pointer)
    m=row['tree']['m_MuscleClip'];f.configure_time(start=m['m_StartTime'],stop=m['m_StopTime'],cycle_offset=m['m_CycleOffset'])
    old=json.load(gzip.open(caller118.OUT));samples=[]
    for previous in old['source']['runs']:
        f.configure_node(current=previous['node_seconds_double'],loop=m['m_LoopTime']);out=f.parent();assert out['output_bits']==previous['native']['output_bits'] and out['completion_byte']==1;samples.append(dict(query=previous['query'],native=out))
    return f,graph,samples
def build():
    cases=[standalone(count,prefill) for count,prefill in ((0,0xa5),(1,0xa5),(3,0xa5),(3,0))]
    f,graph,samples=source_fixture()
    paths=[RAW,graph122.RAW,factory121.RAW,node120.RAW,parent119.RAW,caller118.OUT,factory121.OUT,ROOT/'tools/recovery/vtable123.py',Path(__file__),ROOT/'tests/test_vtable123.py',ROOT/'tools/verify/graph122.py',ROOT/'tools/verify/factory121.py',ROOT/'tools/verify/node120.py',ROOT/'tools/verify/parent119.py',ROOT/'tools/verify/tag23_113_native.py']
    return dict(provisional=True,provenance='arena/ef6b75ef',inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},standalone=cases,source=dict(graph=graph,post_graph_bindings=[0x118,0x128,0x130,0x1d0],clock_control_loop='configure_node fixture inputs, not recovered writers',source_node=f.node,calls=samples),original_vtable=dict(vptr=VPTR,slots={str(k):v for k,v in SLOTS.items()},constructor=0x6d2894,factory=0x6d26d4,graph_caller=0x6cf7b4,graph_call_pcs=[0x6cfc34,0x6cfc44]),counts=dict(standalone_cases=len(cases),standalone_graph_calls=len(cases),standalone_loop_counts=[c['count'] for c in cases],standalone_factory_calls=sum(c['count'] for c in cases),standalone_graph_instructions=[c['run']['instruction_count'] for c in cases],source_graph_calls=1,source_loop_count=3,source_factory_calls=3,source_graph_instructions=graph['run']['instruction_count'],source_calls=len(samples),source_dwords=sum(len(x['native']['output_bits']) for x in samples)),scope='Original vtable-backed graph-populator loop with real native virtual methods on prepared synthetic manager/list/pool/TLS and explicit allocator/memset/stack-check services. Source1609 integration uses one of three prepared factory nodes with post-graph harness bindings and unchanged119parent chain. Shared115–122lineage, not independent extraction, live graph construction, game-side writers, previous/active pose/apply/readback/render. Static native analysis only.')
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();x=build();b=gzip.compress((json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
    if a.check:assert OUT.read_bytes()==b
    else:OUT.write_bytes(b)
    print(json.dumps(dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),counts=x['counts'])))
if __name__=='__main__':main()
