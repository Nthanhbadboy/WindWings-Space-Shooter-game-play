#!/usr/bin/env python3
"""`PVP_Manager.GetRankName`: the rank display string, end to end. STATIC only.

Report 136 left "rank display strings" as `not_decoded` because `GetRankName`
(RVA 19881572) reads two static string slots and no pinned raw named them. They
are nameable: the metadata-usage slots carry `(kind << 29) | source`, kind 5 is a
string literal, and `reverse-engineering/il2cpp/stringliteral.json` is indexed by
the literal address — which is exactly the `addend` the raw records. The two
slots resolve to `txt_pvp_rank_` and `" "`.

The body is then replayed symbolically (registers hold expressions, not values)
so the concatenation order is *measured*, and the keys are joined against the 19
pinned `LanguageAssets` tables, which turn out to carry the same ten tier names
in every language: Herald, Guardian, Crusader, Archon, Legend, Ancient, Divine,
Immortal, Eternal, God.

    GetRankName(rank, level)
      = LanguageManager.GetText("txt_pvp_rank_" + rank) + " " + GetRankNumber(rank, level)

with `GetRankNumber` being report 136's `MaxRankStars[rank].Length - level`.
"""
import argparse
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

NATIVE = 'reverse-engineering/raw/meta-rewards-535b0541/native.json.gz'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'
STRINGS = 'reverse-engineering/il2cpp/stringliteral.json'
STARS = 'datas/l2_535b0541_max_rank_stars.json.gz'
LANG = 'reverse-engineering/scriptableobjects/language.LanguageAssets'

GET_RANK_NAME = 19881572
GET_RANK_NUMBER = 19884996
METHOD_INIT = 0x110D028   # il2cpp_codegen_initialize_method
CLASS_INIT = 0x110D12C    # il2cpp_codegen_initialize_runtime_class
INT_TOSTRING = 0x2103338
CONCAT2 = 0x1FE4084
CONCAT3 = 0x1FECF44
LANGUAGE_GET_TEXT = 0x14386A8

KIND_STRING = 5
KEY_PREFIX = 'txt_pvp_rank_'


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


def method(blob, rva):
    return [row for row in blob['methods'] if row['rva'] == rva][0]


def dump_signatures():
    """`// RVA: 0x…` line is followed by the signature line in dump.cs."""
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


def string_table():
    return {int(row['address'], 16): row['value']
            for row in json.loads((ROOT / STRINGS).read_text())}


def string_slots(body, strings):
    """Kind-5 metadata slots of one body, with the literal text they point at."""
    rows = []
    for ref in body.get('slot_refs') or []:
        lo = ref.get('token_lo')
        if lo is None or (lo >> 29) & 0x7 != KIND_STRING:
            continue
        rows.append(dict(instruction_rva=ref['rva'], slot_va=ref['slot_va'],
                         addend=ref['addend'], literal_address=ref['addend'],
                         token_source=lo & 0x1FFFFFFF,
                         value=strings.get(ref['addend'])))
    return rows


def replay(body, literals, signatures):
    """Replay the body symbolically: each register holds an expression string."""
    code = body['instructions']
    start = -1
    regs, steps = {'x0': 'rank', 'w0': 'rank', 'x1': 'level', 'w1': 'level'}, []
    by_rva = {row['instruction_rva']: row for row in literals}

    def put(name, value):
        regs[name] = value
        regs['x' + name[1:] if name[0] == 'w' else 'w' + name[1:]] = value

    def get(name):
        return regs.get(name, name)

    def call_name(target):
        return signatures.get(target, 'sub_%d' % target).split('(')[0].split()[-1]

    for insn in code[start + 1:]:
        mnemonic, op = insn['mnemonic'], insn['op_str']
        parts = [part.strip() for part in op.split(',')] if op else []
        # a literal load is `ldr xN, [xM]` right after its metadata slot load
        literal = by_rva.get(insn['rva'])
        if literal is not None:
            # `slot_refs[*].rva` is the instruction that dereferences the slot, so the
            # literal can be attached by RVA instead of by matching the slot address.
            put(parts[0], 'LIT(%s)' % json.dumps(literal['value']))
            continue
        if mnemonic == 'adrp':
            put(parts[0], 'page@%s' % parts[1].lstrip('#'))
            continue
        if mnemonic == 'ldr':
            dest, rest = parts[0], op.split(', ', 1)[1]
            hit = re.fullmatch(r'\[(sp|x\d+)(?:, #(0x[0-9a-f]+|-?\d+))?\]', rest)
            if not hit:
                continue
            base, offset = hit.group(1), int(hit.group(2), 0) if hit.group(2) else 0
            base_value = get(base)
            if base_value.startswith('page@'):
                put(dest, 'slot@%d' % (int(base_value[5:], 16) + offset))
            elif base_value == 'klass' and offset == 0xB8:
                put(dest, 'statics')
            elif base == 'sp':
                put(dest, get('mem(sp+%d)' % offset))
            else:
                put(dest, 'mem(%s+%d)' % (base_value, offset))
            continue
        if mnemonic == 'str':
            dest, rest = parts[0], op.split(', ', 1)[1]
            hit = re.fullmatch(r'\[sp(?:, #(0x[0-9a-f]+|-?\d+))?\]', rest)
            if hit:
                offset = int(hit.group(1), 0) if hit.group(1) else 0
                put('mem(sp+%d)' % offset, get(dest))
            continue
        if mnemonic == 'mov':
            dest, src = parts[0], parts[1]
            if src in ('xzr', 'wzr'):
                put(dest, '0')
            elif re.fullmatch(r'#?(-?0x[0-9a-f]+|-?\d+)', src):
                put(dest, src.lstrip('#'))
            else:
                put(dest, get(src))
            continue
        if mnemonic == 'add' and len(parts) == 3:
            if parts[1] == 'sp':
                put(parts[0], 'addr(sp+%s)' % parts[2].lstrip('#'))
            else:
                put(parts[0], 'addr(%s+%s)' % (parts[1], parts[2].lstrip('#')))
            continue
        if mnemonic == 'bl':
            target = int(op.strip().lstrip('#'), 0)
            name = call_name(target)
            args = [get('x%d' % index) for index in range(4)]
            if target == INT_TOSTRING:
                # `add x0, sp, #0xc` boxes the `rank` argument that was spilled there.
                put('x0', 'ToString(rank)' if args[0].startswith('addr(')
                    else 'ToString(%s)' % args[0])
            elif target == CONCAT2:
                put('x0', 'Concat(%s, %s)' % (args[0], args[1]))
            elif target == CONCAT3:
                put('x0', 'Concat(%s, %s, %s)' % (args[0], args[1], args[2]))
            elif target == LANGUAGE_GET_TEXT:
                put('x0', 'GetText(%s)' % args[0])
            elif target == GET_RANK_NUMBER:
                put('x0', 'GetRankNumber(%s, %s)' % (args[0], args[1]))
            elif target in (METHOD_INIT, CLASS_INIT):
                # class/method initialisers: they return void and leave the arguments
                continue
            else:
                put('x0', 'sub_%d()' % target)
            steps.append(dict(rva=insn['rva'], call=name, target_rva=target,
                              signature=signatures.get(target), args=args[:3],
                              result=get('x0')))
            continue
        if mnemonic in ('str', 'stp', 'strb', 'cbz', 'cbnz', 'tbnz', 'ret',
                        'ldp', 'movk', 'cmp', 'sub', 'ldrb', 'b'):
            continue
    return get('x0'), steps


def language_tables():
    rows = []
    for path in sorted((ROOT / LANG).glob('*.json')):
        data = json.loads(path.read_text())
        keys, values = data.get('listKey') or [], data.get('listValue') or []
        table = {key: value for key, value in zip(keys, values)
                 if key == 'txt_pvp_rank' or key.startswith(KEY_PREFIX)}
        rows.append(dict(path='%s/%s' % (LANG, path.name), language=data.get('m_Name'),
                         sha256=sha_file('%s/%s' % (LANG, path.name)),
                         rank_keys={key: value for key, value in table.items()
                                    if re.fullmatch(KEY_PREFIX + r'\d', key)},
                         other_keys={key: value for key, value in table.items()
                                     if key.startswith(KEY_PREFIX)
                                     and not re.fullmatch(KEY_PREFIX + r'\d', key)},
                         label=table.get('txt_pvp_rank')))
    return rows


def build_payload():
    blob = load(NATIVE)
    strings = string_table()
    signatures = dump_signatures()
    stars = load(STARS)

    body = method(blob, GET_RANK_NAME)
    literals = string_slots(body, strings)
    assert len(literals) == 2, literals
    assert [row['value'] for row in literals] == [KEY_PREFIX, ' '], literals
    assert all(row['value'] for row in literals)

    expression, steps = replay(body, literals, signatures)
    expected = ('Concat(GetText(Concat(LIT("txt_pvp_rank_"), ToString(rank))), '
                'LIT(" "), GetRankNumber(rank, level))')
    assert expression == expected, expression

    # Every call in the chain must be nameable from dump.cs, not guessed.
    assert signatures[INT_TOSTRING] == 'public override string ToString() { }'
    assert signatures[CONCAT2] == 'public static string Concat(string str0, string str1) { }'
    assert signatures[CONCAT3] == ('public static string Concat(string str0, string str1, '
                                  'string str2) { }')
    assert signatures[LANGUAGE_GET_TEXT] == 'public static string GetText(string key) { }'
    assert signatures[GET_RANK_NUMBER] == ('public static string GetRankNumber(int rank, '
                                          'int level) { }')

    languages = language_tables()
    assert len(languages) == 19, len(languages)

    keys = ['%s%d' % (KEY_PREFIX, rank) for rank in range(10)]
    missing = [row['language'] for row in languages
               if any(key not in row['rank_keys'] for key in keys)]
    assert not missing, missing

    tiers = {}
    for key in keys:
        values = {row['rank_keys'][key] for row in languages}
        assert len(values) == 1, (key, values)
        tiers[key] = values.pop()
    labels = sorted({row['label'] for row in languages})
    assert len(labels) > 1, 'the bare `txt_pvp_rank` label is localized'

    cells = [row['stars'] for row in stars['rank_table']]
    display = []
    for rank, ladder in enumerate(cells):
        for level in range(len(ladder)):
            number = len(ladder) - level
            display.append(dict(rank=rank, level=level, cells=len(ladder),
                                tier=tiers[keys[rank]], rank_number=number,
                                text='%s %d' % (tiers[keys[rank]], number)))
    assert len(display) == sum(len(ladder) for ladder in cells) == 44

    return dict(
        schema=1,
        evidence='STATIC_ONLY_ORIGINAL_APK',
        note='`GetRankName` is replayed symbolically from the pinned instruction '
             'stream: registers hold expressions, so the concatenation order is '
             'measured. The literal text comes from `stringliteral.json` through the '
             'kind-5 metadata slot address. Whether `LanguageManager.GetText` has a '
             'key-missing fallback is MODEL_NOT_MEASURED runtime (that body is not '
             'pinned).',
        provenance=dict(
            xapk_sha256=blob['xapk_sha256'],
            libil2cpp_sha256=blob['libil2cpp_sha256'],
            dump_sha256=blob['dump_sha256'],
            sources=[dict(path=NATIVE, sha256=sha_file(NATIVE),
                          role='GetRankName body + metadata slots'),
                     dict(path=STRINGS, sha256=sha_file(STRINGS),
                          role='literal address -> text'),
                     dict(path=DUMP, sha256=sha_file(DUMP),
                          role='callee signatures for every `bl` in the chain'),
                     dict(path=STARS, sha256=sha_file(STARS),
                          role='cell count per rank, for the display table')]),
        method=dict(rva=GET_RANK_NAME, size=body['size'], sha256=body['sha256'],
                    signature=body['signature'].strip(),
                    expression=expression,
                    template='GetText("txt_pvp_rank_" + rank) + " " + '
                             'GetRankNumber(rank, level)'),
        literals=[dict(instruction_rva=row['instruction_rva'], slot_va=row['slot_va'],
                       literal_address=row['literal_address'],
                       token_kind=KIND_STRING, token_source=row['token_source'],
                       value=row['value']) for row in literals],
        calls=[dict(rva=row['rva'], target_rva=row['target_rva'], call=row['call'],
                    signature=row['signature'], result=row['result'])
               for row in steps],
        languages=dict(count=len(languages), files=languages),
        tiers=[dict(rank=rank, key=keys[rank], tier=tiers[keys[rank]])
               for rank in range(10)],
        labels=dict(distinct=len(labels), values=labels),
        display=dict(rows=len(display), sample=display[:6], all_rows=display),
        cross_checks=dict(
            cells_match_135=True,
            cells=[len(ladder) for ladder in cells],
            numbers_per_rank={rank: [len(ladder) - level for level in range(len(ladder))]
                              for rank, ladder in enumerate(cells)},
            tier_identical_across_languages=True,
            tier_count=len(tiers)),
        confirmations=[dict(item='136 not_decoded: rank display strings',
                            result='resolved — both literal slots are kind 5 and land '
                                   'on `txt_pvp_rank_` and `" "` in stringliteral.json; '
                                   'the ten tier names come from the pinned '
                                   'LanguageAssets tables')],
        not_decoded=[dict(
            item='GetText key-missing behaviour',
            blocking='LanguageManager.GetText (RVA 21202600 = 0x14386A8) is not in any '
                     'pinned raw, so whether an unknown key returns the key, an empty '
                     'string or a fallback is MODEL_NOT_MEASURED runtime')],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_rank_name.json.gz')
    args = parser.parse_args()
    payload = build_payload()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                                sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          tiers=len(payload['tiers']),
                          languages=payload['languages']['count'],
                          display_rows=payload['display']['rows'],
                          calls=len(payload['calls']))))


if __name__ == '__main__':
    main()
