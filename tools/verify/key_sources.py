#!/usr/bin/env python3
"""Where the quest keys come from, how they are stored, and what caps them.

STATIC only. Reports 129-131 fixed the *cost* side (three boxes, 30 keys each,
6/20/100 gems per missing key). This report answers the *supply* side from four
pinned scans, because no single scoped extraction shows both "who calls the
accessors" (a whole-`.text` branch scan) and "what the callee does" (method
bodies plus two read-only jump tables):

* `call-sites-535b0541` - every `bl`/`b` in `.text` that targets one of the six
  `GameDatas` KeyCount accessors -> 35 caller methods in 31 classes;
* `key-jump-535b0541` - `TimeFreeRewardPack.SaveDataReward` plus its dispatch
  table at 0x779C4A -> pack value index 16/17/18 reaches KeyCount0/1/2;
* `key-grant-535b0541` - `Board_Quest`, `Board_PVP`, `Bonus_Quest`, `GameDatas`
  -> the two direct grants, the negative clamp, the lazy PlayerPrefs load, and
  the anti-cheat cap table;
* `pvp-dispatch-535b0541` - the `GiftType` dispatch table at 0x779DF0 used by
  `Board_PVP.OnClickHunterCollect`.

Nothing is executed. Amounts a player actually receives depend on the pack data
and on which PvP stage they collect (MODEL_NOT_MEASURED runtime).
"""
import argparse
import bisect
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CALLS = 'reverse-engineering/raw/call-sites-535b0541/calls.json.gz'
JUMP = 'reverse-engineering/raw/key-jump-535b0541/native.json.gz'
GRANT = 'reverse-engineering/raw/key-grant-535b0541/native.json.gz'
PVP = 'reverse-engineering/raw/pvp-dispatch-535b0541/native.json.gz'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'
LITERALS = 'reverse-engineering/il2cpp/stringliteral.json'

GETTERS = {'KeyCount0': 20070740, 'KeyCount1': 20071068, 'KeyCount2': 20071396}
SETTERS = {'KeyCount0': 20070940, 'KeyCount1': 20071268, 'KeyCount2': 20071596}
STATIC_OFFSET = {'KeyCount0': 0x50, 'KeyCount1': 0x54, 'KeyCount2': 0x58}

PACK_TABLE = dict(va=0x779C4A, length=22, base_pad=0x124CA98)
PVP_TABLE = dict(va=0x779DF0, length=10, base_pad=0x12E0518)

# GiftType (dump.cs TypeDefIndex 1245) - reward ids reused by the PvP stages
GIFT_TYPES = {0: 'Gcoins', 1: 'Gems', 6: 'Overdrive', 7: 'Energy', 13: 'DroneExp',
              14: 'DroneCards', 15: 'PlayerCards', 16: 'Key0', 17: 'Key1', 18: 'Key2',
              19: 'WingCoins', 20: 'VipPoint', 21: 'TimeRewards', 23: 'PVPMedal'}


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


def dump_lines():
    return gzip.decompress((ROOT / DUMP).read_bytes()).decode().split('\n')


def dump_names(lines):
    """rva -> declaration line (the declaration sits one line below the RVA)."""
    out = {}
    for index, line in enumerate(lines):
        rva = re.match(r'\s*// RVA: 0x([0-9A-F]+)', line)
        if rva and index + 1 < len(lines):
            out[int(rva.group(1), 16)] = lines[index + 1].strip()
    return out


def field_offsets(lines, class_name):
    """field -> offset for one class (instance fields of that class only)."""
    for index, line in enumerate(lines):
        if re.search(r'(class|struct) %s(\s*:|\s+//)' % re.escape(class_name), line) \
                and '// TypeDefIndex:' in line:
            out = {}
            depth = 0
            for row in lines[index + 1:]:
                if re.search(r'^\s*\}', row):
                    depth += 1
                    if depth:
                        break
                match = re.search(r'\b(\w+); // 0x([0-9A-F]+)$', row)
                if match:
                    out[match.group(1)] = int(match.group(2), 16)
            return out
    raise AssertionError(f'class {class_name} not in dump.cs')


def enum_values(lines, name):
    out, inside = {}, False
    for line in lines:
        if re.search(r'enum %s\b' % re.escape(name), line):
            inside = True
            continue
        if inside:
            match = re.search(r'public const \w+ (\w+) = (-?\d+);', line)
            if match:
                out[int(match.group(2))] = match.group(1)
            if line.strip() == '}':
                return out
    raise AssertionError(f'enum {name} not in dump.cs')


def short(signature):
    """'public static int get_KeyCount0() { }' -> 'get_KeyCount0'."""
    head = signature.split('(')[0].replace('public static ', '').replace('private ', '') \
        .replace('internal ', '')
    return head.split()[-1]


def call_target(insn):
    return int(insn['op_str'].lstrip('#'), 0)


def decode_imm_pair(insns, stop, reg):
    """(lo, hi) of `mov wR,#lo` + `movk wR,#hi,lsl #16` searched backwards."""
    hi = lo = None
    for insn in reversed(insns[max(0, stop - 12):stop]):
        if hi is None and insn['mnemonic'] == 'movk' and insn['op_str'].startswith(reg + ','):
            hi = int(re.search(r'#(0x[0-9a-f]+|\d+)', insn['op_str']).group(1), 0)
        elif lo is None and insn['mnemonic'] == 'mov' and insn['op_str'].startswith(reg + ','):
            value = re.search(r'#(0x[0-9a-f]+|\d+)', insn['op_str'])
            lo = int(value.group(1), 0) if value else (0 if 'wzr' in insn['op_str'] else None)
            if lo is not None:
                break
    return lo, hi


def accessor_semantics(names, by_rva):
    """negative clamp + lazy load from PlayerPrefs + immediate write-back."""
    out = {}
    for key, rva in GETTERS.items():
        getter = by_rva[rva]
        insns = getter['instructions']
        store = [i for i in insns if i['mnemonic'] == 'str'
                 and i['op_str'].endswith(f'#0x{STATIC_OFFSET[key]:x}]')]
        sentinel = [i for i in insns if i['mnemonic'] == 'cmn' and i['op_str'] == 'w9, #1']
        if not sentinel:
            raise AssertionError(f'{key} getter has no -1 sentinel check')
        loads = [i for i in insns if i['mnemonic'] == 'bl'
                 and names.get(call_target(i), '').startswith('public static int GetInt(')]
        if not loads:
            raise AssertionError(f'{key} getter does not fall back to PlayerPrefs.GetInt')
        setter = by_rva[SETTERS[key]]
        clamp = [i for i in setter['instructions'] if i['mnemonic'] == 'bic'
                 and i['op_str'] == 'w19, w19, w19, asr #31']
        writes = [i for i in setter['instructions'] if i['mnemonic'] in ('bl', 'b')
                  and names.get(call_target(i), '').startswith('public static void SetInt(')]
        if not clamp or not writes:
            raise AssertionError(f'{key} setter is not clamp-then-save')
        out[key] = dict(
            static_offset=STATIC_OFFSET[key],
            getter_rva=rva, setter_rva=SETTERS[key],
            unloaded_sentinel=-1,
            lazy_load='PlayerPrefs.GetInt(key, 0) when the cached int is -1',
            negative_clamp='bic w19, w19, w19, asr #31 (max(value, 0))',
            write_through='PlayerPrefs.SetInt(key, value) on every set',
            getter_size=getter['size'], setter_size=setter['size'],
            store_offsets=[i['op_str'] for i in store])
    return out


def cheat_caps(names, by_rva, key):
    """the `IsHasCheatResources` clamp table, including the KeyCount caps."""
    rva = 20068376
    insns = by_rva[rva]['instructions']
    out = []
    for index, insn in enumerate(insns):
        if insn['mnemonic'] != 'bl':
            continue
        name = names.get(call_target(insn), '')
        if not name.startswith('public static int get_'):
            continue
        resource = name.split('get_')[1].split('(')[0]
        cmp_insn = next((i for i in insns[index + 1:index + 14]
                         if i['mnemonic'] == 'cmp' and i['op_str'].startswith('w0, ')), None)
        if cmp_insn is None:
            continue
        reg = cmp_insn['op_str'].split(', ')[1]
        row = dict(resource=resource, getter_rva=call_target(insn),
                   threshold=None, threshold_source='immediate', reset_to=None)
        if reg.startswith('w') and reg != 'w0':
            lo, hi = decode_imm_pair(insns, insns.index(cmp_insn), reg)
            if hi is None:
                row['threshold'] = lo if lo is not None else 0
            else:
                row['threshold'] = (lo or 0) | (hi << 16)
        else:
            prior = next((i for i in reversed(insns[:index])
                          if i['mnemonic'] == 'ldr' and i['op_str'].startswith('w21,')
                          or i['mnemonic'] == 'ldr' and i['op_str'].startswith('w9,')), None)
            row['threshold_source'] = 'static field (see cap_note)'
            row['threshold_reg'] = reg
        reset = None
        for position in range(index, index + 16):
            follow = insns[position]
            if follow['mnemonic'] != 'bl':
                continue
            target = names.get(call_target(follow), '')
            if not target.startswith('public static void set_'):
                continue
            reset = target.split('set_')[1].split('(')[0]
            value = next((i for i in reversed(insns[max(0, position - 4):position])
                          if i['mnemonic'] == 'mov' and i['op_str'].startswith('w0,')), None)
            if value is not None:
                row['reset_to'] = 0 if 'wzr' in value['op_str'] else int(
                    re.search(r'#(0x[0-9a-f]+|\d+)', value['op_str']).group(1), 0)
            break
        row['reset_target'] = reset
        out.append(row)
    caps = {}
    for row in out:
        if row['resource'] in key and row['threshold']:
            caps[row['resource']] = row['threshold']
    if caps != {'KeyCount0': 1_000_000, 'KeyCount1': 500_000, 'KeyCount2': 100_000}:
        raise AssertionError(f'unexpected key caps: {caps}')
    return dict(method_rva=rva, method='GameDatas.IsHasCheatResources',
                rows=[row for row in out if row['resource'].startswith('KeyCount')],
                key_caps=caps,
                note='a value at or above the cap is written back as 0 and the '
                     'method returns true, so the guard rewrites cheated keys',
                other_resources=[row['resource'] for row in out
                                 if not row['resource'].startswith('KeyCount')])


def pack_routing(names, jump):
    window = (jump.get('rodata_windows') or [None])[0]
    if not window or window['va'] != PACK_TABLE['va']:
        raise AssertionError('pack dispatch table window missing or moved')
    table = list(bytes.fromhex(window['hex']))
    saver = next(m for m in jump['methods'] if 'SaveDataReward' in m['signature'])
    insns = saver['instructions']
    by_rva = {i['rva']: i for i in insns}
    default_pad = next(call_target(i) for i in insns[:40] if i['mnemonic'] == 'b.hi')
    routing = {}
    for index, byte in enumerate(table):
        pad = PACK_TABLE['base_pad'] + 4 * byte
        if pad == default_pad:
            routing[index] = dict(pad=pad, grant=None, note='falls through to ret')
            continue
        calls = []
        for offset in range(0, 0x40, 4):
            one = by_rva.get(pad + offset)
            if one and one['mnemonic'] in ('bl', 'b'):
                calls.append((one['mnemonic'], names.get(call_target(one), '?')))
        getter = next((c[1] for c in calls if c[0] == 'bl' and re.search(r'\bget_', c[1])), None)
        setter = next((c[1] for c in calls if c[0] == 'b'), None)
        adds = any(by_rva.get(pad + off, {}).get('op_str') == 'w0, w0, w19'
                   for off in range(0, 0x30, 4))
        routing[index] = dict(pad=pad, get=short(getter) if getter else None,
                              set=short(setter) if setter else None,
                              adds_value=adds)
    keys = {index: row['get'] for index, row in routing.items() if row.get('get', '') and
            row['get'].startswith('get_KeyCount')}
    if keys != {16: 'get_KeyCount0', 17: 'get_KeyCount1', 18: 'get_KeyCount2'}:
        raise AssertionError(f'unexpected pack -> key routing: {keys}')
    for index in (16, 17, 18):
        if not routing[index]['adds_value'] or routing[index]['set'] != f'set_KeyCount{index - 16}':
            raise AssertionError(f'pack index {index} does not do get -> +value -> set')
    return dict(
        table=dict(va=PACK_TABLE['va'], length=len(table), hex=window['hex'],
                   sha256=window['sha256'],
                   rule='pad = 0x124ca98 + 4 * table[index]'),
        method=dict(class_name=saver['class_name'], rva=saver['rva'], size=saver['size'],
                    signature=saver['signature']),
        default_pad=default_pad,
        default_indices=sorted(i for i, row in routing.items() if not row.get('get')),
        key_indices=keys,
        routing=routing)


def quest_grants(names, grant, by_rva, lines):
    bonus = field_offsets(lines, 'Bonus_Quest')
    if {k: bonus.get(k) for k in ('key0', 'key1', 'key2')} != {'key0': 0x10, 'key1': 0x14,
                                                              'key2': 0x18}:
        raise AssertionError('Bonus_Quest key fields moved')
    collect = next(m for m in by_rva.values() if 'g__Collect|2' in m['signature'])
    insns = collect['instructions']
    blocks = {}
    for index, one in enumerate(insns):
        if one['mnemonic'] != 'bl':
            continue
        name = names.get(call_target(one), '')
        put = re.match(r'public static void set_KeyCount(\d)\(', name)
        if not put:
            continue
        window = insns[max(0, index - 8):index + 1]
        load = next((inner for inner in window if inner['mnemonic'] == 'ldr'
                     and re.match(r'w8, \[x21, #0x1[048]\]', inner['op_str'])), None)
        get = next((names.get(call_target(inner), '') for inner in window
                    if inner['mnemonic'] == 'bl'
                    and names.get(call_target(inner), '').startswith('public static int get_KeyCount')),
                   '?')
        if load is None or get == '?':
            raise AssertionError(f'set_KeyCount{put.group(1)} block has no Bonus_Quest field')
        offset = int(re.search(r'#0x([0-9a-f]+)', load['op_str']).group(1), 16)
        field = {0x10: 'key0', 0x14: 'key1', 0x18: 'key2'}[offset]
        if f'get_KeyCount{put.group(1)}' not in get:
            raise AssertionError(f'{field} feeds the wrong counter')
        if not any(inner['mnemonic'] == 'add' and inner['op_str'] == 'w0, w8, w0'
                   for inner in window):
            raise AssertionError(f'{field} block does not add the bonus value')
        blocks[field] = dict(offset=offset, get=short(get), set=short(name),
                             effect=f'{short(name)}({short(get)}() + bonus.{field})')

    caq = by_rva[19955408]
    caq_insns = caq['instructions']
    statics_28 = any(one['mnemonic'] == 'ldr' and one['op_str'] == 'x8, [x8, #0x28]'
                     for one in caq_insns)
    bonus_key2 = any(one['mnemonic'] == 'ldr' and one['op_str'] == 'w8, [x8, #0x18]'
                     for one in caq_insns)
    if not (statics_28 and bonus_key2):
        raise AssertionError('collect-all button no longer reads bonusClearAllQuests.key2')
    muliple = field_offsets(lines, 'Board_Quest').get('keyMuliple')
    return dict(
        per_quest=dict(method=dict(class_name=collect['class_name'], rva=collect['rva'],
                                   size=collect['size'], signature=collect['signature']),
                       blocks=blocks,
                       rule='one Bonus_Quest row per completed quest bar; each of key0/1/2 '
                            'is added to the matching GameDatas counter when >= 1'),
        collect_all=dict(method=dict(class_name=caq['class_name'], rva=caq['rva'],
                                     size=caq['size'], signature=caq['signature']),
                         bonus_source='Board_Quest.bonusClearAllQuests (static, 0x28)',
                         field='Bonus_Quest.key2 (0x18)',
                         rule='only KeyCount2 is granted here, and only from the '
                              'Configured bonus, not from the quest count'),
        display_multiplier=dict(field='Board_Quest.keyMuliple', offset=muliple,
                                note='the floating text spawns with keyMuliple * bonus.keyN '
                                     'while the stored value grows by bonus.keyN only; '
                                     'whether both ever differ is MODEL_NOT_MEASURED runtime'),
    )


def pvp_grant(names, grant, by_rva, pvp, lines):
    window = (pvp.get('rodata_windows') or [None])[0]
    if not window or window['va'] != PVP_TABLE['va']:
        raise AssertionError('PvP dispatch table window missing or moved')
    table = list(bytes.fromhex(window['hex']))
    method = by_rva[19792936]
    insns = method['instructions']
    by_rva = {i['rva']: i for i in insns}
    base = next((int(i['op_str'].split('#')[-1], 0) for i in insns
                 if i['mnemonic'] == 'adr'
                 and int(i['op_str'].split('#')[-1], 0) == PVP_TABLE['base_pad']), None)
    if base is None:
        raise AssertionError('dispatcher base adr not found')
    select = next(i for i in insns if i['mnemonic'] == 'sub' and i['op_str'] == 'w9, w8, #0xe')
    span = next(i for i in insns if i['mnemonic'] == 'cmp' and i['op_str'] == 'w9, #9')
    first_type = int(select['op_str'].rsplit('#', 1)[1], 0)
    if span['op_str'] != f'w9, #{len(table) - 1}' or first_type != 14:
        raise AssertionError('reward-type window changed')
    routing = {}
    for index, byte in enumerate(table):
        pad = base + 4 * byte
        action = 'no reward (falls through to ret)'
        for offset in range(0, 0x120, 4):
            one = by_rva.get(pad + offset)
            if one and one['mnemonic'] == 'bl':
                name = names.get(call_target(one), '')
                match = re.search(r'public static void (\w+)\(', name)
                if match and match.group(1) in ('set_KeyCount2', 'set_PvPMedal',
                                                'SetDroneCards', 'SetPlayerCards',
                                                'set_Gems', 'set_Coins'):
                    action = f'{match.group(1)}(+ amount)'
                    break
        routing[first_type + index] = dict(type_id=first_type + index, pad=pad,
                                           action=action,
                                           gift_type_hint=GIFT_TYPES.get(first_type + index))
    if routing[18]['action'] != 'set_KeyCount2(+ amount)':
        raise AssertionError(f'type 18 no longer routes to the key counter: {routing[18]}')
    live = {t: row['action'] for t, row in routing.items()
            if not row['action'].startswith('no reward')}
    fields = field_offsets(lines, 'Board_PVP')
    return dict(
        method=dict(class_name=method['class_name'], rva=method['rva'], size=method['size'],
                    signature=method['signature']),
        table=dict(va=PVP_TABLE['va'], length=len(table), hex=window['hex'],
                   sha256=window['sha256'],
                   rule='target = 0x12e0518 + 4 * table[type - 14]'),
        routing=routing,
        gate='rewardTypes index (sibling index / 2) must be below SeasonProgress and the '
             'stage must not be collected yet',
        live_types=live,
        dead_types=sorted(t for t, row in routing.items()
                          if row['action'].startswith('no reward')),
        note='every live id resolves to the same-named GiftType member (14 DroneCards, '
             '15 PlayerCards, 18 Key2, 23 PVPMedal), but no case exists for 16/17 '
             '(Key0/Key1), so this line can only ever add KeyCount2',
        amount_source=dict(type_array=dict(field='rewardIndexs', offset=fields.get('rewardIndexs')),
                           amount_array=dict(field='rewardValues', offset=fields.get('rewardValues')),
                           scales_array=dict(field='rewardScales', offset=fields.get('rewardScales')),
                           note='per-stage instance arrays filled at runtime, so the amount is '
                                'MODEL_NOT_MEASURED runtime'),
    )


def build_payload():
    calls, jump, grant, pvp = load(CALLS), load(JUMP), load(GRANT), load(PVP)
    lines = dump_lines()
    names = dump_names(lines)
    by_rva = {m['rva']: m for m in grant['methods']}
    literals = {row['value'] for row in json.loads((ROOT / LITERALS).read_text())}

    method_rows = []
    current = ''
    for index, line in enumerate(lines):
        match = re.search(r'(?:class|struct) (\S+).*?// TypeDefIndex:', line)
        if match:
            current = match.group(1)
        rva = re.match(r'\s*// RVA: 0x([0-9A-F]+)', line)
        if rva and index + 1 < len(lines):
            method_rows.append((int(rva.group(1), 16), current, lines[index + 1].strip()))
    method_rows.sort()
    rvas = [row[0] for row in method_rows]

    # --- call sites -> caller method, then role -----------------------------
    hits = []
    for hit in calls['hits']:
        index = bisect.bisect_right(rvas, hit['rva']) - 1
        if index < 0:
            raise AssertionError('call site before the first method')
        rva, cls, signature = method_rows[index]
        hits.append(dict(hit, target_name={t['rva']: t['name'] for t in calls['targets']}[hit['target']],
                         caller=dict(class_name=cls, method_rva=rva, signature=signature)))

    grouped = {}
    for hit in hits:
        grouped.setdefault((hit['caller']['class_name'], hit['caller']['method_rva']), []).append(hit)
    roles = {}
    for (cls, rva), group in grouped.items():
        signature = group[0]['caller']['signature']
        sets = [g['target_name'] for g in group if g['target_name'].startswith('set_')]
        if cls.startswith('Board_QuestRewards') and 'SaveDataReward' not in signature and sets:
            role = 'spend'
        elif 'SaveDataReward' in signature:
            role = 'grant_via_pack_value'
        elif 'IsHasCheatResources' in signature:
            role = 'cheat_guard'
        elif sets:
            role = 'grant_direct'
        elif cls.startswith('DataPrefs'):
            role = 'serialization'
        else:
            role = 'display_or_state'
        roles[(cls, rva)] = dict(class_name=cls, method_rva=rva, signature=signature,
                                 role=role, hits=len(group),
                                 targets=sorted({g['target_name'] for g in group}),
                                 call_sites=sorted({g['rva'] for g in group}))

    order = ['grant_via_pack_value', 'grant_direct', 'spend', 'cheat_guard',
             'serialization', 'display_or_state']
    by_role = {}
    for row in roles.values():
        by_role.setdefault(row['role'], []).append(row)
    summary = {}
    for role in order:
        items = sorted(by_role.get(role, []), key=lambda r: r['method_rva'])
        summary[role] = dict(
            methods=len(items), classes=len({i['class_name'] for i in items}),
            hits=sum(i['hits'] for i in items),
            class_names=sorted({i['class_name'] for i in items}))

    payload = dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='Four pinned scans plus dump.cs. Nothing is executed; the size of a real '
             'reward depends on pack/stage data (MODEL_NOT_MEASURED runtime).',
        provenance=dict(
            xapk_sha256=calls['provenance']['xapk_sha256'],
            libil2cpp_sha256=calls['provenance']['libil2cpp_sha256'],
            words_scanned=calls['method']['words_scanned'],
            segments=calls['method']['segments'],
            hits_total=len(hits),
            sources=[dict(path=path, sha256=sha_file(path))
                     for path in (CALLS, JUMP, GRANT, PVP, DUMP, LITERALS)]),
        accessors=dict(
            counters={name: dict(getter=rva, setter=SETTERS[name], static_offset=STATIC_OFFSET[name])
                      for name, rva in GETTERS.items()},
            semantics=accessor_semantics(names, by_rva),
            prefs_keys=dict(literals=sorted(v for v in literals
                                            if re.fullmatch(r'KeyCount\d', v)),
                            note='the three literals are present in stringliteral.json; the '
                                 'slot -> literal binding is not in the pinned data')),
        caps=cheat_caps(names, by_rva, GETTERS),
        supply=dict(pack_values=pack_routing(names, jump),
                    quest=quest_grants(names, grant, by_rva, lines),
                    pvp=pvp_grant(names, grant, by_rva, pvp, lines),
                    no_regeneration='no caller of a KeyCount setter adds anything except a '
                                    'reward argument, so there is no idle or timed drip; the '
                                    'three UpdateKey*.MoveNext coroutines only animate labels'),
        callers=summary,
        callers_detail=sorted(roles.values(), key=lambda r: (order.index(r['role']),
                                                             r['method_rva'])),
        not_decoded=[
            dict(item='per-call pack amount for the 20 SaveDataReward clones',
                 blocking='the value arrives as the _value argument from pack data; the '
                          'store path is decoded, the operand is not'),
            dict(item='PvP stage reward types and amounts',
                 blocking='Board_PVP.rewardTypes/rewardValues are instance arrays filled at '
                          'runtime; the dispatch table proves Key2 is reachable, not how much'),
            dict(item='PlayerPrefs key -> literal binding for KeyCount0/1/2',
                 blocking='metadata usage table for the string slots is not in the pinned data'),
            dict(item='a direct static store outside these classes',
                 blocking='the branch scan sees calls, not stores; a writer that assigns '
                          'statics 0x50/0x54/0x58 inline elsewhere would not appear'),
        ],
    )

    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_key_sources.json.gz')
    args = parser.parse_args()
    payload = build_payload()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                                sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          hits=payload['provenance']['hits_total'],
                          methods=sum(row['methods'] for row in payload['callers'].values()),
                          roles={k: v['methods'] for k, v in payload['callers'].items()},
                          key_caps=payload['caps']['key_caps'],
                          pack_keys=payload['supply']['pack_values']['key_indices'],
                          pvp_key2=payload['supply']['pvp']['routing'][18]['action'])))


if __name__ == '__main__':
    main()
