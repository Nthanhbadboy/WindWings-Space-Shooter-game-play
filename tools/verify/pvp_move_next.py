#!/usr/bin/env python3
"""Report 172: one false positive in 169, and what `d__78.MoveNext` really is.

169 listed `Board_PVP`'s array readers by matching `[xN, #offset]` in a method body.
That pattern cannot tell a **field of the receiver** from a **metadata cell**: IL2CPP
emits `adrp x8, #page` + `ldr x8, [x8, #off]` for cells too, and the cell pages happen
to sit at handy offsets. `Board_PVP.<GetPvPUserCachingDatas>d__78.MoveNext` (19813332)
was listed as a reader of all three bet ladders for exactly that reason — its
`[x8, #0x208]`, `[x8, #0x210]` and `[x8, #0x218]` are cells in the `0x2ae0000` page,
not fields of `Board_PVP`.

This report separates the two mechanically (the base register's last definition decides),
re-derives the reader table, and then reads the method it accidentally promoted: a
six-state coroutine that pulls the PvP user document out of Firebase, waits, compares a
stored date against the clock, and then hands off to `IESummarySeasonRewards` or
`LoadPvPDatas` — or deletes the database entry when it is stale.
"""
import argparse
import functools
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import buy_delegate as BD  # noqa: E402

MOVENEXT = 19813332
ONCHANGE_COIN = 19779724
ONCHANGE_GEM = 19779984
ONCHANGE_MEDAL = 19780244
SETUP = 19791640
ONCLICK = 19792936
ISCOLLECTED0 = 19811092
OFFSETS = {'rewardIndexs': 0x198, 'rewardValues': 0x1A0, 'rewardScales': 0x1A8,
           'allBetCoinValues': 0x208, 'allBetGemValues': 0x210, 'allBetMedalValues': 0x218}
SCANNED = {SETUP: 'Board_PVP.SetupHunters', ONCLICK: 'Board_PVP.OnClickHunterCollect',
           ONCHANGE_COIN: 'Board_PVP.OnChangeCoins', ONCHANGE_GEM: 'Board_PVP.OnChangeGems',
           ONCHANGE_MEDAL: 'Board_PVP.OnChangeMedals',
           ISCOLLECTED0: '<>c__DisplayClass79_0.<IESummarySeasonRewards>g__IsCollected|0',
           MOVENEXT: '<GetPvPUserCachingDatas>d__78.MoveNext'}
CELL_PAGE = 0x2AE0000
PREV169 = 'datas/l2_535b0541_pvp_reward_arrays.json.gz'
ARTIFACT = 'datas/l2_535b0541_pvp_move_next.json.gz'


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@functools.lru_cache(maxsize=None)
def methods():
    return BD.slices()


def body(rva):
    for (_, key), row in methods().items():
        if key == rva:
            return row
    raise AssertionError('no body for %d' % rva)


def text(insn):
    return insn['mnemonic'] + ' ' + insn['op_str']


WRITERS = set('mov movk movz movn ldr ldrb ldrh ldrsb ldur adr adrp add sub and orr eor '
              'lsl lsr asr cset csinc csel csinv csneg fmov fadd fsub fmul fdiv fabs fneg '
              'fcvt fcvtzs scvtf frintp frintm madd msub sxtw uxtw ubfx sbfx mul sdiv udiv '
              'neg mvn ldp ldpsw'.split())


def defines(insns, index, register):
    """Last index < `index` whose destination is `register`, or None."""
    pattern = re.compile(r'(^|, )%s($|,)' % re.escape(register))
    for number in range(index - 1, -1, -1):
        insn = insns[number]
        if insn['mnemonic'] not in WRITERS:
            continue
        head = insn['op_str'].split(',')[0].strip()
        if head == register or (insn['mnemonic'] == 'ldp' and
                                register in [part.strip() for part in
                                             insn['op_str'].split(',')[:2]]):
            return number
        if pattern.search(insn['op_str']) and head != register:
            continue
    return None


def literal(insn):
    """`#imm` out of an operand string, as an int (decimal or hex)."""
    match = re.search(r'#(-?0x[0-9a-f]+|-?\d+)', insn['op_str'])
    return int(match.group(1), 0) if match else None


def base_kind(insns, number, base, offset):
    """`static_cell` when the base register was last set by `adrp`, else `object_field`."""
    if not base.startswith('x'):
        return dict(base=base, kind='other', cell=None)
    number_of_def = defines(insns, number, base)
    if number_of_def is None:
        return dict(base=base, kind='other', cell=None)
    definition = insns[number_of_def]
    if definition['mnemonic'] == 'adrp':
        page = BD.const(definition['op_str'])
        return dict(base=base, kind='static_cell',
                    cell=page + offset if page is not None else None,
                    adrp_rva=definition['rva'])
    return dict(base=base, kind='object_field', cell=None,
                loaded_at=definition['rva'], loaded_by=text(definition))


def reads():
    """Every `ldr` that touches one of the six offsets, with its base kind."""
    rows = []
    for rva, name in SCANNED.items():
        insns = body(rva)['instructions']
        for number, insn in enumerate(insns):
            if insn['mnemonic'] not in ('ldr', 'ldrb'):
                continue
            match = re.search(r'\[(x\d+), #(0x[0-9a-f]+)\]', insn['op_str'])
            if not match:
                continue
            offset = int(match.group(2), 16)
            field = next((name_ for name_, value in OFFSETS.items() if value == offset), None)
            if field is None:
                continue
            rows.append(dict(method=name, method_rva=rva, rva=insn['rva'], op=text(insn),
                             offset=hex(offset), field=field,
                             **base_kind(insns, number, match.group(1), offset)))
    return rows


def reader_table(rows):
    table = {}
    for field in OFFSETS:
        real = sorted({row['method_rva'] for row in rows
                       if row['field'] == field and row['kind'] == 'object_field'})
        cells = sorted({row['cell'] for row in rows
                        if row['field'] == field and row['kind'] == 'static_cell'})
        table[field] = dict(real_readers=real, cells=[hex(cell) for cell in cells if cell],
                            real_reads=len([row for row in rows if row['field'] == field
                                            and row['kind'] == 'object_field']),
                            cell_reads=len([row for row in rows if row['field'] == field
                                            and row['kind'] == 'static_cell']))
    return table


def states():
    """`MoveNext` is a state machine: `str wN, [x19, #0x10]` writes the state field.

    Three of the states are written through one shared store that the code reaches
    with `mov w8, #k; b <store>`, so following the branch is the only way to read them.
    """
    insns = body(MOVENEXT)['instructions']
    stores = {insn['rva']: insn for insn in insns
              if insn['mnemonic'] == 'str' and '[x19, #0x10]' in insn['op_str']}
    writes = []
    for number, insn in enumerate(insns):
        value = None
        via = None
        if insn['rva'] in stores:
            source = insn['op_str'].split(',')[0].strip()
            number_of_def = defines(insns, number, source)
        elif insn['mnemonic'] == 'b':
            target = BD.call_target(insn)
            if target not in stores:
                continue
            source = stores[target]['op_str'].split(',')[0].strip()
            number_of_def = defines(insns, number, source)
        else:
            continue
        if number_of_def is not None:
            via = text(insns[number_of_def])
            value = literal(insns[number_of_def])
        writes.append(dict(rva=insn['rva'], op=text(insn), via=via, value=value))
    return dict(field='0x10', writes=writes, values=[row['value'] for row in writes],
                store_rvas=sorted(stores))


def call_rows():
    insns = body(MOVENEXT)['instructions']
    rows = []
    for insn in insns:
        if insn['mnemonic'] not in ('bl', 'b'):
            continue
        target = BD.call_target(insn)
        if target is None:
            continue
        named = BD.name(target)
        if not named['class_name']:
            continue
        rows.append(dict(rva=insn['rva'], target=target, op=text(insn),
                         class_name=named['class_name'], signature=named['signature']))
    return rows


def flow():
    """The coroutine's parts, keyed by a substring of the callee signature."""
    wants = {
        'path': 'get_pathOfDataUsers',
        'user': 'get_userID',
        'format': 'Format(string format',
        'download': 'DownloadDatabase',
        'wait_until': 'WaitUntil',
        'wait_seconds': 'WaitForSecondsRealtime',
        'parse_date': 'BinaryStringToDateTime',
        'less_than': 'op_LessThan',
        'log': 'Debug Log(',
        'utc': 'GetValueUTC',
        'summary': 'IESummarySeasonRewards',
        'load': 'LoadPvPDatas',
        'delete': 'DeleteDatabase',
        'start': 'StartCoroutine',
    }
    rows = call_rows()
    out = {}
    for key, needle in wants.items():
        hit = [row for row in rows
               if needle in '%s %s' % (row['class_name'], row['signature'] or '')]
        out[key] = dict(hit[0]) if hit else None
    return out


def check(rows, name, passed, detail=None):
    rows.append(dict(name=name, passed=bool(passed), detail=detail))


def run_checks(rows, table, state_row, flow_rows, call_list, previous):
    checks = []
    bet = ['allBetCoinValues', 'allBetGemValues', 'allBetMedalValues']
    check(checks, 'the-bet-ladders-have-one-real-reader-each',
          [table[field]['real_readers'] for field in bet] == [[19779724], [19779984],
                                                              [19780244]], table)
    check(checks, 'the-move-next-hits-are-cells-not-fields',
          all(table[field]['cell_reads'] > 0 and MOVENEXT not in table[field]['real_readers']
              for field in bet),
          {field: (table[field]['cell_reads'], table[field]['cells']) for field in bet})
    check(checks, 'every-false-hit-is-a-cell-in-the-2ae0000-page',
          {field: row['cells'] for field, row in table.items()} ==
          {'rewardIndexs': ['0x2ae0198'], 'rewardValues': ['0x2ae01a0'],
           'rewardScales': ['0x2ae01a8'], 'allBetCoinValues': ['0x2ae0208'],
           'allBetGemValues': ['0x2ae0210'], 'allBetMedalValues': ['0x2ae0218']},
          {field: row['cells'] for field, row in table.items()})
    check(checks, 'the-reward-arrays-have-two-two-and-one-real-readers',
          table['rewardIndexs']['real_readers'] == [SETUP, ONCLICK]
          and table['rewardValues']['real_readers'] == [SETUP, ONCLICK]
          and table['rewardScales']['real_readers'] == [SETUP], table)
    check(checks, 'move-next-does-not-read-any-board_pvp-array',
          [row['real_readers'] for row in table.values() if MOVENEXT in row['real_readers']] == [],
          [row['cells'] for row in table.values()])
    check(checks, '169-listed-move-next-for-all-three-bet-arrays',
          all(MOVENEXT in [site['rva'] for site in previous['readers'][field]['reads']]
              for field in bet),
          {field: [site['rva'] for site in previous['readers'][field]['reads']]
           for field in bet})
    check(checks, 'the-correction-has-a-cell-for-every-false-hit',
          all(row['cell'] for row in rows if row['kind'] == 'static_cell'),
          [row for row in rows if row['kind'] == 'static_cell'])
    check(checks, 'the-state-machine-has-six-states',
          sorted(set(state_row['values'])) == [-1, 1, 2, 3, 4, 5], state_row['values'])
    check(checks, 'the-coroutine-builds-the-path-first',
          bool(flow_rows['path'] and flow_rows['user'] and flow_rows['format'])
          and flow_rows['format']['rva'] > flow_rows['path']['rva'],
          {key: (row or {}).get('rva') for key, row in flow_rows.items()})
    check(checks, 'it-downloads-the-user-document',
          'DownloadDatabase' in (flow_rows['download'] or {}).get('signature', ''),
          flow_rows['download'])
    check(checks, 'it-waits-twice',
          flow_rows['wait_until'] is not None and flow_rows['wait_seconds'] is not None,
          [flow_rows['wait_until'], flow_rows['wait_seconds']])
    check(checks, 'it-compares-the-stored-date-with-the-clock',
          flow_rows['parse_date'] is not None and flow_rows['less_than'] is not None,
          [flow_rows['parse_date'], flow_rows['less_than']])
    check(checks, 'a-stale-entry-is-deleted',
          'DeleteDatabase' in (flow_rows['delete'] or {}).get('signature', ''),
          flow_rows['delete'])
    check(checks, 'a-fresh-entry-hands-off-to-the-two-iterators',
          bool(flow_rows['summary'] and flow_rows['load'])
          and flow_rows['summary']['rva'] < flow_rows['load']['rva'],
          [flow_rows['summary'], flow_rows['load']])
    check(checks, 'both-iterators-are-started-with-startcoroutine',
          len([row for row in call_list if 'StartCoroutine' in (row['signature'] or '')]) == 2,
          [row for row in call_list if 'StartCoroutine' in (row['signature'] or '')])
    check(checks, 'the-firebase-manager-is-a-singleton-cell',
          (flow_rows['download'] or {}).get('class_name') == 'FirebaseDatabaseManager'
          and (flow_rows['delete'] or {}).get('class_name') == 'FirebaseDatabaseManager',
          [(flow_rows['download'] or {}).get('class_name'),
           (flow_rows['delete'] or {}).get('class_name')])
    check(checks, 'every-scanned-method-has-a-body',
          all(body(rva)['size'] > 0 for rva in SCANNED), sorted(SCANNED))
    check(checks, 'the-six-offsets-are-the-169-offsets',
          previous['ctor'] and [row['offset'] for row in previous['ctor']['initializers']] ==
          ['0x198', '0x1a0', '0x1a8', '0x208', '0x210', '0x218'],
          [row['offset'] for row in previous['ctor']['initializers']])
    check(checks, 'the-coroutine-is-452-instructions', len(body(MOVENEXT)['instructions']) == 452,
          len(body(MOVENEXT)['instructions']))
    return checks


def build(output=None):
    rows = reads()
    table = reader_table(rows)
    state_row = states()
    call_list = call_rows()
    flow_rows = flow()
    previous = load(PREV169)
    checks = run_checks(rows, table, state_row, flow_rows, call_list, previous)

    payload = dict(
        schema='l2/535b0541/pvp-move-next/1',
        boundary=dict(branch='arena/535b0541-windwings-space-shooter-game-p',
                      correction_of=169,
                      note='reader attribution re-derived by base-register kind; the '
                           'coroutine is described, not executed'),
        evidence='STATIC_ONLY_ORIGINAL_APK',
        movenext=dict(rva=MOVENEXT, size=body(MOVENEXT)['size'],
                      instructions=len(body(MOVENEXT)['instructions']),
                      class_name=BD.name(MOVENEXT)['class_name'],
                      signature=BD.name(MOVENEXT)['signature']),
        offsets={name: hex(value) for name, value in OFFSETS.items()},
        reads=rows,
        readers=table,
        corrected=[dict(report=169, field=field,
                        was='reader list included %s' % SCANNED[MOVENEXT],
                        now='reads %d cell(s) %s in the 0x2ae0000 page, not the field'
                            % (table[field]['cell_reads'], table[field]['cells']))
                   for field in ('allBetCoinValues', 'allBetGemValues', 'allBetMedalValues')],
        states=state_row,
        flow=flow_rows,
        calls=call_list,
        open_items=[
            dict(item='what Firebase returns', why='served data',
                 detail='MODEL_NOT_MEASURED runtime; the coroutine only proves the route'),
            dict(item='the date comparison outcome per user', why='runtime clock and data',
                 detail='which branch runs depends on the stored value'),
            dict(item='the format string cell 0x2adebb0', why='a string cell',
                 detail='the path template text is data, not code'),
        ],
        provenance=dict(inputs=[dict(path=PREV169, sha256=sha_file(PREV169))],
                        slices=[dict(path='reverse-engineering/raw/%s/native.json.gz'
                                          % path.parent.name,
                                     sha256=sha_file('reverse-engineering/raw/%s/native.json.gz'
                                                     % path.parent.name))
                                for path in sorted(ROOT.glob(BD.RAW_GLOB))]),
        totals=dict(reads=len(rows), real=len([row for row in rows
                                               if row['kind'] == 'object_field']),
                    cells=len([row for row in rows if row['kind'] == 'static_cell']),
                    calls=len(call_list), states=len(state_row['writes']),
                    checks_passed=sum(1 for row in checks if row['passed']),
                    checks_total=len(checks)),
        checks=checks,
    )
    blob = json.dumps(payload, sort_keys=True, indent=1, ensure_ascii=False).encode('utf-8')
    packed = gzip.compress(blob, mtime=0)
    if output:
        (ROOT / output).write_bytes(packed)
    return payload, packed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=ARTIFACT)
    args = parser.parse_args()
    payload, packed = build(args.output)
    print(json.dumps(dict(bytes=len(packed), sha256=hashlib.sha256(packed).hexdigest(),
                          **payload['totals'])))
    if payload['totals']['checks_passed'] != payload['totals']['checks_total']:
        print(json.dumps([row['name'] for row in payload['checks'] if not row['passed']]))
        raise SystemExit('checks failed')


if __name__ == '__main__':
    main()
