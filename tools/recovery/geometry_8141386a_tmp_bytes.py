"""Read-only original TMP byte corroboration; no pixels/APK modifications/runtime.
provenance: arena/8141386a-windwings-space-shooter-game-p
Framing uses acknowledged shared ef111/110 readers. Table layout seeded from capture.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tools.verify.serialized110_binary import header,parse
from tools.verify.unityfs111_binary import framing,block_bytes
from tools.verify.l3_geometry_8141386a_tmp_binary import exact_table_witness

RAW=ROOT/'reverse-engineering/raw/geometry-8141386a/tmp'
XAPK='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
DATA='7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7'
BRANCH='arena/8141386a-windwings-space-shooter-game-p'


def sha(b):return hashlib.sha256(b).hexdigest()


def recover(path):
    if sha(path.read_bytes())!=XAPK:raise ValueError('XAPK source mismatch')
    bundles=[]
    with zipfile.ZipFile(path) as outer:
        for member in sorted(outer.namelist()):
            if not member.endswith('.apk'):continue
            apk=outer.read(member)
            with zipfile.ZipFile(io.BytesIO(apk)) as inner:
                p='assets/bin/Data/data.unity3d'
                if p in inner.namelist():bundles.append((member,sha(apk),inner.read(p)))
    if len(bundles)!=1 or sha(bundles[0][2])!=DATA:raise ValueError('bundle source mismatch')
    apk_name,apk_sha,blob=bundles[0];frame=framing(blob);cache={};blocks={}
    def read(offset,size):
        if not 0<=offset<=offset+size<=frame['uncompressed_size']:raise ValueError('bad logical range')
        out=[]
        for b in frame['blocks']:
            start=b['uncompressed_start']
            if offset<start+b['uncompressed_size'] and start<offset+size:
                if b['index'] not in cache:
                    packed=blob[b['physical_start']:b['physical_start']+b['compressed_size']]
                    cache[b['index']]=block_bytes(blob,b)
                    blocks[b['index']]=dict(**b,compressed_sha256=sha(packed),decoded_sha256=sha(cache[b['index']]))
                decoded=cache[b['index']]
                out.append(decoded[max(0,offset-start):min(len(decoded),offset+size-start)])
        value=b''.join(out)
        if len(value)!=size:raise ValueError('logical range consumption mismatch')
        return value
    query_path=RAW/'byte-queries.json.gz';query=json.loads(gzip.decompress(query_path.read_bytes()))
    if query['provenance']!=BRANCH or query['xapk_sha256']!=XAPK:raise ValueError('query source/provenance mismatch')
    by_file=defaultdict(list)
    for q in query['objects']:by_file[q['identity']['serialized_file']].append(q)
    files=[];objects=[]
    for file,queries in sorted(by_file.items()):
        node=next(n for n in frame['nodes'] if 'data.unity3d/'+n['path']==file)
        h=header(read(node['offset'],48));prefix=read(node['offset'],h['data_offset']);table=parse(prefix)
        if h['file_size']!=node['size'] or h['endian']!='<':raise ValueError('unsupported serialized source')
        wanted={q['identity']['path_id'] for q in queries};entries={e['path_id']:e for e in table['objects'] if e['path_id'] in wanted}
        files.append(dict(serialized_file=file,node=node,header=h,metadata_prefix_sha256=sha(prefix),object_count=len(table['objects'])))
        del table
        for q in queries:
            e=entries[q['identity']['path_id']]
            if e['class_id']!=q['class_id']:raise ValueError('class mismatch')
            value=read(node['offset']+e['byte_start'],e['byte_size'])
            if sha(value)!=q['expected_object_sha256']:raise ValueError('fresh object differs from raw102')
            result=dict(identity=q['identity'],role=q['role'],object_table_entry=e,object_sha256=sha(value),fresh_sha_matches_capture=True)
            if q['role']=='font':
                result['tables']={name:dict(**exact_table_witness(value,bytes.fromhex(expected)),sha256=sha(bytes.fromhex(expected))) for name,expected in q['tables'].items()}
            objects.append(result)
        print(file,len(queries),'objects corroborated',flush=True)
    pin_paths=['tools/recovery/geometry_8141386a_tmp_bytes.py','tools/verify/l3_geometry_8141386a_tmp_binary.py',
               'tools/verify/serialized110_binary.py','tools/verify/unityfs111_binary.py',str(query_path.relative_to(ROOT))]
    v=dict(schema=1,item=4,provenance=BRANCH,xapk_sha256=XAPK,bundle_sha256=DATA,apk_member=apk_name,apk_sha256=apk_sha,
           files=files,objects=objects,block_receipts=[blocks[i] for i in sorted(blocks)],tool_pins={p:sha((ROOT/p).read_bytes()) for p in pin_paths},
           scope='Fresh whole object hashes; complete unique count-prefixed glyph/character byte tables. NOT native layout, independent schema discovery, mesh readback or render.')
    body=(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    (RAW/'byte-witness.json.gz').write_bytes(gzip.compress(body,mtime=0))
    print(len(objects),'fresh whole-object SHA matches; 7 complete glyph/character table byte spans preserved',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--xapk',type=Path,required=True);a=p.parse_args();recover(a.xapk)
