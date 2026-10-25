"""APK-static rate-field and scheduler evidence. No observed firing/hit-rate claims."""
import gzip
import hashlib
import json
import re
from collections import deque
from pathlib import Path
from tools.verify.combat_argument_audit import RAW, ROOT, instructions, successors

OUT = ROOT / 'datas/combat_rate_consumers.json'
DUMP = ROOT / 'reverse-engineering/il2cpp/dump.cs.gz'
CONTRACT = ROOT / 'datas/combat_chain_contract.json.gz'


def owner_states(body, entry, iterator_offset=None):
    """Must-alias analysis, normal CFG paths; owner/iterator/unknown only.

    W writes destroy X pointer aliases. Calls clobber x0..x18. The iterator's
    metadata-typed <>4__this field can recover its enclosing attack owner.
    """
    initial = [None] * 31
    initial[0] = 'iterator' if iterator_offset is not None else 'owner'
    incoming = {entry: tuple(initial)}
    todo = deque([entry])
    while todo:
        at = todo.popleft()
        state = list(incoming[at]); op, args = body[at]
        if op in ('bl', 'blr'):
            state[:19] = [None] * 19
        elif not (op.startswith(('st', 'b.')) or op in ('cmp','cmn','tst','ccmp','fcmp','fccmp','b','br','ret','cbz','cbnz','tbz','tbnz','prfm','nop')):
            parts = args.split(','); dests = parts[:2] if op.startswith('ldp') else parts[:1]
            value = None
            m = re.fullmatch(r'x(\d+), x(\d+)', args)
            if op == 'mov' and m:
                value = state[int(m[2])]
            load = re.fullmatch(r'x\d+, \[x(\d+), #0x([0-9a-f]+)\]', args)
            if op == 'ldr' and load and iterator_offset is not None and state[int(load[1])] == 'iterator' and int(load[2],16) == iterator_offset:
                value = 'owner'
            for i, dest in enumerate(dests):
                m = re.fullmatch(r'([xw])(\d+)', dest.strip())
                if m and int(m[2]) < 31:
                    state[int(m[2])] = value if i == 0 and m[1] == 'x' else None
        writeback = re.search(r'\[x(\d+)(?:, [^\]]+)?\](?:!|,)', args)
        if writeback:
            state[int(writeback[1])] = None
        for nxt in successors(at,op,args,body):
            new = tuple(state) if nxt not in incoming else tuple(a if a == b else None for a,b in zip(incoming[nxt],state))
            if incoming.get(nxt) != new:
                incoming[nxt] = new; todo.append(nxt)
    return incoming


def class_text(dump, name):
    m = re.search(r'\bclass ' + re.escape(name) + r'(?=\s|:)[^\S\n]*(?::[^\n]*)?[^\n]*\n\{',dump)
    assert m, name
    return dump[m.end():dump.index('\n}',m.end())]


def fields(text):
    return {int(offset,16): {'name':name,'declaration':decl.strip()} for decl,name,offset in re.findall(r'^([^\n;]*?\s(\S+)); // 0x([0-9A-Fa-f]+)$',text,re.M)}


def build():
    contract = json.loads(gzip.decompress(CONTRACT.read_bytes()))
    dump = gzip.decompress(DUMP.read_bytes()).decode()
    methods = contract['methods']; symbols = {int(m['rva'],16): m['class_name']+'.'+m['method'] for m in methods}
    symbols.update({0x2786dc0:'UnityEngine.Time.get_time',0x278276c:'MonoBehaviour.StartCoroutine(IEnumerator)',0x2786508:'WaitForSeconds..ctor'})
    rows = []; used = {CONTRACT, DUMP}
    base = fields(class_text(dump,'Player_Attack'))
    assert base[0x30]['name'] == 'demo'
    for ship in contract['ships']:
        cls = ship['implementation']; fs = fields(class_text(dump,cls))
        rate = next(k for k,v in fs.items() if v['name'] == 'timeRateMainCannon')
        members = [m for m in methods if m['class_name'] == cls or m['class_name'].startswith(cls+'.')]
        bodies = {}; accesses = []; waits = []; starts = []
        for method in members:
            path = RAW/'native'/(re.sub(r'[^\w.]','_',method['class_name'])+'.asm.txt'); used.add(path)
            all_ins = instructions(path); start = int(method['rva'],16); end = start+method['clipped_bytes']
            body = {a:v for a,v in all_ins.items() if start <= a < end}
            assert set(body) == set(range(start,end,4)), (cls,method)
            nested = method['class_name'] != cls
            offset = None
            if nested:
                nf = fields(class_text(dump,method['class_name']))
                offset = next((k for k,v in nf.items() if v['name'] == '<>4__this'),None)
            states = owner_states(body,start,offset) if not nested or offset is not None else {}
            bodies[(method['class_name'],method['method'],start)] = body
            for a,(op,args) in sorted(body.items()):
                mem = re.search(r'\[x(\d+), #0x([0-9a-f]+)\]',args)
                # This is an owner-qualified access inventory, not offset coincidence.
                widths = {'w':4,'x':8,'s':4,'d':8,'q':16,'v':16,'h':2,'b':1}
                width = widths.get(args[:1],0) * (2 if op.startswith(('ldp','stp')) else 1)
                if op in ('ldrb','strb'): width = 1
                if op in ('ldrh','strh'): width = 2
                if op == 'ldrsw': width = 4
                if mem and op.startswith(('ld','st')) and int(mem[2],16) <= rate < int(mem[2],16)+width and states.get(a,(None,)*31)[int(mem[1])] == 'owner':
                    accesses.append({'method':method['class_name']+'.'+method['method'],'at':hex(a),'op':op,'operands':args,'access_start':hex(int(mem[2],16)),'access_bytes':width})
                if op in ('bl','b') and args in ('#0x2786508','#0x278276c'):
                    record = {'method':method['class_name']+'.'+method['method'],'at':hex(a),'context':[{'at':hex(p),'op':body[p][0],'operands':body[p][1]} for p in range(max(start,a-24),min(end,a+12),4)]}
                    (waits if args == '#0x2786508' else starts).append(record)
        def body_for(name):
            return next(b for (c,m,a),b in bodies.items() if c == cls and m == name)
        setup = body_for('SetupDatas'); call = int(ship['main_rate_consumers'][0]['call']['at'],16)
        tail = {a:v for a,v in setup.items() if call < a <= call+64}
        select = next(a for a,v in tail.items() if v == ('fcsel','s0, s0, s1, eq'))
        compare = max(a for a,v in tail.items() if a<select and v[0] == 'cmp')
        assert tail[compare] == ('cmp','w8, #0')
        assert all(tail[a][0] in ('mov','movk','orr') for a in range(compare+4,select,4))
        demo_read = next(a for a,v in tail.items() if v == ('ldrb','w8, [x19, #0x30]'))
        demo_constant = next(float(args.split('#')[1]) for a,(op,args) in tail.items() if demo_read < a < select and op == 'fmov' and args.startswith('s1, #'))
        store = next(a for a,v in tail.items() if a>select and v == ('str',f's0, [x19, #0x{rate:x}]'))
        assert all(op not in ('bl','blr') for a,(op,args) in setup.items() if call<a<=store)
        main = body_for('MainCannonShoot')
        load = next(a for a,v in main.items() if v == ('ldr',f's1, [x19, #0x{rate:x}]'))
        deadline_store = next(a for a,v in main.items() if load<a<=load+16 and v[0] == 'str' and v[1].startswith('s0, [x19,'))
        assert ('fadd','s0, s0, s1') in [main[a] for a in range(load+4,deadline_store,4)]
        deadline = int(re.search(r'#0x([0-9a-f]+)',main[deadline_store][1])[1],16)
        gate_load = next(a for a,v in main.items() if a<load and v == ('ldr',f's1, [x19, #0x{deadline:x}]'))
        assert main[gate_load-4] == ('bl','#0x2786dc0')
        assert main[gate_load+4] == ('fcmp','s0, s1')
        assert main[gate_load+8][0] in ('b.mi','b.pl')
        extra = any(op == 'cmp' and args == 'w20, #1' for op,args in main.values())
        if extra:
            assert ('add','w8, w8, #1') in main.values()
            assert ('cmp','w8, w9') in main.values()
            assert any(op == 'b.le' and int(args[1:],16) == deadline_store+4 for op,args in main.values())
        start_body = body_for('StartAttack')
        start_load = next(a for a,v in start_body.items() if v == ('ldr',f's1, [x19, #0x{rate:x}]'))
        start_context = [{'at':hex(a),'op':op,'operands':args} for a,(op,args) in sorted(start_body.items()) if start_load-28 <= a <= start_load+24]
        # Record all scheduler instructions, then exact dispatch calls/tail calls.
        prefix = [{'at':hex(a),'op':op,'operands':args} for a,(op,args) in sorted(main.items()) if a<=deadline_store]
        dispatch = [{'at':hex(a),'kind':op,'target':args[1:],'symbol':symbols.get(int(args[1:],16))} for a,(op,args) in sorted(main.items()) if a>deadline_store and op in ('bl','b') and re.fullmatch(r'#0x[0-9a-f]+',args)]
        rows.append({'implementation':cls,'rate_field':{'offset':hex(rate),**fs[rate]},'demo_field':base[0x30], 'setup':{'getter_call':hex(call),'demo_read':hex(demo_read),'demo_constant':demo_constant,'select':hex(select),'store':hex(store)},'rate_accesses':accesses,'deadline_field':{'offset':hex(deadline),**fs[deadline]},'scheduler_kind':'extra_shot_counter' if extra else 'single_deadline','scheduler_fields':{hex(k):v for k,v in fs.items() if any(f'[x19, #0x{k:x}]' in ins['operands'] for ins in prefix)},'scheduler_prefix':prefix,'start_attack_rate_context':start_context,'dispatch':dispatch,'ability_refresh_inside_scheduler':any(v == ('bl','#0x14c7758') for v in main.values()),'wait_for_seconds_sites':waits,'start_coroutine_sites':starts,'nested_move_next':[{'class':m['class_name'],'rva':m['rva']} for m in members if m['class_name'] != cls and m['method']=='MoveNext']})
    return {'status':'PROVISIONAL_APK_STATIC_NOT_MEASURED_CADENCE','scope':'24 implementation fields; owner-qualified accesses in preserved implementation/nested methods; exact scheduler prefixes; WaitForSeconds/StartCoroutine direct-site contexts, NOT full coroutine emission semantics','inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(used)},'ships':rows}


def render():
    return json.dumps(build(),ensure_ascii=False,indent=2)+'\n'

if __name__ == '__main__':
    import sys
    result = render()
    if '--check' in sys.argv:
        assert OUT.read_text() == result, 'stale combat rate consumer evidence'
    else:
        OUT.write_text(result)
    print('24 rate consumers, scheduler prefixes and coroutine site inventory verified')
