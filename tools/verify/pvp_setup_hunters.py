#!/usr/bin/env python3
"""`Board_PVP.SetupHunters`: the six reward rows, and what each one is given.

169 mapped the six arrays to their fields and their readers, but stopped before the
method that actually *uses* them. This one reads that method end to end. Everything
below is an instruction in the pinned slice, so the interesting part is not "which
array" (169 answered that) but the wiring:

* `allPoints` is a `WinPoint[]` (0x190). The ctor fills six reward arrays of length 6,
  but the loop walks **twelve** points: even indices get the "collected" marker, odd
  indices get a reward box. The reward index is `k = (i - 1) >> 1`, so 12 points carry
  6 rewards.
* `boxRewards` (WinPoint+0x28) is the `Box_Rewards` that gets `SetInfo`. Its arguments
  are the three arrays 169 decoded: `w3 = rewardValues[k]`, `s0 = rewardScales[k]`,
  and `x1` = `DataShopPack.GetBoxSpriteGeneral(rewardIndexs[k])`.
* `rewardIndexs[k]` also picks which sprite slot the box uses: 14 -> `+0x58`,
  15 -> `+0x50`, anything else -> `[list + id*8 + 0x20]`. And `_isCards` is
  `(id & ~1) == 14`, i.e. true for ids 14 and 15 — the same flag 166 measured on the
  box side, now with its condition.
* `collectedObject` (WinPoint+0x38) is toggled by `IsCollected(i)`, which is **not**
  the array reader 169 listed: it reads `PlayerPreferences.GetInt(prefix + i, 0) == 1`,
  so "collected" is local device state, one key per point.
* `onClick` (WinPoint+0x40) gets `new Action<WinPoint>(this)`.
* `allDieObjects` (0x170) is shown for `i < get_SeasonDies()`; `lineProgress`
  (SpriteRenderer 0x188) gets `size = get_SeasonProgress() * 1.5`, and its two children
  toggle on `progress > 0` and `progress == allDieObjects.Length`.

The reward *content* stays where 169 left it: `rewardIndexs`' blob is bound, the
`rewardValues` / `rewardScales` blobs are not, so no row's amount or scale is claimed.
"""
import argparse
import functools
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import buy_delegate as BD  # noqa: E402

CLASS = 'Board_PVP'
SETUP = 19791640
IS_COLLECTED = 19792764
SET_INFO = 19990656
GET_BOX_SPRITE = 20180172
SEASON_DIES = 19784352
SEASON_PROGRESS = 19784460
GAMEOBJECT_SETACTIVE = 41424900
GET_GAMEOBJECT = 41415048
SET_POINT_ACTIVE = 19952820
GET_TRANSFORM = 41414988
GET_CHILD = 41462580
SPRITE_GET_SIZE = 41463204
SPRITE_SET_SIZE = 41463348
ACTION_CTOR = 25843072
INT_TOSTRING = 34616120
STRING_CONCAT = 33439876
PREFS_GETINT = 20912668
PREV169 = 'datas/l2_535b0541_pvp_reward_arrays.json.gz'
ARTIFACT = 'datas/l2_535b0541_pvp_setup_hunters.json.gz'

# dump.cs, `Board_PVP` field block (see `fields()`), and `WinPoint`'s own block.
POV_FIELDS = {0x170: ('allDieObjects', 'GameObject[]'),
              0x188: ('lineProgress', 'SpriteRenderer'),
              0x190: ('allPoints', 'WinPoint[]'),
              0x198: ('rewardIndexs', 'int[]'),
              0x1A0: ('rewardValues', 'int[]'),
              0x1A8: ('rewardScales', 'float[]')}
POINT_FIELDS = {0x20: ('textNumber', 'TextMeshPro'),
                0x28: ('boxRewards', 'Box_Rewards'),
                0x30: ('anim', 'Animator'),
                0x38: ('collectedObject', 'GameObject'),
                0x40: ('onClick', 'Action<WinPoint>')}

# The instructions this report leans on, as (rva, mnemonic op_str) pairs.
LANDMARKS = [
    (0x12dff78, 'ldr x8, [x19, #0x170]'),
    (0x12dffc8, 'bl #0x12de2a0'),
    (0x12dffd4, 'cset w1, lt'),
    (0x12dffe0, 'bl #0x2781804'),
    (0x12e001c, 'ldr x8, [x8, #0x20]'),
    (0x12e0024, 'ldr x0, [x8, #0x28]'),
    (0x12e0038, 'and w1, w20, #1'),
    (0x12e0044, 'tbz w20, #0, #0x12e0180'),
    (0x12e0050, 'sub w9, w20, #1'),
    (0x12e0060, 'asr w11, w9, #1'),
    (0x12e0074, 'ldr w8, [x8, #0x20]'),
    (0x12e0080, 'b.eq #0x12e00a4'),
    (0x12e00b4, 'add x8, x0, #0x58'),
    (0x12e009c, 'add x8, x0, #0x50'),
    (0x12e011c, 'ldr x22, [x8]'),
    (0x12e0124, 'ldr w23, [x8, #0x20]'),
    (0x12e0134, 'bl #0x133eccc'),
    (0x12e0154, 'ldr s0, [x8, #0x20]'),
    (0x12e0160, 'mov x1, x0'),
    (0x12e0164, 'cset w4, eq'),
    (0x12e016c, 'mov x2, x22'),
    (0x12e0170, 'mov w3, w23'),
    (0x12e017c, 'bl #0x1310880'),
    (0x12e01bc, 'mov x1, xzr'),
    (0x12e01c0, 'bl #0x13074b4'),
    (0x12e01e8, 'ldr x21, [x8, #0x38]'),
    (0x12e01fc, 'bl #0x12e037c'),
    (0x12e0204, 'and w1, w0, #1'),
    (0x12e0250, 'bl #0x18a5580'),
    (0x12e0258, 'str x21, [x22, #0x40]'),
    (0x12e02a4, 'fmov s2, #1.50000000'),
    (0x12e02a8, 'fmul s0, s0, s2'),
    (0x12e02b4, 'bl #0x278ae34'),
    (0x12e02f4, 'cset w1, gt'),
    (0x12e0364, 'cset w1, eq'),
]


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@functools.lru_cache(maxsize=None)
def methods():
    return BD.slices()


def body(rva):
    for (klass, key), row in methods().items():
        if key == rva:
            return row
    raise AssertionError('no body for %d' % rva)


def text(insn):
    return insn['mnemonic'] + ' ' + insn['op_str']


@functools.lru_cache(maxsize=None)
def dump_lines():
    return gzip.decompress((ROOT / 'reverse-engineering/il2cpp/dump.cs.gz').read_bytes()) \
        .decode('utf-8', 'replace').split('\n')


def class_fields(header):
    """The field block of a class in `dump.cs`: offset -> (name, declared type)."""
    start = next(index for index, line in enumerate(dump_lines()) if line.startswith(header))
    out = {}
    for line in dump_lines()[start:start + 200]:
        stripped = line.strip()
        if stripped.startswith('// Methods'):
            break
        if '// 0x' not in stripped or ';' not in stripped:
            continue
        declaration, offset = stripped.rsplit('//', 1)
        declaration = declaration.strip().rstrip(';')
        name = declaration.split()[-1]
        declared = declaration.replace('public ', '').replace('private ', '') \
            .replace('internal ', '').replace('static ', '')
        declared = declared[:len(declared) - len(name)].strip()
        out[int(offset.strip(), 16)] = (name, declared)
    return out


def fields():
    return {'board_pvp': {hex(offset): dict(name=name, declared=declared)
                          for offset, (name, declared) in sorted(class_fields(
                              'public class Board_PVP').items())
                          if offset in POV_FIELDS},
            'winpoint': {hex(offset): dict(name=name, declared=declared)
                         for offset, (name, declared) in sorted(class_fields(
                             'public class WinPoint').items())},
            'expected_pvp': {hex(offset): list(pair) for offset, pair in POV_FIELDS.items()},
            'expected_point': {hex(offset): list(pair) for offset, pair in POINT_FIELDS.items()}}


def landmarks():
    rows = body(SETUP)['instructions']
    index = {insn['rva']: text(insn) for insn in rows}
    return [dict(rva=rva, expected=expected, actual=index.get(rva),
                 pass_=index.get(rva) == expected) for rva, expected in LANDMARKS]


def callers():
    """Calls to the nine named methods, to show which of them this method uses."""
    targets = {SET_INFO: 'Box_Rewards.SetInfo', GET_BOX_SPRITE: 'DataShopPack.GetBoxSpriteGeneral',
               SET_POINT_ACTIVE: 'WinPoint.SetPointActive', IS_COLLECTED: 'Board_PVP.IsCollected',
               GAMEOBJECT_SETACTIVE: 'GameObject.SetActive', GET_GAMEOBJECT: 'Component.get_gameObject',
               ACTION_CTOR: 'Action<WinPoint>..ctor', SEASON_DIES: 'Board_PVP.get_SeasonDies',
               SEASON_PROGRESS: 'Board_PVP.get_SeasonProgress', GET_CHILD: 'Transform.GetChild',
               SPRITE_SET_SIZE: 'SpriteRenderer.set_size', GET_TRANSFORM: 'Component.get_transform'}
    found = {}
    for insn in body(SETUP)['instructions']:
        if insn['mnemonic'] not in ('bl', 'b'):
            continue
        target = BD.call_target(insn)
        if target in targets:
            found.setdefault(targets[target], []).append(insn['rva'])
    return dict(sorted((name, sorted(sites)) for name, sites in found.items()))


def rows():
    """The twelve points: which branch each one takes, and the reward index it uses."""
    return [dict(i=i, parity='odd' if i % 2 else 'even',
                 reward_index=None if i % 2 == 0 else (i - 1) // 2)
            for i in range(12)]


def prefix_cell(insns):
    """The static cell the key prefix is loaded from: adrp page + ldr offset."""
    pages = {insn['op_str'].split(',')[0]: insn for insn in insns
             if insn['mnemonic'] == 'adrp'}
    for insn in insns:
        if insn['mnemonic'] != 'ldr' or insn['op_str'].startswith('ldrb'):
            continue
        register, memory = insn['op_str'].split(',', 1)
        if '#0xfa8' not in memory:
            continue
        page = pages.get(register.strip())
        if page and '0x2adf000' in page['op_str']:
            return hex(0x2adf000 + 0xfa8)
    return None


def collected():
    """`IsCollected(int)` reads a PlayerPreferences int, not the reward arrays."""
    insns = body(IS_COLLECTED)['instructions']
    ops = [text(insn) for insn in insns]
    return dict(rva=IS_COLLECTED, size=body(IS_COLLECTED)['size'],
                signature=body(IS_COLLECTED)['signature'],
                reads_reward_arrays=sum(1 for row in insns
                                        if any(offset in row['op_str']
                                               for offset in ('#0x198', '#0x1a0', '#0x1a8'))),
                prefix_cell=prefix_cell(insns),
                calls=[dict(rva=BD.call_target(insn), op=text(insn),
                            class_name=BD.name(BD.call_target(insn))['class_name'],
                            name=BD.name(BD.call_target(insn))['signature'])
                       for insn in insns if insn['mnemonic'] == 'bl'],
                compare=[op for op in ops if op.startswith('cmp w0,')],
                returns=[op for op in ops if op.startswith('cset w0,')])


def progress():
    """The progress bar: size = SeasonProgress * 1.5, two children toggle."""
    insns = body(SETUP)['instructions']
    return dict(field='0x188 lineProgress',
                size_calls=[dict(rva=insn['rva'], op=text(insn),
                                 name=('get_size' if BD.call_target(insn) == SPRITE_GET_SIZE
                                       else 'set_size'))
                            for insn in insns
                            if insn['mnemonic'] == 'bl'
                            and BD.call_target(insn) in (SPRITE_GET_SIZE,
                                                         SPRITE_SET_SIZE)],
                scale=[text(insn) for insn in insns if '#1.50000000' in insn['op_str']],
                children=[dict(rva=insn['rva'], op=text(insn)) for insn in insns
                          if insn['mnemonic'] == 'bl'
                          and BD.call_target(insn) == GET_CHILD],
                gates=[text(insn) for insn in insns if insn['mnemonic'] == 'cset'])


def setinfo_arguments():
    """The five values 169's arrays feed into `SetInfo`, with their instruction."""
    pairs = [('box', 0x12e0114, 'ldr x10, [x10, #0x20]'),
             ('number', 0x12e0170, 'mov w3, w23'),
             ('isCards', 0x12e0164, 'cset w4, eq'),
             ('scale', 0x12e0154, 'ldr s0, [x8, #0x20]'),
             ('icon', 0x12e0160, 'mov x1, x0'),
             ('sprite', 0x12e016c, 'mov x2, x22'),
             ('call', 0x12e017c, 'bl #0x1310880')]
    index = {insn['rva']: text(insn) for insn in body(SETUP)['instructions']}
    return [dict(argument=name, rva=rva, expected=expected, actual=index.get(rva),
                 pass_=index.get(rva) == expected) for name, rva, expected in pairs]


def check(rows_out, name, passed, detail=None):
    rows_out.append(dict(name=name, passed=bool(passed), detail=detail))


def run_checks(land, calls, field_map, rows_table, coll, prog, args, previous):
    checks = []
    check(checks, 'every-landmark-instruction-is-where-it-was-written',
          all(row['pass_'] for row in land),
          [row for row in land if not row['pass_']])
    check(checks, 'the-setup-method-is-the-one-169-named',
          body(SETUP)['signature'] == 'private void SetupHunters() { }', body(SETUP)['signature'])
    check(checks, 'setup-reads-all-points-and-the-three-reward-arrays',
          set(calls) >= {'Box_Rewards.SetInfo', 'DataShopPack.GetBoxSpriteGeneral',
                         'WinPoint.SetPointActive', 'Board_PVP.IsCollected',
                         'GameObject.SetActive', 'Component.get_gameObject',
                         'Action<WinPoint>..ctor', 'Board_PVP.get_SeasonDies',
                         'Board_PVP.get_SeasonProgress'}, sorted(calls))
    check(checks, 'setinfo-is-called-once', calls['Box_Rewards.SetInfo'] == [0x12e017c],
          calls['Box_Rewards.SetInfo'])
    check(checks, 'the-box-sprite-comes-from-the-reward-id',
          calls['DataShopPack.GetBoxSpriteGeneral'] == [0x12e0134],
          calls['DataShopPack.GetBoxSpriteGeneral'])
    check(checks, 'setactive-is-called-five-times', len(calls['GameObject.SetActive']) == 5,
          calls['GameObject.SetActive'])
    check(checks, 'the-point-fields-are-the-five-winpoint-fields',
          {offset: row['name'] for offset, row in field_map['winpoint'].items()} ==
          {hex(offset): pair[0] for offset, pair in POINT_FIELDS.items()},
          field_map['winpoint'])
    check(checks, 'the-six-pov-fields-are-named',
          {offset: row['name'] for offset, row in field_map['board_pvp'].items()} ==
          {hex(offset): pair[0] for offset, pair in POV_FIELDS.items()},
          field_map['board_pvp'])
    check(checks, 'allpoints-is-a-winpoint-array',
          field_map['board_pvp']['0x190'] == dict(name='allPoints', declared='WinPoint[]'),
          field_map['board_pvp']['0x190'])
    check(checks, 'twelve-points-six-rewards',
          [row['reward_index'] for row in rows_table if row['parity'] == 'odd'] ==
          [0, 1, 2, 3, 4, 5], rows_table)
    check(checks, 'the-reward-index-is-the-halved-point-index',
          all(row['reward_index'] == (row['i'] - 1) // 2
              for row in rows_table if row['parity'] == 'odd'), rows_table)
    check(checks, 'the-parity-branch-is-the-tbz', rows_table[0]['parity'] == 'even'
          and rows_table[1]['parity'] == 'odd', rows_table[:2])
    check(checks, 'iscollected-does-not-read-the-reward-arrays',
          coll['reads_reward_arrays'] == 0, coll['reads_reward_arrays'])
    named = [row for row in coll['calls'] if row['name'] or row['rva'] == 17879080]
    check(checks, 'iscollected-asks-playerpreferences',
          [row['rva'] for row in coll['calls'] if row['rva'] in (INT_TOSTRING, STRING_CONCAT,
                                                                 PREFS_GETINT)] ==
          [INT_TOSTRING, STRING_CONCAT, PREFS_GETINT], coll['calls'])
    check(checks, 'iscollected-compares-to-one',
          coll['compare'] == ['cmp w0, #1'] and coll['returns'] == ['cset w0, eq'], coll['compare'])
    check(checks, 'the-collected-flag-is-local-state',
          [row['class_name'] for row in coll['calls']
           if row['rva'] == PREFS_GETINT] == ['PlayerPreferences'],
          [(row['rva'], row['class_name']) for row in coll['calls']])
    check(checks, 'setinfo-gets-the-three-array-values',
          [row['argument'] for row in args] == ['box', 'number', 'isCards', 'scale', 'icon',
                                                'sprite', 'call']
          and all(row['pass_'] for row in args), args)
    check(checks, 'the-scale-is-rewritten-at-1.5-for-the-progress-bar',
          prog['scale'] == ['fmov s2, #1.50000000']
          and [row['name'] for row in prog['size_calls']] == ['get_size', 'set_size']
          and prog['size_calls'][0]['rva'] < prog['size_calls'][1]['rva'], prog)
    check(checks, 'the-progress-bar-has-two-children',
          [row['rva'] for row in prog['children']] == [0x12e02d4, 0x12e0320], prog['children'])
    check(checks, 'the-progress-gates',
          prog['gates'] == ['cset w1, lt', 'cset w4, eq', 'cset w1, gt', 'cset w1, eq'],
          prog['gates'])
    check(checks, 'the-card-flag-test-is-id-and-not-one',
          'cset w4, eq' == text(next(insn for insn in body(SETUP)['instructions']
                                     if insn['rva'] == 0x12e0164))
          and 'and w8, w21, #0xfffffffe' in [text(insn) for insn in body(SETUP)['instructions']],
          [text(insn) for insn in body(SETUP)['instructions'] if insn['rva'] == 0x12e0158])
    check(checks, 'the-icon-switch-has-three-cases',
          [text(insn) for insn in body(SETUP)['instructions']
           if insn['rva'] in (0x12e009c, 0x12e00b4)] == ['add x8, x0, #0x50',
                                                         'add x8, x0, #0x58'],
          ['add x8, x0, #0x50', 'add x8, x0, #0x58'])
    check(checks, 'the-dies-loop-toggles-by-season-dies',
          [text(insn) for insn in body(SETUP)['instructions']
           if insn['rva'] in (0x12dffd4, 0x12dffe0)] == ['cset w1, lt', 'bl #0x2781804'],
          'cset w1, lt then SetActive')
    check(checks, '169-widths-still-hold', previous['totals']['length'] == 6
          and len(previous['ctor']['initializers']) == 6, previous['totals'])
    check(checks, 'the-amount-and-scale-stay-not-bound',
          previous['blobs']['indexs_blob']['values'] == [23, 0, 14, 1, 15, 18]
          and len(previous['blobs']['unclaimed_floats']) == 4,
          previous['blobs']['unclaimed_floats'])
    check(checks, 'every-landmark-has-a-unique-rva',
          len({row['rva'] for row in land}) == len(land), len(land))
    return checks


def build(output=None):
    land = landmarks()
    calls = callers()
    field_map = fields()
    rows_table = rows()
    coll = collected()
    prog = progress()
    args = setinfo_arguments()
    previous = load(PREV169)
    checks = run_checks(land, calls, field_map, rows_table, coll, prog, args, previous)

    payload = dict(
        schema='l2/535b0541/pvp-setup-hunters/1',
        boundary=dict(branch='arena/535b0541-windwings-space-shooter-game-p',
                      not_consulted=['Board_PVP.<GetPvPUserCachingDatas>d__78.MoveNext'],
                      note='one method end to end; its callees are named by RVA, not decoded'),
        evidence='STATIC_ONLY_ORIGINAL_APK',
        class_=field_map,
        methods=dict(
            setup=dict(rva=SETUP, size=body(SETUP)['size'],
                       instructions=len(body(SETUP)['instructions']),
                       signature=body(SETUP)['signature']),
            is_collected=dict(rva=IS_COLLECTED, size=coll['size'],
                              signature=coll['signature']),
            set_info=dict(rva=SET_INFO, name=BD.name(SET_INFO)['signature']),
            get_box_sprite=dict(rva=GET_BOX_SPRITE, name=BD.name(GET_BOX_SPRITE)['signature'])),
        landmarks=land,
        calls=calls,
        rows=dict(count=len(rows_table), rewards=6, table=rows_table,
                  element='allPoints[i]  (array element at +0x20)',
                  box='allPoints[i].boxRewards (+0x28)',
                  collected='allPoints[i].collectedObject (+0x38)',
                  click='allPoints[i].onClick (+0x40)'),
        dies=dict(field='0x170 allDieObjects', getter=SEASON_DIES,
                  rule='SetActive(i < get_SeasonDies())'),
        icon_switch=dict(source='rewardIndexs[k]', id_14='+0x58', id_15='+0x50',
                         other='[list + id*8 + 0x20] via [singleton+0xb8] +0x20',
                         is_cards='(id & 0xfffffffe) == 14'),
        setinfo=dict(rva='0x1310880', call=0x12e017c, arguments=args),
        collected=coll,
        progress=prog,
        open_items=[
            dict(item='rewardValues / rewardScales bytes', why='169 left them NOT_BOUND',
                 detail='the rows are wired, but no row amount or scale is claimed'),
            dict(item='the icon list behind id 14/15 and the default case',
                 why='`[singleton+0xb8]` is a serialized sprite list, not code',
                 detail='the three cases are code; their contents are asset data'),
            dict(item='the PlayerPreferences prefix string',
                 why='the prefix comes from a static string cell',
                 detail='MODEL_NOT_MEASURED runtime for its value'),
            dict(item='<GetPvPUserCachingDatas>d__78.MoveNext', why='not consulted here',
                 detail='it reads all three bet ladders; the next report'),
        ],
        provenance=dict(
            inputs=[dict(path=path, sha256=sha_file(path))
                    for path in (PREV169, BD.DUMP)],
            slices=[dict(path='reverse-engineering/raw/%s/native.json.gz' % name,
                         sha256=sha_file('reverse-engineering/raw/%s/native.json.gz' % name))
                    for name in sorted({path.parent.name
                                        for path in ROOT.glob(BD.RAW_GLOB)})]),
        totals=dict(landmarks=len(land), calls=sum(len(v) for v in calls.values()),
                    points=len(rows_table), rewards=6,
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
