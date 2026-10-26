"""Must-value CFG audit of w0 at direct combat stat getters.

All conditional edges are retained, no guessed branch predicates. Unknown calls kill
w0; x0 aliases w0. Unknown register-producing operations kill w0. This is an
intraprocedural proof of an argument on normal paths reaching a call, not execution.
"""
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
from collections import deque

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'reverse-engineering/raw/combat-chain'


def instructions(path):
    rows = {}
    for address, op, operands in re.findall(r'^[ \t]*0x([0-9a-f]+):[ \t]+(\S+)[ \t]*(.*?)$', path.read_text(), re.M):
        item = (op, operands.strip())
        addr = int(address,16)
        assert addr not in rows or rows[addr] == item
        rows[addr] = item
    return rows


def successors(addr, op, operands, body):
    target_match = re.search(r'#0x([0-9a-f]+)$',operands)
    target = int(target_match[1],16) if target_match else None
    if op in ('ret','br'):
        return []
    if op == 'b':
        return [target] if target in body else []
    if op.startswith('b.') or op in ('cbz','cbnz','tbz','tbnz'):
        return [p for p in (target, addr+4) if p in body]
    return [addr+4] if addr+4 in body else []


def transfer(value, op, operands):
    if op in ('bl','blr'):
        return None  # AAPCS64 caller-clobbered x0/w0
    # No comparison/store/branch writes a general-purpose destination operand.
    if op.startswith(('st','b.')) or op in ('cmp','cmn','tst','ccmp','ccmn','b','br','ret','cbz','cbnz','tbz','tbnz','prfm','nop'):
        # A writeback base x0 would change the alias, though current getters do not use it.
        if op.startswith('st') and re.search(r'\[x0(?:, [^\]]+)?\](?:!|,)', operands):
            return None
        return value
    parts = operands.split(',')
    dests = [parts[0].strip()] if parts else []
    if op.startswith('ldp') and len(parts)>1:
        dests.append(parts[1].strip())
    if re.search(r'\[x0(?:, [^\]]+)?\](?:!|,)', operands):
        return None
    if not any(d in ('w0','x0') for d in dests):
        return value
    match = re.fullmatch(r'(w0|x0), (wzr|xzr|#(?:0x[0-9a-f]+|[0-9]+))',operands) if op=='mov' else None
    if not match:
        return None
    return 0 if match[2] in ('wzr','xzr') else int(match[2][1:],0) & ((1<<32)-1)


def must_w0(body, entry):
    """UNREACHABLE is absent from map; None is reachable but unknown.

    Merge keeps a value only when every reached predecessor agrees. Iterate to a
    fixed point including back edges; do not inspect only the textual previous MOV.
    """
    incoming = {entry:None}
    queue = deque([entry])
    while queue:
        at = queue.popleft()
        op, operands = body[at]
        outgoing = transfer(incoming[at],op,operands)
        for nxt in successors(at,op,operands,body):
            if nxt not in incoming:
                incoming[nxt] = outgoing; queue.append(nxt)
            else:
                merged = incoming[nxt] if incoming[nxt] == outgoing else None
                if merged != incoming[nxt]:
                    incoming[nxt] = merged; queue.append(nxt)
    return incoming


def build():
    pack = json.loads(gzip.decompress((ROOT/'datas/combat_chain_contract.json.gz').read_bytes()))
    checked = []
    getters = {'GetMainCannonRate','GetMainCannonDamage','GetWingCannonDamage'}
    for record in pack['methods']:
        if not re.fullmatch(r'Player_Attack_\d+',record['class_name']): continue
        calls = [c for c in record['direct_calls'] if any(d['class_name']=='Player_Get_Datas' and d['method'] in getters
                                                        for d in c['declarations'])]
        if not calls: continue
        path=RAW/'native'/f"{record['class_name']}.asm.txt"
        rows=instructions(path)
        start=int(record['rva'],16); end=start+record['clipped_bytes']
        body={a:i for a,i in rows.items() if start<=a<end}
        assert sorted(body)==list(range(start,end,4)), 'Incomplete instruction span'
        assert not any(op=='br' for op,args in body.values()), 'Computed branch needs target recovery'
        flow=must_w0(body,start)
        for call in calls:
            at=int(call['at'],16)
            checked.append(dict(implementation=record['class_name'],method=record['method'],rva=record['rva'],
                call=call['at'],getters=[d['method'] for d in call['declarations'] if d['class_name']=='Player_Get_Datas'],
                value=flow.get(at),reachable=at in flow,
                status='PROVED_MUST_CONSTANT_ON_ALL_NORMAL_CFG_PATHS_REACHING_CALL' if flow.get(at) is not None else 'NOT_PROVED_BY_THIS_ANALYSIS',
                body_start=hex(start),body_end=hex(end),cfg_nodes=len(body),reachable_nodes=len(flow),
                source=path.relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    rate=[r for r in checked if 'GetMainCannonRate' in r['getters']]
    assert len(rate)==24 and all(r['value']==int(r['implementation'].rsplit('_',1)[1])-1 for r in rate)
    cells=json.loads(gzip.decompress((RAW/'referenced-cells.json.gz').read_bytes()))['cells']
    tiers=[]
    for lo,hi,va in [(1,1,'0x756ecc'),(2,3,'0x756e18'),(4,6,'0x75706c'),(7,8,'0x756c78'),(9,None,'0x756b38')]:
        cell=next(r for r in cells if r['va']==va and r['width']==4)
        tiers.append(dict(min_level=lo,max_level=hi,va=va,hex=cell['hex'],value=struct.unpack('<f',bytes.fromhex(cell['hex']))[0]))
    arrays=json.loads((ROOT/'reverse-engineering/il2cpp/ia-resolved.json').read_text())['methods']['Player_Get_Datas.cctor']
    rate_blob=next(r for r in arrays if r['addr']=='0x14e5eb4')
    assert rate_blob['len']==24 and rate_blob['length_valid']
    rate_values=list(struct.unpack_from('<24f',bytes.fromhex(rate_blob['raw'])))
    span_audit=[]
    for record in pack['methods']:
        if record['exporter_ends_clean']:continue
        path=RAW/'native'/(re.sub(r'[^\w.]','_',record['class_name'])+'.asm.txt')
        rows=instructions(path);start=int(record['rva'],16);end=start+record['clipped_bytes']
        body=sorted((a,op,args) for a,(op,args) in rows.items() if start<=a<end)
        span_audit.append(dict(class_name=record['class_name'],method=record['method'],start=hex(start),end=hex(end),
            last_instruction=dict(at=hex(body[-1][0]),opcode=body[-1][1],operands=body[-1][2]),
            returns=[hex(a) for a,op,args in body if op=='ret'],
            not_supported_ctor_sites=[hex(a) for a,op,args in body if op=='bl' and args=='#0x2107de0'],
            diagnosis='RESET_EXCEPTION_BODY_NOT_A_TRUNCATION_FLAG' if record['method']=='Reset' else 'RET_BEFORE_EXPORTER_LAST12_WINDOW'))
    roots=[]
    for row in pack['collider_roots']:
        if row['receiver_candidates']:continue
        roots.append(dict(serialized_file=row['serialized_file'],component_path_id=row['component_path_id'],
                          reason='SERIALIZED_ROOT_POINTER_NULL' if row['root'] is None else 'ROOT_HAS_NO_MONOBEHAVIOUR',
                          root=row['root']))
    return dict(unclean_span_audit=span_audit,receiver_absence_audit=roots, main_rate_modifier=dict(tech_stat_index=1,tech_getter_rva='0x139d96c',
                percent_getter_rva='0x14e3d6c',rate_getter_rva='0x14e3cd8',tiers=tiers,
                below_level_one_percent=0.0,base_rates=rate_values,base_rates_raw_hex=rate_blob['raw'],
                initialize_array_call='0x14e5eb4',static_array_store='0x14e5ec4',static_field_offset='0x80',
                formula='f32(base_rate[index] * f32(1.0 - percent(Tech_Datas.GetTechStatLevel(1))))'),status='STATIC_ARGUMENT_PROOF_NOT_A_DPS_MODEL',proofs=checked,
                summary=dict(stat_calls=len(checked),proved=sum(r['value'] is not None for r in checked),rate_calls=len(rate)),
                boundaries=['All conditional CFG edges retained; normal returned calls clobber w0.',
                            'No exception execution or cross-method value proof; returned/non-returning helper distinction not guessed.',
                            'Proves argument when the site is reached, not that Awake/SetupDatas ran on a device.',
                            'Body uses preserved contract next-declared-RVA clipping, not every exporter minimum span.'])


if __name__=='__main__':
    result=build()
    (ROOT/'datas/combat_argument_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['summary']))
