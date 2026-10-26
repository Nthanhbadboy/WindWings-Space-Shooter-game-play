"""Capture original SerializedFile metadata prefix, independently choose controller slices."""
import argparse,gzip,hashlib,json,sys
from pathlib import Path
from asset_pack_v2 import XAPK_SHA,extract_payload,serialized_files,sha
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tools.verify.serialized110_binary import header,parse

def canonical(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def table_digest(rows):return sha(canonical(sorted([{k:r[k] for k in ['path_id','type_id','class_id','byte_start','byte_size']} for r in rows],key=lambda r:r['path_id'])))
def recover(xapk,work):
 import UnityPy
 assert sha(xapk.read_bytes())==XAPK_SHA;inputs=extract_payload(xapk,work/'input');env=UnityPy.load(*(str(p) for p in sorted((work/'input').iterdir())))
 olddir=ROOT/'reverse-engineering/raw/controller109';oldidx=json.loads((olddir/'index.json').read_bytes());old={(r['serialized_file'],r['path_id']):r for ch in oldidx['chunks'] for r in json.loads(gzip.decompress((olddir/ch['path']).read_bytes()))};wanted={k[0] for k in old};out=ROOT/'reverse-engineering/raw/controller110';out.mkdir(parents=True,exist_ok=True);files=[]
 for f,sf in serialized_files(env):
  if f not in wanted:continue
  rd=sf.reader;rd.Position=0;h=header(rd.read_bytes(48));rd.Position=0;prefix=rd.read_bytes(h['data_offset']);fresh=parse(prefix);baseline=[dict(path_id=int(o.path_id),type_id=o.type_id,class_id=int(o.type),byte_start=o.byte_start,byte_size=o.byte_size) for o in sf.objects.values()]
  assert table_digest(fresh['objects'])==table_digest(baseline),'independent object-table mismatch'
  chunks=[]
  for first in range(0,len(prefix),1048576):
   name=f'{len(files):02}-prefix-{first//1048576:03}.json.gz';b=gzip.compress(canonical(dict(offset=first,hex=prefix[first:first+1048576].hex())),mtime=0);assert len(b)<5*1024*1024;(out/name).write_bytes(b);chunks.append(dict(path=name,sha256=sha(b)))
  controllers=[]
  for r in fresh['objects']:
   if r['class_id']!=91:continue
   key=(f,r['path_id']);assert key in old;rd.Position=r['byte_start'];data=rd.read_bytes(r['byte_size']);assert sha(data)==old[key]['raw_sha256'] and data.hex()==old[key]['hex'];controllers.append(dict(**r,raw_sha256=sha(data)))
  files.append(dict(serialized_file=f,header=h,prefix_sha256=sha(prefix),prefix_chunks=chunks,unitypy_object_count=len(baseline),unitypy_table_digest=table_digest(baseline),independently_selected_controller_slices=controllers))
 assert len(files)==len(wanted)==2 and sum(len(f['independently_selected_controller_slices']) for f in files)==308
 index=dict(provisional=True,provenance='arena/ef6b75ef',xapk_sha256=XAPK_SHA,tool_sha256=sha(Path(__file__).read_bytes()),parser_sha256=sha((ROOT/'tools/verify/serialized110_binary.py').read_bytes()),helper_sha256=sha((ROOT/'tools/recovery/asset_pack_v2.py').read_bytes()),previous_index_sha256=sha((olddir/'index.json').read_bytes()),inputs=inputs,files=files,scope='UnityPy bundle extraction/shared file naming remains. Metadata/object-table parsed by separate stdlib reader; original controller slices selected at independent computed offsets and compared to109. Builtin controller schema still shared.')
 (out/'index.json').write_bytes(canonical(index));print([(f['serialized_file'],f['unitypy_object_count'],len(f['independently_selected_controller_slices'])) for f in files],flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args()
 try:recover(a.xapk,a.work)
 except Exception:
  import traceback
  print('::error::'+traceback.format_exc().replace('%','%25').replace('\n','%0A'),flush=True);raise
