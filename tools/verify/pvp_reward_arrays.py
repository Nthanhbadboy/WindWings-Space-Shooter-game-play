#!/usr/bin/env python3
"""`Board_PVP`'s six reward arrays: which instruction fills which field.

133 stopped at "`rewardValues` / `rewardScales` handle slots unresolved", and 132's
open item calls them "instance arrays filled at runtime". Both statements need
correcting, and the ctor is where that shows:

1. `Board_PVP..ctor` (19796420, 500 B) makes **six** `RuntimeHelpers.InitializeArray`
   calls, and each one is followed immediately by `str x20, [x19, #offset]`. So the
   call -> field mapping is *adjacent in the instruction stream*: 0x198, 0x1a0,
   0x1a8, 0x208, 0x210, 0x218. Nothing about the metadata usage table is needed to
   say **which** field each call fills — only to read the **bytes** it fills it with.
2. The dump gives the declared types: `int[] rewardIndexs` (0x198),
   `int[] rewardValues` (0x1a0), **`float[] rewardScales`** (0x1a8), then the three
   bet ladders as `int[]`.
3. `Board_PVP` has **no `rewardTypes` field at all** — so 132's sentence names one
   field that does not exist and calls the other two "filled at runtime" when the
   ctor fills them from build-time blobs.
4. Every one of the six arrays is length **6**, allocated by the same helper
   (17879196) with `w1 = 6`, then filled by `InitializeArray(array, handle)`.
5. Readers: the three reward arrays are read together — `rewardIndexs` and
   `rewardValues` by the same three methods, `rewardScales` by two of them — while
   the bet ladders are read by `<GetPvPUserCachingDatas>d__78` and one method each.
   So a stage row is `(id, amount, icon scale)` at the same index, which is exactly
   the `SetInfo(number, isCards, scale)` shape 166/167 measured on the box side.
6. The bytes stay unread: 982 `<PrivateImplementationDetails>` blobs, 99 of them
   exactly 24 bytes, only 7 read as six plausible floats, and one of those seven is
   already attributed to `Board_Drones..ctor` by `ia-resolved.json`. Content cannot
   pick `rewardScales` out, so the two blobs stay `NOT_BOUND`.
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

import buy_delegate as BD  # noqa: E402

CLASS = 'Board_PVP'
CTOR = 19796420
CCTOR = 19796920
INIT_ARRAY = 0x205B07C      # RuntimeHelpers.InitializeArray(Array, RuntimeFieldHandle)
ARRAY_NEW = 0x110D09C       # the `newarr` helper
FIELD_DEFAULTS = 'reverse-engineering/il2cpp/field-defaults.json'
IA_RESOLVED = 'reverse-engineering/il2cpp/ia-resolved.json'
PREV133 = 'datas/l2_535b0541_pvp_hunter_reward_table.json.gz'
PREV132 = 'datas/l2_535b0541_key_sources.json.gz'
ARTIFACT = 'datas/l2_535b0541_pvp_reward_arrays.json.gz'

FIELDS = {0x198: ('rewardIndexs', 'int[]'), 0x1A0: ('rewardValues', 'int[]'),
          0x1A8: ('rewardScales', 'float[]'), 0x208: ('allBetCoinValues', 'int[]'),
          0x210: ('allBetGemValues', 'int[]'), 0x218: ('allBetMedalValues', 'int[]')}
LENGTH = 6
INDEXS_BLOB_DATA = 30944      # 133's `data_index` for the `rewardIndexs` data
INDEXS_BLOB_VALUES = [23, 0, 14, 1, 15, 18]


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


def text(insn):
    return insn['mnemonic'] + ' ' + insn['op_str']


@functools.lru_cache(maxsize=None)
def methods():
    return BD.slices()


@functools.lru_cache(maxsize=None)
def dump_lines():
    return gzip.decompress((ROOT / 'reverse-engineering/il2cpp/dump.cs.gz').read_bytes()) \
        .decode('utf-8', 'replace').splitlines()


def class_body(name=CLASS):
    start = next(number for number, line in enumerate(dump_lines())
                 if re.match(r'^\s*(public|internal) (sealed )?class %s\b' % name, line))
    out = []
    for line in dump_lines()[start + 1:]:
        if line.strip() == '}' and out:
            break
        out.append(line)
    return out


def fields_from_dump():
    """`{offset: (name, type)}` for the six arrays, straight out of dump.cs."""
    rows = {}
    for line in class_body():
        match = re.match(r'\s*private (\S+) (\w+); // 0x([0-9A-Fa-f]+)', line)
        if not match:
            continue
        declared, name, offset = match.group(1), match.group(2), int(match.group(3), 16)
        if offset in FIELDS:
            rows[hex(offset)] = dict(offset=hex(offset), name=name, declared=declared)
    return rows


def initializers():
    """One row per `InitializeArray` in the ctor: what it fills, and where it lands."""
    insns = methods()[(CLASS, CTOR)]['instructions']
    rows = []
    for number, insn in enumerate(insns):
        if BD.call_target(insn) != INIT_ARRAY:
            continue
        window = insns[max(0, number - 8):number + 2]
        allocate = next((item for item in window
                         if item['mnemonic'] == 'bl' and BD.call_target(item) == ARRAY_NEW), None)
        length = next((item for item in window if item['mnemonic'] == 'mov'
                       and item['op_str'].startswith('w1, #')), None)
        handle = next((item for item in reversed(window)
                       if item['mnemonic'] == 'ldr' and item['op_str'].startswith('x1,')), None)
        store = next((item for item in insns[number + 1:number + 3]
                      if item['mnemonic'] == 'str'), None)
        offset = None
        if store is not None:
            match = re.search(r'#(0x[0-9a-f]+)\]', store['op_str'])
            offset = int(match.group(1), 16) if match else None
        rows.append(dict(call=dict(rva=insn['rva'], op=text(insn)),
                         allocate=dict(rva=allocate['rva'], op=text(allocate)) if allocate else None,
                         length=BD.const(length['op_str']) if length else None,
                         handle=dict(rva=handle['rva'], op=text(handle)) if handle else None,
                         store=dict(rva=store['rva'], op=text(store)) if store else None,
                         offset=hex(offset) if offset is not None else None,
                         field=FIELDS.get(offset, (None, None))[0],
                         declared=FIELDS.get(offset, (None, None))[1]))
    return rows


def readers():
    """Who reads each array, deduped, with the reader's body checked in the slices."""
    rows = load('datas/l2_535b0541_pvp_hunter_arrays.json.gz')['arrays']
    out = {}
    for entry in rows:
        field = entry['field'].split('.')[-1]
        offset = entry['instance_offset']
        pattern = re.compile(r'\[x\d+, #%s\]' % hex(offset))
        sites = {}
        for reader in entry.get('readers', []):
            body = methods().get((reader['class_name'], reader['rva']))
            sites[(reader['class_name'], reader['rva'])] = dict(
                class_name=reader['class_name'], rva=reader['rva'],
                method=(body or {}).get('signature'),
                loads=len([insn for insn in (body or {}).get('instructions', [])
                           if pattern.search(insn['op_str'])]),
                body_in_slices=bool(body))
        out[field] = dict(offset=hex(offset), declared=entry['declared'],
                          elements=entry['elements'],
                          reads=sorted(sites.values(), key=lambda row: (row['class_name'],
                                                                        row['rva'])))
    return out


def cctor():
    row = methods()[(CLASS, CCTOR)]
    stores = [dict(rva=insn['rva'], op=text(insn)) for insn in row['instructions']
              if insn['mnemonic'] == 'str' and '[x8' in insn['op_str']]
    return dict(rva=CCTOR, size=row['size'], instructions=len(row['instructions']),
                signature=row['signature'], stores=stores)


def blobs():
    """The `InitializeArray` data census, and why it cannot name the two blobs."""
    fields = json.loads((ROOT / FIELD_DEFAULTS).read_text())['fields']
    pid = [dict(name=key.split('.')[-1], data_index=value['data_index'],
                field_index=value['field_index'], raw=bytes.fromhex(value['raw']))
           for key, value in fields.items() if 'PrivateImplementation' in key]
    sized = [row for row in pid if len(row['raw']) == 24]
    plausible = []
    for row in [item for item in pid if len(item['raw']) >= 24]:
        values = list(struct.unpack('<6f', row['raw'][:24]))
        if all(0.25 <= value <= 4.0 for value in values):
            plausible.append(dict(name=row['name'], data_index=row['data_index'],
                                  values=[round(value, 4) for value in values]))
    attributed = set()
    for method, entries in json.loads((ROOT / IA_RESOLVED).read_text())['methods'].items():
        for entry in entries:
            attributed.add(entry['field'].split('.')[-1])
    unclaimed = [row for row in plausible
                 if row['name'] not in attributed
                 and row['data_index'] != INDEXS_BLOB_DATA]
    indexs = next((row for row in pid if row['data_index'] == INDEXS_BLOB_DATA), None)
    return dict(pid_fields=len(pid), exactly_24_bytes=len(sized),
                float_plausible=plausible, unclaimed_floats=unclaimed,
                attributed_to_other_ctors=sorted(attributed & {row['name'] for row in plausible}),
                indexs_blob=dict(name=indexs['name'], data_index=indexs['data_index'],
                                 values=list(struct.unpack('<6i', indexs['raw'][:24])))
                if indexs else None,
                adjacent_data_indexes=sorted(row['data_index'] for row in pid
                                             if abs(row['data_index'] - INDEXS_BLOB_DATA) <= 64))


def reward_types():
    body = '\n'.join(class_body())
    item = next((row for row in load(PREV132)['not_decoded']
                 if 'rewardTypes' in (row.get('blocking') or '') + row.get('item', '')), None)
    return dict(in_class=body.count('rewardTypes'),
                cited_by_132=bool(item),
                cited_text=(item or {}).get('item'),
                cited_blocking=(item or {}).get('blocking'),
                fields_named=[row['name'] for row in fields_from_dump().values()])


def check(rows, name, passed, detail=None):
    rows.append(dict(name=name, passed=bool(passed), detail=detail))


def plain(value):
    if isinstance(value, dict):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, (set, frozenset)):
        return sorted(plain(item) for item in value)
    if isinstance(value, (list, tuple)):
        return [plain(item) for item in value]
    return value


def run_checks(init, read, blob, types, stat):
    checks = []
    fields = fields_from_dump()

    # -- the six calls ----------------------------------------------------
    check(checks, 'the-ctor-makes-six-initializearray-calls', len(init) == 6, len(init))
    check(checks, 'every-call-is-directly-followed-by-its-store',
          all(row['store'] and int(row['store']['rva']) == int(row['call']['rva']) + 4
              for row in init), [row['store'] for row in init])
    check(checks, 'the-six-offsets-are-the-six-fields',
          [row['offset'] for row in init] == ['0x198', '0x1a0', '0x1a8',
                                              '0x208', '0x210', '0x218'],
          [row['offset'] for row in init])
    check(checks, 'the-field-names-follow-the-offsets',
          [row['field'] for row in init] == [name for name, _ in FIELDS.values()],
          [row['field'] for row in init])
    check(checks, 'every-array-is-length-six',
          all(row['length'] == LENGTH for row in init), [row['length'] for row in init])
    check(checks, 'every-array-comes-from-the-same-helper',
          all(row['allocate'] for row in init), [row['allocate'] for row in init])
    check(checks, 'the-handle-of-each-call-comes-from-a-cell',
          all(row['handle']['op'].startswith('ldr x1') for row in init),
          [row['handle']['op'] for row in init])
    check(checks, 'the-dump-declares-the-six-types',
          {offset: row['declared'] for offset, row in fields.items()} ==
          {hex(offset): declared for offset, (_, declared) in FIELDS.items()}, fields)
    check(checks, 'rewardscales-is-a-float-array', fields['0x1a8']['declared'] == 'float[]',
          fields['0x1a8'])
    check(checks, 'the-ctor-matches-133s-call-rvas',
          [row['call']['rva'] for row in init] ==
          [entry['initarray_rva'] for entry in load(PREV133)['table']['arrays']],
          [row['call']['rva'] for row in init])

    # -- what 132 got wrong ----------------------------------------------
    check(checks, 'board_pvp-has-no-rewardtypes-field', types['in_class'] == 0, types)
    check(checks, '132s-item-names-a-field-that-does-not-exist',
          types['cited_by_132'] and 'rewardTypes' in (types['cited_blocking'] or '')
          and types['in_class'] == 0, types['cited_blocking'])
    check(checks, 'the-two-arrays-are-filled-in-the-ctor-not-at-runtime',
          [row['field'] for row in init] == [name for name, _ in FIELDS.values()]
          and all(row['store'] for row in init), [row['field'] for row in init])

    # -- readers ---------------------------------------------------------
    check(checks, 'all-six-arrays-have-readers', len(read) == 6, sorted(read))
    check(checks, 'every-reader-body-is-in-the-pinned-slices',
          all(site['body_in_slices'] for entry in read.values() for site in entry['reads']),
          {name: [site['rva'] for site in entry['reads']] for name, entry in read.items()})
    check(checks, 'every-reader-loads-its-own-offset',
          all(site['loads'] for entry in read.values() for site in entry['reads']),
          {name: [(site['rva'], site['loads']) for site in entry['reads']]
           for name, entry in read.items()})
    check(checks, 'the-three-reward-arrays-share-their-readers',
          [site['rva'] for site in read['rewardIndexs']['reads']] ==
          [site['rva'] for site in read['rewardValues']['reads']], read['rewardIndexs']['reads'])
    check(checks, 'rewardscales-is-read-by-two-of-them',
          [site['rva'] for site in read['rewardScales']['reads']] == [19791640, 19811092],
          read['rewardScales']['reads'])
    check(checks, 'the-extra-indexs-reader-is-the-collect-handler',
          [site['rva'] for site in read['rewardIndexs']['reads']] == [19791640, 19792936, 19811092],
          read['rewardIndexs']['reads'])
    check(checks, 'the-bet-ladders-share-one-reader-and-own-one-each',
          [site['rva'] for site in read['allBetCoinValues']['reads']] == [19779724, 19813332] and
          [site['rva'] for site in read['allBetGemValues']['reads']] == [19779984, 19813332] and
          [site['rva'] for site in read['allBetMedalValues']['reads']] == [19780244, 19813332],
          {name: [site['rva'] for site in read[name]['reads']]
           for name in ('allBetCoinValues', 'allBetGemValues', 'allBetMedalValues')})

    # -- the bytes -------------------------------------------------------
    check(checks, 'the-blob-census-is-982-pid-fields', blob['pid_fields'] == 982,
          blob['pid_fields'])
    check(checks, 'ninety-nine-blobs-are-exactly-24-bytes', blob['exactly_24_bytes'] == 99,
          blob['exactly_24_bytes'])
    check(checks, 'seven-read-as-six-plausible-floats', len(blob['float_plausible']) == 7,
          blob['float_plausible'])
    check(checks, 'three-of-the-seven-are-already-attributed-elsewhere',
          blob['attributed_to_other_ctors'] == sorted(
              ['7BB8C603EF9292AE455044ED83E2B9FE2DE6520959C86D6DEA54C895590A0D31',
               '849203E6B4E586413022AB65A115F70A9E41CB0EE678FA1984C90F7D4A5F33AD',
               'C9A0FA1D0ECC4E61C8B391176C4974E4CEC7B7B6D5446684E5735F4FC7AFC9CB']),
          blob['attributed_to_other_ctors'])
    check(checks, 'four-float-candidates-remain-unclaimed',
          len(blob['unclaimed_floats']) == 4
          and blob['unclaimed_floats'][0]['values'] == [0.8, 1.0, 1.5, 2.0, 2.5, 3.0],
          blob['unclaimed_floats'])
    check(checks, 'the-rewardindexs-blob-is-the-known-one',
          blob['indexs_blob'] and blob['indexs_blob']['values'] == INDEXS_BLOB_VALUES,
          blob['indexs_blob'])
    check(checks, 'no-float-candidate-sits-next-to-the-rewardindexs-data',
          all(row['data_index'] not in blob['adjacent_data_indexes']
              for row in blob['float_plausible']), blob['adjacent_data_indexes'])

    # -- the static ctor -------------------------------------------------
    check(checks, 'the-static-ctor-only-zeroes-a-struct',
          stat['size'] == 88 and [row['op'] for row in stat['stores']] ==
          ['str d0, [x8]', 'str xzr, [x8, #0x10]', 'str wzr, [x8, #0x18]'],
          stat['stores'])
    return checks


def build(output):
    init = initializers()
    read = readers()
    blob = blobs()
    types = reward_types()
    stat = cctor()
    checks = run_checks(init, read, blob, types, stat)
    payload = dict(
        schema=1,
        boundary='static read of the pinned dump, the pinned slices and the extracted field '
                 'defaults; no FDE, runtime, emulator, or device',
        evidence='STATIC_ONLY_ORIGINAL_APK',
        class_=CLASS,
        ctor=dict(rva=CTOR, size=methods()[(CLASS, CTOR)]['size'],
                  instructions=len(methods()[(CLASS, CTOR)]['instructions']),
                  signature=methods()[(CLASS, CTOR)]['signature'], initializers=init),
        fields=fields_from_dump(),
        readers=read,
        reward_types=types,
        blobs=blob,
        static_ctor=stat,
        corrections=[
            dict(report=132, item='PvP stage reward types and amounts',
                 was='`Board_PVP.rewardTypes/rewardValues` are instance arrays filled at runtime',
                 now='`Board_PVP` has no `rewardTypes` field; `rewardValues` (0x1a0) and '
                     '`rewardScales` (0x1a8, float[]) are filled in `..ctor` by '
                     '`InitializeArray` from build-time blobs, so the amounts are build data '
                     'whose *content* needs the metadata usage table'),
            dict(report=133, item='unresolved handle slots 0x2ae0010 / 0x2ae0018',
                 was='handle slots 0x2ae0010 / 0x2ae0018 are unresolved, so the field each '
                     'call fills is unknown',
                 now='the field is known from the adjacent store (call+4); only the blob bytes '
                     'stay unread, which is a narrower block than 133 recorded')],
        totals=dict(initializers=len(init), readers=sum(len(entry['reads']) for entry in read.values()),
                    blobs=blob['pid_fields'], float_candidates=len(blob['unclaimed_floats']),
                    arrays=len(FIELDS), length=LENGTH,
                    checks_passed=sum(1 for row in checks if row['passed']),
                    checks_total=len(checks)),
        provenance=dict(
            inputs=[dict(path=path, sha256=sha_file(path))
                    for path in (FIELD_DEFAULTS, IA_RESOLVED, PREV133, PREV132, BD.DUMP)],
            slices=[dict(path='reverse-engineering/raw/%s/native.json.gz' % path.parent.name,
                         sha256=sha_file('reverse-engineering/raw/%s/native.json.gz'
                                         % path.parent.name))
                    for path in sorted(ROOT.glob(BD.RAW_GLOB))]),
        checks=checks,
    )
    blob_json = json.dumps(payload, sort_keys=True, indent=1, ensure_ascii=False).encode('utf-8')
    packed = gzip.compress(blob_json, mtime=0)
    if output:
        (ROOT / output).write_bytes(packed)
    return payload, packed


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--output', default=ARTIFACT)
    args = parser.parse_args()
    payload, packed = build(args.output)
    failed = [row['name'] for row in payload['checks'] if not row['passed']]
    print(json.dumps(dict(bytes=len(packed), sha256=hashlib.sha256(packed).hexdigest(),
                          checks_passed=payload['totals']['checks_passed'],
                          checks_total=payload['totals']['checks_total'],
                          failed=failed), indent=1))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
