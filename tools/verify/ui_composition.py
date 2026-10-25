"""Serialized layout-frame TRS/activity and scoped font/material references.
Not Unity layout, runtime activation, shader execution, or a render approval.
"""
import csv,gzip,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
from tools.verify.ui_reference_links import resolve
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'datas/ui_composition.json.gz'
IDENTITY=[1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.]
def sequential_sum(values):
    # Python3.12 changed built-in float sum; pin left-to-right arithmetic.
    total=0.0
    for value in values:total=total+value
    return total
def multiply(a,b):return [sequential_sum(a[i*4+k]*b[k*4+j] for k in range(4)) for i in range(4) for j in range(4)]
def trs(node):
    p,q,s=(node.get(k) for k in ('local_pos','rotation','scale'))
    if p is None or q is None or s is None:return None
    if len(p)!=3 or len(q)!=4 or len(s)!=3 or not all(math.isfinite(v) for seq in (p,q,s) for v in seq):return None
    x,y,z,w=q
    if abs(sequential_sum(v*v for v in q)-1.)>.001:return None
    # Standard row-major T*R*S, raw near-unit quaternion components; float64.
    return [(1-2*y*y-2*z*z)*s[0],(2*x*y-2*z*w)*s[1],(2*x*z+2*y*w)*s[2],p[0],(2*x*y+2*z*w)*s[0],(1-2*x*x-2*z*z)*s[1],(2*y*z-2*x*w)*s[2],p[1],(2*x*z-2*y*w)*s[0],(2*y*z+2*x*w)*s[1],(1-2*x*x-2*y*y)*s[2],p[2],0.,0.,0.,1.]
def conjunction(a,b):return False if a is False or b is False else True if a is True and b is True else None
def hierarchy(nodes):
    paths=defaultdict(list)
    for i,n in enumerate(nodes):paths[n.get('path')].append(i)
    result={}
    for i in sorted(range(len(nodes)),key=lambda i:(nodes[i].get('depth',-1),i)):
        n=nodes[i];depth=n.get('depth');flag=n.get('active');flag=bool(flag) if flag in (0,1) else None
        if depth==0:
            result[i]=dict(parent=None,parent_status='layout_root',activity_within_root=flag,layout_frame_matrix=list(IDENTITY));continue
        path=n.get('path','');suffix='/'+n.get('name','');parent_path=path[:-len(suffix)] if path.endswith(suffix) else None;candidates=[j for j in paths.get(parent_path,[]) if nodes[j].get('depth')==depth-1] if isinstance(depth,int) else []
        parent=candidates[0] if len(candidates)==1 else None
        p=result.get(parent);local=trs(n);matrix=multiply(p['layout_frame_matrix'],local) if p and p['layout_frame_matrix'] is not None and local is not None else None
        result[i]=dict(parent=parent,parent_status='unique_path_parent' if parent is not None else 'ambiguous_parent' if len(candidates)>1 else 'missing_parent',activity_within_root=conjunction(flag,p['activity_within_root'] if p else None),layout_frame_matrix=matrix)
    return result

def build():
    ui=ROOT/'reverse-engineering/raw/ui';index=ui/'_index.csv';assets={};evidence={};cache={}
    for kind in ('Material','TMP_FontAsset'):
        p=ui/'render-context'/f'{kind}.jsonl.gz';b=p.read_bytes();assets[kind]=[json.loads(l) for l in gzip.decompress(b).splitlines()];evidence[str(p.relative_to(ROOT))]=hashlib.sha256(b).hexdigest()
    def binding(owner,kind,ref):
        key=json.dumps([owner.get('serialized_file'),owner.get('externals',[]),kind,ref],sort_keys=True)
        if key not in cache:cache[key]=resolve(owner,ref,assets[kind])
        return cache[key]
    sources=[];records=[];totals=Counter();parents=Counter();references=Counter()
    for entry in csv.DictReader(index.read_text().splitlines()):
        p=ui/entry['file'];b=p.read_bytes();d=json.loads(gzip.decompress(b));nodes=d['nodes'];g=hierarchy(nodes);source=len(sources)
        sources.append(dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),screen=d['class'],nodes=len(nodes),walk_diagnostics=d.get('walk_diagnostics'),root_local_transform={k:nodes[0].get(k) for k in ('local_pos','rotation','scale')} if nodes else {}))
        for ni,n in enumerate(nodes):
            parents[g[ni]['parent_status']]+=1
            for ci,c in enumerate(n.get('components',[])):
                if c.get('class') not in ('SpriteRenderer','SpriteMask','Image','TextMeshPro','TextMeshProUGUI','ParticleSystemRenderer','Camera'):continue
                props=c.get('visual_properties',{});links=[]
                for field,kind in [('m_fontAsset','TMP_FontAsset'),('m_sharedMaterial','Material')]:
                    if field in props:links.append(dict(field=field,result=binding(d,kind,props[field])))
                for j,ref in enumerate(props.get('m_Materials',[])):links.append(dict(field=f'm_Materials[{j}]',result=binding(d,'Material',ref)))
                for l in links:references[l['field'].split('[')[0]+':'+l['result']['status']]+=1
                totals['components']+=1;totals['matrix_derived' if g[ni]['layout_frame_matrix'] is not None else 'matrix_unknown']+=1;totals['activity_'+str(g[ni]['activity_within_root'])]+=1
                records.append(dict(source=source,node_index=ni,component_index=ci,path=n.get('path'),component=c['class'],**g[ni],renderer_enabled=props.get('m_Enabled'),rect_layout_pending=any(x.get('class')=='RectTransform' for x in n.get('components',[])),properties=props,references=links))
    for p in (index,Path(__file__),ROOT/'tools/verify/ui_reference_links.py'):evidence[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    return dict(schema=1,provisional=True,scope='797 indexed layouts. Parent reconstruction is unique path+depth, not Transform PPtr proof. Matrices float64 in layout-root frame, ROOT LOCAL TRS EXCLUDED; no anchored/Canvas/driver layout or Unity rounding. Activity is serialized within-root only. Missing enabled flags remain unknown. No sort order execution or runtime visibility claims.',totals=dict(totals),parent_status=dict(parents),references=dict(references),sources=sources,evidence=evidence,records=records)
def write(d):
    directory=ROOT/'datas/ui-composition';directory.mkdir(exist_ok=True);records=d.pop('records');chunks=[]
    for start in range(0,len(records),18000):
        p=directory/f'{start//18000:03d}.json.gz';b=gzip.compress(json.dumps(records[start:start+18000],ensure_ascii=False,separators=(',',':')).encode(),mtime=0);assert len(b)<5_000_000;p.write_bytes(b);chunks.append(dict(path=str(p.relative_to(ROOT)),rows=len(records[start:start+18000]),sha256=hashlib.sha256(b).hexdigest()))
    d['chunks']=chunks;OUT.write_bytes(gzip.compress(json.dumps(d,ensure_ascii=False,separators=(',',':')).encode(),mtime=0));assert OUT.stat().st_size<5_000_000
    return d
if __name__=='__main__':
    d=write(build());print(json.dumps({k:d[k] for k in ('totals','parent_status','references','chunks')},indent=2))
