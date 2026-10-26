"""Original node constructor with explicit preallocated pool, not game graph creation."""
import argparse,gzip,hashlib,json,struct
from pathlib import Path
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.arm64_const import UC_ARM64_REG_PC,UC_ARM64_REG_SP
from tools.verify.tag23_113_native import Fixture
from tools.verify import parent119,caller118,packed115
from tools.verify.caller118_native import combine
ROOT=Path(__file__).resolve().parents[2];RAW=ROOT/'reverse-engineering/raw/node120/probe.json.gz';OUT=ROOT/'datas/l3_ef6b75ef120_native_node_initialization.json.gz'
def raw():return json.load(gzip.open(RAW))
def constructor(f,node,prefill=0xa5,label=94,old_count=0,tag=0):
    if not 0<=old_count<4:raise ValueError('prepared chunk capacity4 required')
    f.put(node,bytes([prefill])*0x200,False)
    service=f.base+0x70000;queue=service+0x1000;chunk=service+0x2000;slots=service+0x3000
    for a,n in ((service,0x500),(queue,16),(chunk,0x68),(slots,32)):f.put(a,bytes(n),False)
    f.sq(0x116cb40,service);f.sq(service+0x450,queue);f.sq(queue,chunk);f.sq(queue+8,tag);f.sq(chunk,0);f.sq(chunk+0x40,slots);f.sq(chunk+0x50,old_count);f.sq(chunk+0x58,8)
    f.put(slots,b'\xa5'*32,False)
    writes=[]
    def hook(u,access,a,n,value,data):
        if node<=a and a+n<=node+0x200:writes.append(dict(pc=u.reg_read(UC_ARM64_REG_PC),offset=a-node,size=n))
    h=f.u.hook_add(UC_HOOK_MEM_WRITE,hook)
    saved_sinks=f.sinks;f.sinks={}  # Reject any service substitution during native construction.
    try:r=f.call(0x6d353c,(node,label))
    finally:
        f.sinks=saved_sinks;f.u.hook_del(h)
    image=bytes(f.u.mem_read(node,0x200));covered=sorted({a for w in writes for a in range(w['offset'],w['offset']+w['size'])})
    assert f.q(node)==0x10b1240 and f.q(0x10b12c0)==0x6d46a8 and f.q(node+0x30)==chunk
    assert f.q(queue)==0 and f.q(queue+8)==tag+1 and f.w(service+0x43c)==1
    # Native pool acquisition resets length before appending a null slot; old_count is deliberately discarded.
    assert f.q(chunk+0x50)==1 and f.q(slots)==0
    assert f.u.reg_read(UC_ARM64_REG_SP)==f.base+0x1f000
    return dict(entry=0x6d353c,ret=f.visits[-1],run=r,node=node,label=label,prefill=prefill,image_hex=image.hex(),writes=writes,written_offsets=covered,preserved_offsets=[i for i in range(0x200) if i not in covered],pool=dict(service=service,queue=queue,chunk=chunk,slots=slots,queue_tag_before=tag,queue_tag_after=f.q(queue+8),queue_head_after=f.q(queue),acquired_count=f.w(service+0x43c),chunk_length_after=f.q(chunk+0x50),slot0=f.q(slots)),external_calls=[],scope='Complete original constructor/base/member chain on supplied storage and preinitialized pool. No service/allocator instruction sink during this call, but graph/pool/label/storage synthetic; NOT original factory/handle attachment or observed game-created node.')
def standalone(prefill=0xa5,label=94,base=0x3000000,**kw):
    r=raw();f=Fixture(dict(windows=r['windows'],native_slices=r['cells'],strings=r['strings'],relocations=r['relocations']),base)
    return constructor(f,base+0x4000,prefill,label,**kw)
def build():
    r=raw();cases=[standalone(prefill,label) for prefill,label in ((0xa5,94),(0,94),(0xff,7))];row,s,data=packed115.source_stream();args,r119=parent119.raws();f=parent119.ParentFixture(*args,raw119=combine(r119,r),packed=data,continuous=s['curveCount'],discrete=s['discreteCurveCount']);init=constructor(f,f.node)
    # Explicit post-constructor fixture bindings, NOT original graph/clip acquisition.
    for offset,pointer in ((0x118,f.blob),(0x128,f.cache),(0x130,f.holder),(0x1d0,f.native_clip)):f.sq(f.node+offset,pointer)
    m=row['tree']['m_MuscleClip'];f.configure_time(start=m['m_StartTime'],stop=m['m_StopTime'],cycle_offset=m['m_CycleOffset']);old=json.load(gzip.open(caller118.OUT));samples=[]
    for previous in old['source']['runs']:
        f.configure_node(current=previous['node_seconds_double'],loop=m['m_LoopTime']);out=f.parent();assert out['output_bits']==previous['native']['output_bits'];samples.append(dict(query=previous['query'],native=out))
    paths=[RAW,ROOT/'tools/recovery/node120.py',Path(__file__),ROOT/'tests/test_node120.py',ROOT/'tools/verify/tag23_113_native.py',ROOT/'tools/verify/parent119.py',parent119.OUT,caller118.OUT]
    return dict(provisional=True,provenance='arena/ef6b75ef',inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},standalone=cases,source_constructor=init,source_calls=samples,post_constructor_bindings=dict(pointer_fields=[0x118,0x128,0x130,0x1d0],clock_control_loop='configure_node fixture inputs, not recovered writers'),vtable=dict(primary=0x10b1240,secondary=0x10b1420,parent_slot=0x10b12c0,parent=0x6d46a8),counts=dict(standalone_cases=len(cases),source_calls=len(samples),source_dwords=sum(len(x['native']['output_bits']) for x in samples),constructor_instructions=init['run']['instruction_count'],constructor_written_bytes=len(init['written_offsets']),constructor_preserved_bytes=len(init['preserved_offsets'])),scope='Native constructor replaces host-invented initialization for declared written fields; source integration then installs explicit prepared clip/cache/output pointers and clock/flags. Original factory/allocator/handle creation, graph/control writer provenance, active pose/apply/readback/render remain OPEN.')
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();x=build();b=gzip.compress((json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
    if a.check:assert OUT.read_bytes()==b
    else:OUT.write_bytes(b)
    print(json.dumps(dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),counts=x['counts'])))
if __name__=='__main__':main()
