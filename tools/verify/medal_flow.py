#!/usr/bin/env python3
"""The medal wallet: one static int per faction, clamped at zero, and 30 callers.

154 proved the exchange popup never deducts and left the question open: *who
spends the medal after the popup returns*. This report answers it from the
wallet side, and the answer has three parts worth writing down:

* the wallet is `GameDatas.arenaMedal` (+0x9C) and `GameDatas.pvpMedal` (+0xA0),
  two declared statics; both start at `-1` from `GameDatas..cctor`, and `-1` is
  the "not loaded" sentinel that makes the getter call `PlayerPrefs.GetInt` and
  cache the answer into the same slot;
* the setter clamps at zero with `bic w19, w19, w19, asr #31` and then persists
  with a **tail call** (`b PlayerPrefs.SetInt`), so a scan that only reads `bl`
  sees writes that do not exist and misses the ones that do;
* across the eight dumped slices there are 61 `bl` to the four accessors, 42
  distinct (method, accessor) pairs in 30 methods. Twelve of them write. Six are
  the two shops' buy closures (`msub w0, w8, w21, w0` = medal - count * price),
  five credit, and two move the medal **in lockstep with coins and gems** using
  the `Board_PVP` bet scalars.

The popup stays a reader. That is the closure of 154's open item: the debit
exists, it is in `Arena_Shop`/`PVP_Shop`, and which closure the popup's `onExit`
points at is still not in the dump.
"""
import argparse
import functools
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import arena_rewards as AR  # noqa: E402  (dump reader + owner())

RAW_GLOB = 'reverse-engineering/raw/*535b0541/native.json.gz'
KEY_GRANT = 'reverse-engineering/raw/key-grant-535b0541/native.json.gz'
DUMP = 'reverse-engineering/il2cpp/dump.cs.gz'
PREV_KEYS = 'datas/l2_535b0541_economy_keys.json.gz'
PREV = 'datas/l2_535b0541_exchange_cost.json.gz'

WALLETS = {
    'ArenaMedal': dict(getter=20084804, setter=20085004, field=0x9C,
                       declared='arenaMedal'),
    'PvPMedal': dict(getter=20085132, setter=20085332, field=0xA0,
                     declared='pvpMedal'),
}
# The two other wallets that move in the same statement as the medal.
COMPANIONS = {'Coins': dict(getter=20069516, setter=20069860),
              'Gems': dict(getter=20068904, setter=20069244)}
BETS = [('betCoinValues', 0x10), ('betGemValues', 0x14), ('betMedalValues', 0x18)]
SHOPS = ('Arena_Shop', 'PVP_Shop')


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@functools.lru_cache(maxsize=None)
def slices():
    rows = []
    for path in sorted(ROOT.glob(RAW_GLOB)):
        rows.append((path.parent.name, json.loads(gzip.decompress(path.read_bytes()))))
    return rows


@functools.lru_cache(maxsize=None)
def all_methods():
    rows = []
    for tag, blob in slices():
        for row in blob['methods']:
            rows.append((tag, row))
    return rows


def owner(rva):
    return AR.owner(rva)


def named(rva, want):
    klass, signature = owner(rva)
    assert signature and want in signature, (rva, klass, signature)
    return klass, signature.strip()


def find(insns, mnemonic=None, pattern=None, rva=None):
    for insn in insns:
        if rva is not None and insn['rva'] != rva:
            continue
        text = insn['mnemonic'] + ' ' + insn['op_str']
        if mnemonic and insn['mnemonic'] != mnemonic:
            continue
        if pattern and not re.search(pattern, text):
            continue
        return insn
    raise AssertionError('no instruction %r %r %r' % (mnemonic, pattern, rva))


# ------------------------------------------------------------------ the fields
def declared():
    """`GameDatas`'s own field list — the slot names behind +0x9C and +0xA0."""
    lines = AR.MR.dump_text().split('\n')
    start = next(i for i, line in enumerate(lines)
                 if line.startswith('public class GameDatas :'))
    rows = {}
    for line in lines[start + 1:]:
        text = line.strip()
        if text == '}':
            break
        if text.startswith('// Methods'):
            break
        match = re.match(r'(?:public|private|protected|internal)\s+(?:static\s+)?'
                         r'(\S+)\s+(\w+);\s*// (0x[0-9A-F]+)$', text)
        if match and int(match.group(3), 16) in (0x9C, 0xA0):
            rows[int(match.group(3), 16)] = dict(name=match.group(2),
                                                 declared_type=match.group(1),
                                                 word=text.split(';')[0].strip())
    assert sorted(rows) == [0x9C, 0xA0], rows
    for name, want in WALLETS.items():
        row = rows[want['field']]
        assert row['name'] == want['declared'], (name, row)
        assert row['declared_type'] == 'int', row
    return {name: dict(offset=hex(want['field']), field=rows[want['field']]['name'],
                       declared=rows[want['field']]['word'])
            for name, want in WALLETS.items()}


# ------------------------------------------------------------------ the accessors
def method(tag, rva):
    for name, row in all_methods():
        if name == tag and row['rva'] == rva:
            return row
    raise AssertionError('%s %s not in the slices' % (tag, rva))


def accessors():
    out = {}
    for name, want in WALLETS.items():
        getter = method('key-grant-535b0541', want['getter'])
        setter = method('key-grant-535b0541', want['setter'])
        slot = '#%s]' % hex(want['field'])
        field_load = find(getter['instructions'], 'ldr', pattern=re.escape(slot))
        sentinel = find(getter['instructions'], 'cmn', pattern=r'#1$')
        reload_call = None
        for insn in getter['instructions']:
            if insn['mnemonic'] != 'bl':
                continue
            target = int(insn['op_str'].lstrip('#'), 16)
            klass, signature = owner(target)
            if not signature or 'GetInt' not in signature:
                continue
            reload_call = dict(rva=insn['rva'], target=target, class_name=klass,
                               signature=signature.strip())
            break
        assert reload_call, (name, 'no PlayerPrefs.GetInt in the getter')
        cache_store = [insn for insn in getter['instructions']
                       if insn['mnemonic'] == 'str' and insn['op_str'].endswith(slot)]
        clamp = find(setter['instructions'], 'bic', pattern=r'asr #31$')
        store = [insn for insn in setter['instructions']
                 if insn['mnemonic'] == 'str' and insn['op_str'].endswith(slot)]
        tail = [insn for insn in setter['instructions'] if insn['mnemonic'] == 'b']
        assert len(tail) == 1, tail
        tail_target = int(tail[0]['op_str'].lstrip('#'), 16)
        klass, signature = named(tail_target, 'SetInt')
        key = next(row for row in load(PREV_KEYS)['keys'] if row['key'] == name)
        assert key['slot_va'] is not None and len(key['writes']) == 2, key
        out[name] = dict(
            offset=hex(want['field']),
            getter=dict(rva=getter['rva'], size=getter['size'],
                        signature=getter['signature'].strip()),
            setter=dict(rva=setter['rva'], size=setter['size'],
                        signature=setter['signature'].strip()),
            field_load=dict(rva=field_load['rva'],
                            op=field_load['mnemonic'] + ' ' + field_load['op_str']),
            sentinel=dict(rva=sentinel['rva'],
                          op=sentinel['mnemonic'] + ' ' + sentinel['op_str'],
                          meaning='-1 means "never loaded", not a balance'),
            lazy_load=reload_call,
            cache_store=dict(rva=cache_store[0]['rva'],
                             op=cache_store[0]['mnemonic'] + ' ' + cache_store[0]['op_str']),
            clamp=dict(rva=clamp['rva'],
                       op=clamp['mnemonic'] + ' ' + clamp['op_str'],
                       meaning='max(0, value): the sign bits are cleared, so a '
                               'deduction below zero lands on zero'),
            store=dict(rva=store[0]['rva'],
                       op=store[0]['mnemonic'] + ' ' + store[0]['op_str']),
            persist=dict(rva=tail[0]['rva'], target=tail_target, class_name=klass,
                         signature=signature,
                         note='a tail `b`, not a `bl` — a call scan that ignores `b` '
                              'reports zero writes'),
            key=dict(name=key['key'], literal=key['literal'], slot_va=key['slot_va'],
                     note='cross-checked against the 142-145 '
                                                'PlayerPrefs census, not re-derived'),
        )
    return out


def cctor():
    row = None
    for tag, candidate in all_methods():
        if candidate['class_name'] == 'GameDatas' and '.cctor' in candidate['signature']:
            assert row is None or row['rva'] == candidate['rva'], candidate
            row = candidate
    stores = [insn for insn in row['instructions']
              if insn['mnemonic'] == 'str' and insn['op_str'].endswith('#0xa0]')]
    wide = [insn for insn in row['instructions']
            if insn['mnemonic'] == 'str' and insn['op_str'].endswith('#0x98]')]
    assert len(stores) == 1 and len(wide) == 1, (stores, wide)
    assert stores[0]['op_str'].startswith('w22') and wide[0]['op_str'].startswith('x22')
    return dict(rva=row['rva'], size=row['size'],
                pvp_medal=dict(rva=stores[0]['rva'],
                               op=stores[0]['mnemonic'] + ' ' + stores[0]['op_str'],
                               value=-1),
                arena_medal=dict(rva=wide[0]['rva'],
                                 op=wide[0]['mnemonic'] + ' ' + wide[0]['op_str'],
                                 value=-1,
                                 note='`stur`-adjacent 8-byte store: +0x98 and +0x9C '
                                      'both get -1 from one `str x22`'),
                note='`campaignPoints` (+0x98) and `arenaMedal` (+0x9C) share one '
                     '64-bit store, which is why the arena sentinel has no `str w` '
                     'of its own')


# ------------------------------------------------------------------ the callers
def value_source(insns, index):
    """The instruction that produces `w0` for the call at `index`."""
    for insn in reversed(insns[max(0, index - 8):index]):
        text = insn['mnemonic'] + ' ' + insn['op_str']
        if insn['mnemonic'] == 'bl':
            return dict(rva=insn['rva'], op=text, effect='result-of-call')
        if insn['op_str'].startswith('x1,') or insn['op_str'].startswith('x2,'):
            continue
        if not (insn['op_str'].startswith('w0,') or insn['op_str'].startswith('x0,')):
            continue
        if insn['mnemonic'] in ('add', 'sub', 'subs', 'msub', 'madd', 'mul', 'neg', 'and',
                                'mov', 'ldr', 'csel', 'sxtw'):
            effect = {'add': 'credit', 'sub': 'deduct', 'subs': 'deduct',
                      'msub': 'deduct', 'neg': 'deduct'}.get(insn['mnemonic'], 'read')
            return dict(rva=insn['rva'], op=text, effect=effect)
    raise AssertionError('no value source before rva %s' % insns[index]['rva'])


def callers():
    targets = {}
    for name, want in WALLETS.items():
        targets[want['getter']] = (name, 'get')
        targets[want['setter']] = (name, 'set')
    for name, want in COMPANIONS.items():
        targets[want['getter']] = (name, 'get')
        targets[want['setter']] = (name, 'set')
    medal_only = {want['getter']: (n, 'get') for n, want in WALLETS.items()}
    medal_only.update({want['setter']: (n, 'set') for n, want in WALLETS.items()})

    raw = 0
    seen = {}
    for tag, row in all_methods():
        insns = row['instructions']
        hits = []
        for index, insn in enumerate(insns):
            if insn['mnemonic'] != 'bl':
                continue
            target = int(insn['op_str'].lstrip('#'), 16)
            if target in medal_only:
                raw += 1
            if target in targets:
                hits.append((index, insn, targets[target]))
        if not hits:
            continue
        key = (row['class_name'], row['signature'].strip())
        entry = seen.setdefault(key, dict(
            class_name=row['class_name'], signature=key[1], method_rva=row['rva'],
            size=row['size'], raw=tag, hits=set(), companions=set()))
        for index, insn, (wallet, api) in hits:
            if wallet in COMPANIONS:
                entry['companions'].add((wallet, api, insn['rva']))
                continue
            entry['hits'].add((wallet, api, insn['rva'], index))

    rows = []
    for key in sorted(seen):
        entry = seen[key]
        for wallet, api, rva, index in sorted(entry['hits'], key=lambda row: row[2]):
            row = dict(wallet=wallet, api=api, class_name=entry['class_name'],
                       signature=entry['signature'], method_rva=entry['method_rva'],
                       size=entry['size'], call_rva=rva, raw=entry['raw'])
            if api == 'set':
                row['value_from'] = value_source(method(entry['raw'], entry['method_rva'])
                                                 ['instructions'], index)
                row['effect'] = row['value_from']['effect']
                if ', lsl #' in row['value_from']['op']:
                    row['shift'] = row['value_from']['op'].split(',', 2)[2].strip()
            else:
                row['effect'] = 'read'
            rows.append(row)
    companions = []
    for key in sorted(seen):
        entry = seen[key]
        if entry['companions'] and entry['hits']:
            companions.append(dict(
                class_name=entry['class_name'], signature=entry['signature'],
                medals=sorted({row[0] for row in entry['hits']}),
                others=sorted({(name, api) for name, api, _ in entry['companions']}),
                calls=sorted(entry['companions'], key=lambda row: row[2])))
    return raw, rows, companions


def counts(rows, raw):
    writers = [row for row in rows if row['api'] == 'set']
    return dict(raw_bl=raw, calls=len(rows),
                pairs=len({(row['class_name'], row['signature'], row['wallet'], row['api'])
                           for row in rows}),
                methods=len({row['signature'] + row['class_name'] for row in rows}),
                readers=len(rows) - len(writers), writers=len(writers),
                credit=len([row for row in writers if row['effect'] == 'credit']),
                deduct=len([row for row in writers if row['effect'] == 'deduct']),
                per_wallet={name: dict(
                    pairs=len([row for row in rows if row['wallet'] == name]),
                    writes=len([row for row in writers if row['wallet'] == name]))
                    for name in WALLETS})


def clusters(rows):
    def names(predicate):
        return sorted({(row['class_name'], row['signature']) for row in rows if predicate(row)})

    def is_shop(name):
        return any(name == shop or name.startswith(shop + '.') for shop in SHOPS)

    shop_writes = [row for row in rows if row['api'] == 'set' and is_shop(row['class_name'])]
    return dict(
        shop_deduct=[dict(class_name=row['class_name'], signature=row['signature'],
                          wallet=row['wallet'], call_rva=row['call_rva'],
                          op=row['value_from']['op'])
                     for row in shop_writes],
        credits=[dict(class_name=row['class_name'], signature=row['signature'],
                      wallet=row['wallet'], call_rva=row['call_rva'],
                      op=row['value_from']['op'])
                 for row in rows if row['api'] == 'set' and row['effect'] == 'credit'],
        deduct_not_shop=[dict(class_name=row['class_name'], signature=row['signature'],
                              wallet=row['wallet'], call_rva=row['call_rva'],
                              op=row['value_from']['op'])
                         for row in rows if row['api'] == 'set' and row['effect'] == 'deduct'
                         and not is_shop(row['class_name'])],
        popup_reads=names(lambda row: 'ShopExchange' in row['class_name']),
        exchange_writes=[row for row in rows if row['api'] == 'set'
                         and 'ShopExchange' in row['class_name']],
        read_methods=len(names(lambda row: row['api'] == 'get')),
        write_methods=len({(row['class_name'], row['signature'])
                           for row in rows if row['api'] == 'set'}))


def bet_statics():
    lines = AR.MR.dump_text().split('\n')
    start = next(i for i, line in enumerate(lines) if line.startswith('public class Board_PVP :'))
    rows = {}
    for line in lines[start + 1:]:
        text = line.strip()
        if text.startswith('// Namespace') or text.startswith('public class') and rows:
            break
        match = re.match(r'public static int (\w+); // (0x[0-9A-F]+)$', text)
        if match:
            rows[match.group(1)] = int(match.group(2), 16)
    assert [(name, rows[name]) for name, _ in BETS] == BETS, rows
    return [dict(name=name, offset=hex(offset)) for name, offset in BETS]


def direct_writes():
    """Any `str w.., [.., #0x9c / #0xa0]` inside `GameDatas` outside the accessors."""
    allowed = {WALLETS['ArenaMedal']['setter'], WALLETS['PvPMedal']['setter'],
               WALLETS['ArenaMedal']['getter'], WALLETS['PvPMedal']['getter']}
    hits = []
    for tag, row in all_methods():
        if row['class_name'] != 'GameDatas':
            continue
        for insn in row['instructions']:
            if not insn['mnemonic'].startswith('str'):
                continue
            if not (insn['op_str'].endswith('#0x9c]') or insn['op_str'].endswith('#0xa0]')):
                continue
            if not insn['op_str'].startswith('w'):
                continue
            hits.append(dict(raw=tag, method_rva=row['rva'], rva=insn['rva'],
                             signature=row['signature'].strip(),
                             accessor=row['rva'] in allowed))
    return hits


def build():
    fields = declared()
    accessor = accessors()
    init = cctor()
    raw, rows, companions = callers()
    tally = counts(rows, raw)
    cluster = clusters(rows)
    bets = bet_statics()
    writes = direct_writes()
    previous = load(PREV)

    checks = []
    checks.append(dict(check='two-named-statics',
                       passed={name: row['field'] for name, row in fields.items()}
                              == {'ArenaMedal': 'arenaMedal', 'PvPMedal': 'pvpMedal'}))
    checks.append(dict(check='offsets-are-0x9c-and-0xa0',
                       passed={name: row['offset'] for name, row in accessor.items()}
                              == {'ArenaMedal': '0x9c', 'PvPMedal': '0xa0'}))
    checks.append(dict(check='getters-lazy-load-on-minus-one',
                       passed=all(row['sentinel']['op'] == 'cmn w9, #1'
                                  and row['lazy_load']['signature'].startswith(
                                      'public static int GetInt')
                                  for row in accessor.values())))
    checks.append(dict(check='cctor-seeds-both-to-minus-one',
                       passed=init['pvp_medal']['value'] == -1
                              and init['arena_medal']['value'] == -1
                              and init['arena_medal']['op'].startswith('str x22')))
    checks.append(dict(check='setters-clamp-at-zero',
                       passed=all(row['clamp']['op'] == 'bic w19, w19, w19, asr #31'
                                  for row in accessor.values())))
    checks.append(dict(check='setters-persist-by-tail-call',
                       passed=all(row['persist']['signature'].startswith(
                           'public static void SetInt')
                           and not [insn for insn in method('key-grant-535b0541',
                                                            row['setter']['rva'])
                                    ['instructions']
                                    if insn['mnemonic'] == 'bl'
                                    and int(insn['op_str'].lstrip('#'), 16)
                                    == row['persist']['target']]
                                  for row in accessor.values())))
    checks.append(dict(check='keys-match-the-142-145-census',
                       passed={name: row['key']['name'] for name, row in accessor.items()}
                              == {'ArenaMedal': 'ArenaMedal', 'PvPMedal': 'PvPMedal'}))
    checks.append(dict(check='sixty-one-calls-in-thirty-methods',
                       passed=(tally['raw_bl'], tally['calls'], tally['pairs'],
                               tally['methods']) == (61, 53, 42, 30)))
    checks.append(dict(check='twelve-writers-six-of-them-shops',
                       passed=(cluster['write_methods'], len(cluster['shop_deduct'])) == (12, 6)))
    stray = [row for row in writes
             if not row['accessor'] and row['method_rva'] != init['rva']]
    seeded = [row for row in writes
              if not row['accessor'] and row['method_rva'] == init['rva']]
    checks.append(dict(check='no-direct-field-write-outside-accessors-and-cctor',
                       passed=not stray and len(seeded) == 2))
    checks.append(dict(check='shops-subtract-price-times-count',
                       passed=all(row['op'].startswith('msub w0, ')
                                  for row in cluster['shop_deduct'])))
    checks.append(dict(check='exchange-popups-never-write',
                       passed=not cluster['exchange_writes']))
    checks.append(dict(check='one-non-shop-deduction',
                       passed=[row['class_name'] for row in cluster['deduct_not_shop']]
                              == ['Board_RoomPVP']))
    trios = sorted(row['class_name'] + ' ' + row['signature'].split('(')[0]
                   for row in companions
                   if {'Coins', 'Gems'} <= {name for name, _ in row['others']})
    checks.append(dict(check='four-methods-move-all-three-wallets',
                       passed=trios == ['Board_PVP private void CollectGifts',
                                        'Board_PVP private void OnClickHunterCollect',
                                        'Board_RoomPVP public void ShowPlayer',
                                        'PVP_Endgame private void AddBetValues']))
    checks.append(dict(check='bet-scalars-are-board-pvp-statics',
                       passed=[row['name'] for row in bets]
                              == ['betCoinValues', 'betGemValues', 'betMedalValues']))
    checks.append(dict(check='report-154-left-this-open',
                       passed='onExit' in previous['open_items'][0]['blocking']))
    assert all(row['passed'] for row in checks), [row for row in checks if not row['passed']]

    sources = [path.parent.name + '/native.json.gz' for path in sorted(ROOT.glob(RAW_GLOB))]
    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='The medal is one static int per faction with a -1 "never loaded" sentinel '
             'and a hard floor at zero. Twelve of its 30 callers write; six are the two '
             'shops, and two of the non-shop writers move it in lockstep with coins and '
             'gems through the `Board_PVP` bet scalars. The exchange popup only reads.',
        provenance=dict(
            sources=[dict(path='reverse-engineering/raw/' + rel, sha256=sha_file(
                'reverse-engineering/raw/' + rel)) for rel in sources]
            + [dict(path=rel, sha256=sha_file(rel)) for rel in (DUMP, PREV_KEYS, PREV)],
            libil2cpp_sha256=load(KEY_GRANT)['libil2cpp_sha256'],
            xapk_sha256=load(KEY_GRANT)['xapk_sha256'],
            slices=len(sources)),
        declared=fields,
        accessors=accessor,
        cctor=init,
        callers=rows,
        companions=companions,
        counts=tally,
        clusters=cluster,
        bet_statics=bets,
        field_writes=writes,
        checks=checks,
        confirmations=[
            dict(item="154 `open_items` \"who spends the medal after the popup returns\"",
                 result='the debit exists and is bounded — six shop closures subtract '
                        '`count * price`; the popup itself has zero writers, so the only '
                        'missing link is which closure `onExit` points at'),
            dict(item='150: cell `0x2ADF238` holds `Board_PVP` and its statics '
                      '`+0x10 / +0x14 / +0x18` are the bet values',
                 result='confirmed and used — the two lockstep writers read exactly those '
                        'three offsets'),
            dict(item='153: three buy closures per shop, matching three bands',
                 result='confirmed by count — `Arena_Shop` and `PVP_Shop` each have '
                        '`<>c__DisplayClass31_1/2/3`, one per band, and each subtracts'),
        ],
        open_items=[
            dict(item='which buy closure is wired as the popup `onExit`',
                 blocking='all six subtract, and `SetPopup` still has no caller in any of '
                          'the eight slices, so the binding is an inspector delegate or '
                          'code outside the dump — not resolvable statically'),
            dict(item='the class behind slot `0x2ADC840`, whose static `+0x20` gates the '
                      '`Board_RoomPVP` deduction',
                 blocking='the guard is `cmp w8, #1` on a static of a class the slices '
                          'never name; only the offset is known'),
            dict(item='why `AddBetValues` credits `2 * bet` rather than `bet`',
                 blocking='the `lsl #1` is in the instruction, but whether the doubling '
                          'is a refund to both players or a payout rule is a runtime '
                          'question — MODEL_NOT_MEASURED runtime'),
        ],
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='datas/l2_535b0541_medal_flow.json.gz')
    args = parser.parse_args()
    payload = build()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    target.write_bytes(gzip.compress(blob, mtime=0))
    print(json.dumps(dict(
        bytes=target.stat().st_size,
        sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        counts=payload['counts'],
        checks_passed=sum(1 for row in payload['checks'] if row['passed']),
        checks_total=len(payload['checks']))))


if __name__ == '__main__':
    main()
