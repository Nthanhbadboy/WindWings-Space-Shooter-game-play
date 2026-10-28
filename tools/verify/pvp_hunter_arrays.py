#!/usr/bin/env python3
"""The six `Board_PVP..ctor` arrays, read out of pinned metadata field defaults.

133 stopped at the handle slots: `rewardValues` and `rewardScales` were reported as
"needs the metadata usage table for handle slot 0x2ae0010 / 0x2ae0018", and the three
bet ladders as "content alone cannot name them". Both blockers are artefact-of-the-raw:

* the `initialize_arrays` block for `Board_PVP..ctor` exists in
  `reverse-engineering/raw/key-grant-535b0541/native.json.gz` — six events, one per
  array, each with its own metadata token and `slot_va`. 133 read the same constructor
  through `arena-pvp-535b0541`, which carries the method but no `initialize_arrays`,
  so the slots looked unresolved.
* the position, not the content, names each array: every event is followed by
  `str x20, [x19, #off]`, and `off` is that field's offset in `dump.cs`
  (408/416/424/520/528/536 — the same six offsets 133 lists).

131 already proved the rest of the chain on `Board_Quest..cctor`:
token → odd source → `<PrivateImplementationDetails>` ordinal → field-default bytes.
Here that binding is validated on the one array that has an independent check —
`rewardIndexs` must come out as the blob 133 identified by content — and only then
applied to the other five.

Build-time bytes of the original APK. Anything about a live match stays
`MODEL_NOT_MEASURED runtime`.
"""
import argparse
import functools
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

KEY_RAW = 'reverse-engineering/raw/key-grant-535b0541/native.json.gz'
ARENA_RAW = 'reverse-engineering/raw/arena-pvp-535b0541/native.json.gz'
DEFAULTS = 'reverse-engineering/il2cpp/field-defaults.json'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'
PREV = 'datas/l2_535b0541_pvp_hunter_reward_table.json.gz'

CLASS = 'Board_PVP'
INITIALIZE = 0x205B07C                     # RuntimeHelpers.InitializeArray
TO_STRING_FORMAT = 0x21033CC               # int.ToString(string format), per dump.cs
STORE = re.compile(r'^x\d+, \[x19, #(0x[0-9a-f]+)\]$')

# 133's store offsets -> the name each one must carry in dump.cs.
OFFSETS = {408: 'rewardIndexs', 416: 'rewardValues', 424: 'rewardScales',
           520: 'allBetCoinValues', 528: 'allBetGemValues', 536: 'allBetMedalValues'}

# The bet ladders also have readers, so their labels do not rest on offset order alone.
BET_READER = {520: ('OnChangeCoins', 0x1F8), 528: ('OnChangeGems', 0x1FC),
              536: ('OnChangeMedals', 0x200)}


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@functools.lru_cache(maxsize=None)
def previous():
    return load(PREV)


@functools.lru_cache(maxsize=None)
def ctor():
    for method in load(KEY_RAW)['methods']:
        if method['class_name'] == CLASS and '.ctor' in method['signature']:
            return method
    raise AssertionError('Board_PVP..ctor not in the key-grant raw')


@functools.lru_cache(maxsize=None)
def arena_ctor():
    """The same constructor as the other raw carries it: no `initialize_arrays`."""
    for method in load(ARENA_RAW)['methods']:
        if method['class_name'] == CLASS and '.ctor' in method['signature']:
            return method
    raise AssertionError('Board_PVP..ctor not in the arena raw')


def decode(raw, length, element_type):
    if element_type == 'int[]':
        return list(struct.unpack('<%di' % length, raw[:4 * length]))
    if element_type == 'float[]':
        return list(struct.unpack('<%df' % length, raw[:4 * length]))
    raise ValueError('unexpected declared type %r' % element_type)


def store_offset(event):
    """The `str` that lands the fresh array in the instance, right after the call."""
    insns = ctor()['instructions']
    start = next(k for k, i in enumerate(insns) if i['rva'] == event['initialize_rva'])
    for following in insns[start:start + 10]:
        if following['mnemonic'] == 'str':
            hit = STORE.match(following['op_str'])
            if hit:
                return int(hit.group(1), 16)
    raise AssertionError('InitializeArray result never stored into the instance')


def readers():
    """{field offset: [(class, signature, rva, raw)]} inside Board_PVP's own methods."""
    out = {}
    for rel in (KEY_RAW, ARENA_RAW):
        for method in load(rel)['methods']:
            if not method['class_name'].startswith(CLASS):
                continue
            for insn in method['instructions']:
                if insn['mnemonic'] not in ('ldr', 'ldrsw'):
                    continue
                hit = re.search(r'\[x\d+, #(0x[0-9a-f]+)\]$', insn['op_str'])
                if not hit:
                    continue
                offset = int(hit.group(1), 16)
                if offset not in OFFSETS:
                    continue
                row = (method['class_name'], method['signature'].strip(),
                       method['rva'], rel.split('/')[-2])
                out.setdefault(offset, [])
                if row not in out[offset]:
                    out[offset].append(row)
    return out


def build():
    defaults = MR.field_defaults()
    text = MR.dump_text()
    pids = MR.parse_pid_classes(text)
    index = MR.parse_type_index(text)
    pid = MR.pid_for(pids, index[CLASS])
    layout = MR.instance_layouts(CLASS)
    events = ctor()['initialize_arrays']
    prev = previous()['table']
    handlers = previous()['handlers']
    found = readers()

    assert len(events) == 6, len(events)
    assert [row['store_offset'] for row in prev['arrays']] == list(OFFSETS)

    rows, checks = [], []
    for event in events:
        resolved = MR.resolve_initialize_array(event, pid, defaults)
        assert resolved['status'] == 'ok', resolved['status']
        offset = store_offset(event)
        name, declared = layout[offset]
        entry = defaults['%s.%s' % (MR.PID_CLASS, resolved['field'])]
        payload = bytes.fromhex(entry['raw'])
        values = decode(payload, event['length'], declared)
        assert resolved['declared_bytes'] == 4 * event['length'], offset

        checks.append(dict(check='offset_named_by_dump', offset=offset,
                           passed=OFFSETS[offset] == name, dump=name))
        checks.append(dict(check='offset_matches_133', offset=offset,
                           passed=next(row['store_offset'] for row in prev['arrays']
                                       if row['field'] == name) == offset))
        checks.append(dict(check='declared_type_matches_width', offset=offset,
                           passed=resolved['declared_bytes'] == 4 * event['length'],
                           declared=declared))

        rows.append(dict(
            statics_offset=None, instance_offset=offset, field='%s.%s' % (CLASS, name),
            declared=declared, element_type=('int32' if declared == 'int[]' else 'float32'),
            elements=event['length'], values=values,
            initialize_rva=event['initialize_rva'],
            array_new_rva=event['array_new_rva'],
            slot_va=event['slot_va'], addend=event['addend'],
            token=dict(kind=(event['token_lo'] >> 29) & 0x7,
                       source=event['token_lo'] & 0x1FFFFFFF,
                       field_ordinal=resolved['field_ordinal'],
                       pid_type_index=resolved['pid_type_index']),
            blob=dict(field_id=resolved['field'], field_type=resolved['field_type'],
                      declared_bytes=resolved['declared_bytes'],
                      default_raw_hex=entry['raw'],
                      field_data_index=entry['data_index'],
                      field_index=entry['field_index']),
            readers=[dict(class_name=cls, signature=signature, rva=rva, raw=raw)
                     for cls, signature, rva, raw in found.get(offset, [])],
        ))

    by_name = {row['field'].split('.')[1]: row for row in rows}

    # The stage ladder: reward id per stage joined with its amount and handler.
    stage_table = []
    for position, (type_id, amount) in enumerate(zip(by_name['rewardIndexs']['values'],
                                                     by_name['rewardValues']['values'])):
        stage_table.append(dict(stage=position, reward_type=type_id,
                                handler=handlers.get(str(type_id)),
                                amount=amount,
                                scale=by_name['rewardScales']['values'][position]))

    bet_ladders = []
    for offset, (method, index_offset) in sorted(BET_READER.items()):
        field = OFFSETS[offset]
        values = by_name[field]['values']
        index_name, index_type = layout[index_offset]
        bet_ladders.append(dict(
            field=field, offset=offset, index_field=index_name,
            index_offset=index_offset, index_type=index_type, values=values,
            ascending=values == sorted(values), distinct=len(set(values)) == len(values),
            reader=[row for row in by_name[field]['readers']
                    if row['class_name'] == CLASS and method in row['signature']],
            rule='index = clamp(index + amount, 0, len-1) then the ladder element is '
                 'formatted and shown; the selected value lands in a static block at '
                 '+0x10 / +0x14 / +0x18'))

    # Independent checks: 133's content-based identification, and the key stage.
    identified = prev['reward_indexs']
    key_stage = previous()['key_stage']
    key_position = by_name['rewardIndexs']['values'].index(key_stage['type_id'])
    cross = dict(
        reward_indexs_blob_matches_133=(by_name['rewardIndexs']['blob']['field_id']
                                        == identified['blob'].split('.')[-1]),
        reward_indexs_values_match_133=(by_name['rewardIndexs']['values']
                                        == identified['values']),
        reward_indexs_domain=all(type_id in {int(k) for k in handlers}
                                 for type_id in by_name['rewardIndexs']['values']),
        key_stage_slot_matches_133=(key_position == key_stage['slot']),
        key_stage_amount=dict(stage=key_position, type_id=key_stage['type_id'],
                              amount=by_name['rewardValues']['values'][key_position]),
        scales_are_fractional=any(v != 1.0 for v in by_name['rewardScales']['values']),
        ladder_index_fields=[row['index_field'] for row in bet_ladders],
        arena_raw_has_no_initialize_arrays=not (arena_ctor().get('initialize_arrays')),
    )
    assert cross['reward_indexs_blob_matches_133']
    assert cross['reward_indexs_values_match_133']
    assert cross['reward_indexs_domain']
    assert cross['key_stage_slot_matches_133']
    assert all(row['ascending'] for row in bet_ladders)
    assert all(row['reader'] for row in bet_ladders)
    assert cross['arena_raw_has_no_initialize_arrays']

    sources = [dict(path=p, sha256=sha_file(p)) for p in
               (KEY_RAW, ARENA_RAW, DEFAULTS, DUMP, PREV)]
    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='The six arrays of Board_PVP..ctor are build-time bytes: the token binding '
             'is validated on rewardIndexs (133 identified that blob by content) and then '
             'applied positionally to the other five. Which reward a player actually '
             'receives in a match is MODEL_NOT_MEASURED runtime.',
        provenance=dict(sources=sources,
                        xapk_sha256=load(KEY_RAW)['xapk_sha256'],
                        libil2cpp_sha256=load(KEY_RAW)['libil2cpp_sha256'],
                        field_defaults_count=len(defaults),
                        field_defaults_source='global-metadata.dat fieldDefaultValues v31'),
        chain=dict(
            ctor=dict(rva=ctor()['rva'], size=ctor()['size'],
                      instructions=len(ctor()['instructions']),
                      initialize_arrays=len(events)),
            other_raw=dict(path=ARENA_RAW, rva=arena_ctor()['rva'],
                           initialize_arrays=0,
                           why='the same constructor is present but its metadata-token '
                               'table was not extracted there, which is what made 133 '
                               'report the handle slots as unresolved'),
            pid=dict(type_index=pid['type_index'], field_count=len(pid['fields'])),
            initialize_array_rva=INITIALIZE, to_string_rva=TO_STRING_FORMAT,
            resolution='InitializeArray(FieldInfo token) -> odd source -> PID ordinal -> '
                       'fieldDefaultValues raw bytes -> element view by declared type',
            naming='store offset after the call -> dump.cs instance layout'),
        arrays=rows,
        stage_table=stage_table,
        bet_ladders=bet_ladders,
        cross_checks=cross,
        confirmations=[
            dict(item='148 #39 `amount per stage (rewardValues)` (ACTIONABLE)',
                 result='closed — six values, and stage 5 = 10 keys matches '
                        '133\'s key_stage type 18 / slot 5'),
            dict(item='148 #40 `icon scale per stage (rewardScales)` (ACTIONABLE)',
                 result='closed — float[6], f32 exact: 1.0 / 1.0 / 0.6 / 1.0 / 0.6 / 0.8'),
            dict(item='133 `table.reward_values` / `reward_scales` (NOT_BOUND)',
                 result='closed — the blocking reason was a missing `initialize_arrays` '
                        'block in the raw 133 read, not a missing metadata table'),
            dict(item='133 `table.bet_tables` (NOT_BOUND, "content cannot name them")',
                 result='closed — naming comes from the store offset plus the reader '
                        'method (OnChangeCoins / OnChangeGems / OnChangeMedals) and the '
                        'index fields betCoins / betGems / betMedals'),
        ],
        checks=checks,
        not_decoded=[
            dict(item='which reward a player actually receives in a match',
                 blocking='the ladder is static; claiming it needs a played match — '
                          'MODEL_NOT_MEASURED runtime'),
            dict(item='how many markers the scene really has',
                 blocking='allPoints is a serialized WinPoint[] filled from the scene; '
                          'unchanged from 133'),
            dict(item='class behind cell 0x2ADF238, where the chosen bet is stored',
                 blocking='the slot resolves to one addend (45765696) that is not a string '
                          'literal, so the owning class is still unnamed; only the field '
                          'offsets +0x10 / +0x14 / +0x18 are known'),
        ],
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='datas/l2_535b0541_pvp_hunter_arrays.json.gz')
    args = parser.parse_args()
    payload = build()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    target.write_bytes(gzip.compress(blob, mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size,
                          sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                          arrays=len(payload['arrays']),
                          checks_passed=sum(1 for c in payload['checks'] if c['passed']),
                          checks_total=len(payload['checks']),
                          stages=[
                              [row['stage'], row['reward_type'], row['amount']]
                              for row in payload['stage_table']])))


if __name__ == '__main__':
    main()
