#!/usr/bin/env python3
"""`ArenaConfig`: the remote tier above `ArenaManager`. STATIC only.

Report 139 established that `Board_Arena.GetConfigs` copies `ArenaConfig` statics
onto `ArenaManager` statics and that the `+0x1C` fail-closed gate belongs to
`ArenaConfig`, not `ArenaManager`. This report decodes the tier itself:

* `ArenaConfig..cctor` (RVA 22726640, 164 B) ships every field already filled —
  two 10-element strings, two room counts packed into one 8-byte literal, a float
  summary time, and `IsOpen = false`.
* The season table is therefore available without any server: ten seasons, each a
  rank window from `RankSplit` and a duration from `SeasonTime`.
* The unit is **minutes**, and that is measured, not assumed: the reader
  `ArenaManager.IESetRankSetups` feeds `SeasonTimes[i]` through `scvtf` into
  `DateTime.AddMinutes` (RVA 21621968), and `IECheckUserStatus` does the same with
  `SeasonSummaryTime` before comparing against the current time.
* The gate chain is `Board_Arena.IECheckArenaOpen` -> `ArenaConfig.IsOpen` ->
  `GetConfigs()` -> `<game config flag>` -> `GetGameConfig()`.

The field map is locked by **metadata slot** (`0x2AECA98` for `ArenaConfig`,
`0x2AE19D0` for the `ArenaManager` block) rather than by which method contains the
instruction. Report 138 got that wrong once; a slot-keyed scan cannot repeat it,
and it also rejects the `str x0,[x9,#0x18]` in `GetConfigs` that writes
`ArenaManager.SeasonTimes` while the register still looks like config statics.
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

CCtor = 22726640
CHECK_OPEN = 22810128
SET_RANK_SETUPS = 22720624
CHECK_USER_STATUS = 22707048

CONFIG_SLOT = 0x2AECA98
ARENA_SLOT = 0x2AE19D0
GAME_CONFIG_SLOT = 0x2ADB8E0

ADD_MINUTES = 0x20E6CF0
GE_DATETIME = 0x20EA03C

FIELD_LINE = re.compile(r'public static ([\w\[\]<>]+) (\w+); // 0x([0-9A-Fa-f]+)')


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


def body(blob, rva):
    return [row for row in blob['methods'] if row['rva'] == rva][0]


def dump_text():
    return gzip.decompress((ROOT / DUMP).read_bytes()).decode('utf-8', 'replace')


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


def class_fields(text, header):
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


def norm(reg):
    return 'x' + reg[1:]


def slot_access(blob, slot):
    """Every read/write of the statics behind one metadata slot.

    Precedence matters: a register that held a page can be overwritten by a slot
    load, so the slot dereference is tested **before** the page test, and any
    register redefined by a non-tracked load loses its statics/klass role. Without
    that, `GetConfigs` attributes its `ArenaManager` store to `ArenaConfig`.
    """
    out = []
    for method in blob['methods']:
        pages, slots, klasses, statics, rows = {}, {}, {}, set(), []
        for insn in method['instructions']:
            op, mnemonic = insn['op_str'], insn['mnemonic']
            adrp = re.fullmatch(r'(x\d+), #(0x[0-9a-f]+)', op)
            if mnemonic == 'adrp' and adrp:
                reg = norm(adrp.group(1))
                pages[reg] = int(adrp.group(2), 0)
                slots.pop(reg, None)
                klasses.pop(reg, None)
                statics.discard(reg)
                continue
            if ', [' not in op or mnemonic not in ('ldr', 'str', 'strb', 'ldrb'):
                continue
            dest, rest = op.split(', ', 1)
            hit = re.fullmatch(r'\[(x\d+)(?:, #(0x[0-9a-f]+|-?\d+))?\]', rest)
            if not hit:
                statics.discard(norm(dest))
                continue
            base = norm(hit.group(1))
            offset = int(hit.group(2), 0) if hit.group(2) else 0
            target = norm(dest)
            if mnemonic == 'ldr' and offset == 0 and base in slots:
                klasses[target] = slots[base]
                statics.discard(target)
                pages.pop(target, None)
                continue
            if mnemonic == 'ldr' and base in pages:
                slots[target] = pages[base] + offset
                pages.pop(target, None)
                klasses.pop(target, None)
                statics.discard(target)
                continue
            if mnemonic == 'ldr' and offset == 0xB8 and base in klasses:
                statics.discard(target)
                if klasses[base] == slot:
                    statics.add(target)
                continue
            if base in statics:
                rows.append(dict(rva=insn['rva'], kind='read' if 'ldr' in mnemonic
                                 else 'write', mnemonic=mnemonic, offset=offset))
                continue
            statics.discard(target)
        if rows:
            out.append(dict(class_name=method['class_name'],
                            name=method['signature'].strip().split('(')[0].split()[-1],
                            signature=method['signature'].strip(), rva=method['rva'],
                            size=method['size'], accesses=rows))
    return out


def cctor_payload(row, strings, fields):
    code = {insn['rva']: insn for insn in row['instructions']}
    by_offset = {field['offset']: field for field in fields}

    rank_split_ref = [ref for ref in row['slot_refs'] if ref['rva'] == 22726736][0]
    season_ref = [ref for ref in row['slot_refs'] if ref['rva'] == 22726760][0]
    rank_split = strings[rank_split_ref['addend']]
    season_time = strings[season_ref['addend']]

    packed = [item for item in row['literals'] if item['instruction_rva'] == 22726764][0]
    max_room, min_room = struct.unpack('<ii', bytes.fromhex(packed['hex']))
    summary_bits = code[22726776]['op_str'].split('#')[1]
    summary = struct.unpack('<f', struct.pack('<I', int(summary_bits, 16)))[0]

    writes = [
        dict(rva=22726748, offset=0x0, value=rank_split, kind='str x9'),
        dict(rva=22726780, offset=0x8, value=season_time, kind='str x10'),
        dict(rva=22726784, offset=0x10, value=max_room,
             kind='str d0 (low half of an 8-byte literal)'),
        dict(rva=22726784, offset=0x14, value=min_room,
             kind='str d0 (high half of the same literal)'),
        dict(rva=22726788, offset=0x18, value=summary, kind='str w9 (movz float bits)'),
        dict(rva=22726792, offset=0x1C, value=False, kind='strb wzr'),
    ]
    for write in writes:
        write['field'] = by_offset[write['offset']]['name']
        write['field_type'] = by_offset[write['offset']]['type']
    assert [row['offset'] for row in writes] == \
        [0x0, 0x8, 0x10, 0x14, 0x18, 0x1C], writes
    assert summary_bits == '0x42700000' and summary == 60.0
    return dict(writes=writes, rank_split=rank_split, season_time=season_time,
                packed_literal=dict(instruction_rva=22726764, hex=packed['hex'],
                                    va=packed['va'],
                                    decoded=dict(MaxRoomCount=max_room,
                                                 MinRoomCount=min_room)),
                summary_literal=dict(instruction_rva=22726776, bits=summary_bits,
                                     value=summary,
                                     note='float bit pattern, not an address'))


def season_table(rank_split, season_time):
    splits = rank_split.split(';')
    durations = season_time.split(';')
    assert len(splits) == len(durations) == 10, (len(splits), len(durations))
    rows = []
    for index, (split, duration) in enumerate(zip(splits, durations)):
        bounds = split.split('-')
        assert len(bounds) == 2, split
        low, high = (int(value) for value in bounds)
        assert 0 < low <= high, split
        rows.append(dict(season=index, rank_low=low, rank_high=high,
                         minutes=int(duration),
                         days=round(int(duration) / 1440, 4)))
    minutes = [row['minutes'] for row in rows]
    assert minutes == sorted(minutes) and len(set(minutes)) == 10, minutes
    for row in rows:
        assert row['days'] == int(row['days']), row
    return dict(count=len(rows), rows=rows,
                totals=dict(first_minutes=rows[0]['minutes'],
                            last_minutes=rows[-1]['minutes'],
                            unique_durations=len(set(minutes))))


def unit_proof(blob, sigs):
    """`SeasonTimes[i]` reaches `DateTime.AddMinutes`, which pins the unit."""
    setups = {insn['rva']: insn for insn in body(blob, SET_RANK_SETUPS)['instructions']}
    assert setups[22721052]['op_str'] == 'x8, [x8, #0x18]'          # SeasonTimes
    assert setups[22721092]['mnemonic'] == 'scvtf'
    assert setups[22721096]['op_str'] == '#0x20e6cf0'
    assert sigs[ADD_MINUTES] == 'public DateTime AddMinutes(double value) { }'

    status = {insn['rva']: insn for insn in body(blob, CHECK_USER_STATUS)['instructions']}
    assert status[22708728]['op_str'] == 'd8, [x9, #0x10]'          # SeasonSummaryTime
    assert status[22708760]['op_str'] == '#0x20e6cf0'
    assert status[22708776]['op_str'] == '#0x20ea03c'
    assert sigs[GE_DATETIME] == ('public static bool op_GreaterThanOrEqual(DateTime t1, '
                                 'DateTime t2) { }')
    return dict(
        call=dict(rva=ADD_MINUTES, signature=sigs[ADD_MINUTES]),
        witnesses=[
            dict(method='ArenaManager.IESetRankSetups', rva=SET_RANK_SETUPS,
                 instruction_rva=22721052, reads='SeasonTimes (+0x18)'),
            dict(method='ArenaManager.IESetRankSetups', rva=SET_RANK_SETUPS,
                 instruction_rva=22721096, calls='DateTime.AddMinutes'),
            dict(method='ArenaManager.IECheckUserStatus', rva=CHECK_USER_STATUS,
                 instruction_rva=22708728, reads='SeasonSummaryTime (+0x10)'),
            dict(method='ArenaManager.IECheckUserStatus', rva=CHECK_USER_STATUS,
                 instruction_rva=22708776, calls='DateTime.op_GreaterThanOrEqual'),
        ],
        verdict='SeasonTimes values are minutes; season N ends SeasonTimes[N] minutes '
                'after the current season starts')


def gate_chain(blob, sigs):
    code = {insn['rva']: insn for insn in body(blob, CHECK_OPEN)['instructions']}
    assert code[22810692]['op_str'] == 'w8, [x8, #0x1c]'            # ArenaConfig.IsOpen
    assert code[22810696]['op_str'] == 'w8, #0x15c1104'             # skip when false
    assert code[22810700]['op_str'] == '#0x15ba060'                 # GetConfigs()
    assert code[22810736]['op_str'] == 'w9, [x8, #4]'               # game-config flag
    assert code[22810796]['op_str'] == '#0x15be1d8'                 # GetGameConfig()
    return dict(
        method=dict(class_name='Board_Arena.<IECheckArenaOpen>d__55', rva=CHECK_OPEN,
                    signature=body(blob, CHECK_OPEN)['signature'].strip()),
        steps=[
            dict(rva=22810692, step='ldrb w8,[statics,#0x1c]', reads='ArenaConfig.IsOpen'),
            dict(rva=22810696, step='cbz w8', effect='skip the whole load when closed'),
            dict(rva=22810700, step='bl GetConfigs', target_rva=22782048,
                 signature=sigs[22782048]),
            dict(rva=22810736, step='ldrb w9,[statics,#4]',
                 reads='class behind slot 0x2ADB8E0, field +4'),
            dict(rva=22810796, step='bl GetGameConfig', target_rva=22798808,
                 signature=sigs[22798808]),
        ],
        game_config_slot=dict(va=GAME_CONFIG_SLOT, decimal=GAME_CONFIG_SLOT))


def build_payload():
    blob = load(NATIVE)
    strings = string_table()
    text = dump_text()
    sigs = signatures(text)

    fields = class_fields(text, 'public class ArenaConfig')
    assert [field['offset'] for field in fields] == [0x0, 0x8, 0x10, 0x14, 0x18, 0x1C]

    row = body(blob, CCtor)
    cctor = cctor_payload(row, strings, fields)
    seasons = season_table(cctor['rank_split'], cctor['season_time'])
    unit = unit_proof(blob, sigs)
    chain = gate_chain(blob, sigs)

    config_access = slot_access(blob, CONFIG_SLOT)
    arena_access = slot_access(blob, ARENA_SLOT)
    writers = [row for row in config_access
               if any(item['kind'] == 'write' for item in row['accesses'])]
    readers = [row for row in config_access
               if any(item['kind'] == 'read' for item in row['accesses'])]

    # The bridge must appear on both sides and must not be mis-attributed.
    bridge = [row for row in arena_access if row['rva'] == 22782048][0]
    bridge_writes = {item['offset'] for item in bridge['accesses']
                     if item['kind'] == 'write'}
    assert bridge_writes == {0x4, 0x8, 0x10, 0x18, 0x28, 0x30}, bridge_writes
    assert all(item['offset'] != 0x18 for item in
               [x for x in config_access if x['rva'] == 22782048][0]['accesses']
               if item['kind'] == 'write'), 'config statics must not receive +0x18'

    return dict(
        schema=1,
        evidence='STATIC_ONLY_ORIGINAL_APK',
        note='`ArenaConfig` ships fully populated, so the season table below exists '
             'without a server. Any later remote load overwrites it and is '
             'MODEL_NOT_MEASURED runtime.',
        provenance=dict(
            xapk_sha256=blob['xapk_sha256'],
            libil2cpp_sha256=blob['libil2cpp_sha256'],
            dump_sha256=blob['dump_sha256'],
            sources=[dict(path=NATIVE, sha256=sha_file(NATIVE),
                          role='ArenaConfig..cctor, readers, gate chain'),
                     dict(path=STRINGS, sha256=sha_file(STRINGS),
                          role='RankSplit and SeasonTime literals'),
                     dict(path=DUMP, sha256=sha_file(DUMP),
                          role='field layout and callee signatures')]),
        layout=dict(fields=fields,
                    slots=dict(arena_config=dict(va=CONFIG_SLOT, decimal=CONFIG_SLOT),
                               arena_manager=dict(va=ARENA_SLOT, decimal=ARENA_SLOT))),
        cctor=dict(rva=row['rva'], size=row['size'], sha256=row['sha256'],
                   signature=row['signature'].strip(),
                   writes=cctor['writes'],
                   packed_literal=cctor['packed_literal'],
                   summary_literal=cctor['summary_literal']),
        seasons=seasons,
        unit_proof=unit,
        gate_chain=chain,
        access=dict(arena_config=config_access, arena_manager=arena_access,
                    writers=[dict(class_name=row['class_name'], name=row['name'],
                                  rva=row['rva']) for row in writers],
                    readers=[dict(class_name=row['class_name'], name=row['name'],
                                  rva=row['rva']) for row in readers]),
        cross_checks=dict(
            arena_manager_season_times=dict(
                claim='after Board_Arena.GetConfigs runs, ArenaManager.SeasonTimes '
                      'equals the ten durations parsed from ArenaConfig.SeasonTime',
                minutes=[row['minutes'] for row in seasons['rows']],
                proven_by='139 parse pipeline (Split(\';\') -> Int32.Parse) + 140 '
                          'literal'),
            summary_time_matches_139=dict(arena_config=60.0, arena_manager=60.0,
                                         note='float 60.0 widened to double 60.0'),
            room_counts=dict(arena_config=dict(MaxRoomCount=50, MinRoomCount=10),
                             arena_manager=dict(MaxRoomCount=50, MinUserCount=10),
                             note='MinRoomCount and MinUserCount carry the same 10')),
        method=dict(
            slot_keyed=True,
            rule='a register is a page, a metadata slot, a klass or statics; '
                 'redefinition clears the old role, and the slot dereference is '
                 'tested before the page test',
            regression_witness=dict(
                rva=22782328, instruction='str x0, [x9, #0x18]',
                naive_result='ArenaConfig write at +0x18 (wrong)',
                correct_result='ArenaManager write at +0x18 (SeasonTimes)',
                why='x9 was `ArenaConfig` statics earlier in the same method and is '
                    'reloaded from the ArenaManager block two instructions before the '
                    'store; keeping statics sticky mis-attributes the store'),
        ),
        not_decoded=[
            dict(item='class behind slot 0x2ADB8E0 (44939488)',
                 blocking='the gate chain tests its field +4 before calling '
                          'GetGameConfig, but no pinned symbol names that class'),
            dict(item='served overrides of the shipped table',
                 blocking='`ArenaConfig` is rewritten by the remote loader at runtime '
                          'and the database is not in the APK — MODEL_NOT_MEASURED '
                          'runtime'),
        ],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_arena_config.json.gz')
    args = parser.parse_args()
    payload = build_payload()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                                sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          writes=len(payload['cctor']['writes']),
                          seasons=payload['seasons']['count'],
                          config_writers=len(payload['access']['writers']),
                          config_readers=len(payload['access']['readers']))))


if __name__ == '__main__':
    main()
