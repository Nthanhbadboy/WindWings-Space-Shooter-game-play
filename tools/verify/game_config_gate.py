#!/usr/bin/env python3
"""Who is behind slot `0x2ADBB88`? `GameConfig` — and what the arena gate means.

Report 140 left one blocker: the `+4` flag that `Board_Arena` tests before calling
`GetGameConfig` belonged to a class no pinned symbol named. The slot behind that
test is `0x2ADBB88` (44940168), and the class is `GameConfig` (TypeDefIndex 34).
Two independent proofs:

* **Layout.** `dump.cs` declares `GameConfig` as `int versionCode @0`, `bool
  isEmpty @4`, `bool backupAvailable @5`, `bool restoreAvailable @6`, `int
  lastestVersionCode @8`, two strings, `bool hasGiftCode @0x20`, `int GemCode
  @0x24`. Among every class in `dump.cs` that declares static fields, exactly one
  has an `int` at 0, a `bool` at 4 and an `int` at 8 — `GameConfig`.
* **Use.** All five pinned readers of that slot touch only offsets 0, 4 and 8, and
  the version sites pair `+8` with `+0` in a `cmp`.

Measured gate, identical in both boards:

    if (GameConfig.isEmpty)                       -> stop loading, show notice
    else if (GameConfig.lastestVersionCode > GameConfig.versionCode)
                                                  -> require / remind update
    else                                          -> GetGameConfig(callback)

So the arena gate is not a local flag: it depends on the game config having been
downloaded, and it re-checks the version pair on the same path. The write side is
`ConfigStruct.SetupDatas` / `ReplaceDatas` plus `GameConfig..cctor`; none of those
three bodies is in a pinned raw, so the values stay `not_decoded` with exact RVAs.

The report also fixes a constant from 140: the slot is `0x2ADBB88`, not
`0x2ADB8E0` (44939488, a different slot used by the same boards).
"""
import argparse
import gzip
import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

NATIVE = 'reverse-engineering/raw/arena-pvp-535b0541/native.json.gz'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'
STRINGS = 'reverse-engineering/il2cpp/stringliteral.json'

SLOT = 0x2ADBB88          # 44940168 — the game-config slot
STALE_SLOT = 0x2ADB8E0    # 44939488 — what 140 recorded
STATICS_OFFSET = 0xB8

FIELD_LINE = re.compile(r'public static ([\w\[\]<>]+) (\w+); // 0x([0-9A-Fa-f]+)')
CLASS_LINE = re.compile(r'\s*(?:public|private|internal)?\s*(?:static\s+)?'
                        r'(?:sealed\s+)?(?:abstract\s+)?class ([\w\.<>`]+)')

OPEN_FLOWS = {
    'Board_Arena.<IECheckArenaOpen>d__55': 22810128,
    'Board_Arena.<>c__DisplayClass55_0': 22806816,
    'Board_PVP.<IECheckPvPOpen>d__74': 19817328,
    'Board_PVP.<>c__DisplayClass74_0': 19803208,
    'ArenaHub.<>c__DisplayClass20_0': 22680000,
}

VERSION_SITES = {22680092, 22807152, 19803544, 22811048, 19818236}

WRITERS = [
    dict(class_name='GameConfig', name='.cctor', rva=19082168),
    dict(class_name='ConfigStruct', name='SetupDatas', rva=19042256),
    dict(class_name='ConfigStruct', name='ReplaceDatas', rva=19049040),
]


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@lru_cache(maxsize=None)
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


def classes_with_statics(text):
    """Every class in dump.cs that declares at least one static field."""
    out, lines = [], text.split('\n')
    for index, line in enumerate(lines):
        if 'TypeDefIndex' not in line:
            continue
        found = CLASS_LINE.match(line)
        if not found:
            continue
        fields = []
        for follow in lines[index + 1:]:
            if '// Methods' in follow or '// Properties' in follow:
                break
            hit = FIELD_LINE.search(follow)
            if hit:
                fields.append(dict(type=hit.group(1), name=hit.group(2),
                                   offset=int(hit.group(3), 16)))
        if fields:
            out.append(dict(name=found.group(1), fields=fields, line=index))
    return out


def norm(reg):
    return 'x' + reg[1:]


def slot_access(blob, slot):
    """Reads/writes of the statics behind one metadata slot, with witnesses.

    One role per register, and every write replaces it: page (adrp), slot
    (page + offset), klass (deref of a slot) or statics (klass + 0xB8). Without
    that exclusivity `ldr w8,[x8]` over a statics base looks like a klass deref and
    the `versionCode` read vanishes. The scan is linear and conservative: a role
    clobbered on one branch path is dropped, so a site can be missed here — the
    `version_sites()` pass below is deliberately register-free and catches those.
    """
    out = []
    for method in blob['methods']:
        roles, rows = {}, []
        for insn in method['instructions']:
            op, mnemonic = insn['op_str'], insn['mnemonic']
            adrp = re.fullmatch(r'(x\d+), #(0x[0-9a-f]+)', op)
            if mnemonic == 'adrp' and adrp:
                roles[norm(adrp.group(1))] = ('page', int(adrp.group(2), 0))
                continue
            if ', [' not in op or mnemonic not in ('ldr', 'str', 'strb', 'ldrb'):
                continue
            dest, rest = op.split(', ', 1)
            hit = re.fullmatch(r'\[(x\d+)(?:, #(0x[0-9a-f]+|-?\d+))?\]', rest)
            if not hit:
                roles.pop(norm(dest), None)
                continue
            base = norm(hit.group(1))
            offset = int(hit.group(2), 0) if hit.group(2) else 0
            target = norm(dest)
            role = roles.get(base)
            if mnemonic == 'ldr' and role and role[0] == 'slot' and offset == 0:
                roles[target] = ('klass', role[1])
                continue
            if mnemonic == 'ldr' and role and role[0] == 'page':
                roles[target] = ('slot', role[1] + offset)
                continue
            if mnemonic == 'ldr' and role and role[0] == 'klass' \
                    and offset == STATICS_OFFSET:
                roles[target] = ('statics', role[1])
                continue
            if role and role[0] == 'statics' and role[1] == slot:
                rows.append(dict(rva=insn['rva'],
                                 kind='read' if 'ldr' in mnemonic else 'write',
                                 mnemonic=mnemonic, offset=offset, operands=op))
                continue
            roles.pop(target, None)
        if rows:
            out.append(dict(class_name=method['class_name'],
                            name=method['signature'].strip().split('(')[0].split()[-1],
                            signature=method['signature'].strip(),
                            rva=method['rva'], size=method['size'], accesses=rows))
    return out


def version_sites(blob, slot):
    """`ldr w9,[base,#8]` + `ldr w8,[base]` + `cmp` inside a slot-using method.

    Register-free on purpose: it only asks that the same base register is used at
    offset 8 and offset 0, that a `cmp` immediately follows, and that a `klass+0xB8`
    statics load into that base appears shortly before. That survives the linear
    scan losing the role across branches.
    """
    out = []
    for method in blob['methods']:
        if not any(ref.get('slot_va') == slot for ref in method.get('slot_refs', [])):
            continue
        code = method['instructions']
        for index, insn in enumerate(code):
            eight = re.fullmatch(r'w\d+, \[(x\d+), #8\]', insn['op_str'])
            if insn['mnemonic'] != 'ldr' or not eight:
                continue
            base = eight.group(1)
            if index + 2 >= len(code):
                continue
            zero, compare = code[index + 1], code[index + 2]
            if not re.fullmatch(r'w\d+, \[' + base + r'\]', zero['op_str']):
                continue
            if compare['mnemonic'] != 'cmp' or zero['mnemonic'] != 'ldr':
                continue
            statics_load = re.compile(r'%s, \[x\d+, #0xb8\]' % base)
            lookback = [item for item in code[max(0, index - 20):index]
                        if item['mnemonic'] == 'ldr'
                        and statics_load.fullmatch(item['op_str'])]
            if not lookback:
                continue
            branch = code[index + 3] if index + 3 < len(code) else None
            target = None
            if branch and re.fullmatch(r'#0x[0-9a-f]+', branch['op_str'].strip()):
                target = int(branch['op_str'].strip().lstrip('#'), 0)
            out.append(dict(method=method['class_name'], method_rva=method['rva'],
                            latest_read_rva=insn['rva'],
                            version_read_rva=zero['rva'],
                            cmp_rva=compare['rva'],
                            operands=compare['op_str'],
                            branch=branch['mnemonic'] if branch else None,
                            branch_operands=branch['op_str'] if branch else None,
                            branch_target=target,
                            branch_target_calls=side_calls(method, target) if target else [],
                            fall_through_calls=side_calls(
                                method, code[index + 4]['rva']
                                if index + 4 < len(code) else insn['rva'] + 4),
                            semantics='branch taken when lastestVersionCode <= '
                                      'versionCode, i.e. update needed only when '
                                      'lastestVersionCode > versionCode'))
    return out


def side_calls(method, start_rva, limit=3, window=24):
    """The first `bl` targets on one side of a branch, nearest first."""
    code = [insn for insn in method['instructions'] if insn['rva'] >= start_rva]
    out = []
    for insn in code[:window]:
        if insn['mnemonic'] != 'bl':
            continue
        target = int(insn['op_str'].strip().lstrip('#'), 0)
        out.append(target)
        if len(out) >= limit:
            break
    return out


def find_class(classes, observed):
    """Every class whose static layout explains all observed offsets/types."""
    matches = []
    for entry in classes:
        by_offset = {field['offset']: field for field in entry['fields']}
        if all((by_offset.get(offset) or {}).get('type') == want
               for offset, want in observed.items()):
            matches.append(entry)
    return matches


def pinned_rvas():
    seen = set()
    for path in sorted(ROOT.glob('reverse-engineering/raw/*/native.json.gz')):
        for method in json.loads(gzip.decompress(path.read_bytes()))['methods']:
            seen.add(method['rva'])
    return seen


def gate_follow_ups(blob, sigs, rows):
    """For each `isEmpty` read: the branch, both sides, and the first calls."""
    out = []
    for row in rows:
        method = [item for item in blob['methods'] if item['rva'] == row['rva']][0]
        for item in [entry for entry in row['accesses'] if entry['offset'] == 0x4]:
            after = [insn for insn in method['instructions'] if insn['rva'] > item['rva']]
            branch = next((insn for insn in after[:3]
                           if insn['mnemonic'].startswith('cb')), None)
            target = None
            if branch and re.fullmatch(r'w\d+, #0x[0-9a-f]+', branch['op_str'].strip()):
                target = int(branch['op_str'].split('#')[1], 16)
            fall_through = side_calls(method, after[0]['rva'] if after else item['rva'] + 4)
            out.append(dict(
                method=row['class_name'], read_rva=item['rva'],
                branch=branch['mnemonic'] if branch else None,
                branch_operands=branch['op_str'] if branch else None,
                branch_target=target,
                branch_side_calls=side_calls(method, target) if target else [],
                fall_through_calls=[dict(rva=rva,
                                         signature=sigs.get(rva, 'UNNAMED_EXTERNAL'))
                                    for rva in fall_through],
                taken_when='isEmpty is false' if branch and branch['mnemonic'] == 'cbz'
                           else 'isEmpty is true'))
    return out


def build_payload():
    blob = load(NATIVE)
    text = dump_text()
    sigs = signatures(text)

    rows = slot_access(blob, SLOT)
    assert rows, 'no access through slot 0x2ADBB88'
    assert set(row['class_name'] for row in rows) == set(OPEN_FLOWS), sorted(
        row['class_name'] for row in rows)
    for row in rows:
        assert FLOWS_RVA_OK(row), row['rva']
        assert row['accesses'], row['class_name']
        assert {item['offset'] for item in row['accesses']} <= {0x0, 0x4, 0x8}
        assert not [item for item in row['accesses'] if item['kind'] == 'write']

    offsets = {item['offset'] for row in rows for item in row['accesses']}
    assert offsets == {0x0, 0x4, 0x8}, offsets

    observed = {0x0: 'int', 0x4: 'bool', 0x8: 'int'}
    classes = classes_with_statics(text)
    matches = find_class(classes, observed)
    assert len(matches) == 1, [entry['name'] for entry in matches]
    winner = matches[0]
    assert winner['name'] == 'GameConfig', winner['name']

    sites = version_sites(blob, SLOT)
    assert {site['latest_read_rva'] for site in sites} == VERSION_SITES, sorted(
        site['latest_read_rva'] for site in sites)
    assert all(site['branch'] == 'b.le' for site in sites
               if site['method_rva'] != 22680000)

    empties = [row for row in rows if any(item['offset'] == 0x4
                                         for item in row['accesses'])]
    assert len(empties) == 4, [row['class_name'] for row in empties]
    assert 'ArenaHub.<>c__DisplayClass20_0' not in [row['class_name']
                                                    for row in empties]

    # The raw itself records the slot behind the klass load.
    opener = [item for item in blob['methods'] if item['rva'] == 22810128][0]
    witness = [ref['rva'] for ref in opener.get('slot_refs', [])
               if ref.get('slot_va') == SLOT]
    stale = [ref['rva'] for ref in opener.get('slot_refs', [])
             if ref.get('slot_va') == STALE_SLOT]
    assert witness == [22810712, 22810728, 22811040], witness
    assert not stale, stale

    pinned = pinned_rvas()
    writers = [dict(entry, pinned=entry['rva'] in pinned) for entry in WRITERS]
    assert not any(entry['pinned'] for entry in writers), writers

    follows = gate_follow_ups(blob, sigs, rows)
    assert len(follows) == 4, follows
    assert all(item['branch'] == 'cbz' for item in follows), follows
    assert all(item['taken_when'] == 'isEmpty is false' for item in follows), follows
    # The version check is what `!isEmpty` leads to: in both open checks the
    # branch target lands just above the version-compare site of the same method.
    targets = {item['method']: item['branch_target'] for item in follows}
    sites_by_method = {site['method']: site['cmp_rva'] for site in sites}
    for meth in ('Board_Arena.<IECheckArenaOpen>d__55',
                 'Board_PVP.<IECheckPvPOpen>d__74'):
        assert meth in targets and meth in sites_by_method, meth
        gap = sites_by_method[meth] - targets[meth]
        assert 0 < gap < 0x400, (meth, gap)

    # Name the two outcomes so the shape is not just offsets: the `!isEmpty` side
    # runs the user check, the update side calls the unnamed notice helper.
    fall_through = {item['method']: [call['rva'] for call in item['fall_through_calls']]
                    for item in follows}
    continue_calls = {site['method']: site['branch_target_calls'] for site in sites}
    update_calls = {site['method']: site['fall_through_calls'] for site in sites}
    for meth in ('Board_Arena.<IECheckArenaOpen>d__55',
                 'Board_PVP.<IECheckPvPOpen>d__74'):
        names = [sigs.get(rva, '') for rva in fall_through[meth]]
        assert any('GetGameConfig' in name for name in names), (meth, names)
    assert 22782848 in continue_calls['Board_Arena.<IECheckArenaOpen>d__55']
    assert 19789004 in continue_calls['Board_PVP.<IECheckPvPOpen>d__74']
    assert 34325296 in update_calls['Board_Arena.<IECheckArenaOpen>d__55']
    assert 34325296 in update_calls['Board_PVP.<IECheckPvPOpen>d__74']

    return dict(
        schema=1,
        evidence='STATIC_ONLY_ORIGINAL_APK',
        note='`GameConfig` is pinned by static layout and by the fields its five '
             'pinned readers touch. Its values are written from the served config at '
             'runtime and no writer body is pinned, so the values stay not_decoded; '
             'the gate logic below is measured.',
        provenance=dict(
            xapk_sha256=blob['xapk_sha256'],
            libil2cpp_sha256=blob['libil2cpp_sha256'],
            dump_sha256=blob['dump_sha256'],
            sources=[dict(path=NATIVE, sha256=sha_file(NATIVE),
                          role='pinned readers of the GameConfig statics'),
                     dict(path=DUMP, sha256=sha_file(DUMP),
                          role='static layouts (class identity) and callee signatures'),
                     dict(path=STRINGS, sha256=sha_file(STRINGS),
                          role='consulted; carries no GameConfig data')]),
        slot=dict(va=SLOT, decimal=SLOT,
                  note='0x2ADBB88 = page 0x2ADB000 + 0xB88, the operand of '
                       '`ldr x21,[x21,#0xb88]` in the two open checks'),
        identity=dict(
            class_name=winner['name'], fields=winner['fields'],
            observed=observed,
            candidates_with_statics=len(classes), matches=len(matches),
            proof='the only class in dump.cs with an int at 0, a bool at 4 and an '
                  'int at 8 among its statics'),
        readers=dict(count=len(rows), flows=rows, isEmpty_readers=len(empties)),
        version=dict(
            sites=[dict(site,
                        branch_target_calls=[dict(rva=rva,
                                                  signature=sigs.get(rva,
                                                                     'UNNAMED_EXTERNAL'))
                                              for rva in site['branch_target_calls']],
                        fall_through_calls=[dict(rva=rva,
                                                 signature=sigs.get(rva,
                                                                    'UNNAMED_EXTERNAL'))
                                            for rva in site['fall_through_calls']],
                        update_path='fall-through (nearest call: %s)' % (
                            sigs.get(site['fall_through_calls'][1]
                                     if len(site['fall_through_calls']) > 1
                                     else 0, 'UNNAMED_EXTERNAL')))
                   for site in sites],
            method_count=len({site['method'] for site in sites}),
            rule='update_required = lastestVersionCode > versionCode',
            note='`b.le` skips the update path when the client is not behind; the '
                 'ArenaHub witness returns the same comparison as a bool via `cset '
                 'w1, le`'),
        gate=dict(
            shape='if (GameConfig.isEmpty) stop; else if (lastestVersionCode > '
                  'versionCode) require update; else GetGameConfig(callback)',
            empty_checks=[dict(item,
                               branch_side_calls=[dict(rva=rva,
                                                       signature=sigs.get(
                                                           rva, 'UNNAMED_EXTERNAL'))
                                                   for rva in item['branch_side_calls']])
                          for item in follows],
            empty_flag='isEmpty', empty_offset=0x4,
            note='four of five readers test `isEmpty` first; the fifth '
                 '(ArenaHub.<CheckLastestGameVersion>b__0) is version-only'),
        writers=dict(entries=writers, pinned=0,
                     note='`ConfigStruct.SetupDatas` / `ReplaceDatas` push the parsed '
                          'config into `GameConfig`; neither is pinned'),
        corrections=[dict(
            item='140: the gate flag lives behind slot 0x2ADB8E0 (44939488)',
            measured=dict(slot_va=SLOT, decimal=SLOT,
                          slot_ref_rvas=witness,
                          operand='ldr x21,[x21,#0xb88] at RVA 22810708'),
            why='140 reused the slot constant 0x2ADB8E0 from 138 instead of reading '
                'the operand of the instruction it had pinned; a scan of 0x2ADB8E0 '
                'returns nothing in all 8 raws',
            impact='the class is `GameConfig`, the `+4` field is `isEmpty`, and the '
                   'arena gate therefore depends on the game config download, not on '
                   'a local open flag')],
        confirmations=[dict(
            item='140 not_decoded: "class behind slot 0x2ADB8E0 is not named"',
            result='resolved — `GameConfig` (TypeDefIndex 34), matched by layout and '
                   'by five readers')],
        not_decoded=[
            dict(item='GameConfig values (versionCode, lastestVersionCode, isEmpty, '
                      'update strings, gift code)',
                 blocking='`GameConfig..cctor` RVA 19082168, `ConfigStruct.'
                          'SetupDatas` RVA 19042256 and `ConfigStruct.ReplaceDatas` '
                          'RVA 19049040 are in none of the 8 pinned raws; the values '
                          'arrive from the served JSON at runtime — MODEL_NOT_MEASURED '
                          'runtime'),
            dict(item='slot 0x2ADB8E0 (44939488) class',
                 blocking='a neighbouring slot referenced at RVA 22810480 / 22810756 '
                          'in the arena open check; naming it needs its own pass — '
                          'no access through it was decoded here')],
    )


def FLOWS_RVA_OK(row):
    return OPEN_FLOWS.get(row['class_name']) == row['rva']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_game_config_gate.json.gz')
    args = parser.parse_args()
    payload = build_payload()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                               sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          readers=payload['readers']['count'],
                          version_sites=payload['version']['method_count'],
                          fields=len(payload['identity']['fields']))))


if __name__ == '__main__':
    main()
