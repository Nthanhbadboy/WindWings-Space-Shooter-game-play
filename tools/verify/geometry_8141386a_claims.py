"""Explicit, READ-ONLY historical verification-support scope, not scientific acceptance.
provenance: arena/8141386a-windwings-space-shooter-game-p

The ef base deliberately retains old runtime-probe and local spec summaries. Do not
rewrite those peer paths to satisfy historical spec assertions. A small pinned support
fixture overlays them only in a disposable symlink view; APKD1/AI1/RD1 ALWAYS measure
and check current own worktree, including the same-commit report. All other assertions
retain original spec expected values. --unscoped-legacy still exposes the inherited
incompatibilities; scoped success MUST NOT be represented as all current raw passing.
"""
from __future__ import annotations

import base64
import fnmatch
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from functools import wraps
from contextlib import contextmanager
import os

ROOT=Path(__file__).resolve().parents[2]
SPEC="0e2af55f4b2cf1ee6b0b2b66bf151aa28573013d"
BUNDLE=ROOT/"reverse-engineering/raw/geometry-8141386a/historical-verification-support.json.gz"
PROVENANCE="arena/8141386a-windwings-space-shooter-game-p"
SCOPED_CURRENT={"APKD1","AI1","RD1"}
EXACT={"docs/spec/ASSETS.md","docs/spec/BALANCE.md","docs/spec/UI.md",
       "runtime-probe/RamusBridge.cs","runtime-probe/README.md","runtime-probe/collect.sh",
       ".github/scripts/build-bridge.sh","docs/apk-analysis/15-enemy-hp.csv",
       "reverse-engineering/il2cpp/dump.cs.gz", "tools/verify-claims.py"}
PATTERNS=["docs/apk-analysis/ramus/2026-10-23-phone/*.json",
          "docs/apk-analysis/ramus/2026-10-23-phone/*.md",
          "reverse-engineering/raw/typetrees/*AnimationEvents*.jsonl.gz",
          "docs/apk-analysis/*_Director.csv","docs/apk-analysis/*AnimationEvents.csv"]


def digest(b):return hashlib.sha256(b).hexdigest()


def in_group(p):
    return p in EXACT or any(fnmatch.fnmatchcase(p,pat) for pat in PATTERNS)


def pack_support():
    """Explicit named path groups only, not importing a peer checkout/tree."""
    tree=subprocess.check_output(["git","-C",str(ROOT),"ls-tree","-r","-z",SPEC]).split(b"\0")
    selected=[]
    for line in tree:
        if not line:continue
        meta,path=line.split(b"\t",1);path=path.decode()
        if not in_group(path):continue
        body=subprocess.check_output(["git","-C",str(ROOT),"show",SPEC+":"+path])
        if len(body)>5000000:raise ValueError("oversized support input")
        item=dict(path=path,git_blob=meta.decode().split()[2],bytes=len(body),sha256=digest(body))
        if path=='reverse-engineering/il2cpp/dump.cs.gz':
            current=(ROOT/path).read_bytes()
            # The only AP1 classification delta is gzip MTIME, NOT different C#.
            # Preserve an exact pinned-header recipe instead of a 2.7 MB duplicate.
            if current[10:]!=body[10:]:raise ValueError('dump suffix differs: not a timestamp-only support patch')
            item['pinned_header_recipe']=dict(prefix_hex=body[:10].hex(),suffix_sha256=digest(body[10:]),
                                               note='Historical support view only; original worktree gzip is never rewritten')
        else:item['base64']=base64.b64encode(body).decode()
        selected.append(item)
    if not EXACT <= {r['path'] for r in selected}:raise ValueError("incomplete named support fixture")
    value=dict(schema=1,provenance=PROVENANCE,spec_ref=SPEC,scope="HISTORICAL_VERIFICATION_SUPPORT_NOT_CURRENT_RAW_OR_GEOMETRY",
               path_groups=PATTERNS,exact=sorted(EXACT),files=selected)
    data=(json.dumps(value,sort_keys=True,separators=(",",":"))+"\n").encode()
    BUNDLE.write_bytes(gzip.compress(data,mtime=0))
    print(len(selected),"historical support paths",len(data),"JSON bytes",BUNDLE.stat().st_size,"gz bytes")


def unpack_support():
    value=json.loads(gzip.decompress(BUNDLE.read_bytes()))
    if value['spec_ref']!=SPEC or value['provenance']!=PROVENANCE:raise ValueError("support source/provenance mismatch")
    found={}
    for item in value['files']:
        path=item['path']
        if not in_group(path) or Path(path).is_absolute() or '..' in Path(path).parts or path in found:
            raise ValueError("unexpected/unsafe/duplicate support path")
        if 'pinned_header_recipe' in item:
            if path!='reverse-engineering/il2cpp/dump.cs.gz':raise ValueError('unexpected header-recipe path')
            recipe=item['pinned_header_recipe'];suffix=(ROOT/path).read_bytes()[10:]
            prefix=bytes.fromhex(recipe['prefix_hex'])
            if len(prefix)!=10 or digest(suffix)!=recipe['suffix_sha256']:raise ValueError('historical gzip suffix mismatch')
            body=prefix+suffix
        else:body=base64.b64decode(item['base64'],validate=True)
        blob=hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()
        if digest(body)!=item['sha256'] or len(body)!=item['bytes'] or blob!=item['git_blob']:
            raise ValueError("support byte/git blob witness mismatch: "+path)
        found[path]=body
    if not EXACT<=found.keys():raise ValueError("incomplete support")
    return found


def writable_parent(view,relative):
    """Copy-on-write only symlink directory entries. Never mutate original targets."""
    cursor=view
    for part in Path(relative).parts[:-1]:
        cursor=cursor/part
        if cursor.is_symlink():
            target=cursor.resolve()
            children=list(target.iterdir())
            cursor.unlink();cursor.mkdir()
            for child in children:(cursor/child.name).symlink_to(child,target_is_directory=child.is_dir())
        elif not cursor.exists():cursor.mkdir()
    return view/relative


@contextmanager
def actual_root(module):
    previous=module.ROOT
    try:
        module.ROOT=str(ROOT)
        yield
    finally:module.ROOT=previous


def actual_measure(module,fn):
    @wraps(fn)  # preserve original source introspection for RB1, not fabricated kinds
    def measure():
        with actual_root(module):return fn()
    return measure


def main(module):
    if '--pack-geometry-support' in module.sys.argv:
        module.sys.argv.remove('--pack-geometry-support');pack_support();return 0
    files=unpack_support()
    scratch=ROOT/'.arena';scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='geometry-claims-',dir=scratch) as temp:
        view=Path(temp)
        for name in ('datas','docs','reverse-engineering','runtime-probe','tools','.github','.git'):
            original=ROOT/name
            if original.exists():(view/name).symlink_to(original,target_is_directory=original.is_dir())
        # Hide own-only rows from historical globs only; list them explicitly in output.
        masked=[]
        for pat in PATTERNS:
            for original in ROOT.glob(pat):
                rel=str(original.relative_to(ROOT))
                if original.is_file() and rel not in files:
                    path=writable_parent(view,rel)
                    if path.is_symlink():path.unlink();masked.append(rel)
        for rel,body in files.items():
            path=writable_parent(view,rel)
            if path.is_symlink():path.unlink()
            path.write_bytes(body)
        print('SCOPE: historical support spec '+SPEC+'; '+str(len(files))+' pinned overlay paths; NO peer worktree changes.')
        print('CURRENT OWN WORKTREE: APKD1 / AI1 / RD1 only. Geometry has separate source-byte/artifact/regression tests.')
        print('NOT a claim that all current ef raw/runtime-probe passed historical assertions. --unscoped-legacy exposes that diagnostic.')
        print('Support bundle sha256: '+digest(BUNDLE.read_bytes()))
        for p in masked:print('Historical-glob excludes own-only path: '+p)
        module.ROOT=str(view)
        module.PHONE=str(view/'docs/apk-analysis/ramus/2026-10-23-phone')
        # Every source is in the explicit view. Pin only own HEAD as a last-resort
        # git fallback, never a moving peer ref. PROVENANCE reports any such fallback.
        own_head=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD']).decode().strip()
        module.DEFAULT_REFS=[own_head]
        module.REFS=[own_head]
        for c in module.CLAIMS:
            if c.cid in SCOPED_CURRENT:c.measure=actual_measure(module,c.measure)
        # Git subprocesses (if an explicit user --ref is supplied) must point at the real
        # repository. No claim may silently use an unpinned moving default ref.
        original_git=module.git
        def real_git(*args):
            with actual_root(module):return original_git(*args)
        module.git=real_git
        old=os.getcwd()
        try:
            os.chdir(view)
            return module.main()
        finally:
            os.chdir(old)
            module.ROOT=str(ROOT)


if __name__=='__main__':pack_support()
