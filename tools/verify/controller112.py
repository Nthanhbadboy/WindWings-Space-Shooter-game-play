"""Native-generated controller schema fixture -> original object payloads.
Native allocator/interner modeled, NOT Unity readback/type registration/runtime.
"""
import gzip,hashlib,json,struct
from pathlib import Path
from collections import Counter
from tools.verify.controller112_native import generate
from tools.verify.controller109_binary import Reader
ROOT=Path(__file__).resolve().parents[2];RAW=ROOT/'reverse-engineering/raw/controller112/probe.json.gz';OUT=ROOT/'datas/l3_ef6b75ef112_native_controller_schema.json.gz'
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def core(n):return {k:([core(c) for c in n[k]] if k=='children' else n[k]) for k in ('type','name','byte_size','meta_flag','children')}
def flatten(n,path=''):
    path=path+'/'+n['name'];return [(path,n)]+[v for c in n['children'] for v in flatten(c,path)]
def build():
    used={RAW,ROOT/'tools/verify/controller112.py',ROOT/'tools/verify/controller112_native.py',ROOT/'tools/verify/controller109_binary.py',ROOT/'.github/workflows/recover-controller112.yml'};raw=json.loads(gzip.decompress(RAW.read_bytes()))
    recovery=ROOT/'tools/recovery/controller112.py';used.add(recovery);assert sha(recovery.read_bytes())==raw['tool_sha256']
    # Audit original ELF mapping and exact retained RELA before fixture uses them.
    spans=raw['native_evidence']['ranges']+raw['native_evidence']['cells']+[o for s in raw['strings'] for o in s['occurrences']]
    for v in spans:
        assert any(s['va']<=v['va'] and v['va']+len(v['hex'])//2<=s['va']+s['file_size'] and v['file_offset']==s['offset']+v['va']-s['va'] for s in raw['segments'])
    for r in raw['native_evidence']['relocations']:assert struct.unpack('<QQq',bytes.fromhex(r['hex']))==(r['address'],1027,r['addend'])
    native=generate(raw);schema=core(native['schema']);nodes=flatten(native['schema']);assert len(nodes)==281
    # Comparison schema used AFTER native generation, never passed as layout to generator.
    oldroot=ROOT/'reverse-engineering/raw/controller109';idxpath=oldroot/'index.json';used.add(idxpath);assert sha(idxpath.read_bytes())==raw['query_schema_sha256'];idx=json.loads(idxpath.read_bytes());shared=next(iter(idx['schemas'].values()));equal=schema==shared;assert equal,'native-generated schema differs from shared builtin comparison'
    results=[];selectors=0;ordinary=0
    for ch in idx['chunks']:
        p=oldroot/ch['path'];used.add(p);assert sha(p.read_bytes())==ch['sha256']
        for row in json.loads(gzip.decompress(p.read_bytes())):
            b=bytes.fromhex(row['hex']);assert len(b)==row['object_byte_size'] and sha(b)==row['raw_sha256'];reader=Reader(b,row['endian']);tree=reader.decode(schema);assert tree==row['unitypy_tree']
            machines=[m['data'] for m in tree['m_Controller']['m_StateMachineArray']]
            selector_rows=[t['data'] for m in machines for s in m['m_SelectorStateConstantArray'] for t in s['data']['m_TransitionConstantArray']]
            ordinary_rows=[t['data'] for m in machines for t in m['m_AnyStateTransitionConstantArray']]+[t['data'] for m in machines for s in m['m_StateConstantArray'] for t in s['data']['m_TransitionConstantArray']]
            assert all(set(t)=={'m_Destination','m_ConditionConstantArray'} for t in selector_rows)
            assert all('m_InterruptionSource' in t and 'm_OrderedInterruption' in t for t in ordinary_rows)
            selectors+=len(selector_rows);ordinary+=len(ordinary_rows)
            results.append(dict(serialized_file=row['serialized_file'],path_id=row['path_id'],raw_sha256=sha(b),byte_size=len(b),consumed=reader.pos,decoded_tree_sha256=sha(canonical(tree)),baseline_tree_sha256=sha(canonical(row['unitypy_tree'])),selector_count=len(selector_rows),ordinary_transition_count=len(ordinary_rows)))
    assert len(results)==308
    types=[dict(path=p,type=n['type'],fields=[dict(name=c['name'],type=c['type'],byte_size=c['byte_size'],meta_flag=c['meta_flag']) for c in n['children']]) for p,n in nodes if n['type'] in ('TransitionConstant','SelectorTransitionConstant')]
    return dict(schema='windwings.native_controller_schema112.v1',provisional=True,provenance='arena/ef6b75ef',xapk_sha256=raw['xapk_sha256'],libunity_sha256=raw['libunity_sha256'],libunity_size=raw['libunity_size'],probe_counts=dict(queries=len(raw['strings']),matched_queries=sum(bool(s['occurrences']) for s in raw['strings']),address_candidates=len(raw['references']),code_ranges=len(raw['native_evidence']['ranges']),pointer_cells=len(raw['native_evidence']['cells']),relocations=len(raw['native_evidence']['relocations'])),native_generation=native,node_count=len(nodes),all_four_core_fields_and_hierarchy_equal_builtin=equal,native_schema_core_sha256=sha(canonical(schema)),transition_type_schemas=types,controller_results=results,decoded_payload_bytes=sum(r['byte_size'] for r in results),full_trees_equal=len(results),ordinary_transition_count=ordinary,selector_transition_count=selectors,scope='Native generator fixture corroborates full schema; original code emits names/types/order and executes size/flag/version/array/end/align logic. Only node allocation/interning is hooked. NOT live Unity TypeTree readback/registration/runtime/render.',limits=['Search strings were seeded from109 shared builtin schema; target selection is not blind/clean-room discovery. Native generation does not consume that layout, only original code/data/relocations.','Begin-node allocation/string interning at0x5eb544 is modeled from preserved original body: version1, zero size/typeFlags, inherited meta flags, child append and iterator/caches. Synthetic root label/type, object, storage, stack/TLS zero fixture; no engine bootstrap or real native TypeTree container readback.','Native type/class91 registration and selection of this generator by a live engine are not executed/proven. Whole schema equality plus308payload reads is bounded corroboration.','Unicorn CPU model and our sink interpretation remain common assumptions; two object-address fixtures share the same sink, not independent engine implementations.','Selector schema field absence is corroborated for captured native generator, not proof of runtime interruption/priority/scheduler semantics.'],inputs={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted(used)})
def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();r=build();b=gzip.compress(canonical(r),mtime=0)
    if a.check:assert OUT.read_bytes()==b,'artifact drift'
    else:OUT.write_bytes(b)
    print('controller112:',r['node_count'],'native schema nodes /',r['full_trees_equal'],'full payload equal /',r['selector_transition_count'],'selector rows PASS')
if __name__=='__main__':main()
