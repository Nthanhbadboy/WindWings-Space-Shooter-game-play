"""#7 raw102 grep/selection, independently streamed; no guessed default mesh.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
from __future__ import annotations
import argparse
from collections import Counter
import gzip
import json
from tools.verify.geometry_8141386a_atlas_io import ROOT, BRANCH, canonical, key, identity, sha_file, scratch

RAW = ROOT/'reverse-engineering/raw/geometry-8141386a/builtin'
SURFACE = ROOT/'reverse-engineering/raw/l3-visual-surface'
SELECTED = RAW/'selected-inputs.json.gz'
DEFAULT_PATH = 'Library/unity default resources'


def select():
    index = json.loads((SURFACE/'index.json').read_bytes())
    files = {f['serialized_file']:f['externals'] for f in index['files']}
    pins = {str((SURFACE/'index.json').relative_to(ROOT)):sha_file(SURFACE/'index.json')}
    counts, refs, selected = Counter(), [], {}
    def rows(group):
        for part in index[group]:
            p = SURFACE/part['path']
            if sha_file(p) != part['sha256']:
                raise ValueError('raw102 compressed SHA drift')
            pins[str(p.relative_to(ROOT))] = part['sha256']
            n = 0
            with gzip.open(p,'rb') as h:
                for i,line in enumerate(h):
                    n += 1
                    yield json.loads(line),dict(path=str(p.relative_to(ROOT)),row=i)
            if n != part['rows']:
                raise ValueError('raw102 row count drift')
    for row,loc in rows('objects'):
        if row['type'] != 'ParticleSystemRenderer':
            continue
        counts['ParticleSystemRenderer'] += 1
        for field,pointer in row['tree'].items():
            if not field.startswith('m_Mesh') or not isinstance(pointer,dict) or not pointer.get('m_PathID'):
                continue
            owner = row['serialized_file']
            fid = pointer['m_FileID']
            external = files[owner][fid-1]['path'] if fid else owner
            ref = dict(owner=identity(key(row)),field=field,pointer=pointer,external_path=external,
                       render_mode=row['tree']['m_RenderMode'],object_sha256=row['raw_object_sha256'],raw_location=loc)
            refs.append(ref)
            counts['nonnull_mesh_refs'] += 1
            if external == DEFAULT_PATH:
                counts['builtin_mesh_refs'] += 1
                selected[key(row)] = dict(identity=identity(key(row)),record=row,raw_location=loc,refs=[ref])
            else:
                counts['other_mesh_refs'] += 1
    links=[]
    for row,loc in rows('links'):
        k=key(row['owner'])
        if k in selected and row['location'] == '.m_Mesh':
            links.append(dict(record=row,raw_location=loc))
    if len(links) != len(selected):
        raise ValueError('selected builtin refs lack exact raw link rows')
    for link in links:
        row=link['record'];s=selected[key(row['owner'])]
        if row['status']!='unresolved' or row['pointer']!=s['refs'][0]['pointer']:
            raise ValueError('builtin raw link evidence differs from selection')
    value=dict(schema=1,item=7,provenance=BRANCH,xapk_sha256=index['xapk_sha256'],
               default_resource_path=DEFAULT_PATH,scan_scope=index['scope'],summary=dict(counts),
               files=index['files'],nonnull_mesh_references=refs,records=[selected[k] for k in sorted(selected)],
               original_unresolved_links=links,source_pins=pins,
               grep_recipe='Stream all indexed object/links JSONL shards, SHA + row counts checked; type ParticleSystemRenderer, nonnull m_Mesh* PPtr; exact owning external path Library/unity default resources. No Graph/no basename substitution.',
               lineage='Shared ef raw102 UnityPy capture/schema. Own streamed grep/selection; not native execution or original-byte recovery by itself.')
    return value


def load():
    v=json.loads(gzip.decompress(SELECTED.read_bytes()))
    for p,h in v['source_pins'].items():
        if sha_file(ROOT/p)!=h:raise ValueError('builtin raw source pin drift: '+p)
    return v


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
    v=select();body=gzip.compress(canonical(v)+b'\n',mtime=0)
    if a.check:
        if SELECTED.read_bytes()!=body:raise SystemExit('builtin selection drift')
    else:
        RAW.mkdir(parents=True,exist_ok=True);SELECTED.write_bytes(body)
    print(v['summary'])
