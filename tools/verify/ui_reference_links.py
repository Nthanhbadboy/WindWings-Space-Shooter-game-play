#!/usr/bin/env python3
"""Scoped PPtr joins for UI drawing assets; never join a bare path_id globally."""
import csv
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCREENS = {'Board_Home','Board_Maps','Board_Stage','Board_Endgame','GP_Tutorials',
           'Tut_Settings','Tut_Settings1','Board_Pause','Board_Players','Board_Drones'}


def resolve(owner, ref, rows):
    if not isinstance(ref, dict):
        return {'status':'not_a_pptr'}
    pid=ref.get('m_PathID',0)
    if not pid:
        return {'status':'null'}
    if not owner.get('serialized_file'):
        return {'status':'owner_scope_missing'}
    fid=ref.get('m_FileID',0)
    if fid == 0:
        filename=owner['serialized_file']
    else:
        externals=[r['path'] for r in owner.get('externals',[]) if r['file_id']==fid]
        if len(externals)!=1:
            return {'status':'external_file_unresolved','file_id':fid}
        filename=externals[0]
    files={r['serialized_file'] for r in rows if r.get('serialized_file')}
    if filename not in files:
        # Serialized names may include archive prefixes. Only collapse to basename
        # when exactly one named file matches; never use path ID as a fallback.
        matches=[f for f in files if f.replace('\\','/').split('/')[-1] == filename.replace('\\','/').split('/')[-1]]
        if len(matches)!=1:
            return {'status':'target_file_unresolved','target_file':filename}
        filename=matches[0]
    matches=[r for r in rows if r.get('serialized_file')==filename and r.get('path_id')==pid]
    if len(matches)!=1:
        return {'status':'target_missing_or_ambiguous','target_file':filename,'matches':len(matches)}
    row=matches[0]
    if row.get('status')!='exported':
        return {'status':'target_export_failed','target_file':filename}
    tree=row.get('tree',{})
    return {'status':'resolved_exact_scoped_pptr','target_file':filename,'path_id':pid,
            'name':tree.get('m_Name'),'type':row.get('type'),
            'geometry':{k:tree[k] for k in ('m_Rect','m_Pivot','m_Border','m_PixelsToUnits') if k in tree}}


def main():
    ui=ROOT/'reverse-engineering/raw/ui'
    assets={};sources=[]
    for kind in ('TMP_FontAsset','Material','Sprite'):
        p=ui/'render-context'/f'{kind}.jsonl.gz'
        assets[kind]=[json.loads(l) for l in gzip.open(p,'rt')]
        sources.append({'source':str(p.relative_to(ROOT)), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    records=[]
    for entry in csv.DictReader((ui/'_index.csv').open()):
        if entry['class'] not in SCREENS: continue
        p=ui/entry['file']
        owner=json.load(gzip.open(p,'rt'))
        counts=Counter();links=[]
        for node in owner['nodes']:
            for component in node['components']:
                props=component.get('visual_properties',{})
                for field,kind in [('m_fontAsset','TMP_FontAsset'),('m_sharedMaterial','Material'),('m_Sprite','Sprite')]:
                    if field not in props: continue
                    result=resolve(owner,props[field],assets[kind])
                    counts[field+':'+result['status']]+=1
                    links.append({'node':node['path'],'component':component['class'],'field':field,
                                  'reference':props[field],'result':result})
        records.append({'class':owner['class'],'source':str(p.relative_to(ROOT)),
                        'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                        'walk_diagnostics':owner.get('walk_diagnostics',{}),
                        'counts':dict(counts),'links':links})
    out={'status':'PROVISIONAL','warning':'exact serialized binding, not runtime visibility or language font switching',
         'render_sources':sources, 'screens':records}
    p=ROOT/'reverse-engineering/raw/ui-audit/scoped-visual-links.json.gz'
    with gzip.open(p,'wt') as f: json.dump(out,f,ensure_ascii=False,indent=2)
    for r in records: print(r['class'],r['counts'])


if __name__=='__main__': main()
