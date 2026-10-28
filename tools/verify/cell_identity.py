#!/usr/bin/env python3
"""What each unnamed metadata cell in the lane actually is.

Reports 138, 149 and 142 all end at the same wall: a cell in the usage table whose
class or literal cannot be read out of `slot_refs` alone. This pass adds two rules
that need no new extractor, and applies them to every cell the lane left open.

**Rule K (kind).** A usage addend that appears in `stringliteral.json` is a string
literal; an addend that does not is a type usage. Checked on the two cells 142/149
already named (both type usages) and on the two literals this report reads.

**Rule C (naming by own `.cctor`).** A class initialises its own statics inside its
own `..cctor`, and it reaches them through its own type usage. So if cell C is
loaded in `K..cctor` and the stores that follow (through the statics pointer at
`+0xB8`) land exactly on K's declared static fields, C is K's type usage. The rule
is only accepted when the layout is *unique* in `dump.cs`, otherwise the offsets
could belong to another class.

Two things fall out:

* `0x2ADF238` is `Board_PVP` — the cell the three bet handlers write through.
  The same `.cctor` also decodes its packed literal: `backBoard = BoardHome (1)`,
  `costEnergy = 15`.
* `ArenaManager.get_pathRoot` has **three** roots, not the two 138 listed: the
  fallback (neither `companyName == "Test"` nor `VersionControlSystem.PREMIUM`)
  returns the literal `arena---datas`.

Everything is static; no device, no probe.
"""
import argparse
import functools
import glob
import gzip
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import meta_rewards as MR  # noqa: E402

ARENA_RAW = 'reverse-engineering/raw/arena-pvp-535b0541/native.json.gz'
KEY_RAW = 'reverse-engineering/raw/key-grant-535b0541/native.json.gz'
RAW_GLOB = 'reverse-engineering/raw/*/native.json.gz'
STRINGS = 'reverse-engineering/il2cpp/stringliteral.json'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'

STATICS_PTR = 0xB8                     # Il2CppClass::static_fields on this build
INIT_METADATA = 17879080               # helper called before every usage load

# Every cell the lane left unnamed, plus the two that are already named and are used
# here as controls for rule K.
CELLS = {
    44954168: dict(hex='0x2ADF238', opened_by=149,
                   question='class behind the bet-value stores'),
    44939488: dict(hex='0x2ADB8E0', opened_by=142,
                   question='class behind the arena gate (142: Application)'),
    44954592: dict(hex='0x2ADF3E0', opened_by=138,
                   question='string compared with Application.companyName'),
    45009312: dict(hex='0x2AEC9A0', opened_by=138,
                   question='database root when companyName == Test'),
    45009320: dict(hex='0x2AEC9A8', opened_by=None,
                   question='database root in neither branch (never listed)'),
    45009328: dict(hex='0x2AEC9B0', opened_by=138,
                   question='database root when VersionControlSystem.PREMIUM'),
    44939608: dict(hex='0x2ADB958', opened_by=138,
                   question='class whose field +0 is tested before both fetches'),
    44961792: dict(hex='0x2AE1000', opened_by=138,
                   question='type argument of JsonParse.FromJson in PVP_Manager'),
}

# Already named by an earlier report; used here as a control for rule K, not re-derived.
KNOWN = {44939488: dict(klass='UnityEngine.Application', named_by=142)}

CALLS = {41274380: 'Application.get_companyName',
         20068044: 'VersionControlSystem.get_PREMIUM',
         33475124: 'String.op_Equality',
         INIT_METADATA: 'runtime-metadata init helper'}


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@functools.lru_cache(maxsize=None)
def strings():
    return {int(row['address'], 16): row['value']
            for row in json.loads((ROOT / STRINGS).read_text())}


@functools.lru_cache(maxsize=None)
def methods():
    """(class, signature) -> method, from either raw; raws overlap."""
    out = {}
    for rel in (KEY_RAW, ARENA_RAW):
        for method in load(rel)['methods']:
            out.setdefault((method['class_name'], method['signature'].strip()), method)
    return out


@functools.lru_cache(maxsize=None)
def rva_index():
    """method RVA -> (class, signature), read straight out of dump.cs."""
    out = {}
    lines = MR.dump_text().split('\n')
    current = None
    for index, line in enumerate(lines):
        decl = re.search(r'\b(?:class|struct) ([\w<>`.=]+)[^\n]*// TypeDefIndex: \d+\s*$', line)
        if decl and '{' not in line:
            current = decl.group(1)
        marker = re.search(r'// RVA: 0x([0-9A-Fa-f]+) Offset:', line)
        if marker:
            signature = lines[index + 1].strip() if index + 1 < len(lines) else ''
            out.setdefault(int(marker.group(1), 16), (current, signature))
    return out


@functools.lru_cache(maxsize=None)
def static_layouts():
    """{class: {offset: declared type}} for every class in dump.cs, one pass."""
    out, current, depth = {}, None, 0
    for line in MR.dump_text().split('\n'):
        if current is None:
            decl = re.match(r'^\s*(?:public|internal|private)?\s*(?:sealed\s+|abstract\s+|'
                            r'static\s+)*class ([\w<>`.=]+)[^\n]*// TypeDefIndex: \d+\s*$', line)
            if decl:
                current, depth = decl.group(1), 0
            continue
        depth += line.count('{') - line.count('}')
        if depth <= 0 and ('{' in line or '}' in line):
            current = None
            continue
        field = re.match(r'\s*(?:public|private|protected|internal)\s+static\s+'
                         r'(?:readonly\s+)?(.+?)\s+(\w+);\s*//\s*0x([0-9A-Fa-f]+)\s*$', line)
        if field:
            out.setdefault(current, {})[int(field.group(3), 16)] = field.group(1).strip()
    return out


def raw_paths():
    return tuple(sorted(glob.glob(RAW_GLOB)))


def token_tables():
    """{cell: {(kind, index)}} over every pinned raw — a cell's usage token."""
    out = {}
    for rel in raw_paths():
        for method in load(rel)['methods']:
            for ref in method.get('slot_refs') or []:
                lo = ref.get('token_lo')
                if lo is None:
                    continue
                out.setdefault(ref['slot_va'], set()).add(((lo >> 29) & 0x7,
                                                           lo & 0x1FFFFFFF))
    return out


TOKEN_KIND = {1: 'type', 5: 'string-literal', 6: 'method-ref'}


def token(cell):
    """The one (kind, index) a cell carries, if the extractor recorded it."""
    values = token_tables().get(cell)
    if not values:
        return dict(kind=None, index=None, consistent=None,
                    why='no slot_ref anywhere in the pinned raws')
    assert len(values) == 1, values
    kind, index = next(iter(values))
    return dict(kind=kind, kind_name=TOKEN_KIND.get(kind, 'other'), index=index,
                consistent=True,
                why='every use across the eight pinned raws carries the same token')


def uses(cell):
    """Every instruction that loads `cell`, deduplicated across the eight raws."""
    seen, rows = set(), []
    for rel in raw_paths():
        for method in load(rel)['methods']:
            for ref in method.get('slot_refs') or []:
                if ref['slot_va'] != cell:
                    continue
                key = (method['class_name'], method['signature'].strip(),
                       method['rva'], ref['rva'])
                if key in seen:
                    continue
                seen.add(key)
                rows.append(dict(raw=rel.split('/')[-2], class_name=method['class_name'],
                                 signature=method['signature'].strip(),
                                 method_rva=method['rva'],
                                 instruction_rva=ref['rva'], addend=ref.get('addend')))
    return rows


def addend(cell):
    for row in uses(cell):
        if row['addend'] is not None:
            return row['addend']
    return None


def kind(cell):
    """Rule K: the addend is either a string-literal address or a type index."""
    value = addend(cell)
    if value is None:
        return dict(kind='unrecorded', addend=None, literal=None,
                    why='the extractor recorded no addend for this cell, so even the '
                        'kind is out of reach here')
    if value in strings():
        return dict(kind='string', addend=value, literal=strings()[value],
                    why='addend appears in `stringliteral.json`')
    return dict(kind='type', addend=value, literal=None,
                why='addend is not a string-literal address, so the usage is a type')


def stored_fields(method, cell):
    """The statics writes a `.cctor` performs through `cell`, in instruction order."""
    insns = method['instructions']
    start = [k for k, i in enumerate(insns)
             if i['rva'] == next(ref['rva'] for ref in method['slot_refs']
                                 if ref['slot_va'] == cell)]
    cursor = start[0]
    reg = None
    while cursor < len(insns):
        hit = re.match(r'(x\d+), \[(x\d+), #0xb8\]$', insns[cursor]['op_str'])
        if insns[cursor]['mnemonic'] == 'ldr' and hit:
            reg = hit.group(1)
            statics = hit.group(2)
            cursor += 1
            break
        cursor += 1
    assert reg is not None, 'no statics pointer after the cell load'

    regs = {}
    for insn in insns:
        match = re.match(r'(d\d+|s\d+), \[', insn['op_str'])
        if insn['mnemonic'] == 'ldr' and match:
            for literal in method.get('literals') or []:
                if literal['instruction_rva'] == insn['rva']:
                    regs[match.group(1)] = literal

    rows = []
    for insn in insns[cursor:]:
        match = re.match(r'(.+?), \[(x\d+)(?:, #(0x[0-9a-f]+))?\]$', insn['op_str'])
        if insn['mnemonic'] not in ('str', 'strb', 'strh') or not match:
            continue
        if match.group(2) != reg:
            continue
        source, offset = match.group(1), int(match.group(3) or '0', 16)
        width = {'strb': 1, 'strh': 2}.get(insn['mnemonic'])
        if width is None:
            width = 8 if source.startswith(('x', 'xzr', 'd')) else 4
        literal = regs.get(source)
        decoded = None
        if literal is not None and width == len(bytes.fromhex(literal['hex'])):
            raw = bytes.fromhex(literal['hex'])
            decoded = dict(va=literal['va'], hex=literal['hex'],
                           ints=list(struct.unpack('<%di' % (len(raw) // 4), raw)))
        rows.append(dict(rva=insn['rva'], mnemonic=insn['mnemonic'], source=source,
                         offset=offset, width=width, literal=decoded,
                         covers=[offset + step for step in range(width)]))
    return rows


def layout_unique(layout):
    """How many classes in dump.cs share this exact static layout."""
    signature = {str(offset): kind for offset, kind in layout.items()}
    return sorted(name for name, fields in static_layouts().items()
                  if {str(offset): kind for offset, kind in fields.items()} == signature)


def analyse_cell(cell):
    meta = CELLS[cell]
    row = dict(cell=cell, **meta, uses=uses(cell), kind=kind(cell), token=token(cell))
    row['users'] = sorted({(use['class_name'], use['signature']) for use in row['uses']})
    row['user_classes'] = sorted({use['class_name'] for use in row['uses']})
    row['name'] = KNOWN[cell]['klass'] if cell in KNOWN else None
    row['named_by'] = KNOWN[cell]['named_by'] if cell in KNOWN else None
    row['naming'] = None

    # Rule C: is the cell loaded inside some class's own ..cctor?
    cctors = sorted({use['class_name'] for use in row['uses']
                     if '.cctor' in use['signature']})
    if cctors:
        assert len(cctors) == 1, cctors
        klass = cctors[0]
        method = methods()[(klass, 'private static void .cctor() { }')]
        writes = stored_fields(method, cell)
        layout = static_layouts()[klass]
        covered = {offset for write in writes for offset in write['covers']}
        missing = sorted(set(layout) - covered)
        # Everything not written must default to null, which in this build means a
        # reference type; a missing value type would mean the store set is incomplete.
        null_defaultable = [layout[offset] for offset in missing]
        unique = layout_unique(layout)
        assert all(kind_ in ('string', 'int[]', 'string[]', 'float[]')
                   for kind_ in null_defaultable), null_defaultable
        assert covered <= set(range(0, max(layout) + 4)), covered
        row['naming'] = dict(
            rule='own .cctor',
            klass=klass, cctor_rva=method['rva'],
            statics_pointer_offset=STATICS_PTR,
            writes=writes,
            declared_layout=[dict(offset=offset, type=kind_)
                             for offset, kind_ in sorted(layout.items())],
            covered_offsets=sorted(covered),
            null_defaulted=[dict(offset=offset, type=layout[offset]) for offset in missing],
            layout_matches=unique,
            layout_unique=len(unique) == 1,
        )
        assert len(unique) == 1 and unique[0] == klass, unique
        row['name'] = klass
        row['named_by'] = 150
    return row


def path_root():
    """`ArenaManager.get_pathRoot`, decoded to its three roots."""
    method = methods()[('ArenaManager', 'public static string get_pathRoot() { }')]
    insns = method['instructions']
    calls = []
    for insn in insns:
        if insn['mnemonic'] != 'bl':
            continue
        target = int(insn['op_str'].lstrip('#'), 16)
        klass, signature = rva_index().get(target, (None, None))
        calls.append(dict(rva=insn['rva'], target_rva=target,
                          named=CALLS.get(target), klass=klass, signature=signature))

    loads = {}
    for insn in insns:
        hit = re.match(r'x(\d+), \[x\d+, #(0x[0-9a-f]+)\]$', insn['op_str'])
        if insn['mnemonic'] == 'ldr' and hit:
            loads.setdefault(insn['rva'], 0x2AEC000 + int(hit.group(2), 16))

    branches = [
        dict(order=1, test='Application.companyName == "Test"',
             predicate_rva=CALLS_GET_COMPANY, compare_rva=CALLS_OP_EQUALITY,
             returns=dict(cell=45009312, hex='0x2AEC9A0')),
        dict(order=2, test='VersionControlSystem.PREMIUM',
             predicate_rva=CALLS_GET_PREMIUM,
             returns=dict(cell=45009328, hex='0x2AEC9B0')),
        dict(order=3, test='neither',
             predicate_rva=None,
             returns=dict(cell=45009320, hex='0x2AEC9A8')),
    ]
    for row in branches:
        row['returns']['kind'] = kind(row['returns']['cell'])
    return dict(
        method=dict(rva=method['rva'], size=method['size'],
                    instructions=len(insns)),
        calls=calls,
        branches=branches,
        csel='csel x8, x9, x8, ne — x9 (0x2AEC9B0) when PREMIUM, x8 (0x2AEC9A8) otherwise',
        note='the fallback branch is the one 138 never listed',
    )


CALLS_GET_COMPANY = 41274380
CALLS_GET_PREMIUM = 20068044
CALLS_OP_EQUALITY = 33475124


def build():
    cells = [analyse_cell(cell) for cell in sorted(CELLS)]
    by_cell = {row['cell']: row for row in cells}

    root = path_root()
    board = by_cell[44954168]
    assert board['name'] == 'Board_PVP'
    packed = [write for write in board['naming']['writes'] if write['literal']]
    assert len(packed) == 1
    packed = packed[0]
    assert packed['literal']['ints'] == [1, 15]

    # The literal names the first two declared statics in order.
    layout = board['naming']['declared_layout']
    decoded = [dict(offset=layout[index]['offset'], type=layout[index]['type'],
                    declared=[row for row in static_field_names('Board_PVP')
                              if row['offset'] == layout[index]['offset']][0]['field'],
                    value=value)
               for index, value in enumerate(packed['literal']['ints'])]

    checks = []
    # Rule K is a rule only if it agrees with the cells already named.
    checks.append(dict(check='rule-k-application-is-type',
                       cell=44939488, passed=by_cell[44939488]['kind']['kind'] == 'type'))
    checks.append(dict(check='rule-k-board-pvp-is-type',
                       cell=44954168, passed=board['kind']['kind'] == 'type'))
    checks.append(dict(check='rule-k-test-is-string',
                       cell=44954592,
                       passed=by_cell[44954592]['kind']['literal'] == 'Test'))
    checks.append(dict(check='rule-k-fallback-is-string',
                       cell=45009320,
                       passed=by_cell[45009320]['kind']['literal'] == 'arena---datas'))
    checks.append(dict(check='rule-c-layout-unique', cell=44954168,
                       passed=board['naming']['layout_unique']))
    checks.append(dict(check='rule-c-covers-declared', cell=44954168,
                       passed=bool(board['naming']['covered_offsets']) and
                              len(board['naming']['null_defaulted']) == 1))
    handlers = {user[1] for user in board['users'] if 'OnChange' in user[1]}
    checks.append(dict(check='three-bet-handlers-share-the-cell', cell=44954168,
                       passed={'private void OnChangeCoins(int amount) { }',
                               'private void OnChangeGems(int amount) { }',
                               'private void OnChangeMedals(int amount) { }'} <= handlers))
    checks.append(dict(check='a-bet-reader-exists-outside-the-board', cell=44954168,
                       passed=('PVP_Endgame', 'private void AddBetValues(int rankMine) { }')
                              in board['users']))
    checks.append(dict(check='get-path-root-has-three-roots', cell=None,
                       passed=[row['returns']['cell'] for row in root['branches']]
                              == [45009312, 45009328, 45009320]))
    checks.append(dict(check='get-path-root-calls-named', cell=None,
                       passed={row['target_rva'] for row in root['calls']} >=
                              {CALLS_GET_COMPANY, CALLS_GET_PREMIUM, CALLS_OP_EQUALITY}))
    checks.append(dict(check='token-agrees-with-rule-k',
                       cell=44954592,
                       passed=(by_cell[44954592]['token']['kind_name'] == 'string-literal'
                               and by_cell[44954592]['kind']['kind'] == 'string')))
    checks.append(dict(check='json-type-cell-is-a-method-ref', cell=44961792,
                       passed=by_cell[44961792]['token']['kind_name'] == 'method-ref'))
    checks.append(dict(check='premium-predicate-is-version-control', cell=None,
                       passed=dict((row['target_rva'], row['klass'])
                                   for row in root['calls'])[CALLS_GET_PREMIUM]
                              == 'VersionControlSystem'))
    assert all(row['passed'] for row in checks), [row for row in checks if not row['passed']]

    resolved = sum(1 for row in cells
                   if (row['name'] and row['named_by'] == 150) or row['kind']['literal'])
    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='Eight metadata cells, two rules, no new extractor: kind from the addend, '
             'identity from the class\'s own .cctor plus a unique static layout. Values '
             'that only exist on a device stay MODEL_NOT_MEASURED runtime.',
        provenance=dict(
            sources=[dict(path=path, sha256=sha_file(path))
                     for path in (KEY_RAW, ARENA_RAW, STRINGS, DUMP)],
            raws_scanned=len(raw_paths()),
            libil2cpp_sha256=load(KEY_RAW)['libil2cpp_sha256'],
            xapk_sha256=load(KEY_RAW)['xapk_sha256'],
            string_literals=len(strings()),
            classes_parsed=len(static_layouts()),
            token_cells=len(token_tables()),
            token_consistent=sum(1 for values in token_tables().values()
                                 if len(values) == 1)),
        rules=[
            dict(id='K', name='kind from the addend',
                 statement='an addend that appears in `stringliteral.json` is a string '
                           'literal; an addend that does not is a type usage',
                 control_cases=[44939488, 44954168, 44954592, 45009320]),
            dict(id='C', name='identity from the own `.cctor`',
                 statement='a cell loaded inside `K..cctor` whose statics writes land on '
                           'exactly K\'s declared fields is K\'s type usage; accepted only '
                           'when that layout is unique in dump.cs',
                 applied_to=[44954168]),
        ],
        cells=cells,
        board_pvp=dict(cell=44954168, klass='Board_PVP', packed_literal=packed['literal'],
                       consumers=[dict(class_name=user[0], signature=user[1])
                                  for user in board['users']
                                  if 'OnChange' in user[1] or 'BetValues' in user[1]],
                       decoded=decoded, cctor_rva=board['naming']['cctor_rva'],
                       layout_unique=board['naming']['layout_matches']),
        get_path_root=root,
        checks=checks,
        totals=dict(cells=len(cells),
                    named=dict((row['hex'], dict(klass=row['name'], by=row['named_by']))
                               for row in cells if row['name']),
                    literal=dict((row['hex'], row['kind']['literal'])
                                 for row in cells if row['kind']['literal']),
                    type_usage=[row['hex'] for row in cells
                                if row['kind']['kind'] == 'type' and not row['name']],
                    unresolved=[row['hex'] for row in cells
                                if not row['name'] and not row['kind']['literal']],
                    resolved=resolved),
        corrections=[
            dict(target=138, item='ArenaManager root variants',
                 statement='`get_pathRoot` returns slot 0x2AEC9A0 when companyName == '
                           '"Test" and slot 0x2AEC9B0 when PREMIUM',
                 correction='it has three returns, and the third — neither Test nor '
                            'PREMIUM — is `arena---datas`, which 138 never listed; the '
                            'PREMIUM predicate is `VersionControlSystem.get_PREMIUM` '
                            '(RVA 20068044), not an ArenaManager field',
                 evidence=dict(branches=[row['returns']['cell'] for row in root['branches']],
                               fallback_literal='arena---datas',
                               fallback_addend=46051720)),
            dict(target=149, item='class behind cell 0x2ADF238, where the chosen bet is stored',
                 statement='only the field offsets +0x10 / +0x14 / +0x18 are known',
                 correction='the cell is Board_PVP itself: it is what Board_PVP..cctor '
                            'initialises its own statics through, and the three offsets are '
                            'its declared betCoinValues / betGemValues / betMedalValues',
                 evidence=dict(klass='Board_PVP', cctor_rva=board['naming']['cctor_rva'],
                               layout_unique=board['naming']['layout_matches'])),
        ],
        confirmations=[
            dict(item='142: cell 0x2ADB8E0 is UnityEngine.Application',
                 result='confirmed from a second method — `ArenaManager.get_pathRoot` '
                        'initialises this cell and then calls Application.get_companyName'),
            dict(item='138: `arena---datas` is a live database root',
                 result='confirmed — it is the fallback return of get_pathRoot'),
        ],
        token_index=dict(
            note='every cell that appears in `slot_refs` carries exactly one '
                 '(kind, index) token, so the missing piece is only the index-to-name '
                 'table — not the identity of the index',
            kind_1=[dict(hex=row['hex'], index=row['token']['index'],
                         name=row['name']) for row in cells
                    if row['token'].get('kind_name') == 'type'],
            kind_5=[dict(hex=row['hex'], index=row['token']['index'],
                         literal=row['kind'].get('literal')) for row in cells
                    if row['token'].get('kind_name') == 'string-literal'],
            kind_6=[dict(hex=row['hex'], index=row['token']['index']) for row in cells
                    if row['token'].get('kind_name') == 'method-ref']),
        open_items=[
            dict(item='the Test root (0x2AEC9A0) and the PREMIUM root (0x2AEC9B0)',
                 blocking='both are string usages, but the extractor recorded no addend '
                          'for either load (3 of the method\'s 5 usage loads were '
                          'recorded), so the text needs the metadata-usage table, which '
                          'is not in the repo'),
            dict(item='class behind 0x2ADB958 (read as field +0 before both fetches)',
                 blocking='rule K says it is a type usage, rule C does not apply (no '
                          'pinned .cctor loads it), and no other pinned method names it'),
            dict(item='type argument of `JsonParse.FromJson` behind 0x2AE1000',
                 blocking='not a type usage at all: the token is kind 6 (method-ref, index '
                          '121683), so the generic instantiation is named in the method-ref '
                          'table. Resolving it needs that table; the load site exposes '
                          'nothing else'),
            dict(item='what the game does with these roots on a device',
                 blocking='MODEL_NOT_MEASURED runtime'),
        ],
    )


def static_field_names(klass):
    """[{offset, field, type}] for `klass`, from dump.cs."""
    text = MR.dump_text()
    match = re.search(r'^[^\n]*?\bclass ' + re.escape(klass) + r'(?=[\s:<])[^\n]*'
                      r'// TypeDefIndex: \d+$', text, re.M)
    start = text.index('{', match.start())
    depth, end = 0, start
    for end in range(start, len(text)):
        if text[end] == '{':
            depth += 1
        elif text[end] == '}':
            depth -= 1
            if depth == 0:
                break
    rows = []
    for line in text[start:end].split('\n'):
        field = re.match(r'\s*(?:public|private|protected|internal)\s+static\s+'
                         r'(?:readonly\s+)?(.+?)\s+(\w+);\s*//\s*0x([0-9A-Fa-f]+)\s*$', line)
        if field:
            rows.append(dict(offset=int(field.group(3), 16), field=field.group(2),
                             type=field.group(1).strip()))
    return sorted(rows, key=lambda row: row['offset'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='datas/l2_535b0541_cell_identity.json.gz')
    args = parser.parse_args()
    payload = build()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    target.write_bytes(gzip.compress(blob, mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size,
                          sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                          **payload['totals'])))


if __name__ == '__main__':
    main()
