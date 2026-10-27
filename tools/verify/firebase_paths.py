#!/usr/bin/env python3
"""Report 182: the game's Firebase path schema, read statically out of the data page.

Report 181 identified the cell that reaches `FirebaseDatabaseManager` and had to
record one gap: the path *prefixes* are not string literals, they are **cells**
(`0x2AE0D28`, `0x2AEC9A8`, ...) whose text was "not attached to any pinned
dereference". That was too pessimistic. The workspace already carries the two
tables needed to dereference a cell without the `.so`:

* `reverse-engineering/raw/ui-audit/native-relocations.json.gz` — 288733
  relocation sites, `slot VA -> pointer VA`;
* `reverse-engineering/raw/ui-audit/metadata-index.json.gz` — `ScriptString`
  (15054 `Address -> Value`) and `ScriptMetadata` (10758 `Address -> Name`).

So `cell -> relocation target -> ScriptString` is a two-table lookup, not a guess.
Everything below is that lookup applied to the 34 methods of report 181 plus the
root getters, and every row keeps both midpoints (cell VA and target VA) so the
chain can be re-walked by hand.

What it produces:

* the **roots**: `ArenaManager.get_pathRoot` (22685676) = `arena-test-datas` /
  `arena---datas` / `arena--datas` behind `Application.get_companyName() == "Test"`,
  and `PVP_Manager.get_pathRoot` (19859292) = `data-leagues`;
* 27 path fragments and 19 `String.Format` templates — the shape of every
  `summary-datas` / `rank-datas` / `rank-configs` / `data-solos` / `map-{n}` path
  the game reads or writes;
* an **independent confirmation of 181**: the cell `0x2ADB958` relocates to
  `FirebaseDatabaseManager_TypeInfo`, which 181 did not use.

Static only: which season / rank / room numbers are substituted, and what the
server returns, stay `MODEL_NOT_MEASURED runtime`.
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

import firebase_cell as FC  # noqa: E402

RELOCATIONS = 'reverse-engineering/raw/ui-audit/native-relocations.json.gz'
METADATA_INDEX = 'reverse-engineering/raw/ui-audit/metadata-index.json.gz'
DUMP = FC.DUMP

APIS = FC.APIS                 # six FirebaseDatabaseManager methods, from 181
CELL_181 = FC.SLOT             # 0x2ADB958 = 44939608
CELL_APPLICATION = FC.NEIGHBOUR  # 0x2ADB8E0, report 142

CONCAT = 33439876              # String.Concat(string, string), one of the overloads
FORMAT = 33477820              # String.Format(string format, object[] args), one of them
COMPANY_NAME = 41274380        # Application.get_companyName()
STRING_EQUALITY = 33475124     # String.op_Equality(string, string)
PREMIUM = 20068044             # VersionControlSystem.get_PREMIUM()

ROOT_GETTERS = {
    22685676: 'ArenaManager.get_pathRoot',
    19859292: 'PVP_Manager.get_pathRoot',
    19887544: 'PVP_Manager.get_pathOfDataUsers',
    19874728: 'PVP_Manager.get_pathOfDataRanks',
    19915052: 'PVP_Manager.get_pathOfDataPlayOfUsers',
    19915784: 'PVP_Manager.get_pathOfDataPlayOfMachines',
    19915932: 'PVP_Manager.get_pathOfDataConfigs',
}


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def relocations():
    """cell VA -> pointer target VA, straight out of the APK's relocation table."""
    blob = json.loads(gzip.decompress((ROOT / RELOCATIONS).read_bytes()))
    return {int(key, 16): int(value, 16) for key, value in blob['relocations'].items()}


@lru_cache(maxsize=None)
def metadata_index():
    blob = json.loads(gzip.decompress((ROOT / METADATA_INDEX).read_bytes()))
    return blob['tables']


@lru_cache(maxsize=None)
def script_strings():
    return {row['Address']: row['Value']
            for row in metadata_index()['ScriptString']}


@lru_cache(maxsize=None)
def script_metadata():
    return {row['Address']: row['Name']
            for row in metadata_index()['ScriptMetadata']}


@lru_cache(maxsize=None)
def resolve(cell):
    """cell VA -> (kind, value, target VA) or None."""
    target = relocations().get(cell)
    if target is None:
        return None
    value = script_strings().get(target)
    if value is not None:
        return dict(kind='string', value=value, target=target)
    name = script_metadata().get(target)
    if name is not None:
        return dict(kind='metadata', value=name, target=target)
    return None


def cell_reads(method):
    """Every `adrp page` + `ldr xN,[xN,#off]` cell load in one method."""
    code = method['instructions']
    out = []
    for position, insn in enumerate(code):
        if insn['mnemonic'] != 'adrp':
            continue
        found = re.fullmatch(r'(x\d+), #(0x[0-9a-f]+)', insn.get('op_str') or '')
        if not found:
            continue
        page, reg = int(found.group(2), 16), found.group(1)
        for follow in code[position + 1:position + 3]:
            read = re.fullmatch(r'%s, \[%s(?:, #(0x[0-9a-f]+))?\]' % (reg, reg),
                                follow.get('op_str') or '')
            if follow['mnemonic'] == 'ldr' and read:
                cell = page + (int(read.group(1), 16) if read.group(1) else 0)
                out.append((cell, insn['rva']))
                break
    return out


def literals_of(method):
    """Resolved string cells of one method, de-duplicated, with both midpoints."""
    rows, seen = [], set()
    for cell, load_rva in cell_reads(method):
        if cell in seen:
            continue
        seen.add(cell)
        found = resolve(cell)
        if found and found['kind'] == 'string':
            rows.append(dict(cell=cell, cell_decimal=cell, target=found['target'],
                             target_decimal=found['target'],
                             value=found['value'], load_rva=load_rva))
    return sorted(rows, key=lambda row: row['cell'])


def metadata_of(method):
    rows, seen = [], set()
    for cell, _ in cell_reads(method):
        if cell in seen:
            continue
        seen.add(cell)
        found = resolve(cell)
        if found and found['kind'] == 'metadata':
            rows.append(dict(cell=cell, cell_decimal=cell, target=found['target'],
                             name=found['value']))
    return sorted(rows, key=lambda row: row['cell'])


@lru_cache(maxsize=None)
def string_helpers():
    """Every `String.Format` / `String.Concat` overload, read off dump.cs.

    The templates are formatted through different overloads — the two-argument
    `Format` in `ArenaDatabaseCleaner.<Start>d__0`, the `object[]` one in
    `ArenaManager` — so a single hard-coded RVA undercounts. The table is derived,
    not typed.
    """
    table = {}
    for rva, (klass, signature) in FC.rva_index().items():
        if klass != 'String':
            continue
        if 'static string Format(' in signature:
            table[rva] = 'String.Format'
        elif 'static string Concat(' in signature:
            table[rva] = 'String.Concat'
    return table


def call_counts(method, table):
    counts = {}
    for insn in method['instructions']:
        if insn['mnemonic'] not in ('bl', 'b'):
            continue
        operand = (insn.get('op_str') or '').strip()
        if not re.fullmatch(r'#0x[0-9a-f]+', operand):
            continue
        target = int(operand.lstrip('#'), 16)
        if target in table:
            counts[table[target]] = counts.get(table[target], 0) + 1
    return counts


def is_path(value):
    return value.startswith('/') or value.endswith('/') or '/' in value


def is_template(value):
    return '{' in value


def placeholders(value):
    """`{n}` / `{n:fmt}` indices in order of appearance."""
    return [int(found.group(1)) for found in re.finditer(r'\{(\d+)(?::[^}]*)?\}', value)]


def firebase_methods():
    found = {}
    for path in FC.raw_paths():
        for method in FC.load(path)['methods']:
            found.setdefault(method['rva'], method)
    return found


def census():
    scanned = firebase_methods()
    rows = []
    for rva in sorted({row['rva'] for row in FC.census()[0]}):
        method = scanned[rva]
        strings = literals_of(method)
        metadata = metadata_of(method)
        paths = [row for row in strings if is_path(row['value'])]
        templates = [row for row in strings if is_template(row['value'])]
        rows.append(dict(
            rva=rva, class_name=method['class_name'],
            signature=method['signature'].strip(), size=method['size'],
            api_calls=sorted({call['name'] for call in FC.calls(method, APIS)}),
            format_calls=call_counts(method, string_helpers()).get('String.Format', 0),
            concat_calls=call_counts(method, string_helpers()).get('String.Concat', 0),
            string_cells=len(strings), metadata_cells=len(metadata),
            path_literals=[row['value'] for row in paths],
            templates=[row['value'] for row in templates],
            literals=paths + [row for row in templates if row not in paths],
            cell_reads=len(cell_reads(method)),
        ))
    return rows


def roots():
    """Every root getter, with the cells it selects between."""
    scanned = firebase_methods()
    out = []
    for rva, name in sorted(ROOT_GETTERS.items()):
        method = scanned[rva]
        strings = literals_of(method)
        table = dict(string_helpers())
        table.update({COMPANY_NAME: 'Application.get_companyName',
                      STRING_EQUALITY: 'String.op_Equality',
                      PREMIUM: 'VersionControlSystem.get_PREMIUM'})
        calls = call_counts(method, table)
        branches = []
        if rva == 22685676:
            values = {item['value']: item['cell'] for item in strings}
            branches = [
                dict(cell=values['arena-test-datas'], cell_decimal=values['arena-test-datas'],
                     literal='arena-test-datas',
                     condition='Application.get_companyName() == "Test"'),
                dict(cell=values['arena--datas'], cell_decimal=values['arena--datas'],
                     literal='arena--datas',
                     condition='VersionControlSystem.get_PREMIUM() != false'),
                dict(cell=values['arena---datas'], cell_decimal=values['arena---datas'],
                     literal='arena---datas',
                     condition='otherwise — PREMIUM false'),
            ]
            branches.sort(key=lambda row: row['cell'])
        out.append(dict(
            rva=rva, name=name, size=method['size'], branches=branches,
            signature=method['signature'].strip(),
            literals=strings,
            calls=calls,
            rule=('`if (Application.get_companyName() == "Test") return '
                  '"arena-test-datas"; return VersionControlSystem.get_PREMIUM() ? '
                  '"arena--datas" : "arena---datas";` — a `csel` on the PREMIUM flag, '
                  'no concatenation' if rva == 22685676 else
                  'the literal concatenated with a sibling `String.Concat` part; the '
                  'root itself is a constant here'),
        ))
    return out


def templates(rows):
    """Template -> where it is used, plus the placeholder shape."""
    out = {}
    for row in rows:
        for value in row['templates']:
            entry = out.setdefault(value, dict(value=value, placeholders=placeholders(value),
                                               kind='path' if is_path(value) else 'message',
                                               users=[]))
            entry['users'].append(dict(rva=row['rva'], class_name=row['class_name'],
                                       api_calls=row['api_calls'],
                                       format_calls=row['format_calls']))
    for entry in out.values():
        entry['users'].sort(key=lambda item: item['rva'])
        entry['contiguous'] = entry['placeholders'] == list(range(len(entry['placeholders'])))
    return [out[key] for key in sorted(out)]


def machine_names(rows):
    """The name pool loaded in the same method that fabricates machine/user ids."""
    scanned = firebase_methods()
    hits = []
    for row in rows:
        pool = [value for value in
                [item['value'] for item in literals_of(scanned[row['rva']])]
                if not is_path(value) and not is_template(value)]
        fabricates_ids = any(token in ' '.join(row['templates'])
                            for token in ('PVP_Machine', 'user#'))
        if len(pool) >= 8 and fabricates_ids:
            hits.append(dict(rva=row['rva'], class_name=row['class_name'],
                             names=sorted(pool), count=len(pool)))
    return hits


def build_payload():
    rows = census()
    assert len(rows) == 34, len(rows)

    identity_cell = resolve(CELL_181)
    identity_app = resolve(CELL_APPLICATION)
    assert identity_cell == dict(kind='metadata', value='FirebaseDatabaseManager_TypeInfo',
                                 target=identity_cell['target']), identity_cell
    assert identity_app['value'] == 'UnityEngine.Application_TypeInfo', identity_app

    root_rows = roots()
    by_name = {row['name']: row for row in root_rows}
    arena_root = by_name['ArenaManager.get_pathRoot']
    assert sorted(row['value'] for row in arena_root['literals']) == \
        ['Test', 'arena---datas', 'arena--datas', 'arena-test-datas'], \
        arena_root['literals']
    assert arena_root['calls'].get('Application.get_companyName') == 1, arena_root['calls']
    assert arena_root['calls'].get('VersionControlSystem.get_PREMIUM') == 1, arena_root['calls']
    assert [row['literal'] for row in arena_root['branches']] == \
        ['arena-test-datas', 'arena---datas', 'arena--datas'], arena_root['branches']
    assert [row['value'] for row in by_name['PVP_Manager.get_pathRoot']['literals']] == \
        ['data-leagues']

    getters = {row['name']: row for row in root_rows if 'get_pathOf' in row['name']}
    assert len(getters) == 5, sorted(getters)
    got = {name: sorted(row['value'] for row in spec['literals'])
           for name, spec in getters.items()}
    assert got == {
        'PVP_Manager.get_pathOfDataUsers': ['/data-users', 'data-leagues'],
        'PVP_Manager.get_pathOfDataRanks': ['/data-ranks', 'data-leagues'],
        'PVP_Manager.get_pathOfDataPlayOfUsers': ['/data-play/data-play-users', 'data-leagues'],
        'PVP_Manager.get_pathOfDataPlayOfMachines':
            ['/data-play/data-play-machines', 'data-leagues'],
        'PVP_Manager.get_pathOfDataConfigs': ['/data-configs', 'data-leagues'],
    }, got
    for spec in getters.values():
        assert spec['calls'].get('String.Concat') == 1, spec['calls']

    all_literals = sorted({item['value'] for row in rows
                           for item in literals_of(firebase_methods()[row['rva']])})
    path_literals = [value for value in all_literals if is_path(value)]
    template_rows = templates(rows)
    assert len(all_literals) == 179, len(all_literals)
    assert len(path_literals) == 27, path_literals
    assert len(template_rows) == 19, len(template_rows)
    assert len([row for row in template_rows if row['kind'] == 'path']) == 16, \
        [row['value'] for row in template_rows if row['kind'] == 'message']
    assert all(row['contiguous'] for row in template_rows), [
        row['value'] for row in template_rows if not row['contiguous']]

    # 138 named `arena---datas/is-open` as an audit item; here both halves are cells.
    is_open = [item for row in rows for item in literals_of(firebase_methods()[row['rva']])
               if item['value'] == '/is-open']
    assert is_open and all(item['cell'] == 0x2ADE3A0 for item in is_open), is_open

    pools = machine_names(rows)
    assert len(pools) == 1, pools
    pool = pools[0]
    assert pool['count'] == 108, pool['count']
    assert 'Máy sấy' in pool['names'] and 'John Lùy' in pool['names'], pool['names']
    assert {'PVP_Machine_{0}_{1}_{2}', 'user#{0}{1}{2}'} <= {
        value for row in rows if row['rva'] == pool['rva'] for value in row['templates']
    }, 'the pool method must be the id-fabricating one'

    relocation_table = relocations()
    raw_meta = [dict(path=path, sha256=sha_file(path)) for path in FC.raw_paths()]
    blob = FC.load(next(path for path in FC.raw_paths() if 'arena-pvp' in path))
    return dict(
        schema=1,
        evidence='STATIC_ONLY_ORIGINAL_APK',
        note='Cell text is read through the APK\'s own relocation table plus the '
             'metadata string table; the numbers substituted into the templates at '
             'runtime and every served value are MODEL_NOT_MEASURED runtime.',
        provenance=dict(
            xapk_sha256=blob['xapk_sha256'],
            libil2cpp_sha256=blob['libil2cpp_sha256'],
            dump_sha256=blob['dump_sha256'],
            sources=[
                dict(path=RELOCATIONS, sha256=sha_file(RELOCATIONS),
                     role='cell VA -> pointer target VA (288733 relocation sites)'),
                dict(path=METADATA_INDEX, sha256=sha_file(METADATA_INDEX),
                     role='pointer target -> ScriptString value / ScriptMetadata name'),
                dict(path=DUMP, sha256=sha_file(DUMP),
                     role='RVA -> declaring class and signature for every callee'),
                *[dict(path=row['path'], sha256=row['sha256'],
                       role='pinned methods that load the cells') for row in raw_meta],
            ]),
        resolver=dict(
            relocations=len(relocation_table),
            script_strings=len(script_strings()),
            script_metadata=len(script_metadata()),
            rule='cell -> relocations[cell] -> ScriptString | ScriptMetadata; both '
                 'midpoints are kept in every row so the chain can be re-walked',
            method='two-table lookup, no disassembly of the data page and no .so',
        ),
        identity_crosscheck=dict(
            cell=CELL_181, cell_decimal=CELL_181,
            target=identity_cell['target'], target_decimal=identity_cell['target'],
            metadata=identity_cell['value'],
            application_cell=CELL_APPLICATION,
            application_metadata=identity_app['value'],
            note='report 181 identified 0x2ADB958 by the klass-cell idiom, the '
                 '`statics+0x0` read and the dump.cs field at 0x0; the relocation '
                 'table was not consulted there, and it names the same class — an '
                 'independent fifth test (and the neighbouring Application cell '
                 'resolves the same way 142 read it)',
        ),
        roots=root_rows,
        path_literals=[dict(value=value,
                            cells=sorted({item['cell'] for row in rows
                                          for item in literals_of(firebase_methods()[row['rva']])
                                          if item['value'] == value}),
                            users=sorted({row['rva'] for row in rows
                                          if value in row['path_literals']}))
                       for value in path_literals],
        templates=template_rows,
        machine_names=pools,
        census=dict(methods=len(rows), rows=rows,
                    path_literals=len(path_literals),
                    templates=len(template_rows),
                    path_templates=len([row for row in template_rows
                                        if row['kind'] == 'path']),
                    message_templates=[row['value'] for row in template_rows
                                       if row['kind'] == 'message'],
                    note_templates='a template with no `/` is a log line or an id '
                                    'builder, not a database path',
                    distinct_literals=len(all_literals),
                    note='`census.rows` keeps only the path-ish and template literals '
                         'per method; `string_cells` counts every resolved string cell '
                         'so the filtered view cannot be mistaken for the whole'),
        audit_corroboration=dict(
            item=53,
            claim='`data-leagues/data-configs` and `arena---datas/is-open` live in the '
                  'Firebase database',
            here=dict(arena_root=[item['value'] for item in arena_root['literals']],
                      is_open_cell=0x2ADE3A0,
                      configs=[item['value'] for item in getters[
                          'PVP_Manager.get_pathOfDataConfigs']['literals']]),
            verdict='corroborated statically; the item itself stays RUNTIME because '
                    'the payload served under those paths is not in the APK',
        ),
        not_decoded=[
            dict(item='the numbers substituted into each template',
                 blocking='season / rank / room / map come from save data and the '
                          'server at runtime — MODEL_NOT_MEASURED runtime'),
            dict(item='which root is live in a build',
                 blocking='`arena-test-datas` vs `arena---datas` vs `arena--datas` '
                          'depends on `Application.get_companyName()` on the device'),
            dict(item='the pairing between the name pool and the fabricated ids',
                 blocking='the pool and `PVP_Machine_{0}_{1}_{2}` / `user#{0}{1}{2}` '
                          'are in one method but the field each pool entry lands in is '
                          'not traced here'),
        ],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_firebase_paths.json.gz')
    args = parser.parse_args()
    payload = build_payload()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                                sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          methods=payload['census']['methods'],
                          path_literals=payload['census']['path_literals'],
                          templates=payload['census']['templates'],
                          literals=payload['census']['distinct_literals'],
                          identity=payload['identity_crosscheck']['metadata'])))


if __name__ == '__main__':
    main()
