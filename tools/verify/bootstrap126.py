"""Original graph-builder dispatch callers on prepared N2 serialized-owner state."""
import argparse,gzip,hashlib,json,struct
from collections import Counter
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import UC_ARM64_REG_PC,UC_ARM64_REG_SP,UC_ARM64_REG_TPIDR_EL0,UC_ARM64_REG_X1,UC_ARM64_REG_X3,UC_ARM64_REG_X4,UC_ARM64_REG_X5,UC_ARM64_REG_X8
from tools.verify import graph122,vtable123,nodefactories124
from tools.verify.caller118_native import combine
from tools.verify.tag23_113_native import Fixture
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'reverse-engineering/raw/bootstrap126/probe.json.gz'
N2=ROOT/'reverse-engineering/raw/l3-ef6b75ef126-n2-source/l3_a5_n2_serialized_owner_graph_builder.json'
N2_REPORT=ROOT/'reverse-engineering/raw/l3-ef6b75ef126-n2-source/158-n2-serialized-owner-graph-builder.md'
VER=ROOT/'reverse-engineering/raw/l3-ef6b75ef126-verification'
OUT=ROOT/'datas/l3_ef6b75ef126_native_graph_builder_dispatch.json.gz'
TARGET=0x6cf7b4;SET_ENTRY=0x6cef64;REBUILD_ENTRY=0x6cefdc;SET_RET=0x6cefd8;EARLY_RET=0x6cefc0;TAIL_RET=0x571128
CANARY=0x1122334455667788
def sha(b):return hashlib.sha256(b).hexdigest()
def raw():return json.load(gzip.open(RAW))
def n2():return json.loads(N2.read_text())
def merged():return combine(combine(graph122.merged(),vtable123.raw()),combine(nodefactories124.raw(),raw()))
def fixture_raw(r):return dict(windows=r['windows'],native_slices=r['cells'],strings=r['strings'],relocations=r['relocations'],imports=r.get('imports',[]),pointed_strings=r.get('pointed_strings',[]))
def prepare(f,base=0x3000000):
    owner=n2();ctl=owner['serialized_owner']['controller'];comp=owner['serialized_owner']['animator_component'];h=owner['serialized_owner']['hierarchy']
    assert ctl['path_id']==1856 and ctl['name']=='Body 1' and ctl['prefab_roots']==['Boss-37004'] and comp['component_path_id']==493584 and comp['controller_ref']['m_PathID']==1856 and comp['gameobject_ref']['m_PathID']==76852 and h['root_gameobject_name']=='Boss-37004'
    addresses=dict(controller=base+0x4000,owner=base+0x5000,chunk=base+0x6000,slots=base+0x6100,child=base+0x6200,vtable_ctrl=base+0x7000,vtable_owner=base+0x7100,sentinel=base+0x7600,sink_e0=base+0x7300,sink_d8=base+0x7310,sink_memset=base+0x7320,sink_fail=base+0x7330,service=base+0x7400,tls=base+0x7500)
    for k,n in [('controller',0x200),('owner',0x100),('chunk',0x60),('slots',0x20),('child',0x100),('vtable_ctrl',0x100),('vtable_owner',0x100),('sentinel',0x40),('sink_e0',4),('sink_d8',4),('sink_memset',4),('sink_fail',4),('service',0x100),('tls',0x100)]:f.put(addresses[k],bytes(n),False)
    C=addresses['controller'];O=addresses['owner'];CH=addresses['chunk'];S=addresses['slots'];VC=addresses['vtable_ctrl'];VO=addresses['vtable_owner'];SE=addresses['sink_e0'];SD=addresses['sink_d8']
    f.sq(C,VC);f.sq(C+0x20,addresses['child']);f.sq(C+0x30,CH);f.sw(C+0x18,0);f.sw(C+0x38,0);f.sw(C+0xa8,0);f.put(C+0x102,b'\0',False);f.put(C+0x103,b'\0',False);f.sq(C+0x118,addresses['sentinel'])
    f.sq(O,VO);f.sq(O+0x8,ctl['path_id']);f.sq(O+0x10,comp['component_path_id']);f.sq(O+0x18,comp['gameobject_ref']['m_PathID']);f.sq(O+0x20,h['parent_chain_child_to_root'][-1]['gameobject_path_id']);f.sq(O+0x28,comp['controller_ref']['m_FileID']);f.sq(O+0x30,comp['controller_ref']['m_PathID']);f.sq(O+0x38,h['transform_path_id'])
    for i,entry in enumerate(h['parent_chain_child_to_root']):f.sq(O+0x40+i*0x10,entry['father_transform_path_id']);f.sq(O+0x48+i*0x10,entry['gameobject_path_id'])
    f.sq(CH,0);f.sq(CH+0x40,S);f.sq(CH+0x50,1);f.sq(CH+0x58,8);f.sq(S,0)
    f.sq(VC+0xe0,SE);f.sq(VO+0xd8,SD)
    f.sq(0x116cb40,addresses['service']);f.sq(addresses['tls']+0x28,CANARY);f.u.reg_write(UC_ARM64_REG_TPIDR_EL0,addresses['tls'])
    r=merged();bindings=[vtable123.plt_binding(f,r,0x109ace0,'memset',addresses['sink_memset']),vtable123.plt_binding(f,r,0x109acc0,'__stack_chk_fail',addresses['sink_fail'])]
    rec=dict(graph_builder=[],virtual=[],service=[],failure=[])
    def gb(f):f.ret(0)
    def e0(f):f.ret(0)
    def d8(f):f.ret(0)
    def memset(f):
        dest,value,length=f.reg(0),f.reg(1)&0xff,f.reg(2);f.put(dest,bytes([value])*length,False);rec['service'].append(dict(symbol='memset',dest=dest,value=value,length=length));f.ret()
    def fail(f):
        rec['failure'].append(dict(symbol='__stack_chk_fail',pc=f.u.reg_read(UC_ARM64_REG_PC)));raise RuntimeError('stack canary failure')
    f.sinks[TARGET]=gb;f.sinks[SE]=e0;f.sinks[SD]=d8;f.sinks[addresses['sink_memset']]=memset;f.sinks[addresses['sink_fail']]=fail
    def hook(u,pc,size,data):
        if pc in (0x6cef84,0x6cefe4):
            rec['graph_builder'].append(dict(call_pc=pc,x0=f.reg(0),x1=f.reg(1),x2=f.reg(2),x3=f.reg(3)&0xffffffff))
        elif pc in (0x6cef94,0x6cefb0,0x6ceff8):
            target=u.reg_read(UC_ARM64_REG_X1) if pc==0x6ceff8 else u.reg_read(UC_ARM64_REG_X8);obj=f.reg(0)
            d=dict(pc=pc,target=target,object=obj)
            if pc==0x6cefb0:
                d.update(kind='owner_release',controller_path=f.q(obj+0x8),component_path=f.q(obj+0x10),gameobject_path=f.q(obj+0x18),root_gameobject=f.q(obj+0x20),controller_ref_path=f.q(obj+0x30))
            else:d['kind']='rebuild_notify' if pc==0x6cef94 else 'rebuild_notify_tail'
            rec['virtual'].append(d)
    return dict(addresses=addresses,records=rec,bindings=bindings,n2_owner=owner['serialized_owner'],n2_unresolved=owner['unresolved_edges'])
def run_case(f,p,entry=SET_ENTRY,early=False,owner_null=False):
    C=p['addresses']['controller'];O=p['addresses']['owner'];rec=p['records']
    for k in rec:rec[k].clear()
    f.sq(C+0x118,O if early else p['addresses']['sentinel']);f.sw(C+0x38,0);f.sw(C+0xa8,0);f.put(C+0x102,b'\0',False);f.put(C+0x103,b'\0',False)
    f.u.reg_write(UC_ARM64_REG_X3,0);f.u.reg_write(UC_ARM64_REG_X4,0);f.u.reg_write(UC_ARM64_REG_X5,0)
    h=f.u.hook_add(UC_HOOK_CODE,prepare_hook(f,p))
    try:run=f.call(entry,(C,0 if owner_null else O,0))
    finally:f.u.hook_del(h)
    hits=Counter(f.visits);common=dict(entry=entry,ret=f.visits[-1],stack_pointer_after=f.u.reg_read(UC_ARM64_REG_SP),stop_pc=f.u.reg_read(UC_ARM64_REG_PC),run=run,graph_builder_calls=list(rec['graph_builder']),virtual_calls=list(rec['virtual']),service_calls=list(rec['service']),failure_calls=list(rec['failure']),pc_hits={hex(k):v for k,v in sorted(hits.items()) if k in (SET_ENTRY,REBUILD_ENTRY,TARGET,0x6cef84,0x6cefe4,0x6cef94,0x6cefb0,0x6ceff8,0x6d6bf8,0x6cf768,0x5710ec,0x571128,0x57112c,EARLY_RET,TAIL_RET,SET_RET,0x6cefc0,0x6ceff8)},node_after=dict(slot118=f.q(C+0x118),byte102=bytes(f.u.mem_read(C+0x102,1))[0],byte103=bytes(f.u.mem_read(C+0x103,1))[0],flags38=f.w(C+0x38),halfword_a8=struct.unpack_from('<H',f.u.mem_read(C+0xa8,2))[0]))
    assert f.u.reg_read(UC_ARM64_REG_PC)==f.stop and f.u.reg_read(UC_ARM64_REG_SP)==f.base+0x1f000 and not rec['service'] and not rec['failure']
    assert TARGET not in hits and 0x57112c not in hits
    if early:
        assert f.visits[-1]==EARLY_RET and not rec['graph_builder'] and not rec['virtual'] and f.q(C+0x118)==O
    elif entry==REBUILD_ENTRY:
        assert len(rec['graph_builder'])==1 and len(rec['virtual'])==1 and rec['virtual'][0]['kind']=='rebuild_notify_tail' and rec['virtual'][0]['target']==p['addresses']['sink_e0']
        assert 0x6ceff8 in hits and 0x6d6bf8 not in hits and 0x5710ec not in hits and f.q(C+0x118)==p['addresses']['sentinel']
    else:
        assert len(rec['graph_builder'])==1 and f.visits[-1]==TAIL_RET and 0x6d6bf8 in hits and 0x6cf768 in hits and 0x5710ec in hits and 0x571128 in hits
        assert (f.q(C+0x118),bytes(f.u.mem_read(C+0x102,1))[0],bytes(f.u.mem_read(C+0x103,1))[0])==(0 if owner_null else O,1,0)
        assert len(rec['virtual'])==(1 if owner_null else 2)
        if not owner_null:assert rec['virtual'][1]['kind']=='owner_release' and rec['virtual'][1]['controller_path']==1856 and rec['virtual'][1]['component_path']==493584 and rec['virtual'][1]['gameobject_path']==76852
    return common
def prepare_hook(f,p):
    rec=p['records']
    def hook(u,pc,size,data):
        if pc in (0x6cef84,0x6cefe4):rec['graph_builder'].append(dict(call_pc=pc,x0=f.reg(0),x1=f.reg(1),x2=f.reg(2),x3=f.reg(3)&0xffffffff))
        elif pc in (0x6cef94,0x6cefb0,0x6ceff8):
            target=u.reg_read(UC_ARM64_REG_X1) if pc==0x6ceff8 else u.reg_read(UC_ARM64_REG_X8);obj=f.reg(0);d=dict(pc=pc,target=target,object=obj)
            if pc==0x6cefb0:d.update(kind='owner_release',controller_path=f.q(obj+0x8),component_path=f.q(obj+0x10),gameobject_path=f.q(obj+0x18),root_gameobject=f.q(obj+0x20),controller_ref_path=f.q(obj+0x30))
            else:d['kind']='rebuild_notify' if pc==0x6cef94 else 'rebuild_notify_tail'
            rec['virtual'].append(d)
    return hook
def build():
    r=raw();fde={x['entry']:x['unwind']['end'] for x in r['followed'] if x['unwind']}
    cases=[]
    for kw in [dict(entry=SET_ENTRY),dict(entry=SET_ENTRY,early=True),dict(entry=REBUILD_ENTRY),dict(entry=SET_ENTRY,owner_null=True)]:
        f=Fixture(fixture_raw(merged()));p=prepare(f);cases.append(run_case(f,p,**kw))
    paths=[RAW,N2,N2_REPORT,VER/'claim.json',VER/'spec-lane103.json',VER/'n2-handoff.json',VER/'recovery.json',Path(__file__),ROOT/'tests/test_bootstrap126.py',ROOT/'tools/recovery/bootstrap126.py',ROOT/'tools/verify/graph122.py',ROOT/'tools/verify/vtable123.py',ROOT/'tools/verify/nodefactories124.py']
    return dict(schema=1,provisional=True,provenance='arena/ef6b75ef',claim=6425017706,target=TARGET,direct_refs=[dict(pc=x['pc'],target=x['target'],owner_start=x['owner_start'],owner_end=x['owner_end']) for x in r['direct_refs']],rela_matches=r['rela_matches'],fde={hex(k):v for k,v in fde.items() if k in r['root_entries']},n2_owner=n2()['serialized_owner'],inputs={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths},n2_source=dict(artifact_sha256=sha(N2.read_bytes()),report_sha256=sha(N2_REPORT.read_bytes()),owner=n2()['serialized_owner'],unresolved_edges=n2()['unresolved_edges']),cases=cases,counts=dict(cases=len(cases),graph_builder_sink_calls=sum(len(c['graph_builder_calls']) for c in cases),virtual_service_calls=sum(len(c['virtual_calls']) for c in cases),native_instructions=[c['run']['instruction_count'] for c in cases],direct_refs=len(r['direct_refs']),rela_matches=len(r['rela_matches'])),scope='Original native graph-builder dispatch callers6cef64/6cefdc entry-to-tail on prepared N2 serialized-owner state. Graph-builder0x6cf7b4 itself is an explicit synthetic sink; virtual+0xe0/+0xd8, memset/stack-check PLT services and controller/owner/chunk/TLS state are prepared. NOT full graph-builder execution, observed game instance, serialized-owner rediscovery, native heap, Unity readback/render or runtime. Static-only; no selfACK/full#27closure.',limits=['N2 owner identity is a read-only static serialized pin, not proof that this native range constructed controller1856/Boss-37004.','Full graph-builder prerequisites remain OPEN; only two direct callers and their small helper/tail chain execute.','No RELA addend points to graph-builder; direct BL linkage only.'])
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();x=build();b=gzip.compress((json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
    if a.check:assert OUT.read_bytes()==b
    else:OUT.write_bytes(b)
    print(json.dumps(dict(path=str(OUT.relative_to(ROOT)),bytes=len(b),sha256=sha(b),counts=x['counts'])))
if __name__=='__main__':main()
