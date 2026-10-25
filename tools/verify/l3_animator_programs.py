"""Compiled Animator programs and explicit clip-local coefficient probes.
Provisional static interpretation, not Unity Animator execution or visual acceptance.
"""
import argparse
import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from tools.verify.l3_chain_graph import ROOT, key
from tools.verify.balloon_animation import width
OUT=ROOT/'datas/l3_animator_programs.json.gz'

def unwrap(value):return value.get('data',value)
def names(table,value):return table.get(value,[])

def controller_program(asset,raw):
    t=raw['tree'];c=t['m_Controller'];tos=defaultdict(list)
    for h,name in t['m_TOS']:
        if name not in tos[h]:tos[h].append(name)
    refs={r['field']:r['target'] for r in asset['references']}
    clips=[refs.get(f'.m_AnimationClips[{i}]') for i in range(len(t['m_AnimationClips']))]
    defaults=unwrap(c['m_DefaultValues']);parameters=[]
    # Serialized parameter enum values are retained; scalar default slots are typed.
    for v in unwrap(c['m_Values'])['m_ValueArray']:
        field={1:'m_FloatValues',3:'m_IntValues',4:'m_BoolValues',9:'m_BoolValues'}.get(v['m_Type'])
        array=defaults.get(field,[]) if field else []
        parameters.append(dict(raw=v,names=names(tos,v['m_ID']),default=array[v['m_Index']] if 0<=v['m_Index']<len(array) else None,default_status='typed_slot' if 0<=v['m_Index']<len(array) else 'unresolved_slot',default_storage=field))
    def transition(tw,state_count,selector=False):
        tr=unwrap(tw);destination=tr['m_Destination' if selector else 'm_DestinationState']
        return dict(raw=tr,name_candidates=names(tos,tr.get('m_ID')),destination_index=destination,destination_status='local_state_index' if 0<=destination<state_count else 'encoded_selector_or_exit_not_local_index',conditions=[dict(raw=unwrap(cw),parameter_names=names(tos,unwrap(cw)['m_EventID'])) for cw in tr['m_ConditionConstantArray']])
    machines=[]
    for mi,mw in enumerate(c['m_StateMachineArray']):
        m=unwrap(mw);state_count=len(m['m_StateConstantArray']);states=[]
        for si,sw in enumerate(m['m_StateConstantArray']):
            s=unwrap(sw);trees=[]
            for tree_index,bw in enumerate(s['m_BlendTreeConstantArray']):
                nodes=[]
                for ni,nw in enumerate(unwrap(bw)['m_NodeArray']):
                    n=unwrap(nw);cid=n['m_ClipID'];children=n['m_ChildIndices']
                    nodes.append(dict(node_index=ni,raw=n,clip=clips[cid] if not children and 0<=cid<len(clips) else None,clip_status='leaf_clip_index_resolved' if not children and 0<=cid<len(clips) and clips[cid] else 'internal_blend_node' if children else 'unresolved_clip_index'))
                trees.append(dict(tree_index=tree_index,nodes=nodes))
            states.append(dict(state_index=si,name_candidates=names(tos,s['m_NameID']),path_candidates=names(tos,s['m_FullPathID']),raw=s,trees=trees,transitions=[transition(tw,state_count) for tw in s['m_TransitionConstantArray']]))
        default=m['m_DefaultState']
        machines.append(dict(machine_index=mi,default_state_index=default,default_status='valid_index' if 0<=default<state_count else 'empty_machine' if not states else 'invalid_index',states=states,any_state_transitions=[transition(tw,state_count) for tw in m['m_AnyStateTransitionConstantArray']],selectors=[dict(raw=unwrap(sel),transitions=[transition(tw,state_count,True) for tw in unwrap(sel)['m_TransitionConstantArray']]) for sel in m['m_SelectorStateConstantArray']]))
    return dict(identity=asset['identity'],name=t['m_Name'],raw_location=asset['raw_location'],raw_object_sha256=raw['raw_object_sha256'],layers=[unwrap(l) for l in c['m_LayerArray']],parameters=parameters,parameter_default_arrays=defaults,machines=machines,clips=clips,behaviour_ranges=t['m_StateMachineBehaviourVectorDescription'],behaviours=t['m_StateMachineBehaviours'])

def build():
    from tools.verify.l3_recipe import Recipes
    r=Recipes();controllers=[controller_program(a,r.raw(a['raw_location'])) for a in r.section('assets') if a['type']=='AnimatorController'];attachments={}
    for n in r.section('nodes'):
        for c in n['components']:
            if c['type']=='Animator':
                direct=[ref['target'] for ref in c['references'] if ref['field']=='.m_Controller']
                row=dict(animator=c['identity'],gameobject=n['gameobject'],controllers=direct,enabled=c['enabled'],serialized_properties=c['properties'])
                k=key(c['identity'])
                if k in attachments:assert attachments[k]==row
                attachments[k]=row
    counts=Counter(controllers=len(controllers),animator_attachments=len(attachments))
    for c in controllers:
        counts['parameters']+=len(c['parameters'])
        for m in c['machines']:
            counts['machines']+=1;counts['states']+=len(m['states']);counts['empty_machines']+=not m['states'];counts['any_transitions']+=len(m['any_state_transitions'])
            for s in m['states']:
                counts['state_transitions']+=len(s['transitions']);counts['motion_leaves']+=sum(len(t['nodes']) for t in s['trees'])
    # Audit every failed/ambiguous binding against the actual source GO's component list.
    node_map={key(n['gameobject']):n for n in r.section('nodes')};diagnostics=[]
    for b in r.section('animation_bindings'):
        if b['status']=='unique_target':continue
        candidates=[]
        for p in b['path_candidates']:
            n=node_map.get(key(p['gameobject']));components=n['component_identities'] if n else []
            candidates.append(dict(**p,actual_components=components))
        reason='multiple_component_targets' if b['status']=='ambiguous_targets' else 'path_not_in_animator_subtree' if not candidates else 'required_component_class_absent' if all(not any(c['type']=='MonoBehaviour' if b['binding']['typeID']==114 else c['type']=='BoxCollider2D' if b['binding']['typeID']==61 else True for c in p['actual_components']) for p in candidates) else 'exact_script_or_type_not_matched'
        diagnostics.append(dict(animator=b['animator'],clip=b['clip'],binding_index=b['binding_index'],required=b['binding'],reason=reason,candidates=candidates,existing_targets=b['component_targets']))
    counts['binding_diagnostics']=len(diagnostics)
    return dict(schema=1,provisional=True,scope='Compiled controller state/default/transition/condition/leaf clip graph and source binding diagnostics. No transition scheduler, script Play/CrossFade invocation, blending, particles, projection or render execution.',base_contract_sha256=hashlib.sha256((ROOT/'datas/l3_scene_chains.json.gz').read_bytes()).hexdigest(),tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),counts=dict(counts),controllers=controllers,animator_attachments=[attachments[k] for k in sorted(attachments)],binding_diagnostics=diagnostics)

def load():
    b=OUT.read_bytes();d=json.loads(gzip.decompress(b));assert d['base_contract_sha256']==hashlib.sha256((ROOT/'datas/l3_scene_chains.json.gz').read_bytes()).hexdigest();return d

def probe_channels(m,time):
    """Evaluate a chosen clip at an explicit local time, without choosing a runtime state.
    Streamed coefficients are a cubic polynomial relative to their key; dense grid is linear.
    Sprite/int channels use a step. Constant initial/sentinel keys are time-independent; nonconstant sentinels are not extrapolated.
    """
    if not math.isfinite(time) or not m['start']<=time<=m['stop']:raise ValueError('time must be finite inside explicit clip start/stop')
    discrete=set();cursor=0
    for b in m['bindings']:
        if b.get('isPPtrCurve') or b.get('isIntCurve'):discrete.update(range(cursor,cursor+width(b)))
        cursor+=width(b)
    sc=m['continuous_stream_curve_count']+m['discrete_curve_count'];dense=m['dense'];dc=dense['m_CurveCount'];values=[]
    for index in range(m['channel_count']):
        if index<sc:
            keys=[dict(time=f['time'],**k) for f in m['streamed'] if isinstance(f['time'],(float,int)) and m['start']<=f['time']<=time for k in f['keys'] if k['index']==index]
            if not keys:
                initial=[k for f in m['streamed'] if isinstance(f['time'],(float,int)) and f['time']<m['start'] for k in f['keys'] if k['index']==index]
                if initial and initial[-1]['coeff'][:3]==[0,0,0]:
                    values.append(dict(channel=index,value=initial[-1]['coeff'][3],status='initial_constant_key'))
                else:values.append(dict(channel=index,value=None,status='no_non_sentinel_key_before_time'))
                continue
            k=keys[-1];dt=time-k['time'];a,b,c,v=k['coeff']
            value=v if index in discrete or dt==0 else ((a*dt+b)*dt+c)*dt+v
            values.append(dict(channel=index,value=value if math.isfinite(value) else None,status='nonfinite_polynomial_unknown' if not math.isfinite(value) else 'discrete_step' if index in discrete else 'streamed_polynomial_model',key_time=k['time']))
        elif index<sc+dc:
            rate=dense['m_SampleRate'];frame=(time-dense['m_BeginTime'])*rate
            if not 0<=frame<=dense['m_FrameCount']-1:values.append(dict(channel=index,value=None,status='outside_dense_grid'));continue
            lo=math.floor(frame);hi=min(lo+1,dense['m_FrameCount']-1);column=index-sc;arr=dense['m_SampleArray'];v0=arr[lo*dc+column];v1=arr[hi*dc+column]
            values.append(dict(channel=index,value=v0 if index in discrete else v0+(v1-v0)*(frame-lo),status='dense_step' if index in discrete else 'dense_linear_model'))
        else:values.append(dict(channel=index,value=m['constants'][index-sc-dc],status='constant'))
    result=[];cursor=0
    for bi,b in enumerate(m['bindings']):
        selected=values[cursor:cursor+width(b)];row=dict(binding_index=bi,binding=b,channels=selected)
        if b.get('isPPtrCurve'):
            value=selected[0]['value'];i=int(value) if value is not None and math.isfinite(value) and value==int(value) else None
            row['pptr_mapping_index']=i;row['pptr_target']=m['pptr_targets'][i] if i is not None and 0<=i<len(m['pptr_targets']) else None
        result.append(row);cursor+=width(b)
    return result

def probe_state(reader,animator,controller,machine_index,state_index,time):
    programs=load()
    attachment=next(a for a in programs['animator_attachments'] if key(a['animator'])==key(animator))
    if key(controller) not in {key(c) for c in attachment['controllers']}:raise ValueError('controller is not directly attached to this Animator')
    program=next(c for c in programs['controllers'] if key(c['identity'])==key(controller))
    if machine_index<0 or state_index<0:raise ValueError('negative machine/state index')
    state=program['machines'][machine_index]['states'][state_index]
    leaves=[n for t in state['trees'] for n in t['nodes']]
    if len(leaves)!=1 or leaves[0]['clip_status']!='leaf_clip_index_resolved':raise ValueError('probe requires one resolved motion leaf; no implicit blend selection')
    clip=leaves[0]['clip'];motion=next(m for m in reader.section('motion') if key(m['identity'])==key(clip))
    properties=probe_channels(motion,time)
    bindings={b['binding_index']:b for b in reader.section('animation_bindings') if key(b['animator'])==key(animator) and key(b['clip'])==key(clip)}
    for prop in properties:
        binding=bindings.get(prop['binding_index'])
        prop['target_binding']=binding
    return dict(provisional=True,scope='User-selected compiled state and explicit clip-local time; polynomial arithmetic model, NOT runtime state selection, transition/blend execution or rendered pose.',animator=animator,controller=controller,machine_index=machine_index,state_index=state_index,state_names=state['name_candidates'],serialized_state_speed=state['raw']['m_Speed'],clip=clip,clip_local_time=time,properties=properties)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--clip',type=int);p.add_argument('--animator',type=int);p.add_argument('--controller',type=int);p.add_argument('--state',type=int,default=0);p.add_argument('--machine',type=int,default=0);p.add_argument('--time',type=float,default=0);p.add_argument('--file',default='data.unity3d/resources.assets');p.add_argument('--out',type=Path);a=p.parse_args()
    if a.animator is not None:
        if a.controller is None:p.error('--animator requires --controller')
        from tools.verify.l3_recipe import Recipes
        d=probe_state(Recipes(),dict(serialized_file=a.file,path_id=a.animator),dict(serialized_file=a.file,path_id=a.controller),a.machine,a.state,a.time);b=json.dumps(d,indent=2).encode()
        if a.out:a.out.write_bytes(b)
        else:print(b.decode())
        return
    if a.clip is None:
        d=build();b=gzip.compress(json.dumps(d,ensure_ascii=True,separators=(',',':')).encode(),mtime=0);assert len(b)<5_000_000;OUT.write_bytes(b);print(json.dumps(d['counts'],indent=2));return
    from tools.verify.l3_recipe import Recipes
    r=Recipes();m=next(m for m in r.section('motion') if key(m['identity'])==(a.file,a.clip));d=dict(provisional=True,clip=m['identity'],local_time=a.time,scope='Explicit clip coefficient probe, not runtime state selection or rendered pose',properties=probe_channels(m,a.time));b=json.dumps(d,indent=2).encode()
    if a.out:a.out.write_bytes(b)
    else:print(b.decode())
if __name__=='__main__':main()
