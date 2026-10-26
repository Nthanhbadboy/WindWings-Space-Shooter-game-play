#!/usr/bin/env python3
"""`PVP_Manager..cctor`: the five static tables and the reserved PvP rules. STATIC only.

Report 127 read the numbers out of `.cctor` one literal at a time. This report
re-derives the whole routine from the *instruction stream plus the recorded
literal bytes*, and pins the invariant that makes the read-out checkable:

    Object..ctor sites in `.cctor`      = 53 = 10 SeasonRewards + 43 PVPReward
    List<T>.Add sites (reference T)      = 87 = 10 gift + 10 season + 14 medal rows
                                               + 10 star arrays + 43 rewards
    List<int>.Add sites                  = 90 = 6 star points + 14 x 6 medal columns
    InitializeArray calls                = 10 = the ten `MaxRankStars` arrays

The four counters come from the method body alone, so a table that is off by one
row breaks the identity. That is how the one correction below was found:
`AllRewards` has **43** rows, not 42 (rank 0 carries `lvl=1` *and* `lvl=2`). The
earlier read started at the second pool window; the first one
(`[0,1,100,0]`, VA 7835632) pairs with an `Object..ctor` exactly like every
other row.

Two of the rule fields are 8-byte stores of an **int pair**, not a `double`:
`pvpMaxLife/pointReduceDie` and `timePlay/timeStep` are declared `int` in
`dump.cs`, and the constant pools hold `03 00 00 00 dc 05 00 00` and
`a0 00 00 00 0a 00 00 00`. Both windows are pinned in
`reverse-engineering/raw/pvp-rules-535b0541/native.json.gz`, so the byte claim
is re-readable instead of being quoted from a report.

`MaxRankStars` stays unbound: the `InitializeArray` field-default data that the
pinned raw captured is metadata (words such as `0x8000000D`), not the int
values, and `ia-resolved.json` covers 17 methods — none of them PvP.
"""
import argparse
import gzip
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

META = 'reverse-engineering/raw/meta-rewards-535b0541/native.json.gz'
RULES = 'reverse-engineering/raw/pvp-rules-535b0541/native.json.gz'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'

CCTOR = 19916640            # PVP_Manager..cctor
STATICS_OFF = 0xB8          # klass->static_fields

OBJECT_CTOR = 0x2143330     # Object..ctor (shared by SeasonRewards and PVPReward)
GIFT_CTOR = 0x13BC614       # Gift..ctor()
LIST_CTOR = 0x1BD768C       # List<T>..ctor
INT_LIST_CTOR = 0x1B94514   # List<int>..ctor
ADD_REF = 0x1BD7E58         # List<T>.AddWithResize (reference T)
ADD_INT = 0x1B94D0C         # List<int>.AddWithResize
INIT_ARRAY = 0x205B07C      # RuntimeHelpers.InitializeArray

# One window per table: [start, end) in the method body.
REGIONS = {
    'seasons': (19917056, 19919772),      # 0x12FE900 .. 0x12FF39C  AllSeasonRewards
    'star_points': (19919776, 19920420),  # 0x12FF3A0 .. 0x12FF624  TournamentAddStarPoints
    'medals': (19920424, 19930240),       # 0x12FF628 .. 0x1301C80  TournamentRewardMedals
    'max_rank': (19930244, 19931460),     # 0x1301C84 .. 0x1302144  MaxRankStars
    'rewards': (19931464, 19936528),      # 0x1302148 .. 0x1303510  AllRewards
}

TABLE_FIELDS = ('AllSeasonRewards', 'TournamentAddStarPoints', 'TournamentRewardMedals',
                'MaxRankStars', 'AllRewards')

GIFT_TYPES = {0: 'Gcoins', 1: 'Gems', 2: 'Item0', 3: 'Item1', 4: 'Item2', 5: 'Item3',
              6: 'Overdrive', 7: 'Energy', 8: 'DeviceC', 9: 'DeviceB', 10: 'DeviceA',
              11: 'DeviceS', 12: 'DeviceSS'}


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


def call_target(insn):
    text = insn['op_str'].strip().lstrip('#')
    return int(text, 0) if re.fullmatch(r'(0x[0-9a-f]+|\d+)', text) else None


def written_regs(insn):
    """Registers an instruction writes (enough for the statics-base invalidation)."""
    if insn['mnemonic'] in ('str', 'strb', 'strh', 'stp', 'cmp', 'cbz', 'cbnz',
                            'tbz', 'tbnz', 'b', 'bl', 'ret', 'nop'):
        return set()
    head = insn['op_str'].split('[')[0]
    return {reg for reg in re.findall(r'\b([xw]\d+)\b', head)}


def method(blob, rva=CCTOR):
    rows = [row for row in blob['methods'] if row['rva'] == rva]
    assert len(rows) == 1, 'expected exactly one method at RVA %d' % rva
    return rows[0]


def in_region(rows, name):
    lo, hi = REGIONS[name]
    return [row for row in rows if lo <= row['rva'] < hi]


def count_calls(rows, target):
    return sum(1 for row in rows if row['mnemonic'] == 'bl' and call_target(row) == target)


def immediate(insn, reg):
    """`mov wN, #imm` -> int, tolerating decimal, hex and negative forms."""
    match = re.fullmatch(r'%s, #(-?0x[0-9a-f]+|-?\d+)' % reg, insn['op_str'])
    return int(match.group(1), 0) if match else None


def static_fields(dump_text):
    """Field name/type/offset straight from dump.cs (declaration order = layout order)."""
    block = dump_text.split('public class PVP_Manager : MonoBehaviour')[1]
    block = block.split('// Properties')[0]
    return [dict(name=name, type=type_, offset=int(offset, 16))
            for type_, name, offset in
            re.findall(r'public static ([\w<>\[\], .]+) (\w+); // 0x([0-9A-Fa-f]+)', block)]


def statics_writes(rows):
    """Every `str/strb` whose base is the `klass + 0xb8` statics pointer."""
    writes, base = [], None
    for row in rows:
        match = re.fullmatch(r'(x\d+), \[(x\d+), #0xb8\]', row['op_str'])
        if row['mnemonic'] == 'ldr' and match and match.group(1) == match.group(2):
            base = match.group(1)
            continue
        if base:
            hit = re.fullmatch(r'[^,]+(?:, [^,]+)?, \[%s(?:, #(0x[0-9a-f]+|-?\d+))?\]' % base,
                               row['op_str'])
            if row['mnemonic'] in ('str', 'strb') and hit:
                writes.append(dict(rva=row['rva'], mnemonic=row['mnemonic'],
                                   op_str=row['op_str'],
                                   offset=int(hit.group(1), 0) if hit.group(1) else 0))
            elif base in written_regs(row):
                base = None
    return writes


def pair_literal(rows, literals, store_rva, reg, search=64):
    """Bytes behind a `str <reg>,[<statics>,#off]`: nearest preceding `ldr <reg>`."""
    by_rva = {row['rva']: row for row in rows}
    by_load = {row['instruction_rva']: row for row in literals}
    for rva in range(store_rva - 4, store_rva - 4 * search, -4):
        row = by_rva.get(rva)
        if row is None or row['mnemonic'] != 'ldr':
            continue
        if not row['op_str'].startswith(reg + ', ['):
            continue
        hit = by_load.get(rva)
        assert hit, 'no pinned bytes for literal load at RVA %d' % rva
        return dict(load_rva=rva, va=hit['va'], hex=hit['hex'],
                    words=list(struct.unpack('<2i', bytes.fromhex(hit['hex']))))
    raise AssertionError('no literal load for %s before store RVA %d' % (reg, store_rva))


def immediate_value(rows, store_rva, reg, search=64):
    by_rva = {row['rva']: row for row in rows}
    for rva in range(store_rva - 4, store_rva - 4 * search, -4):
        row = by_rva.get(rva)
        if row is None or row['mnemonic'] != 'mov':
            continue
        value = immediate(row, reg)
        if value is not None:
            return dict(mov_rva=rva, value=value)
    raise AssertionError('no immediate for %s before store RVA %d' % (reg, store_rva))


def reserved_rules(rows, literals, fields, windows):
    """The scalar half of the statics block: six stores, two of them int pairs."""
    by_offset = {row['offset']: row for row in fields}
    pinned = {window['va']: window for window in windows}
    rules, pairs = [], []
    for write in statics_writes(rows):
        offset = write['offset']
        if offset < 0x28:
            continue
        field = by_offset[offset]
        op = write['op_str']
        row = dict(field=field['name'], offset=offset, type=field['type'], rva=write['rva'],
                   instruction=write['mnemonic'] + ' ' + op)
        if op.startswith('d0,') or op.startswith('d1,'):
            pair = pair_literal(rows, literals, write['rva'], op.split(',')[0])
            assert field['type'] == 'int', 'int-pair store to non-int field ' + field['name']
            partner = by_offset[offset + 4]
            assert partner['type'] == 'int'
            window = pinned[pair['va']]
            assert window['hex'] == pair['hex'] and window['length'] == 8
            row.update(kind='int_pair', value=pair['words'][0], partner=partner['name'],
                       partner_value=pair['words'][1], load_rva=pair['load_rva'],
                       pool_va=pair['va'], pool_hex=pair['hex'])
            pairs.append(dict(store_rva=write['rva'], mnemonic=write['mnemonic'],
                              hex=pair['hex'], words=pair['words'],
                              fields=[field['name'], partner['name']],
                              pool_va=pair['va'], load_rva=pair['load_rva']))
        elif write['mnemonic'] == 'strb':
            assert op.startswith('wzr'), op
            row.update(kind='byte_zero', value=False)
        elif 'xzr' in op:
            row.update(kind='zero', value=None)
        else:
            reg = op.split(',')[0]
            assert reg.startswith('w'), op
            found = immediate_value(rows, write['rva'], reg)
            if field['type'] == 'float':
                row.update(kind='float_bits',
                           value=struct.unpack('<f', struct.pack('<I', found['value']))[0],
                           bits=found['value'], mov_rva=found['mov_rva'])
            else:
                row.update(kind='immediate', value=found['value'], mov_rva=found['mov_rva'])
        rules.append(row)
    assert len(pinned) == 2
    return rules, pairs


def pool_words(rows_by_rva, literals_by_rva, rva, width):
    hit = literals_by_rva.get(rva)
    if not hit or len(bytes.fromhex(hit['hex'])) != width:
        return None
    raw = bytes.fromhex(hit['hex'])
    words = list(struct.unpack('<%di' % (width // 4), raw))
    return dict(rva=rva, va=hit['va'], hex=hit['hex'], words=words)


def seasons(rows, literals):
    """`new SeasonRewards(rankStart, rankEnd, new List<Gift>{ new Gift(type, number) })`."""
    by_rva = {row['rva']: row for row in rows}
    by_load = {row['instruction_rva']: row for row in literals}
    ctors = [row['rva'] for row in rows
             if row['mnemonic'] == 'bl' and call_target(row) == OBJECT_CTOR]
    gift_ctors = [row['rva'] for row in rows
                  if row['mnemonic'] == 'bl' and call_target(row) == GIFT_CTOR]
    assert len(ctors) == len(gift_ctors) == 10, (len(ctors), len(gift_ctors))
    entries = []
    for index, ctor_rva in enumerate(ctors):
        gift_ctor = max(rva for rva in gift_ctors if rva < ctor_rva)
        gift = None
        for probe in range(gift_ctor + 4, gift_ctor + 4 * 8, 4):
            gift = pool_words(by_rva, by_load, probe, 8)
            if gift:
                break
        assert gift and len(gift['words']) == 2, 'no gift literal after RVA %d' % gift_ctor
        rank = None
        for probe in range(ctor_rva + 4, ctor_rva + 4 * 14, 4):
            insn = by_rva.get(probe)
            if insn is None:
                continue
            if insn['mnemonic'] == 'movi' and insn['op_str'] == 'v0.2s, #1':
                rank = dict(rva=probe, va=None, hex=None, words=[1, 1], kind='movi')
                break
            if insn['mnemonic'] == 'ldr' and insn['op_str'].startswith('d0, ['):
                found = pool_words(by_rva, by_load, probe, 8)
                if found:
                    rank = dict(found, kind='pool')
                    break
        assert rank and len(rank['words']) == 2, 'no rank literal after RVA %d' % ctor_rva
        entries.append(dict(rank_start=rank['words'][0], rank_end=rank['words'][1],
                            rank_kind=rank['kind'], rank_rva=rank['rva'],
                            rank_pool_va=rank['va'], rank_pool_hex=rank['hex'],
                            ctor_rva=ctor_rva,
                            gifts=[dict(type=gift['words'][0], number=gift['words'][1],
                                        type_name=GIFT_TYPES.get(gift['words'][0], '?'),
                                        load_rva=gift['rva'], pool_va=gift['va'],
                                        pool_hex=gift['hex'])]))
    return entries


def int_adds(rows, region):
    """`mov w1,#imm` + `bl List<int>.AddWithResize` pairs, in body order."""
    lo, hi = REGIONS[region]
    out = []
    for index, row in enumerate(rows):
        if row['mnemonic'] != 'bl' or call_target(row) != ADD_INT:
            continue
        if not lo <= row['rva'] < hi:
            continue
        value = None
        for back in range(index - 1, max(-1, index - 5), -1):
            value = immediate(rows[back], 'w1')
            if value is not None:
                break
        assert value is not None, 'int add without a value at RVA %d' % row['rva']
        out.append(dict(rva=row['rva'], value=value))
    return out


def medals(rows):
    lo, hi = REGIONS['medals']
    starts = [row['rva'] for row in rows
              if row['mnemonic'] == 'bl' and call_target(row) == INT_LIST_CTOR
              and lo <= row['rva'] < hi]
    adds = int_adds(rows, 'medals')
    out = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else hi
        out.append(dict(ctor_rva=start,
                        values=[add['value'] for add in adds if start < add['rva'] < end]))
    return out


def rewards(rows, literals):
    """`new PVPReward(rank, lvl, medal, gem)`: one 16-byte pool window per row."""
    by_rva = {row['rva']: row for row in rows}
    by_load = {row['instruction_rva']: row for row in literals}
    out = []
    for row in rows:
        if row['mnemonic'] != 'bl' or call_target(row) != OBJECT_CTOR:
            continue
        load = None
        for probe in range(row['rva'] - 4 * 3, row['rva'] + 4 * 4, 4):
            insn = by_rva.get(probe)
            if insn is None or insn['mnemonic'] != 'ldr':
                continue
            if not insn['op_str'].startswith('q0, ['):
                continue
            load = pool_words(by_rva, by_load, probe, 16)
            if load:
                break
        assert load and len(load['words']) == 4, 'no reward literal at RVA %d' % row['rva']
        out.append(dict(rank=load['words'][0], level=load['words'][1],
                        medal=load['words'][2], gem=load['words'][3],
                        ctor_rva=row['rva'], load_rva=load['rva'],
                        pool_va=load['va'], pool_hex=load['hex']))
    return out


def build_payload():
    meta, rules_raw = load(META), load(RULES)
    body = method(meta)
    rows, literals = body['instructions'], body['literals']
    dump = gzip.open(ROOT / DUMP, 'rt', encoding='utf-8', errors='replace').read()
    fields = static_fields(dump)

    rule_rows, pairs = reserved_rules(rows, literals, fields, rules_raw['rodata_windows'])
    by_name = {row['field']: row for row in rule_rows}
    assert sorted(by_name) == ['IsOpen', 'RankShowCount', 'pvpDatas', 'pvpMaxLife',
                               'pvpTimeScale', 'timePlay'], sorted(by_name)
    assert (by_name['pvpMaxLife']['partner'], by_name['timePlay']['partner']) == \
        ('pointReduceDie', 'timeStep')
    assert (by_name['pvpMaxLife']['value'], by_name['pvpMaxLife']['partner_value']) == (3, 1500)
    assert (by_name['timePlay']['value'], by_name['timePlay']['partner_value']) == (160, 10)
    assert by_name['RankShowCount']['value'] == 100
    assert by_name['pvpTimeScale']['value'] == 1.0
    assert by_name['IsOpen']['value'] is False and by_name['pvpDatas']['value'] is None
    assert [(row['field'], row['offset']) for row in rule_rows] == [
        ('pvpMaxLife', 0x28), ('RankShowCount', 0x30), ('pvpDatas', 0x38),
        ('timePlay', 0x40), ('pvpTimeScale', 0x48), ('IsOpen', 0x4C)], rule_rows

    season_rows = seasons(in_region(rows, 'seasons'), literals)
    assert [row['rank_start'] for row in season_rows] == [1, 2, 4, 6, 11, 51, 101, 201, 501, 1251]
    assert [row['rank_end'] for row in season_rows] == [1, 3, 5, 10, 50, 100, 200, 500, 1250, 3000]
    for left, right in zip(season_rows, season_rows[1:]):
        assert left['rank_end'] + 1 == right['rank_start'], (left, right)
    assert [row['gifts'][0]['type'] for row in season_rows] == [1] * 10
    assert [row['gifts'][0]['number'] for row in season_rows] == \
        [2000, 1000, 500, 300, 200, 150, 100, 80, 50, 20]

    star_points = [add['value'] for add in int_adds(rows, 'star_points')]
    assert star_points == [25, 10, 5, -1, -6, -12], star_points

    medal_rows = medals(rows)
    assert len(medal_rows) == 14 and all(len(row['values']) == 6 for row in medal_rows)
    assert medal_rows[0]['values'] == [20, 12, 8, 5, 3, 2]
    assert medal_rows[-1]['values'] == [100, 60, 40, 25, 15, 10]

    init_arrays = [row for row in body['initialize_arrays']
                   if REGIONS['max_rank'][0] <= row['initialize_rva'] < REGIONS['max_rank'][1]]
    lengths = [row['length'] for row in init_arrays]
    assert lengths == [3, 3, 4, 4, 5, 5, 5, 5, 5, 5], lengths

    reward_rows = rewards(in_region(rows, 'rewards'), literals)
    assert len(reward_rows) == 43, len(reward_rows)
    assert (reward_rows[0]['rank'], reward_rows[0]['level'], reward_rows[0]['medal'],
            reward_rows[0]['gem']) == (0, 1, 100, 0)
    for row in reward_rows:
        assert row['medal'] == 100 * (row['rank'] + 1), row
        assert (row['gem'] != 0) == (row['level'] == 0), row
    assert sorted({row['rank'] for row in reward_rows}) == list(range(10))

    counts = {}
    for name in REGIONS:
        block = in_region(rows, name)
        counts[name] = dict(object_ctor=count_calls(block, OBJECT_CTOR),
                            gift_ctor=count_calls(block, GIFT_CTOR),
                            add_ref=count_calls(block, ADD_REF),
                            add_int=count_calls(block, ADD_INT),
                            int_list_ctor=count_calls(block, INT_LIST_CTOR),
                            list_ctor=count_calls(block, LIST_CTOR),
                            initialize_array=count_calls(block, INIT_ARRAY))
    totals = {key: sum(block[key] for block in counts.values()) for key in counts['seasons']}
    assert totals['object_ctor'] == 53 == 10 + 43
    assert totals['add_ref'] == 87 == 10 + 10 + 14 + 10 + 43
    assert totals['add_int'] == 90 == 6 + 14 * 6
    assert totals['initialize_array'] == 10
    assert totals['gift_ctor'] == 10 and totals['int_list_ctor'] == 15

    writes = statics_writes(rows)
    assert len(writes) == 11, [(w['offset'], w['rva']) for w in writes]
    by_name = {row['name']: row for row in fields}
    table_sites = {}
    for write in writes:
        for field in fields:
            if field['offset'] == write['offset'] and field['name'] in TABLE_FIELDS:
                table_sites[field['name']] = write['rva']
    assert sorted(table_sites) == sorted(TABLE_FIELDS), table_sites
    assert table_sites == {'AllSeasonRewards': 19919772, 'TournamentAddStarPoints': 19920420,
                           'TournamentRewardMedals': 19930240, 'MaxRankStars': 19931460,
                           'AllRewards': 19936528}, table_sites

    return dict(
        schema=1,
        evidence='STATIC_ONLY_ORIGINAL_APK',
        note='Every number below is a build-time literal of the original APK. How a match '
             'really runs (tick length, network jitter, how remote config overrides these '
             'defaults) is MODEL_NOT_MEASURED runtime.',
        provenance=dict(
            xapk_sha256=meta['xapk_sha256'], libil2cpp_sha256=meta['libil2cpp_sha256'],
            dump_sha256=meta['dump_sha256'],
            sources=[dict(path=META, sha256=sha_file(META), role='PVP_Manager..cctor body'),
                     dict(path=RULES, sha256=sha_file(RULES),
                          role='two pinned 8-byte rule literals'),
                     dict(path=DUMP, sha256=sha_file(DUMP),
                          role='field declarations: int vs double, class shapes')]),
        method=dict(class_name=body['class_name'], signature=body['signature'].strip(),
                    rva=body['rva'], size=body['size'], sha256=body['sha256'],
                    boundary=meta['boundary']),
        statics=dict(base_offset=STATICS_OFF, pointer_from='PVP_Manager klass + 0xb8',
                     fields=fields, table_write_sites=table_sites, write_count=len(writes)),
        rules=dict(fields=rule_rows, coalesced_int_pairs=pairs,
                   read_as='pvpMaxLife=3 lives, -1500 points on death, 160 s match, '
                           '10 s step, 1.0x time scale, rank board shows 100 rows, '
                           'IsOpen=false, pvpDatas=null until LoadRemoteConfigs fills it'),
        tables=dict(
            all_season_rewards=dict(field='AllSeasonRewards', type='List<SeasonRewards>',
                                    assign_rva=table_sites['AllSeasonRewards'],
                                    entries=season_rows),
            tournament_add_star_points=dict(field='TournamentAddStarPoints', type='List<int>',
                                            assign_rva=table_sites['TournamentAddStarPoints'],
                                            values=star_points),
            tournament_reward_medals=dict(field='TournamentRewardMedals',
                                          type='List<List<int>>',
                                          assign_rva=table_sites['TournamentRewardMedals'],
                                          rows=[row['values'] for row in medal_rows],
                                          row_ctor_rvas=[row['ctor_rva'] for row in medal_rows]),
            max_rank_stars=dict(field='MaxRankStars', type='List<int[]>',
                                assign_rva=table_sites['MaxRankStars'], lengths=lengths,
                                initialize_rvas=[row['initialize_rva'] for row in init_arrays],
                                values=None,
                                blocking='InitializeArray field-default data at the pinned '
                                         'addends is metadata (words 0x8000000D, '
                                         '0x8000000F, ...), not the int values; resolving it '
                                         'needs the <PrivateImplementationDetails> blob for '
                                         'this class, which ia-resolved.json does not cover '
                                         '(17 methods, none PvP).'),
            all_rewards=dict(field='AllRewards', type='List<PVPReward>',
                             assign_rva=table_sites['AllRewards'], entries=reward_rows),
        ),
        counts=counts,
        totals=totals,
        cross_checks=dict(
            rewards=len(reward_rows), seasons=len(season_rows), medal_rows=len(medal_rows),
            star_arrays=len(lengths), medal_columns=sum(len(row['values']) for row in medal_rows),
            identity='object_ctor 53 = 10 SeasonRewards + 43 PVPReward; add_ref 87 = 10 gifts '
                     '+ 10 seasons + 14 medal rows + 10 star arrays + 43 rewards; add_int 90 = '
                     '6 star points + 84 medal cells; initialize_array 10 = the ten '
                     'MaxRankStars arrays'),
        corrections=[dict(
            item='AllRewards row count',
            report_127='42 rows, starting at [0,2,100,0]; "rank 0 only has lvl=2"',
            measured='43 rows, starting at [0,1,100,0]; rank 0 has lvl=1 and lvl=2',
            evidence='43 `bl Object..ctor` + 43 `str q0,[x20,#0x10]` + 43 list adds inside '
                     'RVA 19931464..19936528; the window at VA 7835632 (hex '
                     '00000000010000006400000000000000) is stored into the object built at '
                     'RVA 19931500 exactly like every other row, and 53 = 10 SeasonRewards + '
                     '43 PVPReward closes the object count',
            impact='PVPReward(rank=0, lvl=1, medal=100, gem=0) exists and belongs in any '
                   'reward lookup table')],
        not_decoded=[
            dict(item='MaxRankStars values',
                 blocking='field-default blob unresolved (see tables.max_rank_stars.blocking)'),
            dict(item='how remote config rewrites these defaults',
                 blocking='PVP_Manager/ArenaManager LoadRemoteConfigs read Firebase; the '
                          'shipped defaults are static, the served values are '
                          'MODEL_NOT_MEASURED runtime'),
            dict(item='what the 14 medal rows are indexed by',
                 blocking='PVP_Endgame.GetTournamentMedalReward(rank, index) indexes '
                          '[rank][index]; the meaning of rank 0..13 is not in the cctor'),
            dict(item='paired-field independence for pvpMaxLife/pointReduceDie and '
                      'timePlay/timeStep',
                 blocking='the compiler merged each pair into one 8-byte store, so the two '
                          'ints always travel together in build data; whether the game ever '
                          'rewrites one without the other is runtime (MODEL_NOT_MEASURED)'),
        ],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_pvp_manager_rules.json.gz')
    args = parser.parse_args()
    payload = build_payload()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                                sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          rules={row['field']: row['value']
                                 for row in payload['rules']['fields']},
                          seasons=len(payload['tables']['all_season_rewards']['entries']),
                          rewards=len(payload['tables']['all_rewards']['entries']),
                          medals=len(payload['tables']['tournament_reward_medals']['rows']))))


if __name__ == '__main__':
    main()
