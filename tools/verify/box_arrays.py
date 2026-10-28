#!/usr/bin/env python3
"""Contents of `Board_Quest` key/reward arrays, from pinned metadata defaults.

Report 130 named this as its blocking step: `Board_Quest..cctor` fills
`BoxKeyCost`, `KeyPrices`, `NumberRewards` and `AllTimeAds` through
`RuntimeHelpers.InitializeArray`, so the bytes live in `global-metadata.dat`
field defaults, not in `libil2cpp.so`. The repository already carries that table
(`reverse-engineering/il2cpp/field-defaults.json`, `fieldDefaultValues` v31), so
the gap closes without any new native recovery:

    InitializeArray bl  -> FieldInfo token (kind 4, odd source)
                        -> <PrivateImplementationDetails> field ordinal
                        -> fieldDefaultValues entry (raw bytes)
                        -> new int[3] / new double[3] element view

The extractor's `initialize_arrays[].blobs` are **not** used: they are relocated
metadata-token tables (`0x8000xxxx` pointers), not array contents.
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

import meta_rewards as MR  # noqa: E402

BOX_RAW = 'reverse-engineering/raw/box-draw-535b0541/native.json.gz'
META_RAW = 'reverse-engineering/raw/meta-rewards-535b0541/native.json.gz'
DEFAULTS = 'reverse-engineering/il2cpp/field-defaults.json'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'

QUEST_CLASS = 'Board_Quest'
INITIALIZE = 0x205B07C          # RuntimeHelpers.InitializeArray
TOTAL_SECONDS = 21105208        # MyLibrary.GetTotalSecondsTravelTime
STORE = re.compile(r'^x19, \[x8, #(0x[0-9a-f]+)\]$')

SEMANTICS = {
    0x38: ('BoxKeyCost', 'keys required to open this box', 'keys'),
    0x40: ('KeyPrices', 'gems charged per missing key', 'gems/key'),
    0x48: ('NumberRewards', 'draws taken from the pack pool', 'draws'),
    0x50: ('AllTimeAds', 'ad cooldown threshold compared with a seconds value',
           'seconds'),
}


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


def statics_type(cls):
    """declared type per static offset of `cls`, from dump.cs."""
    lines = MR.dump_text().split('\n')
    start = next(k for k, l in enumerate(lines)
                 if re.match(r'\s*public class ' + re.escape(cls) + r'\b', l))
    depth = 0
    for end in range(start, len(lines)):
        depth += lines[end].count('{') - lines[end].count('}')
        if end > start and depth == 0:
            break
    out = {}
    for line in lines[start:end]:
        field = re.match(r'\s*(?:public|private|protected|internal)\s+static\s+(.+?)\s+(\w+);'
                         r'\s*//\s*0x([0-9A-Fa-f]+)\s*$', line)
        if field:
            out[int(field.group(3), 16)] = (field.group(2), field.group(1).strip())
    return out


def decode(raw, length, declared_bytes):
    """(element type, values) for a declared element count, 4 or 8 bytes each."""
    per = declared_bytes // length
    if per == 4:
        return 'int32', list(struct.unpack('<%di' % length, raw[:4 * length]))
    if per == 8:
        return 'float64', list(struct.unpack('<%dd' % length, raw[:8 * length]))
    raise ValueError(f'unexpected element width {per}')


def build():
    raw = load(BOX_RAW)
    meta = load(META_RAW)
    defaults = MR.field_defaults()
    text = MR.dump_text()
    pids = MR.parse_pid_classes(text)
    index = MR.parse_type_index(text)
    pid = MR.pid_for(pids, index[QUEST_CLASS])
    types = statics_type(QUEST_CLASS)

    cctor = next(m for m in raw['methods']
                 if m['class_name'] == QUEST_CLASS and '.cctor' in m['signature'])
    events = cctor['initialize_arrays']
    insns = cctor['instructions']

    rows, checks = [], []
    for ordinal_position, event in enumerate(events):
        resolved = MR.resolve_initialize_array(event, pid, defaults)
        token_kind = (event['token_lo'] >> 29) & 0x7
        token_source = event['token_lo'] & 0x1FFFFFFF
        if token_kind != 4 or token_source % 2 != 1:
            raise AssertionError('unexpected InitializeArray token shape')
        if resolved['status'] not in ('ok', 'blob_length_mismatch'):
            raise AssertionError(f'token did not resolve: {resolved["status"]}')

        # the array is stored into statics a few instructions after the call
        offset = None
        for following in insns[next(k for k, i in enumerate(insns)
                                    if i['rva'] == event['initialize_rva']):
                               ][:14]:
            match = following['mnemonic'] == 'str' and STORE.match(following['op_str'])
            if match:
                offset = int(match.group(1), 16)
                break
        if offset is None:
            raise AssertionError('InitializeArray result never stored to statics')

        entry = defaults[f'{MR.PID_CLASS}.{resolved["field"]}']
        payload = bytes.fromhex(entry['raw'])
        length = event['length']
        declared_bytes = resolved['declared_bytes']
        element_type, values = decode(payload, length, declared_bytes)
        name, semantics, unit = SEMANTICS[offset]

        checks.append(dict(check='declared_size_matches_elements',
                           statics_offset=offset,
                           passed=declared_bytes == length * (4 if element_type == 'int32' else 8),
                           declared_bytes=declared_bytes, elements=length,
                           element_type=element_type))
        checks.append(dict(check='dump_declares_same_name',
                           statics_offset=offset,
                           passed=types[offset][0] == name, dump_name=types[offset][0]))

        rows.append(dict(
            statics_offset=offset, field=f'{QUEST_CLASS}.{name}',
            declared=types[offset][1], element_type=element_type, elements=length,
            values=values, unit=unit, semantics=semantics,
            initialize_rva=event['initialize_rva'], array_new_rva=event['array_new_rva'],
            token=dict(kind=token_kind, source=token_source,
                       field_ordinal=resolved['field_ordinal'],
                       pid_type_index=resolved['pid_type_index']),
            blob=dict(field_id=resolved['field'],
                      field_type=resolved['field_type'],
                      declared_bytes=declared_bytes,
                      default_raw_hex=entry['raw'],
                      field_data_index=entry['data_index'],
                      field_index=entry['field_index']),
            not_the_extractor_blobs=(
                'initialize_arrays[].blobs in the raw are relocated metadata-token '
                'tables and hence not array contents; the values above come from '
                'fieldDefaultValues'),
        ))

    by_name = {row['field'].split('.')[1]: row for row in rows}
    keys = by_name['BoxKeyCost']['values']
    prices = by_name['KeyPrices']['values']
    draws = by_name['NumberRewards']['values']
    ads = by_name['AllTimeAds']['values']
    derived = dict(
        type_box_domain=list(range(len(keys))),
        keys_per_box=dict(zip(map(str, range(len(keys))), keys)),
        gems_per_missing_key=dict(zip(map(str, range(len(prices))), prices)),
        draws_per_box=dict(zip(map(str, range(len(draws))), draws)),
        buy_all_missing_keys_gems=dict(zip(map(str, range(len(keys))),
                                           [k * p for k, p in zip(keys, prices)])),
        ad_cooldown_seconds=dict(zip(map(str, range(len(ads))), ads)),
        ad_cooldown_hours=dict(zip(map(str, range(len(ads))), [a / 3600 for a in ads])),
        note='typeBox 0 also double-weights index 13 (DroneExp) inside the draw '
             'pool (report 129); the numbers here only set the draw count',
    )

    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='Array contents read from pinned metadata field default values. '
             'No draw is simulated; anything about which item is drawn is '
             'MODEL_NOT_MEASURED runtime.',
        provenance=dict(
            sources=[dict(path=p, sha256=sha_file(p)) for p in (DEFAULTS, BOX_RAW, META_RAW, DUMP)],
            xapk_sha256=raw['xapk_sha256'],
            libil2cpp_sha256=raw['libil2cpp_sha256'],
            field_defaults_count=len(defaults),
            field_defaults_source='global-metadata.dat fieldDefaultValues v31'),
        chain=dict(
            initialize_array_rva=INITIALIZE,
            board_quest_cctor_rva=cctor['rva'], board_quest_cctor_size=cctor['size'],
            pid_type_index=pid['type_index'], pid_field_count=len(pid['fields']),
            resolution='InitializeArray(FieldInfo token) -> odd source -> PID ordinal -> '
                       'fieldDefaultValues raw bytes -> element view',
            seconds_source=dict(rva=TOTAL_SECONDS,
                                method='MyLibrary.GetTotalSecondsTravelTime',
                                used_by='Board_QuestRewards.IsTimeAdsReady',
                                evidence='AllTimeAds[typeBox] is compared double-vs-double '
                                         'against that value, so its unit is seconds'),
        ),
        arrays=rows,
        derived=derived,
        checks=checks,
        not_decoded=[
            dict(item='which reward the draw returns',
                 blocking='UnityEngine.Random seeded at runtime — MODEL_NOT_MEASURED runtime'),
            dict(item='where the key counters are incremented',
                 blocking='GameDatas.set_KeyCount0/1/2 call sites live outside the families '
                          'pinned by this session (reports 128-131)'),
        ],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_box_arrays.json.gz')
    args = parser.parse_args()
    payload = build()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                                sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          arrays=len(payload['arrays']),
                          checks_passed=sum(1 for c in payload['checks'] if c['passed']),
                          checks_total=len(payload['checks']),
                          derived=payload['derived']['draws_per_box'])))


if __name__ == '__main__':
    main()
