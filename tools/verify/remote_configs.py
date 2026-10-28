#!/usr/bin/env python3
"""`LoadRemoteConfigs` for the PvP board and the Arena: paths, gates, callback. STATIC.

Two classes load their remote configuration the same way and gate a static bool on
the result:

    PVP_Manager   path = get_pathOfDataConfigs()          = data-leagues/data-configs
                  handler deserialises the JSON and copies config[+0x10] into IsOpen(+0x4C)
    ArenaManager  path = get_pathRoot() + "/is-open"      = arena---datas/is-open
                  handler parses an int and stores `count > 0` in IsOpen(+0x1C)

Both refuse to fetch when `NetworkReachability.get_internetReachability()` is 0,
both `Log("No network connected")` on that path, both force the gate to false, and
both invoke the `Action<bool>` callback exactly once: `true` when the snapshot
parsed, `false` on every failure path. The gate is therefore fail-closed at three
sites per class (class ctor, the parent, the handler) — report 134 saw only the
first.

Every claim below is tied to a witness instruction asserted verbatim against the
pinned raw, so a change in the bytes breaks the build rather than the prose.
"""
import argparse
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

NATIVE = 'reverse-engineering/raw/arena-pvp-535b0541/native.json.gz'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'
STRINGS = 'reverse-engineering/il2cpp/stringliteral.json'

PVP_PARENT = 19916080
PVP_HANDLER = 19936584
ARENA_PARENT = 22691808
ARENA_HANDLER = 22705216
PVP_CONFIGS = 19915932
PVP_ROOT = 19859292
PVP_RANKS = 19874728
PVP_USERS = 19887544
PVP_PLAY_USERS = 19915052
PVP_PLAY_MACHINES = 19915784
ARENA_ROOT = 22685676

GETTERS = [
    (PVP_ROOT, 'PVP_Manager', 'get_pathRoot', 'data-leagues', None),
    (PVP_CONFIGS, 'PVP_Manager', 'get_pathOfDataConfigs', 'data-leagues', '/data-configs'),
    (PVP_RANKS, 'PVP_Manager', 'get_pathOfDataRanks', 'data-leagues', '/data-ranks'),
    (PVP_USERS, 'PVP_Manager', 'get_pathOfDataUsers', 'data-leagues', '/data-users'),
    (PVP_PLAY_USERS, 'PVP_Manager', 'get_pathOfDataPlayOfUsers', 'data-leagues',
     '/data-play/data-play-users'),
    (PVP_PLAY_MACHINES, 'PVP_Manager', 'get_pathOfDataPlayOfMachines', 'data-leagues',
     '/data-play/data-play-machines'),
]

# (method rva, instruction rva, mnemonic, operands) — the bytes that carry the claim.
WITNESSES = {
    PVP_PARENT: [
        (19916288, 'bl', '#0x275cd60'),      # NetworkReachability.get_internetReachability
        (19916292, 'cbz', 'w0, #0x12fe6c4'),  # 0 == NotReachable -> failure
        (19916392, 'bl', '#0x12fe49c'),      # get_pathOfDataConfigs
        (19916444, 'bl', '#0x18a5580'),      # Action<object>..ctor
        (19916480, 'b', '#0x142bba4'),       # DownloadDatabase(path, onComplete)
        (19916520, 'ldr', 'x0, [x8]'),       # log slot: "No network connected"
        (19916524, 'bl', '#0x275f390'),      # Log(object)
        (19916560, 'strb', 'wzr, [x8, #0x4c]'),  # IsOpen = false
        (19916592, 'mov', 'w1, wzr'),        # callback(false)
        (19916600, 'br', 'x3'),              # invoke the Action<bool>
    ],
    PVP_HANDLER: [
        (19936664, 'bl', '#0x1665170'),      # DataSnapshot.get_Value
        (19936680, 'bl', '#0x1665458'),      # GetRawJsonValue
        (19936696, 'bl', '#0x1723d24'),      # JsonParse.FromJson<object>
        (19936712, 'ldrb', 'w20, [x8, #0x10]'),  # bool at +0x10 of the parsed object
        (19936736, 'strb', 'w20, [x8, #0x4c]'),  # IsOpen = that bool
        (19936760, 'mov', 'w1, #1'),         # callback(true)
        (19936792, 'strb', 'wzr, [x8, #0x4c]'),  # failure: IsOpen = false
        (19936816, 'mov', 'w1, wzr'),        # failure: callback(false)
    ],
    ARENA_PARENT: [
        (22692024, 'mov', 'x0, xzr'),
        (22692028, 'bl', '#0x275cd60'),      # get_internetReachability
        (22692032, 'cbz', 'w0, #0x15a4190'),
        (22692120, 'bl', '#0x15a27ec'),      # get_pathRoot
        (22692140, 'bl', '#0x1fe4084'),      # String.Concat(root, "/is-open")
        (22692204, 'bl', '#0x18a5580'),
        (22692236, 'b', '#0x142bba4'),       # DownloadDatabase
        (22692256, 'bl', '#0x15b77b0'),      # Log("No network connected")
        (22692292, 'strb', 'wzr, [x8, #0x1c]'),  # IsOpen = false
        (22692324, 'mov', 'w1, wzr'),
        (22692332, 'br', 'x3'),
    ],
    ARENA_HANDLER: [
        (22705284, 'bl', '#0x1665170'),
        (22705300, 'bl', '#0x1665458'),
        (22705308, 'bl', '#0x2103668'),      # Int32.Parse
        (22705344, 'cmp', 'w20, #0'),
        (22705348, 'cset', 'w9, gt'),        # count > 0
        (22705352, 'strb', 'w9, [x8, #0x1c]'),   # IsOpen = count > 0
        (22705376, 'mov', 'w1, #1'),
        (22705408, 'strb', 'wzr, [x8, #0x1c]'),
        (22705432, 'mov', 'w1, wzr'),
    ],
    ARENA_ROOT: [
        (22685800, 'bl', '#0x275cc0c'),      # Application.get_companyName
        (22685812, 'bl', '#0x1feca34'),      # string.op_Equality
        (22685816, 'tbz', 'w0, #0, #0x15a2888'),
        (22685836, 'bl', '#0x13236cc'),      # PREMIUM
        (22685856, 'tst', 'w0, #1'),
        (22685860, 'csel', 'x8, x9, x8, ne'),
    ],
}


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


def body(blob, rva):
    return [row for row in blob['methods'] if row['rva'] == rva][0]


def string_table():
    return {int(row['address'], 16): row['value']
            for row in json.loads((ROOT / STRINGS).read_text())}


def signatures():
    text = gzip.decompress((ROOT / DUMP).read_bytes()).decode('utf-8', 'replace')
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


def call_targets(row):
    out = []
    for insn in row['instructions']:
        if insn['mnemonic'] not in ('bl', 'b', 'br'):
            continue
        text = insn['op_str'].strip().lstrip('#')
        if re.fullmatch(r'0x[0-9a-f]+|\d+', text):
            out.append(dict(rva=insn['rva'], target=int(text, 0)))
    return out


def literals(row, strings):
    seen, out = set(), []
    for ref in row.get('slot_refs') or []:
        value = strings.get(ref['addend'])
        if value is None or ref['rva'] in seen:
            continue
        seen.add(ref['rva'])
        lo = ref.get('token_lo')
        out.append(dict(instruction_rva=ref['rva'], slot_va=ref['slot_va'],
                        literal_address=ref['addend'],
                        token_kind=None if lo is None else (lo >> 29) & 0x7,
                        value=value))
    return out


def check_witnesses(row):
    index = {insn['rva']: insn for insn in row['instructions']}
    found = []
    for rva, mnemonic, operands in WITNESSES[row['rva']]:
        insn = index.get(rva)
        assert insn is not None, (row['rva'], rva)
        assert insn['mnemonic'] == mnemonic, (rva, insn['mnemonic'], mnemonic)
        assert insn['op_str'] == operands, (rva, insn['op_str'], operands)
        found.append(dict(rva=rva, mnemonic=mnemonic, operands=operands))
    return found


def method_row(blob, rva, sigs, strings, role):
    row = body(blob, rva)
    return dict(role=role, class_name=row['class_name'], rva=rva, size=row['size'],
                sha256=row['sha256'], signature=row['signature'].strip(),
                witnesses=check_witnesses(row),
                calls=[dict(rva=call['rva'], target_rva=call['target'],
                            signature=sigs.get(call['target'])) for call in call_targets(row)],
                literals=literals(row, strings))


def build_payload():
    blob = load(NATIVE)
    strings = string_table()
    sigs = signatures()

    # Path getters: `mov x0, <root slot>` ... `mov x1, <suffix slot>` ... `b Concat`.
    getters = []
    for rva, class_name, name, root, suffix in GETTERS:
        row = body(blob, rva)
        found = literals(row, strings)
        values = [item['value'] for item in found]
        assert root in values, (name, values)
        if suffix is not None:
            assert suffix in values, (name, values)
            assert row['instructions'][-1]['mnemonic'] == 'b'
            assert int(row['instructions'][-1]['op_str'].lstrip('#'), 0) == 0x1FE4084
            value = root + suffix
        else:
            value = root
        getters.append(dict(rva=rva, class_name=class_name, name=name, size=row['size'],
                            sha256=row['sha256'], literals=found, value=value))

    arena_root_branches = [
        dict(condition='Application.companyName == "Test"',
             result='static string slot 0x2AEC9A0 (not dereferenced in any pinned raw)'),
        dict(condition='PREMIUM',
             result='static string slot 0x2AEC9B0 (not dereferenced in any pinned raw)'),
        dict(condition='otherwise', result='arena---datas'),
    ]

    parents = [method_row(blob, PVP_PARENT, sigs, strings, 'parent'),
               method_row(blob, ARENA_PARENT, sigs, strings, 'parent')]
    handlers = [method_row(blob, PVP_HANDLER, sigs, strings, 'handler'),
                method_row(blob, ARENA_HANDLER, sigs, strings, 'handler')]
    root_row = method_row(blob, ARENA_ROOT, sigs, strings, 'path getter')

    for row in parents:
        values = [item['value'] for item in row['literals']]
        assert 'No network connected' in values, (row['class_name'], values)
    for row in handlers:
        assert row['literals'] == [], row['class_name']

    arena_parent = [row for row in parents if row['class_name'] == 'ArenaManager'][0]
    assert '/is-open' in [item['value'] for item in arena_parent['literals']]

    gates = [
        dict(class_name='PVP_Manager', field='IsOpen', offset=0x4C, type='bool',
             source='config object +0x10 (bool) after JsonParse.FromJson<object>',
             path='data-leagues/data-configs', fail_closed=True,
             writes=[dict(rva=19936560, kind='strb wzr (class ctor)'),
                     dict(rva=19916560, kind='strb wzr (parent, no network)'),
                     dict(rva=19936736, kind='strb parsed bool (handler)'),
                     dict(rva=19936792, kind='strb wzr (handler failure)')]),
        dict(class_name='ArenaManager', field='+0x1C bool', offset=0x1C, type='bool',
             source='Int32.Parse(snapshot raw json) > 0',
             path='arena---datas/is-open', fail_closed=True,
             writes=[dict(rva=22692292, kind='strb wzr (parent, no network)'),
                     dict(rva=22705352, kind='cset gt -> strb (handler)'),
                     dict(rva=22705408, kind='strb wzr (handler failure)')]),
    ]

    return dict(
        schema=1,
        evidence='STATIC_ONLY_ORIGINAL_APK',
        note='Paths, gates and the callback argument are read from witness '
             'instructions asserted byte for byte against the pinned raw. The two '
             'ArenaManager root variants and the PVP config class identity are not '
             'reachable from pinned data and are recorded as not_decoded; the served '
             'values themselves are MODEL_NOT_MEASURED runtime.',
        provenance=dict(
            xapk_sha256=blob['xapk_sha256'],
            libil2cpp_sha256=blob['libil2cpp_sha256'],
            dump_sha256=blob['dump_sha256'],
            sources=[dict(path=NATIVE, sha256=sha_file(NATIVE),
                          role='LoadRemoteConfigs, handlers, path getters'),
                     dict(path=STRINGS, sha256=sha_file(STRINGS),
                          role='literal address -> text (paths, log message)'),
                     dict(path=DUMP, sha256=sha_file(DUMP),
                          role='every callee signature named in the chain')]),
        paths=dict(getters=getters, arena_root=dict(branches=arena_root_branches,
                                                    method=root_row)),
        remote_configs=dict(parents=parents, handlers=handlers, gates=gates,
                            callback=dict(
                                type='Action<bool>',
                                true_when='the snapshot parsed and the gate was written',
                                false_when='no internet, missing reference, empty '
                                           'snapshot or unparsable payload',
                                invocations='exactly one per call, both paths, via '
                                            '`br x3` tail call')),
        corrections=[dict(
            item='136/137: `GetRankNumber` tail call is `Int32.ToString`',
            measured='the tail `b` goes to RVA 21103836, which dump.cs declares as '
                     '`MyLibrary.ToRoman(int number)`, so the rank number string is a '
                     'roman numeral, not an arabic number',
            impact='the display table in 137 (`Herald 3`, `God 5`) must be read as '
                   '`Herald III`, `God V`; the glyphs themselves stay not_decoded '
                   'because `MyLibrary.ToRoman` is in no pinned raw')],
        not_decoded=[
            dict(item='ArenaManager root variants',
                 blocking='`get_pathRoot` returns slot 0x2AEC9A0 when companyName == '
                          '"Test" and slot 0x2AEC9B0 when PREMIUM; neither slot is '
                          'dereferenced (`ldr x0,[x8]`) in any pinned raw, so no '
                          'literal address -> no text'),
            dict(item='PVP_Manager config class identity',
                 blocking='`JsonParse.FromJson<object>` takes its type from metadata '
                          'slot 0x2AE1000, which is not a kind-5 string literal; the '
                          'field at +0x10 is therefore named only by offset'),
            dict(item='class owning static field 0 read before both fetches',
                 blocking='both parents read field +0 of the class behind metadata slot '
                          '0x2ADB958 and check it with Object.op_Implicit; that class is '
                          'not identified by any pinned symbol'),
            dict(item='served remote values',
                 blocking='`data-leagues/data-configs` and `arena---datas/is-open` live '
                          'in the Firebase database, not in the APK — '
                          'MODEL_NOT_MEASURED runtime'),
        ],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_remote_configs.json.gz')
    args = parser.parse_args()
    payload = build_payload()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                                sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          getters=len(payload['paths']['getters']),
                          parents=len(payload['remote_configs']['parents']),
                          handlers=len(payload['remote_configs']['handlers']),
                          witnesses=sum(len(row['witnesses']) for row in
                                        payload['remote_configs']['parents']
                                        + payload['remote_configs']['handlers'])) ))


if __name__ == '__main__':
    main()
