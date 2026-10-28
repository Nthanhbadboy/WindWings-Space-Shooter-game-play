"""Replay preserved UnityFS envelope and metadata codec samples, audit recovery receipts."""
import gzip,hashlib,json
from pathlib import Path
from tools.verify.unityfs111_binary import framing,decode
ROOT=Path(__file__).resolve().parents[2];RAW=ROOT/'reverse-engineering/raw/controller111/evidence.json.gz';OUT=ROOT/'datas/l3_ef6b75ef111_unityfs_framing.json.gz'
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
class Envelope:
    """Only preserved header/info bytes, NOT a fabricated full bundle or decoded payload."""
    def __init__(self,envelope):
        self.header=bytes.fromhex(envelope['header_hex']);self.tail=bytes.fromhex(envelope['tail_info_hex']);self.size=envelope['frame']['size'];self.tail_start=envelope['frame']['info_start']
    def __len__(self):return self.size
    def find(self,needle,start):return self.header.find(needle,start)
    def __getitem__(self,key):
        assert isinstance(key,slice) and key.step is None
        a=key.start or 0;b=self.size if key.stop is None else key.stop
        if 0<=a<=b<=len(self.header):return self.header[a:b]
        if self.tail and self.tail_start<=a<=b<=self.tail_start+len(self.tail):return self.tail[a-self.tail_start:b-self.tail_start]
        raise ValueError('payload bytes not captured in framing envelope')
def build():
    used={RAW,Path(__file__),ROOT/'tools/verify/unityfs111_binary.py',ROOT/'.github/workflows/recover-controller111.yml'};r=json.loads(gzip.decompress(RAW.read_bytes()))
    for p,h in r['source_pins'].items():
        p=ROOT/p;used.add(p);assert sha(p.read_bytes())==h
    frame=framing(Envelope(r['envelope']));assert frame==r['envelope']['frame'];blocks={b['index']:b for b in frame['blocks']};receipts={b['index']:b for b in r['block_receipts']};assert len(receipts)==len(r['block_receipts'])
    previous=ROOT/'reverse-engineering/raw/controller110/index.json';old=json.loads(previous.read_bytes());oldfiles={f['serialized_file']:f for f in old['files']};selected=set();controllers=0;samples=[]
    for f in r['files']:
        node=next(n for n in frame['nodes'] if 'data.unity3d/'+n['path']==f['serialized_file']);assert node==f['node'];baseline=oldfiles[f['serialized_file']];assert node['size']==baseline['header']['file_size']
        ranges=f['ranges'];assert len([x for x in ranges if x['kind']=='metadata_prefix'])==1
        byid={c['path_id']:c for c in baseline['independently_selected_controller_slices']}
        assert len(ranges)==1+len(byid)
        for v in ranges:
            assert v['fresh_independent_sha256']==v['sha256'];assert v['logical_start']==node['offset']+v['offset'];assert 0<=v['offset']<=v['offset']+v['size']<=node['size']
            if v['kind']=='metadata_prefix':assert v['offset']==0 and v['size']==baseline['header']['data_offset'] and v['sha256']==baseline['prefix_sha256']
            else:
                assert v['kind']=='controller';c=byid.pop(v['path_id']);assert (v['offset'],v['size'],v['sha256'])==(c['byte_start'],c['byte_size'],c['raw_sha256']);controllers+=1
            for b in frame['blocks']:
                if v['logical_start']<b['uncompressed_start']+b['uncompressed_size'] and b['uncompressed_start']<v['logical_start']+v['size']:selected.add(b['index'])
        assert not byid
    assert selected==set(receipts)
    for i,b in receipts.items():assert all(b[k]==v for k,v in blocks[i].items())
    for s in r['samples']:
        b=receipts[s['block_index']];packed=bytes.fromhex(s['compressed_hex']);assert len(packed)==b['compressed_size'] and sha(packed)==b['compressed_sha256'];decoded=decode(packed,b['flags'],b['uncompressed_size']);assert sha(decoded)==b['decoded_sha256']
        # Prove the whole sample lies within an original metadata prefix, no media node sample.
        matched=False
        for f in r['files']:
            v=f['ranges'][0];start=b['uncompressed_start']-v['logical_start']
            if 0<=start and start+len(decoded)<=v['size']:
                chunks=oldfiles[f['serialized_file']]['prefix_chunks'];parts=[]
                for c in chunks:
                    p=ROOT/'reverse-engineering/raw/controller110'/c['path'];used.add(p);assert sha(p.read_bytes())==c['sha256'];parts.append(bytes.fromhex(json.loads(gzip.decompress(p.read_bytes()))['hex']))
                assert b''.join(parts)[start:start+len(decoded)]==decoded;matched=True
        assert matched;samples.append(dict(block_index=s['block_index'],decoded_bytes=len(decoded),decoded_sha256=sha(decoded)))
    assert len(samples)==3 and controllers==308 and len(r['files'])==2
    return dict(schema='windwings.unityfs111.v1',provisional=True,provenance='arena/ef6b75ef',xapk_sha256=r['xapk_sha256'],data_sha256=r['data_sha256'],frame=frame,selected_block_receipts=r['block_receipts'],metadata_sample_replays=samples,files=r['files'],controller_count=controllers,limits=r['limits']+['Local replay covers framing and three compressed metadata blocks. Fresh full-prefix/controller decode receipts require pinned original APK via recovery CI; unpreserved blocks cannot be redecoded locally without source.','Bundle hash field is preserved literal, not a validated checksum.'],inputs={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted(used)})
def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();r=build();b=gzip.compress(canonical(r),mtime=0)
    if a.check:assert OUT.read_bytes()==b,'artifact drift'
    else:OUT.write_bytes(b)
    print('controller111:',len(r['frame']['nodes']),'nodes /',len(r['selected_block_receipts']),'decoded source blocks /',r['controller_count'],'fresh controller slices PASS')
if __name__=='__main__':main()
