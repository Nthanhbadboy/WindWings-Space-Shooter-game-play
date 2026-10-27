#!/usr/bin/env python3
"""What is behind slot `0x2ADB8E0` (44939488)? The `UnityEngine.Application` klass cell.

Report 141 closed the *gate* slot (`0x2ADBB88` = `GameConfig`) and left this
neighbouring slot open. It is loaded in 47 methods across four raws, always in the
same shape — `adrp page` + `ldr xN,[xN,#0x8E0]`, i.e. page `0x2ADB000` plus
`0x8E0` — and never dereferenced to statics (`klass + 0xB8`), which is why a
statics scan finds nothing.

Two facts pin the class:

* the loaded pointer is used as an `Il2CppClass*`: `ldr w,[that,#0xE0]` is the
  "initialized" byte and `0x110D028` is the class-init helper — exactly the idiom
  that 141 read for the *known* `GameConfig` cell;
* 47/47 methods that load the cell then call a static method of
  `UnityEngine.Application` (resolved by RVA through `dump.cs`). No method loads
  the cell and calls only non-`Application` statics.

So the cell is `Application`'s klass, and the census of what the game calls on it
is the interesting part: `internetReachability` (the network chips), `companyName`
(path root and save defaults), `systemLanguage` (the gift-code language gate) and
`OpenURL` (the popup buttons).

Also decoded here, because the cell leads straight to them:

* `GameDatas.IsHasGiftLanguages` = `SystemLanguage ∈ {8, 10, 15, 22, 23}`
  = {Danish, English, German, Japanese, Korean} — Vietnamese is **not** included;
* the four `GameDatas` currency getters read `PlayerPrefs.GetInt(key, default)`
  behind a `-1` cache sentinel, with the default switched by
  `Application.companyName == "Test"`.

Evidence caveat recorded in the artifact: the raws' `slot_refs` index is *not*
exhaustive — it lists 45 of the 47 methods that actually load this cell.
"""
import argparse
import gzip
import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

RAW_GLOB = 'reverse-engineering/raw/*/native.json.gz'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'
STRINGS = 'reverse-engineering/il2cpp/stringliteral.json'

PAGE = 0x2ADB000
OFFSET = 0x8E0
SLOT = PAGE + OFFSET            # 0x2ADB8E0 = 44939488
CLASS_INIT = 0x110D028          # 17879080
CLASS_INIT_CHECK = 0x110D12C    # 17879340
PLAYER_PREFS_GET_INT = 0x277CCA0  # 41405600
STALE_GATE_SLOT = 0x2ADBB88     # the GameConfig cell from 141, for contrast

APIS = {
    41274380: 'Application.get_companyName',
    41274680: 'Application.get_systemLanguage',
    41274720: 'Application.get_internetReachability',
    41274460: 'Application.OpenURL',
}

GETTERS = {
    20069516: dict(name='GameDatas.get_Coins', cache=0x44, cheat=0x14, default=68999),
    20068904: dict(name='GameDatas.get_Gems', cache=0x48, cheat=0x18, default=500),
    20075932: dict(name='GameDatas.get_StarCount', cache=0x4C, cheat=0x1C, default=0),
    20070312: dict(name='GameDatas.get_WingCoins', cache=0x5C, cheat=None, default=999999),
}

GIFT_RVA = 20071724             # GameDatas.IsHasGiftLanguages
GIFT_SET = {8, 10, 14, 15, 22, 23, 26}

CLASS_LINE = re.compile(r'\s*(?:public|private|internal)?\s*(?:static\s+)?'
                        r'(?:sealed\s+)?(?:abstract\s+)?(?:partial\s+)?'
                        r'(?:class|struct|enum|interface) ([\w\.<>`]+)')


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
    """RVA -> (declaring class, signature) from dump.cs."""
    index, current = {}, None
    lines = dump_text().split('\n')
    for position, line in enumerate(lines[:-1]):
        found = CLASS_LINE.match(line)
        if found:
            current = found.group(1)
        rva = re.search(r'// RVA: 0x([0-9A-Fa-f]+)', line)
        if rva:
            index.setdefault(int(rva.group(1), 16), (current, lines[position + 1].strip()))
    return index


@lru_cache(maxsize=None)
def system_language():
    """value -> name for UnityEngine.SystemLanguage, straight from dump.cs."""
    names, inside = {}, False
    for line in dump_text().split('\n'):
        if re.match(r'\s*public enum SystemLanguage ', line):
            inside = True
            continue
        if inside:
            if line.strip().startswith('}'):
                break
            found = re.search(r'SystemLanguage (\w+) = (\d+);', line)
            if found:
                names[int(found.group(2))] = found.group(1)
    return names


def cell_sites(blob):
    """Every `adrp 0x2ADB000` + `ldr xN,[xN,#0x8E0]` in one raw."""
    out = []
    for method in blob['methods']:
        code = method['instructions']
        for position, insn in enumerate(code):
            if insn['mnemonic'] != 'adrp':
                continue
            found = re.fullmatch(r'(x\d+), #(0x[0-9a-f]+)', insn['op_str'])
            if not found or int(found.group(2), 0) != PAGE:
                continue
            reg = found.group(1)
            for follow in code[position + 1:position + 3]:
                load = re.fullmatch(r'%s, \[%s, #0x([0-9a-f]+)\]' % (reg, reg),
                                    follow['op_str'])
                if follow['mnemonic'] == 'ldr' and load \
                        and int(load.group(1), 16) == OFFSET:
                    out.append(dict(class_name=method['class_name'],
                                    signature=method['signature'].strip(),
                                    method_rva=method['rva'],
                                    adrp_rva=insn['rva'],
                                    load_rva=follow['rva'],
                                    reg=reg))
    return out


def idiom(blob, method_rva, load_rva):
    """Tags for how the loaded pointer is used right after the cell load.

    Two shapes share the cell: an eager `bl 0x110D028` (class init) and a lazy
    `ldr xD,[xR]` followed by `ldr w,[xD,#0xE0]` (the `initialized` byte of the
    klass). String parsing rather than regex, so the tag is easy to read.
    """
    method = next(item for item in blob['methods'] if item['rva'] == method_rva)
    code = {insn['rva']: insn for insn in method['instructions']}
    rvas = sorted(code)
    window = [code[rva] for rva in rvas[rvas.index(load_rva) + 1:][:5]]
    tags = []
    if any(insn['mnemonic'] == 'bl' and insn['op_str'].strip() == '#0x%x' % CLASS_INIT
           for insn in window):
        tags.append('class_init(0x110D028)')
    for position, insn in enumerate(window[:-1]):
        if insn['mnemonic'] != 'ldr':
            continue
        dest, _, rest = insn['op_str'].partition(', ')
        if not rest.startswith('[') or not rest.endswith(']') or ', ' in rest[1:-1]:
            continue
        base = rest[1:-1]
        flag = window[position + 1]
        if flag['mnemonic'] == 'ldr' and flag['op_str'].startswith('w') \
                and flag['op_str'].endswith('[%s, #0xe0]' % dest):
            tags.append('initialized_flag(klass+0xE0)')
            break
    return tags or ['unclassified']


def calls(method):
    """Call targets, `bl` and tail `b` alike."""
    out = []
    for insn in method['instructions']:
        if insn['mnemonic'] not in ('bl', 'b'):
            continue
        operand = insn['op_str'].strip()
        if re.fullmatch(r'#0x[0-9a-f]+', operand):
            out.append(int(operand.lstrip('#'), 16))
    return out


def census():
    """Per raw: methods loading the cell, and which Application API they call."""
    rows, sites_total = [], 0
    for path in raw_paths():
        blob = load(path)
        found = cell_sites(blob)
        sites_total += len(found)
        by_method = {}
        for site in found:
            by_method.setdefault(site['method_rva'], []).append(site)
        for method_rva, method_sites in sorted(by_method.items()):
            method = next(item for item in blob['methods'] if item['rva'] == method_rva)
            apis = sorted({APIS[target] for target in calls(method) if target in APIS})
            kinds = sorted({tag for site in method_sites
                            for tag in idiom(blob, method_rva, site['load_rva'])})
            rows.append(dict(raw=path.split('/')[-2], class_name=method['class_name'],
                             signature=method['signature'].strip(),
                             rva=method_rva, size=method['size'],
                             sites=len(method_sites), idiom=kinds, apis=apis))
    return rows, sites_total


def coverage(rows):
    """`slot_refs` lists fewer methods than the instruction scan finds."""
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
    return dict(scanned=len(scanned), indexed=len(indexed),
                missing_from_slot_refs=missing,
                note='`slot_refs` is an index, not a proof of absence: two methods '
                     'load the cell but never appear in it')


def gift_languages():
    blob = load(next(path for path in raw_paths() if 'key-grant' in path))
    method = next(item for item in blob['methods'] if item['rva'] == GIFT_RVA)
    names = system_language()
    checks = []
    for insn in method['instructions']:
        found = re.fullmatch(r'w\d+, #(0x[0-9a-f]+|\d+)', insn['op_str'])
        if insn['mnemonic'] == 'cmp' and found:
            value = int(found.group(1), 0)
            checks.append(dict(rva=insn['rva'], value=value,
                               name=names.get(value)))
    languages = [check['value'] for check in checks]
    return dict(rva=GIFT_RVA, signature=method['signature'].strip(), size=method['size'],
                checks=checks, languages=sorted(languages),
                names=[names[value] for value in sorted(languages)],
                excluded_example=dict(value=39, name=names.get(39)),
                structure='five `cmp w0, #v` + `b.eq` to the shared "true" exit '
                          '(10, 15, 23, 22, 26), then `cmp w0, #8` + `b.ne` so '
                          'Danish also returns true, then a second systemLanguage '
                          'read compared with `#0xe` (French) and returned via '
                          '`cset w0, eq`',
                rule='true when the device language is one of the seven; every '
                     'other value falls through to the French `cset` and returns '
                     'false')


def currency():
    """The PlayerPrefs default behind each cached currency getter.

    Each getter has one `PlayerPrefs.GetInt(key, default)` call per branch; the
    default is an immediate (`mov w1,#imm` possibly followed by `movk w1,#k,lsl
    #16`, or `mov w1,wzr`) in the normal branch, and a statics field load in the
    `companyName == "Test"` branch.
    """
    blob = load(next(path for path in raw_paths() if 'key-grant' in path))
    out = []
    for rva, spec in sorted(GETTERS.items()):
        method = next(item for item in blob['methods'] if item['rva'] == rva)
        code = method['instructions']
        hits = []
        for position, insn in enumerate(code):
            if insn['mnemonic'] != 'bl' or insn['op_str'].strip() != \
                    '#0x%x' % PLAYER_PREFS_GET_INT:
                continue
            back = code[max(0, position - 14):position]
            pages, constants, cheat, key = {}, [], None, None
            for offset, item in enumerate(back):
                adrp = re.fullmatch(r'(x\d+), #(0x[0-9a-f]+)', item['op_str'])
                if item['mnemonic'] == 'adrp' and adrp:
                    pages[adrp.group(1)] = int(adrp.group(2), 0)
                    continue
                loaded = re.fullmatch(r'(x\d+), \[(x\d+), #(0x[0-9a-f]+)\]',
                                      item['op_str'])
                if item['mnemonic'] == 'ldr' and loaded:
                    base = loaded.group(2)
                    if base in pages:
                        key = pages[base] + int(loaded.group(3), 16)
                wide = re.fullmatch(r'w1, #(0x[0-9a-f]+|\d+), lsl #16',
                                    item['op_str'])
                if item['mnemonic'] == 'movk' and wide:
                    continue
                fixed = re.fullmatch(r'w1, #(0x[0-9a-f]+|\d+)', item['op_str'])
                if item['mnemonic'] == 'mov' and fixed:
                    value = int(fixed.group(1), 0)
                    if offset + 1 < len(back):
                        nxt = back[offset + 1]
                        if nxt['mnemonic'] == 'movk' and wide_match(nxt['op_str']):
                            value += int(wide_match(nxt['op_str']).group(1), 0) << 16
                    constants.append(value)
                if item['mnemonic'] == 'mov' and item['op_str'].strip() == 'w1, wzr':
                    constants.append(0)
                cheat_ldr = re.fullmatch(r'w1, \[(x\d+), #(0x[0-9a-f]+)\]',
                                         item['op_str'])
                if item['mnemonic'] == 'ldr' and cheat_ldr:
                    cheat = int(cheat_ldr.group(2), 16)
            hits.append(dict(call_rva=insn['rva'], key_cell=key,
                             defaults=sorted(set(constants)), cheat_offset=cheat))
        defaults = sorted({value for hit in hits for value in hit['defaults']})
        out.append(dict(name=spec['name'], rva=rva, size=method['size'],
                        cache_offset=spec['cache'], cheat_offset=spec['cheat'],
                        sentinel=-1, call_sites=hits, defaults=defaults,
                        rule='if (cached == -1) cached = PlayerPrefs.GetInt(key, '
                             'Application.companyName == "Test" ? <cheat field> : '
                             '<constant>)'))
    return out


def wide_match(text):
    return re.fullmatch(r'w1, #(0x[0-9a-f]+|\d+), lsl #16', text)


def build_payload():
    rows, sites_total = census()
    assert len(rows) == 47, len(rows)
    assert sites_total >= 47, sites_total
    assert all(row['apis'] for row in rows), [row['class_name'] for row in rows
                                              if not row['apis']]

    apis = {}
    for row in rows:
        for name in row['apis']:
            apis[name] = apis.get(name, 0) + 1
    assert set(apis) == set(APIS.values()), sorted(apis)
    assert apis == {'Application.get_internetReachability': 29,
                    'Application.OpenURL': 6,
                    'Application.get_companyName': 10,
                    'Application.get_systemLanguage': 2}, apis

    kinds = {}
    for row in rows:
        for kind in row['idiom']:
            kinds[kind] = kinds.get(kind, 0) + 1
    assert kinds == {'class_init(0x110D028)': 47,
                     'initialized_flag(klass+0xE0)': 38,
                     'unclassified': 2}, kinds

    gift = gift_languages()
    assert gift['languages'] == sorted(GIFT_SET), gift['languages']
    assert gift['names'] == ['Danish', 'English', 'French', 'German', 'Japanese',
                             'Korean', 'Norwegian']
    assert 39 not in gift['languages']

    table = currency()
    assert [row['name'] for row in table] == [spec['name']
                                              for _, spec in sorted(GETTERS.items())]
    got = {row['name']: row['defaults'] for row in table}
    # 0xD87 then movk #1,lsl#16 is 0x10D87 = 68999 — not 0x1D87.
    assert 68999 in got['GameDatas.get_Coins'], got
    assert 7559 not in got['GameDatas.get_Coins'], got
    assert 500 in got['GameDatas.get_Gems'], got
    assert 0 in got['GameDatas.get_StarCount'], got
    assert 999999 in got['GameDatas.get_WingCoins'], got

    distinct = len({row['rva'] for row in rows})
    assert distinct == 33, distinct

    cover = coverage(rows)
    assert cover['scanned'] == 47 and cover['indexed'] == 45, cover

    raw_meta = [dict(path=path, sha256=sha_file(path)) for path in raw_paths()]
    blob = load(next(path for path in raw_paths() if 'arena-pvp' in path))
    return dict(
        schema=1,
        evidence='STATIC_ONLY_ORIGINAL_APK',
        note='The cell is identified as `UnityEngine.Application` by the class-init '
             'idiom plus a 47/47 callee census; the values it returns at runtime '
             '(device language, reachability, company name, save state) are '
             'MODEL_NOT_MEASURED runtime.',
        provenance=dict(
            xapk_sha256=blob['xapk_sha256'],
            libil2cpp_sha256=blob['libil2cpp_sha256'],
            dump_sha256=blob['dump_sha256'],
            sources=[dict(path=DUMP, sha256=sha_file(DUMP),
                          role='RVA -> declaring class for every callee, plus the '
                               'SystemLanguage enum values'),
                     dict(path=STRINGS, sha256=sha_file(STRINGS),
                          role='literal text for the comparisons'),
                     *[dict(path=row['path'], sha256=row['sha256'],
                            role='pinned methods that load the cell') for row in raw_meta]]),
        cell=dict(va=SLOT, decimal=SLOT, page=PAGE, offset=OFFSET,
                  klass='UnityEngine.Application',
                  gate_slot_from_141=dict(va=STALE_GATE_SLOT,
                                          decimal=STALE_GATE_SLOT,
                                          klass='GameConfig'),
                  delta=SLOT - STALE_GATE_SLOT),
        census=dict(methods=len(rows), distinct_methods=distinct, sites=sites_total,
                    per_raw={raw: sum(1 for row in rows if row['raw'] == raw)
                             for raw in sorted({row['raw'] for row in rows})},
                    rows=rows),
        api_census=apis,
        idiom=dict(kinds=kinds,
                   note='`ldr w,[klass+0xE0]` is the initialized byte and 0x110D028 '
                        'the class-init helper — the same shape 141 read for the '
                        'known GameConfig cell, which is what makes the cell a klass '
                        'pointer at all'),
        gift_languages=gift,
        currency=dict(rows=table,
                      get_int_rva=PLAYER_PREFS_GET_INT,
                      note='the four getters share one shape: a -1 sentinel in the '
                           'statics, then PlayerPrefs.GetInt(key, default) with the '
                           'default swapped by Application.companyName == "Test"'),
        coverage=cover,
        not_decoded=[
            dict(item='what Application.* returns on a device',
                 blocking='device language, reachability and company name are read '
                          'at runtime; the APK only carries the call sites — '
                          'MODEL_NOT_MEASURED runtime'),
            dict(item='PlayerPrefs key strings for the four currency getters',
                 blocking='the keys sit in string slots (0x2ADC0B8 / 0x2ADC0C8 / '
                          '0x2ADC0E0 / 0x2ADC1D0) whose literals are not attached to '
                          'any pinned dereference, so the text is not read here'),
        ],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_application_cell.json.gz')
    args = parser.parse_args()
    payload = build_payload()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                               sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          methods=payload['census']['methods'],
                          sites=payload['census']['sites'],
                          apis=len(payload['api_census']),
                          gift=payload['gift_languages']['names'])))


if __name__ == '__main__':
    main()
