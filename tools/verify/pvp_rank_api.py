#!/usr/bin/env python3
"""`PVP_Manager` rank API: the points codec and the `MaxRankStars` reader. STATIC only.

Three pinned methods answer "how is a PvP rank stored", and one of them is the
reader report 135 said was missing:

* `ToPoints(rank, level, star, point)`  RVA 19903696 — packs four numbers into one int.
* `DataFromPoints(points)`              RVA 19871992 — unpacks them into
  `UserPointDataLeagues` (`pvpRank @0x10`, `pvpLevel @0x14`, `pvpPoints @0x18`,
  `totalPoints @0x1C`, `pvpStars @0x20`).
* `GetRankNumber(rank, level)`          RVA 19884996 — `MaxRankStars[rank].Length - level`.

The verifier does not paraphrase these bodies: it **executes the pinned
instruction stream** with a tiny AArch64 subset interpreter (the same idea as the
`PVP_Manager..cctor` reports, but now on straight-line code) and compares the
result with the closed-form formula on a grid. Two invariants then fall out:

    ToPoints(DataFromPoints(p)) == p                for every p built by ToPoints
    GetRankNumber(rank, level) == cells(rank) - level

Corrections carried here (frozen artifacts are not rewritten):

* **135 said "no pinned PVP_Manager method touches statics +0x18".** Wrong:
  `GetRankNumber` reads `MaxRankStars` through `ldr x8,[class,#0xb8];
  ldr x0,[x8,#0x18]`. 135's scan looked for `ldr x8,[x8,#0xb8]` — the statics
  base was `x8` written from `x0` there, so the follow-up load started with
  `x0,` and every read was dropped. The statics map below re-scans with register
  tracking instead of a fixed pattern.
* **134 said `IsOpen` is only written in `.cctor`.** `LoadRemoteConfigs`
  (RVA 19916080) also stores `strb wzr,[statics,#0x4C]`, i.e. the board is forced
  closed on every remote-config load — fail-closed, not just an initial value.
"""
import argparse
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

META = 'reverse-engineering/raw/meta-rewards-535b0541/native.json.gz'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'
STARS = 'datas/l2_535b0541_max_rank_stars.json.gz'
RULES = 'datas/l2_535b0541_pvp_manager_rules.json.gz'

TO_POINTS = 19903696
FROM_POINTS = 19871992
RANK_NUMBER = 19884996
REMOTE = 19916080
CCTOR = 19916640

MEMCPY_ALLOC = 0x110D240
LIST_GET_ITEM = 0x1BD7B94
INT_TOSTRING = 0x14204DC

CLASS = {'tags': 'PVP_Manager klass'}
STATICS = {'tags': 'static fields'}
LIST = {'tags': 'MaxRankStars list'}
ARRAY = {'tags': 'MaxRankStars[rank]'}
OBJ = {'tags': 'UserPointDataLeagues instance'}

SUPPORTED = {'mov', 'movk', 'cmp', 'csel', 'mul', 'madd', 'msub', 'smull', 'bic',
             'add', 'sub', 'lsr', 'asr', 'stp', 'str', 'ldr', 'ldrb', 'adrp',
             'cbz', 'cbnz', 'tbnz', 'b', 'bl', 'ret', 'ldp', 'strb'}


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


def call_target(insn):
    text = insn['op_str'].strip().lstrip('#')
    return int(text, 0) if re.fullmatch(r'(0x[0-9a-f]+|\d+)', text) else None


def imm(text):
    text = text.strip().lstrip('#').strip()
    shift = 0
    match = re.fullmatch(r'(-?0x[0-9a-f]+|-?\d+)(?:, lsl #(\d+))?', text)
    if not match:
        return None
    value = int(match.group(1), 0)
    if match.group(2):
        shift = int(match.group(2))
        value &= 0xFFFFFFFF
        value = (value << shift) & 0xFFFFFFFFFFFFFFFF
        if value & 0x80000000:
            value &= 0xFFFFFFFF
    return value


def reg_index(name):
    return int(name[1:])


def norm(reg):
    """`w8` and `x8` are the same register for tracking purposes."""
    return 'x' + reg[1:]


def written_regs(insn):
    if insn['mnemonic'] in ('str', 'strb', 'strh', 'stp', 'cmp', 'cbz', 'cbnz',
                            'tbz', 'tbnz', 'b', 'bl', 'ret', 'nop'):
        return set()
    head = insn['op_str'].split('[')[0]
    return {norm(reg) for reg in re.findall(r'\b([xw]\d+)\b', head)}


# ---------------------------------------------------------------- statics map


# Every PVP_Manager method reaches its statics through a metadata-usage slot that
# holds the klass pointer. `0x2ADFE40` (decimal 44957248) is proven to be the
# PVP_Manager usage: `GetRankNumber` loads it, and running that body against
# 135's `MaxRankStars` reproduces `MaxRankStars[rank].Length - level` exactly, so
# the slot must be PVP_Manager's. Reads through other slots belong to other types
# even though they also index +0xb8.
PVP_KLASS_SLOT = 0x2ADFE40


def statics_access(blob):
    """Every `PVP_Manager` static field touched, by slot and register tracking."""
    out, ignored = [], []
    for body in blob['methods']:
        if body['class_name'] != 'PVP_Manager':
            continue
        pages, slots, klasses, statics, rows = {}, {}, {}, {}, []
        for insn in body['instructions']:
            mnemonic, op = insn['mnemonic'], insn['op_str']
            adrp = re.fullmatch(r'(x\d+), #(0x[0-9a-f]+)', op)
            if mnemonic == 'adrp' and adrp:
                reg = norm(adrp.group(1))
                pages[reg] = int(adrp.group(2), 0)
                for table in (slots, klasses, statics):
                    table.pop(reg, None)
                continue
            if ', [' in op and mnemonic in ('ldr', 'ldrb', 'str', 'strb'):
                dest, rest = op.split(', ', 1)
                hit = re.fullmatch(r'\[(x\d+)(?:, #(0x[0-9a-f]+|-?\d+))?\]', rest)
                if hit:
                    base = norm(hit.group(1))
                    offset = int(hit.group(2), 0) if hit.group(2) else 0
                    is_load = mnemonic in ('ldr', 'ldrb')
                    # A: `ldr xR,[xPage,#off]` -> R = the value of metadata slot xPage+off.
                    if is_load and mnemonic == 'ldr' and base in pages:
                        page, dest_norm = pages[base], norm(dest)
                        for table in (slots, klasses, statics):
                            table.pop(dest_norm, None)
                        pages.pop(dest_norm, None)
                        slots[dest_norm] = page + offset
                        continue
                    # B: `ldr xK,[xR]` -> K = klass held by the slot value in R.
                    if is_load and base in slots and offset == 0:
                        klasses[norm(dest)] = slots[base]
                        statics.pop(norm(dest), None)
                        continue
                    # C: `ldr xS,[xK,#0xb8]` -> S = klass->static_fields.
                    if is_load and base in klasses and offset == 0xB8:
                        statics[norm(dest)] = klasses[base]
                        continue
                    # D: any access through the statics pointer is a static field.
                    if base in statics:
                        rows.append(dict(rva=insn['rva'],
                                         kind='read' if is_load else 'write',
                                         mnemonic=mnemonic, dest=dest, offset=offset,
                                         klass_slot=statics[base]))
                        continue
            for reg in written_regs(insn):
                for table in (pages, slots, klasses, statics):
                    table.pop(reg, None)
        if not rows:
            continue
        name = body['signature'].strip().split('(')[0].split()[-1]
        if name != '.cctor':
            kept = [row for row in rows if row['klass_slot'] == PVP_KLASS_SLOT]
            for row in rows:
                if row['klass_slot'] != PVP_KLASS_SLOT:
                    ignored.append(dict(method=name, rva=row['rva'], offset=row['offset'],
                                        klass_slot=row['klass_slot'],
                                        reason='metadata slot is not PVP_Manager'))
            rows = kept
        if rows:
            out.append(dict(method=name, rva=body['rva'], accesses=rows))
    return out, ignored


# ---------------------------------------------------------------- interpreter


class Unsupported(Exception):
    pass


class Regs(dict):
    """One 64-bit register file: `w8` and `x8` are the same storage."""

    def __setitem__(self, name, value):
        value = 0 if value is None else value
        if name[0] == 'w':
            super().__setitem__('x' + name[1:], value & 0xFFFFFFFF)
        else:
            super().__setitem__(name, value)

    def __getitem__(self, name):
        if name[0] == 'w':
            return super().__getitem__('x' + name[1:]) & 0xFFFFFFFF
        return super().__getitem__(name)

    def get(self, name, default=0):
        try:
            return self[name]
        except KeyError:
            return default


def run(insns, regs, hooks=None, mem=None):
    """Execute the pinned instructions; a deliberately small AArch64 subset."""
    hooks = hooks or {}
    mem = mem if mem is not None else {}
    flags = {}
    seeded = Regs()
    for name, value in regs.items():
        seeded[name] = value
    regs = seeded
    for insn in insns:
        mnemonic, op = insn['mnemonic'], insn['op_str']
        if mnemonic not in SUPPORTED:
            raise Unsupported(mnemonic + ' @' + hex(insn['rva']))
        parts = [part.strip() for part in op.split(',')] if op else []
        if mnemonic == 'ret':
            break
        if mnemonic in ('adrp', 'ldp', 'nop'):
            continue
        if mnemonic == 'mov':
            dest, src = parts[0], parts[1]
            if src in ('xzr', 'wzr'):
                regs[dest] = 0
            elif imm(src) is not None:
                regs[dest] = imm(src)
            else:
                regs[dest] = regs.get(src, 0)
            continue
        if mnemonic == 'movk':
            dest, src = parts[0], parts[1]
            shift = int(re.search(r'lsl #(\d+)', op).group(1))
            value = regs.get(dest, 0) & ~(0xFFFF << shift)
            regs[dest] = (value | ((imm(src) & 0xFFFF) << shift)) & 0xFFFFFFFFFFFFFFFF
            continue
        if mnemonic == 'cmp':
            left, right = parts[0], parts[1]
            value = regs.get(right, imm(right) if imm(right) is not None else 0)

            def signed(word):
                word &= 0xFFFFFFFF
                return word - (1 << 32) if word & 0x80000000 else word

            # `lt`/`ge` are signed conditions, so compare as int32.
            flags['cmp'] = signed(regs.get(left, 0)) - signed(value)
            continue
        if mnemonic == 'csel':
            dest, left, right, cond = parts
            diff = flags.get('cmp', 0)
            take_left = (diff < 0) if cond == 'lt' else (diff >= 0) if cond == 'ge' else None
            assert take_left is not None, 'csel cond ' + cond
            regs[dest] = regs.get(left, 0) if take_left else regs.get(right, 0)
            continue
        if mnemonic == 'bic':
            # `bic wD, wN, wN, asr #31` is the clamp-to-zero idiom: it clears every
            # bit when wN is negative and leaves it untouched otherwise.
            dest, left, right, shift = parts[0], parts[1], parts[2], parts[3]
            assert shift.startswith('asr #'), op
            base = regs.get(right, 0) & 0xFFFFFFFF
            signed_base = base - (1 << 32) if base & 0x80000000 else base
            amount = (signed_base >> int(shift.split('#')[1], 0)) & 0xFFFFFFFF
            regs[dest] = (regs.get(left, 0) & 0xFFFFFFFF) & ~amount & 0xFFFFFFFF
            continue
        if mnemonic == 'mul':
            regs[parts[0]] = (regs.get(parts[1], 0) * regs.get(parts[2], 0)) & 0xFFFFFFFF
            continue
        if mnemonic in ('madd', 'msub'):
            dest, a, b, c = parts
            product = regs.get(a, 0) * regs.get(b, 0)
            total = regs.get(c, 0) + product if mnemonic == 'madd' else regs.get(c, 0) - product
            regs[dest] = total & 0xFFFFFFFF
            continue
        if mnemonic == 'smull':
            dest, left, right = parts
            a, b = regs.get(left, 0), regs.get(right, 0)
            a = a - (1 << 32) if a & 0x80000000 else a
            b = b - (1 << 32) if b & 0x80000000 else b
            regs[dest] = (a * b) & 0xFFFFFFFFFFFFFFFF
            continue
        if mnemonic == 'lsr':
            dest, src = parts[0], parts[1]
            shift_n = int(parts[2].split('#')[1], 0)
            regs[dest] = (regs.get(src, 0) & 0xFFFFFFFFFFFFFFFF) >> shift_n
            continue
        if mnemonic == 'asr':
            dest, src = parts[0], parts[1]
            shift_n = int(parts[2].split('#')[1], 0)
            value = regs.get(src, 0) & 0xFFFFFFFFFFFFFFFF
            if value & (1 << 63):
                value -= 1 << 64
            regs[dest] = value >> shift_n
            continue
        if mnemonic == 'add':
            dest = parts[0]
            if len(parts) == 2:
                regs[dest] = regs.get(parts[1], 0)
                continue
            left = regs.get(parts[1], 0)
            right = parts[2]
            if 'asr #' in op:
                shift_n = int(re.search(r'asr #(0x[0-9a-f]+|\d+)', op).group(1), 0)
                value = regs.get(right, 0)
                if value & 0x80000000:
                    value -= 1 << 32
                regs[dest] = (left + (value >> shift_n)) & 0xFFFFFFFF
            elif right.startswith('#'):
                regs[dest] = (left + imm(right)) & 0xFFFFFFFF
            else:
                regs[dest] = (left + regs.get(right, 0)) & 0xFFFFFFFF
            continue
        if mnemonic == 'sub':
            regs[parts[0]] = (regs.get(parts[1], 0) - regs.get(parts[2], 0)) & 0xFFFFFFFF
            continue
        if mnemonic in ('ldr', 'ldrb'):
            dest, rest = parts[0], op.split(', ', 1)[1]
            hit = re.fullmatch(r'\[(x\d+)(?:, #(0x[0-9a-f]+|-?\d+))?\]', rest)
            if not hit:
                regs[dest] = 0
                continue
            base = regs.get(hit.group(1), 0)
            offset = int(hit.group(2), 0) if hit.group(2) else 0
            if base is CLASS and offset == 0xB8:
                regs[dest] = STATICS
            elif base is STATICS:
                regs[dest] = mem.get((id(STATICS), offset), 0)
            elif base is LIST:
                regs[dest] = mem.get((id(LIST), offset), 0)
            elif base is ARRAY:
                regs[dest] = mem.get((id(ARRAY), offset), 0)
            elif base is OBJ:
                regs[dest] = mem.get((id(OBJ), offset), 0)
            else:
                regs[dest] = 0
            continue
        if mnemonic in ('str', 'strb', 'stp'):
            rest = op.split('[', 1)[1].rstrip(']')
            target, offset = rest.split(',') if ',' in rest else (rest, '#0')
            base = regs.get(target.strip(), 0)
            offset = int(offset.strip().replace('#', ''), 0)
            values = [regs.get(parts[0], 0)] if mnemonic != 'stp' else \
                [regs.get(parts[0], 0), regs.get(parts[1], 0)]
            for index, value in enumerate(values):
                key = (id(base), offset + 4 * index)
                mem[key] = value
            continue
        if mnemonic == 'bl':
            target = call_target(insn)
            hook = hooks.get(target)
            regs['x0'] = hook(regs) if hook else None
            continue
        if mnemonic in ('b', 'cbz', 'cbnz', 'tbnz'):
            if mnemonic == 'b':
                target = call_target(insn)
                hook = hooks.get(target)
                if hook:
                    regs['x0'] = hook(regs)
                continue
            if mnemonic == 'cbz' and regs.get(parts[0], 0) == 0:
                raise AssertionError('cbz not modelled at %s' % hex(insn['rva']))
            if mnemonic == 'cbnz' and regs.get(parts[0], 0) != 0:
                raise AssertionError('cbnz not modelled at %s' % hex(insn['rva']))
            continue
        raise Unsupported(mnemonic)
    return regs, mem


def slice_from(body, start_rva):
    rows = [insn for insn in body['instructions'] if insn['rva'] >= start_rva]
    for index, insn in enumerate(rows):
        if insn['mnemonic'] == 'ret':
            return rows[:index + 1]
    # Some of these bodies end in a tail call (`b`) instead of `ret`.
    return rows


def body_of(blob, rva):
    return [row for row in blob['methods'] if row['rva'] == rva][0]


# ---------------------------------------------------------------- derivations


def to_points(blob):
    body = body_of(blob, TO_POINTS)
    cases = []
    for rank in (0, 1, 5, 9, 12):
        for level in (0, 1, 4, 9):
            for star in (0, 3, 9):
                for point in (-5, 0, 1, 99, 100, 150):
                    regs, _ = run(body['instructions'],
                                  {'w0': rank & 0xFFFFFFFF, 'w1': level & 0xFFFFFFFF,
                                   'w2': star & 0xFFFFFFFF, 'w3': point & 0xFFFFFFFF})
                    expected = (rank * 1000000 + level * 100000 + star * 10000
                                + min(max(point, 0), 100))
                    assert regs['w0'] == expected & 0xFFFFFFFF, (rank, level, star, point,
                                                                regs['w0'], expected)
                    cases.append(dict(rank=rank, level=level, star=star, point=point,
                                      points=regs['w0']))
    constants = decode_constants(body['instructions'], ('w9', 'w10', 'w8'))
    assert constants['w9'] == 1000000 and constants['w10'] in (100000, 10000)
    return dict(rva=TO_POINTS, size=body['size'], sha256=body['sha256'],
                constants=constants, clamp_high=100, clamp_low=0,
                formula='points = rank*1_000_000 + level*100_000 + star*10_000 + '
                        'clamp(point, 0, 100)',
                emulated_cases=len(cases), sample=cases[:6])


def decode_constants(insns, wanted):
    """Value of every `mov wN,#lo` + `movk wN,#hi,lsl#16` pair."""
    out, pending = {}, {}
    for insn in insns:
        match = re.match(r'(w\d+), #(0x[0-9a-f]+|\d+)(?:, lsl #16)?$', insn['op_str'])
        if insn['mnemonic'] == 'mov' and match:
            pending[match.group(1)] = int(match.group(2), 0)
        elif insn['mnemonic'] == 'movk' and match:
            reg = match.group(1)
            hi = int(match.group(2), 0)
            lo = pending.get(reg, 0)
            out[reg] = (lo & 0xFFFF) | (hi << 16)
    return {reg: value for reg, value in out.items() if reg in wanted}


def from_points(blob, stars):
    body = body_of(blob, FROM_POINTS)
    start = next(insn['rva'] for insn in body['instructions']
                 if insn['mnemonic'] == 'cbz') + 4
    code = slice_from(body, start)
    fields = {}
    cases = []
    for points in (0, 1, 99, 100, 10000, 100000, 999999, 1000000, 1000001,
                   1234567, 99999999, 100000000):
        mem = {}
        run(code, {'x20': OBJ, 'w19': points & 0xFFFFFFFF}, mem=mem)
        got = {offset: mem.get((id(OBJ), offset), 0)
               for offset in (0x10, 0x14, 0x18, 0x1C, 0x20)}
        expected = dict(rank=points // 1000000, level=(points % 1000000) // 100000,
                        points=points % 100, total=points,
                        stars=(points % 100000) // 10000)
        assert got[0x10] == expected['rank'], (points, got, expected)
        assert got[0x14] == expected['level'], (points, got, expected)
        assert got[0x18] == expected['points'], (points, got, expected)
        assert got[0x1C] == expected['total'], (points, got, expected)
        assert got[0x20] == expected['stars'], (points, got, expected)
        fields = expected
        cases.append(dict(total_points=points, **expected))
    return dict(rva=FROM_POINTS, size=body['size'], sha256=body['sha256'],
                field_offsets={'pvpRank': 0x10, 'pvpLevel': 0x14, 'pvpPoints': 0x18,
                               'totalPoints': 0x1C, 'pvpStars': 0x20},
                formula='pvpRank = points / 1_000_000; pvpLevel = (points % 1_000_000) / '
                        '100_000; pvpPoints = points % 100; pvpStars = (points % 100_000) / '
                        '10_000; totalPoints = points',
                emulated_cases=len(cases), sample=cases)


def rank_number(blob, stars):
    body = body_of(blob, RANK_NUMBER)
    table = [row['stars'] for row in stars['rank_table']]
    start = next(insn['rva'] for insn in body['instructions']
                 if insn['op_str'] == 'x8, [x0, #0xb8]')
    code = slice_from(body, start)


    cases = []
    for rank in range(10):
        for level in range(0, len(table[rank])):
            # The body ends in a tail call to `Int32.ToString` (RVA 14205020), so the
            # number under test is the argument handed to that call.
            seen = []
            mem = {(id(STATICS), 0x18): LIST}

            def get_item(regs, mem=mem):
                index = regs.get('w1', 0)
                assert 0 <= index < len(table), index
                mem[(id(ARRAY), 0x18)] = len(table[index])
                return ARRAY

            def to_string(regs, seen=seen):
                seen.append(regs.get('w0', 0))
                return str(seen[-1])

            run(code, {'x0': CLASS, 'w20': rank, 'w19': level},
                hooks={LIST_GET_ITEM: get_item, INT_TOSTRING: to_string}, mem=mem)
            value = seen[-1]
            expected = len(table[rank]) - level
            assert value == expected, (rank, level, value, expected)
            cases.append(dict(rank=rank, level=level, cells=len(table[rank]),
                              rank_number=value))
    return dict(rva=RANK_NUMBER, size=body['size'], sha256=body['sha256'],
                reads='PVP_Manager statics +0x18 (MaxRankStars)',
                returns='string: Int32.ToString(cells - level), reached by a tail `b` to '
                        'RVA 21103836',
                signature='public static string GetRankNumber(int rank, int level)',
                formula='GetRankNumber(rank, level) = MaxRankStars[rank].Length - level',
                emulated_cases=len(cases),
                by_rank=[dict(rank=rank, cells=len(table[rank]),
                              numbers=[len(table[rank]) - level
                                       for level in range(len(table[rank]))])
                         for rank in range(10)])


def rank_scale(rank, level, star, point):
    return rank * 1000000 + level * 100000 + star * 10000 + min(max(point, 0), 100)


def build_payload():
    meta = load(META)
    stars = load(STARS)
    rules = load(RULES)

    accesses, unowned = statics_access(meta)
    assert RANK_NUMBER in {row['rva'] for row in accesses}
    rank_read = [row for row in accesses if row['rva'] == RANK_NUMBER][0]
    assert all(row['kind'] == 'read' for row in rank_read['accesses']
               if row['offset'] == 0x18), rank_read
    remote = [row for row in accesses if row['rva'] == REMOTE][0]
    is_open_write = [row for row in remote['accesses']
                     if row['kind'] == 'write' and row['offset'] == 0x4C]
    assert is_open_write, remote

    to_points_rows = to_points(meta)
    from_points_rows = from_points(meta, stars)
    rank_rows = rank_number(meta, stars)

    # Round trip: anything ToPoints can emit must unpack back to the same fields.
    round_trip = []
    for rank in (0, 1, 9, 12):
        for level in (0, 4, 9):
            for star in (0, 5, 9):
                for point in (0, 42, 99):
                    packed = rank * 1000000 + level * 100000 + star * 10000 + point
                    unpacked = dict(rank=packed // 1000000,
                                    level=(packed % 1000000) // 100000,
                                    star=(packed % 100000) // 10000,
                                    point=packed % 100)
                    assert unpacked == dict(rank=rank, level=level, star=star, point=point)
                    round_trip.append(dict(points=packed, **unpacked))

    return dict(
        schema=1,
        evidence='STATIC_ONLY_ORIGINAL_APK',
        note='The codec and the reader below are executed from the pinned instruction '
             'stream. Anything that depends on live data (served rank configs, the '
             'localized rank-name strings) is MODEL_NOT_MEASURED runtime or recorded as '
             'not_decoded.',
        provenance=dict(
            xapk_sha256=meta['xapk_sha256'], libil2cpp_sha256=meta['libil2cpp_sha256'],
            dump_sha256=meta['dump_sha256'],
            sources=[dict(path=META, sha256=sha_file(META),
                          role='PVP_Manager method bodies'),
                     dict(path=STARS, sha256=sha_file(STARS),
                          role='MaxRankStars cells, needed to run GetRankNumber'),
                     dict(path=RULES, sha256=sha_file(RULES),
                          role='statics layout, used to name offsets'),
                     dict(path=DUMP, sha256=sha_file(DUMP),
                          role='UserPointDataLeagues field declarations')]),
        pinned_methods=[dict(name=row['signature'].strip(), rva=row['rva'],
                             size=row['size'], sha256=row['sha256'])
                        for row in (body_of(meta, TO_POINTS), body_of(meta, FROM_POINTS),
                                    body_of(meta, RANK_NUMBER), body_of(meta, REMOTE),
                                    body_of(meta, CCTOR))],
        statics_access=dict(
            klass_slot=dict(va=PVP_KLASS_SLOT, decimal=PVP_KLASS_SLOT,
                            basis='GetRankNumber reads +0x18 through this slot and running '
                                  'that body against 135 gives cells(rank) - level, so the '
                                  'slot is PVP_Manager'),
            methods=accesses,
            rejected_reads=unowned),
        to_points=to_points_rows,
        data_from_points=from_points_rows,
        get_rank_number=rank_rows,
        round_trip=dict(cases=len(round_trip),
                        identity='DataFromPoints(ToPoints(rank, level, star, point)) '
                                 'restores all four fields for point < 100, level < 10, '
                                 'star < 10',
                        sample=round_trip[:4],
                        saturation=dict(
                            note='point is stored as `points % 100`, so a clamped '
                                 'point == 100 reads back as 0: the top of the clamp '
                                 'range is not representable.',
                            point_100=dict(points=rank_scale(0, 0, 0, 100),
                                           pvp_points=0))),
        corrections=[
            dict(item="135: 'no pinned PVP_Manager method touches statics +0x18'",
                 measured='GetRankNumber (RVA 19884996) reads statics +0x18 and indexes it '
                          'with List.get_Item(rank)',
                 why_missed='135 scanned for `ldr x8,[x8,#0xb8]`; here the statics base is '
                            'x8 loaded from x0, so the follow-up load reads `x0, [x8,#0x18]` '
                            'and the pattern-based scan dropped it. This report tracks '
                            'classes/statics through registers instead.',
                 impact='MaxRankStars[rank] is the cell list for that rank: index = rank is '
                        'proven here, not inferred'),
            dict(item='134: IsOpen written only in .cctor',
                 measured='LoadRemoteConfigs (RVA 19916080) also does strb wzr,[statics,#0x4C]',
                 why_missed='134 only walked .cctor',
                 impact='the PvP board is fail-closed on every remote-config load, so a '
                        'failed fetch leaves IsOpen=false rather than the shipped default'),
        ],
        not_decoded=[
            dict(item='rank display strings',
                 blocking='GetRankName (RVA 19881572) concatenates a static prefix string '
                          'with rank.ToString() and GetRankNumber(); the prefix lives in a '
                          'static string slot (0x2ADCAE0 / 0x2ADB0B38) that no pinned raw '
                          'resolves, so the textual rank names cannot be quoted'),
            dict(item='served rank configuration',
                 blocking='LoadRemoteConfigs fetches Firebase and only then fills pvpDatas; '
                          'the shipped file has no server payload — MODEL_NOT_MEASURED runtime'),
            dict(item='whether level 0 of rank 0 is a real tier',
                 blocking='GetRankNumber proves rank 0 has 3 cells (levels 0..2) while '
                          'AllRewards has reward rows only for levels 1..2; no pinned code '
                          'explains the missing level-0 row'),
        ],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_pvp_rank_api.json.gz')
    args = parser.parse_args()
    payload = build_payload()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                                sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          methods=len(payload['statics_access']['methods']),
                          to_points=payload['to_points']['emulated_cases'],
                          from_points=payload['data_from_points']['emulated_cases'],
                          rank_number=payload['get_rank_number']['emulated_cases'])))


if __name__ == '__main__':
    main()
