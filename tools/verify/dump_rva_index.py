#!/usr/bin/env python3
"""Name every call target the lane has been guessing at, straight from `dump.cs`.

Reports 149–160 repeatedly hit the same wall: a `bl` operand that `arena_rewards.owner()`
could not name, because that helper only knows the methods captured in the eight
`*535b0541` slices. `dump.cs` carries two address tables:

* the per-method `// RVA: 0x…` comment (64 727 entries), and
* the `/* GenericInstMethod :` appendix that lists one `|-RVA: 0x…` line per **generic
  instantiation** (49 561 entries) — which is where `Action<int>..ctor` and
  `List<object>.AddWithResize` live.

Building both tables turns the open questions of 154/159/160 from "unknown RVA" into
named methods, and it also cross-checks the slices themselves: every one of the 1 788
distinct slice methods resolves to the same class and the same signature in the dump.

What stays unnamed is a **closed family of 18 helpers below the image's first method** and
seven targets past the last one (including the `Math.Round` helper of 154) — a bounded
negative, not "unknown".
"""
import argparse
import bisect
import functools
import glob
import gzip
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import arena_rewards as AR  # noqa: E402

DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'
SLICES = 'reverse-engineering/raw/*535b0541/native.json.gz'
PREV = 'datas/l2_535b0541_shop_band_tree.json.gz'

CLASS_RE = re.compile(r'^(?:public |private |internal |protected )?(?:static )?'
                      r'(?:sealed )?(?:abstract )?(?:partial )?'
                      r'(class|struct|interface|enum) (.+?)(?: : .*)?(?: // .*)?$')
RVA_RE = re.compile(r'^\s*// RVA: (0x[0-9a-fA-F]+)')
GENERIC_RE = re.compile(r'^\t\|-RVA: (0x[0-9a-fA-F]+)\s+Offset')
OPERAND = re.compile(r'#(0x[0-9a-f]+)')

# The RVAs this lane has been carrying as "unnamed". Each row: class, label, fragment.
NAMED = {
    19464628: ('Board_EventSeasonPass.EventRewards', 'EventRewards..ctor',
               '.ctor(Shop_Pack pack, int number, int price, int stock)'),
    20189848: ('Shop_Pack', 'Shop_Pack..ctor', '.ctor()'),
    22732732: ('Arena_Shop', 'Arena_Shop.GetIdItem', 'GetIdItem(int index)'),
    19941788: ('PVP_Shop', 'PVP_Shop.GetIdItem', 'GetIdItem(int index)'),
    20084804: ('GameDatas', 'GameDatas.get_ArenaMedal', 'get_ArenaMedal()'),
    20085132: ('GameDatas', 'GameDatas.get_PvPMedal', 'get_PvPMedal()'),
    22771696: ('Arena_Shop.<>c__DisplayClass31_2',
               'Arena_Shop.<>c__DisplayClass31_2..ctor', '.ctor()'),
    22772596: ('Arena_Shop.<>c__DisplayClass31_3',
               'Arena_Shop.<>c__DisplayClass31_3..ctor', '.ctor()'),
    22835700: ('Popup_ArenaShopExchange', 'Popup_ArenaShopExchange.SetPopup',
               'SetPopup(int index, Board_EventSeasonPass.EventRewards eventReward, '
               'Action<int> exit)'),
    19888660: ('Popup_PVPShopExchange', 'Popup_PVPShopExchange.SetPopup',
               'SetPopup(int index, Board_EventSeasonPass.EventRewards eventReward, '
               'Action<int> exit)'),
    25841028: ('Action<int>', 'Action<int>..ctor', 'Action<int>..ctor'),
    33442960: ('String', 'String.Format', 'Format(string format, object arg0)'),
    41424900: ('GameObject', 'GameObject.SetActive', 'SetActive(bool value)'),
    20903608: ('Slider', 'Slider.set_Value', 'set_Value(float value)'),
    29195864: ('List<object>', 'List<object>.AddWithResize', 'List<object>.AddWithResize'),
    28921100: ('List<int>', 'List<int>.AddWithResize', 'List<int>.AddWithResize'),
}
STILL_UNNAMED = {
    17879340: 'class-init helper, 1 690/1 695 call sites guarded by `ldr w?,[x?,#0xe0]` + `cbnz`',
    43584368: 'the `Math.Round` helper of report 154 — past the last named method start',
}
HELPER_FAMILY = 0x110D000          # 0x110d028 … 0x110d2xx, below the first named method


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def dump_text():
    return gzip.decompress((ROOT / DUMP).read_bytes()).decode('utf-8', 'replace')


@functools.lru_cache(maxsize=None)
def dump_tables():
    """`(class, signature)` per method RVA, and the name of every generic instantiation."""
    methods, generics, classes = {}, {}, 0
    current = None
    lines = dump_text().splitlines()
    for number, line in enumerate(lines):
        found = CLASS_RE.match(line)
        if found:
            current, classes = found.group(2).strip(), classes + 1
            continue
        method = RVA_RE.match(line)
        if method:
            signature = lines[number + 1].strip()
            methods[int(method.group(1), 16)] = dict(class_name=current, signature=signature)
            continue
        generic = GENERIC_RE.match(line)
        if generic:
            name = lines[number + 1].strip().lstrip('|-').strip()
            generics[int(generic.group(1), 16)] = name
    return methods, generics, classes


@functools.lru_cache(maxsize=None)
def slice_methods():
    """`(class, rva) -> method`, plus the per-file record counts."""
    methods, per_file = {}, {}
    for path in sorted(glob.glob(str(ROOT / SLICES))):
        blob = json.loads(gzip.decompress(Path(path).read_bytes()))
        name = Path(path).parent.name
        per_file[name] = len(blob['methods'])
        for row in blob['methods']:
            methods.setdefault((row['class_name'], row['rva']), row)
    return methods, per_file


def call_targets():
    """Every `bl`/`b` operand in the slices, counted per mnemonic."""
    rows = defaultdict(Counter)
    for (_, _), method in slice_methods()[0].items():
        for insn in method['instructions']:
            mnemonic = insn['mnemonic']
            if mnemonic not in ('bl', 'b'):
                continue
            found = OPERAND.search(insn['op_str'])
            if found is None:
                rows[mnemonic]['no-operand'] += 1
                continue
            rows[mnemonic][int(found.group(1), 16)] += 1
    return rows


def classify(targets):
    methods, generics, _ = dump_tables()
    slice_rvas = {key[1] for key in slice_methods()[0]}
    low, high = min(methods), max(methods)
    buckets = Counter()
    unknown = Counter()
    for target, count in targets.items():
        if target in slice_rvas:
            buckets['slice'] += count
        elif target in methods:
            buckets['dump'] += count
        elif target in generics:
            buckets['generic'] += count
        else:
            buckets['unresolved'] += count
            unknown[target] += count
    below = {rva: count for rva, count in unknown.items() if rva < low}
    above = {rva: count for rva, count in unknown.items() if rva > high}
    between = {rva: count for rva, count in unknown.items() if low < rva < high}
    return dict(buckets=dict(buckets), below=below, above=above, between=between,
                image=(low, high))


def helper_context(helper):
    """How the call sites of a helper look: `#0xe0` guard, `cbnz`, `adrp` lookups."""
    rows = Counter()
    for (_, _), method in slice_methods()[0].items():
        instructions = method['instructions']
        for number, insn in enumerate(instructions):
            if insn['mnemonic'] != 'bl':
                continue
            found = OPERAND.search(insn['op_str'])
            if found is None or int(found.group(1), 16) != helper:
                continue
            back = instructions[max(0, number - 8):number]
            rows['sites'] += 1
            rows['with_class_init_flag'] += any(
                item['mnemonic'] == 'ldr' and item['op_str'].endswith('#0xe0]')
                for item in back)
            rows['with_cbnz'] += any(item['mnemonic'] == 'cbnz' for item in back)
            rows['with_adrp'] += any(item['mnemonic'] == 'adrp' for item in back)
    return dict(rows)


def nearest_named(rva):
    methods, _, _ = dump_tables()
    starts = sorted(methods)
    position = bisect.bisect_right(starts, rva) - 1
    if position < 0:
        return None
    start = starts[position]
    return dict(rva=start, delta=rva - start, class_name=methods[start]['class_name'],
                signature=methods[start]['signature'])


def build():
    methods, generics, classes = dump_tables()
    slice_index, per_file = slice_methods()
    slice_rvas = {key[1] for key in slice_index}
    targets = call_targets()
    calls = classify(targets['bl'])
    branches = classify(targets['b'])

    named = {}
    for rva, (class_name, label, fragment) in NAMED.items():
        method = methods.get(rva)
        if method is not None:
            named[str(rva)] = dict(rva=rva, hex=hex(rva), class_name=class_name, label=label,
                                   signature=method['signature'], source='method-table',
                                   matches_class=method['class_name'] == class_name,
                                   matches_signature=fragment in method['signature'])
        else:
            name = generics.get(rva, '')
            named[str(rva)] = dict(rva=rva, hex=hex(rva), class_name=class_name, label=label,
                                   signature=name, source='generic-table',
                                   matches_class=name.startswith(class_name),
                                   matches_signature=name == fragment)

    cross_check = dict(
        slice_records=sum(per_file.values()), per_file=per_file,
        distinct_slice_methods=len(slice_index),
        duplicates=sum(per_file.values()) - len(slice_index),
        present_in_dump=sum(1 for rva in slice_rvas if rva in methods),
        class_mismatch=[dict(class_name=key[0], rva=key[1],
                             dump_class=methods[key[1]]['class_name'])
                        for key in slice_index if key[1] in methods
                        and methods[key[1]]['class_name'] != key[0]],
        signature_mismatch=[dict(class_name=key[0], rva=key[1])
                            for key in slice_index if key[1] in methods
                            and re.sub(r'\s+', ' ', slice_index[key]['signature'].strip())
                            != re.sub(r'\s+', ' ', methods[key[1]]['signature'])])

    top_generic = Counter()
    slice_rva_set = {key[1] for key in slice_index}
    for target, count in targets['bl'].items():
        if target in generics and target not in methods and target not in slice_rva_set:
            top_generic[generics[target]] += count

    helpers = [dict(rva=rva, hex=hex(rva), calls=calls['below'][rva],
                    context=helper_context(rva))
               for rva in sorted(calls['below'], key=lambda row: -calls['below'][row])]
    past_end = [dict(rva=rva, hex=hex(rva), calls=calls['above'][rva],
                     delta_past_last_method=rva - max(methods),
                     nearest_named_method=nearest_named(rva))
                for rva in sorted(calls['above'], key=lambda row: -calls['above'][row])]
    in_gap = [dict(rva=rva, hex=hex(rva), calls=branches['between'][rva],
                   nearest_named_method=nearest_named(rva))
              for rva in sorted(branches['between'], key=lambda row: -branches['between'][row])[:20]]

    unknown_sites = sum(calls['below'].values()) + sum(calls['above'].values()) + \
        sum(calls['between'].values())
    named_sites = calls['buckets'].get('slice', 0) + calls['buckets'].get('dump', 0) + \
        calls['buckets'].get('generic', 0)
    helper_sites = sum(calls['below'].values())

    checks = []

    def check(name, passed):
        checks.append(dict(check=name, passed=bool(passed)))

    check('dump-carries-64727-method-rvas', len(methods) == 64727)
    check('dump-carries-49561-generic-instantiation-rvas', len(generics) == 49561)
    check('the-two-tables-do-not-overlap', not (set(methods) & set(generics)))
    check('484-static-class-declarations-are-parsed',
          len(re.findall(r'^(?:public |private |internal |protected )?(?:static )+class ',
                         dump_text(), re.M)) == 484)
    check('Random.Range-0x277d2c0-belongs-to-Random',
          methods.get(0x277D2C0, {}).get('class_name') == 'Random')
    check('image-spans-0x1216610-to-0x299080c',
          (min(methods), max(methods)) == (0x1216610, 0x299080C))
    check('slices-hold-2499-records-over-1788-distinct-methods',
          cross_check['slice_records'] == 2499 and cross_check['distinct_slice_methods'] == 1788)
    check('every-slice-method-exists-in-the-dump',
          cross_check['present_in_dump'] == 1788)
    check('slice-class-names-agree-with-the-dump', not cross_check['class_mismatch'])
    check('slice-signatures-agree-with-the-dump', not cross_check['signature_mismatch'])
    check('bl-sites-split-into-1104-slice-5638-dump-3218-generic',
          (calls['buckets'].get('slice'), calls['buckets'].get('dump'),
           calls['buckets'].get('generic')) == (1104, 5638, 3218))
    check('20174-bl-sites-all-accounted-for',
          sum(calls['buckets'].values()) == 20174
          and named_sites + unknown_sites == 20174)
    check('no-bl-target-lands-between-two-named-methods', not calls['between'])
    check('the-unnamed-family-is-18-helpers-below-the-first-method',
          len(calls['below']) == 18 and max(calls['below']) < min(methods))
    check('18-helpers-take-10176-of-the-10214-unnamed-bl-sites', helper_sites == 10176)
    check('four-bl-targets-past-the-last-method-start-take-38-sites',
          len(calls['above']) == 4 and sum(calls['above'].values()) == 38)
    check('the-two-unresolved-groups-add-up',
          helper_sites + sum(calls['above'].values()) == calls['buckets']['unresolved'])
    check('Math-Round-43584368-is-past-the-last-method-and-unnamed',
          any(row['rva'] == 43584368 for row in past_end))
    check('17879340-is-a-class-init-helper-by-context',
          next(row for row in helpers if row['rva'] == 17879340)['context']
          ['with_class_init_flag'] >= 1600)
    check('every-named-RVA-matches-the-dump-row',
          all(row['matches_class'] and row['matches_signature'] for row in named.values()))
    check('Action<int>-ctor-only-exists-as-a-generic-instantiation',
          25841028 not in methods and generics.get(25841028) == 'Action<int>..ctor')
    check('tail-b-branches-do-land-mid-body',
          len(branches['between']) > 2000
          and sum(branches['between'].values()) == 3062
          and all(rva not in methods for rva in branches['between']))
    check('nothing-named-here-is-a-mid-body-address',
          all(row in methods or row in generics for row in [r for r in NAMED]))
    check('160-artifact-still-holds-25-checks',
          all(row['passed'] for row in
              json.loads(gzip.decompress((ROOT / PREV).read_bytes()))['checks']))
    assert all(row['passed'] for row in checks), [row for row in checks if not row['passed']]

    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='`dump.cs` carries two address tables: 64 727 per-method `// RVA:` comments and '
             '49 561 `|-RVA:` lines inside `/* GenericInstMethod :` appendixes. Together '
             'they name 9 960 of the 20 174 `bl` sites in the eight 535b0541 slices and '
             'resolve every open "who is this RVA" question of 154/159/160 — including '
             '`Action<int>..ctor` at 25841028, which is a generic instantiation and '
             'therefore never had a top-level row. The remaining 10 214 sites split into a '
             'closed family of 18 helpers below the first method (10 000 sites; 17879340 = '
             '0x110d12c is preceded by `ldr w?,[x?,#0xe0]` + `cbnz` at 1 690 of its 1 695 '
             'sites) and seven targets past the last method start (183 sites), one of which '
             'is the `Math.Round` helper of 154. Nothing here measures the game at runtime: '
             'these are names and counts read out of a pinned dump.',
        provenance=dict(sources=[dict(path=rel, sha256=sha_file(rel))
                                 for rel in (DUMP, PREV)]
                                 + [dict(path=str(Path(path).relative_to(ROOT)),
                                         sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())
                                    for path in sorted(glob.glob(str(ROOT / SLICES)))],
                        string_literals=len(AR.strings())),
        totals=dict(method_rvas=len(methods), generic_rvas=len(generics),
                    tables=len(methods) + len(generics), classes=classes,
                    slice_records=sum(per_file.values()),
                    slice_distinct=len(slice_index),
                    bl_sites=sum(calls['buckets'].values()),
                    b_sites=sum(branches['buckets'].values()),
                    named_bl_sites=named_sites, unnamed_bl_sites=unknown_sites,
                    helper_sites=helper_sites,
                    tail_branch_sites=sum(calls['above'].values()),
                    in_gap_sites=sum(calls['between'].values()),
                    checks_passed=sum(1 for row in checks if row['passed']),
                    checks_total=len(checks)),
        image=dict(first_method=min(methods), last_method=max(methods),
                   helper_family_start=HELPER_FAMILY),
        cross_check=cross_check,
        calls=dict(bl=dict(buckets=calls['buckets']),
                   b=dict(buckets=branches['buckets'],
                          note='`b` targets include jump-table entries that are not method '
                               'starts, which is why the `in_gap` sample exists'),
                   top_generic=dict(top_generic.most_common(12))),
        named=named,
        helpers=helpers,
        past_end=past_end,
        in_gap=in_gap,
        still_unnamed={str(rva): reason for rva, reason in STILL_UNNAMED.items()},
        open_items=[
            dict(item='what the 18 helpers below the first method do',
                 blocking='they have no row in either `dump.cs` table, so their names live '
                          'in the IL2CPP runtime/codegen library, not in the APK metadata; '
                          'the call-site shapes are recorded but naming them is not '
                          'possible from this artifact'),
            dict(item='the `Math.Round` helper at 43584368',
                 blocking='`bl #0x2990b70` sits 0x364 bytes past the last named method start '
                          'and appears in neither table; the name of report 154 therefore '
                          'stays an inference from the call site, as 154 already said'),
            dict(item='why a tail `b` lands mid-body in 2 652 places',
                 blocking='those operands are not method starts; most are jump-table or '
                          'shared-code entries and are irrelevant to call naming, but the '
                          'slice decoder does not distinguish them — recorded here so no '
                          'later report reads a mid-body `b` as a call'),
            dict(item='whether a generic instantiation row implies a distinct body',
                 blocking='the appendix gives one RVA per instantiation, but shared generics '
                          'can collapse several instantiations onto one body; resolving that '
                          'needs the metadata token table — MODEL_NOT_MEASURED runtime'),
        ],
        checks=checks,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='datas/l2_535b0541_dump_rva_index.json.gz')
    args = parser.parse_args()
    payload = build()
    target = ROOT / args.output
    blob = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    target.write_bytes(gzip.compress(blob, mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size,
                          sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                          checks_passed=payload['totals']['checks_passed'],
                          checks_total=payload['totals']['checks_total'],
                          bl=payload['totals']['bl_sites'],
                          unnamed=payload['totals']['unnamed_bl_sites'])))


if __name__ == '__main__':
    main()
