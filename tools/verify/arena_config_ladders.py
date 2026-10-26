#!/usr/bin/env python3
"""`ArenaConfig` — the shipped half of the Arena season ladder.

139 listed `ArenaConfig`'s six static fields but never opened its `.cctor`, so the
values behind them were only known as "server supplied". They are not: the class
ships two ladders and three scalars as build constants, and `Board_Arena.GetConfigs`
can only *overwrite* them later.

The decode is small; what makes it worth a report is that the shipped text settles
questions the earlier reports had to leave open:

* `SeasonTimes` is in **minutes**, not seconds and not days — the only consumer,
  `ArenaManager.<IESetRankSetups>d__41`, feeds it to `DateTime.AddMinutes`.
* a rank window is `"<up>-<down>"` and the down bound is **45 in all ten seasons**,
  which is exactly where 151's reward table stops paying out (`46-50` is the
  demote band).
* the season start/end are strings holding `DateTime.ToBinary()` longs, which is
  why `IEGetTimeSpan` runs `Int64.Parse` -> `DateTime.FromBinary`.
"""
import argparse
import functools
import glob
import gzip
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import arena_rewards as AR  # noqa: E402  (string table, dump reader, owner())

NATIVE = 'reverse-engineering/raw/arena-pvp-535b0541/native.json.gz'
STRINGS = 'reverse-engineering/il2cpp/stringliteral.json'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'
PREV = 'datas/l2_535b0541_arena_rewards.json.gz'
STAGE1 = 'datas/l2_535b0541_arena_statics.json.gz'   # 139: the field names

CCTOR = 22726640
CONFIG_CELL = 0x2AECA98
MANAGER_CELL = 0x2AE19D0
STATICS_PTR = 0xB8
ARRAY_DATA = 0x20
SEASONS = 10
RANK_MAX = 9

HELPERS = [
    (34499824, 'DateTime.AddMinutes(double)', 'the unit of `SeasonTimes`'),
    (34503640, 'DateTime.ToBinary()', 'season start/end are stored as ToBinary longs'),
    (34620480, 'Int64.ToString()', 'that long is written out as a string'),
    (34376300, 'Convert.ToInt64(string)', '`IEGetTimeSpan` reads the string back'),
    (34502572, 'DateTime.FromBinary(long)', 'and rebuilds the DateTime from it'),
    (34617932, 'Int32.TryParse(string, out int)', 'placement bounds'),
]


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@functools.lru_cache(maxsize=None)
def strings():
    return AR.strings()


@functools.lru_cache(maxsize=None)
def method(klass, needle):
    for row in load(NATIVE)['methods']:
        if row['class_name'] == klass and needle in row['signature']:
            return row
    raise AssertionError('%s %s not in the raw' % (klass, needle))


def blob_sha(row):
    """sha256 of the pinned method body, so the report can cite a stable digest."""
    text = '|'.join('%d:%s %s' % (insn['rva'], insn['mnemonic'], insn['op_str'])
                    for insn in row['instructions'])
    return hashlib.sha256(text.encode()).hexdigest()


# ------------------------------------------------------------------ the class
def cctor():
    row = method('ArenaConfig', '.cctor')
    assert row['rva'] == CCTOR, row['rva']
    insns = {insn['rva']: insn for insn in row['instructions']}
    refs = {ref['rva']: ref for ref in row['slot_refs']}
    assert set(refs) == {22726732, 22726736, 22726752, 22726760}, sorted(refs)

    packed = [lit for lit in row['literals'] if lit['instruction_rva'] == 22726764]
    assert len(packed) == 1
    max_room, min_room = struct.unpack('<2i', bytes.fromhex(packed[0]['hex']))

    def ref_text(rva):
        return strings().get(refs[rva]['addend'])

    writes = [
        dict(rva=22726748, offset=0x00, field='RankSplit', type='string',
             kind='str x9', source={'literal_cell': refs[22726736]['slot_va'],
                                    'literal_address': refs[22726736]['addend'],
                                    'text': ref_text(22726736)}),
        dict(rva=22726780, offset=0x08, field='SeasonTime', type='string',
             kind='str x10', source={'literal_cell': refs[22726760]['slot_va'],
                                     'literal_address': refs[22726760]['addend'],
                                     'text': ref_text(22726760)}),
        dict(rva=22726784, offset=0x10, field='MaxRoomCount', type='int',
             kind='str d0 (low half)', source={'literal_rva': 22726764,
                                               'hex': packed[0]['hex'],
                                               'value': max_room}),
        dict(rva=22726784, offset=0x14, field='MinRoomCount', type='int',
             kind='str d0 (high half)', source={'literal_rva': 22726764,
                                                'value': min_room}),
        dict(rva=22726788, offset=0x18, field='SummaryTime', type='float',
             kind='str w9 (#0x42700000)', source={'imm': '0x42700000'}),
        dict(rva=22726792, offset=0x1c, field='IsOpen', type='bool',
             kind='strb wzr', source={'value': False}),
    ]
    assert insns[22726788]['op_str'] == 'w9, [x8, #0x18]'  # operands only
    summary = struct.unpack('<f', struct.pack('<I', 0x42700000))[0]
    assert summary == 60.0
    return dict(rva=row['rva'], size=row['size'], sha256=blob_sha(row),
                signature=row['signature'].strip(), writes=writes,
                packed_literal=dict(rva=22726764, va=packed[0]['va'],
                                    hex=packed[0]['hex'],
                                    decoded={'MaxRoomCount': max_room,
                                             'MinRoomCount': min_room}),
                summary_time=summary,
                note='six distinct offsets, seven values: 50 and 10 arrive as one '
                     'stored double whose two halves are the two ints')


def ladders():
    row = method('ArenaConfig', '.cctor')
    refs = {ref['rva']: ref for ref in row['slot_refs']}
    split_text = strings()[refs[22726736]['addend']]
    time_text = strings()[refs[22726760]['addend']]

    windows = []
    for season, chunk in enumerate(split_text.split(';')):
        up, _, down = chunk.partition('-')
        windows.append(dict(season=season, text=chunk, up=int(up), down=int(down),
                            widths=int(down) - int(up) + 1))
    minutes = []
    for season, chunk in enumerate(time_text.split(';')):
        value = int(chunk)
        minutes.append(dict(season=season, text=chunk, minutes=value,
                            days=value / 1440, whole_days=value % 1440 == 0))
    assert len(windows) == SEASONS and len(minutes) == SEASONS
    return dict(
        rank_split=dict(text=split_text, seasons=len(windows), rows=windows,
                        shape='<up>-<down> joined by ";"'),
        season_times=dict(text=time_text, seasons=len(minutes), rows=minutes,
                          shape='minutes joined by ";"'),
        observed=dict(up_by_season=[row['up'] for row in windows],
                      down_by_season=[row['down'] for row in windows],
                      minutes_by_season=[row['minutes'] for row in minutes],
                      days_by_season=[int(row['days']) for row in minutes],
                      total_days=int(sum(row['days'] for row in minutes))))


# ------------------------------------------------------------------- the uses
def semantics():
    """`<IEResetUserProfileStatus>d__37`: what a placement does to a rank."""
    row = method('ArenaManager.<IEResetUserProfileStatus>d__37', 'MoveNext')
    at = {insn['rva']: insn['mnemonic'] + ' ' + insn['op_str']
          for insn in row['instructions']}
    steps = [
        dict(rva=22719856, op='ldr x11, [x9, #0x28]', meaning='RankUpIndexs'),
        dict(rva=22719864, op='ldrsw x10, [x8, #0x1c]', meaning='arenaRank'),
        dict(rva=22719884, op='ldr w11, [x11, #0x20]', meaning='RankUpIndexs[rank]'
                                                              ' via x11 + rank*4 + 0x20'),
        dict(rva=22719888, op='cmp w21, w11', meaning='status vs the up bound'),
        dict(rva=22719892, op='b.le #0x15aaec4', meaning='status <= up -> promote'),
        dict(rva=22720196, op='add w9, w10, #1', meaning='arenaRank + 1'),
        dict(rva=22720200, op='cmp w9, #9', meaning='clamp to 9'),
        dict(rva=22720208, op='csinc w9, w9, w10, ge', meaning='min(rank + 1, 9)'),
        dict(rva=22720212, op='str w9, [x8, #0x1c]', meaning='store arenaRank'),
        dict(rva=22719928, op='ldr x10, [x9, #0x30]', meaning='RankDropIndexs'),
        dict(rva=22719960, op='cmp w21, w10', meaning='status vs the down bound'),
        dict(rva=22719964, op='b.le #0x15aaed8', meaning='status <= down -> keep rank'),
        dict(rva=22719968, op='sub w9, w9, #1', meaning='arenaRank - 1'),
        dict(rva=22719972, op='bic w9, w9, w9, asr #31', meaning='clamp to 0'),
        dict(rva=22720216, op='mov w9, #-1', meaning='status = -1'),
        dict(rva=22720220, op='str w9, [x8, #0x28]', meaning='status reset'),
        dict(rva=22720224, op='str w9, [x8, #0x20]', meaning='roomIndex = -1'),
    ]
    for step in steps:
        assert at[step['rva']] == step['op'], (step['rva'], at[step['rva']])
    return dict(method=dict(rva=row['rva'], size=row['size'],
                            signature=row['signature'].strip()),
                rules=[
                    dict(when='status <= RankUpIndexs[arenaRank]',
                         effect='arenaRank = min(arenaRank + 1, 9)',
                         evidence=[22719888, 22719892, 22720196, 22720208]),
                    dict(when='RankUpIndexs[arenaRank] < status <= RankDropIndexs[arenaRank]',
                         effect='rank unchanged', evidence=[22719960, 22719964]),
                    dict(when='status > RankDropIndexs[arenaRank]',
                         effect='arenaRank = max(arenaRank - 1, 0)',
                         evidence=[22719968, 22719972]),
                    dict(when='always', effect='status = -1 and roomIndex = -1 after '
                                               'grading', evidence=[22720216, 22720224]),
                ],
                status_is_a_placement=True,
                steps=steps)


def minutes_consumer():
    """`<IESetRankSetups>d__41`: SeasonTimes[i] goes straight into AddMinutes."""
    row = method('ArenaManager.<IESetRankSetups>d__41', 'MoveNext')
    at = {insn['rva']: insn['mnemonic'] + ' ' + insn['op_str']
          for insn in row['instructions']}
    facts = [
        dict(rva=22721052, op='ldr x8, [x8, #0x18]', meaning='SeasonTimes'),
        dict(rva=22721060, op='ldrsw x9, [x19, #0x28]', meaning='season index'),
        dict(rva=22721080, op='ldr w8, [x8, #0x20]', meaning='SeasonTimes[season]'),
        dict(rva=22721092, op='scvtf d0, w8', meaning='int -> double'),
        dict(rva=22721096, op='bl #0x20e6cf0', meaning='DateTime.AddMinutes(double)'),
        dict(rva=22721128, op='bl #0x2104440', meaning='Int64.ToString()'),
        dict(rva=22721132, op='stp x0, xzr, [x21, #0x18]',
             meaning='ArenaRankSetup.seasonEnd'),
        dict(rva=22721016, op='str x0, [x21, #0x10]',
             meaning='ArenaRankSetup.seasonStart'),
    ]
    for fact in facts:
        assert at[fact['rva']] == fact['op'], (fact['rva'], at[fact['rva']])
    assert AR.owner(0x20E6CF0)[1].startswith('public DateTime AddMinutes')
    return dict(method=dict(rva=row['rva'], size=row['size'],
                            signature=row['signature'].strip()),
                unit='minutes',
                chain=['SeasonTimes[season] (int)',
                       'scvtf d0, w8',
                       'DateTime.AddMinutes(double)',
                       'DateTime.ToBinary()',
                       'Int64.ToString()',
                       'ArenaRankSetup.seasonEnd (string)'],
                facts=facts)


def time_span_reader():
    """`<IEGetTimeSpan>d__19`: the served `seasonEnd` string is a ToBinary long."""
    row = method('ArenaManager.<IEGetTimeSpan>d__19', 'MoveNext')
    at = {insn['rva']: insn['mnemonic'] + ' ' + insn['op_str']
          for insn in row['instructions']}
    facts = [
        dict(rva=22717660, op='ldr x20, [x8, #0x18]',
             meaning='ArenaRankSetup.seasonEnd (string)'),
        dict(rva=22717688, op='bl #0x20c8a6c', meaning='Convert.ToInt64(string)'),
        dict(rva=22717732, op='bl #0x20e77ac', meaning='DateTime.FromBinary(long)'),
        dict(rva=22717760, op='blr x9', meaning='callback(DateTime)'),
    ]
    for fact in facts:
        assert at[fact['rva']] == fact['op'], (fact['rva'], at[fact['rva']])
    return dict(method=dict(rva=row['rva'], size=row['size'],
                            signature=row['signature'].strip()),
                reading='seasonEnd is not a date string; it is `DateTime.ToBinary()` '
                        'rendered with Int64.ToString(), so parsing it as a date fails '
                        'and parsing it as a long is exact',
                facts=facts)


def helpers():
    rows = []
    for rva, role, why in HELPERS:
        klass, signature = AR.owner(rva)
        assert signature and role.split('(')[0].split('.')[-1] in signature, (rva, signature)
        rows.append(dict(rva=rva, class_name=klass,
                         signature=signature.strip(), role=role, why=why))
    return rows


# --------------------------------------------------------- census, all raws
def census():
    """Every method in the eight dumped slices that reaches ArenaManager's statics."""
    paths = sorted(glob.glob(str(ROOT / 'reverse-engineering/raw/*535b0541/native.json.gz')))
    seen, methods = {}, 0
    for path in paths:
        blob = json.loads(gzip.decompress(Path(path).read_bytes()))
        slice_name = Path(path).parent.name
        methods += len(blob['methods'])
        for target in blob['methods']:
            roles, hits = {}, []
            for insn in target['instructions']:
                mnemonic, operand = insn['mnemonic'], insn['op_str']
                adrp = re.fullmatch(r'(x\d+), #(0x[0-9a-f]+)', operand)
                if mnemonic == 'adrp' and adrp:
                    roles[adrp.group(1)] = ('page', int(adrp.group(2), 0))
                    continue
                read = re.fullmatch(r'(x\d+), \[(x\d+)(?:, #(0x[0-9a-f]+))?\]', operand)
                if mnemonic in ('ldr', 'ldrsw') and read:
                    dest, base = read.group(1), read.group(2)
                    offset = int(read.group(3) or '0', 16)
                    role = roles.get(base)
                    if role and role[0] == 'page' and role[1] + offset == MANAGER_CELL:
                        roles[dest] = ('cell',)
                    elif role and role[0] == 'cell' and offset == 0:
                        roles[dest] = ('klass',)
                    elif role and role[0] == 'klass' and offset == STATICS_PTR:
                        roles[dest] = ('statics',)
                    elif role and role[0] == 'statics':
                        hits.append((insn['rva'], mnemonic, offset, operand))
                        roles.pop(dest, None)
                    else:
                        roles.pop(dest, None)
                    continue
                store = re.fullmatch(r'(?:[xw]\d+|wzr|xzr), \[(x\d+)(?:, #(0x[0-9a-f]+))?\]',
                                     operand)
                if mnemonic in ('str', 'strb', 'strh') and store:
                    if (roles.get(store.group(1)) or ('',))[0] == 'statics':
                        hits.append((insn['rva'], mnemonic,
                                     int(store.group(2) or '0', 16), operand))
                    continue
                named = re.match(r'(x\d+),', operand)
                if named and mnemonic not in ('cmp', 'tst'):
                    roles.pop(named.group(1), None)
            if not hits:
                continue
            key = (target['class_name'], target['signature'].strip(), target['rva'])
            slot = seen.setdefault(key, dict(class_name=key[0], signature=key[1],
                                             rva=key[2], slices=set(), access=set()))
            slot['slices'].add(slice_name)
            slot['access'].update(hits)

    rows = []
    for key in sorted(seen, key=lambda item: item[2]):
        slot = seen[key]
        access = [dict(rva=rva, mnemonic=mnemonic, offset=offset, operand=operand)
                  for rva, mnemonic, offset, operand in sorted(slot['access'])]
        offsets = sorted({row['offset'] for row in access})
        rows.append(dict(class_name=slot['class_name'], signature=slot['signature'],
                         rva=slot['rva'], slices=sorted(slot['slices']),
                         offsets=[hex(value) for value in offsets],
                         access=access))

    names = {hex(row['offset']): row['name']
             for row in load(STAGE1)['layout']['arena_manager']}
    touched = {value for row in rows for value in row['offsets']}
    silent = []
    for offset in (0x0, 0x4, 0x8, 0x10, 0x18, 0x20, 0x28, 0x30, 0x38):
        if hex(offset) not in touched:
            silent.append(dict(offset=hex(offset), field=names.get(hex(offset))))
    return dict(slices=len(paths), methods_dumped=methods,
                methods_touching=len(rows), rows=rows,
                touched_offsets=sorted(touched),
                never_touched=silent,
                scope='the eight dumps are slices of one libil2cpp build '
                      '(9cb038e8…); this census sees %d methods, not the whole '
                      'binary, so "never touched" means "not in these slices"' % methods)


def build():
    config_cctor = cctor()
    ladder = ladders()
    use = semantics()
    units = minutes_consumer()
    span = time_span_reader()
    table = helpers()
    cover = census()
    previous = load(PREV)

    checks = []
    checks.append(dict(check='cctor-rva-and-size',
                       passed=(config_cctor['rva'], config_cctor['size']) == (22726640, 164)))
    checks.append(dict(check='six-offsets-seven-values',
                       passed=[row['offset'] for row in config_cctor['writes']]
                              == [0x0, 0x8, 0x10, 0x14, 0x18, 0x1c]))
    checks.append(dict(check='packed-literal-is-two-ints',
                       passed=config_cctor['packed_literal']['decoded']
                              == {'MaxRoomCount': 50, 'MinRoomCount': 10}))
    checks.append(dict(check='summary-time-60f',
                       passed=config_cctor['summary_time'] == 60.0))
    checks.append(dict(check='is-open-false',
                       passed=config_cctor['writes'][-1]['source'] == {'value': False}))
    checks.append(dict(check='ten-seasons-in-both-ladders',
                       passed=(ladder['rank_split']['seasons'],
                               ladder['season_times']['seasons']) == (SEASONS, SEASONS)))
    checks.append(dict(check='down-bound-constant-45',
                       passed=set(ladder['observed']['down_by_season']) == {45}))
    checks.append(dict(check='up-bound-tightens',
                       passed=ladder['observed']['up_by_season']
                              == sorted(ladder['observed']['up_by_season'], reverse=True)))
    checks.append(dict(check='season-times-are-whole-days',
                       passed=all(row['whole_days'] for row in ladder['season_times']['rows'])))
    checks.append(dict(check='season-times-grow',
                       passed=ladder['observed']['minutes_by_season']
                              == sorted(ladder['observed']['minutes_by_season'])))
    checks.append(dict(check='unit-is-minutes',
                       passed=units['unit'] == 'minutes'
                              and 'AddMinutes' in units['chain'][2]))
    checks.append(dict(check='season-end-is-a-tobinary-long',
                       passed=any('FromBinary' in fact['meaning'] for fact in span['facts'])))
    checks.append(dict(check='three-promotion-rules',
                       passed=len(use['rules']) == 4
                              and 'min(arenaRank + 1, 9)' in use['rules'][0]['effect']))
    checks.append(dict(check='rank-clamped-to-9',
                       passed=any('cmp w9, #9' == fact['op'] for fact in use['steps'])))
    checks.append(dict(check='drop-check-reads-the-ring-below',
                       passed='ldr x10, [x9, #0x30]' in [fact['op']
                                                         for fact in use['steps']]))
    checks.append(dict(check='census-covers-eight-slices',
                       passed=cover['slices'] == 8 and cover['methods_dumped'] > 2000))
    checks.append(dict(check='nine-methods-touch-the-statics',
                       passed=cover['methods_touching'] == 9))
    checks.append(dict(check='summary-time-is-never-read',
                       passed='0x10' in [row['offset'] for row in cover['never_touched']]))
    checks.append(dict(check='helpers-resolve',
                       passed=len(table) == len(HELPERS)))
    checks.append(dict(check='reward-table-and-drop-bound-agree',
                       passed=previous['rewards'][0]['bands'][-1]['low'] == 46
                              and set(ladder['observed']['down_by_season']) == {45}))
    assert all(row['passed'] for row in checks), [row for row in checks
                                                 if not row['passed']]

    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='Every value here is a build constant of the original APK. `Board_Arena.'
             'GetConfigs` may overwrite `RankSplit`/`SeasonTime`/`SeasonTimes` at run '
             'time from the served config, so which ladder a live season used is '
             'MODEL_NOT_MEASURED runtime — what ships in the binary is what is decoded '
             'here.',
        provenance=dict(
            sources=[dict(path=rel, sha256=sha_file(rel))
                     for rel in (NATIVE, STRINGS, DUMP, PREV, STAGE1)],
            libil2cpp_sha256=load(NATIVE)['libil2cpp_sha256'],
            xapk_sha256=load(NATIVE)['xapk_sha256'],
            string_literals=len(strings())),
        arena_config=dict(
            cell=dict(hex=hex(CONFIG_CELL), decimal=CONFIG_CELL,
                      named_by='139 `layout.slots.arena_config`'),
            fields=[dict(offset=hex(row['offset']), field=row['name'])
                    for row in load(STAGE1)['layout']['arena_config']],
            cctor=config_cctor),
        ladders=ladder,
        units=units,
        season_end=span,
        semantics=use,
        helpers=table,
        census=cover,
        cross_checks=dict(
            season_times_are_minutes=True,
            season_times_whole_days=[row['whole_days'] for row in ladder['season_times']['rows']],
            down_bound=45,
            last_reward_band_low=previous['rewards'][0]['bands'][-1]['low'],
            first_reward_band_low=previous['rewards'][0]['bands'][0]['low'],
            season_lengths_days=ladder['observed']['days_by_season'],
            total_season_days=ladder['observed']['total_days']),
        checks=checks,
        confirmations=[
            dict(item='139 `ArenaConfig` = six static fields, `RankSplit` and '
                      '`SeasonTime` were left unread',
                 result='closed — both are literal strings with ten semicolon-separated '
                        'entries, and the other four fields are three immediates'),
            dict(item='139 `ArenaManager.SeasonSummaryTime` default 60.0',
                 result='confirmed and sourced — it is `ArenaConfig.SummaryTime` 60.0f '
                        '(0x42700000) copied through `GetConfigs`'),
            dict(item='151 left the unit of `SeasonTimes` unstated',
                 result='closed — minutes, via `DateTime.AddMinutes` at rva 34499824'),
            dict(item='151 reward bands stop at `51+`? no: they stop at 46-50',
                 result='consistent — the demote bound is 45 in all ten seasons, so '
                        '46-50 is exactly the band that stops paying and gets demoted'),
        ],
        open_items=[
            dict(item='which ladder a live season actually used',
                 blocking='`Board_Arena.GetConfigs` (rva 22782048) overwrites both '
                          'ladders from the served config; MODEL_NOT_MEASURED runtime'),
            dict(item='`SummaryTime` (60.0f) has no reader in the dumped slices',
                 blocking='the census sees 2 499 methods of one build; a reader may live '
                          'outside the eight slices — this is a bounded negative, not '
                          '"unused"'),
            dict(item='what the season start date is',
                 blocking='`seasonStart` is `DateTime.ToBinary()` of a value the game '
                          'computes at season creation; the binary ships no epoch'),
        ],
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='datas/l2_535b0541_arena_config_ladders.json.gz')
    args = parser.parse_args()
    payload = build()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    target.write_bytes(gzip.compress(blob, mtime=0))
    print(json.dumps(dict(
        bytes=target.stat().st_size,
        sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        seasons=payload['ladders']['rank_split']['seasons'],
        days=payload['cross_checks']['season_lengths_days'],
        up=payload['ladders']['observed']['up_by_season'],
        checks_passed=sum(1 for row in payload['checks'] if row['passed']),
        checks_total=len(payload['checks']))))


if __name__ == '__main__':
    main()
