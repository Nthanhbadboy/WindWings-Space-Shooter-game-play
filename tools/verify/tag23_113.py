"""Bounded native tag23 registration/dispatch evidence and an opt-in model bridge."""
import argparse,gzip,hashlib,json
from pathlib import Path
from tools.verify.tag23_113_native import registration,dispatch,resolve,callbacks,type_records,binding_policy
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'reverse-engineering/raw/tag23-113/probe.json.gz'
OUT=ROOT/'datas/l3_ef6b75ef113_native_tag23.json.gz'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load_raw():return json.load(gzip.open(RAW))
def model_bridge(raw):
    from tools.verify.l3_frame import Frame
    from tools.verify.l3_visual_surface import load
    s=load();animator=dict(serialized_file='data.unity3d/level2',path_id=4695);clip=dict(serialized_file='data.unity3d/resources.assets',path_id=1609)
    b=next(b for b in s['sections']['bindings'] if b['animator']==animator and b['clip']==clip and b['binding']['customType']==23)
    m=next(m for m in s['sections']['motion'] if m['identity']==clip);loc=m['raw_location'];row=json.loads(gzip.decompress((ROOT/loc['path']).read_bytes()).splitlines()[loc['row']])
    assert row['tree']['m_ClipBindingConstant']['genericBindings'][b['binding_index']]==b['binding']
    assert b['status']=='unique_target' and len(b['targets'])==1
    f=Frame(1,1);target=tuple(b['targets'][0][k] for k in ('serialized_file','path_id'));component=f.g.rows[target]
    assert component['type']=='SpriteRenderer'
    field=binding_policy(raw,b['binding'],component['class_id'])
    try:f.clip(animator,clip,0)
    except ValueError as e:default_rejection=str(e)
    else:raise AssertionError('default frame policy unexpectedly accepted custom tag')
    assert not f.log,'default rejection must be atomic'
    samples=[]
    keys=next(k['keys'] for k in m['discrete_pptr_keys'] if k['binding_index']==b['binding_index'])
    for key in keys:
        t=max(m['start'],key['time'])
        writes=f.clip(animator,clip,t,pointer_fields={b['binding_index']:field})
        pointer=[w for w in writes if w.get('field')==field and w['target']==b['targets'][0]]
        assert len(pointer)==1
        samples.append(dict(time=t,write_count=len(writes),sprite_write=pointer[0],readback=f.view.target(target,'.m_Sprite')))
    return dict(binding=b,field=field,clip_raw_location=loc,clip_raw_object_sha256=row['raw_object_sha256'],target_raw_object_sha256=component['raw_object_sha256'],target_class_id=component['class_id'],default_rejection=default_rejection,viewport_fixture=[1,1],samples=samples,scope='Opt-in existing Frame modeled clip transaction only; no projection/render, engine tick, or Unity reference readback')
def build():
    raw=load_raw();model=model_bridge(raw)
    reg=registration(raw);native=dispatch(raw);types=type_records(raw)
    assert reg['map_tag']==23 and reg['map_type_descriptor']==types[0]['descriptor'] and reg['slot_23']==reg['handler']
    assert native['lookup']['return_value']==types[1]['descriptor']
    matches=[resolve(raw,text,flags,inline) for text,flags in [('m_Sprite',1),('m_Sprite',0),('m_Sprite',2),('m_Sprite',3),('m_Color',1),('m_Sprit',1),('m_SpriteX',1),('',1)] for inline in (True,False)]
    paths=[RAW,ROOT/'tools/recovery/tag23_113.py',Path(__file__),ROOT/'tools/verify/tag23_113_native.py',ROOT/'datas/l3_visual_surface.json.gz',ROOT/'reverse-engineering/raw/l3-visual-surface/index.json',ROOT/'reverse-engineering/raw/l3-layout-native/objects.json.gz',ROOT/'reverse-engineering/raw/l3-layout-native/anchor-cells.json',ROOT/'datas/l3_layout.json.gz',ROOT/'datas/l3_composition.json.gz']
    for name in ('l3_frame','l3_visual_surface','l3_composition','l3_composition_math','l3_chain_graph','l3_scene_chains','l3_animator_programs','ui_composition','l3_layout','l3_layout_math','l3_layout_emulator','balloon_animation'):paths.append(ROOT/f'tools/verify/{name}.py')
    # Pin every original object/link chunk used by Frame, plus derived motion/binding chunks.
    index=json.loads((ROOT/'reverse-engineering/raw/l3-visual-surface/index.json').read_bytes())
    for kind in ('objects','links'):
        paths.extend(ROOT/'reverse-engineering/raw/l3-visual-surface'/p['path'] for p in index[kind])
    header=json.load(gzip.open(ROOT/'datas/l3_visual_surface.json.gz'))
    paths.extend(ROOT/p['path'] for chunks in header['chunks'].values() for p in chunks)
    return dict(schema=1,provisional=True,provenance='arena/ef6b75ef',inputs={str(p.relative_to(ROOT)):digest(p) for p in sorted(set(paths))},xapk_sha256=raw['xapk_sha256'],libunity_sha256=raw['libunity_sha256'],recovery_tool_sha256=raw['tool_sha256'],type_records=types,registration=reg,absent_service=registration(raw,False),dispatch=native,unregistered_fixture_tag=dispatch(raw,tag=22),foreign_fixture_class=dispatch(raw,type_id=214),resolver_cases=matches,callbacks=callbacks(raw),model_bridge=model,scope='Original APK native registration/table stores/tag lookup/virtual callbacks in explicit synthetic fixtures; static type-info links; opt-in modeled reference write. NOT native class bootstrap, Unity service/readback, live Animator tick, full sprite setter execution, GPU or render acceptance.')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();data=build();blob=gzip.compress((json.dumps(data,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
    if args.check:assert OUT.read_bytes()==blob,'artifact differs'
    else:OUT.write_bytes(blob)
    print(json.dumps(dict(path=str(OUT.relative_to(ROOT)),sha256=hashlib.sha256(blob).hexdigest(),bytes=len(blob),registration_instructions=data['registration']['run']['instruction_count'],dispatch_instructions=data['dispatch']['lookup']['instruction_count'],resolver_cases=len(data['resolver_cases']),model_samples=len(data['model_bridge']['samples']))))
if __name__=='__main__':main()
