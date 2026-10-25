#!/usr/bin/env python3
"""Preserve exact resource-container -> prefab tree joins for early campaign waves.

No name-based dedupe or path-ID-only cross-file resolution. Original component
bytes accompany generated typetrees so later audits can check decoding.
"""
import base64
from collections import deque
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
from ui_render_context import file_context

ROOT=Path('reverse-engineering/raw/early-waves')
DATA=Path('/tmp/apk/extract')
WANTED={'wave_0164','wave_0113','wave_0005'}


def identity(reader):
    return {'serialized_file':file_context(reader)['serialized_file'],'path_id':reader.path_id}


def deref(ptr):
    return ptr.deref_parse_as_object().object_reader


def record(reader, raw=False):
    row=dict(identity(reader),type=reader.type.name)
    if reader.type.name=='MonoBehaviour':
        head=reader.parse_monobehaviour_head()
        script=head.m_Script.deref_parse_as_object()
        row['script_class']=script.m_ClassName
        row['script_namespace']=script.m_Namespace
        row['header_script_pointer']={'m_FileID':head.m_Script.m_FileID,'m_PathID':head.m_Script.m_PathID}
        row['script_identity']=identity(script.object_reader)
    row['tree']=reader.read_typetree()
    if raw:
        blob=reader.get_raw_data()
        row['bytes_base64']=base64.b64encode(blob).decode()
        row['bytes_sha256']=hashlib.sha256(blob).hexdigest()
    return row


def go_components(reader):
    go=reader.read()
    return [deref(getattr(c,'component',c)) for c in go.m_Component]


def export_tree(root):
    nodes=[];seen=set();refs={};queue=deque([(root,'')])
    while queue:
        reader,parent=queue.popleft();key=(file_context(reader)['serialized_file'],reader.path_id)
        assert key not in seen,'Cycle/repeated GameObject in transform subtree'
        seen.add(key)
        go=reader.read();path=parent+'/'+go.m_Name if parent else go.m_Name
        comps=go_components(reader)
        node={'path':path,'gameobject':record(reader),'components':[]}
        for comp in comps:
            node['components'].append(record(comp,raw=comp.type.name=='MonoBehaviour'))
            if comp.type.name in ('Transform','RectTransform'):
                for ptr in comp.read().m_Children:
                    tr=ptr.deref_parse_as_object()
                    queue.append((deref(tr.m_GameObject),path))
            if comp.type.name=='MonoBehaviour':
                head=comp.parse_monobehaviour_head()
                if head.m_Script.deref_parse_as_object().m_ClassName=='Call_Data':
                    # Generated custom fields are plain PPtr dictionaries; resolve
                    # through the owning serialized file's PPtr implementation.
                    from UnityPy.classes.PPtr import PPtr
                    for p in node['components'][-1]['tree'].get('listPrefabEnemies',[]):
                        target=deref(PPtr(m_FileID=p['m_FileID'],m_PathID=p['m_PathID'],assetsfile=comp.assets_file))
                        k=(file_context(target)['serialized_file'],target.path_id)
                        if k not in refs:
                            refs[k]={'gameobject':record(target),'components':[
                                record(c,raw=c.type.name=='MonoBehaviour') for c in go_components(target)
                                if c.type.name=='MonoBehaviour' and c.parse_monobehaviour_head().m_Script.deref_parse_as_object().m_ClassName=='Enemy_Datas']}
        nodes.append(node)
        assert len(nodes)<3000,'Refuse truncated export'
    return {'nodes':nodes,'enemy_references':list(refs.values())}


def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    inputs={n:hashlib.sha256((DATA/n).read_bytes()).hexdigest() for n in ('data.unity3d','libil2cpp.so','global-metadata.dat')}
    env=UnityPy.load(str(DATA/'data.unity3d'))
    gen=TypeTreeGenerator('2022.3.62f3',generator='AssetStudio')
    gen.load_il2cpp((DATA/'libil2cpp.so').read_bytes(),(DATA/'global-metadata.dat').read_bytes())
    env.typetree_generator=gen
    if '--enemy-details' in sys.argv:
        index=json.loads((ROOT/'index.json').read_text())
        targets={}
        for entry in index['entries']:
            if not entry['container_key'].startswith('datas/maps/waves/'):continue
            prior=json.load(gzip.open(ROOT/entry['export'],'rt'))
            assert prior['inputs_sha256']==inputs
            for ref in prior['enemy_references']:
                ident=ref['gameobject']
                targets[(ident['serialized_file'],ident['path_id'])]=ident
        found=[]
        for reader in env.objects:
            if reader.type.name!='GameObject':continue
            k=(file_context(reader)['serialized_file'],reader.path_id)
            if k not in targets:continue
            found.append({'gameobject':record(reader), 'components':[
                record(c,raw=c.type.name=='MonoBehaviour') for c in go_components(reader)]})
        assert len(found)==len(targets)
        output={'status':'PROVISIONAL — exact referenced enemy root components, not runtime replay',
                'inputs_sha256':inputs,'enemy_roots':found}
        path=ROOT/'default-enemy-components.json.gz'
        path.write_bytes(gzip.compress(json.dumps(output,ensure_ascii=False,indent=2).encode(),mtime=0))
        assert path.stat().st_size<5_000_000
        print('Exported',len(found),'exact enemy roots')
        return
    entries=[]
    for reader in env.objects:
        if reader.type.name not in ('AssetBundle','ResourceManager'):continue
        for name,value in reader.read().m_Container:
            clean=name.lower().removesuffix('.prefab')
            if clean.rsplit('/',1)[-1] not in WANTED:continue
            ptr=getattr(value,'asset',value)
            root=deref(ptr)
            entries.append({'container_key':name,'container_object':identity(reader),'root':identity(root)})
            output=export_tree(root)
            output.update(status='PROVISIONAL — exact APK resource candidate, not runtime replay',
                          inputs_sha256=inputs,container_key=name,container_object=identity(reader),root=identity(root),
                          serialized_file_context=file_context(root))
            filename=re.sub(r'[^a-zA-Z0-9_-]','_',name)+'__'+str(root.path_id)+'.json.gz'
            with gzip.open(ROOT/filename,'wt') as f:json.dump(output,f,ensure_ascii=False,indent=2)
            assert (ROOT/filename).stat().st_size<5_000_000
            entries[-1]['export']=filename
    (ROOT/'index.json').write_text(json.dumps({'status':'PROVISIONAL','inputs_sha256':inputs,'entries':entries},indent=2)+'\n')
    print(json.dumps(entries,indent=2))
    assert all(any(e['container_key'].lower().removesuffix('.prefab').endswith('datas/maps/waves/'+w) for e in entries) for w in WANTED),'Missing exact default resource keys; do not substitute same-named branch prefab'


if __name__=='__main__':main()
