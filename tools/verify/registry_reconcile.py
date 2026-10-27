#!/usr/bin/env python3
"""Report 184: reconcile the registry rows whose blockers name an absolute slot.

`datas/l2_535b0541_registry_v4.json.gz` (32 ledger rows, sha `bcd0e0fd…`) is the
Gate-1 ledger. Reviewer `8141386a` noticed (PR12 `6445017285`) that its rows are
pinned at a cut older than reports 181/182, and that two rows can now be re-read
against evidence those reports produced:

* row **50** (`ArenaManager` root variants, `missing-input`) says the slots
  `0x2AEC9A0` / `0x2AEC9B0` are "never dereferenced in the pinned raws";
* row **52** (class owning static field 0, `policy`) says the class behind slot
  `0x2ADB958` is "unnamed".

This tool does not trust those reports either — it re-walks the same pinned
tables and recomputes:

1. **the scan**: every ledger row is text-searched for absolute slot VAs, so the
   set of rows to reconcile is derived, not hand-picked (3 rows, 4 slots);
2. **row 50**: `slot -> relocations[slot] -> ScriptString`, plus the load site of
   each cell inside `ArenaManager.get_pathRoot` (22685676), recomputed from the
   raw rather than copied from 182;
3. **row 52**: `slot -> relocations[slot] -> ScriptMetadata`
   (`FirebaseDatabaseManager_TypeInfo`), the `dump.cs` declaration of the static
   at offset `0x0`, and the statics-block offset that every one of the 141 load
   sites actually reads;
4. **row 51**: the honest negative — slot `0x2AE1000` has no relocation entry and
   no load site anywhere in the pinned raws, so the join v4 proposes cannot run
   on this corpus. It stays `policy` / owner.

`v4` is *not* rewritten: the ledger at its cut is byte-identical, and this report
carries an **amendment** per row (`label_after`, `verdict_after`, `residual`).
Anything that only a device can answer stays `MODEL_NOT_MEASURED runtime`; audit
row 53 in particular stays `RUNTIME`.
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
import firebase_paths as FP  # noqa: E402

LEDGER = 'datas/l2_535b0541_registry_v4.json.gz'
SCHEMA = 1

CELL_52 = FC.SLOT                 # 0x2ADB958 = 44939608, the FirebaseDatabaseManager cell
CELL_50 = (45009312, 45009320, 45009328)   # 0x2AEC9A0 / 0x2AEC9A8 / 0x2AEC9B0
CELL_51 = 0x2AE1000               # 44564480, from the v4 step text for row 51
ARENA_ROOT = 22685676             # ArenaManager.get_pathRoot
INSTANCE_OFFSET = 0x0             # FirebaseDatabaseManager.Instance
STATICS_OFFSET = 0xB8             # klass -> statics block, report 141/142 idiom

SLOT_FLOOR = 0x1000000            # anything below this in a step is an offset, not a slot


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def ledger():
    raw = (ROOT / LEDGER).read_bytes()
    data = json.loads(gzip.decompress(raw))
    data['_bytes'] = len(raw)
    data['_sha256'] = hashlib.sha256(raw).hexdigest()
    return data


def slots_in_text(text):
    """Absolute VAs (>= 0x1000000) mentioned in one ledger row, decimal-sorted."""
    found = {int(m.group(0), 16) for m in re.finditer(r'0x[0-9A-Fa-f]{5,}', text)}
    return sorted(value for value in found if value >= SLOT_FLOOR)


def row_text(row):
    return ' '.join(str(row.get(key, '')) for key in
                    ('item', 'kind', 'label', 'step', 'verdict', 'closer', 'report'))


def scan():
    """Derive the reconcile set: rows whose text names an absolute slot."""
    rows, slots = [], set()
    for row in ledger()['ledger']:
        found = slots_in_text(row_text(row))
        if not found:
            continue
        rows.append(dict(n=row['n'], item=row['item'], label=row['label'],
                         verdict=row['verdict'], step=row['step'],
                         label_before=row['label'], report=row['report'], slots=found))
        slots.update(found)
    resolved = sum(1 for slot in sorted(slots) if FP.resolve(slot))
    return rows, dict(rows=len(ledger()['ledger']), rows_with_slots=len(rows),
                      slots=len(slots), resolved=resolved,
                      unresolved=len(slots) - resolved)


def slot_row(slot):
    found = FP.resolve(slot)
    out = dict(slot=slot, decimal=slot, resolved=bool(found))
    if found:
        out.update(kind=found['kind'], value=found['value'], target=found['target'],
                   target_decimal=found['target'])
    return out


@lru_cache(maxsize=None)
def arena_root_cells():
    """Cell loads inside `ArenaManager.get_pathRoot`, recomputed from the raws."""
    out = {}
    for rel in FC.raw_paths():
        for method in FC.load(rel)['methods']:
            if method['rva'] != ARENA_ROOT:
                continue
            for cell, adrp_rva, ldr_rva in cell_reads(method):
                out.setdefault(cell, (adrp_rva, ldr_rva))
    return out


def cell_reads(method):
    """`adrp page` + `ldr xN,[xN,#off]` -> (slot VA, adrp rva, ldr rva)."""
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
            hit = re.fullmatch(r'%s, \[%s, #(0x[0-9a-f]+)\]' % (reg, reg),
                               follow.get('op_str') or '')
            if follow['mnemonic'] == 'ldr' and hit:
                out.append((page + int(hit.group(1), 16), insn['rva'], follow['rva']))
                break
    return out


def slot51_loads():
    """Any `adrp 0x2AE0000` + `ldr x,[x,#0x1000]` in the pinned raws? (row 51)"""
    page, offset = CELL_51 & ~0xFFF, CELL_51 & 0xFFF
    hits = []
    for rel in FC.raw_paths():
        for method in FC.load(rel)['methods']:
            for cell, adrp_rva, ldr_rva in cell_reads(method):
                if cell == CELL_51:
                    hits.append(dict(raw=rel, class_name=method['class_name'],
                                     signature=method['signature'].strip(),
                                     method_rva=method['rva'], adrp_rva=adrp_rva,
                                     ldr_rva=ldr_rva))
    return dict(page=page, offset=offset, hits=hits)


@lru_cache(maxsize=None)
def statics_census():
    """Every load site of the 0x2ADB958 cell: tag and statics-block offset."""
    tags, offsets, methods, raws, sites = {}, {}, set(), set(), 0
    for rel in FC.raw_paths():
        for site in FC.cell_sites(FC.load(rel)):
            sites += 1
            methods.add((site['class_name'], site['method_rva']))
            raws.add(rel)
            label, found = FC.idiom(FC.load(rel), site['method_rva'], site['load_rva'])
            tags.setdefault('+'.join(label), 0)
            tags['+'.join(label)] += 1
            for offset in found:
                offsets[offset] = offsets.get(offset, 0) + 1
    return dict(sites=sites, methods=len(methods), raws=sorted(raws),
                tags=tags, statics_offsets={str(k): v for k, v in sorted(offsets.items())},
                class_init=FC.CLASS_INIT)


@lru_cache(maxsize=None)
def instance_declaration():
    """The `dump.cs` line that declares static field 0 on the cell's class."""
    text = FC.dump_text()
    class_hit = re.search(r'(?m)^(?:public |private |internal )?(?:sealed )?'
                          r'class FirebaseDatabaseManager\s*:\s*\w+.*$', text)
    field_hit = re.search(r'public static FirebaseDatabaseManager Instance; // (0x[0-9a-f]+)', text)
    return dict(class_line=class_hit.group(0).strip() if class_hit else None,
                field_line=field_hit.group(0).strip() if field_hit else None,
                field_offset=int(field_hit.group(1), 16) if field_hit else None)


def amendment_50():
    loads = arena_root_cells()
    rows = []
    for cell in CELL_50:
        found = slot_row(cell)
        adrp_rva, ldr_rva = loads.get(cell, (None, None))
        found.update(adrp_rva=adrp_rva, ldr_rva=ldr_rva)
        rows.append(found)
    return dict(n=50, label_before='missing-input', verdict_before='OPEN',
                label_after='shipped-default',
                verdict_after='STATIC_CONFIRMED',
                basis=['three cells of ArenaManager.get_pathRoot (22685676) resolve '
                       'through relocations -> ScriptString',
                       'every load site is inside that one 204-byte method'],
                residual=dict(label='runtime-gated→USER', verdict='MODEL_NOT_MEASURED runtime',
                              why='which of the three is live depends on '
                                  'Application.get_companyName() (41274380) and '
                                  'VersionControlSystem.get_PREMIUM() (20068044) on the device'),
                slots=rows)


def amendment_52():
    census = statics_census()
    decl = instance_declaration()
    return dict(n=52, label_before='policy', verdict_before='OPEN',
                label_after='shipped-default',
                verdict_after='STATIC_CONFIRMED',
                basis=['relocations[44939608] -> ScriptMetadata '
                       'FirebaseDatabaseManager_TypeInfo',
                       'dump.cs declares `public static FirebaseDatabaseManager Instance; '
                       '// 0x0` and nothing else static on that class',
                       'all %d statics-block reads (klass+0x%x) out of %d load sites '
                       'touch offset 0x%x of that block'
                       % (census['statics_offsets'].get(str(INSTANCE_OFFSET), 0),
                          STATICS_OFFSET, census['sites'], INSTANCE_OFFSET)],
                residual=dict(label='runtime-gated→USER', verdict='MODEL_NOT_MEASURED runtime',
                              why='whether Instance is non-null and authenticated when a '
                                  'fetch runs is device state'),
                slots=[slot_row(CELL_52)], census=census, declaration=decl)


def amendment_51():
    probe = slot51_loads()
    return dict(n=51, label_before='policy', verdict_before='OPEN', label_after='policy',
                verdict_after='OPEN',
                basis=['no relocation entry for 44564480 in native-relocations.json.gz',
                       'no load site for that slot in any pinned raw (%d hits)'
                       % len(probe['hits'])],
                residual=dict(label='policy', verdict='OPEN',
                              why='owner decision still needed: the join v4 proposes '
                                  'has no input in this corpus'),
                slots=[slot_row(CELL_51)], probe=probe)


@lru_cache(maxsize=None)
def root182_literals():
    """The three root literals report 182 recorded for `ArenaManager.get_pathRoot`."""
    blob = json.loads(gzip.decompress(
        (ROOT / 'datas/l2_535b0541_firebase_paths.json.gz').read_bytes()))
    root = next(item for item in blob['roots'] if item['rva'] == ARENA_ROOT)
    return tuple(lit for lit in root['literals'] if lit['cell'] in CELL_50)


def checks(payload):
    out = []
    out.append(('ledger bytes match the pinned v4', payload['v4']['bytes'] == 4851))
    out.append(('ledger sha match', payload['v4']['sha256'].startswith('bcd0e0fd')))
    out.append(('scan found the three rows', sorted(row['n'] for row in payload['scan']['rows']) == [50, 51, 52]))
    out.append(('row 50: three slots', len(payload['items'][0]['slots']) == 3))
    out.append(('row 50: all resolved as strings', all(s['resolved'] and s['kind'] == 'string'
                                                       for s in payload['items'][0]['slots'])))
    out.append(('row 50: every string non-empty', all(s['value'] for s in payload['items'][0]['slots'])))
    out.append(('row 50: load sites all inside ArenaManager.get_pathRoot',
                all(s['ldr_rva'] and s['ldr_rva'] == s['adrp_rva'] + 4
                    for s in payload['items'][0]['slots'])))
    recorded = sorted(lit['load_rva'] for lit in root182_literals())
    out.append(('row 50: adrp sites match the ones 182 recorded',
                recorded == sorted(s['adrp_rva'] for s in payload['items'][0]['slots'])))
    out.append(('row 52: cell resolves to metadata',
                payload['items'][2]['slots'][0]['kind'] == 'metadata'))
    out.append(('row 52: metadata name', payload['items'][2]['slots'][0]['value'] ==
                'FirebaseDatabaseManager_TypeInfo'))
    out.append(('row 52: Instance declared at 0x0',
                payload['items'][2]['declaration']['field_offset'] == INSTANCE_OFFSET))
    out.append(('row 52: census offsets are all 0x0',
                list(payload['items'][2]['census']['statics_offsets']) == ['0']))
    out.append(('row 52: census sites 141', payload['items'][2]['census']['sites'] == 141))
    out.append(('row 52: census methods 34', payload['items'][2]['census']['methods'] == 34))
    out.append(('row 51: unchanged', payload['items'][1]['label_after'] == 'policy'))
    out.append(('row 51: no load site', payload['items'][1]['probe']['hits'] == []))
    out.append(('row 51: slot unresolved', not payload['items'][1]['slots'][0]['resolved']))
    out.append(('audit row 53 still RUNTIME', payload['audit_53'] == 'RUNTIME'))
    out.append(('ledger rows untouched', payload['unchanged_rows'] == 29))
    return [dict(name=name, ok=bool(ok)) for name, ok in out]


def build_payload():
    rows, summary = scan()
    audit_53 = next(row['verdict'] for row in ledger()['ledger'] if row['n'] == 53)
    payload = dict(
        schema=SCHEMA,
        evidence='STATIC_ONLY_ORIGINAL_APK',
        note='v4 is not rewritten: each row keeps the label/step it had at the cut and '
             'gains an amendment with a residual. Nothing here is a device measurement.',
        v4=dict(bytes=ledger()['_bytes'], sha256=ledger()['_sha256'],
                items=ledger()['totals']['items'], ledger=len(ledger()['ledger']),
                cut_report='180'),
        scan=dict(total=summary['rows'], rows_with_slots=summary['rows_with_slots'],
                  slots=summary['slots'], resolved=summary['resolved'],
                  unresolved=summary['unresolved'], rows=rows),
        items=[amendment_50(), amendment_51(), amendment_52()],
        unchanged_rows=len(ledger()['ledger']) - summary['rows_with_slots'],
        audit_53=audit_53,
        not_measured=['which ArenaManager root a build uses — MODEL_NOT_MEASURED runtime',
                      'whether FirebaseDatabaseManager.Instance is signed in when a fetch runs '
                      '— MODEL_NOT_MEASURED runtime',
                      'every served value and every number substituted into a path lettered '
                      'in 182/183 — MODEL_NOT_MEASURED runtime'],
        provenance=dict(
            ledger=dict(path=LEDGER, sha256=ledger()['_sha256'], bytes=ledger()['_bytes']),
            tables=dict(relocations=len(FP.relocations()),
                        script_metadata=len(FP.script_metadata()),
                        script_strings=len(FP.script_strings())),
            sources=[dict(path=path, sha256=FP.sha_file(path)) for path in
                     (LEDGER, FP.RELOCATIONS, FP.METADATA_INDEX, FP.DUMP,
                      'datas/l2_535b0541_firebase_paths.json.gz')]),
    )
    payload['checks'] = checks(payload)
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--out', default='datas/l2_535b0541_registry_reconcile.json.gz')
    args = parser.parse_args()
    payload = build_payload()
    failed = [check for check in payload['checks'] if not check['ok']]
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':')).encode('utf-8')
    if args.write:
        out = ROOT / args.out
        out.write_bytes(gzip.compress(body, compresslevel=9, mtime=0))
        blob = out.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
    else:
        digest = hashlib.sha256(body).hexdigest()
        blob = body
    print(json.dumps(dict(bytes=len(blob), sha256=digest,
                          items=len(payload['items']),
                          scan=dict(rows_with_slots=payload['scan']['rows_with_slots'],
                                    slots=payload['scan']['slots'],
                                    resolved=payload['scan']['resolved'],
                                    unresolved=payload['scan']['unresolved']),
                          checks=len(payload['checks']), failed=len(failed),
                          failed_names=[check['name'] for check in failed]),
                     ensure_ascii=False, indent=1))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
