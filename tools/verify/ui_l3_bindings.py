"""L3 drawing-use index: exact scoped PPtr != legacy name candidate != visibility."""
import csv,gzip,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
from tools.verify.ui_reference_links import resolve
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'datas/ui_l3_bindings.json.gz'
def match(owner,component,assets,names,cache):
    ref=component.get('visual_properties',{}).get('m_Sprite')
    if ref is not None:
        key=json.dumps([owner.get('serialized_file'),owner.get('externals',[]),ref],sort_keys=True)
        if key not in cache:cache[key]=resolve(owner,ref,assets)
        return cache[key]
    name=component.get('sprite')
    if name:
        choices=names.get(name,[])
        return dict(status='name_candidate_only' if len(choices)==1 else 'ambiguous_name' if choices else 'name_not_in_scoped_catalog',name=name,candidates=choices)
    return dict(status='sprite_ref_not_recorded')
def build():
    ui=ROOT/'reverse-engineering/raw/ui';indexed=list(csv.DictReader((ui/'_index.csv').read_text().splitlines()));assets=[json.loads(l) for l in gzip.decompress((ui/'render-context/Sprite.jsonl.gz').read_bytes()).splitlines()];names=defaultdict(list)
    for a in assets:names[a.get('tree',{}).get('m_Name')].append(dict(serialized_file=a.get('serialized_file'),path_id=a['path_id']))
    inventory=sorted(ui.glob('*.json.gz'));sources=[];uses=[];cache={};counts=Counter();by_screen=defaultdict(Counter)
    for row in indexed:
        p=ui/row['file'];b=p.read_bytes();owner=json.loads(gzip.decompress(b));source=len(sources);sources.append(dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),screen=owner['class'],root_path_id=owner['root_path_id'],serialized_file=owner.get('serialized_file'),nodes=len(owner['nodes'])))
        for node_index,n in enumerate(owner['nodes']):
            for component_index,c in enumerate(n.get('components',[])):
                if not(c.get('sprite') or 'm_Sprite' in c.get('visual_properties',{}) or c.get('class') in ('SpriteRenderer','Image')):continue
                result=match(owner,c,assets,names,cache);counts[result['status']]+=1;by_screen[owner['class']][result['status']]+=1
                uses.append(dict(source=source,node_index=node_index,component_index=component_index,path=n.get('path'),component=c.get('class'),active_self=n.get('active'),local_pos=n.get('local_pos'),scale=n.get('scale'),rotation=n.get('rotation'),size_delta=n.get('size_delta'),visual_properties=c.get('visual_properties',{}),sprite=result))
    evidence=[ui/'_index.csv',ui/'render-context/Sprite.jsonl.gz',Path(__file__),ROOT/'tools/verify/ui_reference_links.py']
    return dict(schema=1,provisional=True,scope='indexed APK layout sources only; name-only candidates NEVER exact asset identity; local active flag NEVER effective/runtime visibility',inventory=dict(layout_files_present=len(inventory),indexed_files=len(indexed),unindexed_files=len({p.name for p in inventory}-{r['file'] for r in indexed})),counts=dict(counts),by_screen={k:dict(v) for k,v in sorted(by_screen.items())},sources=sources,uses=uses,evidence={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in evidence})
if __name__=='__main__':
    data=build();OUT.write_bytes(gzip.compress(json.dumps(data,ensure_ascii=False,separators=(',',':')).encode(),mtime=0));assert OUT.stat().st_size<5_000_000
    print(json.dumps(dict(inventory=data['inventory'],uses=len(data['uses']),counts=data['counts'],bytes=OUT.stat().st_size),indent=2))
