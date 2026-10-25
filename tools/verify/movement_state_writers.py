"""Conservative linear store hints + manually checked movement state contracts.

Not a CFG emulator, whole-program writer proof or Unity replay. Scan only the
preserved Enemy_Movement class; never treat stack offsets as object fields.
"""
from dataclasses import dataclass, replace
import gzip
import hashlib
import json
from pathlib import Path
import re
from early_ui_native import section

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'reverse-engineering/raw'
FIELDS = {0x4c: 'typeMove', 0x50: 'path', 0x58: 'dstTravelled', 0x5c: 'moving', 0xd0: 'movein'}


def store_hints(asm):
    aliases, constants, rows = {'x0': 0}, {'wzr': 0, 'xzr': 0}, []
    for line in asm.splitlines():
        match = re.search(r'(0x[0-9a-f]+):\s+(\S+)\s*(.*)', line)
        if not match:
            continue
        address, op, args = match.groups()
        store = re.fullmatch(r'([wx]\d+|[wx]zr), \[(x\d+), #(0x[0-9a-f]+|\d+)\]', args)
        if op in ('str', 'strb') and store and store[2] in aliases:
            offset = aliases[store[2]] + int(store[3], 0)
            if offset in FIELDS:
                rows.append(dict(address=address, instruction=op+' '+args, field=FIELDS[offset],
                                 value=constants.get(store[1]), value_known=store[1] in constants))
        if op in ('bl', 'blr'):
            for i in range(19):
                aliases.pop('x'+str(i), None)
                constants.pop('w'+str(i), None)
                constants.pop('x'+str(i), None)
            continue
        mov = re.fullmatch(r'(x\d+), (x\d+)', args)
        literal = re.fullmatch(r'([wx]\d+), #(-?0x[0-9a-f]+|-?\d+)', args)
        if op == 'mov' and mov:
            value = aliases.get(mov[2])
            aliases.pop(mov[1], None)
            constants.pop(mov[1], None)
            constants.pop('w'+mov[1][1:], None)
            if value is not None:
                aliases[mov[1]] = value
        elif op == 'mov' and literal:
            constants[literal[1]] = int(literal[2], 0)
            aliases.pop('x'+literal[1][1:], None)
            constants.pop(('w' if literal[1].startswith('x') else 'x')+literal[1][1:], None)
        elif op not in ('str', 'strb', 'stur', 'stp', 'cmp', 'fcmp', 'tst', 'ret', 'cbz', 'cbnz', 'tbz', 'tbnz') and not op.startswith('b'):
            dest = args.split(',', 1)[0]
            aliases.pop(dest, None)
            if re.fullmatch(r'[wx]\d+', dest):
                aliases.pop('x'+dest[1:], None)
                constants.pop('w'+dest[1:], None)
                constants.pop('x'+dest[1:], None)
            constants.pop(dest, None)
    return rows


@dataclass(frozen=True)
class State:
    type_move: int = 0
    path: str | None = None
    waypoints: tuple = ()
    distance: float = 0
    moving: bool = False
    movein: bool = False


def contract(state, operation, payload=None):
    """Restricted state-field effects, not complete method/activation/lifecycle execution."""
    if operation in ('enable', 'airfree_set_position', 'set_angle'):
        return state
    if operation == 'appeared':
        return replace(state, moving=True)
    if operation == 'set_position_and_angle':
        return replace(state, moving=False, movein=False)
    if operation == 'set_path_valid':
        if payload is None:
            raise ValueError('only valid-path successful contract supported')
        return replace(state, type_move=0, path=payload, distance=0)
    if operation == 'set_waypoints':
        if payload is None:
            raise ValueError('null-waypoint exception route not modeled')
        result = replace(state, type_move=1, distance=0)
        # Native logs/returns for length<2, after the two writes above.
        return replace(result, waypoints=tuple(payload)) if len(payload) >= 2 else result
    if operation == 'stop':
        return replace(state, moving=False)
    if operation == 'start':
        return replace(state, moving=True)
    raise ValueError('unsupported operation')


def build():
    asm_path = RAW / 'ui-audit/extra-native/Enemy_Movement.asm.txt'
    inv_path = RAW / 'ui-audit/extra-native/Enemy_Movement.json'
    inventory = json.loads(inv_path.read_text())['methods']
    methods = []
    for inv in inventory:
        assert not inv['size_capped']
        text = section(asm_path.read_text(), inv['method'])
        methods.append(dict(method=inv['method'], inventory=inv, asm=text, store_hints=store_hints(text)))
    texts = {m['method']: m['asm'] for m in methods}
    def has(name, *parts):
        return all(p in texts[name] for p in parts)
    completion_path = RAW / 'early-waves/movement-completion.json.gz'
    completion = json.load(gzip.open(completion_path, 'rt'))
    airfree = [dict(resource_key=w['resource_key'], **r) for w in completion['waves'] for r in w['rows'] if r['spawner'] == 'AirFree_Spawner']
    checks = dict(
        four_type_writers={m['method'] for m in methods for s in m['store_hints'] if s['field'] == 'typeMove'} == {'SetPathFollower', 'SetWaypoints', 'SetMoveLinearly', 'RocketResumeMove'},
        one_path_writer={m['method'] for m in methods for s in m['store_hints'] if s['field'] == 'path'} == {'SetPathFollower'},
        enable_not_reset='0x1586074: str      s0, [x19, #0x48]' in texts['OnEnable'] and not store_hints(texts['OnEnable']),
        separate_position_not_reset=not store_hints(texts['SetPosition']),
        combined_setter_stops=has('SetPositionAndAngle', '0x1584164: strb     wzr, [x0, #0xd0]', '0x1584168: strb     wzr, [x0, #0x5c]'),
        short_waypoints_changes_mode_before_log_return=has('SetWaypoints', '0x1583f48: str      w8, [x19, #0x4c]', '0x1583f5c: b.ge     #0x1583f84', '0x1583f80: b        #0x15b77b0', '0x1583f84: str      x20, [x19, #0x60]'),
        path_writer_only_after_get_path=has('SetPathFollower', '0x1583e74: bl       #0x143bd84', '0x1583e78: str      x0, [x19, #0x50]'),
        stop_does_not_clear_path=has('StopMove', '0x158474c: strb     wzr, [x0, #0x5c]') and 'path' not in [s['field'] for s in store_hints(texts['StopMove'])],
        sole_early_airfree_bb=len(airfree) == 1 and airfree[0]['enemy_roots'] == [dict(serialized_file='resources.assets', path_id=185704)],
    )
    sources = []
    extra = RAW / 'il2cpp-consts/Enemy_Sub.asm.txt'
    for path in (asm_path, inv_path, completion_path, extra):
        data = path.read_bytes()
        if path.suffix == '.gz':
            data = gzip.decompress(data)
        sources.append(dict(path=str(path.relative_to(ROOT)), sha256=hashlib.sha256(data).hexdigest(), hash_bytes='gzip-decompressed' if path.suffix == '.gz' else 'file'))
    return dict(status='PROVISIONAL_CLASS_LOCAL_STORE_HINTS_NOT_RUNTIME_WRITER_CLOSURE',
                sources=sources, methods=methods, checks=checks, early_airfree=airfree,
                sub_setters={n: section(extra.read_text(), n) for n in ('SetPosition', 'SetAngle', 'SetPositionAndAngle', 'SetPathFollower', 'SetWaypoints')},
                limits=['Linear scan hints are not control-flow proof', 'Only preserved Enemy_Movement class scanned, not all native code', 'No pool instance history or live state observation', 'Successful field contracts exclude activation callbacks and external mutation'])


if __name__ == '__main__':
    result = build()
    assert all(result['checks'].values()), result['checks']
    path = RAW / 'balloon-animation/movement-state-writers.json.gz'
    with gzip.GzipFile(filename=str(path), mode='wb', mtime=0) as f:
        f.write(json.dumps(result, indent=2).encode())
    print(len(result['methods']), 'methods;', len(result['checks']), 'checks')
