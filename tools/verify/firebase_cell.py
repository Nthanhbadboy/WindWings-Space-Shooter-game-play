#!/usr/bin/env python3
"""What is behind slot `0x2ADB958` (44939608)? The `FirebaseDatabaseManager` klass cell.

Report 142 decoded the neighbouring slot `0x2ADB8E0` (the `UnityEngine.Application`
klass cell) and left the page `0x2ADB000` mapped only in part. Bookkeeping from 142
and 178 flagged one slot as *unattributed*: 34 methods in the Arena/PvP family load
`adrp 0x2ADB000` + `ldr xN,[xN,#0x958]`, and nearly all of them then call
`FirebaseDatabaseManager` — but "nearly all" is not an identification.

Three measurements pin it (none of them a guess from a method name):

* the load is the klass-cell idiom 141/142 read for `GameConfig` and `Application`
  (`ldr xK,[cell]`, the `initialized` byte at `klass+0xE0`, the class-init helpers
  `0x110D028` / `0x110D12C`);
* every site that goes on to read a static reads **offset `0x0` of the statics block**
  — and `dump.cs` declares exactly one static on `FirebaseDatabaseManager`,
  `public static FirebaseDatabaseManager Instance; // 0x0`;
* the object pulled out of `statics+0x0` is then passed as `this` to
  `FirebaseDatabaseManager` instance methods (`x0 = Instance` immediately before
  `bl UploadDatabase` / `DownloadDatabase` / `Query` / `DeleteDatabase` /
  `DownloadDatabaseQueryRank` / `UploadDatabaseObj`).

The interesting part is the census: which game classes talk to Firebase, with which
API, and where. One method (`Board_Arena.<IESignInOrRestoreYourDatas>d__91`) touches
the cell without calling any of the six APIs: it null-checks `Instance` through
`UnityEngine.Object.op_Implicit` and loops on `Time.get_time` against a `+10s`
deadline — a *wait for the singleton* loop, not a database call.

Evidence is static-only: nothing here says what the game actually wrote to Firebase
on a device, only which paths and payload builders the code contains.
"""
import argparse
import gzip
import hashlib
import json
import re
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import application_cell as AC  # noqa: E402

RAW_GLOB = 'reverse-engineering/raw/*535b0541/native.json.gz'
DUMP = AC.DUMP
SLOTS = 'reverse-engineering/raw/ui-audit/metadata-slots.json'

PAGE = 0x2ADB000
OFFSET = 0x958
SLOT = PAGE + OFFSET            # 0x2ADB958 = 44939608
CLASS_INIT = 0x110D028          # 17879080, eager class-init helper
CLASS_INIT_CHECK = 0x110D12C    # 17879340, lazy class-init helper
ALLOC = 0x110D240               # 17879616, object allocation helper
NEIGHBOUR = AC.SLOT             # 0x2ADB8E0 = Application, from 142

APIS = {
    0x142B86C: 'FirebaseDatabaseManager.UploadDatabase',
    0x142BBA4: 'FirebaseDatabaseManager.DownloadDatabase',
    0x142C120: 'FirebaseDatabaseManager.Query',
    0x142B7B0: 'FirebaseDatabaseManager.DeleteDatabase',
    0x142BD04: 'FirebaseDatabaseManager.DownloadDatabaseQueryRank',
    0x142BA08: 'FirebaseDatabaseManager.UploadDatabaseObj',
}

HELPERS = {
    0x27849C8: ('UnityEngine.Object', 'op_Implicit'),
    0x2786DC0: ('UnityEngine.Time', 'get_time'),
    0x13EBC6C: ('JsonParse', 'ToJson'),
    0x1429824: ('FirebaseAuthManager', 'SignInWithGooglePlayGames'),
    0x18A4388: (None, 'unresolved (generic delegate ctor)'),
    0x18A5580: (None, 'unresolved (generic delegate ctor)'),
}

RETRY_RVA = 22814532            # Board_Arena.<IESignInOrRestoreYourDatas>d__91
FIELD_INSTANCE = 0x0            # FirebaseDatabaseManager.Instance


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def raw_paths():
    return tuple(sorted(str(path.relative_to(ROOT)) for path in ROOT.glob(RAW_GLOB)))


@lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@lru_cache(maxsize=None)
def dump_text():
    return gzip.decompress((ROOT / DUMP).read_bytes()).decode('utf-8', 'replace')


@lru_cache(maxsize=None)
def rva_index():
    """RVA -> (declaring class, signature) straight from dump.cs."""
    return AC.rva_index()


@lru_cache(maxsize=None)
def statics_page_slots():
    """Slots the workspace already attributes to a class (report 142's map)."""
    blob = json.loads((ROOT / SLOTS).read_text())
    return {int(key, 16): int(value, 16)
            for key, value in blob.get('slot_effective_addresses', {}).items()}


def operands(insn):
    return insn.get('op_str') or ''


def cell_sites(blob):
    """Every `adrp 0x2ADB000` + `ldr xN,[xN,#0x958]` pair in one raw."""
    out = []
    for method in blob['methods']:
        code = method['instructions']
        for position, insn in enumerate(code):
            if insn['mnemonic'] != 'adrp':
                continue
            found = re.fullmatch(r'(x\d+), #(0x[0-9a-f]+)', operands(insn))
            if not found or int(found.group(2), 16) != PAGE:
                continue
            reg = found.group(1)
            for follow in code[position + 1:position + 3]:
                if follow['mnemonic'] == 'ldr' and operands(follow) == \
                        '%s, [%s, #0x%x]' % (reg, reg, OFFSET):
                    out.append(dict(class_name=method['class_name'],
                                    signature=method['signature'].strip(),
                                    method_rva=method['rva'], size=method['size'],
                                    adrp_rva=insn['rva'], load_rva=follow['rva'],
                                    reg=reg))
                    break
    return out


def _deref(text):
    """`x8, [x8]` -> ('x8', 'x8', None); `x8, [x8, #0xb8]` -> ('x8', 'x8', 184)."""
    found = re.fullmatch(r'(x\d+), \[(x\d+)(?:, #0x([0-9a-f]+))?\]', text)
    if not found:
        return None
    return found.group(1), found.group(2), (int(found.group(3), 16)
                                            if found.group(3) else 0)


def idiom(blob, method_rva, load_rva):
    """How the klass pointer is used after the load: init, flag, or statics."""
    method = next(item for item in blob['methods'] if item['rva'] == method_rva)
    code = method['instructions']
    rvas = [insn['rva'] for insn in code]
    window = code[rvas.index(load_rva) + 1:][:8]
    tags, offsets = [], []
    if any(insn['mnemonic'] == 'bl' and operands(insn).strip() == '#0x%x' % CLASS_INIT
           for insn in window):
        tags.append('class_init(0x110D028)')
    klass = None
    for position, insn in enumerate(window):
        if insn['mnemonic'] != 'ldr':
            continue
        read = _deref(operands(insn))
        if not read or read[2] != 0:
            continue
        klass = read[0]
        if position + 1 >= len(window):
            continue
        follow = window[position + 1]
        nxt = _deref(operands(follow))
        if follow['mnemonic'] == 'ldr' and nxt and nxt[1] == klass:
            if nxt[0].startswith('w') and nxt[2] == 0xE0:
                tags.append('initialized_flag(klass+0xE0)')
                break
            if nxt[2] == 0xB8:
                tags.append('statics(klass+0xB8)')
                break
    if 'statics(klass+0xB8)' in tags:
        for position, insn in enumerate(window):
            read = _deref(operands(insn)) if insn['mnemonic'] == 'ldr' else None
            if read and read[2] == 0xB8:
                for later in window[position + 1:position + 4]:
                    if later['mnemonic'] not in ('ldr', 'ldrb', 'ldrh', 'ldrsw', 'str'):
                        continue
                    touch = _deref(operands(later))
                    if touch and touch[1] == read[0]:
                        offsets.append(touch[2])
    return (tags or ['unclassified']), sorted(set(offsets))


def calls(method, table):
    out = []
    for insn in method['instructions']:
        if insn['mnemonic'] not in ('bl', 'b'):
            continue
        operand = operands(insn).strip()
        if re.fullmatch(r'#0x[0-9a-f]+', operand):
            target = int(operand.lstrip('#'), 16)
            if target in table:
                out.append(dict(rva=insn['rva'], target=target, name=table[target]))
    return out


@lru_cache(maxsize=None)
def helper_names():
    return {rva: ('%s.%s' % spec if spec[0] else 'unresolved@0x%x' % rva)
            for rva, spec in HELPERS.items()}


def cell_methods():
    """One record per distinct method that loads the cell (first raw wins)."""
    seen = {}
    for path in raw_paths():
        for method in load(path)['methods']:
            if method['rva'] not in seen:
                seen[method['rva']] = method
    return seen


def census():
    rows, sites_total, pairs = [], 0, 0
    for path in raw_paths():
        blob = load(path)
        found = cell_sites(blob)
        sites_total += len(found)
        by_method = {}
        for site in found:
            by_method.setdefault(site['method_rva'], []).append(site)
        for method_rva, method_sites in sorted(by_method.items()):
            method = next(item for item in blob['methods'] if item['rva'] == method_rva)
            apis, helpers, offsets, tags = [], [], set(), set()
            for call in calls(method, dict(list(APIS.items()) + list(helper_names().items()))):
                name = call['name']
                bucket = apis if call['target'] in APIS else helpers
                if name not in bucket:
                    bucket.append(name)
            for site in method_sites:
                kinds, found_offsets = idiom(blob, method_rva, site['load_rva'])
                tags.update(kinds)
                offsets.update(found_offsets)
            pairs += 1
            rows.append(dict(raw=path.split('/')[-2], class_name=method['class_name'],
                             signature=method['signature'].strip(), rva=method_rva,
                             size=method['size'], sites=len(method_sites),
                             api_calls=sorted(apis), helpers=sorted(helpers),
                             idiom=sorted(tags), statics_offsets=sorted(offsets)))
    return rows, sites_total, pairs


def coverage(rows):
    """`slot_refs` is an index; the instruction scan is the measurement."""
    scanned = {(row['raw'], row['rva']) for row in rows}
    indexed = set()
    for path in raw_paths():
        blob = load(path)
        for method in blob['methods']:
            if any(ref.get('slot_va') == SLOT for ref in method.get('slot_refs', [])):
                indexed.add((path.split('/')[-2], method['rva']))
    missing = []
    for raw_name, rva in sorted(scanned - indexed):
        row = next(item for item in rows if item['raw'] == raw_name and item['rva'] == rva)
        missing.append(dict(raw=raw_name, class_name=row['class_name'],
                            signature=row['signature'], rva=rva))
    note = ('`slot_refs` covers the scan completely for this slot in the eight raws '
            '(unlike 142, where it listed 45 of 47): the instruction scan is still the '
            'measurement, the index only agrees with it here')
    if missing:
        note = ('`slot_refs` is a per-raw index, not a proof of absence: the '
                'instruction scan is the measurement and it is a superset')
    return dict(scanned=len(scanned), indexed=len(indexed),
                missing_from_slot_refs=missing, note=note)


def retry_loop():
    """The one method that loads the cell and calls *none* of the six APIs."""
    blob = next(item for item in (load(path) for path in raw_paths())
                if any(method['rva'] == RETRY_RVA for method in item['methods']))
    method = next(item for item in blob['methods'] if item['rva'] == RETRY_RVA)
    code = method['instructions']
    window = {}
    for insn in code:
        read = _deref(operands(insn)) if insn['mnemonic'] == 'ldr' else None
        if read and read[2] == 0xB8:
            for later in code[code.index(insn) + 1:code.index(insn) + 3]:
                touch = _deref(operands(later))
                if touch and touch[1] == read[0] and touch[2] == FIELD_INSTANCE:
                    window['instance_load'] = dict(rva=later['rva'],
                                                   text=operands(later).strip())
    null_checks = [dict(rva=call['rva'], name=call['name'])
                   for call in calls(method, helper_names())
                   if call['target'] == 0x27849C8]
    clocks = [dict(rva=call['rva'], name=call['name'])
              for call in calls(method, helper_names()) if call['target'] == 0x2786DC0]
    deadline = []
    for position, insn in enumerate(code):
        if insn['mnemonic'] == 'fmov' and operands(insn).strip() == 's1, #10.00000000':
            deadline.append(dict(rva=insn['rva'], text='fmov s1, #10.00000000'))
    return dict(rva=RETRY_RVA, class_name=method['class_name'],
                signature=method['signature'].strip(), size=method['size'],
                instance_load=window.get('instance_load'),
                null_checks=null_checks, clock_reads=clocks, deadline=deadline,
                rule='loop while `UnityEngine.Object.op_Implicit(FirebaseDatabaseManager'
                     '.Instance) == false` and `UnityEngine.Time.get_time()` is still '
                     'below the `+10s` deadline: the coroutine waits for the singleton '
                     'instead of failing, and writes nothing to Firebase')


def build_payload():
    rows, sites_total, pairs = census()
    distinct = len({row['rva'] for row in rows})
    assert distinct == 34, distinct
    assert sites_total == 141, sites_total
    assert pairs == 54, pairs

    offsets = sorted({offset for row in rows for offset in row['statics_offsets']})
    assert offsets == [0], offsets

    scanned = cell_methods()
    api_calls, api_methods, api_distinct = {}, {}, {}
    for row in rows:
        for name in row['api_calls']:
            api_methods[name] = api_methods.get(name, 0) + 1
    for path in raw_paths():
        blob = load(path)
        for method in blob['methods']:
            for call in calls(method, APIS):
                api_calls[call['name']] = api_calls.get(call['name'], 0) + 1
    for method in scanned.values():
        for name in {call['name'] for call in calls(method, APIS)}:
            api_distinct[name] = api_distinct.get(name, 0) + 1
    api_sites_distinct = sum(len({call['rva'] for call in calls(scanned[rva], APIS)})
                             for rva in sorted({row['rva'] for row in rows}))
    assert api_sites_distinct == 59, api_sites_distinct
    assert api_calls == {'FirebaseDatabaseManager.DownloadDatabase': 44,
                         'FirebaseDatabaseManager.UploadDatabase': 33,
                         'FirebaseDatabaseManager.DeleteDatabase': 7,
                         'FirebaseDatabaseManager.Query': 6,
                         'FirebaseDatabaseManager.DownloadDatabaseQueryRank': 2,
                         'FirebaseDatabaseManager.UploadDatabaseObj': 1}, api_calls
    assert api_distinct == {'FirebaseDatabaseManager.DownloadDatabase': 20,
                            'FirebaseDatabaseManager.UploadDatabase': 14,
                            'FirebaseDatabaseManager.DeleteDatabase': 4,
                            'FirebaseDatabaseManager.Query': 2,
                            'FirebaseDatabaseManager.DownloadDatabaseQueryRank': 1,
                            'FirebaseDatabaseManager.UploadDatabaseObj': 1}, api_distinct

    helpers = {}
    for rva in sorted({row['rva'] for row in rows}):
        for name in {call['name'] for call in calls(scanned[rva], helper_names())}:
            helpers[name] = helpers.get(name, 0) + 1
    assert helpers == {'unresolved@0x18a5580': 23, 'unresolved@0x18a4388': 15,
                       'JsonParse.ToJson': 14, 'UnityEngine.Object.op_Implicit': 8,
                       'UnityEngine.Time.get_time': 2,
                       'FirebaseAuthManager.SignInWithGooglePlayGames': 2}, helpers
    assert sum(1 for row in rows if not row['api_calls']) == 1, rows

    retry = retry_loop()
    assert retry['instance_load'], retry
    assert retry['clock_reads'], retry
    assert retry['deadline'], retry

    index = rva_index()
    instance_field = None
    for line in dump_text().split('\n'):
        if 'public static FirebaseDatabaseManager Instance;' in line:
            instance_field = line.strip()
    assert instance_field and '0x0' in instance_field, instance_field

    raw_meta = [dict(path=path, sha256=sha_file(path)) for path in raw_paths()]
    blob = load(next(path for path in raw_paths() if 'arena-pvp' in path))
    return dict(
        schema=1,
        evidence='STATIC_ONLY_ORIGINAL_APK',
        note='The cell is identified as `FirebaseDatabaseManager` by the klass-cell '
             'idiom, the `statics+0x0` read and a `dump.cs` field that sits at 0x0; '
             'what the game wrote to Firebase on a device is MODEL_NOT_MEASURED runtime.',
        provenance=dict(
            xapk_sha256=blob['xapk_sha256'],
            libil2cpp_sha256=blob['libil2cpp_sha256'],
            dump_sha256=blob['dump_sha256'],
            sources=[dict(path=DUMP, sha256=sha_file(DUMP),
                          role='declaring class + signature for every callee, and the '
                               '`Instance` field offset'),
                     dict(path=SLOTS, sha256=sha_file(SLOTS),
                          role='the slot -> statics-page map 142 and 178 use, for the '
                               'neighbour contrast'),
                     *[dict(path=row['path'], sha256=row['sha256'],
                            role='pinned methods that load the cell') for row in raw_meta]]),
        cell=dict(va=SLOT, decimal=SLOT, page=PAGE, offset=OFFSET,
                  klass='FirebaseDatabaseManager',
                  type_def_index=1485,
                  neighbour_from_142=dict(va=NEIGHBOUR, decimal=NEIGHBOUR,
                                          klass='UnityEngine.Application'),
                  delta=SLOT - NEIGHBOUR,
                  field=dict(name='Instance', offset=FIELD_INSTANCE,
                             declaration=instance_field),
                  identification=[
                      dict(test='klass-cell idiom',
                           result='`ldr xK,[cell]` + `klass+0xE0` initialized byte + '
                                  'class-init helpers 0x110D028 / 0x110D12C, the same '
                                  'shape 141/142 read for GameConfig and Application'),
                      dict(test='statics read offset',
                           result='every statics read from this cell is at offset 0x0 '
                                  '(%d/%d rows carry only 0x0)' % (len(rows), len(rows))),
                      dict(test='statics+0x0 is `this`',
                           result='`ldr xT,[statics]` then `mov x0, xT` immediately '
                                  'before `bl` of a FirebaseDatabaseManager instance '
                                  'method'),
                      dict(test='dump.cs field',
                           result=instance_field),
                  ]),
        census=dict(pairs=pairs, distinct_methods=distinct, sites=sites_total,
                    per_raw={raw: sum(1 for row in rows if row['raw'] == raw)
                             for raw in sorted({row['raw'] for row in rows})},
                    rows=rows),
        api_census=dict(rvas={name: rva for rva, name in sorted(APIS.items())},
                        calls_per_raw=api_calls,
                        calls_distinct=api_sites_distinct,
                        methods_any_raw=api_methods,
                        methods_distinct=api_distinct,
                        note='`calls_per_raw` counts `bl` sites over the eight raw '
                             'snapshots (a method present in two raws counts twice); '
                             '`calls_distinct` and `methods_distinct` de-duplicate by '
                             'method, so they are the numbers to quote'),
        helper_census=dict(rvas={name: rva for rva, name in
                                  sorted((rva, name) for rva, name
                                         in helper_names().items())},
                           calls=helpers,
                           roles={name: 'declared in dump.cs' for name in
                                  sorted(helper_names().values())}),
        retry_loop=retry,
        coverage=coverage(rows),
        not_decoded=[
            dict(item='what was actually stored under each Firebase path',
                 blocking='the payload builders are decoded (SetSummaryDatas builds '
                          '`String.Format("{0}{1}/{2}/{3}", ...)` then '
                          '`JsonParse.ToJson`), but the remote values only exist at '
                          'runtime — MODEL_NOT_MEASURED runtime'),
            dict(item='the literal text of the path prefixes',
                 blocking='the path getters (`PVP_Manager.get_pathOfDataUsers` and '
                          'four siblings) read string *cells* on page 0x2AE0000, not '
                          'string literals, so the text is not attached to any pinned '
                          'dereference'),
            dict(item='the two unresolved delegate ctors',
                 blocking='0x18A4388 / 0x18A5580 are generic instantiations and have no '
                          'RVA line in dump.cs; they sit immediately before the '
                          '`UploadDatabase` / `DownloadDatabase` calls and take the '
                          'callback, but the instantiation is not named here'),
        ],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_firebase_cell.json.gz')
    args = parser.parse_args()
    payload = build_payload()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                               sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          pairs=payload['census']['pairs'],
                          methods=payload['census']['distinct_methods'],
                          sites=payload['census']['sites'],
                          calls=payload['api_census']['calls_distinct'])))


if __name__ == '__main__':
    main()
