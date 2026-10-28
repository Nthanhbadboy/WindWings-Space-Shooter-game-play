"""M2 split: serialized clip/motion content versus the runtime motion-set object.

Static audit only. All native bytes come from the pinned 127 recovery
(reverse-engineering/raw/graph127/probe.json.gz, XAPK f5d3c7a1...). No FDE is
executed here: the three builders consume a runtime object that no pinned raw
contains, so running them would require fabricating it.
"""
import argparse,gzip,hashlib,json,re
from collections import Counter
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_ARM
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'reverse-engineering/raw/graph127/probe.json.gz'
MOTION=ROOT/'datas/l3-scene-chains/motion-000.json.gz'
CTRL_TREES=ROOT/'reverse-engineering/raw/typetrees/animator-controller-graphs.jsonl.gz'
CTRL_GRAPHS=ROOT/'reverse-engineering/raw/animation-audit/controller-graphs.json.gz'
CLIP_LINKS=ROOT/'reverse-engineering/raw/animation-audit/enemy-clip-links.json.gz'
VER=ROOT/'reverse-engineering/raw/l3-ef6b75ef128-verification'
OUT=ROOT/'datas/l3_ef6b75ef128_native_motion_input_contract.json.gz'
RAW_SHA='43adb19f62684262066e4ca71bec636b87e3e5bf0d2a06946de65e24c77fe2e1'
XAPK_SHA='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
LIBUNITY_SHA='d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7'
CLAIM=6426286596
CONTROLLER=1856
CLIP_IDS=[1391,1392,1393,1394,1395,1396,1397,1398]
BUILDERS={0xb98c98:0xb98d6c,0xb98db4:0xb98fc8,0xb99120:0xb9944c,0x6cff44:0x6d006c}
MD=Cs(CS_ARCH_ARM64,CS_MODE_ARM)
# (pc, exact little-endian word, role) - every word is re-asserted from the pinned raw.
WITNESSES=[
(0x6cf7e8,'e08e40f9','node+0x118 holds the owner pointer that supplies the motion set'),
(0x6cf7ec,'003900b4','null owner selects the original epilogue fallback'),
(0x6cf7f4,'085940f9','owner vtable slot +0xb0 loaded before the first virtual call'),
(0x6cf80c,'085540f9','owner vtable slot +0xa8 loaded; called with w1=1'),
(0x6cf814,'e09600f9','motion-set pointer returned by +0xa8 stored at node+0x128'),
(0x6cf818,'c00600b4','null motion selects the original error path at 6cf8f0'),
(0x6cf8a4,'681240b9','secondary count read from motion+0x10'),
(0x6cf8b8,'16ed7cd3','secondary slot array sized count<<4'),
(0x6cf8cc,'20013fd6','allocator vtable[0] call through the object at node+0xc0'),
(0x6cf9b8,'7a610091','secondary table base at motion+0x18'),
(0x6cf9c4,'096973f8','slot-relative secondary offset load'),
(0x6cf9d0,'083540b9','secondary record count at +0x34'),
(0x6cfa9c,'2a0140b9','child record index at +0x00'),
(0x6cfaac,'380540b9','child record slot index at +0x04'),
(0x6cfc28,'a21b40b9','child record count at +0x18 passed to 6d2950'),
(0x6cfee8,'b9850094','per-child binding-table call 6f15cc'),
(0x6cff5c,'169440f9','delivery tail reads the motion set from node+0x128'),
(0x6cff60,'c80240b9','delivery loop bound is motion+0x00'),
(0x6cff88,'691a40f9','delivery target read from node+0x30'),
(0x6cff8c,'291140f9','delivery target pointer at chunk+0x20'),
(0x6cff90,'350140f9','delivery object taken from the first qword of that pointer'),
(0x6cfff0,'480d40f9','delivery virtual slot +0x18 loaded'),
(0x6cfffc,'00013fd6','delivery virtual call on the prepared target'),
(0x6d000c,'3f1b0094','delivery helper 6d6d08'),
(0x6d0038,'461b0094','delivery helper 6d6d50'),
(0xb98cc4,'01048052','binding-table header allocation size 0x20'),
(0xb98cb8,'02018052','binding-table header alignment 8'),
(0xb98cd0,'00013fd6','allocator virtual call'),
(0xb98cd4,'08f0a752','float 1.0 prepared for the header'),
(0xb98cd8,'080000b9','header +0x00 receives 1.0f'),
(0xb98ce0,'a80240b9','binding count read from motion+0x00'),
(0xb98cf8,'0805088b','binding count expanded by 3'),
(0xb98cfc,'15f17dd3','binding record byte size count*24'),
(0xb98d3c,'600e00f9','binding record array stored at header+0x18'),
(0xb98dd4,'01068052','child-table allocation size 0x30'),
(0xb98e08,'a80240b9','child-table takes motion+0x00'),
(0xb98e1c,'a11240b9','child-table takes motion+0x10'),
(0xb98e40,'881240b9','weight-array length from child-table+0x10'),
(0xb98e94,'880e00f9','weight array stored at child-table+0x18'),
(0xb98e98,'280d42f8','motion+0x20 merge pointer read'),
(0xb98eac,'022ded97','merge builder 6e42b4'),
(0xb98ec8,'2b8d42f8','motion+0x28 merge pointer read'),
(0xb98ee4,'2925ed97','merge builder 6e2388'),
(0xb98f1c,'802940bd','child weight read at record+0x28'),
(0xb98f74,'735aed97','child object builder 6ef940'),
(0xb99144,'01058052','secondary object allocation size 0x28'),
(0xb99160,'a81240b9','secondary object takes motion+0x10'),
(0xb991a8,'760600f9','pointer array stored at secondary object+0x08'),
(0xb991f0,'760200f9','pointer array stored at secondary object+0x00'),
(0xb991f8,'681a00b9','secondary count stored at +0x18'),
(0xb99220,'8c3540b9','secondary record count read at +0x34'),
(0xb9922c,'8831881a','running maximum selected across secondary records'),
(0xb99290,'94061494','max-sized array zeroing call'),
(0xb99300,'3a58ed97','per-record lookup 6ef3e8'),
(0xb99308,'e216ed97','count probe 6dee90'),
(0xb99360,'345aed97','record builder 6efc30'),
(0xb99390,'d959ed97','record builder 6efaf4'),
(0xb993ac,'a80e42f8','motion+0x20 merge read in the secondary builder'),
(0xb99428,'740a00f9','byte array stored at secondary object+0x10'),
(0x6ef95c,'01108052','child object allocation size 0x80'),
(0x6ef964,'02018052','child object alignment 8'),
]
MOTION_HEADER=[
 dict(offset='0x00',width=4,field='child_count',role='number of child motions; bound of the delivery loop and of the binding table',witness_pc=0xb98e08),
 dict(offset='0x08',width=8,field='child_table',role='array of slot-relative int64 pointers to child records',witness_pc=0xb98f00),
 dict(offset='0x10',width=4,field='secondary_count',role='number of secondary records; bound of the GB allocation loop',witness_pc=0xb98e1c),
 dict(offset='0x18',width=8,field='secondary_table',role='array of slot-relative int64 pointers to secondary records',witness_pc=0x6cf9b8),
 dict(offset='0x20',width=8,field='merge_a',role='slot-relative pointer merged by 6e42b4',witness_pc=0xb98e98),
 dict(offset='0x28',width=8,field='merge_b',role='slot-relative pointer merged by 6e2388',witness_pc=0xb98ec8),
]
CHILD_RECORD=[
 dict(offset='0x00',width=4,field='motion_index',role='compared with the child loop index',witness_pc=0x6cfa9c),
 dict(offset='0x04',width=4,field='slot_index',role='index into the per-secondary slot array built at node+0x1c0',witness_pc=0x6cfaac),
 dict(offset='0x18',width=4,field='child_count',role='third argument of graph populator 6d2950',witness_pc=0x6cfc28),
 dict(offset='0x24',width=4,field='flag_eq1',role='bool delivered to 6d6d50 (compare with 1)',witness_pc=0x6d002c),
 dict(offset='0x28',width=4,field='weight_f32',role='per-child weight copied into the N0-float array',witness_pc=0xb98f1c),
 dict(offset='0x30',width=4,field='child_word_30',role='copied into the 0x80 child object at +0x18',witness_pc=0x6ef9a8),
 dict(offset='0x34',width=4,field='child_word_34',role='length of the two child-object arrays',witness_pc=0x6ef9b4),
]
SECONDARY_RECORD=[
 dict(offset='0x00',width=4,field='sub_count',role='bound of the nested sub-record loop',witness_pc=0xb992c0),
 dict(offset='0x08',width=8,field='sub_table',role='slot-relative pointer array; per-sub record built by 6efaf4',witness_pc=0xb992e0),
 dict(offset='0x34',width=4,field='curve_count',role='bound of the per-child slot array and of the max scan',witness_pc=0xb992c8),
]
ALLOCATIONS=[
 dict(builder='0xb98c98',size='0x20',alignment=8,witness_pc=0xb98cc4,role='binding-table header'),
 dict(builder='0xb98c98',size='count*0x18',alignment=4,witness_pc=0xb98cfc,role='binding records, zero filled'),
 dict(builder='0xb98db4',size='0x30',alignment=8,witness_pc=0xb98dd4,role='child table'),
 dict(builder='0xb98db4',size='count*4',alignment=4,witness_pc=0xb98e40,role='per-child weights'),
 dict(builder='0xb99120',size='0x28',alignment=8,witness_pc=0xb99144,role='secondary object'),
 dict(builder='0xb99120',size='count*8',alignment=8,witness_pc=0xb99170,role='pointer array at +0x00'),
 dict(builder='0xb99120',size='count*8',alignment=8,witness_pc=0xb991b8,role='pointer array at +0x08'),
 dict(builder='0xb99120',size='max*4',alignment=1,witness_pc=0xb99244,role='max-sized byte array'),
 dict(builder='0x6ef940',size='0x80',alignment=8,witness_pc=0x6ef95c,role='child object'),
]
DERIVED=[
 dict(builder='0xb98c98',size=0x20,fields=['+0x00=1.0f','+0x18=binding records'],note='the records are zero filled; no serialized binding value is copied here'),
 dict(builder='0xb98db4',size=0x30,fields=['+0x00=secondary_count','+0x08=N1 child pointers','+0x10=child_count','+0x18=N0 weights','+0x20=merge_a'],note='caller-visible child/weight table'),
 dict(builder='0xb99120',size=0x28,fields=['+0x00=pointer array','+0x08=pointer array','+0x10=byte array','+0x18=secondary_count','+0x20=max array'],note='secondary record container'),
 dict(builder='0x6ef940',size=0x80,fields=['+0x00=word_34','+0x08=pointer array','+0x10=pointer array','+0x18=child word_30'],note='per-child object; byte +0x78 cleared by the graph builder'),
]
NOT_RUN=[
 dict(fde='0xb98c98',reason='needs motion+0x00; a synthetic count would fabricate the binding count under test'),
 dict(fde='0xb98db4',reason='needs motion+0x00/0x10/0x20/0x28; the merge sub-objects do not exist in any pinned raw'),
 dict(fde='0xb99120',reason='needs motion+0x10/0x18 and per-record sub-tables'),
 dict(fde='0x6cff44',reason='reads node+0x128/node+0x138, i.e. the objects built by the unrun builders'),
 dict(fde='0x6f15cc',reason='needs node+0x138/node+0x140 and per-child slot arrays'),
 dict(fde='0x6e42b4',reason='merges motion+0x20; structure absent'),
 dict(fde='0x6e2388',reason='merges motion+0x28; structure absent'),
 dict(fde='0x6ef940',reason='called only inside the N1/N0 loops that cannot run'),
 dict(fde='0x6ef3e8,0x6dee90,0x6efc30,0x6efaf4',reason='called only inside the secondary-record loop'),
]
def sha(b):return hashlib.sha256(b).hexdigest()
def raw_bytes():return RAW.read_bytes()
def raw():return json.loads(gzip.decompress(raw_bytes()))
def code_windows(r):
    out={}
    for w in r['windows']:out.setdefault(w['va'],bytes.fromhex(w['hex']))
    return out
def fde_map(r):return {x['entry']:x['unwind']['end'] for x in r['followed'] if x['unwind']}
def disasm(code,entry):return list(MD.disasm(code[:len(code)-(len(code)%4)],entry))
def builder(r,wins,fde,entry):
    code=wins[entry][:fde[entry]-entry]
    ins=disasm(code,entry)
    bases=Counter()
    for i in ins:
        if i.mnemonic.startswith('st'):
            m=re.search(r'\[([a-z0-9]+)',i.op_str)
            if m:bases[m.group(1)]+=1
    calls=[]
    for i in ins:
        if i.mnemonic=='bl' and i.op_str.startswith('#'):
            calls.append(dict(pc=i.address,target=int(i.op_str[1:],16)))
    return dict(entry=entry,fde_end=fde[entry],ret=fde[entry]-4,bytes=len(code),instructions=len(ins),store_bases=dict(sorted(bases.items())),direct_calls=calls)
def witnesses(r):
    wins=code_windows(r);text={}
    for va,code in wins.items():
        for i in disasm(code,va):text[i.address]=f'{i.mnemonic} {i.op_str}'.strip()
    out=[]
    for pc,expect,role in WITNESSES:
        got=None
        for va,code in wins.items():
            if va<=pc<pc+4<=va+len(code):got=code[pc-va:pc-va+4].hex();break
        assert got==expect,(hex(pc),got,expect)
        assert pc in text and text[pc]!='',hex(pc)
        out.append(dict(pc=pc,word_hex=got,instruction=text[pc],role=role))
    return out
def clips():
    rows=[json.loads(l) for l in gzip.open(MOTION,'rt')]
    assert len(rows)==1 and isinstance(rows[0],list)
    by={c['identity']['path_id']:c for c in rows[0]}
    assert all(c['identity']['serialized_file']=='data.unity3d/resources.assets' for c in by.values() if c['identity']['path_id'] in CLIP_IDS)
    out=[]
    for pid in CLIP_IDS:
        c=by[pid];d=c['dense']
        out.append(dict(path_id=pid,name=c['name'],status=c['status'],bindings=len(c['bindings']),pptr_curve_mapping=len(c['pptr_curve_mapping']),streamed_frames=len(c['streamed']),dense_curve_count=d['m_CurveCount'],dense_sample_count=len(d['m_SampleArray']),constant_values=len(c['constants']),channel_count=c['channel_count'],binding_channel_count=c['binding_channel_count'],binding_coverage_exact=c['binding_coverage_exact'],events=len(c['events'])))
    return out
def controller_tree():
    rows=[json.loads(l) for l in gzip.open(CTRL_TREES,'rt')]
    assert set(r['type'] for r in rows)=={'AnimatorController'}
    sel=[r for r in rows if r['path_id']==CONTROLLER];assert len(sel)==1
    t=sel[0]['tree'];mc=t['m_Controller'];sm=mc['m_StateMachineArray'][0]['data'];states=sm['m_StateConstantArray']
    trees=nodes=child_indices=0;clip_ids=[]
    for s in states:
        d=s['data']
        for bt in d['m_BlendTreeConstantArray']:
            trees+=1
            for n in bt['data']['m_NodeArray']:
                nodes+=1;child_indices+=len(n['data']['m_ChildIndices']);clip_ids.append(n['data']['m_ClipID'])
    assert 'm_ClipBindingConstant' not in json.dumps(t)
    return dict(path_id=CONTROLLER,name=t['m_Name'],controller_size=t['m_ControllerSize'],layers=len(mc['m_LayerArray']),state_constants=len(states),blend_tree_constants=trees,blend_nodes=nodes,total_child_indices=child_indices,clip_ids=clip_ids,has_clip_binding_constant=False,raw_sha256=sha(CTRL_TREES.read_bytes()))
def audit_graphs():
    blob=CTRL_GRAPHS.read_bytes();d=json.loads(gzip.decompress(blob));text=gzip.decompress(blob).decode()
    row=[c for c in d['controllers'] if c['path_id']==CONTROLLER]
    assert len(row)==1 and 'ClipBinding' not in text and 'pptrCurve' not in text
    return dict(sha256=sha(blob),controllers=len(d['controllers']),controller_1856=1,states=len(row[0]['machines'][0]['states']),parameters=len(row[0]['parameters']),layer_binding_hash=row[0]['layers_raw'][0]['data']['m_Binding'],has_clip_binding_constant=False,note='layer rows carry only the m_Binding hash; no genericBindings or pptrCurveMapping')
def audit_links():
    blob=CLIP_LINKS.read_bytes();d=json.loads(gzip.decompress(blob))
    a=[x for x in d['animators'] if x['controller_ref']['m_PathID']==CONTROLLER];assert len(a)==1
    return dict(sha256=sha(blob),animators=len(d['animators']),controller_1856_clips=len(a[0]['clips']),declared_clip_count=a[0]['declared_clip_count'],muscle_bytes=sum(c['muscle_bytes'] for c in a[0]['clips']),events=sum(len(c.get('events',[])) for c in a[0]['clips']),curves_decoded_false=sum(1 for c in a[0]['clips'] if not c['curves_decoded']),has_clip_binding_constant=False,note='per-clip membership plus muscle byte counts only; curves_decoded=false for all rows')
def build():
    rb=raw_bytes();assert sha(rb)==RAW_SHA
    r=raw();wins=code_windows(r);fde=fde_map(r)
    assert len(r['windows'])==44 and len(wins)==42 and len(r['followed'])==39 and len(fde)==37
    builders=[builder(r,wins,fde,e) for e in sorted(BUILDERS)]
    bs={hex(b['entry']):b for b in builders}
    assert bs['0xb98c98']['instructions']==53 and bs['0xb98db4']['instructions']==133 and bs['0xb99120']['instructions']==203 and bs['0x6cff44']['instructions']==74
    assert 'x21' not in bs['0xb98c98']['store_bases'] and 'x21' not in bs['0xb98db4']['store_bases'] and 'x21' not in bs['0xb99120']['store_bases'] and 'x22' not in bs['0x6cff44']['store_bases']
    cl=clips();totals=dict(clips=len(cl),bindings=sum(c['bindings'] for c in cl),pptr_curve_mappings=sum(c['pptr_curve_mapping'] for c in cl),streamed_frames=sum(c['streamed_frames'] for c in cl),dense_curve_count=sum(c['dense_curve_count'] for c in cl),constant_values=sum(c['constant_values'] for c in cl),channel_count=sum(c['channel_count'] for c in cl),binding_channel_count=sum(c['binding_channel_count'] for c in cl),events=sum(c['events'] for c in cl))
    assert totals==dict(clips=8,bindings=402,pptr_curve_mappings=0,streamed_frames=142,dense_curve_count=0,constant_values=177,channel_count=654,binding_channel_count=654,events=4)
    assert all(c['binding_coverage_exact'] for c in cl) and all(c['status']=='numeric_stream_dense_constant_decoded_not_playback' for c in cl)
    ctr=controller_tree();assert (ctr['layers'],ctr['state_constants'],ctr['blend_tree_constants'],ctr['blend_nodes'],ctr['total_child_indices'],ctr['controller_size'])==(1,8,8,8,0,4110)
    assert ctr['clip_ids']==[7,1,2,3,4,5,6,0]
    gr=audit_graphs();lk=audit_links();assert (gr['controllers'],lk['animators'],lk['muscle_bytes'],lk['curves_decoded_false'],lk['events'])==(52,154,72300,8,4)
    m2=[
      dict(id='M2a',status='AVAILABLE_SERIALIZED_CONTENT',covers='generic binding counts and channel coverage for the 8 controller-1856 clips, streamed/dense/constant arrays, controller layer/state/blend-tree structure',inputs=[dict(artifact='datas/l3-scene-chains/motion-000.json.gz',sha256=sha(MOTION.read_bytes()),clips=665,target=8,totals=totals),dict(artifact='reverse-engineering/raw/typetrees/animator-controller-graphs.jsonl.gz',sha256=ctr['raw_sha256'],controller=ctr)],does_not_cover='runtime object layout, memory offsets, slot-relative pointer relocation, per-child weight table'),
      dict(id='M2b',status='MISSING_RUNTIME_OBJECT',requires='one motion-set object with the 6-word header, N0 child records with 7 witnessed fields and N1 secondary records with 3 witnessed fields',why='native heap object; no pinned raw captures a native heap instance and no captured FDE constructs it'),
      dict(id='M2c',status='MISSING_PRODUCER',blocked_by='owner vtable slots +0xb0/+0xa8 at node+0x118; the owner class/vtable is still unidentified (M1)',evidence='the only producer in the captured graph is the indirect call 6cf7f8/6cf810; no BL in the 39 followed entries returns the motion set'),
    ]
    paths=[RAW,MOTION,CTRL_TREES,CTRL_GRAPHS,CLIP_LINKS,VER/'claim.json',ROOT/'tools/verify/motion128.py',ROOT/'tests/test_motion128.py']
    return dict(schema=1,provisional=True,provenance='arena/ef6b75ef',claim=CLAIM,cycle=128,xapk_sha256=XAPK_SHA,libunity_sha256=LIBUNITY_SHA,
      fde_recovery=dict(run=40391655099,source='b0a585e5e',raw_sha256=RAW_SHA,note='no new libunity bytes are recovered by 128; all code bytes are the pinned 127 capture'),
      captured=dict(windows=len(r['windows']),unique_windows=len(wins),followed_entries=len(r['followed']),original_fde_entries=len(fde),bounded_windows=len(r['followed'])-len(fde)),
      builders=builders,motion_header=MOTION_HEADER,child_record=CHILD_RECORD,secondary_record=SECONDARY_RECORD,allocations=ALLOCATIONS,derived_objects=DERIVED,
      delivery_contract=dict(node_field='0x30',chunk_field='0x20',target='first qword of the structure at [[node+0x30]+0x20]',virtual_slot='0x18',loop_bound='motion+0x00',helpers=[0x6d6d08,0x6d6d50],witness_pcs=[0x6cff88,0x6cff8c,0x6cff90,0x6cfff0,0x6cfffc,0x6d000c,0x6d0038],status='MISSING_TARGET_IDENTITY: node+0x30 is a prepared synthetic chunk in 122-127; the original animator/target object is not in any pinned raw'),
      witnesses=witnesses(r),controller_1856=ctr,clips=cl,clip_totals=totals,negative_artifacts=dict(controller_graphs=gr,enemy_clip_links=lk),
      m2=m2,correction_to_127='127 recorded M2 as "not in any pinned raw". That is exact for the runtime motion-set object (M2b) but too broad for serialized content: the 8 clips of controller 1856 are pinned with 402 generic bindings and 654 covered channels (M2a). The builders still cannot run, so the 127 execution boundary is unchanged.',
      not_run=NOT_RUN,
      counts=dict(builders=len(builders),witnesses=len(WITNESSES),motion_header_fields=len(MOTION_HEADER),child_fields=len(CHILD_RECORD),secondary_fields=len(SECONDARY_RECORD),allocations=len(ALLOCATIONS),delivery_witnesses=7,clips=len(cl),pinned_bindings=totals['bindings'],pinned_pptr=0,m2_items=len(m2)),
      inputs={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths},
      scope='Static byte-witnessed contract for the three motion/binding builders and the delivery tail, plus a counted audit of pinned serialized controller/clip content. No FDE is executed: the builders consume a runtime motion-set object that no pinned artifact contains, so executing them would require fabricating the object under test.',
      limits=['No execution in 128: builder inputs (M2b) are absent, so the earlier null-domain execution boundary is unchanged.','The serialized binding counts are content evidence, not a runtime object; no offset or pointer identity is claimed between the two.','Owner class and vtable slots +0xb0/+0xa8 remain unidentified (M1); no Unity readback, render, game instance, or #27-full closure.'])
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();x=build();b=gzip.compress((json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
    if a.check:assert OUT.read_bytes()==b
    else:OUT.write_bytes(b)
    print(json.dumps(dict(path=str(OUT.relative_to(ROOT)),bytes=len(b),sha256=sha(b),counts=x['counts'])))
if __name__=='__main__':main()
