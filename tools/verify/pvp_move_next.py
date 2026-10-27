#!/usr/bin/env python3
"""169's reader table, re-checked: three of the six entries were class-init cells.

169 listed readers for the six `Board_PVP` arrays by looking for loads whose offset matched
a field. That test is not sufficient: IL2CPP loads a *metadata cell* with exactly the same
`ldr xN, [xM, #off]` shape, where `xM` comes from `adrp` and the offset is the low bits of
a slot address. Two such slots sit at 0x2ae0198 / 0x2ae01a0 / 0x2ae01a8 / 0x2ae0208 /
0x2ae0210 / 0x2ae0218 — the same numbers as the six field offsets — so any method that
touches a class-init token there looks like a reader.

This report decides each site by the base register's **last definition**: `adrp` means the
register holds a cell address, anything else means it holds an object.

Result: `MoveNext` (19813332) reads none of the six fields, and `<IsCollected|0>` reads no
array either. What is left is the honest table — the bet ladders are read by their own
`OnChange*` handlers, the reward arrays by `SetupHunters` / `OnClickHunterCollect`.

The coroutine itself is described as a side effect: it is the Firebase sync of the PvP user
cache, not a reward reader.

Nothing is executed.
"""
import argparse
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import buy_delegate as BD  # noqa: E402

ARTIFACT = 'datas/l2_535b0541_pvp_move_next.json.gz'
PREV169 = 'datas/l2_535b0541_pvp_reward_arrays.json.gz'

CLASS = 'Board_PVP'
FIELDS = {0x198: 'rewardIndexs', 0x1a0: 'rewardValues', 0x1a8: 'rewardScales',
          0x208: 'allBetCoinValues', 0x210: 'allBetGemValues', 0x218: 'allBetMedalValues'}
MOVE_NEXT = 19813332
IS_COLLECTED = 19811092

EXPECTED = {
    'rewardIndexs': [19791640, 19792936],
    'rewardValues': [19791640, 19792936],
    'rewardScales': [19791640],
    'allBetCoinValues': [19779724],
    'allBetGemValues': [19779984],
    'allBetMedalValues': [19780244],
}

WRITERS = ('str', 'strb', 'strh', 'stur', 'stp')


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


def offset_of(text):
    if not text:
        return 0
    return int(text, 16) if text.startswith('0x') else int(text)


def definition(instructions, index, register):
    """Last instruction before `index` that writes `register` (a name, not a claim)."""
    for position in range(index - 1, -1, -1):
        insn = instructions[position]
        op = insn.get('op_str') or ''
        head = op.split(',')[0].strip()
        if head != register:
            continue
        if insn['mnemonic'] in ('cmp', 'tst', 'fcmp', 'fcmpe', 'movk', 'fmov'):
            continue
        return insn
    return None


def scan():
    """Every read/write of a field offset inside Board_PVP*, decided by its base register."""
    rows = []
    for (klass, rva), payload in BD.slices().items():
        if not klass.startswith(CLASS):
            continue
        for index, insn in enumerate(payload['instructions']):
            op = insn.get('op_str') or ''
            match = re.search(r'\[(x\d+), #(0x[0-9a-f]+|[0-9]+)\]$', op)
            if not match:
                continue
            offset = offset_of(match.group(2))
            if offset not in FIELDS:
                continue
            base = match.group(1)
            source = definition(payload['instructions'], index, base)
            kind = 'unknown'
            if source is not None:
                kind = 'cell' if source['mnemonic'] == 'adrp' else 'instance'
            rows.append(dict(klass=klass, method_rva=rva, field=FIELDS[offset],
                             offset=hex(offset), rva=insn['rva'],
                             mnemonic=insn['mnemonic'], op=op, base=base,
                             base_defined_by=(source['mnemonic'] if source else None),
                             base_definition=(source['rva'] if source else None),
                             kind=kind))
    return rows


def corrected(rows):
    table = {}
    for name in FIELDS.values():
        table[name] = sorted({row['method_rva'] for row in rows
                              if row['field'] == name and row['kind'] == 'instance'
                              and row['mnemonic'] not in WRITERS})
    return table


def move_next():
    payload = BD.slices()[(CLASS + '.<GetPvPUserCachingDatas>d__78', MOVE_NEXT)]
    calls = []
    for insn in payload['instructions']:
        if insn['mnemonic'] != 'bl':
            continue
        target = int((insn.get('op_str') or '').split('#')[1], 16)
        named = BD.name(target)
        if named['class_name'] is None:
            continue
        calls.append(dict(rva=insn['rva'], target=target, klass=named['class_name'],
                          signature=(named['signature'] or '')[:70]))
    return dict(rva=MOVE_NEXT, size=payload['size'],
                instructions=len(payload['instructions']),
                signature=payload['signature'][:70], calls=calls)


def build_payload():
    rows = scan()
    fixed = corrected(rows)
    previous = load(PREV169)
    before = {name: sorted({row['rva'] for row in previous['readers'][name]['reads']})
              for name in FIELDS.values()}
    coroutine = move_next()

    cells = [row for row in rows if row['kind'] == 'cell']
    pinned_false = (19811144, 19811156, 19811168, 19813496, 19813508, 19813520)
    false_sites = [row for row in cells if row['rva'] in pinned_false]
    checks = []

    def check(name, passed, detail=None):
        checks.append(dict(name=name, passed=bool(passed), detail=detail))

    check('the-corrected-table-is-what-the-bytes-say', fixed == EXPECTED, fixed)
    check('the-reward-arrays-lose-IsCollected',
          [name for name in fixed if 19811092 in before[name] and
           19811092 not in fixed[name]] == ['rewardIndexs', 'rewardValues', 'rewardScales'],
          [name for name in fixed if 19811092 in before[name]])
    check('the-bet-ladders-lose-it-too',
          all(19813332 in before[name] and fixed[name] != before[name]
              for name in ('allBetCoinValues', 'allBetGemValues', 'allBetMedalValues')),
          {name: fixed[name] for name in ('allBetCoinValues', 'allBetGemValues',
                                          'allBetMedalValues')})
    check('the-coroutine-reads-no-field',
          [row for row in rows if row['method_rva'] == MOVE_NEXT
           and row['kind'] == 'instance'] == [],
          [row['rva'] for row in rows if row['method_rva'] == MOVE_NEXT])
    check('every-site-inside-the-coroutine-is-a-cell',
          all(row['kind'] == 'cell' for row in rows if row['method_rva'] == MOVE_NEXT),
          [row['kind'] for row in rows if row['method_rva'] == MOVE_NEXT])
    check('IsCollected-touches-three-cells-and-no-array',
          {row['offset'] for row in rows if row['method_rva'] == IS_COLLECTED} ==
          {'0x198', '0x1a0', '0x1a8'} and
          all(row['kind'] == 'cell' for row in rows if row['method_rva'] == IS_COLLECTED),
          [row['offset'] for row in rows if row['method_rva'] == IS_COLLECTED])
    check('six-cell-addresses-are-the-six-field-offsets',
          sorted({row['offset'] for row in cells}) ==
          sorted(hex(offset) for offset in FIELDS), sorted({row['offset'] for row in cells}))
    check('the-false-positive-sites-are-pinned', len(false_sites) == 6,
          [row['rva'] for row in false_sites])
    check('169-listed-the-coroutine-as-a-reader-of-the-bet-ladders',
          all(19813332 in before[name] for name in ('allBetCoinValues', 'allBetGemValues',
                                                    'allBetMedalValues')),
          {name: before[name] for name in ('allBetCoinValues',)})
    check('the-coroutine-is-452-instructions', coroutine['instructions'] == 452,
          coroutine['instructions'])
    check('it-is-1808-bytes', coroutine['size'] == 1808, coroutine['size'])
    check('it-calls-the-firebase-sync',
          {'FirebaseDatabaseManager', 'Board_PVP'} <= {row['klass'] for row in coroutine['calls']},
          sorted({row['klass'] for row in coroutine['calls']}))
    check('it-parses-the-stored-date',
          any('BinaryStringToDateTime' in row['signature'] for row in coroutine['calls']),
          [row['signature'] for row in coroutine['calls']
           if 'DateTime' in row['signature']][:2])

    return {
        'schema': 'l2/535b0541/pvp-move-next/1',
        'evidence': 'STATIC_ONLY_ORIGINAL_APK',
        'note': 'A cell load and a field load are the same instruction shape. Deciding by the '
                'base register removes three readers from the reward arrays and three from '
                'the bet ladders; what remains is the table 169 should have printed.',
        'class_': CLASS,
        'move_next': coroutine,
        'corrections': [
            dict(field='rewardIndexs', was=before['rewardIndexs'],
                 now=fixed['rewardIndexs'],
                 why='169 counted `[x0, #0x198]` at 19811144 in `<IsCollected|0>`, whose '
                     'base came from `adrp x0, #0x2ae0000`; that is class-init token '
                     '0x2ae0198, not the field'),
            dict(field='rewardValues', was=before['rewardValues'], now=fixed['rewardValues'],
                 why='same shape at 19811156 (cell 0x2ae01a0)'),
            dict(field='rewardScales', was=before['rewardScales'], now=fixed['rewardScales'],
                 why='cells 0x2ae01a8 at 19811168 and 19811204, both `<IsCollected|0>`'),
            dict(field='allBetCoinValues', was=before['allBetCoinValues'],
                 now=fixed['allBetCoinValues'],
                 why='cell 0x2ae0208 at 19813496 (coroutine); the real reader is '
                     '`OnChangeCoins`'),
            dict(field='allBetGemValues', was=before['allBetGemValues'],
                 now=fixed['allBetGemValues'], why='cell 0x2ae0210'),
            dict(field='allBetMedalValues', was=before['allBetMedalValues'],
                 now=fixed['allBetMedalValues'], why='cell 0x2ae0218'),
        ],
        'readers': {name: dict(methods=fixed[name],
                               loads=len([row for row in rows
                                          if row['field'] == name
                                          and row['kind'] == 'instance'
                                          and row['mnemonic'] not in WRITERS]))
                    for name in FIELDS.values()},
        'sites': rows,
        'totals': dict(fields=len(FIELDS), sites=len(rows), cells=len(cells),
                       instance=len(rows) - len(cells)),
        'limits': [
            'the classification needs the base register to be defined inside the same '
            'method; a register arriving as an argument is left as `unknown`.',
            'what the coroutine writes into the PvP user cache is a Firebase payload, so it '
            'stays MODEL_NOT_MEASURED runtime.',
        ],
        'provenance': dict(
            xapk_sha256='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e',
            inputs=[dict(path=PREV169, sha256=sha_file(PREV169))]),
        'checks': checks,
    }


def build(output=None):
    payload = build_payload()
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode('utf-8')
    packed = gzip.compress(blob, mtime=0)
    if output:
        (ROOT / output).write_bytes(packed)
    return payload, packed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=ARTIFACT)
    args = parser.parse_args()
    payload, packed = build(args.output)
    failed = [row for row in payload['checks'] if not row['passed']]
    print(json.dumps(dict(bytes=len(packed), sha256=hashlib.sha256(packed).hexdigest(),
                          sites=payload['totals']['sites'], checks=len(payload['checks']),
                          failing=len(failed))))
    if failed:
        print(json.dumps([row['name'] for row in failed]))
        raise SystemExit('gate failed')


if __name__ == '__main__':
    main()
