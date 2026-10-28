"""Original node factory with explicit synthetic allocator service; not graph bootstrap."""
import argparse,gzip,hashlib,json,struct
from pathlib import Path
from unicorn.arm64_const import UC_ARM64_REG_X4,UC_ARM64_REG_X5
from tools.verify import node120,parent119,caller118,packed115
from tools.verify.caller118_native import combine
from tools.verify.tag23_113_native import Fixture
ROOT=Path(__file__).resolve().parents[2];RAW=ROOT/'reverse-engineering/raw/factory121/probe.json.gz';OUT=ROOT/'datas/l3_ef6b75ef121_native_node_factory.json.gz'
def raw():return json.load(gzip.open(RAW))
def merged():return combine(node120.raw(),raw())
def fixture_raw(r):return dict(windows=r['windows'],native_slices=r['cells'],strings=r['strings'],relocations=r['relocations'],imports=r.get('imports',[]),pointed_strings=r.get('pointed_strings',[]))
def standalone(prefill=0xa5,label=94,extra=0,owner_count=41,tag=0,base=0x3000000):
    f=Fixture(fixture_raw(merged()),base);node=base+0x4000;owner=base+0x80000
    f.put(node,bytes([prefill])*0x400,False);f.put(owner,bytes(0x100),False);f.sq(owner+0x48,owner+0x40);f.sw(owner+0x34,owner_count)
    service=base+0x70000;queue=service+0x1000;chunk=service+0x2000;slots=service+0x3000
    for a,n in ((service,0x500),(queue,16),(chunk,0x68),(slots,32)):f.put(a,bytes(n),False)
    f.sq(0x116cb40,service);f.sq(service+0x450,queue);f.sq(queue,chunk);f.sq(queue+8,tag);f.sq(chunk,0);f.sq(chunk+0x40,slots);f.sq(chunk+0x50,0);f.sq(chunk+0x58,8);f.put(slots,b'\xa5'*32,False)
    requests=[]
    def allocate(f):
        x4=f.u.reg_read(UC_ARM64_REG_X4);x5=f.u.reg_read(UC_ARM64_REG_X5)&0xffffffff
        request=dict(size=f.reg(0),alignment=f.reg(1),category=f.reg(2)&0xffffffff,flag=f.reg(3)&0xffffffff,label=x4,aux=x5,expected_size=extra+0x200)
        requests.append(request)
        assert (request['size'],request['alignment'],request['category'],request['flag'],x4,x5)==(extra+0x200,16,94,0,0x12da21,0xab)
        assert bytes(f.source(x4,1))==b'\0'
        f.ret(node)
    f.sinks[0x3c986c]=allocate
    run=f.call(0x6d5e58,(owner,label,extra));pcs=run['executed_addresses']
    assert 0x6d5ec4 in pcs and 0x6d353c in pcs and 0x572a38 in pcs and 0x570ff0 not in pcs and 0x3c986c not in pcs
    assert f.reg(0)==node and f.q(node)==0x10b1240 and f.q(0x10b12c0)==0x6d46a8
    assert f.w(owner+0x34)==owner_count+1 and f.q(owner+0x48)==node+8 and f.q(node+0x20)==owner
    assert f.q(node+8)==owner+0x40 and f.q(node+0x10)==owner+0x48
    assert struct.unpack_from('<H',f.u.mem_read(owner+0xac,2))[0]==0xc8
    assert struct.unpack_from('<H',f.u.mem_read(node+0xac,2))[0]==((prefill<<8)|prefill)&0xffff
    assert f.q(node+0x30)==chunk and f.q(queue)==0 and f.q(queue+8)==tag+1 and f.w(service+0x43c)==1 and f.q(chunk+0x50)==1 and f.q(slots)==0
    return dict(entry=0x6d5e58,ret=f.visits[-1],run=run,node=node,owner=owner,label=label,extra_size=extra,prefill=prefill,returned_node=f.reg(0),allocator_requests=requests,allocator_string=bytes(f.source(0x12da21,16)).hex(),service=dict(global_va=0x116cb40,address=service,queue=queue,chunk=chunk,slots=slots,tag_before=tag,tag_after=f.q(queue+8),acquired_count=f.w(service+0x43c),chunk_length=f.q(chunk+0x50)),owner_after=dict(count=f.w(owner+0x34),list_head=f.q(owner+0x48),list_sentinel=owner+0x40,flags_halfword=struct.unpack_from('<H',f.u.mem_read(owner+0xac,2))[0],image_hex=bytes(f.u.mem_read(owner,0x100)).hex()),node_after=dict(vptr=f.q(node),owner_field=f.q(node+0x20),list_next=f.q(node+8),list_prev=f.q(node+0x10),chunk_field=f.q(node+0x30),flags_halfword=struct.unpack_from('<H',f.u.mem_read(node+0xac,2))[0],image_hex=bytes(f.u.mem_read(node,0x200)).hex()),scope='Original factory/constructor/member/base/pool-acquisition and handle-list insertion entry-to-RET. Allocator at original3c986c is an explicit synthetic argument-checking sink returning prepared storage; owner/list/pool/global/label/storage synthetic. Cleanup570ff0 is naturally skipped by original constructor flags. NOT original heap/allocator, factory caller/graph registration, observed game node, clock/clip binding or pose/apply/readback/render.')
def source_fixture():
    args,r119=parent119.raws();row,s,data=packed115.source_stream();r=merged()
    f=parent119.ParentFixture(*args,raw119=combine(r119,r),packed=data,continuous=s['curveCount'],discrete=s['discreteCurveCount'])
    node=f.node;owner=f.base+0x80000
    f.put(node,bytes([0xa5])*0x400,False);f.put(owner,bytes(0x100),False);f.sq(owner+0x48,owner+0x40);f.sw(owner+0x34,41)
    service=f.base+0x70000;queue=service+0x1000;chunk=service+0x2000;slots=service+0x3000
    for a,n in ((service,0x500),(queue,16),(chunk,0x68),(slots,32)):f.put(a,bytes(n),False)
    f.sq(0x116cb40,service);f.sq(service+0x450,queue);f.sq(queue,chunk);f.sq(queue+8,0);f.sq(chunk,0);f.sq(chunk+0x40,slots);f.sq(chunk+0x50,0);f.sq(chunk+0x58,8);f.put(slots,b'\xa5'*32,False)
    requests=[]
    def allocate(f):
        requests.append(dict(size=f.reg(0),alignment=f.reg(1),category=f.reg(2)&0xffffffff,flag=f.reg(3)&0xffffffff,label=f.u.reg_read(UC_ARM64_REG_X4),aux=f.u.reg_read(UC_ARM64_REG_X5)&0xffffffff))
        assert requests[-1]==dict(size=0x200,alignment=16,category=94,flag=0,label=0x12da21,aux=0xab)
        f.ret(node)
    f.sinks[0x3c986c]=allocate;run=f.call(0x6d5e58,(owner,94,0));assert f.reg(0)==node and 0x572a38 in run['executed_addresses'] and 0x570ff0 not in run['executed_addresses']
    for offset,pointer in ((0x118,f.blob),(0x128,f.cache),(0x130,f.holder),(0x1d0,f.native_clip)):f.sq(node+offset,pointer)
    m=row['tree']['m_MuscleClip'];f.configure_time(start=m['m_StartTime'],stop=m['m_StopTime'],cycle_offset=m['m_CycleOffset'])
    old=json.load(gzip.open(caller118.OUT));samples=[]
    for previous in old['source']['runs']:
        f.configure_node(current=previous['node_seconds_double'],loop=m['m_LoopTime']);out=f.parent();assert out['output_bits']==previous['native']['output_bits'] and out['completion_byte']==1;samples.append(dict(query=previous['query'],native=out))
    return f,row,s,run,requests,samples
def build():
    cases=[standalone(prefill,label,extra) for prefill,label,extra in ((0xa5,94,0),(0,7,0x40),(0xff,94,0x100))]
    f,row,s,run,requests,samples=source_fixture()
    paths=[RAW,node120.RAW,parent119.RAW,caller118.OUT,parent119.OUT,ROOT/'tools/recovery/factory121.py',Path(__file__),ROOT/'tests/test_factory121.py',ROOT/'tools/verify/node120.py',ROOT/'tools/verify/parent119.py',ROOT/'tools/verify/tag23_113_native.py']
    return dict(provisional=True,provenance='arena/ef6b75ef',inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},standalone=cases,source=dict(factory_run=run,allocator_requests=requests,post_factory_bindings=[0x118,0x128,0x130,0x1d0],clock_control_loop='configure_node fixture inputs, not recovered writers',calls=samples),upstream_caller=dict(start=0x6d2950,end=0x6d29e4,direct_call_pc=0x6d2990,scan='one local original direct-branch reference; caller NOT executed'),counts=dict(standalone_cases=len(cases),standalone_factory_calls=len(cases),standalone_factory_instructions=[c['run']['instruction_count'] for c in cases],source_factory_calls=1,source_factory_instructions=run['instruction_count'],source_calls=len(samples),source_dwords=sum(len(x['native']['output_bits']) for x in samples),standalone_allocator_requests=sum(len(c['allocator_requests']) for c in cases),source_allocator_requests=len(requests),inherited_constructor_instructions=174),scope='Native factory entry-to-RET over prepared owner/list/pool and explicit allocator sink, then prepared source bindings and unchanged current-only parent chain. Original heap/service bootstrap/factory caller/graph registration and active pose/application/readback/render remain OPEN. Source comparison inherits118/119/120 lineage, not independent extraction or Unity runtime.')
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();x=build();b=gzip.compress((json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
    if a.check:assert OUT.read_bytes()==b
    else:OUT.write_bytes(b)
    print(json.dumps(dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),counts=x['counts'])))
if __name__=='__main__':main()
