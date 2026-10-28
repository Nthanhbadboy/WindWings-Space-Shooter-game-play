#!/usr/bin/env python3
"""Report 183: where the `{0}` of every Firebase path actually comes from.

182 printed the text of 27 path fragments and 19 templates but left one question
open — *which root supplies `{0}`*, and where `/playerChats` / `/playerScores` /
`/profile/pvpDatas` / `/start` hang. This tool answers it per call site by a
bounded (one `mov` hop, 24-instruction window) back-trace of the register that
carries the format/concat argument, and labels the source:

* `call:<name>`   — the argument is the return value of a method call, e.g.
                    `PVP_Manager.get_pathRoot` (19859292);
* `cell:<text>`   — the argument to concatenate is itself a resolved string cell;
* `field:0x<off>`  — the argument is read out of an object/closure field, so the
                    base was built by whoever wrote that field;
* `constant` / `register` / `unknown` — the honest remainder.

Every row keeps the call RVA and the operand register, so a reader can re-walk
the same instructions. Nothing is inferred from method names.

The worked chain that the report leans on is measured end to end:

    Board_RoomPVP.<IECreateRoom>d__13 (21267840)
      21270116  bl   PVP_Manager.get_pathRoot      -> "data-leagues"
      21270160  bl   String.Format("{0}/data-solos/{1}", root, roomId)
      21270168  str  x0, [x21, #0x20]              -> closure field 0x20
    Board_RoomPVP.<>c__DisplayClass13_0.<IECreateRoom>b__2 (21264984)
      21265220  bl   Query([x19, #0x20])
      21265336  bl   String.Concat([x19, #0x20], "/playerChats")
      21265464  bl   String.Concat([x19, #0x20], "/playerScores")

so the PvP room channels are `data-leagues/data-solos/<room>/playerChats` and
`.../playerScores`. Static only; the room id and every served value stay
`MODEL_NOT_MEASURED runtime`.
"""
import argparse
import gzip
import hashlib
import json
import re
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import firebase_cell as FC  # noqa: E402
import firebase_paths as FP  # noqa: E402

DUMP = FC.DUMP
WINDOW = 24

ROOT_GETTERS = {
    19859292: 'PVP_Manager.get_pathRoot',
    22685676: 'ArenaManager.get_pathRoot',
    19887544: 'PVP_Manager.get_pathOfDataUsers',
    19874728: 'PVP_Manager.get_pathOfDataRanks',
    19915052: 'PVP_Manager.get_pathOfDataPlayOfUsers',
    19915784: 'PVP_Manager.get_pathOfDataPlayOfMachines',
    19915932: 'PVP_Manager.get_pathOfDataConfigs',
}

ROOM_CHAIN = dict(
    producer=21267840,
    consumer=21264984,
    root_call=21270116,
    format_call=21270160,
    field_store=21270168,
    field=0x20,
    query_call=21265220,
    concat_calls=[21265336, 21265464],
)


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def methods():
    return FP.firebase_methods()


@lru_cache(maxsize=None)
def string_helpers():
    return FP.string_helpers()


def cell_before(code, index, reg):
    """Find the cell VA whose value is in `reg` at `index` (adrp+ldr pair)."""
    for position in range(index - 1, max(-1, index - 12), -1):
        insn = code[position]
        if insn['mnemonic'] != 'adrp':
            continue
        found = re.fullmatch(r'(x\d+), #(0x[0-9a-f]+)', insn.get('op_str') or '')
        if not found or found.group(1) != reg:
            continue
        page = int(found.group(2), 16)
        for follow in code[position + 1:position + 6]:
            read = re.fullmatch(r'%s, \[%s(?:, #(0x[0-9a-f]+))?\]' % (reg, reg),
                                follow.get('op_str') or '')
            if follow['mnemonic'] == 'ldr' and read:
                return page + (int(read.group(1), 16) if read.group(1) else 0)
    return None


def source_of(code, index, reg, hops=1):
    """Bounded back-trace: what wrote `reg` before instruction `index`?"""
    for position in range(index - 1, max(-1, index - WINDOW), -1):
        insn = code[position]
        op = insn.get('op_str') or ''
        mnemonic = insn['mnemonic']
        if mnemonic == 'bl' and reg == 'x0':
            target = FC.calls(insn and dict(instructions=[insn]) or {}, {})
            operand = op.strip()
            if re.fullmatch(r'#0x[0-9a-f]+', operand):
                rva = int(operand.lstrip('#'), 16)
                return dict(kind='call', rva=rva, at=insn['rva'],
                            name=ROOT_GETTERS.get(rva) or FP.FC.rva_index().get(rva, (None,))[0])
        dest = op.split(',')[0].strip() if op else ''
        if dest != reg:
            continue
        if mnemonic == 'mov':
            rest = op.split(',', 1)[1].strip()
            if rest in ('xzr',) or re.fullmatch(r'w\d+', rest):
                return dict(kind='constant', text=rest, at=insn['rva'])
            if re.fullmatch(r'x\d+', rest) and hops:
                inner = source_of(code, position, rest, hops - 1)
                inner['via'] = 'mov %s <- %s' % (reg, rest)
                return inner
            return dict(kind='register', text=op, at=insn['rva'])
        if mnemonic == 'ldr':
            read = re.fullmatch(r'(x\d+), \[(x\d+)(?:, #(0x[0-9a-f]+))?\]', op)
            if not read:
                return dict(kind='unknown', text=op, at=insn['rva'])
            base, offset = read.group(2), read.group(3)
            if offset:
                return dict(kind='field', offset=int(offset, 16), base=base,
                            at=insn['rva'], text=op)
            cell = cell_before(code, position, base)
            if cell is not None:
                found = FP.resolve(cell)
                if found and found['kind'] == 'string':
                    return dict(kind='cell', value=found['value'], cell=cell,
                                cell_decimal=cell, at=insn['rva'])
                if found:
                    return dict(kind='metadata', value=found['value'], cell=cell,
                                cell_decimal=cell, at=insn['rva'])
            return dict(kind='unknown', text=op, at=insn['rva'])
        if mnemonic in ('adrp', 'add'):
            return dict(kind='unknown', text=op, at=insn['rva'])
        return dict(kind='unknown', text=op, at=insn['rva'])
    return dict(kind='unknown', text='no writer in window', at=None)


def array_element_zero(code, index, array_reg):
    """`{0}` of a `String.Format(string, object[])` call: element 0 of the array.

    IL2CPP puts the array data at `+0x20`, so element 0 of the `object[]` is the
    last store to `[array_reg, #0x20]` before the call. Only that one element is
    traced — enough to answer *who supplies `{0}`*, which is the question here.
    """
    for position in range(index - 1, max(-1, index - 60), -1):
        insn = code[position]
        op = insn.get('op_str') or ''
        if insn['mnemonic'] != 'str':
            continue
        store = re.fullmatch(r'(x\d+), \[(x\d+), #0x20\]', op)
        if not store or store.group(2) != array_reg:
            continue
        return dict(source_of(code, position, store.group(1)),
                    via='array[0] of %s' % array_reg, array_store=insn['rva'])
    return None


def mov_source(code, index, reg):
    for position in range(index - 1, max(-1, index - 8), -1):
        insn = code[position]
        op = insn.get('op_str') or ''
        if insn['mnemonic'] == 'mov':
            found = re.fullmatch(r'%s, (x\d+)' % reg, op)
            if found:
                return found.group(1)
        if (insn.get('op_str') or '').split(',')[0].strip() == reg:
            return None
    return None


def call_sites(method):
    """Every String.Format / String.Concat call, with both operand sources."""
    code = method['instructions']
    out = []
    for position, insn in enumerate(code):
        if insn['mnemonic'] != 'bl':
            continue
        operand = (insn.get('op_str') or '').strip()
        if not re.fullmatch(r'#0x[0-9a-f]+', operand):
            continue
        rva = int(operand.lstrip('#'), 16)
        kind = string_helpers().get(rva)
        if kind not in ('String.Format', 'String.Concat'):
            continue
        args = {'x0': source_of(code, position, 'x0'),
                'x1': source_of(code, position, 'x1'),
                'x2': source_of(code, position, 'x2'),
                'x3': source_of(code, position, 'x3')}
        if kind == 'String.Format' and args['x1']['kind'] in ('register', 'unknown'):
            array_reg = mov_source(code, position, 'x1')
            if array_reg:
                element = array_element_zero(code, position, array_reg)
                if element and element['kind'] in ('call', 'cell', 'field', 'constant'):
                    args['array0'] = element
        out.append(dict(rva=insn['rva'], call=kind, callee=rva, args=args))
    return out


def literal_rows(sites):
    """Per literal: the base each consuming call supplies, and how it was built."""
    rows = {}
    for site in sites:
        args = site['args']
        literals = [(reg, arg) for reg, arg in args.items()
                    if arg['kind'] == 'cell' and ('/' in arg['value'] or '{' in arg['value'])]
        others = [(reg, arg) for reg, arg in args.items()
                  if not (arg['kind'] == 'cell' and ('/' in arg['value'] or '{' in arg['value']))]
        for reg, literal in literals:
            entry = rows.setdefault(literal['value'], dict(
                value=literal['value'], cell=literal['cell'],
                cell_decimal=literal['cell'], uses=[]))
            preferred = next((arg for reg, arg in others if reg == 'array0'), None)
            base = preferred or (others[0][1] if others else dict(kind='none'))
            base_reg = 'array0' if preferred else (others[0][0] if others else None)
            entry['uses'].append(dict(
                call=site['call'], call_rva=site['rva'], arg_reg=reg,
                base_reg=base_reg,
                base_kind=base['kind'],
                base_name=base.get('name') or base.get('value'),
                base_rva=base.get('rva'), base_offset=base.get('offset'),
                base_at=base.get('at')))
    return [rows[key] for key in sorted(rows)]


def room_chain():
    producer = methods()[ROOM_CHAIN['producer']]
    consumer = methods()[ROOM_CHAIN['consumer']]
    sites = call_sites(producer)
    fmt = [site for site in sites if site['rva'] == ROOM_CHAIN['format_call']]
    assert len(fmt) == 1, fmt
    fmt = fmt[0]
    assert fmt['call'] == 'String.Format', fmt
    assert fmt['args']['x1']['kind'] == 'call', fmt['args']['x1']
    assert fmt['args']['x1']['rva'] == 19859292, fmt['args']['x1']
    assert fmt['args']['x1']['at'] == ROOM_CHAIN['root_call'], fmt['args']['x1']
    template_arg = [arg for arg in fmt['args'].values()
                    if arg['kind'] == 'cell' and '{' in arg.get('value', '')]
    assert len(template_arg) == 1, fmt['args']
    template = template_arg[0]['value']
    assert template == '{0}/data-solos/{1}', template

    stores = [insn for insn in producer['instructions']
              if insn['rva'] == ROOM_CHAIN['field_store']]
    assert stores and stores[0]['mnemonic'] == 'str', stores
    assert (stores[0].get('op_str') or '').endswith('#0x20]'), stores[0]

    consumer_sites = call_sites(consumer)
    appended = []
    for site in consumer_sites:
        args = site['args']
        if site['call'] != 'String.Concat':
            continue
        literal = [arg for arg in args.values() if arg['kind'] == 'cell']
        base = [arg for arg in args.values() if arg['kind'] == 'field']
        if literal and base:
            appended.append(dict(concat_rva=site['rva'],
                                 literal=literal[0]['value'],
                                 base_field=base[0]['offset'],
                                 base_at=base[0]['at']))
    assert appended, consumer_sites
    queries = [insn['rva'] for insn in consumer['instructions']
               if insn['mnemonic'] == 'bl'
               and (insn.get('op_str') or '').strip() == '#0x%x' % 21152032]
    assert ROOM_CHAIN['query_call'] in queries, queries
    return dict(
        producer=dict(rva=ROOM_CHAIN['producer'],
                      class_name=producer['class_name'],
                      signature=producer['signature'].strip(),
                      root_call=fmt['args']['x1']['rva'],
                      root_name=fmt['args']['x1']['name'],
                      format_call=fmt['rva'],
                      template=template,
                      template_cell=template_arg[0]['cell'],
                      template_cell_decimal=template_arg[0]['cell'],
                      room_arg=fmt['args']['x2']['kind'],
                      field_store=ROOM_CHAIN['field_store'],
                      field=ROOM_CHAIN['field'],
                      rule='`String.Format("{0}/data-solos/{1}", '
                           'PVP_Manager.get_pathRoot(), roomId)` and the result is '
                           'stored into closure field 0x20'),
        consumer=dict(rva=ROOM_CHAIN['consumer'],
                      class_name=consumer['class_name'],
                      signature=consumer['signature'].strip(),
                      query_calls=queries,
                      concat_sites=appended,
                      rule='the closure field 0x20 is the base: `Query(base)` then '
                           '`Query(String.Concat(base, "/playerChats" | '
                           '"/playerScores"))`'),
        verdict=dict(room_base='data-leagues/data-solos/<roomId>',
                     channels=['data-leagues/data-solos/<roomId>/playerChats',
                               'data-leagues/data-solos/<roomId>/playerScores'],
                     note='the room id is runtime state — MODEL_NOT_MEASURED runtime'),
    )


def census():
    scanned = methods()
    rows = []
    for rva in sorted({row['rva'] for row in FC.census()[0]}):
        method = scanned[rva]
        sites = call_sites(method)
        rows.append(dict(
            rva=rva, class_name=method['class_name'],
            signature=method['signature'].strip(), size=method['size'],
            root_calls=sorted({ROOT_GETTERS[site['callee']] for site in
                               (dict(callee=arg.get('rva')) for site in sites
                                for arg in site['args'].values())
                               if site['callee'] in ROOT_GETTERS}),
            format_calls=len([site for site in sites if site['call'] == 'String.Format']),
            concat_calls=len([site for site in sites if site['call'] == 'String.Concat']),
            sites=[dict(call=site['call'], rva=site['rva'],
                        args={reg: {key: arg[key] for key in
                                    ('kind', 'value', 'name', 'offset', 'rva',
                                     'cell', 'at')
                                    if key in arg}
                              for reg, arg in site['args'].items()})
                   for site in sites],
        ))
    return rows


def build_payload():
    rows = census()
    assert len(rows) == 34, len(rows)

    sites = [site for row in rows for site in row['sites']]
    literals = literal_rows([dict(args=site['args'], call=site['call'], rva=site['rva'])
                             for site in sites])
    by_value = {row['value']: row for row in literals}
    assert len(literals) >= 19, len(literals)

    # the two channels 182 could not place: both hang off a closure field
    chats = by_value['/playerChats']
    scores = by_value['/playerScores']
    assert chats['uses'] and all(use['base_kind'] == 'field' for use in chats['uses']), chats
    assert scores['uses'] and all(use['base_kind'] == 'field' for use in scores['uses']), scores

    # the four questions 182 left open, answered where the trace reaches
    is_open = by_value['/is-open']
    assert [use['base_name'] for use in is_open['uses']] == \
        ['ArenaManager.get_pathRoot'], is_open
    user_list = by_value['/user-datas/userList/']
    assert all(use['base_name'] == 'ArenaManager.get_pathRoot' for use in user_list['uses'])
    assert len(user_list['uses']) == 4, user_list
    summary = by_value['{0}/summary-datas/season-{1}/rank-{2}/rooms/roomList/room-{3}']
    assert [use['base_name'] for use in summary['uses']] == \
        ['ArenaManager.get_pathRoot'], summary
    assert [use['base_reg'] for use in summary['uses']] == ['array0'], summary
    machines = by_value['{0}/rank-{1}/map-{2}/{3}']
    assert [use['base_name'] for use in machines['uses']] == \
        ['PVP_Manager.get_pathOfDataPlayOfMachines'], machines
    solos = by_value['{0}/data-solos/{1}']
    call_bases = sorted({use['base_name'] for use in solos['uses']
                         if use['base_kind'] == 'call'})
    assert 'PVP_Manager.get_pathRoot' in call_bases, solos
    assert any(use['base_kind'] == 'cell' and use['base_name'] == 'data-leagues'
               for use in solos['uses']), solos

    bases = {}
    for row in literals:
        for use in row['uses']:
            bases[use['base_kind']] = bases.get(use['base_kind'], 0) + 1
    assert bases == {'call': 17, 'field': 7, 'cell': 2, 'register': 18,
                     'unknown': 8}, bases

    chain = room_chain()
    assert chain['producer']['root_name'] == 'PVP_Manager.get_pathRoot', chain
    per_method = [dict(rva=row['rva'], class_name=row['class_name'],
                       root_calls=row['root_calls'],
                       format_calls=row['format_calls'],
                       concat_calls=row['concat_calls']) for row in rows]

    raw_meta = [dict(path=path, sha256=sha_file(path)) for path in FC.raw_paths()]
    blob = FC.load(next(path for path in FC.raw_paths() if 'arena-pvp' in path))
    return dict(
        schema=1,
        evidence='STATIC_ONLY_ORIGINAL_APK',
        note='Bases are read by a bounded (one `mov` hop, 24-instruction) back-trace '
             'of the format/concat argument registers; the room id and every served '
             'value are MODEL_NOT_MEASURED runtime.',
        provenance=dict(
            xapk_sha256=blob['xapk_sha256'],
            libil2cpp_sha256=blob['libil2cpp_sha256'],
            dump_sha256=blob['dump_sha256'],
            sources=[
                dict(path=FP.RELOCATIONS, sha256=sha_file(FP.RELOCATIONS),
                     role='cell VA -> pointer target VA, for the literal operands'),
                dict(path=FP.METADATA_INDEX, sha256=sha_file(FP.METADATA_INDEX),
                     role='pointer target -> ScriptString value / ScriptMetadata name'),
                dict(path=DUMP, sha256=sha_file(DUMP),
                     role='RVA -> declaring class and signature for every callee'),
                *[dict(path=row['path'], sha256=row['sha256'],
                       role='pinned methods whose argument registers are traced')
                  for row in raw_meta],
            ]),
        method=dict(window=WINDOW, hops=1,
                    labels={name: meaning for name, meaning in (
                        ('call', 'the argument is the return value of a call (named '
                                 'when the RVA is one of the seven root getters)'),
                        ('cell', 'the argument is another resolved string cell'),
                        ('field', 'the argument is read out of an object/closure field, '
                                  'so the base was built by whoever wrote that field'),
                        ('constant', 'xor/xzr — an immediate'),
                        ('register', 'a register we could not attribute'),
                        ('unknown', 'no writer inside the window'),
                    )},
                    caveat='a bounded trace is not a proof of absence: `unknown` means '
                           '"not resolved here", never "does not exist"'),
        room_chain=chain,
        literals=literals,
        base_summary=bases,
        census=dict(methods=len(rows), rows=per_method,
                    note='`census.rows` keeps the per-method counts and the operand '
                         'labels of every format/concat call in that method'),
        audit_corroboration=dict(
            item=53,
            claim='`data-leagues/data-configs` and `arena---datas/is-open` live in the '
                  'Firebase database',
            here=dict(is_open_base=[use['base_name'] for use in is_open['uses']],
                      room_channel_base='data-leagues/data-solos/<roomId>'),
            verdict='still RUNTIME: this report places the channels, it does not read '
                    'the served payload'),
        not_decoded=[
            dict(item='the writers of every `field:` base',
                 blocking='a closure field can be written in another method; only the '
                          'room chain is followed to its writer here'),
            dict(item='the remaining 26 of 52 uses (`register` 18 + `unknown` 8)',
                 blocking='those `{0}` values sit in an `object[]` element or a '
                          'register the 24-instruction window cannot attribute; the '
                          'array[0] trace only reaches 3 sites here — UNKNOWN, not '
                          'missing'),
            dict(item='`/profile/pvpDatas`, `/start`, `/playerScores/` bases',
                 blocking='field 0x48 / a String call / a String call — named but the '
                          'writer is in another method'),
            dict(item='the room id and every number substituted into the paths',
                 blocking='runtime state — MODEL_NOT_MEASURED runtime'),
        ],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_path_bases.json.gz')
    args = parser.parse_args()
    payload = build_payload()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                                sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          methods=payload['census']['methods'],
                          literals=len(payload['literals']),
                          bases=payload['base_summary'])))


if __name__ == '__main__':
    main()
