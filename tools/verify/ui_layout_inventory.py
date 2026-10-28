"""Audit EVERY saved layout. Structural equality never transfers scoped identity."""
import csv,gzip,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'datas/ui_layout_inventory.json.gz'
NODE_KEYS=('name','path','depth','active','anchor_min','anchor_max','anchored_pos','size_delta','pivot','scale','local_pos','rotation')
COMPONENT_KEYS=('class','sprite','text','key')
def projection(nodes):
    # Common legacy/enriched fields only. Excludes PPtrs/materials/fonts on purpose:
    # equal hashes are useful drawing-topology candidates, NOT identity proof.
    return [{**{k:n.get(k) for k in NODE_KEYS},'components':[{k:c.get(k) for k in COMPONENT_KEYS} for c in n.get('components',[])]} for n in nodes]
def fingerprint(nodes):return hashlib.sha256(json.dumps(projection(nodes),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def build():
    ui=ROOT/'reverse-engineering/raw/ui';idx_blob=(ui/'_index.csv').read_bytes();indexed={r['file'] for r in csv.DictReader(idx_blob.decode().splitlines())};files=[];groups=defaultdict(lambda:dict(files=0,indexed_files=0,example=None));totals=Counter();class_counts=defaultdict(Counter)
    for p in sorted(ui.glob('*.json.gz')):
        b=p.read_bytes();d=json.loads(gzip.decompress(b));nodes=d['nodes'];features=Counter()
        for n in nodes:
            for c in n.get('components',[]):
                props=c.get('visual_properties',{})
                if 'm_Sprite' in props:features['sprite_pptr_recorded']+=1
                elif c.get('sprite'):features['sprite_name_only']+=1
                if c.get('class') in ('TextMeshPro','TextMeshProUGUI'):
                    features['tmp_components']+=1
                    features['tmp_font_pptr_recorded']+=int('m_fontAsset' in props)
        h=fingerprint(nodes);g=groups[(d['class'],h)];g['files']+=1;g['indexed_files']+=int(p.name in indexed);g['example']=g['example'] or p.name
        scope='indexed' if p.name in indexed else 'outside_index';totals[scope+'_files']+=1;class_counts[d['class']][scope+'_files']+=1
        for k,v in features.items():totals[scope+'_'+k]+=v
        files.append(dict(file=p.name,sha256=hashlib.sha256(b).hexdigest(),screen=d['class'],root_path_id=d['root_path_id'],nodes=len(nodes),indexed=p.name in indexed,serialized_file=d.get('serialized_file'),topology_sha256=h,features=dict(features)))
    group_rows=[dict(screen=k[0],topology_sha256=k[1],**v) for k,v in sorted(groups.items())]
    totals['topology_groups']=len(group_rows);totals['outside_files_with_indexed_topology_candidate']=sum(g['files']-g['indexed_files'] for g in group_rows if g['indexed_files'])
    return dict(schema=1,provisional=True,warning='topology hashes omit material/font/PPtr/render state. Equality does NOT prove same asset, same scene, or rendered equivalence; NO inherited scoped PPtr bindings',totals=dict(totals),classes={k:dict(v) for k,v in sorted(class_counts.items())},groups=group_rows,files=files,evidence={'index_sha256':hashlib.sha256(idx_blob).hexdigest(),'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
def write(d):
    directory=ROOT/'datas/ui-layout-inventory';directory.mkdir(exist_ok=True)
    files=d.pop('files');chunks=[]
    for start in range(0,len(files),14000):
        p=directory/f"{start//14000:03d}.json.gz"
        b=gzip.compress(json.dumps(files[start:start+14000],ensure_ascii=False,separators=(',',':')).encode(),mtime=0)
        assert len(b)<5_000_000;p.write_bytes(b)
        chunks.append(dict(path=str(p.relative_to(ROOT)),rows=len(files[start:start+14000]),sha256=hashlib.sha256(b).hexdigest()))
    d['file_chunks']=chunks
    d['source_manifest_sha256']=hashlib.sha256(''.join(f"{r['file']} {r['sha256']}\n" for r in files).encode()).hexdigest()
    OUT.write_bytes(gzip.compress(json.dumps(d,ensure_ascii=False,separators=(',',':')).encode(),mtime=0));assert OUT.stat().st_size<5_000_000
    return d
if __name__=='__main__':
    d=write(build());print(json.dumps(dict(totals=d['totals'],classes=len(d['classes']),chunks=d['file_chunks'],bytes=OUT.stat().st_size),indent=2))
