"""File-qualified typed hierarchy. No name-based parent reconstruction."""
import gzip,hashlib,json,sys
from collections import defaultdict,deque
from pathlib import Path
from tools.verify.ui_composition import trs,multiply,IDENTITY,conjunction
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'reverse-engineering/raw/l3-chain'
def key(r):return (sys.intern(r['serialized_file']),r['path_id'])
def identity(k):return dict(serialized_file=k[0],path_id=k[1]) if k else None
def read_chunks(index,field):
    for c in index[field]:
        b=(RAW/c['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==c['sha256'];lines=gzip.decompress(b).splitlines();assert len(lines)==c['rows']
        for line in lines:yield json.loads(line)
def bool_flag(value):return bool(value) if value in (0,1) else None
class Graph:
    def __init__(self,rows,links):
        self.rows={key(r):r for r in rows};self.edges={};self.components=defaultdict(list);self.children=defaultdict(list);self.refs=defaultdict(list);self.edge_status=defaultdict(int)
        for l in links:
            owner=key(l['owner']);loc=l['location'];self.edge_status[l['status']]+=1
            if l['status']!='resolved':continue
            target=key(l['target']);edge=(owner,loc)
            if edge in self.edges:assert self.edges[edge]==target,'conflicting exact edge'
            self.edges[edge]=target;self.refs[owner].append((loc,target,l['target']['type']))
            if self.rows[owner]['type']=='GameObject' and loc.startswith('.m_Component['):self.components[owner].append(target)
            if self.rows[owner]['type'] in ('Transform','RectTransform') and loc.startswith('.m_Children['):self.children[owner].append(target)
        self.go_transform={};self.transform_errors=[]
        for go,comps in self.components.items():
            choices=[c for c in comps if self.rows.get(c,{}).get('type') in ('Transform','RectTransform')]
            if len(choices)==1:self.go_transform[go]=choices[0]
            else:self.transform_errors.append(dict(gameobject=identity(go),transforms=len(choices)))
    def target(self,k,field):return self.edges.get((k,field))
    def tree(self,k):
        r=self.rows[k];t=dict(r.get('tree',{}))
        if r['type']=='MonoBehaviour':t.update(r.get('header',{}))
        return t
    def descendants(self,root):
        first=self.go_transform.get(root)
        if first is None:return [],[dict(kind='root_transform_missing',gameobject=identity(root))]
        queue=deque([(first,None,'',list(IDENTITY),True)]);seen=set();nodes=[];errors=[]
        while queue:
            tr,parent,path,matrix,active=queue.popleft()
            if tr in seen:errors.append(dict(kind='repeated_transform_or_cycle',transform=identity(tr)));continue
            seen.add(tr);go=self.target(tr,'.m_GameObject')
            if go not in self.rows:errors.append(dict(kind='gameobject_not_snapshotted',transform=identity(tr)));continue
            gt=self.tree(go);tt=self.tree(tr);name=gt.get('m_Name','');relative=path+'/'+name if parent is not None and path else name if parent is not None else ''
            flag=conjunction(active,bool_flag(gt.get('m_IsActive')))
            if parent is not None:
                if self.target(tr,'.m_Father')!=parent:errors.append(dict(kind='child_father_mismatch',transform=identity(tr)));matrix=None
                else:
                    n={};n['local_pos']=[tt.get('m_LocalPosition',{}).get(k) for k in 'xyz'];n['scale']=[tt.get('m_LocalScale',{}).get(k) for k in 'xyz'];n['rotation']=[tt.get('m_LocalRotation',{}).get(k) for k in 'xyzw']
                    local=trs(n) if all(v is not None for values in n.values() for v in values) else None;matrix=multiply(matrix,local) if matrix is not None and local is not None else None
            nodes.append(dict(gameobject=go,transform=tr,parent=parent,path=relative,name=name,activity=flag,matrix=matrix,components=self.components.get(go,[])))
            for child in self.children.get(tr,[]):queue.append((child,tr,relative,matrix,flag))
        return nodes,errors
    def asset_closure(self,start,allowed):
        seen=set();queue=deque([start]);out=[]
        while queue:
            owner=queue.popleft()
            if owner in seen:continue
            seen.add(owner)
            for loc,target,kind in self.refs.get(owner,[]):
                if kind in allowed:
                    out.append((loc,target,kind));queue.append(target)
        return out
