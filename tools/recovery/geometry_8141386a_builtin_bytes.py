"""#7 original package inventory + selected renderer bytes, bounded/read-only.
provenance: arena/8141386a-windwings-space-shooter-game-p
Reuses immutable #6 compressed mmap/16-block reader and acknowledged ef111/110 framing.
No APK mods, native builtin-generator assumptions or default mesh replacement.
"""
from __future__ import annotations
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import shutil
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tools.verify.geometry_8141386a_atlas_io import BRANCH,canonical,scratch,sha,sha_file
from tools.verify.geometry_8141386a_atlas_sources import XAPK,APK,DATA,APK_MEMBER
from tools.verify.geometry_8141386a_builtin_sources import RAW,SELECTED,load
from tools.verify.l3_geometry_8141386a_builtin_binary import pointer_spans,packaged_target
from tools.recovery.geometry_8141386a_atlas_bytes import Bundle
from tools.verify.serialized110_binary import header,parse


def recover(xapk):
    selected=load()
    if sha_file(xapk)!=XAPK:raise ValueError('original XAPK mismatch')
    with scratch('builtin-original-') as directory:
        package_inventory=[];bundle_path=directory/'data.unity3d'
        with zipfile.ZipFile(xapk) as outer:
            for i,member in enumerate(sorted(n for n in outer.namelist() if n.endswith('.apk'))):
                path=directory/f'apk-{i}.apk'
                with outer.open(member) as src,path.open('wb') as dst:shutil.copyfileobj(src,dst,1024*1024)
                apk_sha=sha_file(path)
                with zipfile.ZipFile(path) as inner:
                    names=sorted(inner.namelist())
                    package_inventory.append(dict(apk_member=member,apk_sha256=apk_sha,entry_names=names,
                                                  default_resource_name_hits=[n for n in names if 'unity default resources' in n.lower()]))
                    if member==APK_MEMBER:
                        if apk_sha!=APK:raise ValueError('base APK mismatch')
                        with inner.open('assets/bin/Data/data.unity3d') as src,bundle_path.open('wb') as dst:shutil.copyfileobj(src,dst,1024*1024)
        if sha_file(bundle_path)!=DATA:raise ValueError('original bundle mismatch')
        bundle=Bundle(bundle_path)
        try:
            files=[];objects=[];expected_files={f['serialized_file'] for f in selected['files']}
            wanted={(r['identity']['serialized_file'],r['identity']['path_id']):r for r in selected['records']}
            found=set()
            target_pids={ref['pointer']['m_PathID'] for r in selected['records'] for ref in r['refs']}
            for node in bundle.frame['nodes']:
                file='data.unity3d/'+node['path']
                if file not in expected_files:continue
                h=header(bundle.read(node['offset'],48))
                if h['data_offset']>32*1024*1024 or h['file_size']!=node['size']:raise ValueError('serialized extent/budget')
                prefix=bundle.read(node['offset'],h['data_offset']);table=parse(prefix)
                info=dict(serialized_file=file,node=node,header=h,metadata_prefix_sha256=sha(prefix),
                          class_counts=dict(Counter(str(e['class_id']) for e in table['objects'])),
                          object_count=len(table['objects']),externals=table['externals'],
                          mesh_objects=[e for e in table['objects'] if e['class_id']==43],
                          same_path_id_other_classes=[e for e in table['objects'] if e['path_id'] in target_pids and e['class_id']!=43])
                files.append(info)
                for e in table['objects']:
                    r=wanted.get((file,e['path_id']))
                    if r is None or r['identity']['serialized_file']!=file:continue
                    if e['class_id']!=199:raise ValueError('renderer class mismatch')
                    blob=bundle.read(node['offset']+e['byte_start'],e['byte_size'])
                    if sha(blob)!=r['record']['raw_object_sha256']:raise ValueError('original renderer hash mismatch')
                    refs=[]
                    for ref in r['refs']:
                        fid=ref['pointer']['m_FileID']
                        actual_path=table['externals'][fid-1]['path']
                        if actual_path!=ref['external_path']:raise ValueError('original owner external differs')
                        match=pointer_spans(blob,ref['pointer'])
                        if not match['aligned_candidates']:raise ValueError('captured PPtr bytes not found in original object')
                        refs.append(dict(field=ref['field'],external_path=actual_path,byte_search=match))
                    objects.append(dict(identity=r['identity'],object_table_entry=e,object_sha256=sha(blob),
                                        original_hex=blob.hex(),references=refs))
                    found.add((file,e['path_id']))
                del table,prefix
            if {f['serialized_file'] for f in files}!=expected_files:raise ValueError('raw102 file inventory not fully represented by original bundle')
            if len(found)!=len(selected['records']):raise ValueError('original selected renderer set incomplete')
            for r in objects:
                for ref in r['references']:
                    ref['package_object_diagnosis']=packaged_target(ref['external_path'],ref['byte_search']['pointer']['m_PathID'],bundle.frame['nodes'],files)
            paths=['tools/recovery/geometry_8141386a_builtin_bytes.py','tools/verify/geometry_8141386a_builtin_sources.py',
                   'tools/verify/l3_geometry_8141386a_builtin_binary.py','tools/recovery/geometry_8141386a_atlas_bytes.py',
                   'tools/verify/geometry_8141386a_atlas_io.py','tools/verify/serialized110_binary.py','tools/verify/unityfs111_binary.py',str(SELECTED.relative_to(ROOT))]
            v=dict(schema=1,item=7,provenance=BRANCH,xapk_sha256=XAPK,apk_sha256=APK,bundle_sha256=DATA,
                   package_inventory=package_inventory,bundle_nodes=bundle.frame['nodes'],files=files,objects=objects,
                   block_receipts=[bundle.receipts[i] for i in sorted(bundle.receipts)],
                   tool_pins={p:sha_file(ROOT/p) for p in paths},
                   scope='All nested-APK ZIP entry names and exact data.unity3d node/SerializedFile metadata inventory; selected7 renderer object hashes/bytes/PPtr candidates. NOT a proof about engine-generated resources in native code or live memory.')
            (RAW/'byte-witness.json.gz').write_bytes(gzip.compress(canonical(v)+b'\n',mtime=0))
            print('Selected original renderer hashes:',len(objects),'original serialized files:',len(files),
                  'packaged Mesh metadata objects:',sum(len(f['mesh_objects']) for f in files),flush=True)
        finally:bundle.close()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--xapk',type=Path,required=True);recover(p.parse_args().xapk)
