#!/usr/bin/env python3
"""Box draw: which `typeBox`, from the real caller sites. STATIC only.

Report 129 left `Shop_Pack` semantics known but the *caller* side open: which
`typeBox` a quest box draws with, and who writes it. This tool closes that from
pinned original-APK bytes:

* the single writer of `Board_QuestRewards.typeBox` — `Board_Quest.
  OnPressedButtonOpenBox(int _index)` stores its argument straight into
  statics+0x0, so the box *button index* is the type box;
* `.cctor` writes both statics (8 bytes: typeBox + timeUpdate) from one pinned
  rodata literal, so the initial value is known and not inferred;
* all three call sites of the pack-index rules, with the register provenance of
  every argument;
* the key economy at the same call site (`BoxKeyCost`, `KeyPrices`) and the
  energy shop that shares the `typeBox`-indexed tables.

Nothing here executes game code; `UnityEngine.Random` is never simulated.
"""
import argparse
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

META = 'reverse-engineering/raw/meta-rewards-535b0541/native.json.gz'
PACK = 'reverse-engineering/raw/pack-index-535b0541/native.json.gz'
BOX = 'reverse-engineering/raw/box-draw-535b0541/native.json.gz'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'

WRITERS = {'mov', 'movz', 'movk', 'movn', 'adrp', 'ldr', 'ldrb', 'ldrh', 'ldrsb', 'ldrsh',
           'ldrsw', 'add', 'adds', 'sub', 'subs', 'and', 'ands', 'orr', 'eor', 'mul', 'madd',
           'sxtw', 'sxtb', 'sxth', 'uxtw', 'lsl', 'asr', 'lsr', 'csel', 'csinc', 'cset', 'neg',
           'sdiv', 'udiv', 'rev', 'scvtf', 'fmov'}
RANDOM_RVA = 20234188      # Shop_Pack.GetListIndexRandomRewards
LIST_RVA = 20199416        # Shop_Pack.GetListIndexRewards
REWARDS_SLOT = 0x2AE1178   # il2cpp class slot of Board_QuestRewards
QUEST_SLOT = 0x2ADC298     # il2cpp class slot of Board_Quest
STATICS = 0xB8             # Il2CppClass::static_fields


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


def dump_lines():
    return gzip.decompress((ROOT / DUMP).read_bytes()).decode().split('\n')


def dump_rva(rel):
    """rva -> (declaration line, enclosing class line) for every dump.cs method."""
    lines = dump_lines()
    out, last = {}, ''
    for index, line in enumerate(lines):
        if '// TypeDefIndex:' in line and re.match(r'\s*(public|private|internal|protected).*'
                                                  r'\b(class|struct|enum|interface)\b', line):
            last = line.strip()
        match = re.match(r'\s*// RVA: 0x([0-9A-F]+)', line)
        if match:
            out[int(match.group(1), 16)] = (lines[index + 1].strip(), last)
    return out


def fields(cls):
    """Declared static fields of `cls` as [(offset, name, type)]."""
    lines = dump_lines()
    start = next(k for k, l in enumerate(lines)
                 if re.match(r'\s*public class ' + re.escape(cls) + r'\b', l))
    depth = 0
    for end in range(start, len(lines)):
        depth += lines[end].count('{') - lines[end].count('}')
        if end > start and depth == 0:
            break
    out = []
    for line in lines[start:end]:
        field = re.match(r'\s*(?:public|private|protected|internal)\s+static\s+(.+?)\s+(\w+);'
                         r'\s*//\s*0x([0-9A-Fa-f]+)\s*$', line)
        if field:
            out.append((int(field.group(3), 16), field.group(2), field.group(1).strip()))
    return out


def insn(raw, rva, mnemonic, op_str):
    """Assert the pinned bytes at `rva` are exactly this instruction."""
    for method in raw['methods']:
        for one in method['instructions']:
            if one['rva'] == rva:
                if (one['mnemonic'], one['op_str']) != (mnemonic, op_str):
                    raise AssertionError(f'{rva}: {one["mnemonic"]} {one["op_str"]} != '
                                         f'{mnemonic} {op_str}')
                return one
    raise AssertionError(f'no instruction at {rva}')


def method(raw, cls, needle):
    for entry in raw['methods']:
        if entry['class_name'] == cls and needle in entry['signature']:
            return entry
    raise KeyError(f'{cls}.{needle}')


def slot_refs(raw, rva):
    for m in raw['methods']:
        for ref in m.get('slot_refs', []):
            if ref['rva'] == rva:
                return ref
    return None


LOAD = re.compile(r'^(x\d+), \[(x\d+)(?:, #(0x[0-9a-f]+))?\]$')
STORE = re.compile(r'^([wxd]\d+), \[(x\d+)\]$')


def stores_to_static0(raws, class_slot):
    """Every store that lands on statics+0 of the class addressed by `class_slot`.

    The extractor annotates each `ldr xD, [xK]` that reads a metadata-usage slot
    with that slot's VA, so `ldr xD, [xK]` -> class pointer, `ldr xM, [xD,
    #0xb8]` -> static_fields, `str wN, [xM]` -> statics+0. Registers are tracked
    inside one method only; a store through another addressing form would be
    missed rather than assumed away.
    """
    out = []
    for raw in raws:
        for m in raw['methods']:
            slots = {ref['rva']: ref['slot_va'] for ref in m.get('slot_refs', [])}
            regs = {}
            for one in m['instructions']:
                load = LOAD.match(one['op_str'])
                if one['mnemonic'] == 'ldr' and load:
                    dest, base, offset = load.group(1), load.group(2), load.group(3)
                    if offset == '0xb8' and regs.get(base, '').startswith('class:'):
                        regs[dest] = regs[base].replace('class:', 'statics:')
                    elif one['rva'] in slots:
                        regs[dest] = f'class:{slots[one["rva"]]}'
                    else:
                        regs[dest] = 'other'
                    continue
                store = STORE.match(one['op_str'])
                if one['mnemonic'].startswith('str') and store:
                    if regs.get(store.group(2)) == f'statics:{class_slot}':
                        out.append(dict(method=m['signature'], class_name=m['class_name'],
                                        rva=one['rva'],
                                        instruction=f"{one['mnemonic']} {one['op_str']}"))
    return out


def call_sites(raws):
    """Every `bl` to the two pack-index rules with its argument provenance."""
    out = []
    for raw in raws:
        for m in raw['methods']:
            insns = m['instructions']
            for index, one in enumerate(insns):
                if one['mnemonic'] != 'bl':
                    continue
                target = int(one['op_str'].lstrip('#'), 0)
                if target not in (RANDOM_RVA, LIST_RVA):
                    continue
                writes = {}
                for reg in ('x0', 'w1', 'w2'):
                    for previous in reversed(insns[max(0, index - 40):index]):
                        writes_reg = (previous['mnemonic'] in WRITERS
                                      and previous['op_str'].split(',')[0].strip() == reg)
                        if writes_reg:
                            writes[reg] = dict(rva=previous['rva'],
                                               instruction=f"{previous['mnemonic']} "
                                                           f"{previous['op_str']}")
                            break
                out.append(dict(
                    callee='GetListIndexRandomRewards' if target == RANDOM_RVA
                    else 'GetListIndexRewards',
                    callee_rva=target, call_rva=one['rva'],
                    caller_class=m['class_name'], caller=m['signature'],
                    caller_rva=m['rva'], argument_writes=writes))
    return sorted(out, key=lambda c: c['call_rva'])


def build():
    meta, pack, box = load(META), load(PACK), load(BOX)

    # --- the writer of typeBox, straight from Board_Quest ------------------
    opener = method(box, 'Board_Quest', 'OnPressedButtonOpenBox')
    insn(box, opener['rva'] + 0x68, 'str', 'w20, [x8]')      # statics[0] = _index
    insn(box, opener['rva'] + 0x10, 'adrp', 'x21, #0x2ae1000')
    insn(box, opener['rva'] + 0x98, 'mov', 'w1, #0x38')       # EventID.OpenBoard
    post = 0x1434CB4

    # --- .cctor: one 8-byte literal fills typeBox + timeUpdate ------------
    cctor = method(meta, 'Board_QuestRewards', '.cctor')
    insn(meta, cctor['rva'] + 0x44, 'str', 'd0, [x8]')
    window = next((w for w in meta.get('rodata_windows') or []), None)
    window = window or box['rodata_windows'][0]
    literal = bytes.fromhex(window['hex'])
    rewards_writers = stores_to_static0([meta, pack, box], REWARDS_SLOT)
    type_box_init, time_update_init = (int.from_bytes(literal[:4], 'little'),
                                       int.from_bytes(literal[4:], 'little'))

    # --- what every statics+0 / statics+0x48 access belongs to ------------
    def slot_users(raw, slot):
        users = {}
        for m in raw['methods']:
            for ref in m.get('slot_refs', []):
                if ref['slot_va'] == slot:
                    users[m['class_name']] = users.get(m['class_name'], 0) + 1
        return dict(sorted(users.items(), key=lambda kv: (-kv[1], kv[0])))

    quest_fields = {offset: (name, kind) for offset, name, kind in fields('Board_Quest')}

    # --- key economy at the same call site --------------------------------
    open_now = method(meta, 'Board_QuestRewards', 'OnPressedButtonOpenNow')
    insn(meta, 0x1310428, 'ldr', 'x25, [x8, #0x38]')
    insn(meta, 0x13104c8, 'ldr', 'x10, [x10, #0x40]')
    insn(meta, 0x13104f0, 'mul', 'w8, w8, w9')

    # --- energy shop ------------------------------------------------------
    buy = method(pack, 'Board_ShopEnergy', 'OnPressedButtonBuyEnergy')
    free = method(pack, 'Board_ShopEnergy', 'OnPressedButtonFreeEnergy')
    exchange = method(pack, 'Board_ShopEnergy', 'GetExchangeGemsFromEnergy')

    # --- array blobs built by RuntimeHelpers.InitializeArray --------------
    initialize = 0x205B07C
    cctor_insns = next(m for m in box['methods']
                       if m['class_name'] == 'Board_Quest' and '.cctor' in m['signature']
                       )['instructions']
    refs = {r['rva']: r for r in slot_refs(box, cctor_insns[0]['rva']) or []}
    cctor_refs = next(m for m in box['methods']
                      if m['class_name'] == 'Board_Quest' and '.cctor' in m['signature']
                      )['slot_refs']
    by_rva = {r['rva']: r for r in cctor_refs}
    blobs = []
    for index, one in enumerate(cctor_insns):
        if one['mnemonic'] != 'bl' or int(one['op_str'].lstrip('#'), 0) != initialize:
            continue
        handle = None
        for previous in reversed(cctor_insns[max(0, index - 6):index]):
            ref = by_rva.get(previous['rva'])
            if ref and ref['token_hi'] >= 0x80000000:
                handle = ref
                break
        target = None
        for following in cctor_insns[index:index + 14]:
            match = re.match(r'x19, \[x8, #(0x[0-9a-f]+)\]$', following['op_str'])
            if following['mnemonic'] == 'str' and match:
                target = int(match.group(1), 16)
                break
        blobs.append(dict(call_rva=one['rva'], statics_offset=target,
                          handle_token_index=handle['token_hi'] - 0x80000000,
                          handle_slot_va=handle['slot_va']))

    return dict(
        schema=1,
        evidence='STATIC_ONLY_ORIGINAL_APK',
        note='Decoded from pinned original-APK bytes; no draw is simulated. '
             'UnityEngine.Random is seeded at runtime, so any sequence is '
             'MODEL_NOT_MEASURED runtime.',
        provenance=dict(
            sources=[dict(path=p, sha256=sha_file(p)) for p in (META, PACK, BOX, DUMP)],
            xapk_sha256=meta['xapk_sha256'],
            libil2cpp_sha256=meta['libil2cpp_sha256'],
            methods_scanned=sum(len(r['methods']) for r in (meta, pack, box))),
        slots=dict(
            note='il2cpp class slots are per-module entries; the two boards are addressed '
                 'through different slots in the same method, so they cannot be confused',
            board_quest_rewards=dict(slot_va=REWARDS_SLOT, users=slot_users(meta, REWARDS_SLOT),
                                     statics_offset=0),
            board_quest=dict(slot_va=QUEST_SLOT, users=slot_users(box, QUEST_SLOT),
                             static_fields={f'{o:#x}': f'{n}: {kind}'
                                            for o, (n, kind) in sorted(quest_fields.items())}),
        ),
        type_box=dict(
            field='Board_QuestRewards.typeBox',
            declared='int', static_offset=0, class_slot_va=REWARDS_SLOT,
            writer=dict(method='Board_Quest.OnPressedButtonOpenBox(int _index)',
                        rva=opener['rva'], size=opener['size'],
                        store_rva=opener['rva'] + 0x68,
                        rule='statics[0] = _index (the box button index)',
                        after=dict(event='EventID.OpenBoard', event_value=56,
                                   board='BoardID.BoardQuestRewards', board_value=18,
                                   post_event_rva=post)),
            initial=dict(source='Board_QuestRewards..cctor', rva=cctor['rva'], size=cctor['size'],
                         store_rva=cctor['rva'] + 0x44,
                         rodata_va=window['va'], rodata_length=window['length'],
                         rodata_hex=window['hex'],
                         type_box=type_box_init, time_update=time_update_init),
            domain=dict(values=[0, 1, 2],
                        reason='BoxKeyCost/KeyPrices/NumberRewards are each `new int[3]` in '
                               'Board_Quest..cctor and OnPressedButtonOpenNow branches '
                               'typeBox == 0 / == 1 / else'),
            writers_total=len(rewards_writers),
            writers=[dict(method=w['method'], rva=w['rva'], instruction=w['instruction'])
                     for w in rewards_writers],
            writers_scope=f'all {sum(len(r["methods"]) for r in (meta, pack, box))} methods '
                          'pinned by this session (meta, pack-index and box-draw families); '
                          'the scan finds exactly the two stores listed: the .cctor literal and '
                          'the OnPressedButtonOpenBox argument',
        ),
        caller_chain=[
            dict(step=1, method='Board_Quest.OnPressedButtonOpenBox(int _index)',
                 rva=opener['rva'], effect='typeBox = _index'),
            dict(step=2, method='EventDispatcherExtension.PostEvent', rva=post,
                 effect='OpenBoard(56) with BoardID.BoardQuestRewards (18) as parameter'),
            dict(step=3, method='Board_QuestRewards.OpenBoard',
                 rva=19985576, effect='reads typeBox to lay out the panel'),
            dict(step=4, method='Board_QuestRewards.OnPressedButtonOpenNow',
                 rva=open_now['rva'], size=open_now['size'],
                 effect='key check, then deduct and open'),
            dict(step=5, method='Board_QuestRewards.OpenBoxNow', rva=19991076,
                 effect='sets flag 0xd0 and starts the OpenBox coroutine'),
            dict(step=6, method='Board_QuestRewards.<OpenBox>d__43.MoveNext',
                 rva=19996384, size=5128,
                 effect='GetListIndexRandomRewards(pack, NumberRewards[typeBox], typeBox)'),
        ],
        call_sites=call_sites([meta, pack, box]),
        box_cost=dict(
            array_initializers=blobs,
            arrays={
                'BoxKeyCost': dict(offset=0x38, declared=quest_fields.get(0x38, ('?', '?'))[1],
                                   length=3),
                'KeyPrices': dict(offset=0x40, declared=quest_fields.get(0x40, ('?', '?'))[1],
                                  length=3),
                'NumberRewards': dict(offset=0x48,
                                      declared=quest_fields.get(0x48, ('?', '?'))[1], length=3),
            },
            rule='owned = typeBox == 0 ? KeyCount0 : typeBox == 1 ? KeyCount1 : KeyCount2; '
                 'if owned >= BoxKeyCost[typeBox] then KeyCountN = owned - BoxKeyCost[typeBox] '
                 'and the box opens, else keyMiss = BoxKeyCost[typeBox] - owned and '
                 'price = KeyPrices[typeBox] * keyMiss is shown instead',
            key_count_statics=dict(KeyCount0=0x50, KeyCount1=0x54, KeyCount2=0x58),
            getters=dict(KeyCount0=20070740, KeyCount1=20071068, KeyCount2=20071396),
            setters=dict(KeyCount0=20070940, KeyCount1=20071268, KeyCount2=20071596),
            sprite=dict(rva=20180172, method='DataShopPack.GetBoxSpriteGeneral',
                        index_rule='typeBox + 16'),
            ui=dict(rva=19990656, method='Box_Rewards.SetInfo'),
        ),
        energy_shop=dict(
            buy=dict(rva=buy['rva'], size=buy['size'],
                     rule='if (GameDatas.Gems < 30) Popup_Notices.NoGems(); else '
                          '{ Gems -= 30; Energy += 50; } then refresh + analytics',
                     gem_cost=30, energy_gain=50,
                     guard=dict(rva=0x13C9FFC, method='Popup_Notices.NoGems'),
                     log=dict(rva=0x13BF534, method='LogEvents.LogEventBuyInShopEnergy')),
            free=dict(rva=free['rva'], size=free['size'],
                      rule='online && video ready && timer ready -> rewarded video at ad '
                           'position 14; the success callback adds energy 30',
                      energy_gain=30,
                      success_callback=dict(method='<OnPressedButtonFreeEnergy>b__16_0',
                                            rva=19432800, energy_add=0x1e, event_id=60,
                                            analytics_event_id=2),
                      ads=dict(rva=0x142E0F8, method='AdsCaller.ShowRewardedVideo', position=14)),
            exchange=dict(rva=exchange['rva'],
                          rule='IsProVersion() ? (energy * 30) / 100 : -1', gems_per_energy=0.3),
        ),
        not_decoded=[
            dict(item='contents of BoxKeyCost / KeyPrices / NumberRewards',
                 blocking='Board_Quest..cctor builds them with `new int[3]` / `new double[3]` and '
                          'RuntimeHelpers.InitializeArray (rva 33927292) over a field handle; the '
                          'bytes live in global-metadata field defaults, which libil2cpp does not '
                          'carry. Handles recorded: ' +
                          ', '.join(f'{b["statics_offset"]:#x} <- handle index '
                                    f'{b["handle_token_index"]} at rva {b["call_rva"]}'
                                    for b in blobs)),
            dict(item='draw sequence / actual items received',
                 blocking='UnityEngine.Random.Range is seeded at runtime; '
                          'MODEL_NOT_MEASURED runtime'),
            dict(item='key acquisition schedule',
                 blocking='UpdateKey0/1/2 only animate the label toward GameDatas.KeyCountN; '
                          'who increments the counts lives outside the pinned families'),
        ],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='datas/l2_535b0541_box_draw.json.gz')
    args = parser.parse_args()
    payload = build()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                                sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          writers=payload['type_box']['writers_total'],
                          initial=payload['type_box']['initial']['type_box'],
                          calls=len(payload['call_sites']))))


if __name__ == '__main__':
    main()
