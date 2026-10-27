"""All APK UIObjectAnchors/ObjectScaler bindings plus bounded typed parent/camera context."""
import gzip,hashlib,io,json,zipfile
from collections import deque,Counter
from pathlib import Path
from asset_pack_v2 import extract_payload,serialized_files,sha
from spine_identity import walk_pointers

def recover(xapk,work,out,binary):
    import UnityPy
    from UnityPy.classes.PPtr import PPtr
    from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
    extract_payload(Path(xapk),work/'input');metadata=[]
    with zipfile.ZipFile(xapk) as outer:
        for entry in outer.namelist():
            if entry.endswith('.apk'):
                with zipfile.ZipFile(io.BytesIO(outer.read(entry))) as apk:
                    p='assets/bin/Data/Managed/Metadata/global-metadata.dat'
                    if p in apk.namelist():metadata.append(apk.read(p))
    assert len(metadata)==1 and sha(metadata[0])=='449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69'
    env=UnityPy.load(*(str(p) for p in sorted((work/'input').iterdir())));gen=TypeTreeGenerator('2022.3.62f3',generator='AssetStudio');gen.load_il2cpp(binary,metadata[0]);env.typetree_generator=gen
    files=serialized_files(env);names={id(sf):name for name,sf in files};records={};queue=deque();roots=[];errors=[];scan_errors=[];scripts={};links=[];headers={};scanned=0
    def ident(o):return dict(serialized_file=names[id(o.assets_file)],path_id=int(o.path_id),type=o.type.name,class_id=int(o.type))
    def key(o):return (names[id(o.assets_file)],int(o.path_id))
    def enqueue(o):
        if key(o) not in records:records[key(o)]=None;queue.append(o)
    for _,sf in files:
        for o in sf.objects.values():
            if o.type.name=='Camera':roots.append(dict(kind='camera_context',target=ident(o)));enqueue(o)
            if o.type.name!='MonoBehaviour':continue
            scanned+=1
            try:
                h=o.parse_monobehaviour_head();p=h.m_Script;sk=(id(sf),p.m_FileID,p.m_PathID)
                if sk not in scripts:
                    s=p.deref_parse_as_object();scripts[sk]=(s.m_Namespace,s.m_ClassName)
                ns,cls=scripts[sk]
                if (ns,cls) not in (('TuPro','UIObjectAnchors'),('','ObjectScaler')):continue
                headers[key(o)]=dict(class_name=cls,namespace=ns,header=dict(m_GameObject=dict(m_FileID=h.m_GameObject.m_FileID,m_PathID=h.m_GameObject.m_PathID),m_Enabled=h.m_Enabled,m_Script=dict(m_FileID=p.m_FileID,m_PathID=p.m_PathID)))
                roots.append(dict(kind=cls,target=ident(o)));enqueue(o)
            except Exception as e:scan_errors.append(dict(**ident(o),error=repr(e)))
    while queue:
        o=queue.popleft();row=dict(**ident(o),raw_object_sha256=sha(o.get_raw_data()),**headers.get(key(o),{}));records[key(o)]=row
        try:
            tree=o.read_typetree();row['tree']=tree
            if o.type.name=='MonoBehaviour':row['header_tree_disagreements']={k:dict(parsed=v,generated=tree.get(k)) for k,v in row['header'].items() if tree.get(k)!=v}
            for location,ptr in walk_pointers(tree):
                if o.type.name=='MonoBehaviour' and location in ('.m_GameObject','.m_Script'):ptr=row['header'][location[1:]]
                link=dict(owner=ident(o),location=location,pointer=ptr);links.append(link)
                if not ptr['m_PathID']:link['status']='null';continue
                try:
                    target=PPtr(m_FileID=ptr['m_FileID'],m_PathID=ptr['m_PathID'],assetsfile=o.assets_file).deref();link.update(status='resolved',target=ident(target))
                    follow=(o.type.name=='GameObject' and location.startswith('.m_Component[') and target.type.name in ('Transform','RectTransform')) or (o.type.name in ('Transform','RectTransform') and location in ('.m_Father','.m_GameObject')) or (o.type.name in ('Camera','SpriteRenderer') and location=='.m_GameObject') or (o.type.name=='MonoBehaviour' and location in ('.m_GameObject','.uiCamera','.objectScale'))
                    if follow:enqueue(target)
                except Exception as e:link.update(status='unresolved',error=repr(e))
        except Exception as e:row['error']=repr(e);errors.append(dict(**ident(o),error=repr(e)))
    rows=[r for _,r in sorted(records.items())];assert all(r is not None for r in rows)
    d=dict(provisional=True,scope='All APK headers scanned for exact target classes; target components/cameras/renderers and typed parent chain only, not child hierarchy expansion',scanned_headers=scanned,header_errors=scan_errors,read_errors=errors,roots=roots,counts=dict(Counter(r['type'] for r in rows)),objects=rows,links=links)
    b=gzip.compress(json.dumps(d,separators=(',',':')).encode(),mtime=0);assert len(b)<5_000_000;(out/'objects.json.gz').write_bytes(b)
