"""Original graph-builder full-FDE null-clip fallback + prerequisite contract."""
import argparse,gzip,hashlib,json
from collections import Counter
from pathlib import Path
from unicorn.arm64_const import UC_ARM64_REG_PC,UC_ARM64_REG_SP,UC_ARM64_REG_TPIDR_EL0
from tools.verify import graph122,vtable123,nodefactories124
from tools.verify.caller118_native import combine
from tools.verify.tag23_113_native import Fixture
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'reverse-engineering/raw/graph127/probe.json.gz'
VER=ROOT/'reverse-engineering/raw/l3-ef6b75ef127-verification'
OUT=ROOT/'datas/l3_ef6b75ef127_native_graph_builder_prelude.json.gz'
GB=0x6cf7b4;GB_RET=0x6cff3c;GB_EPILOGUE=0x6cff0c
CANARY=0x1122334455667788
CALLEES={0x6ceeb0:0x6cef64,0xb98c98:0xb98d6c,0xb98db4:0xb98fc8,0xb99120:0xb9944c,0x6f15cc:0x6f16bc,0x6cff44:0x6d006c}
WITNESSES=[(0x6cf7e8,'e08e40f9','ldr x0,[x23,#0x118]'),(0x6cf7ec,'003900b4','cbz x0,#0x6cff0c'),(0x6cf7f4,'085940f9','ldr x8,[x8,#0xb0]'),(0x6cf7f8,'00013fd6','blr x8'),(0x6cf80c,'085540f9','ldr x8,[x8,#0xa8]'),(0x6cf810,'00013fd6','blr x8'),(0x6cf814,'e09600f9','str x0,[x23,#0x128]'),(0x6cf818,'c00600b4','cbz x0,#0x6cf8f0'),(0x6cf828,'1c251394','bl 0xb98c98'),(0x6cf834,'e10315aa','mov x1,x21'),(0x6cf83c,'5e251394','bl 0xb98db4'),(0x6cf844,'e09e00f9','str x0,[x23,#0x138]'),(0x6cf850,'34261394','bl 0xb99120'),(0x6cf86c,'620b0094','bl 0x6d25f4'),(0x6cf8a0,'44220094','bl 0x6d81b0'),(0x6cf994,'e0e200f9','str x0,[x23,#0x1c0]'),(0x6cfd68,'de2b2794','bl 0x109ace0'),(0x6cfee8,'b9850094','bl 0x6f15cc'),(0x6cff04,'10000094','bl 0x6cff44'),(0x6cff0c,'a81640f9','ldr x8,[x21,#0x28]'),(0x6cff18,'41010054','b.ne #0x6cff40'),(0x6cff3c,'c0035fd6','ret'),(0x6ceec4,'00d040f9','ldr x0,[x0,#0x1a0]'),(0x6ceec8,'000100b4','cbz x0,#0x6ceee8'),(0x6ceed4,'3c86fa97','bl 0x5707c4'),(0x6ceee0,'138ffa97','bl 0x572b2c'),(0x6ceee8,'68ca41b9','ldr w8,[x19,#0x1c8]'),(0x6cef04,'68e240f9','ldr x8,[x19,#0x1c0]'),(0x6cef18,'48e9f397','bl 0x3c9438'),(0x6cef30,'60e240f9','ldr x0,[x19,#0x1c0]'),(0x6cef44,'3de9f397','bl 0x3c9438'),(0x6cef48,'7fe200f9','str xzr,[x19,#0x1c0]'),(0x6cef4c,'7fca01b9','str wzr,[x19,#0x1c8]')]
REQUIRED_FIELDS=[dict(offset='0x118',role='controller/clip source pointer; null selects original epilogue fallback',witness_pc=0x6cf7e8),dict(offset='0x1a0',role='previous graph/child list head freed by6ceeb0',witness_pc=0x6ceec4),dict(offset='0x1c8',role='child count; <=0 skips per-child free loop',witness_pc=0x6ceee8),dict(offset='0x1c0',role='child pointer array; freed then zeroed',witness_pc=0x6cef04),dict(offset='0xc8',role='allocator category/owner id passed to free/alloc services',witness_pc=None),dict(offset='0x20',role='owner/parent object used by6ceeb0 and first factory',witness_pc=None),dict(offset='0x30',role='pool chunk whose+0x30 length selects registration slot',witness_pc=None),dict(offset='0x128',role='clip-data result of virtual+0xa8',witness_pc=0x6cf814),dict(offset='0x130',role='b98c98 result',witness_pc=None),dict(offset='0x138',role='b98db4 result',witness_pc=0x6cf844),dict(offset='0x140',role='b99120 result plus zero',witness_pc=None)]
MISSING_X=[dict(id='M1',item='controller/clip object at node+0x118 with original vtable slots +0xb0/+0xa8',blocked_by='serialized Animator controller/clip instance bytes and native vtable identity; not in any pinned raw'),dict(id='M2',item='clip-data structure consumed by b98c98/b98db4/b99120',blocked_by='real serialized m_ClipBindingConstant-like blobs at clip+0xc0'),dict(id='M3',item='owner/pool objects at node+0x20/+0x30 for factories and registration',blocked_by='original factory/pool bootstrap; prepared synthetic only'),dict(id='M4',item='child arrays at node+0x1c0/+0x1c8 and previous list node+0x1a0',blocked_by='runtime graph construction'),dict(id='M5',item='6f15cc binding tables (node+0x128,+0x138,+0x130,+0x1c0)',blocked_by='same serialized clip data as M1/M2')]
def sha(b):return hashlib.sha256(b).hexdigest()
def raw():return json.load(gzip.open(RAW))
def merged():return combine(combine(graph122.merged(),vtable123.raw()),combine(nodefactories124.raw(),raw()))
def fixture_raw(r):return dict(windows=r['windows'],native_slices=r['cells'],strings=r['strings'],relocations=r['relocations'],imports=r.get('imports',[]),pointed_strings=r.get('pointed_strings',[]))
def prepare(f,node,dealloc,tls,prefill):
    r=merged();f.put(node,bytes([prefill])*0x200,False);f.put(node+0x118,bytes(8),False);f.put(node+0x1a0,bytes(8),False);f.put(node+0x1c0,bytes(8),False);f.sw(node+0x1c8,0);f.put(dealloc,bytes(4),False);f.put(tls,bytes(0x100),False);f.sq(tls+0x28,CANARY);f.u.reg_write(UC_ARM64_REG_TPIDR_EL0,tls)
    calls=[]
    def free(f):
        calls.append(dict(symbol='dealloc_3c9438',object=f.reg(0),category=f.reg(1)&0xffffffff));f.ret()
    f.sinks[0x3c9438]=free
    return dict(node=node,dealloc=dealloc,tls=tls,prefill=prefill,calls=calls)
def disasm_witness(r):
    out=[]
    for pc,expect,text in WITNESSES:
        got=None
        for w in r['windows']:
            b=bytes.fromhex(w['hex'])
            if w['va']<=pc and pc+4<=w['va']+len(b):got=b[pc-w['va']:pc-w['va']+4].hex();break
        assert got==expect,(hex(pc),got,expect)
        out.append(dict(pc=pc,word_hex=got,text=text))
    return out
def case(prefill=0xa5,base=0x3000000):
    f=Fixture(fixture_raw(merged()),base);node=base+0x4000;p=prepare(f,node,base+0x8000,base+0x6000,prefill)
    run=f.call(GB,(node,));hits=Counter(f.visits)
    assert f.visits[-1]==GB_RET and f.u.reg_read(UC_ARM64_REG_PC)==f.stop and f.u.reg_read(UC_ARM64_REG_SP)==f.base+0x1f000 and f.q(p['tls']+0x28)==CANARY
    assert 0x6ceeb0 in hits and GB_EPILOGUE in hits and GB_RET in hits and 0x6cefc0 not in hits
    assert 0x6ceec8 in hits and 0x6cef44 in hits and hits[0x6cef44]==1 and 0x6cef18 not in hits and 0x6cef04 not in hits
    for pc in (0x6cf7f4,0x6cf7f8,0x6cf810,0x6cf828,0x6cf86c,0x6cf8a0,0x6cfd68,0x6cfee8,0x6cff04):assert pc not in hits,hex(pc)
    assert len(p['calls'])==1 and p['calls'][0]['object']==0
    assert f.q(node+0x1c0)==0 and f.w(node+0x1c8)==0 and bytes(f.u.mem_read(node+0x118,8))==bytes(8)
    return dict(prefill=prefill,base=base,ret=f.visits[-1],stack_pointer_after=f.u.reg_read(UC_ARM64_REG_SP),run=run,pc_hits={hex(k):v for k,v in sorted(hits.items()) if k in (GB,0x6ceeb0,0x6ceec8,0x6cef44,GB_EPILOGUE,GB_RET,0x6cefc0)},service_calls=list(p['calls']),node_after=dict(slot118=f.q(node+0x118),slot1a0=f.q(node+0x1a0),slot1c0=f.q(node+0x1c0),count1c8=f.w(node+0x1c8)))
def build():
    r=raw();fde={x['entry']:x['unwind']['end'] for x in r['followed'] if x['unwind']}
    assert all(fde.get(k)==v for k,v in CALLEES.items()) and fde[GB]==0x6cff44
    cases=[case(0xa5),case(0),case(0xa5,0x4000000)]
    paths=[RAW,VER/'claim.json',VER/'recovery.json',Path(__file__),ROOT/'tests/test_graph127.py',ROOT/'tools/recovery/graph127.py',ROOT/'tools/verify/graph122.py',ROOT/'tools/verify/vtable123.py',ROOT/'tools/verify/nodefactories124.py']
    return dict(schema=1,provisional=True,provenance='arena/ef6b75ef',claim=6425979864,graph_builder=dict(entry=GB,fde_end=fde[GB],ret=GB_RET,epilogue=GB_EPILOGUE,callees={hex(k):dict(ret=v-4,fde_end=v) for k,v in CALLEES.items()}),witnesses=disasm_witness(r),required_fields=REQUIRED_FIELDS,missing_x=MISSING_X,inputs={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths},cases=cases,counts=dict(cases=len(cases),native_instructions=[c['run']['instruction_count'] for c in cases],dealloc_calls=sum(len(c['service_calls']) for c in cases),callees=len(CALLEES),witnesses=len(WITNESSES),missing_x=len(MISSING_X)),domain='node+0x118=0, node+0x1a0=0, node+0x1c0=0, node+0x1c8=0: original graph-builder selects its own cbz epilogue path before any clip/vtable/factory use',scope='Full original graph-builder FDE entry-to-RET on the null-clip domain, with only original3c9438 deallocator as an explicit synthetic sink and prepared node/TLS storage. Proves the original early-exit/epilogue path and 6ceeb0 cleanup, NOT the build path. Clip/vtable/factory/serialized-controller prerequisites remain OPEN and are mapped, not fabricated.',limits=['Null-clip domain never executes graph-builder build path (6cf7f4 virtual, factories, 6f15cc).','3c9438 deallocator is a declared sink; original heap is not executed.','Field contract is static byte-witnessed for listed PCs; offsets with witness_pc=null come from surrounding disassembly and are not individually word-asserted in this artifact.','No runtime, Unity readback/render, observed game instance, or #27-full closure.'])
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();x=build();b=gzip.compress((json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
    if a.check:assert OUT.read_bytes()==b
    else:OUT.write_bytes(b)
    print(json.dumps(dict(path=str(OUT.relative_to(ROOT)),bytes=len(b),sha256=sha(b),counts=x['counts'])))
if __name__=='__main__':main()
