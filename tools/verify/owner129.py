"""M1 owner linkage: the class behind graph-builder node+0x118 and the slots it exposes.

Static byte audit only. Every native word comes from the three pinned cycle-129 probes
(owner129 / owner129b / owner129c) plus the pinned graph127 capture for the callee extents.
No FDE is executed: both producers of node+0x118 need the runtime owner object, and the
selector of the non-null branch is a registry lookup by a runtime instance id.
"""
import argparse,gzip,hashlib,json,re
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_ARM
ROOT=Path(__file__).resolve().parents[2]
P129=ROOT/'reverse-engineering/raw/owner129/probe.json.gz'
P129B=ROOT/'reverse-engineering/raw/owner129b/probe.json.gz'
P129C=ROOT/'reverse-engineering/raw/owner129c/probe.json.gz'
GRAPH127=ROOT/'reverse-engineering/raw/graph127/probe.json.gz'
OUT=ROOT/'datas/l3_ef6b75ef129_native_owner_linkage.json.gz'
PINS={P129:'565e276dd18e49c468868ec3955f0f76b18b6699a62ab7659dc898b4a25d73b6',
      P129B:'1e6e0792546a436814ae913d75f0369222ffd5e427f4be826749a8a485c6154c',
      P129C:'778b001b5dea6e994a5cd71a40013a3239417729858d7ab5156c4e16083591c1',
      GRAPH127:'43adb19f62684262066e4ca71bec636b87e3e5bf0d2a06946de65e24c77fe2e1'}
XAPK_SHA='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
LIBUNITY_SHA='d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7'
CLAIM=6426998422
MD=Cs(CS_ARCH_ARM64,CS_MODE_ARM)
NODE_TABLES={0x10b0f98:'primary',0x10b1100:'secondary',0x10b1130:'tertiary_data'}
WITNESSES=[
(0x6ceb90,'c41f0094','node ctor runs the base ctor 6d6aa0 first'),
(0x6ceba4,'7fa611a9','ctor zero-initialises node+0x118 owner and puts 10b1130 at node+0x120'),
(0x6cebb0,'680200f9','primary vptr 10b0f98 is stored at node+0'),
(0x6cebbc,'688a00f9','secondary vptr 10b1100 (primary+0x168) is stored at node+0x110'),
(0x6cebc4,'0101803d','clears the pair at node+0x138'),
(0x6cebd4,'0101803d','clears the pair at node+0x148'),
(0x6cebe0,'2101803d','clears the pair at node+0x128'),
(0x6cebe4,'685a01b9','node+0x158 initialised to 0x4b'),
(0x6cebfc,'000100ad','clears node+0x188..+0x1a7'),
(0x6cebec,'77d4ff97','subobject ctor 6c3dc8(node+0x170, node+0x110)'),
(0x6cec00,'fd60ff97','subobject ctor 6a6ff4(node+0x1a8)'),
(0x6cec10,'683e00b9','node+0x3c initialised to 3'),
(0x6bba34,'40400791','allocator size argument is x2 + 0x1d0'),
(0x6bba4c,'8837f497','original allocator 3c986c performs the node allocation'),
(0x6bba58,'4c4c0094','node ctor 6ceb88 runs on the fresh allocation'),
(0x6bba7c,'efdbfa97','node is attached to the resolved object by 572a38'),
(0x6b81d0,'9cfaff97','setup path resolves the owner by 6b6c40 before any node exists'),
(0x6b8260,'1f200ba9','node inline vector begins null and ends at node+0x1d0'),
(0x6b8264,'600603f9','node pointer is stored at animator+0x608'),
(0x6b8268,'3f5b0094','6cef64(node, owner) is the only writer of node+0x118'),
(0x6b8290,'4e9ff797','owner+0x38 is registered against animator+0x540 by 49ffc8'),
(0x6cef6c,'088c40f9','dispatch compares the stored owner with the incoming one'),
(0x6cef80,'018c00f9','the only store to any +0x118 field in every pinned window'),
(0x6cef84,'0c020094','graph builder 6cf7b4 is called after the owner store'),
(0x6cef90,'087140f9','node vtable slot +0xe0 loaded after the build'),
(0x6cefac,'086d40f9','owner vtable slot +0xd8 loaded before the final branch'),
(0x6cefd8,'4588fa17','tail branch to 5710ec with (node, w0&1)'),
(0x6cefe4,'f4010094','rebuild wrapper 6cefdc calls the graph builder directly'),
(0x6b6c4c,'089c41b9','owner id is read from +0x19c'),
(0x6b6c58,'945a44f9','global registry pointer lives at 0x10e18b0'),
(0x6b6c74,'d057f397','registry map lookup 38cbb4 keyed by that id'),
(0x6b6ca8,'5b86f497','fallback object lookup 3d8614(id)'),
(0x6cf7e8,'e08e40f9','graph builder loads the owner from node+0x118'),
(0x6cf7f4,'085940f9','owner virtual slot +0xb0'),
(0x6cf80c,'085540f9','owner virtual slot +0xa8 loaded and called with w1=1'),
(0x6cf814,'e09600f9','+0xa8 result stored at node+0x128'),
(0x6cf828,'1c251394','builder b98c98(result, node+0xc0)'),
(0x6cf830,'e09a00f9','node+0x130 receives the first builder output'),
(0x6cf83c,'5e251394','builder b98db4(result, node+0xc0)'),
(0x6cf850,'34261394','builder b99120(result, node+0xc0)'),
(0x6cf85c,'e07e14a9','node+0x140 receives x0 and node+0x148 is cleared'),
(0x6cf86c,'620b0094','child-node factory 6d25f4(node+0x20, 0, 0)'),
(0x6cf870,'08e00591','child inline vector ends at child+0x178'),
(0x6cf880,'093c00b9','child+0x3c is set to 7'),
(0x6cf8a0,'44220094','6d81b0(child, node, -1, w3)'),
(0x572a44,'201000f9','attach writes the controller pointer into node+0x20'),
(0x572a90,'083400b9','attach increments the counter at controller+0x34'),
(0x6ce480,'08c13c91','output ctor installs vptr 10b0f30'),
(0x49ffd4,'15a041a9','list head read at owner+0x38 as {count, pointer}'),
]
CALLED={0x10b0f98:[0xe0,0x138],0x10b1100:[],0x10b1130:[],0x10b0c80:[0x50,0x108],
        0x10b0f30:[0x28],0x10b1240:[],0x10b1150:[],0x10b1330:[]}
NOTES={0x10b0f98:'node primary: +0xe0 used by both dispatch wrappers, +0x138 used by the rebuild check at 6b8000',
       0x10b1100:'node secondary at node+0x110 (primary+0x168)',
       0x10b1130:'node data pointer at node+0x120, no call site in any pinned window',
       0x10b0c80:'animator-side class: +0x50 name accessor at 6b7e0c, +0x108 at 6b7f50; 6b947c is its slot +0xf8',
       0x10b0f30:'"AnimatorOuput" object: +0x28 called at 6b7f04 with the node as argument',
       0x10b1240:'motion node primary from 120 (28 slots); RELA 10b12c0 resolves 6d46a8, not a call site',
       0x10b1420:'motion node secondary from 120 (2 slots)',
       0x10b1150:'manager class from 123 (28 slots)',
       0x10b1330:'factory class from 123/124 (28 slots)'}
FAMILY=[0x10b0f98,0x10b1100,0x10b1130,0x10b0c80,0x10b0f30,0x10b1240,0x10b1420,0x10b1150,0x10b1330]
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):
    b=p.read_bytes();assert sha(b)==PINS[p],(str(p),sha(b));return json.loads(gzip.decompress(b))
def wins(*rs):
    out={}
    for r in rs:
        for w in r['windows']:
            cur=bytes.fromhex(w['hex'])
            if w['va'] in out:assert out[w['va']]==cur,hex(w['va'])
            else:out[w['va']]=cur
    return out
def dis(code,va):return list(MD.disasm(code[:len(code)-(len(code)%4)],va))
def text_map(ws):
    out={}
    for va,code in ws.items():
        for i in dis(code,va):out[i.address]=i
    return out
def witnesses(ws):
    txt=text_map(ws);out=[]
    for pc,expect,role in WITNESSES:
        got=None
        for va,code in ws.items():
            if va<=pc<pc+4<=va+len(code):got=code[pc-va:pc-va+4].hex();break
        assert got==expect,(hex(pc),got,expect)
        assert pc in txt,hex(pc)
        i=txt[pc]
        out.append(dict(pc=pc,word_hex=got,instruction=f'{i.mnemonic} {i.op_str}'.strip(),role=role))
    return out
def field_writes(code,va,base='x19'):
    out=[]
    for i in dis(code,va):
        if i.mnemonic not in ('str','stp','strb','strh','strb','str'):continue
        m=re.search(r'\[%s(?:, #(0x[0-9a-f]+))?\]'%base,i.op_str)
        if not m:continue
        off=int(m.group(1),16) if m.group(1) else 0
        out.append(dict(pc=i.address,offset=off,instruction=f'{i.mnemonic} {i.op_str}'.strip(),word_hex=i.bytes.hex()))
    return out
def node_ctor(ws):
    code=ws[0x6ceb88]
    fw=field_writes(code,0x6ceb88)
    offs=[f['offset'] for f in fw]
    assert len(fw)==8,len(fw)
    assert {0x118,0x110,0x00,0x158,0x160,0x1c0,0x1c8,0x3c}<=set(offs),offs
    vptrs=[dict(offset=0x00,table=0x10b0f98,slots=43,source_pc=0x6cebb0),
           dict(offset=0x110,table=0x10b1100,slots=4,source_pc=0x6cebbc),
           dict(offset=0x120,table=0x10b1130,slots=2,source_pc=0x6ceba4)]
    return dict(entry=0x6ceb88,fde_end=0x6cec1c,bytes=len(code),instructions=len(dis(code,0x6ceb88)),
                base_ctor=0x6d6aa0,base_call_pc=0x6ceb90,subobject_ctors=[dict(pc=0x6cebec,entry=0x6c3dc8,object=0x170,arg=0x110),
                                                                    dict(pc=0x6cec00,entry=0x6a6ff4,object=0x1a8,arg=None)],
                zero_init=dict(owner_field=0x118,pair_store_pc=0x6ceba4,pair_word='7fa611a9'),
                field_writes=fw,vptrs=vptrs,constant_fields=[dict(offset=0x158,value=0x4b),dict(offset=0x3c,value=3)],
                cleared_ranges=[[0x128,0x138],[0x138,0x148],[0x148,0x158],[0x188,0x1a8]],
                note='node+0x118 is zero at construction; no serialized object reaches this ctor')
def node_allocator(ws):
    code=ws[0x6bba20];ins=dis(code,0x6bba20)
    calls=[dict(pc=i.address,target=int(i.op_str[1:],16)) for i in ins if i.mnemonic=='bl']
    assert [c['target'] for c in calls]==[0x3c986c,0x6ceb88,0x570ff0,0x572a38],[c['target'] for c in calls]
    return dict(entry=0x6bba20,fde_end=0x6bba90,bytes=len(code),instructions=len(ins),calls=calls,
                size_expression='x2 + 0x1d0',size_pc=0x6bba34,alignment=0x10,tag=0x5e,
                source_label_va=0x12da21,source_line=0xab,direct_allocator=0x3c986c,
                constructor=0x6ceb88,attach=0x572a38,attach_pc=0x6bba7c,
                guard=dict(field_byte='0x38',bit=0,field_half='0xa8',cleanup=0x570ff0,cleanup_pc=0x6bba70))
def owner_resolver(ws):
    code=ws[0x6b6c40];ins=dis(code,0x6b6c40)
    calls=[dict(pc=i.address,target=int(i.op_str[1:],16)) for i in ins if i.mnemonic=='bl']
    assert [c['target'] for c in calls]==[0x38cbb4,0x3d8614]
    return dict(entry=0x6b6c40,fde_end=0x6b6cc4,bytes=len(code),instructions=len(ins),calls=calls,
                id_field=0x19c,id_load_pc=0x6b6c4c,zero_id_returns_null_pc=0x6b6cb0,
                registry_slot_va=0x10e18b0,registry_slot_pc=0x6b6c58,lookup=0x38cbb4,lookup_pc=0x6b6c74,
                entry_payload_offset=0x10,fallback=0x3d8614,fallback_pc=0x6b6ca8,
                fallback_hook=0x111dba0,fallback_hook_pc=0x3d8620,fallback_negative_id_guard_pc=0x3d8640)
def dispatch(ws):
    a=ws[0x6cef64];b=ws[0x6cefdc]
    ia=dis(a,0x6cef64);ib=dis(b,0x6cefdc)
    slots_a=[];slots_b=[]
    for i in ia:
        m=re.search(r'\[x8, #(0x[0-9a-f]+)\]',i.op_str)
        if m and i.mnemonic=='ldr' and i.address in (0x6cef90,0x6cefac):slots_a.append(dict(pc=i.address,slot=int(m.group(1),16)))
    for i in ib:
        m=re.search(r'\[x8, #(0x[0-9a-f]+)\]',i.op_str)
        if m and i.mnemonic=='ldr' and i.address==0x6ceff0:slots_b.append(dict(pc=i.address,slot=int(m.group(1),16)))
    return dict(set_owner=dict(entry=0x6cef64,fde_end=0x6cefdc,bytes=len(a),instructions=len(ia),
                               owner_field=0x118,compare_pc=0x6cef6c,store_pc=0x6cef80,store_word='018c00f9',
                               builder_call_pc=0x6cef84,builder=0x6cf7b4,virtual_slots=slots_a,tail=0x5710ec,tail_pc=0x6cefd8),
                rebuild=dict(entry=0x6cefdc,fde_end=0x6ceffc,bytes=len(b),instructions=len(ib),
                             builder_call_pc=0x6cefe4,builder=0x6cf7b4,virtual_slots=slots_b,virtual_tail=True))
def graph_builder(ws):
    code=ws[0x6cf7b4];ins=dis(code,0x6cf7b4)
    calls=[dict(pc=i.address,target=int(i.op_str[1:],16)) for i in ins if i.mnemonic=='bl']
    targets=[c['target'] for c in calls]
    for t in (0x6ceeb0,0xb98c98,0xb98db4,0xb99120,0x6d25f4,0x6d81b0):
        assert t in targets,(t,)
    return dict(entry=0x6cf7b4,fde_end=0x6cff44,bytes=len(code),instructions=len(ins),
                owner_field=0x118,owner_load_pc=0x6cf7e8,owner_slots=[dict(slot=0xb0,pc=0x6cf7f4,args=[]),
                                                                        dict(slot=0xa8,pc=0x6cf80c,args=['w1=1'])],
                motion_field=0x128,store_pc=0x6cf814,null_motion_branch=0x6cf8f0,
                builders=[dict(slot=0x130,entry=0xb98c98,call_pc=0x6cf828),
                          dict(slot=0x138,entry=0xb98db4,call_pc=0x6cf83c),
                          dict(slot=0x140,entry=0xb99120,call_pc=0x6cf850)],
                builder_arg='node+0xc0',count_field='motion+0x10',record_bytes=0x10,
                child_factory=dict(entry=0x6d25f4,pc=0x6cf86c,arg='node+0x20',flags=[0,0]),
                child_store_field=0x1a0,child_vector=dict(begin_field=0xb0,end_expression='child+0x178'),
                child_flag=dict(offset=0x3c,value=7),child_binder=dict(entry=0x6d81b0,pc=0x6cf8a0),
                child_bind_flag_source='[[node+0x30]+0x30]==0')
def vtables(rb,rc):
    tabs={t['table_start']:t for t in rc['tables']}
    inst=rc['code_refs']+[dict(target=a['target'],pc=a['pc'],add_va=a['add_va'],hex=a['hex']) for a in rb['adrp_refs']]
    out=[]
    for base in FAMILY:
        t=tabs[base]
        called=[]
        for off in CALLED.get(base,[]):
            idx=off//8
            assert t['slot_count']>idx,(hex(base),hex(off))
            called.append(dict(offset=off,target=t['slots'][idx]['addend'],slot_address=t['slots'][idx]['address']))
        out.append(dict(table_start=base,table_end=t['table_end'],slot_count=t['slot_count'],
                        installed_at=[dict(pc=s['pc'],add_va=s['add_va'],word_hex=s['hex']) for s in sorted(inst,key=lambda x:x['pc']) if s['target']==base],
                        called_slots=called,first_slot=t['slots'][0]['addend'],note=NOTES[base]))
    return out
def m2_contract(graph,fc):
    return dict(status='CONTRACT_ONLY_RUNTIME_INPUT_MISSING',
                producer='owner vtable slot +0xa8 called with w1=1 (6cf80c/6cf810)',
                object_fields=[dict(offset=0x10,role='count of 0x10-byte records read at 6cf8a4')],
                record_bytes=0x10,allocation=dict(slot_object='node+0xc0',vtable_slot=0,size='count<<4',align=8,pc=0x6cf8cc),
                builders=[dict(entry=b['entry'],slot=b['slot'],call_pc=b['call_pc'],fde_end=fc.get(b['entry']),arg='(motion_object, node+0xc0)') for b in graph['builders']],
                missing='no pinned raw contains a native heap object returned by an owner +0xa8 slot call; every builder input would have to be fabricated')
def strings(rc):
    return [dict(va=s['va'],length=s['length'],ascii=s['ascii']) for s in rc['strings']]
def build():
    r=load(P129);rb=load(P129B);rc=load(P129C);rg=load(GRAPH127)
    ws=wins(r,rb,rc)
    assert len(ws)==36,(len(ws),)
    ctor=node_ctor(ws);alloc=node_allocator(ws);res=owner_resolver(ws);disp=dispatch(ws);graph=graph_builder(ws)
    vt=vtables(rb,rc)
    fc={x['entry']:x['unwind']['end'] for x in rg['followed'] if x['unwind']}
    assert fc[0x6cf7b4]==0x6cff44 and fc[0xb98c98]==0xb98d6c and fc[0xb98db4]==0xb98fc8 and fc[0xb99120]==0xb9944c
    assert len(rc['stores_118'])==1 and rc['stores_118'][0]['pc']==0x6cef80 and rc['stores_118'][0]['hex']=='018c00f9'
    assert len([s for s in rc['stores_118'] if s['window']!=0x6cef64])==0
    m1=dict(
      M1a=dict(status='CLOSED_BYTE_EVIDENCE',
               owner_field=dict(offset=0x118,init='zeroed by ctor 6ceba4',writers=1,writer_pc=0x6cef80,writer_function=0x6cef64),
               value_source=dict(function=0x6b6c40,called_from=0x6b81d0,field='+0x19c',kind='runtime instance-id registry lookup',
                                 lookup=0x38cbb4,registry_slot_va=0x10e18b0,fallback=0x3d8614),
               node_class=dict(tables={hex(k):v for k,v in NODE_TABLES.items()},ctor=0x6ceb88,base_ctor=0x6d6aa0,allocator=0x3c986c,size='0x1d0',attach=0x572a38,attach_field=0x20),
               second_producer=dict(function=0x6cefdc,path='vector at animator+0x498 (0x10-byte records), owner equality check at 6b7ff0'),
               shape_constraints=dict(owner_slots=[0xb0,0xa8,0xd8],owner_field=0x38,subobject='owner+0x38 is an intrusive list head (49ffc8)')),
      M1b=dict(status='OPEN_RUNTIME_ONLY',
               missing=['runtime instance id stored at animator+0x19c','contents of the object registry behind 0x10e18b0','the owner object vtable behind slots +0xb0/+0xa8/+0xd8'],
               why='no recovered code installs the owner vtable; the id and the registry are runtime state that static bytes do not carry',
               not_claimed='no class name is assigned; the "%s.Animator"/"AnimatorOuput" strings show the rebuild creates a named graph and output, which is consistent with an Animator-side owner but is not proof of the owner class'))
    m2=m2_contract(graph,fc)
    not_run=[
      dict(function=0x6bba20,reason='needs the original allocator service 3c986c and its hook global; no allocation is performed here'),
      dict(function=0x6ceb88,reason='needs a real allocation plus the two subobject ctors 6c3dc8/6a6ff4 and the base ctor side effects'),
      dict(function=0x6b6c40,reason='needs the live registry map and a real instance id at +0x19c'),
      dict(function=0x6cef64,reason='needs an owner object with real vtable slots +0xd8/+0xb0/+0xa8'),
      dict(function=0x6cefdc,reason='needs a node whose +0x118 owner already points at the live registry object'),
      dict(function=0x6cf7b4,entry_domain='non-null owner',reason='the only pinned execution domain is the null-owner branch recorded in 127; the non-null branch needs owner +0xa8 output'),
      dict(function=0x572a38,reason='needs the controller object created by 6d2894; no such instance is in any pinned raw'),
      dict(function=0x49ffc8,reason='needs owner+0x38 list state and animator+0x540 list state'),
    ]
    counts=dict(probes=3,witnesses=len(WITNESSES),field_writes_ctor=len(ctor['field_writes']),vptrs=len(ctor['vptrs']),
                family_tables=len(vt),family_slots=sum(v['slot_count'] for v in vt),called_slots=sum(len(v['called_slots']) for v in vt),
                builder_calls=len(graph['builders']),not_run=len(not_run),region_tables=len(rc['tables']))
    paths=[P129,P129B,P129C,GRAPH127,ROOT/'tools/verify/owner129.py',ROOT/'tests/test_owner129.py']
    return dict(schema=1,provisional=True,provenance='arena/ef6b75ef',branch='arena/ef6b75ef-windwings-space-shooter-game-p',
      claim=CLAIM,cycle=129,xapk_sha256=XAPK_SHA,libunity_sha256=LIBUNITY_SHA,
      probes=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p.read_bytes()),bytes=len(p.read_bytes()),
                   windows=len(load(p)['windows']),role=role) for p,role in
              [(P129,'caller/linkage BFS and vtable table walk'),(P129B,'producer/owner-resolver bodies and ADRP+ADD vtable installers'),
               (P129C,'node ctor, owner registry, rodata strings, table region')]],
      calibration=dict(vtable_region=[0x10b0a00,0x10b1900],region_tables=len(rc['tables']),stores_118=len(rc['stores_118']),
                       rela_to_targets=[dict(target=t['target'],n=t['n']) for t in rc['rela_to_targets']]),
      witnesses=witnesses(ws),node_constructor=ctor,node_allocator=alloc,owner_resolver=res,dispatch=disp,
      graph_builder=graph,vtable_family=vt,strings=strings(rc),
      m1=m1,m2=m2,not_run=not_run,
      correction_to_127='127 treated node+0x118 as an unidentified clip/controller pointer. Byte evidence now fixes it as the owner field: the node ctor zeroes it (6ceba4), exactly one store writes it (6cef80), and the value is produced by 6b6c40 as a registry lookup of a runtime instance id. The node class is likewise identified by its three installed tables (10b0f98/10b1100/10b1130).',
      counts=counts,inputs={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths},
      scope='Static byte-witnessed linkage of the graph-builder owner field plus a resolved vtable family for the node and animator-side classes. No FDE is executed and no runtime object is fabricated.',
      limits=['No execution: every producer of node+0x118 needs runtime registry state that static bytes do not carry.',
              'Vtable slot counts are RELA-backed dense runs; unrelocated slots stay unknown, not null.',
              'No symbols, RTTI names or Unity class names are asserted; table identity is only the installed address.',
              'No Unity readback, render, game instance, or #27-full closure.'])
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();x=build()
    b=gzip.compress((json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
    if a.check:assert OUT.read_bytes()==b
    else:OUT.write_bytes(b)
    print(json.dumps(dict(path=str(OUT.relative_to(ROOT)),bytes=len(b),sha256=sha(b),counts=x['counts'])))
if __name__=='__main__':main()
