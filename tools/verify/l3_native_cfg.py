"""Conservative AArch64 register dataflow. Unknown joins stay unknown.
Only the listed transfer functions are interpreted; no execution of native/engine code.
"""
from collections import deque
import re

def reg(name):
    if name in ('xzr','wzr'):return 'zero'
    return 'x'+name[1:] if re.fullmatch('[xw][0-9]+',name) else name

def interpret(instructions,decls,relocations,literals,static=False):
    bypc={i['pc']:i for i in instructions};pcs=sorted(bypc);nextpc={a:b for a,b in zip(pcs,pcs[1:])};states={pcs[0]:{'x'+str(i):dict(kind='this' if i==0 and not static else 'argument',index=i) for i in range(8)}} if pcs else {};queue=deque(states);calls={};edges=set();iterations=0;branches={}
    def value(token,state):
        if token.startswith('#'):
            try:return dict(kind='integer',value=int(token[1:],0))
            except ValueError:return None
        return dict(kind='integer',value=0) if reg(token)=='zero' else state.get(reg(token))
    def target_names(pc):return decls.get(pc,[])
    while queue:
        pc=queue.popleft();iterations+=1
        if iterations>200000:raise ValueError('CFG iteration budget; no silent truncation')
        i=bypc[pc];mn=i['mnemonic'];op=i['op_str'];parts=[v.strip() for v in op.split(',')];s=dict(states[pc]);fall=nextpc.get(pc);successors=[];dest=None
        try:dest=int(parts[-1].lstrip('#'),0) if mn in ('b','bl','cbz','cbnz','tbz','tbnz') or mn.startswith('b.') else None
        except ValueError:pass
        if mn in ('cbz','cbnz','tbz','tbnz') or mn.startswith('b.'):
            branches[pc]=dict(**i,symbolic_operand=value(parts[0],s) if mn in ('cbz','cbnz','tbz','tbnz') else s.get('nzcv'))
        iscall=mn in ('bl','blr','br') or mn=='b' and dest not in bypc
        if iscall:
            arguments=[s.get('x'+str(n)) for n in range(8)];declarations=target_names(dest)
            calls[pc]=dict(pc=pc,instruction=mn,target_rva=dest,declarations=declarations,arguments=arguments,indirect_register=op if mn in ('blr','br') else None)
            returned=None
            if declarations and all(d['method']=='get_gameObject' and d['class']=='Component' and d['namespace']=='UnityEngine' for d in declarations):returned=dict(kind='component_gameobject',component=arguments[0]) if arguments[0] else None
            if declarations and all(d['method']=='get_transform' and d['class'] in ('Component','GameObject') and d['namespace']=='UnityEngine' for d in declarations):returned=dict(kind='component_transform',component=arguments[0]) if arguments[0] else None
            s.pop('nzcv',None)
            for n in range(19):s.pop('x'+str(n),None)
            if returned:s['x0']=returned
        elif mn in ('mov','movz') and len(parts)>=2:
            v=value(parts[1],s)
            if v is not None and len(parts)==2:s[reg(parts[0])]=v
            else:s.pop(reg(parts[0]),None)
        elif mn=='cmp' and len(parts)==2:
            s['nzcv']=dict(kind='comparison',left=value(parts[0],s),right=value(parts[1],s))
        elif mn=='adrp':
            s[reg(parts[0])]=dict(kind='address',value=int(parts[1].lstrip('#'),0))
        elif mn in ('add','sub') and len(parts)==3:
            a=value(parts[1],s);b=value(parts[2],s);v=None
            if a and b and a['kind'] in ('integer','address') and b['kind']=='integer':v=dict(kind=a['kind'],value=a['value']+(1 if mn=='add' else -1)*b['value'])
            if v:s[reg(parts[0])]=v
            else:s.pop(reg(parts[0]),None)
        elif mn.startswith('ldr') or mn=='ldur':
            match=re.search(r'\[([xw][0-9]+)(?:, #(-?0x[0-9a-f]+|-?[0-9]+))?\]',op);v=None
            if match:
                base=s.get(reg(match[1]));offset=int(match[2] or '0',0)
                if base and base['kind']=='address':
                    addr=base['value']+offset
                    if addr in relocations:v=dict(kind='metadata_slot',address=relocations[addr],got=addr)
                    elif addr in literals:v=dict(kind='literal',address=addr,values=literals[addr])
                elif base and base['kind']=='metadata_slot' and not offset:
                    if base['address'] in literals:v=dict(kind='literal',address=base['address'],values=literals[base['address']])
                elif base and base['kind'] in ('this','field') and len(str(base))<700:v=dict(kind='field',base=base,offset=offset)
            if v:s[reg(parts[0])]=v
            else:s.pop(reg(parts[0]),None)
        else:
            # Capstone supplies explicit and implicit writes. Unsupported instructions kill them.
            for written in i.get('writes',[]):s.pop(reg(written),None)
        if mn=='b':
            if dest in bypc:successors=[dest]
        elif mn=='ret' or mn=='br':successors=[]
        elif mn in ('cbz','cbnz','tbz','tbnz') or mn.startswith('b.'):
            successors=[p for p in (dest,fall) if p in bypc]
        elif fall is not None:successors=[fall]
        for dst in successors:
            edges.add((pc,dst))
            if dst not in states:states[dst]=dict(s);queue.append(dst)
            else:
                merged={k:v for k,v in states[dst].items() if k in s and v==s[k]}
                if merged!=states[dst]:states[dst]=merged;queue.append(dst)
    return dict(calls=[calls[k] for k in sorted(calls)],edges=[list(e) for e in sorted(edges)],reachable_instructions=len(states),iterations=iterations,branches=[branches[k] for k in sorted(branches)])
