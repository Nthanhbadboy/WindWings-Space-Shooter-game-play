"""Report118 / MISSING-row16 follow-up inputs; no closed artifact regeneration.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
from __future__ import annotations
import argparse
from collections import Counter
import gzip
import json
from tools.verify.geometry_8141386a_atlas_io import ROOT,BRANCH,canonical,sha,sha_file,iter_geometry,key,identity

RAW=ROOT/'reverse-engineering/raw/geometry-8141386a/sprite-consumers'
CATALOG=RAW/'sprite-catalog.jsonl.gz'
INPUTS=RAW/'source-inputs.json'
SCHEMAS=RAW/'native-schemas.json.gz'
SOURCES=('l3-chain','l3-visual-surface')


def catalog_rows():
    for row,loc in iter_geometry():
        if row['type']=='Sprite':
            yield dict(identity=identity(key(row)),name=row['tree']['m_Name'],original_object_sha256=row['object_bytes_sha256'],raw_location=loc)


def source_inputs():
    pins={};scopes={}
    for name in SOURCES:
        base=ROOT/'reverse-engineering/raw'/name;idx=json.loads((base/'index.json').read_bytes())
        paths=[base/'index.json']+[base/p['path'] for g in ('objects','links') for p in idx[g]]
        pins.update({str(p.relative_to(ROOT)):sha_file(p) for p in paths})
        scopes[name]=dict(objects=sum(p['rows'] for p in idx['objects']),links=sum(p['rows'] for p in idx['links']),captured_types=idx['counts'],roots=len(idx['roots']))
    base=ROOT/'reverse-engineering/raw/sprite-geometry';idx=json.loads((base/'index.json').read_bytes())
    for p in [base/'index.json']+[base/p['path'] for p in idx['files']]:pins[str(p.relative_to(ROOT))]=sha_file(p)
    previous=ROOT/'reverse-engineering/raw/geometry-8141386a/builtin/byte-witness.json.gz';pins[str(previous.relative_to(ROOT))]=sha_file(previous)
    previous=json.loads(gzip.decompress(previous.read_bytes()));native_counts={r['serialized_file']:r['class_counts'].get('212',0) for r in previous['files']}
    return dict(schema=1,item=118,task='MISSING-row16 sprite-consumer follow-up',provenance=BRANCH,source_pins=pins,captured_scopes=scopes,
                expected_original_sprite_renderer_counts=native_counts,expected_original_sprite_renderers=sum(native_counts.values()),
                lineage='Shared native Sprite-geometry capture + own closed#6 original-object corroboration, raw98/raw102 captures. Context closure is not all-APK consumer coverage or runtime use.')


def build_inputs():
    RAW.mkdir(parents=True,exist_ok=True);rows=list(catalog_rows())
    # Metadata-only catalog: no full Sprite/Graph/geometry fixture retained.
    if len({key(r['identity']) for r in rows})!=len(rows):raise ValueError('duplicate native Sprite identity')
    with CATALOG.open('wb') as handle,gzip.GzipFile(fileobj=handle,filename='',mode='wb',mtime=0) as stream:
        for r in rows:stream.write(canonical(r)+b'\n')
    value=source_inputs();value['sprite_count']=len(rows);value['catalog_sha256']=sha_file(CATALOG)
    INPUTS.write_bytes(canonical(value)+b'\n')
    return value


def load_inputs():
    v=json.loads(INPUTS.read_bytes())
    if v['provenance']!=BRANCH or sha_file(CATALOG)!=v['catalog_sha256']:raise ValueError('sprite-consumer input drift')
    for p,h in v['source_pins'].items():
        if sha_file(ROOT/p)!=h:raise ValueError('sprite-consumer source pin drift:'+p)
    return v


def catalog():
    with gzip.open(CATALOG,'rb') as h:
        for line in h:yield json.loads(line)


def prepare_schemas():
    import UnityPy
    from UnityPy.helpers.Tpk import get_typetree_node
    from UnityPy.helpers.UnityVersion import UnityVersion
    from tools.recovery.geometry_8141386a_builtin_bytes import type_schema
    version='2022.3.62f3'
    v=dict(schema=1,item=118,provenance=BRANCH,UnityPy=UnityPy.__version__,version=version,
           classes={str(c):type_schema(get_typetree_node(c,UnityVersion.from_str(version))) for c in (1,212)},
           scope='Supplied native TPK schema. Must consume/inverse-serialize complete original bytes; not field-layout discovery/native execution.')
    SCHEMAS.write_bytes(gzip.compress(canonical(v)+b'\n',mtime=0))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');p.add_argument('--schemas',action='store_true');a=p.parse_args()
    if a.schemas:prepare_schemas()
    elif a.check:
        v=load_inputs();expected=list(catalog_rows());actual=list(catalog())
        measured=source_inputs()
        if expected!=actual or measured!={k:v[k] for k in measured}:raise SystemExit('sprite-consumer selection drift')
        print('PASS input selection',v['sprite_count'],'native sprites;',v['expected_original_sprite_renderers'],'original SpriteRenderer metadata entries')
    else:
        v=build_inputs();print('Selected',v['sprite_count'],'Sprite identities; expected original renderers',v['expected_original_sprite_renderers'])
