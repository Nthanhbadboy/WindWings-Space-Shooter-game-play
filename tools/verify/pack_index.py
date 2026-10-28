#!/usr/bin/env python3
"""Pack index rules for daily/weekly rewards (build 1.3.118). No code executed.

Follow-up to report 128. Answers two questions that #30 left marked, using only
pinned original-APK bytes:

* which numeric index means which `Shop_Pack` field (`GetValueByIndex`), and
* how a box is drawn from a pack (`GetListIndexRewards` /
  `GetListIndexRandomRewards` / `AddPacks` / `get_BoxRewards` / accessors).

Two sources, both pinned by SHA here:

* `reverse-engineering/raw/meta-rewards-535b0541/native.json.gz` — the #30 raw
  (`Shop_Pack` methods). Its SHA must stay `e91a8c76…`, so this tool never writes
  to it.
* `reverse-engineering/raw/pack-index-535b0541/native.json.gz` — minimal raw with
  `Board_ShopEnergy` (energy→gem exchange) and one pinned read-only window holding
  the `GetValueByIndex` jump table.

The jump table cannot be inferred from instruction order alone (a permuted table
would look identical), so the table bytes are pinned and each entry is verified
against the case body that follows it.
"""
import argparse
import gzip
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

NATIVE = 'reverse-engineering/raw/meta-rewards-535b0541/native.json.gz'
INDEX_RAW = 'reverse-engineering/raw/pack-index-535b0541/native.json.gz'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'

VALUE_BASE = 0x1344280          # first landing pad of GetValueByIndex
VALUE_MAX_INDEX = 0x1a          # cmp w1, #0x1a
FIELD_BASE = 0x10               # first int field of Shop_Pack
SWITCH_TABLE_VA = 0x779EFA      # adrp #0x779000 + add #0xefa
PACK_CLASS = 'Shop_Pack'


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def load(raw_path):
    return json.loads(gzip.decompress((ROOT / raw_path).read_bytes()))


def dump_text():
    return gzip.decompress((ROOT / DUMP).read_bytes()).decode()


def method(native, cls, name):
    for entry in native['methods']:
        if entry['class_name'] == cls and name in entry['signature']:
            return entry
    raise KeyError(f'{cls}.{name} not in raw')


def pack_fields():
    """[(index, offset, name)] for the 27 int32 fields an index can name."""
    text = dump_text()
    match = re.search(r'^[^\n]*?\bclass ' + PACK_CLASS + r'(?=[\s:<])[^\n]*// TypeDefIndex: \d+$',
                      text, re.M)
    depth, pos = 0, text.index('{', match.start())
    for end in range(pos, len(text)):
        if text[end] == '{':
            depth += 1
        elif text[end] == '}':
            depth -= 1
            if depth == 0:
                break
    fields = {}
    for line in text[pos:end].split('\n'):
        field = re.match(r'\s*public\s+int\s+(\w+);\s*//\s*0x([0-9A-Fa-f]+)\s*$', line)
        if field:
            fields[int(field.group(2), 16)] = field.group(1)
    out = []
    for index in range(VALUE_MAX_INDEX + 1):
        offset = FIELD_BASE + 4 * index
        out.append((index, offset, fields[offset]))
    return out, fields


def jump_table(index_raw):
    windows = index_raw.get('rodata_windows') or []
    window = next((w for w in windows if w['va'] == SWITCH_TABLE_VA), None)
    if window is None:
        raise ValueError('pinned jump table window missing')
    return window


def value_index(meta, index_raw):
    """index -> field, proven by the pinned table plus each landing pad's load."""
    fields, all_fields = pack_fields()
    window = jump_table(index_raw)
    entries = list(bytes.fromhex(window['hex']))
    if len(entries) != VALUE_MAX_INDEX + 1:
        raise ValueError(f'jump table has {len(entries)} entries, expected {VALUE_MAX_INDEX + 1}')
    body = method(meta, PACK_CLASS, 'GetValueByIndex')
    by_rva = {insn['rva']: insn for insn in body['instructions']}
    rows = []
    for index, offset, name in fields:
        target = VALUE_BASE + 4 * entries[index]
        load = by_rva.get(target + 4)
        if load is None or load['mnemonic'] != 'ldr' or load['op_str'] != f'w0, [x0, #0x{offset:x}]':
            raise ValueError(f'jump table entry {index} does not land on #{offset:#x}: {target:#x}')
        rows.append(dict(index=index, offset=hex(offset), field=name,
                         jump_entry=entries[index], target_rva=target))
    if entries != sorted(entries) or len(set(entries)) != len(entries):
        raise ValueError('jump table is not a strictly increasing permutation of landing pads')
    unchecked = [name for offset, name in sorted(all_fields.items())
                 if offset < FIELD_BASE or offset > FIELD_BASE + 4 * VALUE_MAX_INDEX]
    return dict(
        entries=rows, max_index=VALUE_MAX_INDEX,
        out_of_range=dict(rule='index < 0 or index > 26 returns 0 (b.hi on cmp w1,#0x1a)',
                          instruction_rva=body['rva'] + 0x34),
        ignored_fields=unchecked,
        jump_table=dict(va=SWITCH_TABLE_VA, length=window['length'], hex=window['hex'],
                        sha256=window['sha256'], entries=entries,
                        validated='entry i -> landing pad (base + 4*entry) loads [x0,#0x10+4i]'))


def pack_values(shop_packs):
    """{table: [[27 values] per row]} straight from the #30 decode."""
    fields, _ = pack_fields()
    names = [name for _, _, name in fields]
    out = {}
    for table, node in shop_packs.items():
        rows = node if isinstance(node, list) else [node]
        if not (rows and isinstance(rows[0], dict)):
            continue
        if '_list' in node if isinstance(node, dict) else False:
            continue
        out[table] = [[int(row.get(name) or 0) for name in names] for row in rows]
    for table in ('allVipRewards', 'allVipRewardsFree', 'allFightBossRewards',
                  'allLogInRewardsRoot', 'allLogInRewardsRoot2'):
        node = shop_packs.get(table) or {}
        rows = node.get('_list') or []
        out[table] = [[int(row.get(name) or 0) for name in names] for row in rows]
    return dict(values=out, names=names)


def index_list(values):
    """GetListIndexRewards: indices whose value is >= 1 (zeros dropped)."""
    return [i for i, value in enumerate(values) if value >= 1]


def exchange_rate(index_raw):
    """`GetExchangeGemsFromEnergy`: pro-only, truncating (energy * 30) / 100."""
    body = method(index_raw, 'Board_ShopEnergy', 'GetExchangeGemsFromEnergy')
    op = [f"{insn['mnemonic']} {insn['op_str']}" for insn in body['instructions']]
    if 'mov w8, #0x1e' not in op or 'movk w9, #0x51eb, lsl #16' not in op:
        raise ValueError('energy exchange no longer matches the decoded magic sequence')
    if 'asr x8, x8, #0x24' not in op or 'smull x8, w8, w9' not in op:
        raise ValueError('energy exchange divisor changed')
    return dict(
        rva=body['rva'], bytes=body['size'],
        rule='IsProVersion() ? (_energy * 30) / 100 (int32, truncating) : -1',
        numerator=30, denominator=100,
        magic=dict(multiplier='0x51eb851f', shift=36,
                   note='signed magic divide by 100 with sign-bit correction'),
        non_pro_value=-1)


def build():
    meta = load(NATIVE)
    index_raw = load(INDEX_RAW)
    from meta_rewards import build as build_meta
    packs = pack_values(build_meta()['shop_packs'])

    vi = value_index(meta, index_raw)
    index_rewards = method(meta, PACK_CLASS, 'GetListIndexRewards')
    index_random = method(meta, PACK_CLASS, 'GetListIndexRandomRewards')
    add_packs = method(meta, PACK_CLASS, 'AddPacks')
    box_rewards = method(meta, PACK_CLASS, 'get_BoxRewards')
    login_rewards = method(meta, PACK_CLASS, 'get_allLogInRewards')
    bp_packs = method(meta, PACK_CLASS, 'get_allBattlePassPacks')

    names = packs['names']
    samples = {}
    for table in ('PackDaily', 'PackWeekly', 'PackDailyVideo', 'PackSpec'):
        samples[table] = [dict(row=i, nonzero=[names[j] for j in index_list(values)],
                               indices=index_list(values))
                          for i, values in enumerate(packs['values'][table])]

    energy = exchange_rate(index_raw)

    def convert(rows):
        """What get_BoxRewards/get_allLogInRewards do to pack Energy for pro users."""
        out = []
        for row in rows:
            values = dict(zip(names, row))
            gems_before = values['Gems']
            gained = 0
            if values['Energy'] >= 1:
                gained = (values['Energy'] * energy['numerator']) // energy['denominator']
            out.append(dict(Gems_before=gems_before, Energy=values['Energy'], gems_gained=gained,
                            Gems_after=gems_before + gained))
        return out

    boxes = convert(packs['values']['BoxRewardsRoot'])
    login_a = convert(packs['values']['allLogInRewardsRoot'])
    login_b = convert(packs['values']['allLogInRewardsRoot2'])

    double_index = 13
    double_field = next(name for index, _, name in vi_entries(vi) if index == double_index)

    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='Static decode only. Draws use UnityEngine.Random at runtime, so no sequence '
             'is claimed here; MODEL_NOT_MEASURED runtime for any actual drop.',
        provenance=dict(
            sources=[dict(path=path, sha256=sha_file(path)) for path in (NATIVE, INDEX_RAW, DUMP)],
            xapk_sha256=index_raw['xapk_sha256'], libil2cpp_sha256=index_raw['libil2cpp_sha256'],
            pack_index_methods=len(index_raw['methods']),
            families=index_raw['families']),
        value_index=vi,
        rules=dict(
            get_value_by_index=dict(
                rva=method(meta, PACK_CLASS, 'GetValueByIndex')['rva'],
                bytes=method(meta, PACK_CLASS, 'GetValueByIndex')['size'],
                rule='switch (index) 0..26 -> Shop_Pack int field at 0x10 + 4*index; else 0'),
            get_list_index_rewards=dict(
                rva=index_rewards['rva'], bytes=index_rewards['size'],
                rule='scan indices 0..26 in field order, append index when value >= 1; '
                     'ToArray of the index list; empty list when every value is 0'),
            get_list_index_random_rewards=dict(
                rva=index_random['rva'], bytes=index_random['size'],
                rule='pool = indices 0..26 with value >= 1; then _numberRewards draws of '
                     'Random.Range(0, pool.Count) mapped through pool -> GetValueByIndex',
                duplicates='allowed: each slot draws independently (with replacement)',
                weight_bias=dict(index=double_index, field=double_field,
                                 condition='typeBox == 0', effect='index appended twice to the pool'),
                empty_pool='pool.Count == 0 makes Random.Range(0,0) = 0 and the following '
                           'List.get_Item(0) out of range: not statically determined'),
            add_packs=dict(
                rva=add_packs['rva'], bytes=add_packs['size'],
                rule='_toPack += _addPack for the 27 indexed int fields (0x10..0x78) only; '
                     'multipleBonus (0x7C) is not added',
                covered='0x10-0x78', excluded=[name for offset, name in
                                               sorted(pack_fields()[1].items())
                                               if offset > FIELD_BASE + 4 * VALUE_MAX_INDEX]),
            box_rewards=dict(
                rva=box_rewards['rva'], bytes=box_rewards['size'],
                rule='if (GameDatas.IsProVersion()) foreach pack in BoxRewardsRoot: '
                     'if (pack.Energy >= 1) { pack.Gems += GetExchangeGemsFromEnergy(pack.Energy); '
                     'pack.Energy = 0; } return BoxRewardsRoot',
                mutates_static=True, non_pro='returns the authored table untouched'),
            login_rewards=dict(
                rva=login_rewards['rva'], bytes=login_rewards['size'],
                rule='list = Board_GiftLogin.get_ResetDailyGiftCount() == 0 ? '
                     'allLogInRewardsRoot : allLogInRewardsRoot2; if IsProVersion() apply the same '
                     'energy->gem conversion over that list; return list'),
            battle_pass_packs=dict(
                rva=bp_packs['rva'], bytes=bp_packs['size'],
                rule='if (GameDatas.IsProVersion()) for each pair in allBattlePassPacksRoot, '
                     'for slot 0..1 apply the energy->gem conversion'),
        ),
        call_targets=dict(
            get_value_by_index='switch dispatch (adr/br x10)',
            random_range=dict(rva=0x277D2C0, name='UnityEngine.Random.Range(int,int)'),
            pro_gate=dict(rva=0x13266FC, name='GameDatas.IsProVersion'),
            energy_exchange=dict(rva=0x12883C0, name='Board_ShopEnergy.GetExchangeGemsFromEnergy'),
            login_variant=dict(rva=0x129BC04, name='Board_GiftLogin.get_ResetDailyGiftCount'),
            list_add=dict(rva=0x1B94D0C, name='List<int>.Add'),
            list_item=dict(rva=0x1B94A1C, name='List<int>.get_Item'),
            list_to_array=dict(rva=0x1B965F8, name='List<int>.ToArray'),
        ),
        energy_economy=dict(
            exchange=energy,
            cost_buy_energy=dict(rva=0x12881D4, value=30),
            value_buy_energy=dict(rva=0x12881DC, value=50),
            value_free_energy=dict(rva=0x12883B8, value=30),
        ),
        samples=dict(
            index_lists=samples,
            boxes_energy_conversion=boxes,
            login_root_energy_conversion=login_a,
            login_root2_energy_conversion=login_b,
        ),
        not_decoded=[
            dict(item='typeBox runtime value',
                 blocking='Board_QuestRewards.typeBox is 0 in .cctor but assigned per box at '
                          'runtime; which boxes use 0 is MODEL_NOT_MEASURED runtime'),
            dict(item='Board_GiftLogin.ResetDailyGiftCount value',
                 blocking='reads player state (daily reset counter); runtime only'),
            dict(item='actual random draws',
                 blocking='UnityEngine.Random.Range is seeded at runtime; no sequence is claimed'),
        ],
    )


def vi_entries(vi):
    return [(row['index'], row['offset'], row['field']) for row in vi['entries']]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_pack_index.json.gz')
    args = parser.parse_args()
    payload = build()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                                sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          entries=len(payload['value_index']['entries']),
                          exchange=payload['energy_economy']['exchange']['rule'])))


if __name__ == '__main__':
    main()
