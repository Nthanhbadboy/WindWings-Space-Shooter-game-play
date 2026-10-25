"""UI native call/CFG evidence -> serialized receiver -> Animator programs.
No claims that source callsites all execute or that an event/delegate has fired.
"""
import gzip,hashlib,importlib.util,json,tempfile,zlib
from collections import Counter,defaultdict
from pathlib import Path
from tools.verify.l3_chain_graph import ROOT,RAW,key,identity,read_chunks
from tools.verify.l3_native_cfg import interpret
from tools.verify.l3_class_hierarchy import hierarchy,lineage
from tools.verify.combat_rate_consumers import class_text,fields
from tools.verify.l3_animator_programs import load as load_programs
RAW_NATIVE=ROOT/'reverse-engineering/raw/l3-ui-native'
OUT=ROOT/'datas/l3_ui_drivers.json.gz'

def build():
    import capstone
    index=json.loads((RAW_NATIVE/'index.json').read_bytes())
    for f in index['files']:assert hashlib.sha256((RAW_NATIVE/f['path']).read_bytes()).hexdigest()==f['sha256']
    native_blob=(RAW_NATIVE/'method-bytes.json.gz').read_bytes();native=json.loads(gzip.decompress(native_blob));dump_blob=(ROOT/'reverse-engineering/il2cpp/dump.cs.gz').read_bytes();dump=gzip.decompress(dump_blob).decode()
    spec=importlib.util.spec_from_file_location('l3_native_dump',ROOT/'tools/apk-analyze/il2cpp_consts.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    with tempfile.NamedTemporaryFile('w+') as f:f.write(dump);f.flush();decls=mod.parse_dump(f.name)
    declared_names={(ns,cls,name) for cls,ns,name,_,_,_ in decls}
    by_rva=defaultdict(list)
    for cls,ns,name,offset,rva,sig in decls:by_rva[rva].append(dict(namespace=ns,**{'class':cls},method=name,signature=sig))
    literal_blob=(ROOT/'reverse-engineering/il2cpp/stringliteral.json').read_bytes();literals=defaultdict(list)
    for l in json.loads(literal_blob):literals[int(l['address'],16)].append(l['value'])
    relocs={int(r['offset'],16):int(r['addend'],16) for r in native['relocations']};md=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);md.detail=True
    methods=[];semantic={'SetActive','SetTrigger','ResetTrigger','Play','CrossFade','set_sprite','set_text','set_color','set_localScale','set_localPosition','SetPopup','OnPressedButtonExit','OffBoard','ObjectAnchor'}
    for m in native['methods']:
        instructions=[]
        for i in md.disasm(bytes.fromhex(m['hex']),int(m['va'],16)):
            instructions.append(dict(pc=i.address,mnemonic=i.mnemonic,op_str=i.op_str,writes=[i.reg_name(r) for r in i.regs_access()[1]]))
        cfg=interpret(instructions,by_rva,relocs,literals,static=' static ' in m['signature'])
        calls=[c for c in cfg['calls'] if any(d['method'] in semantic for d in c['declarations'])]
        methods.append(dict(cls=m['cls'],namespace=m['namespace'],method=m['method'],signature=m['signature'],rva=m['va'],width=m['width'],bytes_sha256=hashlib.sha256(bytes.fromhex(m['hex'])).hexdigest(),decoded_bytes=len(instructions)*4,span_decode_status='complete' if len(instructions)*4==m['width'] else 'stopped_before_span_end',cfg=cfg,appearance_calls=calls))
    source_index=json.loads((RAW/'index.json').read_bytes());classes=set(index['classes']);instances=[];parents=hierarchy(dump);script_types={}
    from tools.verify.l3_recipe import Recipes
    callbacks=Recipes().section('callbacks');event_gaps=[c for c in callbacks if 'receiver_candidates' in c and not c['receiver_candidates']];wanted_go={key(c['gameobject']) for c in event_gaps};components=defaultdict(list)
    for r in read_chunks(source_index,'objects'):
        if r['type']=='MonoBehaviour':script_types[key(r)]=(r.get('namespace',''),r.get('class_name',''))
        if r['type']=='MonoBehaviour' and any(c in classes for ns,c in lineage(script_types[key(r)],parents)):
            instances.append(dict(identity=identity(key(r)),class_name=r['class_name'],namespace=r.get('namespace',''),enabled=r.get('header',{}).get('m_Enabled'),raw_object_sha256=r['raw_object_sha256']))
    owners={key(i['identity']) for i in instances};refs={}
    for l in read_chunks(source_index,'links'):
        if l['status']=='resolved' and key(l['owner']) in wanted_go and l['location'].startswith('.m_Component['):components[key(l['owner'])].append(l['target'])
        if key(l['owner']) in owners and l['status']=='resolved':refs[(key(l['owner']),l['location'])]=l['target']
    field_maps={}
    for cls in {c for i in instances for ns,c in lineage((i['namespace'],i['class_name']),parents)}:
        try:field_maps[cls]=fields(class_text(dump,cls))
        except (ValueError,AssertionError):field_maps[cls]={}
    instance_map={key(i['identity']):i for i in instances}
    def resolve(expr,instance):
        if not expr:return None
        if expr['kind']=='this':return instance['identity']
        if expr['kind']=='component_gameobject':
            c=resolve(expr['component'],instance);return refs.get((key(c),'.m_GameObject')) if c else None
        if expr['kind']=='field':
            base=resolve(expr['base'],instance)
            if base:
                owner=instance_map.get(key(base));field=next((field_maps.get(c,{}).get(expr['offset']) for ns,c in lineage((owner['namespace'],owner['class_name']),parents) if field_maps.get(c,{}).get(expr['offset'])),None) if owner else None
                if field:return refs.get((key(base),'.'+field['name']))
        return None
    programs=load_programs();attachments={key(a['animator']):a for a in programs['animator_attachments']};controllers={key(c['identity']):c for c in programs['controllers']};joined=[]
    for instance in instances:
        for mi,m in enumerate(methods):
            ancestry=lineage((instance['namespace'],instance['class_name']),parents)
            declared=(m['namespace'],m['cls'])
            if declared not in ancestry:continue
            before=ancestry[:ancestry.index(declared)]
            for call in m['appearance_calls']:
                receiver=resolve(call['arguments'][0],instance);argument=call['arguments'][1];routes=[]
                for d in call['declarations']:
                    if d['class']=='Animator' and receiver and key(receiver) in attachments and argument:
                        values=argument.get('values',[]) if argument['kind']=='literal' else [argument['value']] if argument['kind']=='integer' else []
                        for value in values:
                            h=zlib.crc32(value.encode()) if isinstance(value,str) else value
                            for cid in attachments[key(receiver)]['controllers']:
                                program=controllers.get(key(cid))
                                if not program:continue
                                for sm in program['machines']:
                                    if d['method'] in ('SetTrigger','ResetTrigger'):
                                        for tr in sm['any_state_transitions']+[t for s in sm['states'] for t in s['transitions']]:
                                            if any(c['raw']['m_EventID']==h for c in tr['conditions']):routes.append(dict(controller=cid,machine_index=sm['machine_index'],parameter_value=value,transition=tr,kind='matching_parameter_condition_not_transition_execution'))
                                    elif d['method'] in ('Play','CrossFade'):
                                        for state in sm['states']:
                                            if h in (state['raw']['m_NameID'],state['raw']['m_FullPathID']):routes.append(dict(controller=cid,machine_index=sm['machine_index'],state_index=state['state_index'],state_names=state['name_candidates'],kind='name_hash_state_candidate_not_runtime_execution'))
                joined.append(dict(owner=instance['identity'],class_name=instance['class_name'],method_index=mi,method=m['method'],callsite=hex(call['pc']),target_rva=hex(call['target_rva']) if call['target_rva'] is not None else None,declarations=call['declarations'],receiver=receiver,argument=argument,animator_routes=routes,status='resolved_serialized_receiver' if receiver else 'receiver_not_statically_resolved'))
    inherited_events=[]
    for event in event_gaps:
        candidates=[]
        for component in components[key(event['gameobject'])]:
            qualified=script_types.get(key(component))
            if not qualified:continue
            ancestry=lineage(qualified,parents)
            for ns,c in ancestry[1:]:
                found=[dict(namespace=ns,cls=c,name=name,rva=hex(rva),signature=sig) for cls,namespace,name,_,rva,sig in decls if (namespace,cls)==(ns,c) and name==event['event']['functionName']]
                if found:candidates.append(dict(component=component,declared_in=dict(namespace=ns,cls=c),methods=found));break
        inherited_events.append(dict(owner=event['owner'],clip=event['clip'],event=event['event'],candidates=candidates,status='base_declared_candidate_not_runtime_delivery' if candidates else 'no_base_declared_candidate'))
    effects_by_owner_method=defaultdict(list)
    for ei,e in enumerate(joined):effects_by_owner_method[(key(e['owner']),methods[e['method_index']]['rva'])].append(ei)
    for e in joined:
        e['direct_callee_effect_indices']=effects_by_owner_method.get((key(e['receiver']),e['target_rva']),[]) if e['receiver'] else []
    inherited_by_event={(key(e['owner']),key(e['clip']),json.dumps(e['event'],sort_keys=True)):e for e in inherited_events}
    entries=[]
    for ci,cb in enumerate(callbacks):
        receivers=[]
        if 'call' in cb and cb.get('target'):
            receivers=[dict(component=cb['target'],methods=cb['method_candidates'])]
        elif 'receiver_candidates' in cb:
            receivers=list(cb['receiver_candidates'])
            inherited=inherited_by_event.get((key(cb['owner']),key(cb['clip']),json.dumps(cb['event'],sort_keys=True)))
            if inherited:receivers.extend(inherited['candidates'])
        indices=[]
        for receiver in receivers:
            for method in receiver['methods']:indices.extend(effects_by_owner_method.get((key(receiver['component']),method['rva']),[]))
        if indices:entries.append(dict(callback_index=ci,owner=cb['owner'],kind='animation_event' if 'event' in cb else 'persistent_call',effect_indices=sorted(set(indices)),status='source_target_join_not_callback_invocation'))
    counts=dict(callback_entries=len(entries),direct_callee_links=sum(len(e['direct_callee_effect_indices']) for e in joined),inherited_event_candidates=sum(bool(e['candidates']) for e in inherited_events),methods=len(methods),instances=len(instances),appearance_call_instances=len(joined),receiver_status=dict(Counter(j['status'] for j in joined)),animator_routes=sum(len(j['animator_routes']) for j in joined))
    return dict(schema=1,provisional=True,scope='Conservative register CFG and native callsite-to-serialized-receiver join. Branch graph retained; calls are potential effects, not a trace. Unknown branch merges, indirect delegates, unsupported instructions and runtime-added objects are NOT guessed.',inputs=dict(native_index_sha256=hashlib.sha256((RAW_NATIVE/'index.json').read_bytes()).hexdigest(),native_bytes_sha256=hashlib.sha256(native_blob).hexdigest(),dump_sha256=hashlib.sha256(dump_blob).hexdigest(),literal_sha256=hashlib.sha256(literal_blob).hexdigest(),scene_index_sha256=hashlib.sha256((RAW/'index.json').read_bytes()).hexdigest(),program_sha256=hashlib.sha256((ROOT/'datas/l3_animator_programs.json.gz').read_bytes()).hexdigest(),tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),hierarchy_tool_sha256=hashlib.sha256((ROOT/'tools/verify/l3_class_hierarchy.py').read_bytes()).hexdigest(),cfg_tool_sha256=hashlib.sha256((ROOT/'tools/verify/l3_native_cfg.py').read_bytes()).hexdigest()),counts=counts,declared_field_offsets={c:{str(offset):field for offset,field in offsets.items()} for c,offsets in sorted(field_maps.items())},instances=instances,methods=methods,effects=joined,callback_entries=entries,inherited_events=inherited_events)

def load():
    d=json.loads(gzip.decompress(OUT.read_bytes()))
    assert d['inputs']['program_sha256']==hashlib.sha256((ROOT/'datas/l3_animator_programs.json.gz').read_bytes()).hexdigest()
    assert d['inputs']['scene_index_sha256']==hashlib.sha256((RAW/'index.json').read_bytes()).hexdigest()
    return d

if __name__=='__main__':
    d=build();b=gzip.compress(json.dumps(d,ensure_ascii=True,separators=(',',':')).encode(),mtime=0);assert len(b)<5_000_000;OUT.write_bytes(b);print(json.dumps(d['counts'],indent=2))
