#!/usr/bin/env python3
"""`PVP_Manager.MaxRankStars` — the 10 star ladders, bound to real bytes. STATIC only.

Report 127 left the values of `MaxRankStars` `not_decoded`; report 128 read them
(`[3,3,3]`, `[4,4,4]`, …), but only as prose. This report turns that into a
re-derivable measurement and adds the checks that make the binding falsifiable:

1. **Shape from the code.** `PVP_Manager..cctor` makes 10 `InitializeArray` calls
   with `newarr` lengths `3,3,4,4,5,5,5,5,5,5`, and the 10 calls carry only **5
   distinct** static-field tokens — the six 5-cell arrays share one blob, which
   Roslyn emitted once and reused.
2. **Bytes from `fieldDefaultValues`.** Each token resolves to a
   `<PrivateImplementationDetails>.<HEX>` field; `field-defaults.json` holds its
   data. Every data slice is exactly `declared_bytes` long, matching `4 * length`.
3. **Roslyn's naming invariant, recomputed here.** `<HEX>` is
   `sha256(<the declared bytes>).upper()`. The verifier recomputes that digest
   for all five fields — so a wrong field/data pairing cannot pass.
4. **Token bookkeeping.** `token_source = token & 0x7FFFFFFF` is always odd and
   the resolved ordinal is `(token_source - 1) / 2`, the same `2*ordinal+1`
   convention `ia-resolved.json` documents.

Result (index = rank, 0..9): `[3,3,3] [4,4,4] [4,4,4,4] [5,5,5,5]` then
`[5,5,5,5,5]` six times. That is a per-level star cap table: array length equals
the number of `PVPReward.lvl` values the same rank has in `AllRewards` for 9 of
the 10 ranks (rank 0 is the outlier: 3 cells, 2 reward levels).

The reader is **not** in any pinned raw — no method of `PVP_Manager` touches
statics `+0x18` — so "index = rank" is an ordering inference (10 elements, 10
ranks), not a decoded index expression. That is recorded, not hidden.
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
RESOLVED = 'datas/l2_535b0541_meta_rewards.json.gz'
DEFAULTS = 'reverse-engineering/il2cpp/field-defaults.json'
RULES_ARTIFACT = 'datas/l2_535b0541_pvp_manager_rules.json.gz'

CCTOR = 19916640
PID_PREFIX = '<PrivateImplementationDetails>.'


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


def json_file(rel):
    return json.loads((ROOT / rel).read_text())


def call_target(insn):
    text = insn['op_str'].strip().lstrip('#')
    return int(text, 0) if re.fullmatch(r'(0x[0-9a-f]+|\d+)', text) else None


def cctor_arrays(blob):
    """The 10 `newarr` + `InitializeArray` events of `PVP_Manager..cctor`, in order."""
    body = [row for row in blob['methods'] if row['rva'] == CCTOR][0]
    events = sorted(body['initialize_arrays'], key=lambda row: row['initialize_rva'])
    assert len(events) == 10, len(events)
    return [dict(index=index, initialize_rva=row['initialize_rva'], length=row['length'],
                 array_new_rva=row['array_new_rva'], addend=row['addend'],
                 token=row['token_lo'], blob_hex=row['blobs'][0])
            for index, row in enumerate(events)]


def resolved_fields(resolved):
    """128's token -> `<PrivateImplementationDetails>` field resolution, per addend."""
    rows = resolved['initialize_arrays']['by_class']['PVP_Manager'][0]['arrays']
    out = {}
    for row in rows:
        assert row['status'] == 'ok', row
        seen = out.setdefault(row['addend'], row)
        assert seen['field'] == row['field'], (seen, row)
        assert seen['ints'] == row['ints'], (seen, row)
    return out


def field_data(defaults, field_hash):
    key = PID_PREFIX + field_hash
    assert key in defaults, 'field not in fieldDefaultValues: ' + key
    row = defaults[key]
    raw = bytes.fromhex(row['raw'])
    return dict(field=field_hash, raw_hex=row['raw'], data=raw,
                field_index=row['field_index'], data_index=row['data_index'])


def build_payload():
    meta = load(META)
    resolved = load(RESOLVED)
    defaults = json_file(DEFAULTS)['fields']
    rules = load(RULES_ARTIFACT)

    events = cctor_arrays(meta)
    by_addend = resolved_fields(resolved)

    # Token bookkeeping is recomputable from the raw alone.
    for event in events:
        token_source = event['token'] & 0x7FFFFFFF
        assert token_source % 2 == 1, event
        event['token_source'] = token_source
        event['ordinal'] = (token_source - 1) // 2
        assert event['ordinal'] == by_addend[event['addend']]['field_ordinal'], event

    groups = {}
    for event in events:
        groups.setdefault(event['addend'], []).append(event)

    blobs = []
    for addend, calls in sorted(groups.items(), key=lambda item: min(
            call['initialize_rva'] for call in item[1])):
        lengths = {call['length'] for call in calls}
        assert len(lengths) == 1, (addend, lengths)
        length = lengths.pop()
        row = by_addend[addend]
        data = field_data(defaults, row['field'])
        declared = length * 4
        assert row['declared_bytes'] == declared, (addend, row['declared_bytes'], declared)
        assert len(data['data']) >= declared, (addend, len(data['data']))
        values = list(struct.unpack('<%di' % length, data['data'][:declared]))
        digest = hashlib.sha256(data['data'][:declared]).hexdigest().upper()
        assert digest == row['field'], (addend, digest, row['field'])
        blobs.append(dict(
            addend=addend, token=0x80000000 | row['token_source'], token_source=row['token_source'],
            ordinal=row['field_ordinal'], field=row['field'], declared_bytes=declared,
            length=length, values=values, data_hex=data['data'][:declared].hex(),
            name_is_sha256_of_data=True, field_index=data['field_index'],
            shared_by=[call['index'] for call in calls]))
        assert row['ints'][:length] == values, (row['ints'], values)

    assert [row['index'] for row in events] == list(range(10))
    assert [row['length'] for row in events] == [3, 3, 4, 4, 5, 5, 5, 5, 5, 5]
    assert [row['length'] for row in blobs] == [3, 3, 4, 4, 5]
    assert [len(row['shared_by']) for row in blobs] == [1, 1, 1, 1, 6]
    assert len({row['field'] for row in blobs}) == 5

    table = []
    for event in events:
        blob = [row for row in blobs if row['addend'] == event['addend']][0]
        rewards = [row for row in rules['tables']['all_rewards']['entries']
                   if row['rank'] == event['index']]
        levels = sorted({row['level'] for row in rewards})
        data = field_data(defaults, blob['field'])
        values = list(struct.unpack('<%di' % blob['length'],
                                    data['data'][:blob['length'] * 4]))
        table.append(dict(rank=event['index'], length=blob['length'], stars=values,
                          initialize_rva=event['initialize_rva'], addend=event['addend'],
                          field=blob['field'], shared=len(blob['shared_by']) > 1,
                          reward_levels=levels, reward_rows=len(rewards),
                          length_matches_reward_levels=len(levels) == blob['length']))

    assert [row['stars'] for row in table] == [
        [3, 3, 3], [4, 4, 4], [4, 4, 4, 4], [5, 5, 5, 5],
        [5, 5, 5, 5, 5], [5, 5, 5, 5, 5], [5, 5, 5, 5, 5], [5, 5, 5, 5, 5],
        [5, 5, 5, 5, 5], [5, 5, 5, 5, 5]]
    matches = sum(1 for row in table if row['length_matches_reward_levels'])
    assert matches == 9, matches
    assert [row['rank'] for row in table if not row['length_matches_reward_levels']] == [0]
    assert all(max(row['stars']) <= 5 and min(row['stars']) >= 1 for row in table)
    assert {row['length'] for row in blobs} == {3, 4, 5}
    # Continuity with 128: the per-call ints recorded there must equal this read-out.
    for event in events:
        assert by_addend[event['addend']]['ints'][:event['length']] == \
            [row['stars'] for row in table if row['rank'] == event['index']][0], event

    return dict(
        schema=1,
        evidence='STATIC_ONLY_ORIGINAL_APK',
        note='Star caps are build-time bytes of the original APK. The method that reads '
             'MaxRankStars is not in any pinned raw, so "index = rank" is an ordering '
             'inference; how stars are earned/reset in a live match is MODEL_NOT_MEASURED '
             'runtime.',
        provenance=dict(
            xapk_sha256=meta['xapk_sha256'], libil2cpp_sha256=meta['libil2cpp_sha256'],
            dump_sha256=meta['dump_sha256'],
            sources=[dict(path=META, sha256=sha_file(META),
                          role='PVP_Manager..cctor: the 10 InitializeArray events'),
                     dict(path=RESOLVED, sha256=sha_file(RESOLVED),
                          role='token -> <PrivateImplementationDetails> field resolution (128)'),
                     dict(path=DEFAULTS, sha256=sha_file(DEFAULTS),
                          role='fieldDefaultValues: the array bytes'),
                     dict(path=RULES_ARTIFACT, sha256=sha_file(RULES_ARTIFACT),
                          role='AllRewards level coverage, used for the length cross-check')]),
        method=dict(class_name='PVP_Manager', rva=CCTOR, size=19944,
                    calls=len(events)),
        cctor_arrays=events,
        blobs=blobs,
        rank_table=table,
        cross_checks=dict(
            arrays=len(events), distinct_blobs=len(blobs),
            shared_by_six=[row['index'] for row in events
                           if len([b for b in blobs if b['addend'] == row['addend']][0]
                                  ['shared_by']) == 6],
            name_hash_all_match=True, declared_bytes_all_match=True,
            reward_level_length_match=f'{matches}/10',
            values_match_report_128=True,
            identity='10 arrays <- 5 PID blobs (2 x 3-cell, 2 x 4-cell, 1 x 5-cell reused 6x); '
                     'each blob name == sha256(declared bytes) uppercase; declared_bytes == '
                     '4 x length; ordinal == (token & 0x7fffffff - 1) / 2',
        ),
        confirmations=[dict(
            item='128 §3.4 MaxRankStars values',
            status='CONFIRMED',
            measured='the five blobs really hold [3,3,3], [4,4,4], [4,4,4,4], [5,5,5,5], '
                     '[5,5,5,5,5]; the six last ranks share the 5-cell blob',
            evidence='sha256 of each declared byte slice equals its '
                     '<PrivateImplementationDetails> field name, and each slice length equals '
                     '4 x the newarr length')],
        not_decoded=[
            dict(item='the method that reads MaxRankStars',
                 blocking='none of the 15 pinned PVP_Manager methods touches statics +0x18; '
                          'the reader lives in a class whose raw is not pinned '
                          '(PVP_Endgame / Board_*), so index semantics are ordering-only'),
            dict(item='rank 0 has 3 cells but only 2 reward levels in AllRewards',
                 blocking='measured, not explained: either level 0 exists without a reward row '
                          'or the first cell is a placeholder; no pinned code indexes it'),
            dict(item='how stars move during a match',
                 blocking='MODEL_NOT_MEASURED runtime'),
        ],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_max_rank_stars.json.gz')
    args = parser.parse_args()
    payload = build_payload()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                                sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          blobs=len(payload['blobs']),
                          stars=[row['stars'] for row in payload['rank_table']])))


if __name__ == '__main__':
    main()
