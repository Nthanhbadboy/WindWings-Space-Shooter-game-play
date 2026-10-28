#!/usr/bin/env python3
"""Report 177. What `Board_PVP..ctor` actually builds: seven collections, six from the APK.

The audit carries items 30/39/40 as `POLICY` because the two `Board_PVP` blobs
(`rewardValues`, `rewardScales`) were believed to arrive with served data. The
constructor says otherwise: each array is allocated with a literal length of **6** and
filled by `RuntimeHelpers.InitializeArray` from a `<PrivateImplementationDetails>` static
field — the data ships inside the APK.

The constructor also builds a **seventh** collection the earlier field table did not list:
`+0x1b0` is a `List<object>`, built with a different helper pair and read by three
methods.

What this does *not* do is read the 24 bytes behind each cell. Binding cell 0x2ae0008 to
a named `PrivateImplementationDetails` field needs the metadata usage table, which is not
in this repository — `ia-resolved.json` has 17 method buckets and no `Board_PVP` one.
So the blocker moves from "data is served" to "data is in the APK but the cell→blob
binding is missing", which is a `PIN-RAW` problem, not a device problem.

Nothing is executed.
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

import buy_delegate as BD  # noqa: E402

ARTIFACT = 'datas/l2_535b0541_pvp_array_init.json.gz'

CLASS = 'Board_PVP'
CTOR = 19796420
INIT_ARRAY = 33927292      # RuntimeHelpers.InitializeArray(Array, RuntimeFieldHandle)
NEW_ARRAY = 17879196       # il2cpp_array_new(klass, length) - unnamed in the method table
LIST_OBJECT_CTOR = 29193868  # List<object>..ctor
BASE_CTOR = 19131072       # Board..ctor

STORES = [0x198, 0x1a0, 0x1a8, 0x1b0, 0x208, 0x210, 0x218]
FIELDS = {0x198: 'rewardIndexs', 0x1a0: 'rewardValues', 0x1a8: 'rewardScales',
          0x208: 'allBetCoinValues', 0x210: 'allBetGemValues', 0x218: 'allBetMedalValues'}

IA = 'reverse-engineering/il2cpp/ia-resolved.json'
DEFAULTS = 'reverse-engineering/il2cpp/field-defaults.json'


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def load_json(rel):
    raw = (ROOT / rel).read_bytes()
    try:
        return json.loads(raw)
    except UnicodeDecodeError:
        return json.loads(gzip.decompress(raw))


def ctor():
    slices = BD.slices()
    if (CLASS, CTOR) not in slices:
        raise SystemExit('Board_PVP..ctor not in the pinned slices')
    return slices[(CLASS, CTOR)]


def offset_of(text):
    """Operands print small offsets as decimal (`#8`) and the rest as hex (`#0x318`)."""
    if not text:
        return 0
    return int(text, 16) if text.startswith('0x') else int(text)


def call_target(op_str):
    """`bl #0x1234` -> 0x1234. The slices carry the target in the operand, not a field."""
    if '#' not in op_str:
        return None
    return int(op_str.split('#')[1], 16)


def build_rows(instructions):
    """One row per store into `this`, with the blob cell and length that fed it."""
    state, rows = {}, []
    blank = dict(length=None, length_rva=None, klass_cell=None, new_array=None,
                 init_array=None, list_ctor=None, spec=None, init_target=None,
                 list_ctor_target=None, new_array_target=None)
    pending = dict(blank)
    for insn in instructions:
        mnem, op, rva = insn['mnemonic'], insn.get('op_str') or '', insn['rva']
        if mnem == 'adrp' and ',' in op:
            reg, _, page = op.partition(', #')
            state[reg] = ('page', int(page, 16))
            continue
        if mnem in ('mov', 'movz') and op.startswith('w1, #'):
            value = int(op.split('#')[1], 16) if '0x' in op else int(op.split('#')[1])
            pending['length'] = value
            pending['length_rva'] = rva
            continue
        if mnem == 'bl':
            target = call_target(op)
            if target == INIT_ARRAY:
                pending['init_array'] = rva
                pending['init_target'] = target
            elif target == LIST_OBJECT_CTOR:
                pending['list_ctor'] = rva
                pending['list_ctor_target'] = target
            elif target == NEW_ARRAY:
                pending['new_array'] = rva
                pending['new_array_target'] = target
            continue
        load = re.match(r'^(x\d+), \[(x\d+)(?:, #(0x[0-9a-f]+|[0-9]+))?\]$', op)
        if mnem == 'ldr' and load:
            dst, base = load.group(1), load.group(2)
            offset = offset_of(load.group(3))
            tag = state.get(base)
            if tag and tag[0] == 'page':
                state[dst] = ('cell', tag[1], offset)
            elif tag and tag[0] in ('cell', 'deref') and offset == 0:
                state[dst] = ('deref', tag[1], tag[2])
            else:
                state.pop(dst, None)
            if dst == 'x1' and tag and tag[0] in ('cell', 'deref'):
                pending['spec'] = dict(page=tag[1], offset=tag[2],
                                       via='cell' if tag[0] == 'cell' else 'deref')
            if dst == 'x0' and tag and tag[0] in ('cell', 'deref'):
                pending['klass_cell'] = dict(page=tag[1], offset=tag[2])
            continue
        store = re.match(r'^x(\d+), \[x19, #(0x[0-9a-f]+)\]$', op)
        if mnem == 'str' and store:
            offset = int(store.group(2), 16)
            if offset in STORES:
                rows.append(dict(offset=offset, field=FIELDS.get(offset), store_rva=rva, op=op,
                                 kind='list' if pending['list_ctor'] else 'array',
                                 cell=pending['spec'], length=pending['length'],
                                 length_rva=pending['length_rva'],
                                 klass_cell=pending['klass_cell'],
                                 new_array_rva=pending['new_array'],
                                 init_rva=pending['init_array'],
                                 list_ctor_rva=pending['list_ctor'],
                                 init_target=pending['init_target'],
                                 list_ctor_target=pending['list_ctor_target'],
                                 new_array_target=pending['new_array_target']))
            pending = dict(blank)
    return rows


def holders():
    """Where `+0x1b0` is read, so the seventh collection is not anonymous."""
    out = []
    for (klass, _), payload in BD.slices().items():
        if not klass.startswith(CLASS):
            continue
        for insn in payload['instructions']:
            op = insn.get('op_str') or ''
            if '#0x1b0' in op and insn['mnemonic'] == 'ldr':
                out.append(dict(klass=klass, signature=payload['signature'][:80],
                                rva=insn['rva'], op=op))
    return out


def negatives():
    ia = load_json(IA)
    buckets = sorted(ia['methods']) if isinstance(ia.get('methods'), dict) else []
    defaults = load_json(DEFAULTS)
    pid = [key for key in defaults['fields'] if key.startswith('<PrivateImplementationDetails>')]
    three = [key for key in pid if len(defaults['fields'][key]['raw']) == 48]
    return dict(ia_buckets=len(buckets), ia_has_board_pvp=any('Board_PVP' in b for b in buckets),
                pid_blobs=len(pid), pid_blobs_24_bytes=len(three),
                defaults_count=defaults['count'])


def build_payload():
    method = ctor()
    rows = build_rows(method['instructions'])
    read = holders()
    neg = negatives()
    checks = []

    def check(name, passed, detail=None):
        checks.append(dict(name=name, passed=bool(passed), detail=detail))

    arrays = [row for row in rows if row['kind'] == 'array']
    lists = [row for row in rows if row['kind'] == 'list']
    check('seven-stores-into-this', [row['offset'] for row in rows] == STORES,
          [row['offset'] for row in rows])
    check('six-arrays-and-one-list', (len(arrays), len(lists)) == (6, 1),
          dict(arrays=len(arrays), lists=len(lists)))
    check('every-array-has-length-six', {row['length'] for row in arrays} == {6},
          sorted({row['length'] for row in arrays}))
    check('every-array-goes-through-InitializeArray',
          all(row['init_target'] == INIT_ARRAY
              and BD.name(row['init_target'])['class_name'] == 'RuntimeHelpers'
              for row in arrays),
          [row['init_target'] for row in arrays])
    check('the-six-cells-are-consecutive-pairs',
          [row['cell']['offset'] for row in arrays] ==
          [0x8, 0x10, 0x18, 0x30, 0x38, 0x40],
          [row['cell']['offset'] for row in arrays])
    check('the-third-array-uses-a-different-element-class',
          [row['klass_cell']['offset'] for row in arrays].count(0x350) == 1
          and arrays[2]['klass_cell']['offset'] == 0x350,
          [row['klass_cell']['offset'] for row in arrays])
    check('the-list-is-a-List-of-object',
          lists[0]['list_ctor_target'] == LIST_OBJECT_CTOR
          and BD.name(LIST_OBJECT_CTOR)['class_name'] == 'List<object>..ctor',
          lists[0]['list_ctor_target'])
    check('the-seventh-collection-is-read-by-nameable-methods',
          {19800320, 19811460} <= {row['rva'] for row in read}
          and all(row['klass'].startswith(CLASS) for row in read),
          sorted({row['rva'] for row in read}))
    check('the-ctor-chains-to-Board-dot-ctor',
          any(insn['mnemonic'] in ('b', 'bl')
              and call_target(insn.get('op_str') or '') == BASE_CTOR
              for insn in method['instructions']),
          BASE_CTOR)
    check('the-six-named-fields-are-the-six-arrays',
          [row['field'] for row in arrays] ==
          ['rewardIndexs', 'rewardValues', 'rewardScales',
           'allBetCoinValues', 'allBetGemValues', 'allBetMedalValues'],
          [row['field'] for row in arrays])
    check('the-usage-table-is-still-missing', neg['ia_has_board_pvp'] is False,
          neg['ia_buckets'])
    check('the-blob-corpus-is-counted', neg['pid_blobs'] > 900, neg['pid_blobs'])

    return {
        'schema': 'l2/535b0541/pvp-array-init/1',
        'evidence': 'STATIC_ONLY_ORIGINAL_APK',
        'note': 'The seven collections of Board_PVP are built in the constructor. Six are '
                '24-byte blobs that ship inside the APK, so the "served payload" reading '
                'of items 30/39/40 is wrong; what is missing is the cell->blob binding, '
                'not the data.',
        'constructor': dict(klass=CLASS, rva=CTOR, size=method['size'],
                            instructions=len(method['instructions']),
                            chained_to=BASE_CTOR),
        'collections': rows,
        'field_table': [dict(offset=offset, field=name) for offset, name in FIELDS.items()] +
                       [dict(offset=0x1b0, field='(unnamed List<object>)')],
        'readers_of_1b0': read,
        'negatives': neg,
        'limits': [
            'the cell->blob binding needs the metadata usage table, which is not in this '
            'repository; `ia-resolved.json` has no Board_PVP bucket.',
            'the 24-byte values themselves are therefore still NOT_BOUND, even though the '
            'data provably ships inside the APK.',
            'what a device renders from these arrays stays MODEL_NOT_MEASURED runtime.',
        ],
        'provenance': dict(
            xapk_sha256='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e',
            inputs=[dict(path=IA, sha256=sha_file(IA)),
                    dict(path=DEFAULTS, sha256=sha_file(DEFAULTS))]),
        'checks': checks,
    }


def build(output=None):
    payload = build_payload()
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode('utf-8')
    packed = gzip.compress(blob, mtime=0)
    if output:
        (ROOT / output).write_bytes(packed)
    return payload, packed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=ARTIFACT)
    args = parser.parse_args()
    payload, packed = build(args.output)
    failed = [row for row in payload['checks'] if not row['passed']]
    print(json.dumps(dict(bytes=len(packed),
                          sha256=hashlib.sha256(packed).hexdigest(),
                          collections=len(payload['collections']),
                          checks=len(payload['checks']), failing=len(failed))))
    if failed:
        print(json.dumps([row['name'] for row in failed]))
        raise SystemExit('gate failed')


if __name__ == '__main__':
    main()
