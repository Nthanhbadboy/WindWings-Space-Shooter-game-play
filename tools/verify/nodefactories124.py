"""Original specialized node factories with native constructors and explicit allocator services."""
import argparse,gzip,hashlib,json,struct
from collections import Counter
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_ARM
from unicorn.arm64_const import UC_ARM64_REG_PC,UC_ARM64_REG_SP,UC_ARM64_REG_TPIDR_EL0,UC_ARM64_REG_X4,UC_ARM64_REG_X5
from tools.verify import node120,factory121,graph122,vtable123,parent119,caller118,packed115
from tools.verify.caller118_native import combine
from tools.verify.tag23_113_native import Fixture
ROOT=Path(__file__).resolve().parents[2];RAW=ROOT/'reverse-engineering/raw/nodefactories124/probe.json.gz';OUT=ROOT/'datas/l3_ef6b75ef124_native_specialized_node_factories.json.gz'
CANARY=0x1122334455667788
FACTORIES=(0x6d25f4,0x6d2664,0x6d26d4,0x6d2744)
EXPECTED={0x6d25f4:dict(constructor=0x6d6a1c,vptr=0x10b1440,size_offset=0x178,ret=0x6d2660),0x6d2664:dict(constructor=0x6d850c,vptr=0x10b1730,size_offset=0x170,ret=0x6d26d0),0x6d26d4:dict(constructor=0x6d2894,vptr=0x10b1150,size_offset=0x180,ret=0x6d2740),0x6d2744:dict(constructor=0x6d81f8,vptr=0x10b1640,size_offset=0x120,ret=0x6d27b0)}
def raw():return json.load(gzip.open(RAW))
def merged():return combine(combine(node120.raw(),factory121.raw()),combine(combine(graph122.raw(),vtable123.raw()),raw()))
def fixture_raw(r):return dict(windows=r['windows'],native_slices=r['cells'],strings=r['strings'],relocations=r['relocations'],imports=r.get('imports',[]),pointed_strings=r.get('pointed_strings',[]))
def disassemble(r,entry):
    w=next(w for w in r['windows'] if w['va']==entry);return [(i.address,i.mnemonic,i.op_str) for i in Cs(CS_ARCH_ARM64,CS_MODE_ARM).disasm(bytes.fromhex(w['hex']),entry)]
def vptr_from_constructor(r,entry):
    ins=disassemble(r,entry);cur=None
    for pc,mn,op in ins:
        if mn=='adrp' and '#0x10b1000' in op:
            cur=dict(reg=op.split(',')[0].strip(),offset=None)
        elif cur and mn=='add' and op.startswith(cur['reg']+', '+cur['reg']+', #'):
            cur['offset']=int(op.split('#')[1],0)
        elif cur and mn=='str' and op==cur['reg']+', [x19]':
            assert cur['offset'] is not None,(hex(entry),cur)
            return 0x10b1000+cur['offset'],dict(reg=cur['reg'],offset=cur['offset'],adrp=0x10b1000)
    raise ValueError(('constructor vptr store not found',hex(entry)))
def factory_metadata(r):
    fde={x['entry']:x['unwind']['end'] for x in r['followed'] if x['unwind']}
    calls={}
    for x in r['graph_builder_callsites']:calls.setdefault(x['target'],[]).append(x['pc'])
    groups={v['vptr']:v for v in r['known_vtables']}
    out={}
    for e in FACTORIES:
        ins=disassemble(r,e);adds=[op for _,m,op in ins if m=='add' and op.startswith('x0, x2, #')];bl=[op for _,m,op in ins if m=='bl' and op.startswith('#0x6d')]
        size_offset=int(adds[0].split('#')[1],0);constructor=int(bl[0].replace('#',''),0);ret=fde[e]-4
        vptr,literal=vptr_from_constructor(r,constructor)
        assert (constructor,vptr,size_offset,ret)==(EXPECTED[e]['constructor'],EXPECTED[e]['vptr'],EXPECTED[e]['size_offset'],EXPECTED[e]['ret'])
        out[str(e)]=dict(entry=e,fde_end=fde[e],ret=ret,constructor=constructor,constructor_fde_end=fde[constructor],constructor_ret=fde[constructor]-4,vptr=vptr,size_offset=size_offset,graph_builder_callsites=calls.get(e,[]),vtable_slots={hex(s):groups[vptr]['addends'][i] for i,s in enumerate(range(0,0x80,8))},constructor_vptr_literal=literal)
    return out
def prepare(f,entry,node,owner,service,tls,prefill=0xa5,label=94,extra=0,tag=0,owner_count=41):
    r=merged();meta=EXPECTED[entry];expected_size=extra+meta['size_offset']
    service_calls=[];failures=[];allocator_records=[];bindings=[]
    f.put(node,bytes([prefill])*0x400,False);f.put(owner,bytes(0x100),False);f.sq(owner+0x48,owner+0x40);f.sw(owner+0x34,owner_count)
    f.put(tls,bytes(0x100),False);f.sq(tls+0x28,CANARY);f.u.reg_write(UC_ARM64_REG_TPIDR_EL0,tls)
    f.put(service,bytes(0x10000),False);f.sq(0x116cb40,service);queue=service+0x1000;f.sq(service+0x450,queue);f.sq(queue,service+0x2000);f.sq(queue+8,tag)
    chunk=service+0x2000;slots=service+0x3000
    f.sq(chunk,0);f.sq(chunk+0x40,slots);f.sq(chunk+0x50,0);f.sq(chunk+0x58,8);f.put(slots,b'\xa5'*32,False)
    sinks=(f.base+0x90000,f.base+0x90100);bindings=[vtable123.plt_binding(f,r,0x109ace0,'memset',sinks[0]),vtable123.plt_binding(f,r,0x109acc0,'__stack_chk_fail',sinks[1])]
    def memset(f):
        dest,value,length=f.reg(0),f.reg(1)&0xff,f.reg(2);f.put(dest,bytes([value])*length,False);service_calls.append(dict(symbol='memset',dest=dest,value=value,length=length));f.ret()
    def fail(f):
        failures.append(dict(symbol='__stack_chk_fail',pc=f.u.reg_read(UC_ARM64_REG_PC)));raise RuntimeError('stack canary failure')
    def allocate(f):
        x4=f.u.reg_read(UC_ARM64_REG_X4);x5=f.u.reg_read(UC_ARM64_REG_X5)&0xffffffff
        rec=dict(size=f.reg(0),alignment=f.reg(1),category=f.reg(2)&0xffffffff,flag=f.reg(3)&0xffffffff,label=x4,aux=x5,expected_size=expected_size)
        allocator_records.append(rec);assert rec==dict(size=expected_size,alignment=16,category=94,flag=0,label=0x12da21,aux=0xab,expected_size=expected_size);assert bytes(f.source(x4,1))==b'\0'
        f.ret(node)
    f.sinks[sinks[0]]=memset;f.sinks[sinks[1]]=fail;f.sinks[0x3c986c]=allocate
    return dict(entry=entry,expected_size=expected_size,meta=meta,node=node,owner=owner,service=service,tls=tls,queue=queue,chunk=chunk,slots=slots,prefill=prefill,label=label,extra=extra,tag=tag,owner_count=owner_count,service_calls=service_calls,failures=failures,allocator_records=allocator_records,bindings=bindings)
def execute(f,p):
    entry=p['entry'];meta=p['meta'];f.calls=[];run=f.call(entry,(p['owner'],p['label'],p['extra']));hits=Counter(f.visits)
    assert f.visits[-1]==meta['ret'] and f.u.reg_read(UC_ARM64_REG_PC)==f.stop and f.u.reg_read(UC_ARM64_REG_SP)==f.base+0x1f000 and f.q(p['tls']+0x28)==CANARY
    assert f.reg(0)==p['node'] and f.q(p['node'])==meta['vptr']
    assert meta['constructor'] in hits and 0x572a38 in hits and 0x57054c in hits
    for pc in (0x570ff0,0x3c986c,0x109acc0,0x109ace0,0x573a1c,0x575b34):assert pc not in hits,hex(pc)
    assert len(p['allocator_records'])==1 and p['allocator_records'][0]['size']==p['expected_size'] and not p['service_calls'] and not p['failures']
    assert f.w(p['node']+0x18)==p['label'] and f.q(p['node']+0x20)==p['owner'] and f.q(p['node']+0x30)==p['chunk'] and bytes(f.u.mem_read(p['node']+0x38,1))[0]&1 and struct.unpack_from('<H',f.u.mem_read(p['node']+0xa8,2))[0]==0
    assert f.w(p['owner']+0x34)==p['owner_count']+1 and f.q(p['owner']+0x48)==p['node']+8 and struct.unpack_from('<H',f.u.mem_read(p['owner']+0xac,2))[0]==0xc8
    assert f.q(p['queue'])==0 and f.q(p['queue']+8)==p['tag']+1 and f.w(p['service']+0x43c)==1 and f.q(p['chunk']+0x50)==1 and f.q(p['slots'])==0
    specific={}
    if entry==0x6d25f4:
        assert f.w(p['node']+0x118)==0x4b and bytes(f.u.mem_read(p['node']+0x170,1))[0]==1;specific=dict(type_dword=0x4b,flag_170=1)
    elif entry==0x6d2664:
        assert bytes(f.u.mem_read(p['node']+0x16c,1))[0]==0;specific=dict(flag_16c=0)
    elif entry==0x6d26d4:
        assert f.w(p['node']+0x16c)==0x3f800000 and f.q(p['node']+0x178)==0;specific=dict(float_bits_16c=0x3f800000,previous_zero=True)
    elif entry==0x6d2744:
        assert f.w(p['node']+0x118)==0;specific=dict(type_dword=0)
    return dict(entry=entry,ret=f.visits[-1],stack_pointer_after=f.u.reg_read(UC_ARM64_REG_SP),stop_pc=f.u.reg_read(UC_ARM64_REG_PC),run=run,pc_hits={hex(k):v for k,v in sorted(hits.items()) if k in (entry,meta['constructor'],0x572a38,0x57054c,meta['ret'])},allocator_records=list(p['allocator_records']),plt_bindings=p['bindings'],service_calls=list(p['service_calls']),failure_calls=list(p['failures']),node=dict(address=p['node'],vptr=f.q(p['node']),label_field=f.w(p['node']+0x18),owner_field=f.q(p['node']+0x20),chunk_field=f.q(p['node']+0x30),bitfield_38=f.w(p['node']+0x38),halfword_a8=struct.unpack_from('<H',f.u.mem_read(p['node']+0xa8,2))[0],specific=specific),owner_after=dict(count=f.w(p['owner']+0x34),list_head=f.q(p['owner']+0x48),flags_halfword=struct.unpack_from('<H',f.u.mem_read(p['owner']+0xac,2))[0]),pool_after=dict(queue_head=f.q(p['queue']),queue_tag=f.q(p['queue']+8),acquired_count=f.w(p['service']+0x43c),chunk_length=f.q(p['chunk']+0x50),slot0=f.q(p['slots'])),scope='Complete original specialized factory entry-to-RET with native constructor/base/pool/list code. Allocator at3c986c, memset/stack-check PLT services and TLS/owner/pool/node storage explicit synthetic. NOT original heap, serialized controller bootstrap, game graph creation, active pose/apply, Unity readback or render.')
def standalone(entry=0x6d25f4,prefill=0xa5,label=94,extra=0,tag=0,owner_count=41,base=0x3000000):
    f=Fixture(fixture_raw(merged()),base);node=base+0x4000;owner=base+0x80000;service=base+0x70000;tls=base+0x60000
    p=prepare(f,entry,node,owner,service,tls,prefill,label,extra,tag,owner_count);r=execute(f,p)
    return dict(**r,prefill=prefill,label=label,extra=extra,tag=tag,owner_count=owner_count,base=base,owner=owner,service=service,tls=tls)
def source_fixture():
    args,r119=parent119.raws();row,s,data=packed115.source_stream();extra=merged()
    f=parent119.ParentFixture(*args,raw119=combine(r119,extra),packed=data,continuous=s['curveCount'],discrete=s['discreteCurveCount'])
    node=f.node;owner=f.base+0x80000;service=f.base+0x70000
    p=prepare(f,0x6d26d4,node,owner,service,f.tls);factory_run=execute(f,p)
    for offset,pointer in ((0x118,f.blob),(0x128,f.cache),(0x130,f.holder),(0x1d0,f.native_clip)):f.sq(node+offset,pointer)
    m=row['tree']['m_MuscleClip'];f.configure_time(start=m['m_StartTime'],stop=m['m_StopTime'],cycle_offset=m['m_CycleOffset'])
    old=json.load(gzip.open(caller118.OUT));samples=[]
    for previous in old['source']['runs']:
        f.configure_node(current=previous['node_seconds_double'],loop=m['m_LoopTime']);out=f.parent();assert out['output_bits']==previous['native']['output_bits'] and out['completion_byte']==1;samples.append(dict(query=previous['query'],native=out))
    return f,factory_run,samples
def build():
    r=raw();meta=factory_metadata(r)
    cases=[standalone(e) for e in FACTORIES]+[standalone(0x6d25f4,prefill=0,label=7,extra=0x40,tag=41),standalone(0x6d2744,base=0x4000000)]
    f,factory_run,samples=source_fixture()
    paths=[RAW,node120.RAW,factory121.RAW,graph122.RAW,vtable123.RAW,parent119.RAW,caller118.OUT,factory121.OUT,ROOT/'tools/recovery/nodefactories124.py',Path(__file__),ROOT/'tests/test_nodefactories124.py',ROOT/'tools/verify/vtable123.py',ROOT/'tools/verify/graph122.py',ROOT/'tools/verify/factory121.py',ROOT/'tools/verify/node120.py',ROOT/'tools/verify/parent119.py',ROOT/'tools/verify/tag23_113_native.py']
    return dict(provisional=True,provenance='arena/ef6b75ef',inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},factory_metadata=meta,graph_builder_callsites=[dict(pc=x['pc'],target=x['target']) for x in r['graph_builder_callsites']],vtable_groups=[dict(vptr=v['vptr'],addends=v['addends']) for v in r['known_vtables']],standalone=cases,source=dict(factory=0x6d26d4,factory_run=factory_run,post_factory_bindings=[0x118,0x128,0x130,0x1d0],clock_control_loop='configure_node fixture inputs, not recovered writers',source_node=f.node,calls=samples),counts=dict(standalone_cases=len(cases),standalone_factory_calls=len(cases),standalone_instructions=[c['run']['instruction_count'] for c in cases],factory_entries=len(FACTORIES),graph_builder_callsites=len(r['graph_builder_callsites']),source_factory_calls=1,source_calls=len(samples),source_dwords=sum(len(x['native']['output_bits']) for x in samples)),scope='Four original specialized node factories called by captured graph-builder6cf7b4, with native constructors/vtable identities and explicit allocator/PLT/TLS/pool/owner services. Source1609 integration uses one factory-C node with post-factory harness bindings and unchanged119parent chain. Shared115–123lineage; NOT independent extraction, serialized controller bootstrap, observed game graph creation, active pose/apply/readback/render. Static native analysis only.')
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();x=build();b=gzip.compress((json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
    if a.check:assert OUT.read_bytes()==b
    else:OUT.write_bytes(b)
    print(json.dumps(dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),counts=x['counts'])))
if __name__=='__main__':main()
