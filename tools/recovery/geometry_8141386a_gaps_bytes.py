"""#8 original 5 header-only MB +52 default refs +3 actual standalone Mesh targets.
provenance: arena/8141386a-windwings-space-shooter-game-p
Bounded ZIP/one-file metadata/selected objects only, never whole Graph/atlas decode.
"""
from __future__ import annotations
import argparse
import gzip
import json
from pathlib import Path
import shutil
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tools.verify.geometry_8141386a_atlas_io import BRANCH,canonical,key,identity,sha,sha_file,scratch,full_file
from tools.verify.geometry_8141386a_atlas_sources import XAPK,APK,DATA,APK_MEMBER
from tools.verify.geometry_8141386a_gaps_sources import RAW,SELECTED,load
from tools.verify.l3_geometry_8141386a_gaps_header import header as mb_header
from tools.verify.l3_geometry_8141386a_builtin_binary import pointer_spans
from tools.recovery.geometry_8141386a_atlas_bytes import Bundle
from tools.recovery.geometry_8141386a_builtin_bytes import read_default_file,type_schema
from tools.verify.serialized110_binary import header,parse
from tools.verify.controller109_binary import Reader


def recover(xapk):
    import UnityPy
    from UnityPy.helpers.Tpk import get_typetree_node
    from UnityPy.helpers.UnityVersion import UnityVersion
    source=load()
    if sha_file(xapk)!=XAPK:raise ValueError('original XAPK mismatch')
    with scratch('gaps-original-') as directory:
        apk=directory/'base.apk';bundle_path=directory/'data.unity3d';default=directory/'unity default resources'
        with zipfile.ZipFile(xapk) as outer,outer.open(APK_MEMBER) as src,apk.open('wb') as dst:shutil.copyfileobj(src,dst,1024*1024)
        if sha_file(apk)!=APK:raise ValueError('base APK mismatch')
        with zipfile.ZipFile(apk) as inner:
            for entry,p in [('assets/bin/Data/data.unity3d',bundle_path),('assets/bin/Data/unity default resources',default)]:
                with inner.open(entry) as src,p.open('wb') as dst:shutil.copyfileobj(src,dst,1024*1024)
        if sha_file(bundle_path)!=DATA:raise ValueError('original bundle mismatch')
        b=Bundle(bundle_path)
        try:
            wanted={key(r['identity']):r for r in source['header_records']+source['mesh_references']}
            script_targets={};native_headers=[];mesh_refs=[];scripts=[];files=[];found=set()
            # Native script targets are known from the source header's exact owner table,
            # so all selected objects can be recovered in one metadata pass per file.
            ext={f['serialized_file']:f['externals'] for f in source['files']}
            for r in source['header_records']:
                p=r['record']['header']['m_Script'];owner=r['identity']['serialized_file'];file=full_file(ext[owner][p['m_FileID']-1]['path']) if p['m_FileID'] else owner
                script_targets[(file,p['m_PathID'])]=None
            selected_files={k[0] for k in wanted}|{k[0] for k in script_targets}
            for node in b.frame['nodes']:
                file='data.unity3d/'+node['path']
                if file not in selected_files:continue
                h=header(b.read(node['offset'],48))
                if h['data_offset']>32*1024*1024 or h['file_size']!=node['size']:raise ValueError('metadata extent/budget')
                prefix=b.read(node['offset'],h['data_offset']);table=parse(prefix);version=UnityVersion.from_str(table['unity_version'])
                files.append(dict(serialized_file=file,node=node,header=h,unity_version=table['unity_version'],metadata_prefix_sha256=sha(prefix),
                                  embedded_type_tree=table['embedded_type_tree'],object_count=len(table['objects']),externals=table['externals']))
                for e in table['objects']:
                    k=(file,e['path_id'])
                    if k not in wanted and k not in script_targets:continue
                    blob=b.read(node['offset']+e['byte_start'],e['byte_size']);obj=dict(identity=identity(k),entry=e,object_sha256=sha(blob),original_hex=blob.hex())
                    if k in script_targets:
                        if e['class_id']!=115:raise ValueError('exact original script target is not MonoScript')
                        schema=type_schema(get_typetree_node(115,version));reader=Reader(blob);tree=reader.decode(schema)
                        obj.update(tree=tree,schema=schema,schema_sha256=sha(canonical(schema)),fully_consumed=reader.pos)
                        scripts.append(obj);script_targets[k]=obj
                    if k not in wanted:continue
                    q=wanted[k]
                    if sha(blob)!=q['record']['raw_object_sha256']:raise ValueError('original selected-object hash mismatch')
                    if e['class_id']==114:
                        head=mb_header(blob)
                        for field,value in q['record']['header'].items():
                            if head['fields'][field]!=value:raise ValueError('own original native MB header disagrees')
                        schema=type_schema(get_typetree_node(114,version));reader=Reader(blob);native=reader.node(schema)
                        if native!=head['fields'] or reader.pos!=head['header_end']:raise ValueError('native supplied-schema/header decode disagreement')
                        obj.update(native_header=head,native_header_schema=schema,type_table_entry=table['types'][e['type_id']],
                                   class_name=q['record']['class_name'],namespace=q['record'].get('namespace',''),capture_exception=q['capture_exception'])
                        native_headers.append(obj)
                    elif e['class_id'] in (199,33):
                        p=q['reference']['record']['pointer'];fid=p['m_FileID'];path=table['externals'][fid-1]['path'] if fid else file
                        if path!='Library/unity default resources':raise ValueError('original owner external is not default-resource file')
                        match=pointer_spans(blob,p)
                        if not match['unique_aligned_match']:raise ValueError('default Mesh PPtr match is not unique')
                        obj.update(pointer=match,external_path=path,field=q['reference']['record']['location'])
                        mesh_refs.append(obj)
                    else:raise ValueError('selected original component class mismatch')
                    found.add(k)
                del prefix,table
            if found!=set(wanted) or any(v is None for v in script_targets.values()):raise ValueError('original selected object/script inventory incomplete')
            target_pids={r['reference']['record']['pointer']['m_PathID'] for r in source['mesh_references']}
            resource=read_default_file(default,'assets/bin/Data/unity default resources',target_pids)
            pins=['tools/recovery/geometry_8141386a_gaps_bytes.py','tools/verify/geometry_8141386a_gaps_sources.py','tools/verify/l3_geometry_8141386a_gaps_header.py',
                  'tools/recovery/geometry_8141386a_atlas_bytes.py','tools/recovery/geometry_8141386a_builtin_bytes.py','tools/verify/controller109_binary.py',
                  'tools/verify/serialized110_binary.py','tools/verify/unityfs111_binary.py','tools/verify/geometry_8141386a_atlas_io.py',str(SELECTED.relative_to(ROOT))]
            v=dict(schema=1,item=8,provenance=BRANCH,xapk_sha256=XAPK,apk_sha256=APK,bundle_sha256=DATA,UnityPy=UnityPy.__version__,
                   files=files,header_objects=native_headers,mesh_owner_objects=mesh_refs,script_objects=scripts,external_resource=resource,
                   tool_pins={p:sha_file(ROOT/p) for p in pins},block_receipts=[b.receipts[i] for i in sorted(b.receipts)],
                   scope='Fresh original full selected-component bytes, exact native headers/MonoScript type identity, actual three standalone Mesh payloads. Header custom tails remain opaque until separately validated schema decode. No native/runtime/render claim.')
            (RAW/'byte-witness.json.gz').write_bytes(gzip.compress(canonical(v)+b'\n',mtime=0))
            print('Original header objects',[(r['identity']['path_id'],r['entry']['byte_size'],r['native_header']['tail_size']) for r in native_headers],flush=True)
            print('Original default refs',len(mesh_refs),'scripts',len(scripts),'actual meshes',[(m['path_id'],m['tree']['m_Name']) for m in resource['selected_meshes']],flush=True)
        finally:b.close()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--xapk',type=Path,required=True);recover(p.parse_args().xapk)
