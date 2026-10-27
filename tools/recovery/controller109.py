"""Recover original controller object bytes + shared schema + UnityPy baseline.
Schema/framing by UnityPy is NOT an independent serialized-file/schema parser.
"""
import argparse,gzip,hashlib,json
from pathlib import Path
from asset_pack_v2 import XAPK_SHA,extract_payload,serialized_files,sha
ROOT=Path(__file__).resolve().parents[2]
def canonical(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def plain(x):
 if isinstance(x,dict):return {k:plain(v) for k,v in x.items()}
 if isinstance(x,(tuple,list,bytes,bytearray)):return [plain(v) for v in x]
 return x

def recover(xapk,work):
 import UnityPy
 assert sha(xapk.read_bytes())==XAPK_SHA
 inputs=extract_payload(xapk,work/'input');env=UnityPy.load(*(str(p) for p in sorted((work/'input').iterdir())))
 def schema(n):return dict(type=n.m_Type,name=n.m_Name,byte_size=n.m_ByteSize,meta_flag=n.m_MetaFlag or 0,children=[schema(c) for c in n.m_Children])
 out=ROOT/'reverse-engineering/raw/controller109';out.mkdir(parents=True,exist_ok=True);schemas={};rows=[]
 for f,sf in serialized_files(env):
  for obj in sorted(sf.objects.values(),key=lambda o:o.path_id):
   if obj.type.name!='AnimatorController':continue
   node=obj._get_typetree_node();s=schema(node);sid=sha(canonical(s));schemas[sid]=s;raw=obj.get_raw_data()
   rows.append(dict(serialized_file=f,path_id=int(obj.path_id),class_id=int(obj.type),endian=obj.reader.endian,schema_sha256=sid,schema_source='serialized_type.node' if obj.serialized_type and obj.serialized_type.node else 'UnityPy builtin type database',object_byte_start=obj.byte_start,object_byte_size=obj.byte_size,raw_sha256=sha(raw),hex=raw.hex(),unitypy_tree=plain(obj.read_typetree())))
 assert rows,'no recovered controllers'
 chunks=[]
 for first in range(0,len(rows),32):
  part=rows[first:first+32];name=f'objects-{first//32:04}.json.gz';bb=gzip.compress(canonical(part),mtime=0);assert len(bb)<5*1024*1024;(out/name).write_bytes(bb);chunks.append(dict(path=name,rows=len(part),sha256=sha(bb)))
 index=dict(provisional=True,provenance='arena/ef6b75ef',xapk_sha256=XAPK_SHA,tool_sha256=sha(Path(__file__).read_bytes()),helper_sha256=sha((ROOT/'tools/recovery/asset_pack_v2.py').read_bytes()),unitypy_version=UnityPy.__version__,inputs=inputs,schemas=schemas,chunks=chunks,object_count=len(rows),scope='Original object slices from pinned APK. UnityPy frames objects, supplies schema and comparison baseline. Separate reader must not call UnityPy decode. NOT independent schema discovery/runtime engine.')
 (out/'index.json').write_bytes(canonical(index));print(len(rows),'controller raw objects;',len(schemas),'schemas;',len(chunks),'chunks',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args()
 try:recover(a.xapk,a.work)
 except Exception:
  import traceback
  print('::error::'+traceback.format_exc().replace('%','%25').replace('\n','%0A'),flush=True);raise
