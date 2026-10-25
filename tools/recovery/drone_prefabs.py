"""Scoped serialized drone identity/hierarchy snapshot from the pinned APK only."""
import argparse,gzip,hashlib,io,json,re,sys,tempfile,zipfile
from pathlib import Path
from asset_pack_v2 import extract_payload,serialized_files,XAPK_SHA
from combat_coroutine_cells import LIB_SHA
ROOT=Path(__file__).resolve().parents[2]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--xapk',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    apk=Path(a.xapk);assert hashlib.sha256(apk.read_bytes()).hexdigest()==XAPK_SHA
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    import UnityPy
    from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
    with tempfile.TemporaryDirectory() as td:
        temp=Path(td);inputs=extract_payload(apk,temp/'unity');binary=metadata=None
        with zipfile.ZipFile(apk) as outer:
            for name in outer.namelist():
                if not name.endswith('.apk'):continue
                with zipfile.ZipFile(io.BytesIO(outer.read(name))) as part:
                    for path,key in [('lib/arm64-v8a/libil2cpp.so','lib'),('assets/bin/Data/Managed/Metadata/global-metadata.dat','meta')]:
                        if path in part.namelist():
                            if key=='lib':binary=part.read(path)
                            else:metadata=part.read(path)
        assert hashlib.sha256(binary).hexdigest()==LIB_SHA
        assert hashlib.sha256(metadata).hexdigest()=='449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69'
        env=UnityPy.load(*(str(p) for p in sorted((temp/'unity').iterdir())))
        gen=TypeTreeGenerator('2022.3.62f3',generator='AssetStudio');gen.load_il2cpp(binary,metadata);env.typetree_generator=gen
        files=serialized_files(env);names={id(sf):name for name,sf in files};scripts={};records=[];errors=[];scanned=0
        def identity(obj):return dict(serialized_file=names[id(obj.assets_file)],path_id=obj.path_id)
        def snapshot(obj):return dict(**identity(obj),type=obj.type.name,tree=obj.read_typetree())
        def component(obj):
            item=snapshot(obj)
            if obj.type.name=='MonoBehaviour':
                hh=obj.parse_monobehaviour_head();script=hh.m_Script.deref_parse_as_object();item.update(class_name=script.m_ClassName,namespace=script.m_Namespace,raw_object_hex=obj.get_raw_data().hex())
            return item
        containers={}
        for name,ptr in env.container.items():
            try:
                obj=ptr.deref() if hasattr(ptr,'deref') else ptr
                containers.setdefault((id(obj.assets_file),obj.path_id),[]).append(name)
            except Exception as e:errors.append(dict(container=name,error=repr(e)))
        for filename,sf in files:
            for obj in sf.objects.values():
                if obj.type.name!='MonoBehaviour':continue
                scanned+=1
                try:
                    head=obj.parse_monobehaviour_head();ptr=head.m_Script;key=(id(sf),ptr.m_FileID,ptr.m_PathID)
                    if key not in scripts:
                        script=ptr.deref_parse_as_object();scripts[key]=(script.m_Namespace,script.m_ClassName)
                    namespace,cls=scripts[key]
                except Exception as e:errors.append(dict(**identity(obj),phase='header',error=repr(e)));continue
                if not (re.fullmatch(r'Drone_Attack\d*',cls) or cls=='GP_Loader'):continue
                row=dict(**identity(obj),class_name=cls,namespace=namespace,raw_object_hex=obj.get_raw_data().hex(),raw_object_sha256=hashlib.sha256(obj.get_raw_data()).hexdigest())
                try:
                    row['tree']=obj.read_typetree();go=head.m_GameObject.deref();row['gameobject']=snapshot(go)
                    def comps(go):return [component(p.component.deref()) for p in go.parse_as_object().m_Component]
                    # Built-in Transform references, not generated MonoBehaviour pointer fields.
                    tr=next(p.component.deref() for p in go.parse_as_object().m_Component if p.component.deref().type.name=='Transform')
                    ancestry=[];seen=set()
                    while True:
                        ident=(id(tr.assets_file),tr.path_id);assert ident not in seen;seen.add(ident)
                        tt=tr.parse_as_object();ancestor_go=tt.m_GameObject.deref()
                        ancestry.append(dict(transform=snapshot(tr),gameobject=snapshot(ancestor_go),container_paths=sorted(containers.get((id(ancestor_go.assets_file),ancestor_go.path_id),[]))))
                        if not tt.m_Father.m_PathID:break
                        tr=tt.m_Father.deref()
                    row['ancestry']=ancestry;row['root_components']=comps(ancestor_go)
                except Exception as e:row['error']=repr(e);errors.append(dict(**identity(obj),class_name=cls,phase='selected',error=repr(e)))
                records.append(row)
        path=out/'components.json.gz';path.write_bytes(gzip.compress(json.dumps(records,indent=2).encode(),mtime=0))
        (out/'component-index.json').write_text(json.dumps(dict(status='PINNED_SERIALIZED_IDENTITY_NOT_AUTOMATIC_RUNTIME_SPAWN',xapk_sha256=XAPK_SHA,lib_sha256=LIB_SHA,inputs=inputs,scanned_headers=scanned,records=len(records),errors=errors,externals=[dict(serialized_file=n,externals=[dict(path=e.path,type=e.type) for e in sf.externals]) for n,sf in files],sha256=hashlib.sha256(path.read_bytes()).hexdigest()),indent=2)+'\n')
        print('drone prefab snapshot',len(records),'records;',len(errors),'explicit errors')
if __name__=='__main__':main()
