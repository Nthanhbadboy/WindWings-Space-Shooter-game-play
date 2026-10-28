"""Independent SerializedFile tables -> controller framing -> clip PPtr class joins.
UnityPy remains the UnityFS bundle decompressor/file naming source and builtin schema.
"""
import gzip,hashlib,json
from pathlib import Path,PurePosixPath
from collections import Counter
from tools.verify.serialized110_binary import parse
from tools.verify.controller109_binary import Reader
ROOT=Path(__file__).resolve().parents[2];RAW=ROOT/'reverse-engineering/raw/controller110';OUT=ROOT/'datas/l3_ef6b75ef110_controller_framing.json.gz'
def canonical(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(rows):
 keys=['path_id','type_id','class_id','byte_start','byte_size']
 return hashlib.sha256(canonical(sorted([{k:r[k] for k in keys} for r in rows],key=lambda r:r['path_id']))).hexdigest()
def build():
 used=set()
 def read(p):
  used.add(p);b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
 idx=read(RAW/'index.json')
 for p,k in [('tools/recovery/controller110.py','tool_sha256'),('tools/verify/serialized110_binary.py','parser_sha256'),('tools/recovery/asset_pack_v2.py','helper_sha256')]:used.add(ROOT/p);assert sha(ROOT/p)==idx[k]
 oldroot=ROOT/'reverse-engineering/raw/controller109';oldidx=read(oldroot/'index.json');assert sha(oldroot/'index.json')==idx['previous_index_sha256'];old={}
 for ch in oldidx['chunks']:
  p=oldroot/ch['path'];rows=read(p);assert sha(p)==ch['sha256']
  for r in rows:old[r['serialized_file'],r['path_id']]=r
 parsed={};byid={};summaries=[]
 for f in idx['files']:
  fragments=[];offset=0
  for chunk in f['prefix_chunks']:
   p=RAW/chunk['path'];r=read(p);assert sha(p)==chunk['sha256'] and r['offset']==offset;bb=bytes.fromhex(r['hex']);fragments.append(bb);offset+=len(bb)
  prefix=b''.join(fragments);assert hashlib.sha256(prefix).hexdigest()==f['prefix_sha256'];m=parse(prefix);name=f['serialized_file'];parsed[name]=m;byid[name]={r['path_id']:r for r in m['objects']};assert len(byid[name])==f['unitypy_object_count'];d=digest(m['objects']);assert d==f['unitypy_table_digest']
  # Non-empty object intervals must not alias or overlap.
  intervals=sorted((r['byte_start'],r['byte_start']+r['byte_size']) for r in m['objects'] if r['byte_size']);assert all(a[1]<=b[0] for a,b in zip(intervals,intervals[1:]))
  fresh=[r for r in m['objects'] if r['class_id']==91];recorded={r['path_id']:r for r in f['independently_selected_controller_slices']};assert len(recorded)==len(fresh)
  for r in fresh:
   for k in r:assert r[k]==recorded[r['path_id']][k]
   previous=old[name,r['path_id']];assert r['byte_start']==previous['object_byte_start'] and r['byte_size']==previous['object_byte_size'];assert hashlib.sha256(bytes.fromhex(previous['hex'])).hexdigest()==recorded[r['path_id']]['raw_sha256']
  summaries.append(dict(serialized_file=name,header=m['header'],unity_version=m['unity_version'],target_platform=m['target_platform'],object_count=len(m['objects']),table_digest=d,unitypy_digest_equal=True,class_histogram=dict(Counter(str(o['class_id']) for o in m['objects'])),types=m['types'],script_count=len(m['scripts']),externals=m['externals'],ref_type_count=len(m['ref_types']),metadata_end=m['metadata_end'],padding_hex=m['prefix_padding_hex'],controllers=f['independently_selected_controller_slices']))
 refs=[]
 for (source,pid),r in sorted(old.items()):
  framed=byid[source][pid];assert framed['class_id']==91
  tree=Reader(bytes.fromhex(r['hex']),r['endian']).decode(oldidx['schemas'][r['schema_sha256']]);assert tree==r['unitypy_tree']
  for index,ptr in enumerate(tree['m_AnimationClips']):
   fid=ptr['m_FileID'];target_id=ptr['m_PathID'];entry=dict(controller=dict(serialized_file=source,path_id=pid),clip_index=index,pointer=ptr)
   if target_id==0:entry['status']='null'
   else:
    if fid==0:target_file=source
    else:
     assert 0<fid<=len(parsed[source]['externals']);external=parsed[source]['externals'][fid-1];p=PurePosixPath(external['path']);assert not p.is_absolute() and '..' not in p.parts,'unsupported external naming';target_file=str(PurePosixPath(source).parent/p);entry['external']=external
    assert target_file in byid and target_id in byid[target_file],'clip outside captured metadata';target=byid[target_file][target_id];assert target['class_id']==74
    entry.update(status='resolved_class74_from_independent_table',target=dict(serialized_file=target_file,path_id=target_id),target_byte_start=target['byte_start'],target_byte_size=target['byte_size'])
   refs.append(entry)
 for p in ['tools/verify/controller110.py','tools/verify/controller109_binary.py']:used.add(ROOT/p)
 return dict(schema='windwings.controller110.v1',provisional=True,provenance='arena/ef6b75ef',scope='Independent v22 stripped metadata/object-table parsing and controller framing; independent payload reader109 reused. UnityFS bundle decompression/file naming and builtin controller type schema remain shared, NOT full clean-room APK parser/schema discovery/runtime/render.',xapk_sha256=idx['xapk_sha256'],files=summaries,controller_count=sum(len(f['controllers']) for f in summaries),clip_references=refs,independent_table_objects=sum(f['object_count'] for f in summaries),common_mode_limits=['UnityPy performs APK/UnityFS extraction and supplies file naming; bundle block framing/decompression not independently reimplemented.','Builtin controller payload schema is still UnityPy version DB, not independently discovered.','Format layouts were consulted in UnityPy source; this is separately implemented parsing, not clean-room derivation.','Object-table class/range joins are source identity, not actual clip evaluation/state reachability or runtime engine behavior.'],inputs={str(p.relative_to(ROOT)):sha(p) for p in sorted(used)})
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();r=build();b=gzip.compress(canonical(r),mtime=0)
 if a.check:assert OUT.read_bytes()==b,'110 artifact drift'
 else:OUT.write_bytes(b)
 print('controller110:',r['independent_table_objects'],'independent object records /',r['controller_count'],'controller frames /',len(r['clip_references']),'clip PPtr joins PASS')
if __name__=='__main__':main()
