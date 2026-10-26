"""Recover independently named UnityFS directory and decode blocks without UnityPy."""
import argparse,gzip,json,sys
from pathlib import Path
from asset_pack_v2 import XAPK_SHA,DATA_SHA,extract_payload,sha
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tools.verify.unityfs111_binary import framing,block_bytes
from tools.verify.serialized110_binary import parse

def canonical(r):return (json.dumps(r,sort_keys=True,separators=(',',':'))+'\n').encode()
def recover(xapk,work):
    inputs=extract_payload(xapk,work/'input');blob=(work/'input/data.unity3d').read_bytes();assert sha(blob)==DATA_SHA
    frame=framing(blob); idx=json.loads((ROOT/'reverse-engineering/raw/controller110/index.json').read_bytes());out=ROOT/'reverse-engineering/raw/controller111';out.mkdir(parents=True,exist_ok=True)
    # Preserve framing bytes (not complete assets/media), plus three wholly-metadata block samples.
    envelope=dict(header_hex=blob[:frame['data_start']].hex(),tail_info_hex=blob[frame['info_start']:frame['info_start']+frame['info_size']].hex() if frame['flags']&128 else '',frame=frame)
    files=[];samples=[];wanted={}
    for f in idx['files']:
        name=f['serialized_file'];prefix=b''.join(bytes.fromhex(json.loads(gzip.decompress((ROOT/'reverse-engineering/raw/controller110'/c['path']).read_bytes()))['hex']) for c in f['prefix_chunks']);node=next(n for n in frame['nodes'] if 'data.unity3d/'+n['path']==name);assert node['size']==f['header']['file_size'];p=parse(prefix)
        ranges=[dict(kind='metadata_prefix',offset=0,size=len(prefix),sha256=sha(prefix))]+[dict(kind='controller',path_id=r['path_id'],offset=r['byte_start'],size=r['byte_size'],sha256=r['raw_sha256']) for r in f['independently_selected_controller_slices']]
        for r in ranges:
            r['logical_start']=node['offset']+r['offset'];r['parts']=[]
            for b in frame['blocks']:
                if r['logical_start']<b['uncompressed_start']+b['uncompressed_size'] and b['uncompressed_start']<r['logical_start']+r['size']:wanted[b['index']]=b
        files.append(dict(serialized_file=name,node=node,ranges=ranges,object_count=len(p['objects'])))
    receipts=[]
    # Decode once per selected block; never materialize whole decompressed media payload.
    for i,b in sorted(wanted.items()):
        data=block_bytes(blob,b);packed=blob[b['physical_start']:b['physical_start']+b['compressed_size']];receipts.append(dict(**b,compressed_sha256=sha(packed),decoded_sha256=sha(data)))
        for f in files:
            for r in f['ranges']:
                lo=max(r['logical_start'],b['uncompressed_start']);hi=min(r['logical_start']+r['size'],b['uncompressed_start']+len(data))
                if lo<hi:r['parts'].append(data[lo-b['uncompressed_start']:hi-b['uncompressed_start']])
            if len(samples)<3 and f['ranges'][0]['logical_start']<=b['uncompressed_start'] and b['uncompressed_start']+len(data)<=f['ranges'][0]['logical_start']+f['ranges'][0]['size']:
                samples.append(dict(block_index=i,compressed_hex=packed.hex()))
    for f in files:
        for r in f['ranges']:
            data=b''.join(r.pop('parts'));assert len(data)==r['size'] and sha(data)==r['sha256'];r['fresh_independent_sha256']=sha(data)
    raw=dict(provisional=True,xapk_sha256=XAPK_SHA,data_sha256=DATA_SHA,inputs=inputs,envelope=envelope,files=files,block_receipts=receipts,samples=samples,source_pins={p:sha((ROOT/p).read_bytes()) for p in ['tools/recovery/controller111.py','tools/verify/unityfs111_binary.py','tools/verify/serialized110_binary.py','tools/recovery/asset_pack_v2.py','reverse-engineering/raw/controller110/index.json']},limits=['Separately implemented format reader; UnityPy format/compression layout source consulted, not clean-room.','No UnityPy import or codec used here; stdlib ZIP plus own LZ4. Only needed blocks decoded, not all media blocks.','Three original compressed samples wholly inside metadata prefixes; no whole media nodes saved.','Controller payload schema still UnityPy builtin DB via109; no runtime/render proof.'])
    (out/'evidence.json.gz').write_bytes(gzip.compress(canonical(raw),mtime=0));print('UnityFS111',len(frame['nodes']),'nodes',len(receipts),'blocks',sum(len(f['ranges'])-1 for f in files),'controllers verified',flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args()
    try:recover(a.xapk,a.work)
    except Exception:
        import traceback
        print('::error::'+traceback.format_exc().replace('%','%25').replace('\n','%0A'),flush=True);raise
