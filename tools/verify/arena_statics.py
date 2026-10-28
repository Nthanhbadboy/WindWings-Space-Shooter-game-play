#!/usr/bin/env python3
"""`ArenaManager` statics: the shipped defaults, the arena reward table, and the
ArenaConfig bridge. STATIC only.

Three facts come out of the pinned bytes and nothing else:

1. `ArenaManager..cctor` (RVA 22692372, 516 B) writes the whole static block:
   `IsOpen = false`, `MaxRoomCount = 50`, `MinUserCount = 25`,
   `SeasonSummaryTime = 60.0`, `SeasonTimes = null`, `RankMapsIndex = 0`,
   `RankUpIndexs = null`, `RankDropIndexs = null`, and a `newarr` of ten strings
   into `rewards`. The first two ints arrive as **one** 8-byte literal
   (`3200000019000000` at VA 7699216), so a naive reader that decodes it as a
   double sees `5.3e-313` instead of two ints.
2. Those ten strings are the arena payout table, measured verbatim: six placement
   bands (`#1`, `#2`, `#3-4`, `#5-10`, `#11-45`, `#46-50`) each carrying
   `Medal` and `Gems`, escalating with the rank tier.
3. `Board_Arena.GetConfigs` (RVA 22782048, 800 B) is the second writer: it copies
   `ArenaConfig` statics into `ArenaManager` statics, turning the two config
   strings into int arrays with `Replace("\\"", null)` -> `Split(';')` ->
   `int.Parse`, and splitting each rank band on `'-'`.

The report also corrects 138: the fail-closed `+0x1C` store in
`ArenaManager.LoadRemoteConfigs` belongs to **`ArenaConfig.IsOpen`**, not
`ArenaManager` (whose `IsOpen` sits at `+0x0` and is only written by `..cctor`).
The layouts prove it: `ArenaConfig` is `string@0, string@8, int@0x10, int@0x14,
float@0x18, bool@0x1C`, and the same metadata slot `0x2AECA98` is used by
`ArenaConfig`, `Board_Arena` and `ArenaManager`.
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

NATIVE = 'reverse-engineering/raw/arena-pvp-535b0541/native.json.gz'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'
STRINGS = 'reverse-engineering/il2cpp/stringliteral.json'

CCTOR = 22692372
GET_CONFIGS = 22782048
ARENA_SLOT = 0x2AE19D0       # metadata slot whose layout is ArenaManager's static block
CONFIG_SLOT = 0x2AECA98      # metadata slot used by ArenaConfig / Board_Arena
TO_ROMAN = 21103836

BAND = re.compile(r'#([\d\-]+)\[Medal:(\d+),Gems:(\d+)\]')
FIELD_LINE = re.compile(r'public static ([\w\[\]<>]+) (\w+); // 0x([0-9A-Fa-f]+)')


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


def body(blob, rva):
    return [row for row in blob['methods'] if row['rva'] == rva][0]


def dump_text():
    return gzip.decompress((ROOT / DUMP).read_bytes()).decode('utf-8', 'replace')


def class_fields(text, header):
    """Static fields of one class, in declaration order, as (type, name, offset)."""
    lines = text.split('\n')
    start = next(index for index, line in enumerate(lines) if line.strip().startswith(header))
    out = []
    for line in lines[start + 1:]:
        if '// Methods' in line or '// Properties' in line:
            break
        found = FIELD_LINE.search(line)
        if found:
            out.append(dict(type=found.group(1), name=found.group(2),
                            offset=int(found.group(3), 16)))
    return out


def string_table():
    return {int(row['address'], 16): row['value']
            for row in json.loads((ROOT / STRINGS).read_text())}


def signatures(text):
    lines = text.split('\n')
    out = {}
    for index, line in enumerate(lines[:-1]):
        found = re.search(r'// RVA: 0x([0-9A-Fa-f]+)', line)
        if not found:
            continue
        nxt = lines[index + 1].strip()
        if '(' in nxt and not nxt.startswith('//'):
            out[int(found.group(1), 16)] = nxt
    return out


def imm_double(text):
    """`mov x9, #0x404E000000000000` carries a double bit pattern, not an address."""
    return struct.unpack('<d', struct.pack('<Q', int(text, 16)))[0]


def cctor_payload(row, strings, fields):
    code = row['instructions']
    index = {insn['rva']: insn for insn in code}
    by_offset = {field['offset']: field for field in fields}

    writes = []
    reward_stores = []

    def record(rva, offset, value, kind):
        assert offset in by_offset, (hex(offset), 'not a declared static field')
        writes.append(dict(rva=rva, offset=offset, field=by_offset[offset]['name'],
                           field_type=by_offset[offset]['type'], kind=kind, value=value))

    assert index[22692584]['op_str'] == 'wzr, [x8]'
    record(22692584, 0x0, False, 'strb wzr')
    assert index[22692588]['op_str'] == 'd0, [x8, #4]'
    packed = index[22692568]
    assert packed['mnemonic'] == 'ldr' and packed['op_str'] == 'd0, [x9, #0xb10]'
    literal = [item for item in row['literals'] if item['instruction_rva'] == 22692568][0]
    raw = bytes.fromhex(literal['hex'])
    max_room, min_user = struct.unpack('<ii', raw)
    record(22692588, 0x4, max_room, 'stur d0 (low half of an 8-byte literal)')
    record(22692588, 0x8, min_user, 'stur d0 (high half of the same literal)')
    assert index[22692592]['op_str'] == 'x9, xzr, [x8, #0x10]'
    summary = imm_double(index[22692572]['op_str'].split('#')[1])
    record(22692592, 0x10, summary, 'stp x9 (movz double bit pattern)')
    record(22692592, 0x18, None, 'stp xzr (null array)')
    assert index[22692596]['op_str'] == 'wzr, [x8, #0x20]'
    record(22692596, 0x20, 0, 'str wzr')
    assert index[22692600]['op_str'] == 'xzr, xzr, [x8, #0x28]'
    record(22692600, 0x28, None, 'stp xzr (null array)')
    record(22692600, 0x30, None, 'stp xzr (null array)')

    # newarr: `ldr x0,[x20]` where x20 holds the element-type slot, then `mov w1,#0xa`.
    assert index[22692580]['op_str'] == 'w1, #0xa'
    assert index[22692608]['op_str'] == '#0x110d09c'

    # Ten stores of one literal string each into `rewards` at 0x20 .. 0x68.
    for insn in code:
        if insn['mnemonic'] != 'str':
            continue
        found = re.fullmatch(r'(x\d+), \[x0, #(0x[0-9a-f]+)\]', insn['op_str'])
        if not found:
            continue
        offset = int(found.group(2), 0)
        if not 0x20 <= offset <= 0x68:
            continue
        refs = [ref for ref in row['slot_refs'] if ref['rva'] < insn['rva']]
        value = strings.get(refs[-1]['addend'])
        assert value is not None, hex(insn['rva'])
        reward_stores.append(dict(rva=insn['rva'], element=offset // 8 - 4,
                                  load_rva=refs[-1]['rva'],
                                  literal_address=refs[-1]['addend'], value=value))

    assert len(reward_stores) == 10, len(reward_stores)
    assert [item['element'] for item in reward_stores] == list(range(10))
    record(22692868, 0x38, 'string[10]', 'str x0 (array handle)')

    # Every declared field must be covered exactly once, in offset order.
    assert [item['offset'] for item in writes] == sorted(by_offset), writes
    return writes, reward_stores


def parse_rewards(stores):
    rows, band_labels = [], None
    for store in stores:
        bands = BAND.findall(store['value'])
        assert len(bands) == 6, (store['element'], bands)
        labels = [band[0] for band in bands]
        band_labels = band_labels or labels
        assert labels == band_labels, (labels, band_labels)
        assert store['value'] == ';'.join(
            '#%s[Medal:%s,Gems:%s]' % band for band in bands)
        rows.append(dict(rank=store['element'], element_rva=store['rva'],
                         literal_address=store['literal_address'],
                         bands=[dict(placement=label, medal=int(medal), gems=int(gems))
                                for label, medal, gems in bands]))
    assert band_labels == ['1', '2', '3-4', '5-10', '11-45', '46-50'], band_labels
    for column in range(6):
        medals = [row['bands'][column]['medal'] for row in rows]
        gems = [row['bands'][column]['gems'] for row in rows]
        # Non-decreasing across rank tiers; the low bands share a gems value.
        assert medals == sorted(medals), medals
        assert gems == sorted(gems), gems
        assert len(medals) == 10 and len(gems) == 10
    return dict(count=len(rows), bands=band_labels, rows=rows)


def get_configs(row, strings, sigs, arena_fields, config_fields):
    code = {insn['rva']: insn for insn in row['instructions']}
    reads = [
        (22782184, CONFIG_SLOT, 0x10, 'MaxRoomCount int'),
        (22782220, CONFIG_SLOT, 0x14, 'MinRoomCount int'),
        (22782228, CONFIG_SLOT, 0x18, 'SummaryTime float'),
        (22782240, CONFIG_SLOT, 0x08, 'SeasonTime string'),
        (22782480, CONFIG_SLOT, 0x00, 'RankSplit string'),
    ]
    writes = [
        (22782216, 0x04, 'MaxRoomCount'),
        (22782224, 0x08, 'MinUserCount'),
        (22782236, 0x10, 'SeasonSummaryTime'),
        (22782328, 0x18, 'SeasonTimes int[]'),
        (22782576, 0x28, 'RankUpIndexs int[]'),
        (22782600, 0x30, 'RankDropIndexs int[]'),
    ]
    arena_names = {field['offset']: field['name'] for field in arena_fields}
    config_names = {field['offset']: field['name'] for field in config_fields}
    for rva, _slot, offset, label in reads:
        assert offset in config_names, (hex(offset), label, config_names)
    for rva, offset, label in writes:
        assert arena_names.get(offset, '').split()[0].startswith(label.split()[0]), (
            hex(offset), label, arena_names.get(offset))

    pipeline = [
        dict(rva=22782232, step='fcvt d0, s0',
             note='SummaryTime float -> SeasonSummaryTime double'),
        dict(rva=22782268, step='string.Replace(<quote char>, null)',
             signature=sigs[0x1FEE8B4],
             note='strip the double quotes the served strings are wrapped in'),
        dict(rva=22782288, step="Split(';')", signature=sigs[0x1FEEEE0]),
        dict(rva=22782404, step='Int32.Parse', signature=sigs[0x2103668],
             note='one int per season -> SeasonTimes[i]'),
        dict(rva=22782652, step="Split('-')", signature=sigs[0x1FEEEE0]),
        dict(rva=22782712, step='Int32.Parse (lower bound)',
             signature=sigs[0x2103668], note='-> RankUpIndexs[i]'),
        dict(rva=22782772, step='Int32.Parse (upper bound)',
             signature=sigs[0x2103668], note='-> RankDropIndexs[i]'),
    ]
    for item in pipeline:
        assert item['rva'] in code, item
    return dict(rva=row['rva'], size=row['size'], sha256=row['sha256'],
                reads=[dict(rva=rva, slot=hex(CONFIG_SLOT), offset=offset,
                            field=config_names[offset]) for rva, _s, offset, _l in reads],
                writes=[dict(rva=rva, offset=offset,
                             field=arena_names[offset]) for rva, offset, _l in writes],
                pipeline=pipeline)


def build_payload():
    blob = load(NATIVE)
    strings = string_table()
    text = dump_text()
    sigs = signatures(text)

    arena_fields = class_fields(text, 'public class ArenaManager : MonoBehaviour')
    config_fields = class_fields(text, 'public class ArenaConfig')
    assert [field['offset'] for field in arena_fields] == \
        [0x0, 0x4, 0x8, 0x10, 0x18, 0x20, 0x28, 0x30, 0x38], arena_fields
    assert [field['offset'] for field in config_fields] == \
        [0x0, 0x8, 0x10, 0x14, 0x18, 0x1C], config_fields

    cctor = body(blob, CCTOR)
    writes, stores = cctor_payload(cctor, strings, arena_fields)
    rewards = parse_rewards(stores)
    bridge = get_configs(body(blob, GET_CONFIGS), strings, sigs,
                         arena_fields, config_fields)

    # The ToRoman body is still unpinned: no raw in the repo carries that RVA.
    to_roman = []
    for path in sorted(ROOT.glob('reverse-engineering/raw/*/native.json.gz')):
        data = json.loads(gzip.decompress(path.read_bytes()))
        if any(row['rva'] == TO_ROMAN for row in data['methods']):
            to_roman.append(str(path.relative_to(ROOT)))

    return dict(
        schema=1,
        evidence='STATIC_ONLY_ORIGINAL_APK',
        note='Defaults and the payout table are read from the pinned `.cctor`; the '
             'config bridge is read from `Board_Arena.GetConfigs`. The served values '
             'the bridge parses (season times, rank bands, room counts) live in the '
             'remote database and are MODEL_NOT_MEASURED runtime.',
        provenance=dict(
            xapk_sha256=blob['xapk_sha256'],
            libil2cpp_sha256=blob['libil2cpp_sha256'],
            dump_sha256=blob['dump_sha256'],
            sources=[dict(path=NATIVE, sha256=sha_file(NATIVE),
                          role='ArenaManager..cctor, Board_Arena.GetConfigs'),
                     dict(path=STRINGS, sha256=sha_file(STRINGS),
                          role='the ten payout strings and the quote character'),
                     dict(path=DUMP, sha256=sha_file(DUMP),
                          role='static field layouts and callee signatures')]),
        layout=dict(arena_manager=arena_fields, arena_config=config_fields,
                    slots=dict(arena_manager=dict(va=ARENA_SLOT, decimal=ARENA_SLOT),
                               arena_config=dict(va=CONFIG_SLOT, decimal=CONFIG_SLOT))),
        cctor=dict(rva=cctor['rva'], size=cctor['size'], sha256=cctor['sha256'],
                   signature=cctor['signature'].strip(),
                   newarr=dict(rva=22692604, length=10,
                               note='element type comes from metadata slot 0x2ADB7D0; '
                                    'the ten stored values are string literals'),
                   packed_literal=dict(rva=22692568, va=7699216,
                                       hex=[item for item in cctor['literals']
                                            if item['instruction_rva'] == 22692568][0]['hex'],
                                       decoded=dict(MaxRoomCount=max_room(writes),
                                                    MinUserCount=min_user(writes)),
                                       note='one 8-byte store covers two int fields; as a '
                                            'double it would read 5.3e-313'),
                   double_literal=dict(rva=22692572,
                                       bit_pattern='0x404E000000000000',
                                       value=imm_double('404E000000000000')),
                   writes=writes),
        rewards=rewards,
        config_bridge=dict(method=bridge,
                           direction='ArenaConfig statics -> ArenaManager statics',
                           served_shape=dict(
                               SeasonTime='quoted, semicolon separated ints',
                               RankSplit='quoted, semicolon separated `lo-hi` pairs')),
        corrections=[dict(
            item='138: the fail-closed `+0x1C` store in ArenaManager.LoadRemoteConfigs '
                 'is `ArenaManager.IsOpen`',
            measured='it is `ArenaConfig.IsOpen`: the store goes through metadata slot '
                     '0x2AECA98, whose class also serves Board_Arena and ArenaConfig, '
                     'and `ArenaConfig` declares `bool IsOpen; // 0x1C` while '
                     '`ArenaManager` declares `bool IsOpen; // 0x0`',
            why_missed='138 tracked the statics base by register but did not check '
                       'which klass the metadata slot belongs to, so a field at +0x1C '
                       'was attributed to the class whose method contained the store',
            impact='`ArenaManager.IsOpen` is only ever written by `..cctor` (false); '
                   'the remote gate is `ArenaConfig.IsOpen`, which '
                   '`Board_Arena.GetConfigs` reads indirectly by copying the config '
                   'onto ArenaManager')],
        confirmations=[dict(item='127: ArenaManager.SeasonTimes / RankUpIndexs / '
                                'RankDropIndexs come from remote',
                            result='confirmed — `Board_Arena.GetConfigs` parses them '
                                   'from two served strings and `..cctor` leaves all '
                                   'three null')],
        not_decoded=[
            dict(item='served config values',
                 blocking='season times, rank bands and room counts are parsed from the '
                          'remote database, which is not in the APK — '
                          'MODEL_NOT_MEASURED runtime'),
            dict(item='`rewards` consumer',
                 blocking='no method in this raw indexes `ArenaManager.rewards` (+0x38) '
                          'after tracking the klass slot; the reader is in a class '
                          'outside the arena-pvp raw or loads the array through a '
                          'different slot'),
            dict(item='`MyLibrary.ToRoman` glyph table',
                 blocking='RVA 21103836 appears in %d pinned raws (searched all of '
                          'reverse-engineering/raw/*/native.json.gz), so the roman '
                          'numerals printed by `GetRankNumber` stay unmeasured'
                          % len(to_roman)),
        ],
        to_roman_sweep=dict(rva=TO_ROMAN, raws_searched=len(
            list(ROOT.glob('reverse-engineering/raw/*/native.json.gz'))),
            found_in=to_roman),
    )


def max_room(writes):
    return [row['value'] for row in writes if row['offset'] == 0x4][0]


def min_user(writes):
    return [row['value'] for row in writes if row['offset'] == 0x8][0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_arena_statics.json.gz')
    args = parser.parse_args()
    payload = build_payload()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                                sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          writes=len(payload['cctor']['writes']),
                          rewards=payload['rewards']['count'],
                          bands=len(payload['rewards']['bands']),
                          bridge_reads=len(payload['config_bridge']['method']['reads']))))


if __name__ == '__main__':
    main()
