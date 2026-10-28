"""Original graph-populator loop over native node factory, with explicit virtual/allocator services."""
import argparse,gzip,hashlib,json,struct
from collections import Counter
from pathlib import Path
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.arm64_const import UC_ARM64_REG_S0,UC_ARM64_REG_SP,UC_ARM64_REG_TPIDR_EL0,UC_ARM64_REG_X4,UC_ARM64_REG_X5
from tools.verify import node120,factory121,parent119,caller118,packed115
from tools.verify.caller118_native import combine
from tools.verify.tag23_113_native import Fixture
ROOT=Path(__file__).resolve().parents[2];RAW=ROOT/'reverse-engineering/raw/graph122/probe.json.gz';OUT=ROOT/'datas/l3_ef6b75ef122_native_graph_populator.json.gz'
CANARY=0x1122334455667788
def raw():return json.load(gzip.open(RAW))
def merged():return combine(node120.raw(),combine(factory121.raw(),raw()))
def fixture_raw(r):return dict(windows=r['windows'],native_slices=r['cells'],strings=r['strings'],relocations=r['relocations'],imports=r.get('imports',[]),pointed_strings=r.get('pointed_strings',[]))
def prepare(f,count,node_blocks,manager,list_owner,service,tls,prefill=0xa5,tag=0,owner_count=41):
    assert len(node_blocks)==count and 0<=count<=8
    sinks_base=f.base+0x83000;vtable=f.base+0x82000
    f.put(vtable,bytes(0x80),False);f.put(sinks_base,bytes(0x400),False)
    for slot,i in ((0x10,0),(0x18,1),(0x70,2)):f.sq(vtable+slot,sinks_base+0x100+i*0x100)
    f.put(manager,bytes([0xa5])*0x120,False);f.sq(manager,vtable);f.put(manager+0x100,b'\xa5',False)
    f.put(list_owner,bytes(0x100),False);f.sq(list_owner+0x48,list_owner+0x40);f.sw(list_owner+0x34,owner_count)
    for node in node_blocks:f.put(node,bytes([prefill])*0x400,False)
    f.put(tls,bytes(0x100),False);f.sq(tls+0x28,CANARY);f.u.reg_write(UC_ARM64_REG_TPIDR_EL0,tls)
    f.put(service,bytes(0x10000),False);f.sq(0x116cb40,service);queue=service+0x1000;f.sq(service+0x450,queue);f.sq(queue,service+0x2000 if count else 0);f.sq(queue+8,tag)
    chunks=[service+0x2000+i*0x100 for i in range(count)];slots=[service+0x3000+i*0x80 for i in range(count)]
    for i,chunk in enumerate(chunks):
        f.sq(chunk,chunks[i+1] if i+1<count else 0);f.sq(chunk+0x40,slots[i]);f.sq(chunk+0x50,0);f.sq(chunk+0x58,8);f.sq(slots[i],0)
    virtual_records=[];allocator_records=[];zero_writes=[];node_iter=iter(node_blocks)
    def reserve(f):
        virtual_records.append(dict(kind='reserve',manager=f.reg(0),count=f.reg(1)&0xffffffff));assert virtual_records[-1]['count']==count;f.ret(0)
    def notify(f):
        virtual_records.append(dict(kind='notify',manager=f.reg(0),index=f.reg(1)&0xffffffff,s0_bits=f.u.reg_read(UC_ARM64_REG_S0)&0xffffffff));assert virtual_records[-1]['s0_bits']==0;f.ret(0)
    def register(f):
        virtual_records.append(dict(kind='register',manager=f.reg(0),node=f.reg(1),index=f.reg(2)&0xffffffff,slot=f.reg(3)&0xffffffff));assert virtual_records[-1]['slot']==0;f.ret(1)
    def allocate(f):
        x4=f.u.reg_read(UC_ARM64_REG_X4);x5=f.u.reg_read(UC_ARM64_REG_X5)&0xffffffff
        rec=dict(size=f.reg(0),alignment=f.reg(1),category=f.reg(2)&0xffffffff,flag=f.reg(3)&0xffffffff,label=x4,aux=x5)
        allocator_records.append(rec);assert rec==dict(size=0x200,alignment=16,category=94,flag=0,label=0x12da21,aux=0xab);assert bytes(f.source(x4,1))==b'\0'
        f.ret(next(node_iter))
    for i,kind in enumerate((reserve,notify,register)):f.sinks[sinks_base+0x100+i*0x100]=kind
    f.sinks[0x3c986c]=allocate
    watch={manager+0x100}|{node+0x100 for node in node_blocks}
    # PC constant is supplied below via UC_ARM64_REG_PC import alias in wrapper.
    return dict(manager=manager,list_owner=list_owner,service=service,tls=tls,vtable=vtable,sinks_base=sinks_base,queue=queue,chunks=chunks,slots=slots,virtual_records=virtual_records,allocator_records=allocator_records,zero_writes=zero_writes,watch=watch,owner_count=owner_count,tag=tag,prefill=prefill,count=count,node_blocks=node_blocks)
def execute(f,p):
    from unicorn.arm64_const import UC_ARM64_REG_PC
    watch=p['watch'];p['zero_writes'].clear()
    def hook(u,access,a,n,value,data):
        if a in watch and n==1:p['zero_writes'].append(dict(pc=u.reg_read(UC_ARM64_REG_PC),address=a,size=n))
    h=f.u.hook_add(UC_HOOK_MEM_WRITE,hook)
    try:run=f.call(0x6d2950,(p['manager'],p['list_owner'],p['count']))
    finally:f.u.hook_del(h)
    hits=Counter(f.visits);count=p['count']
    assert f.visits[-1]==0x6d29e0 and 0x6d29e0 in hits and f.u.reg_read(UC_ARM64_REG_PC)==f.stop
    assert f.u.reg_read(UC_ARM64_REG_SP)==f.base+0x1f000 and f.q(p['tls']+0x28)==CANARY
    assert hits[0x6d2974]==1 and hits[0x6d2990]==count and hits[0x6d5e58]==count and hits[0x6d81b0]==count and hits[0x57104c]==count and hits[0x570abc]==count and hits[0x570a70]==count and hits[0x5710b0]==count and hits[0x6d29c4]==count and hits[0x6d353c]==count and hits[0x572a38]==count
    for pc in (0x52e15c,0xb2e604,0x3c9438,0x570ff0,0x3c986c,0x575b34,0x573a1c,0x109acc0):assert pc not in hits,hex(pc)
    assert len(p['allocator_records'])==count and len(p['virtual_records'])==1+2*count
    reserve=[x for x in p['virtual_records'] if x['kind']=='reserve'];notify=[x for x in p['virtual_records'] if x['kind']=='notify'];register=[x for x in p['virtual_records'] if x['kind']=='register']
    assert len(reserve)==1 and [x['index'] for x in notify]==list(range(count)) and [x['index'] for x in register]==list(range(count))
    assert all(x['manager']==p['manager'] for x in p['virtual_records']) and [x['node'] for x in register]==p['node_blocks']
    nodes=[]
    for i,node in enumerate(p['node_blocks']):
        d=dict(address=node,vptr=f.q(node),owner_field=f.q(node+0x20),chunk_field=f.q(node+0x30),type_field=f.w(node+0x3c),b0_qword=f.q(node+0xb0),b8_pointer=f.q(node+0xb8),byte_100=bytes(f.u.mem_read(node+0x100,1))[0],flags_38=f.w(node+0x38),chunk_length=f.q(p['chunks'][i]+0x50),slot0=f.q(p['slots'][i]))
        assert d['vptr']==0x10b1240 and d['owner_field']==p['list_owner'] and d['chunk_field']==p['chunks'][i] and d['type_field']==7 and d['b0_qword']==0 and d['b8_pointer']==node+0x200 and d['byte_100']==0 and d['flags_38']&0x100 and d['chunk_length']==1 and d['slot0']==p['manager'];nodes.append(d)
    assert f.w(p['list_owner']+0x34)==p['owner_count']+count
    assert f.q(p['list_owner']+0x48)==(p['node_blocks'][-1]+8 if count else p['list_owner']+0x40)
    assert struct.unpack_from('<H',f.u.mem_read(p['list_owner']+0xac,2))[0]==(0xc8 if count else 0)
    assert bytes(f.u.mem_read(p['manager']+0x100,1))[0]==(0 if count else 0xa5)
    assert f.q(p['queue'])==0 and f.q(p['queue']+8)==p['tag']+count and f.w(p['service']+0x43c)==count
    if count:
        assert {x['address'] for x in p['zero_writes']}==p['watch'] and {x['pc'] for x in p['zero_writes']}<={0x6d81c4,0x6d81c8}
    return dict(entry=0x6d2950,ret=f.visits[-1],stack_pointer_after=f.u.reg_read(UC_ARM64_REG_SP),stop_pc=f.u.reg_read(UC_ARM64_REG_PC),allocator_label_hex=bytes(f.source(0x12da21,16)).hex(),run=run,pc_hits={hex(k):v for k,v in sorted(hits.items()) if k in (0x6d2974,0x6d2990,0x6d5e58,0x6d81b0,0x57104c,0x570abc,0x570a70,0x5710b0,0x6d29c4,0x6d353c,0x572a38,0x6d29e0)},virtual_records=p['virtual_records'],allocator_records=list(p['allocator_records']),zero_writes=list(p['zero_writes']),nodes=nodes,manager_after=dict(byte_100=bytes(f.u.mem_read(p['manager']+0x100,1))[0]),list_owner_after=dict(count=f.w(p['list_owner']+0x34),list_head=f.q(p['list_owner']+0x48),flags_halfword=struct.unpack_from('<H',f.u.mem_read(p['list_owner']+0xac,2))[0]),pool_after=dict(queue_head=f.q(p['queue']),queue_tag=f.q(p['queue']+8),acquired_count=f.w(p['service']+0x43c),chunks=[dict(address=c,length=f.q(c+0x50),slot0=f.q(s)) for c,s in zip(p['chunks'],p['slots'])]),scope='Original graph-populator entry-to-RET with count native factory calls, original constructor/pool/helper/list code, and three explicitly synthetic virtual service sinks plus allocator sink. Manager/list owner/vtable/TLS/pool/node storage synthetic. NOT original virtual implementations, game manager/graph dispatch, observed game nodes, clip/clock binding, active pose/apply, Unity readback or render.')
def standalone(count=3,prefill=0xa5,base=0x3000000,owner_count=41,tag=0):
    f=Fixture(fixture_raw(merged()),base);manager=base+0x80000;list_owner=base+0x81000;service=base+0x70000;tls=base+0x60000;node_blocks=[base+0x14000+i*0x1000 for i in range(count)]
    p=prepare(f,count,node_blocks,manager,list_owner,service,tls,prefill,owner_count=owner_count,tag=tag);r=execute(f,p)
    return dict(**r,count=count,prefill=prefill,manager=manager,list_owner=list_owner,service=service,tls=tls,vtable=p['vtable'],node_blocks=node_blocks,owner_count=owner_count,tag=tag)
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
    paths=[RAW,node120.RAW,factory121.RAW,parent119.RAW,caller118.OUT,factory121.OUT,ROOT/'tools/recovery/graph122.py',Path(__file__),ROOT/'tests/test_graph122.py',ROOT/'tools/verify/factory121.py',ROOT/'tools/verify/node120.py',ROOT/'tools/verify/parent119.py',ROOT/'tools/verify/tag23_113_native.py']
    return dict(provisional=True,provenance='arena/ef6b75ef',inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},standalone=cases,source=dict(graph=graph,post_graph_bindings=[0x118,0x128,0x130,0x1d0],clock_control_loop='configure_node fixture inputs, not recovered writers',source_node=f.node,calls=samples),vtable_service_slots=dict(reserve=0x10,notify=0x18,register=0x70),counts=dict(standalone_cases=len(cases),standalone_graph_calls=len(cases),standalone_loop_counts=[c['count'] for c in cases],standalone_factory_calls=sum(c['count'] for c in cases),standalone_graph_instructions=[c['run']['instruction_count'] for c in cases],standalone_virtual_service_calls=[len(c['virtual_records']) for c in cases],source_graph_calls=1,source_loop_count=3,source_factory_calls=3,source_graph_instructions=graph['run']['instruction_count'],source_calls=len(samples),source_dwords=sum(len(x['native']['output_bits']) for x in samples)),scope='Native graph-populator loop on declared synthetic manager/list/pool/TLS and explicit service/allocator sinks. Source1609 integration uses one of three prepared factory nodes with post-graph harness bindings and unchanged119parent chain. Shared115–121lineage, not independent extraction, live graph construction, game-side writers, previous/active pose/apply/readback/render. Static native analysis only.')
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();x=build();b=gzip.compress((json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
    if a.check:assert OUT.read_bytes()==b
    else:OUT.write_bytes(b)
    print(json.dumps(dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),counts=x['counts'])))
if __name__=='__main__':main()
