"""#8 supplied managed schemas, one bounded static-parser child/class, no game code.
provenance: arena/8141386a-windwings-space-shooter-game-p
Separate workflow step AFTER byte recovery frees its large file-metadata heap.
600MiB child RSS /180s supervision; failures retained, never treated as decoded data.
"""
from __future__ import annotations
import argparse
import gzip
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import zipfile
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tools.verify.geometry_8141386a_atlas_io import BRANCH,canonical,sha,sha_file,scratch
from tools.verify.geometry_8141386a_atlas_sources import XAPK
from tools.verify.geometry_8141386a_gaps_sources import RAW,SELECTED
from tools.recovery.geometry_8141386a_builtin_bytes import type_schema

LIB='9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99'
META='449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69'


def child(args):
    import resource
    import UnityPy
    from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
    from UnityPy.helpers.Tpk import get_typetree_node
    from UnityPy.helpers.UnityVersion import UnityVersion
    if sha_file(args.lib)!=LIB or sha_file(args.metadata)!=META:raise ValueError('original binary/metadata hash mismatch')
    generator=TypeTreeGenerator(args.version,generator='AssetStudio')
    generator.load_il2cpp(args.lib.read_bytes(),args.metadata.read_bytes())
    root=type_schema(generator.get_nodes_up(args.assembly,args.fullname))
    try:event=type_schema(generator.get_nodes_up('UnityEngine.CoreModule','UnityEngine.Events.UnityEventBase'));event_error=None
    except Exception as e:event=None;event_error=repr(e)
    gradients={}
    def walk(n):
        if n.m_Type=='Gradient':
            s=type_schema(n);s['name']='normalized_native_gradient';gradients[sha(canonical(s))]=s
        for c in n.m_Children:walk(c)
    walk(get_typetree_node(198,UnityVersion.from_str(args.version)))
    v=dict(fullname=args.fullname,assembly=args.assembly,unity_version=args.version,schema=root,schema_sha256=sha(canonical(root)),
           unity_event_base_schema=event,unity_event_base_error=event_error,native_gradient_shapes=list(gradients.values()),
           UnityPy=UnityPy.__version__,TypeTreeGeneratorAPI=importlib.metadata.version('TypeTreeGeneratorAPI'),
           measured_child_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
           scope='Supplied AssetStudio managed schema + TPK native templates, NOT field-layout discovery or proof the schema fits original bytes')
    args.out.write_bytes(canonical(v)+b'\n')


def recover(xapk):
    if sha_file(xapk)!=XAPK:raise ValueError('original XAPK mismatch')
    witness=RAW/'byte-witness.json.gz';w=json.loads(gzip.decompress(witness.read_bytes()))
    owner_version=next(f['unity_version'] for f in w['files'] if f['serialized_file']=='data.unity3d/resources.assets')
    bindings={(s['tree']['m_AssemblyName'],s['tree']['m_Namespace'],s['tree']['m_ClassName']) for s in w['script_objects']}
    with scratch('gaps-schemas-') as directory:
        lib=directory/'libil2cpp.so';meta=directory/'global-metadata.dat';found=[]
        with zipfile.ZipFile(xapk) as outer:
            for i,member in enumerate(sorted(n for n in outer.namelist() if n.endswith('.apk'))):
                apk=directory/f'part-{i}.apk'
                with outer.open(member) as src,apk.open('wb') as dst:shutil.copyfileobj(src,dst,1024*1024)
                with zipfile.ZipFile(apk) as inner:
                    for entry,p in [('lib/arm64-v8a/libil2cpp.so',lib),('assets/bin/Data/Managed/Metadata/global-metadata.dat',meta)]:
                        if entry not in inner.namelist():continue
                        if p.exists():raise ValueError('ambiguous original binary input')
                        with inner.open(entry) as src,p.open('wb') as dst:shutil.copyfileobj(src,dst,1024*1024)
                        found.append(dict(apk_member=member,entry=entry,sha256=sha_file(p),size=p.stat().st_size))
        if sha_file(lib)!=LIB or sha_file(meta)!=META:raise ValueError('original code/metadata mismatch')
        results=[]
        for i,(assembly,ns,cls) in enumerate(sorted(bindings)):
            output=directory/f'schema-{i}.json';log=directory/f'schema-{i}.log';fullname=(ns+'.' if ns else '')+cls
            command=[sys.executable,str(Path(__file__)), '--child','--lib',str(lib),'--metadata',str(meta),'--version',owner_version,
                     '--assembly',assembly,'--fullname',fullname,'--out',str(output)]
            env=dict(os.environ,DOTNET_GCHeapHardLimit='20000000',COMPlus_GCHeapHardLimit='20000000')
            start=time.monotonic();peak=0;stop=None
            with log.open('wb') as stream:
                p=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT,env=env)
                while p.poll() is None:
                    try:
                        lines=Path(f'/proc/{p.pid}/status').read_text().splitlines()
                        rss=next(int(l.split()[1]) for l in lines if l.startswith('VmRSS:'));peak=max(peak,rss)
                    except (OSError,StopIteration):pass
                    if peak>600*1024:stop='CHILD_RSS_BUDGET_600MiB';p.kill()
                    elif time.monotonic()-start>180:stop='CHILD_TIMEOUT_180s';p.kill()
                    if stop is not None:break
                    time.sleep(.2)
                p.wait()
            r=dict(fullname=fullname,assembly=assembly,exit_code=p.returncode,budget_stop=stop,observed_child_peak_rss_kib=peak,
                   collector_log_tail=log.read_text(errors='replace')[-4096:],status='CAPTURED_SCHEMA' if p.returncode==0 and output.exists() else 'SCHEMA_CAPTURE_BLOCKED')
            if r['status']=='CAPTURED_SCHEMA':r['capture']=json.loads(output.read_bytes())
            results.append(r);print(fullname,r['status'],'observed childRSS KiB',peak,flush=True)
        paths=['tools/recovery/geometry_8141386a_gaps_schemas.py','tools/recovery/geometry_8141386a_builtin_bytes.py',str(SELECTED.relative_to(ROOT)),str(witness.relative_to(ROOT))]
        v=dict(schema=1,item=8,provenance=BRANCH,xapk_sha256=XAPK,libil2cpp_sha256=LIB,metadata_sha256=META,inputs=found,
               original_byte_witness_sha256=sha_file(witness),results=results,tool_pins={p:sha_file(ROOT/p) for p in paths},
               scope='Static supplied-schema capture only. Sequential isolated children after original-byte process ends; failed/budget-stopped schemas are not parsed field evidence.')
        (RAW/'schema-witness.json.gz').write_bytes(gzip.compress(canonical(v)+b'\n',mtime=0))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--xapk',type=Path);p.add_argument('--child',action='store_true')
    p.add_argument('--lib',type=Path);p.add_argument('--metadata',type=Path);p.add_argument('--version');p.add_argument('--assembly');p.add_argument('--fullname');p.add_argument('--out',type=Path);a=p.parse_args()
    if a.child:child(a)
    elif a.xapk:recover(a.xapk)
    else:p.error('--xapk or --child required')
