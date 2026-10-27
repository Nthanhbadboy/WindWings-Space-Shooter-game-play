#!/usr/bin/env python3
"""What is left in lane #29/#30, and which of it is still reachable.

167 closed the xref half of the reward row. What remains in the lane is a list of
56 open items (`open_items_audit`): some already answered by an artifact but never
marked, some waiting on the device, and some that look "unread" only because the
rationale was written too strongly. This tool sweeps that residue once:

1. **The `ArenaManager.rewards` consumer exists.** 139 recorded "no method in this
   raw indexes `ArenaManager.rewards` (+0x38)" and left the item open; the same
   artifact's own `reader` block has it. The chain is
   `Board_Arena.SetStatusRank` (22793460) -> `SetRewards` (22794144) ->
   `GetRewards` (22795496), and the index is
   `rewards[userProfile.arenaRank]` guarded by the array length and by
   `userProfile.status`, with `+0x28` passed along as the second argument.
2. **The daily free-pack amount is a literal.** 132 left "per-call pack amount for
   the 20 SaveDataReward clones" open because the value arrives as `_value`. It
   does — and the only call site in the eight slices (19187472) sets
   `w2 = 1` at 19187452, with `_device = null`, `_idDrone = w21`, `_index = w23`.
   So all twenty store clones receive one unit.
3. **Three "absent from the raws" rationales are too strong.** The *bodies* of
   `MyLibrary.ToRoman` (21103836) and `LanguageManager.GetText` (21202600) are in
   none of the eight slices, but the calls are: 2 and 127 sites. `GameConfig`'s
   `ReplaceDatas` (19049040) has 2 call sites while its `..cctor` (19082168) and
   `SetupDatas` (19042256) have none. Absent body is not absent path.
4. **What cannot be read here stays named.** The two `InitializeArray` handle
   slots (133) need the global-metadata usage table, which is not in the repo;
   the served values need the device. Both are listed, not guessed.
"""
import argparse
import functools
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import buy_delegate as BD  # noqa: E402

AUDIT = 'datas/l2_535b0541_open_items_audit.json.gz'
PREV139 = 'datas/l2_535b0541_arena_rewards.json.gz'
PREV132 = 'datas/l2_535b0541_key_sources.json.gz'
PREV133 = 'datas/l2_535b0541_pvp_hunter_reward_table.json.gz'
ARTIFACT = 'datas/l2_535b0541_lane_residue.json.gz'

SET_STATUS_RANK = 22793460
SET_REWARDS = 22794144
GET_REWARDS = 22795496
SAVE_DATA_REWARD = 19188220

ABSENT = [('MyLibrary.ToRoman', 21103836), ('LanguageManager.GetText', 21202600),
          ('GameConfig..cctor', 19082168), ('GameConfig.SetupDatas', 19042256),
          ('GameConfig.ReplaceDatas', 19049040)]


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


def text(insn):
    return insn['mnemonic'] + ' ' + insn['op_str']


@functools.lru_cache(maxsize=None)
def methods():
    return BD.slices()


def method_rva(klass, rva):
    row = methods()[(klass, rva)]
    return dict(rva=rva, class_name=klass, size=row['size'], signature=row['signature'],
                instructions=len(row['instructions']))


def instruction(klass, rva, insn_rva):
    for insn in methods()[(klass, rva)]['instructions']:
        if insn['rva'] == insn_rva:
            return dict(rva=insn_rva, op=text(insn))
    raise KeyError('%s+%d has no instruction at %d' % (klass, rva, insn_rva))


def callers(target):
    """Every `bl`/`b` site that resolves to `target`, deduped across slices."""
    out = {}
    for (klass, rva), row in methods().items():
        for insn in row['instructions']:
            if BD.call_target(insn) == target:
                out[(klass, rva, insn['rva'])] = dict(class_name=klass, caller=rva,
                                                     call=insn['rva'],
                                                     tail=insn['mnemonic'] == 'b',
                                                     signature=row['signature'])
    return [out[key] for key in sorted(out)]


def rewards_chain():
    """139's open item, closed with 139's own window plus the caller xref."""
    set_rewards = method_rva('Board_Arena', SET_REWARDS)
    reader = load(PREV139)['reader']
    window = [
        instruction('Board_Arena', SET_REWARDS, 22795324),   # ldr x8, [x0, #0xb8]
        instruction('Board_Arena', SET_REWARDS, 22795328),   # ldr x8, [x8, #0x38]
        instruction('Board_Arena', SET_REWARDS, 22795332),   # cbz x8
        instruction('Board_Arena', SET_REWARDS, 22795336),   # ldrsw x9, [x20, #0x1c]
        instruction('Board_Arena', SET_REWARDS, 22795340),   # ldr w10, [x8, #0x18]
        instruction('Board_Arena', SET_REWARDS, 22795344),   # cmp w9, w10
        instruction('Board_Arena', SET_REWARDS, 22795348),   # b.hs
        instruction('Board_Arena', SET_REWARDS, 22795352),   # add x8, x8, x9, lsl #3
        instruction('Board_Arena', SET_REWARDS, 22795356),   # ldr x1, [x8, #0x20]
        instruction('Board_Arena', SET_REWARDS, 22795360),   # ldr w2, [x20, #0x28]
        instruction('Board_Arena', SET_REWARDS, 22795380),   # bl GetRewards
    ]
    return dict(
        set_rewards=set_rewards,
        set_status_rank=method_rva('Board_Arena', SET_STATUS_RANK),
        get_rewards=method_rva('Board_Arena', GET_REWARDS),
        callers=dict(set_rewards=callers(SET_REWARDS), get_rewards=callers(GET_REWARDS)),
        window=window,
        rule='rewards = [x0+0xb8]+0x38; idx = userProfile.arenaRank (+0x1c); guard idx < '
             'rewards.Length (+0x18); element = [rewards + idx*8 + 0x20]; second argument = '
             'userProfile.status (+0x28)',
        prev139=dict(read_rva=reader['read_rva'], rule=reader['rule'],
                     open_claim='no method in this raw indexes `ArenaManager.rewards` (+0x38)'))


def save_data_reward():
    """132's open item: the `_value` operand at the only `SaveDataReward` site."""
    sites = callers(SAVE_DATA_REWARD)
    site = sites[0] if sites else None
    profile = dict(call_site=site, arguments={})
    if site is not None:
        klass, caller, call = site['class_name'], site['caller'], site['call']
        insns = methods()[(klass, caller)]['instructions']
        position = next(number for number, insn in enumerate(insns) if insn['rva'] == call)
        wanted = {'index': ('w1',), 'value': ('w2',), 'device': ('x3',), 'idDrone': ('w4',)}
        for name, registers in wanted.items():
            found = None
            for number in range(position - 1, -1, -1):
                insn = insns[number]
                head = insn['op_str'].split(', ')[0]
                if head in registers:
                    found = dict(rva=insn['rva'], op=text(insn))
                    break
                if insn['mnemonic'] in ('bl', 'b') and BD.call_target(insn) == SAVE_DATA_REWARD:
                    break
            profile['arguments'][name] = found
    return dict(method=method_rva('TimeFreeRewardPack', SAVE_DATA_REWARD),
                call_sites=len(sites), **profile)


def absence():
    """Body present? call sites? for the five RVAs the audit calls unreadable."""
    rows = []
    for name, rva in ABSENT:
        present = [klass for (klass, method) in methods() if method == rva]
        sites = callers(rva)
        rows.append(dict(name=name, rva=rva, body_in_slices=sorted(set(present)),
                         bodies=len(present), call_sites=len(sites),
                         examples=[site['call'] for site in sites[:3]],
                         signature=BD.name(rva)['signature']))
    return rows


def census():
    audit = load(AUDIT)
    addressed = {}
    for item in audit['items']:
        if item['n'] in (11, 12, 29, 39, 40, 49):
            addressed[item['n']] = dict(item=item['item'], verdict=item['verdict'],
                                        report=item['report'], closer=item.get('closer'),
                                        why=item.get('blocking') or item.get('reason'))
    return dict(totals=audit['totals'], addressed=addressed)


def shop_data():
    """Is there a serialized price/stock table anywhere in the extracted assets?

    127's open item says the medal-shop prices and stock come from "the shop config
    arrays, which no report in the lane decodes". This settles whether the numbers
    exist in the APK's serialized data at all.
    """
    csvs = sorted(ROOT.glob('reverse-engineering/scriptableobjects/*.csv'))
    headers = {}
    for path in csvs:
        with path.open('r', encoding='utf-8', errors='replace') as handle:
            line = handle.readline()
        headers[path.name] = [part.strip('"') for part in line.strip().split(',')]
    money = {}
    for name, columns in headers.items():
        hits = [column for column in columns
                if any(word in column.lower() for word in ('cost', 'price', 'stock'))]
        if hits:
            money[name] = sorted(set(hits))
    shop_pack = [path.name for path in
                 ROOT.glob('reverse-engineering/scriptableobjects/Shop_Pack*')]
    return dict(tables=len(csvs), price_columns=money, shop_pack_assets=shop_pack,
                data_shop_pack=headers.get('DataShopPack.csv', []))


def metadata_present():
    """Is the metadata table that would resolve the 133 handle slots in the repo?"""
    names = ['global-metadata.dat', 'global-metadata.dat.gz', 'metadata.dat']
    return sorted(str(path.relative_to(ROOT)) for name in names
                  for path in ROOT.rglob(name) if '.git/' not in str(path))


def check(rows, name, passed, detail=None):
    rows.append(dict(name=name, passed=bool(passed), detail=detail))


def run_checks(chain, pack, absent, audit, meta, shop):
    checks = []

    # -- the census --------------------------------------------------------
    # 170 refreshed the audit to read this report and 169, so the three checks below
    # assert the *current* agreement instead of the stale counts this report found.
    check(checks, 'the-audit-still-has-56-items', audit['totals']['items'] == 56,
          audit['totals'])
    check(checks, 'the-two-items-this-report-closes-are-closed-in-the-audit',
          audit['addressed'][11]['verdict'] == 'CLOSED'
          and audit['addressed'][11]['closer'] == 168
          and audit['addressed'][29]['verdict'] == 'CLOSED'
          and audit['addressed'][29]['closer'] == 168,
          {key: (audit['addressed'][key]['verdict'], audit['addressed'][key]['closer'])
           for key in (11, 29)})
    # 180: 149 had already bound both handle slots, so 39/40 are closed, not narrowed.
    check(checks, 'the-two-handle-slot-items-are-closed-by-149',
          audit['addressed'][39]['verdict'] == 'CLOSED'
          and audit['addressed'][40]['verdict'] == 'CLOSED'
          and audit['addressed'][39]['closer'] == 149
          and audit['addressed'][40]['closer'] == 149
          and '0x2ae0010' in json.dumps(load(PREV133)['table']) +
          json.dumps(audit['addressed']), audit['addressed'][39])

    # -- 139: the rewards consumer ---------------------------------------
    check(checks, 'the-rewards-consumer-is-board_arena.setrewards',
          chain['set_rewards']['signature'].startswith('private void SetRewards(')
          and chain['set_rewards']['size'] == 1344, chain['set_rewards'])
    check(checks, 'setrewards-reads-the-rewards-slot',
          chain['window'][0]['op'] == 'ldr x8, [x0, #0xb8]'
          and chain['window'][1]['op'] == 'ldr x8, [x8, #0x38]'
          and chain['window'][1]['rva'] == 22795328, chain['window'][:2])
    check(checks, 'the-index-is-the-profile-rank',
          chain['window'][3]['op'] == 'ldrsw x9, [x20, #0x1c]', chain['window'][3])
    check(checks, 'the-guard-is-the-array-length',
          chain['window'][4]['op'] == 'ldr w10, [x8, #0x18]'
          and chain['window'][5]['op'] == 'cmp w9, w10'
          and chain['window'][6]['op'].startswith('b.hs'), chain['window'][4:7])
    check(checks, 'the-element-stride-is-eight-bytes',
          chain['window'][7]['op'] == 'add x8, x8, x9, lsl #3'
          and chain['window'][8]['op'] == 'ldr x1, [x8, #0x20]', chain['window'][7:9])
    check(checks, 'the-second-argument-is-the-profile-status',
          chain['window'][9]['op'] == 'ldr w2, [x20, #0x28]', chain['window'][9])
    check(checks, 'setrewards-hands-the-row-to-getrewards',
          chain['window'][10]['rva'] == 22795380
          and chain['window'][10]['op'] == 'bl #0x15bd4e8', chain['window'][10])
    check(checks, 'getrewards-is-the-139-method',
          chain['get_rewards']['rva'] == GET_REWARDS
          and 'GetRewards(string rankSetup, int userRank)' in chain['get_rewards']['signature'],
          chain['get_rewards'])
    check(checks, 'setrewards-has-exactly-one-caller',
          len(chain['callers']['set_rewards']) == 1
          and chain['callers']['set_rewards'][0]['call'] == 22793992,
          chain['callers']['set_rewards'])
    check(checks, 'that-caller-is-setstatusrank',
          chain['callers']['set_rewards'][0]['caller'] == SET_STATUS_RANK
          and chain['set_status_rank']['signature'].startswith('private void SetStatusRank('),
          chain['set_status_rank'])
    check(checks, 'getrewards-has-exactly-one-caller',
          len(chain['callers']['get_rewards']) == 1
          and chain['callers']['get_rewards'][0]['call'] == 22795380,
          chain['callers']['get_rewards'])
    check(checks, '139-read-rule-and-open-claim-disagree-with-each-other',
          chain['prev139']['read_rva'] == 22795328
          and '+0x38' in chain['prev139']['open_claim'], chain['prev139'])

    # -- 132: the free-pack amount ---------------------------------------
    check(checks, 'savedatareward-has-one-call-site', pack['call_sites'] == 1,
          pack['call_sites'])
    check(checks, 'that-site-is-in-timefreerewardpack.getrewards',
          pack['call_site']['class_name'] == 'TimeFreeRewardPack'
          and pack['call_site']['call'] == 19187472
          and pack['call_site']['caller'] == 19186908, pack['call_site'])
    check(checks, 'the-value-operand-is-the-literal-one',
          pack['arguments']['value']['op'] == 'mov w2, #1'
          and pack['arguments']['value']['rva'] == 19187452, pack['arguments']['value'])
    check(checks, 'the-device-operand-is-null',
          pack['arguments']['device']['op'] == 'mov x3, xzr', pack['arguments']['device'])
    check(checks, 'the-index-and-drone-operands-are-registers',
          pack['arguments']['index']['op'] == 'mov w1, w23'
          and pack['arguments']['idDrone']['op'] == 'mov w4, w21', pack['arguments'])
    check(checks, 'savedatareward-is-one-method-with-one-call-site',
          pack['method']['size'] == 1108 and pack['method']['instructions'] == 277
          and pack['call_sites'] == 1, pack['method'])

    # -- the "absent" rationales -----------------------------------------
    by_name = {row['name']: row for row in absent}
    check(checks, 'toroman-body-is-absent-but-it-is-called',
          not by_name['MyLibrary.ToRoman']['body_in_slices']
          and by_name['MyLibrary.ToRoman']['call_sites'] == 2, by_name['MyLibrary.ToRoman'])
    check(checks, 'gettext-body-is-absent-but-it-is-called-127-times',
          not by_name['LanguageManager.GetText']['body_in_slices']
          and by_name['LanguageManager.GetText']['call_sites'] == 127,
          by_name['LanguageManager.GetText'])
    check(checks, 'gameconfig-cctor-and-setupdatas-have-no-site-at-all',
          by_name['GameConfig..cctor']['call_sites'] == 0
          and by_name['GameConfig.SetupDatas']['call_sites'] == 0,
          {key: by_name[key]['call_sites']
           for key in ('GameConfig..cctor', 'GameConfig.SetupDatas')})
    check(checks, 'gameconfig-replacedatas-is-called-twice',
          by_name['GameConfig.ReplaceDatas']['call_sites'] == 2,
          by_name['GameConfig.ReplaceDatas'])
    check(checks, 'all-five-rvas-still-resolve-to-a-name',
          all(row['signature'] for row in absent), [row['signature'] for row in absent])

    # -- 127: the shop prices are not in the serialized data --------------
    check(checks, 'no-serialized-table-holds-a-price-or-stock-number',
          list(shop['price_columns']) == ['Shop_Cell.csv']
          and all(column.startswith('text') for column in shop['price_columns']['Shop_Cell.csv']),
          shop['price_columns'])
    check(checks, 'the-only-shop-asset-carries-sprites-and-lists-only',
          not any('cost' in column or 'price' in column or 'stock' in column
                  for column in shop['data_shop_pack'])
          and any('m_PathID' in column for column in shop['data_shop_pack']),
          len(shop['data_shop_pack']))
    check(checks, 'the-asset-inventory-is-126-tables', shop['tables'] == 126, shop['tables'])
    check(checks, 'there-is-no-shop_pack-asset-to-read',
          shop['shop_pack_assets'] == [], shop['shop_pack_assets'])

    # -- what stays blocked ----------------------------------------------
    check(checks, 'the-metadata-table-is-not-in-this-repo', meta == [], meta)
    check(checks, 'the-two-133-slots-stay-named-not-guessed',
          '0x2ae0010' in json.dumps(load(PREV133)['table']['reward_values']['blocking'])
          or 'metadata usage table' in
          load(PREV133)['table']['reward_values']['blocking'],
          load(PREV133)['table']['reward_values']['blocking'])
    return checks


def build(output):
    chain = rewards_chain()
    pack = save_data_reward()
    absent = absence()
    audit = census()
    meta = metadata_present()
    checks = run_checks(chain, pack, absent, audit, meta, shop_data())
    payload = dict(
        schema=1,
        boundary='static sweep of the lane residue over the eight pinned slices and the pinned '
                 'lane artifacts; no FDE, runtime, emulator, or device',
        evidence='STATIC_ONLY_ORIGINAL_APK',
        census=audit,
        rewards_chain=chain,
        save_data_reward=pack,
        absence=absent,
        shop_data=shop_data(),
        closed=[dict(n=11, report=139, item=audit['addressed'][11]['item'],
                     how='the consumer is `Board_Arena.SetRewards`; the chain is '
                         'SetStatusRank -> SetRewards -> GetRewards and 139 already had the window'),
                dict(n=29, report=132, item=audit['addressed'][29]['item'],
                     how='the only `SaveDataReward` call site passes the literal 1 in `w2`')],
        corrected=[dict(n=12, report=139,
                        was='RVA 21103836 appears in 0 pinned raws',
                        now='the body is absent, but two call sites reach it (19885148, 21285196)'),
                   dict(n=49, report=137,
                        was='LanguageManager.GetText is not in any pinned raw',
                        now='the body is absent, but 127 call sites reach it')],
        blocked=[dict(n=39, report=133, why='the metadata usage table that names handle slot '
                                            '0x2ae0010 is not in this repo'),
                 dict(n=40, report=133, why='same for 0x2ae0018 (rewardScales)'),
                 dict(n=18, report=146, why='array length is serialized data, not code'),
                 dict(n=30, report=132, why='Board_PVP.rewardTypes/rewardValues are instance '
                                            'arrays filled at runtime'),
                 dict(n=9, report=127, why='no serialized price/stock column exists in the 251 '
                                           'extracted ScriptableObject tables and there is no '
                                           'Shop_Pack asset; the prices are served, not shipped')],
        totals=dict(closed=2, corrected=2, blocked=5,
                    call_sites_scanned=sum(row['call_sites'] for row in absent),
                    checks_passed=sum(1 for row in checks if row['passed']),
                    checks_total=len(checks)),
        provenance=dict(
            inputs=[dict(path=path, sha256=sha_file(path))
                    for path in (AUDIT, PREV139, PREV132, PREV133, BD.DUMP, 'reverse-engineering/il2cpp/ia-resolved.json')],
            slices=[dict(path='reverse-engineering/raw/%s/native.json.gz' % klass,
                         sha256=sha_file('reverse-engineering/raw/%s/native.json.gz' % klass))
                    for klass, _ in slices()]),
        checks=checks,
    )
    blob = json.dumps(payload, sort_keys=True, indent=1, ensure_ascii=False).encode('utf-8')
    packed = gzip.compress(blob, mtime=0)
    if output:
        (ROOT / output).write_bytes(packed)
    return payload, packed


@functools.lru_cache(maxsize=None)
def slices():
    out = []
    for path in sorted(ROOT.glob(BD.RAW_GLOB)):
        out.append((path.parent.name, path))
    return tuple(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--output', default=ARTIFACT)
    args = parser.parse_args()
    payload, packed = build(args.output)
    failed = [row['name'] for row in payload['checks'] if not row['passed']]
    print(json.dumps(dict(bytes=len(packed), sha256=hashlib.sha256(packed).hexdigest(),
                          checks_passed=payload['totals']['checks_passed'],
                          checks_total=payload['totals']['checks_total'],
                          failed=failed), indent=1))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
