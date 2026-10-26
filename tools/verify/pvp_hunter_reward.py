#!/usr/bin/env python3
"""The PvP hunter reward table: six slots, which one pays keys. STATIC only.

Report 132 left one line open: "PvP stage reward types and amounts". The types
turn out to be a compile-time blob, so half of that closes without new native
recovery:

    Board_PVP..ctor -> new T[6] -> RuntimeHelpers.InitializeArray(0x205B07C)
                    -> <PrivateImplementationDetails> field default
                    -> rewardIndexs[0..5]

`rewardIndexs` is identified by content, not by a metadata token (the usage
table is not pinned): among **all** `<PrivateImplementationDetails>` blobs in
`field-defaults.json`, exactly one six-element int blob has every value inside
the set of reward ids `OnClickHunterCollect` actually handles. The two
independent constraints (blob length from `new T[6]`, value domain from the
dispatch table) leave a single candidate.

The amounts (`rewardValues`) and icon scales (`rewardScales`) stay unbound:
same constructor, but their blobs have no content constraint strong enough to
name them. That is recorded as a blocker, not guessed.
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

import key_sources as KS  # noqa: E402

GRANT = 'reverse-engineering/raw/key-grant-535b0541/native.json.gz'
PVP = 'reverse-engineering/raw/pvp-dispatch-535b0541/native.json.gz'
DEFAULTS = 'reverse-engineering/il2cpp/field-defaults.json'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'

CTOR = 19796420           # Board_PVP..ctor
SETUP = 19791640          # Board_PVP.SetupHunters
COLLECT = 19792936        # Board_PVP.OnClickHunterCollect
IS_COLLECTED = 19792764   # Board_PVP.IsCollected
SEASON_GET = 19784460     # Board_PVP.get_SeasonProgress
SEASON_SET = 19794028     # Board_PVP.set_SeasonProgress
SEASON_DIES = 19784352    # Board_PVP.get_SeasonDies

INITIALIZE_ARRAY = 0x205B07C
NEWARR = 0x110D09C
FIELDS = (('rewardIndexs', 0x198), ('rewardValues', 0x1A0), ('rewardScales', 0x1A8),
          ('allBetCoinValues', 0x208), ('allBetGemValues', 0x210), ('allBetMedalValues', 0x218))


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


def call_target(insn):
    return int(insn['op_str'].lstrip('#'), 0)


def handler_types(pvp, by_rva):
    """reward ids OnClickHunterCollect can serve: switch cases + the two ids
    handled before the switch (0 Coins, 1 Gems)."""
    window = pvp['rodata_windows'][0]
    table = list(bytes.fromhex(window['hex']))
    insns = by_rva[COLLECT]['instructions']
    names = KS.dump_names(KS.dump_lines())
    base = next(int(i['op_str'].split('#')[-1], 0) for i in insns if i['mnemonic'] == 'adr')
    select = next(i for i in insns if i['mnemonic'] == 'sub'
                  and i['op_str'].startswith('w9, w8, #'))
    first = int(select['op_str'].rsplit('#', 1)[1], 0)
    span = next(i for i in insns if i['mnemonic'] == 'cmp' and i['op_str'] == f'w9, #{len(table) - 1}')
    if not span:
        raise AssertionError('dispatch guard changed')
    by_rva_local = {i['rva']: i for i in insns}
    live = {}
    for index, byte in enumerate(table):
        pad = base + 4 * byte
        for offset in range(0, 0x120, 4):
            one = by_rva_local.get(pad + offset)
            if not one:
                continue
            if one['mnemonic'] == 'ret':
                break
            if one['mnemonic'] != 'bl':
                continue
            match = re.search(r'public static void (\w+)\(', names.get(call_target(one), ''))
            if match and match.group(1).startswith(('set_', 'Set')):
                live[first + index] = match.group(1)
                break
    called = {re.search(r'public static void (\w+)\(', names.get(call_target(i), '')).group(1)
              for i in insns if i['mnemonic'] == 'bl'
              and re.search(r'public static void (\w+)\(', names.get(call_target(i), ''))}
    fallthrough = {}
    for value, setter in ((0, 'set_Coins'), (1, 'set_Gems')):
        if setter in called:
            fallthrough[value] = setter
    if live != {14: 'SetDroneCards', 15: 'SetPlayerCards',
                18: 'set_KeyCount2', 23: 'set_PvPMedal'}:
        raise AssertionError(f'unexpected dispatch handlers: {live}')
    if fallthrough != {0: 'set_Coins', 1: 'set_Gems'}:
        raise AssertionError(f'fallthrough rewards changed: {fallthrough}')
    return {**fallthrough, **live}


def six_int_pool(defaults):
    """how crowded the six-int blob space is (so the report can say why the
    bet ladders are NOT bound by content)."""
    pid = {k: v for k, v in defaults.items()
           if k.startswith('<PrivateImplementationDetails>')}
    blobs = []
    for key, row in pid.items():
        raw = bytes.fromhex(row['raw'])
        if len(raw) != 32:
            continue
        ints = list(struct.unpack('<8i', raw))
        if ints[6:] != [0, 0]:
            continue
        blobs.append(ints[:6])
    ascending = [b for b in blobs if all(b[i] < b[i + 1] for i in range(5)) and b[0] > 0]
    return dict(six_int_blobs=len(blobs), ascending=len(ascending))


def ctor_arrays(by_rva):
    insns = by_rva[CTOR]['instructions']
    by_rva = {i['rva']: i for i in insns}
    arrays = []
    for index, one in enumerate(insns):
        if one['mnemonic'] != 'bl' or call_target(one) != INITIALIZE_ARRAY:
            continue
        length = next(int(i['op_str'].rsplit('#', 1)[1], 0)
                      for i in reversed(insns[max(0, index - 8):index])
                      if i['mnemonic'] == 'mov' and i['op_str'].startswith('w1,'))
        store = None
        for offset in range(1, 5):
            follow = by_rva.get(one['rva'] + 4 * offset)
            if follow and follow['mnemonic'] == 'str' and re.search(r'\[x19, #0x[0-9a-f]+\]',
                                                                    follow['op_str']):
                store = int(re.search(r'#0x([0-9a-f]+)\]', follow['op_str']).group(1), 16)
                break
        handle = None
        for back in range(1, 6):
            prev = by_rva.get(one['rva'] - 4 * back)
            if prev and prev['mnemonic'] == 'ldr' and prev['op_str'].startswith('x1,'):
                handle = prev['op_str']
                break
        arrays.append(dict(length=length, store_offset=store, field_handle=handle,
                           initarray_rva=one['rva']))
    arrays.sort(key=lambda row: row['initarray_rva'])
    if [row['store_offset'] for row in arrays] != [offset for _, offset in FIELDS]:
        raise AssertionError(f'constructor stores moved: {arrays}')
    if [row['length'] for row in arrays] != [6] * 6:
        raise AssertionError(f'array lengths changed: {arrays}')
    return [dict(field=name, **row) for (name, _), row in zip(FIELDS, arrays)]


def identify_indexs(defaults, allowed):
    """exactly one six-int blob whose values all land in `allowed`."""
    pid = {k: v for k, v in defaults.items()
           if k.startswith('<PrivateImplementationDetails>')}
    found, scanned = [], 0
    for key, row in pid.items():
        raw = bytes.fromhex(row['raw'])
        if len(raw) != 32:          # 6 ints, padded to 8
            continue
        ints = list(struct.unpack('<8i', raw))
        six = ints[:6]
        if ints[6:] != [0, 0]:
            continue
        scanned += 1
        if all(value in allowed for value in six):
            found.append(dict(blob=key, data_index=row['data_index'],
                              field_index=row['field_index'], raw=row['raw'],
                              values=six))
    if len(found) != 1:
        raise AssertionError(f'{len(found)} candidate blobs, expected 1')
    return found[0], scanned, len(pid)


def build_payload():
    grant, pvp = load(GRANT), load(PVP)
    by_rva = {m['rva']: m for m in grant['methods']}
    defaults = json.loads((ROOT / DEFAULTS).read_text())['fields']
    lines = KS.dump_lines()
    names = KS.dump_names(lines)
    fields_pvp = KS.field_offsets(lines, 'Board_PVP')

    for name, offset in FIELDS:
        if fields_pvp.get(name) != offset:
            raise AssertionError(f'Board_PVP.{name} moved')

    candidate_pool = six_int_pool(defaults)
    handlers = handler_types(pvp, by_rva)
    allowed = sorted(handlers)
    blob, scanned, total = identify_indexs(defaults, allowed)
    if blob['values'] != [23, 0, 14, 1, 15, 18]:
        raise AssertionError(f'unexpected rewardIndexs: {blob["values"]}')

    setup = by_rva[SETUP]['instructions']
    setup_ops = {one['mnemonic'] + ' ' + one['op_str'] for one in setup}
    checks = dict(
        odd_buttons=('and w1, w20, #1' in setup_ops),
        even_skipped=any(one['mnemonic'] == 'tbz' and one['op_str'].startswith('w20, #0')
                         for one in setup),
        slot_halving=any(one['mnemonic'] == 'asr' and one['op_str'].startswith('w11, w9, #1')
                         for one in setup),
        sprite_from_reward=any(one['mnemonic'] == 'bl' and call_target(one) == 0x133ECCC
                               for one in setup),
        setinfo=any(one['mnemonic'] == 'bl' and call_target(one) == 0x1310880 for one in setup),
        progress_bar=any(one['mnemonic'] == 'fmov' and one['op_str'] == 's2, #1.50000000'
                         for one in setup),
    )
    if not all(checks.values()):
        raise AssertionError(f'SetupHunters changed: {checks}')

    collected = by_rva[IS_COLLECTED]['instructions']
    collected_ok = any(one['mnemonic'] == 'bl' and call_target(one) == 0x13F1A1C
                       for one in collected)
    if not collected_ok:
        raise AssertionError('IsCollected no longer reads PlayerPrefs.GetInt')

    season = by_rva[SEASON_GET]['instructions']
    season_ok = any(one['mnemonic'] in ('b', 'bl') and call_target(one) == 0x13F1A1C
                    for one in season)
    if not season_ok:
        raise AssertionError('SeasonProgress no longer reads PlayerPrefs')

    stages = []
    for slot, type_id in enumerate(blob['values']):
        stages.append(dict(
            slot=slot, type_id=type_id, gift_type=KS.GIFT_TYPES.get(type_id),
            handler=handlers.get(type_id, 'no handler (falls through to ret)'),
            collectible_point=2 * slot + 1,
            granted='KeyCount2' if handlers.get(type_id) == 'set_KeyCount2' else None))

    payload = dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='Constructor + content-matched metadata blob, plus the collect path. '
             'The size of each reward is still runtime data (MODEL_NOT_MEASURED runtime).',
        provenance=dict(
            xapk_sha256=load('reverse-engineering/raw/call-sites-535b0541/calls.json.gz')
            ['provenance']['xapk_sha256'],
            libil2cpp_sha256=load('reverse-engineering/raw/call-sites-535b0541/calls.json.gz')
            ['provenance']['libil2cpp_sha256'],
            sources=[dict(path=path, sha256=sha_file(path))
                     for path in (GRANT, PVP, DEFAULTS, DUMP)]),
        table=dict(
            arrays=ctor_arrays(by_rva),
            reward_indexs=dict(
                values=blob['values'], blob=blob['blob'],
                data_index=blob['data_index'], field_index=blob['field_index'],
                raw=blob['raw'],
                identification='only six-int <PrivateImplementationDetails> blob whose every '
                               'value is a reward id that OnClickHunterCollect handles',
                candidates_scanned=scanned, pid_blobs=total,
                value_domain=allowed),
            reward_values=dict(field='rewardValues', offset=0x1A0, length=6,
                               status='NOT_BOUND',
                               blocking='same constructor, but no content constraint narrows '
                                        'its blob; needs the metadata usage table for handle '
                                        'slot 0x2ae0010'),
            reward_scales=dict(field='rewardScales', offset=0x1A8, length=6,
                               status='NOT_BOUND',
                               blocking='decorative icon scale; handle slot 0x2ae0018 '
                                        'unresolved for the same reason'),
            bet_tables=dict(
                fields=[dict(field=row['field'], offset=row['store_offset'], length=6)
                        for row in ctor_arrays(by_rva)[3:]],
                status='NOT_BOUND',
                blocking='three ascending int[6] ladders; the label order (coin > gem > '
                         'medal) is a runtime assumption, and %d six-int blobs are already '
                         'strictly ascending, so content alone cannot name them'
                         % candidate_pool['ascending'],
                candidate_pool=candidate_pool),
        ),
        handlers=handlers,
        stages=stages,
        key_stage=dict(slot=stages[-1]['slot'], type_id=stages[-1]['type_id'],
                       collectible_point=stages[-1]['collectible_point'],
                       note='the only slot whose handler writes a key counter'),
        points=dict(
            total_markers=12,
            clickable='odd markers only',
            rule='index = (marker - 1) / 2, clamped at 0; only odd markers get SetInfo '
                 'and a click target, so there are 6 clickable stages for 6 reward slots',
            checks=checks),
        gate=dict(
            collectable='marker < Board_PVP.SeasonProgress (PlayerPrefs int)',
            visible='marker < Board_PVP.SeasonDies',
            collected='Board_PVP.IsCollected(marker): PlayerPrefs.GetInt(<static prefix> + '
                      'marker.ToString(), 0) == 1',
            progress_bar='lineProgress.size.x = SeasonProgress * 1.5',
            finished_marker='child 1 active when SeasonProgress == allPoints.Length',
            season_getter=SEASON_GET, season_setter=SEASON_SET, season_dies=SEASON_DIES),
        not_decoded=[
            dict(item='amount per stage (rewardValues)',
                 blocking='blob unbound (see table.reward_values.blocking)'),
            dict(item='icon scale per stage (rewardScales)',
                 blocking='blob unbound (see table.reward_scales.blocking)'),
            dict(item='how many markers the scene really has',
                 blocking='allPoints is a serialized WinPoint[] filled from the scene, '
                          'MODEL_NOT_MEASURED runtime; the code only proves halving'),
        ],
    )

    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',
                        default='datas/l2_535b0541_pvp_hunter_reward_table.json.gz')
    args = parser.parse_args()
    payload = build_payload()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                                sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          reward_indexs=payload['table']['reward_indexs']['values'],
                          candidates=payload['table']['reward_indexs']['candidates_scanned'],
                          key_slot=payload['key_stage'],
                          handlers=payload['handlers'])))


if __name__ == '__main__':
    main()
