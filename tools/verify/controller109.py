"""Independent object payload decoding/differential of recovered controllers.
Shared UnityPy builtin schema and framing remain a disclosed dependency.
"""
import gzip,hashlib,json
from pathlib import Path
from tools.verify.controller109_binary import Reader
ROOT=Path(__file__).resolve().parents[2];RAW=ROOT/'reverse-engineering/raw/controller109';OUT=ROOT/'datas/l3_ef6b75ef109_controller_decode.json.gz'
def canonical(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def identity(r):return r['serialized_file'],r['path_id']
def unbox(x):return x['data']
def census(tree):
 c=tree['m_Controller'];machines=[unbox(x) for x in c['m_StateMachineArray']];states=[unbox(s) for m in machines for s in m['m_StateConstantArray']];anys=[unbox(t) for m in machines for t in m['m_AnyStateTransitionConstantArray']];state=[unbox(t) for s in states for t in s['m_TransitionConstantArray']];selectors=[unbox(t) for m in machines for s in m['m_SelectorStateConstantArray'] for t in unbox(s)['m_TransitionConstantArray']];alltrans=anys+state+selectors
 return dict(layers=len(c['m_LayerArray']),machines=len(machines),states=len(states),any_transitions=len(anys),state_transitions=len(state),selector_transitions=len(selectors),conditions=sum(len(t['m_ConditionConstantArray']) for t in alltrans),selectors_without_interruption_field=sum('m_InterruptionSource' not in t for t in selectors))
def build():
 used={RAW/'index.json'};index=json.loads((RAW/'index.json').read_bytes())
 for p,key in [('tools/recovery/controller109.py','tool_sha256'),('tools/recovery/asset_pack_v2.py','helper_sha256')]:used.add(ROOT/p);assert sha(ROOT/p)==index[key]
 for key,schema in index['schemas'].items():assert hashlib.sha256(canonical(schema)).hexdigest()==key
 previous=ROOT/'datas/l3_animator_programs.json.gz';used.add(previous);old=json.loads(gzip.decompress(previous.read_bytes()))['controllers'];oldby={identity(c['identity']):c for c in old};assert len(oldby)==232
 results=[];decoded={};coverage={}
 for chunk in index['chunks']:
  path=RAW/chunk['path'];used.add(path);assert sha(path)==chunk['sha256'];rows=json.loads(gzip.decompress(path.read_bytes()));assert len(rows)==chunk['rows']
  for row in rows:
   key=identity(row);assert key not in decoded;data=bytes.fromhex(row['hex']);assert hashlib.sha256(data).hexdigest()==row['raw_sha256'];assert len(data)==row['object_byte_size'] and row['object_byte_start']%4==0
   reader=Reader(data,row['endian']);actual=reader.decode(index['schemas'][row['schema_sha256']]);assert actual==row['unitypy_tree'],('binary decode mismatch',key)
   decoded[key]=actual;h=hashlib.sha256(canonical(actual)).hexdigest();counts=census(actual)
   spans={s['field']:[s['start'],s['end']] for s in reader.root_spans};controller_span=spans['m_Controller'];entry=dict(serialized_file=key[0],path_id=key[1],name=actual['m_Name'],raw_sha256=row['raw_sha256'],schema_sha256=row['schema_sha256'],schema_source=row['schema_source'],byte_size=len(data),consumed_bytes=reader.pos,decoded_tree_sha256=h,unitypy_tree_sha256=hashlib.sha256(canonical(row['unitypy_tree'])).hexdigest(),root_spans=spans,padding=reader.padding,declared_ControllerSize_literal=actual['m_ControllerSize'],controller_disk_span_bytes=controller_span[1]-controller_span[0],counts=counts,previous_program_subset=key in oldby)
   results.append(entry)
   for k,v in counts.items():coverage[k]=coverage.get(k,0)+v
 assert len(decoded)==index['object_count']==308
 # Compare old normalized program input bytes/identity AND its original full raw
 # tree, not merely count tokens. Read exact original row location/hash.
 joined=[]
 for key,controller in oldby.items():
  assert key in decoded;loc=controller['raw_location'];path=ROOT/loc['path'];used.add(path);lines=gzip.decompress(path.read_bytes()).splitlines();r=json.loads(lines[loc['row']]);assert identity(r)==key and r['raw_object_sha256']==controller['raw_object_sha256'];assert r['tree']==decoded[key]
  fresh=next(r for r in results if identity(r)==key);assert fresh['raw_sha256']==r['raw_object_sha256'];joined.append(dict(serialized_file=key[0],path_id=key[1],counts=census(decoded[key]),raw_sha256=fresh['raw_sha256']))
 subset={k:sum(r['counts'][k] for r in joined) for k in coverage}
 for p in ['tools/verify/controller109.py','tools/verify/controller109_binary.py']:used.add(ROOT/p)
 return dict(schema='windwings.controller109.v1',provisional=True,provenance='arena/ef6b75ef',scope='Independent stdlib object-payload decoder, shared UnityPy builtin type schema and serialized-file framing; NOT independent schema discovery/bundle reader/engine interpolation/Unity runtime/render',xapk_sha256=index['xapk_sha256'],results=results,all_controller_counts=coverage,previous232_counts=subset,previous232_joins=joined,comparisons=dict(full_trees_equal=308,old_raw_trees_equal=232,mismatches=0,field_presence_preserved=True),limits=['UnityPy extracts object slices and provides builtin version schema plus comparison baseline; framing/schema bugs are common-mode, not independently detected.','Full raw-tree equality is independent binary read arithmetic, NOT engine semantics of serialized fields or runtime state transitions.','ControllerSize is retained literally, not treated as on-disk controller span length.','Shared previous decoded input rows are compared after independent read; this is not just re-running prior generator.'],inputs={str(p.relative_to(ROOT)):sha(p) for p in sorted(used)})
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();r=build();data=gzip.compress(canonical(r),mtime=0)
 if a.check:assert OUT.read_bytes()==data,'controller109 artifact drift'
 else:OUT.write_bytes(data)
 print('controller109:308 fresh payload decodes /232 old graph joins /0 full-tree mismatch PASS')
if __name__=='__main__':main()
