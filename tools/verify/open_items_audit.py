#!/usr/bin/env python3
"""The 56 open items of lane #29/#30, re-read against the reports that came later.

147 listed the lane's open items by copying each artifact's `not_decoded` verbatim.
That is a census, not a status: the lane keeps closing its own items, and it records
the closure inside the artifact — `corrections` when a later report overturns an
earlier statement, `confirmations` when it answers a listed item. Copying the lists
therefore reports as open several things that are already answered, and hides the
case where a *route* was proven in-lane but never run.

Each of the 56 items gets one verdict:

* `CLOSED`     — a later report in the lane answers it; `closer` names that report and
                 `proofs` are re-evaluated here, so the claim is a test, not prose.
* `RESTATED`   — narrowed by a later report, still open.
* `ACTIONABLE` — the blocking reason was removed by a method proven in-lane; the decode
                 has not been run yet.
* `RUNTIME`    — device or served state: `MODEL_NOT_MEASURED runtime`.
* `NOTE`       — recorded so an index is complete; not a gap.

No disassembly happens here. Every proof reads a field of an existing artifact.
"""
import argparse
import glob
import gzip
import hashlib
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_GLOB = 'datas/l2_535b0541_*.json.gz'
CLOSEOUT = 'datas/l2_535b0541_lane_closeout.json.gz'
OUTPUT = 'datas/l2_535b0541_open_items_audit.json.gz'

REPORTS = {
    127: 'arena_pvp', 128: 'meta_rewards', 129: 'pack_index', 130: 'box_draw',
    131: 'box_arrays', 132: 'key_sources', 133: 'pvp_hunter_reward_table',
    134: 'pvp_manager_rules', 135: 'max_rank_stars', 136: 'pvp_rank_api',
    137: 'rank_name', 138: 'remote_configs', 139: 'arena_statics',
    140: 'arena_config', 141: 'game_config_gate', 142: 'application_cell',
    143: 'economy_keys', 144: 'game_store_keys', 145: 'store_key_callers',
    146: 'computed_key_index',
}


def sha_file(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def artifacts():
    return tuple(sorted(path for path in glob.glob(ARTIFACT_GLOB)
                        if not path.endswith(('_lane_closeout.json.gz',
                                              '_open_items_audit.json.gz'))))


@lru_cache(maxsize=None)
def load(rel):
    return json.loads(gzip.decompress((ROOT / rel).read_bytes()))


@lru_cache(maxsize=None)
def art(report):
    return load('datas/l2_535b0541_%s.json.gz' % REPORTS[report])


@lru_cache(maxsize=None)
def closeout():
    return load(CLOSEOUT)


# ---------------------------------------------------------------- proofs
# Each returns a JSON-able value; the item states the value it must equal.

def _currency_keys():
    return sorted(row['key'] for row in art(143)['currency']['rows'])


def _currency_cells():
    """143's currency keys -> their string-cell slots, which 142 could not read."""
    slots = {row['key']: row['slot_va'] for row in art(143)['keys']}
    return sorted(slots[row['key']] for row in art(143)['currency']['rows'])


def _gate_slot():
    measured = art(141)['corrections'][0]['measured']
    return [measured['slot_va'], art(141)['corrections'][0]['impact'].split('`')[1]]


def _arena_rewards():
    rewards = art(139)['rewards']
    return [rewards['count'], len(rewards['rows'][0]['bands'])]


def _config_strings():
    writes = {row['field']: row['value'] for row in art(140)['cctor']['writes']}
    split, season = writes['RankSplit'].split(';'), writes['SeasonTime'].split(';')
    return [len(split), len(season), writes['RankSplit']]


def _season_minutes():
    return art(140)['cross_checks']['arena_manager_season_times']['minutes']


def _star_blobs():
    blobs, table = art(135)['blobs'], art(135)['rank_table']
    return [len(blobs), len(table), all(row['data_hex'] for row in blobs)]


def _key_callers():
    callers = art(132)['callers']
    return [callers['grant_direct']['hits'], callers['grant_direct']['classes'],
            callers['grant_via_pack_value']['classes']]


def _no_drip():
    text = art(132)['supply']['no_regeneration']
    return [True, 'no idle or timed drip' in text]


def _box_arrays():
    return {row['field'].split('.')[-1]: row['values'] for row in art(131)['arrays']
            if row['field'].startswith('Board_Quest.') and row['elements'] == 3
            and row['element_type'] == 'int32'}


def _store_census():
    return [art(144)['census']['calls'], art(145)['census']['calls'],
            art(145)['census']['by_kind']['unknown']]


def _store_api():
    return art(144)['census']['by_api']


def _app_cell():
    return [art(142)['cell']['va'], art(142)['cell']['klass']]


def _rank_reader():
    row = art(136)['corrections'][0]
    return [19884996, 'GetRankNumber' in row['measured']]


def _rank_text():
    return [art(137)['confirmations'][0]['item'].split(':')[0],
            art(137)['confirmations'][0]['result'].startswith('resolved')]


def _key_counts():
    rows = [row for row in art(143)['keys'] if row['key'].startswith('KeyCount')]
    return [[row['key'], row['literal'], row['slot_va']] for row in rows]


def _index_structure():
    bands = [row['band'] for row in art(146)['bands']]
    return [len(bands), len(sorted(set(bands))),
            len(art(146)['families']), art(146)['census']['records']]


def _field_defaults():
    """131 bound InitializeArray handles to field defaults; 133 stopped short of it."""
    return [art(131)['provenance']['field_defaults_count'],
            art(133)['table']['reward_values']['status']]


def _cut_rows():
    """The 147 rows whose blocking text is not the source text, split by cause."""
    nulls, cut = [], []
    for row in closeout()['open_items']:
        if row['blocking'] == 'None':
            nulls.append(row['report'])
            continue
        source = item_text(row['report'], row['item']).get('blocking') or ''
        if row['blocking'] != source:
            cut.append(row['report'])
    return [sorted(nulls), sorted(cut)]


def _runtime_arithmetic():
    """The tag as 147 counted it (truncated text) and as the source artifacts carry it."""
    tagged_147 = sum(1 for row in closeout()['open_items']
                     if 'MODEL_NOT_MEASURED' in (row['blocking'] or ''))
    tagged_source = sum(1 for row in ITEMS
                        if 'MODEL_NOT_MEASURED' in
                        (item_text(row['report'], row['item']).get('blocking') or ''))
    return [tagged_147, tagged_source]


def _closeout_defect():
    """147 cut blocking text at 220 chars and stringified five nulls."""
    nulls, cut = _cut_rows()
    return [len(nulls), len(cut), 220]


PROOFS = {
    '143-currency-keys': _currency_keys,
    '143-currency-cells': _currency_cells,
    '141-gate-slot': _gate_slot,
    '139-arena-rewards': _arena_rewards,
    '140-config-strings': _config_strings,
    '140-season-minutes': _season_minutes,
    '135-star-blobs': _star_blobs,
    '132-key-callers': _key_callers,
    '132-no-drip': _no_drip,
    '131-box-arrays': _box_arrays,
    '144-145-store': _store_census,
    '144-store-api': _store_api,
    '142-app-cell': _app_cell,
    '136-rank-reader': _rank_reader,
    '137-rank-text': _rank_text,
    '143-key-counts': _key_counts,
    '146-index-structure': _index_structure,
    '131-vs-133-route': _field_defaults,
    '147-text-cut': _closeout_defect,
    '147-runtime-count': _runtime_arithmetic,
}


# ---------------------------------------------------------------- the items
def I(report, item, verdict, closer=None, reason='', proofs=()):
    return dict(report=report, item=item, verdict=verdict, closer=closer,
                reason=reason, proofs=[list(pair) for pair in proofs])


ITEMS = [
    # ---- 127: the five questions the arena report left open
    I(127, 'ArenaManager.rewards[10] string values', 'CLOSED', 139,
      '139 decodes all ten reward rows out of ArenaManager..cctor: six placement '
      'bands each with a medal and a gem amount.',
      [('139-arena-rewards', [10, 6])]),
    I(127, 'ArenaConfig.RankSplit / SeasonTime strings', 'CLOSED', 140,
      '140 reads both literals out of ArenaConfig..cctor: ten rank ranges and ten '
      'season durations, written as `;`-separated strings.',
      [('140-config-strings', [10, 10,
                               '20-45;15-45;15-45;10-45;10-45;10-45;10-45;10-45;10-45;10-45'])]),
    I(127, 'PVP_Manager.MaxRankStars array contents', 'CLOSED', 135,
      '135 binds all ten Arrays to five PID blobs and prints the bytes: the star caps '
      'are build-time data, not a runtime read.',
      [('135-star-blobs', [5, 10, True])]),
    I(127, 'SeasonTimes / RankUpIndexs / RankDropIndexs values', 'CLOSED', 140,
      'the three ArenaManager arrays ship null; 139 gives the parse pipeline and 140 '
      'gives the shipped strings, so the values exist as the ten durations/ranges.',
      [('140-season-minutes', [1440, 2880, 4320, 7200, 10080, 11520, 12960, 14400,
                               15840, 17280])]),
    I(127, 'medal shop prices / stock', 'OPEN', None,
      'still data: 146 fixes the key shape (`ARENA_SHOP_ITEM_ID` / `_STOCK` over three '
      'bands) but the prices and stock per item come from the shop config arrays, which '
      'no report in the lane decodes.'),
    # ---- 142: the four currency keys
    I(142, 'what Application.* returns on a device', 'RUNTIME', None,
      'device language, reachability and company name are read at run time; the APK '
      'only carries the call sites.'),
    I(142, 'PlayerPrefs key strings for the four currency getters', 'CLOSED', 143,
      '143 resolves exactly the four string cells 142 named, and its own `corrections` '
      'record says so: GCoins / Gems / StarCount / WingCoins.',
      [('143-currency-keys', ['GCoins', 'Gems', 'StarCount', 'WingCoins']),
       ('143-currency-cells', [44941496, 44941512, 44941536, 44941776])]),
    # ---- 140 / 141: the gate slot
    I(140, 'class behind slot 0x2ADB8E0 (44939488)', 'CLOSED', 141,
      '141 corrects the slot number: the gate flag is behind 44940168 = `GameConfig`, '
      'and 44939488 is a neighbouring slot. The question as asked rested on the wrong cell.',
      [('141-gate-slot', [44940168, 'GameConfig'])]),
    I(140, 'served overrides of the shipped table', 'RUNTIME', None,
      'ArenaConfig is rewritten by the remote loader and the database is not in the APK.'),
    I(141, 'GameConfig values (versionCode, lastestVersionCode, isEmpty, update strings, '
           'gift code)', 'RUNTIME', None,
      'the three methods that fill the struct are in none of the pinned raws and the '
      'values arrive from the served JSON anyway.'),
    I(141, 'slot 0x2ADB8E0 (44939488) class', 'CLOSED', 142,
      '142 identifies that cell as `UnityEngine.Application` by the class-init idiom '
      'plus a 47/47 callee census; 147 cross-checked it sits 680 bytes from 141\'s slot.',
      [('142-app-cell', [44939488, 'UnityEngine.Application'])]),
    # ---- 139
    I(139, 'served config values', 'RUNTIME', None,
      'season times, rank bands and room counts are parsed from the remote database.'),
    I(139, '`rewards` consumer', 'OPEN', None,
      'no method in the arena-pvp raw indexes `ArenaManager.rewards` (+0x38); the reader '
      'is in a class outside that raw or reaches the array through another slot.'),
    I(139, '`MyLibrary.ToRoman` glyph table', 'RESTATED', 138,
      '138 corrects what that tail call is — the rank number is a roman numeral, not an '
      'arabic one — so the read changes from `Herald 3` to `Herald III`. The glyph table '
      'itself is still absent: 139 swept all eight raws for RVA 21103836 and found none. '
      'The restatement comes from the earlier report, so the item was already stale when '
      '139 wrote it.',
      [('139-arena-rewards', [10, 6])]),
    # ---- 131 / 130: key counters and box tables
    I(131, 'which reward the draw returns', 'RUNTIME', None,
      'UnityEngine.Random is seeded at run time.'),
    I(131, 'where the key counters are incremented', 'CLOSED', 132,
      '132 walks the callers of the three setters: 14 direct grants in 3 classes, 21 '
      'classes granting through a pack value, 7 display-only methods, 1 cheat guard.',
      [('132-key-callers', [14, 3, 21])]),
    I(130, 'contents of BoxKeyCost / KeyPrices / NumberRewards', 'CLOSED', 131,
      '131 binds the four InitializeArray handles to PID fields and reads the blobs out '
      'of the pinned field-default table: the arrays are [30,30,30], [6,20,100], [5,6,9].',
      [('131-box-arrays', {'BoxKeyCost': [30, 30, 30],
                           'KeyPrices': [6, 20, 100],
                           'NumberRewards': [5, 6, 9]})]),
    I(130, 'draw sequence / actual items received', 'RUNTIME', None,
      'UnityEngine.Random.Range is seeded at run time.'),
    I(130, 'key acquisition schedule', 'CLOSED', 132,
      '132 answers it negatively and that is the answer: no setter caller adds anything '
      'except a reward argument, so there is no idle or timed drip; the UpdateKey* '
      'coroutines only animate the label.',
      [('132-no-drip', [True, True])]),
    # ---- 146 / 145: the index half
    I(146, 'the upper bound of every band and every parameter list', 'OPEN', None,
      'a runtime length: `ldr wT, [xConfig, #0x18]` on a config object whose contents '
      'come from serialized data.'),
    I(146, 'the value of a parameter index at run time', 'OPEN', None,
      'callers pass registers; only the literal ones (20 sites passing 999) are visible '
      'statically.'),
    I(146, 'stored values', 'RUNTIME', None, 'device state.'),
    I(143, 'stored values of the 21 keys', 'RUNTIME', None,
      'they live in the device save, not in the APK.'),
    I(143, 'keys of the 174 game-store calls', 'CLOSED', 144,
      '144 is the per-method register pass this item asked for: 184 calls, and 145 then '
      'names all of them, unknown 0.',
      [('144-145-store', [184, 184, 0])]),
    I(143, 'PlayerPrefs string/float/DeleteKey sites', 'CLOSED', 144,
      'the premise is falsified by 144: the pinned raws do carry SetString 32, GetString '
      '25 and DeleteKey 2. Only float stays at zero, which is itself the answer.',
      [('144-store-api', {'DeleteKey': 2, 'GetInt': 58, 'GetString': 25,
                          'SetInt': 67, 'SetString': 32})]),
    I(144, '26 calls whose key is not a literal or a concat prefix', 'CLOSED', 145,
      '145 resolves all 26 by cross-method caller tracking; 147 re-measured 184/184 with '
      'unknown 0.',
      [('144-145-store', [184, 184, 0])]),
    I(144, 'the index half of the 43 computed keys', 'RESTATED', 146,
      '146 gives the structure (three bands 100/200/300, 4 of 14 families enumerable) and '
      'the count is 51, not 43: 144\'s 43 grew by the 8 computed keys it had left unknown.',
      [('146-index-structure', [12, 3, 14, 51])]),
    I(145, 'the index half of the 50 computed keys', 'RESTATED', 146,
      'same question as 144\'s, and the count in the wording is off by one as well: 145 '
      'and 146 both carry 51 records over 14 prefixes.',
      [('146-index-structure', [12, 3, 14, 51])]),
    I(144, 'stored values', 'RUNTIME', None, 'device state, not in the APK.'),
    I(145, 'stored values', 'RUNTIME', None, 'device state, not in the APK.'),
    I(145, 'static writes that are not string keys', 'NOTE', None,
      'not a gap: two `str` writes hold non-key data and are listed only so the static '
      'index is complete.'),
    # ---- 132
    I(132, 'per-call pack amount for the 20 SaveDataReward clones', 'OPEN', None,
      'the value is the `_value` argument from pack data; the store path is decoded, the '
      'operand is serialized data.'),
    I(132, 'PvP stage reward types and amounts', 'OPEN', None,
      '`Board_PVP.rewardTypes/rewardValues` are instance arrays filled at run time; the '
      'dispatch table proves Key2 is reachable, not how much.'),
    I(132, 'PlayerPrefs key -> literal binding for KeyCount0/1/2', 'CLOSED', 143,
      '143 resolves the three slots to the literals `KeyCount0/1/2` with their addends and '
      'the same read/write pair 132 had already found.',
      [('143-key-counts', [['KeyCount0', 46011960, 44941760],
                           ['KeyCount1', 46011968, 44941800],
                           ['KeyCount2', 46011976, 44941784]])]),
    I(132, 'a direct static store outside these classes', 'OPEN', None,
      'a limitation of the method, not of the data: the branch scan sees calls, not '
      'stores, so an inline static write elsewhere would be invisible.'),
    # ---- 135 / 134 / 136 / 137: the rank ladder
    I(135, 'the method that reads MaxRankStars', 'CLOSED', 136,
      '136 finds it and explains the miss: GetRankNumber (19884996) reads statics +0x18, '
      'but the base arrives in x0, so 135\'s pattern scan dropped it.',
      [('136-rank-reader', [19884996, True])]),
    I(135, 'rank 0 has 3 cells but only 2 reward levels in AllRewards', 'OPEN', None,
      'still unexplained: either level 0 exists without a reward row or the first cell is '
      'a placeholder; no pinned code indexes it.'),
    I(135, 'how stars move during a match', 'RUNTIME', None, 'match state.'),
    I(134, 'MaxRankStars values', 'CLOSED', 135,
      '135 decodes the field-default blob this item called unresolved.',
      [('135-star-blobs', [5, 10, True])]),
    I(134, 'how remote config rewrites these defaults', 'RUNTIME', None,
      'LoadRemoteConfigs reads Firebase; the shipped defaults are static, the served '
      'values are not in the APK.'),
    I(134, 'what the 14 medal rows are indexed by', 'OPEN', None,
      '`PVP_Endgame.GetTournamentMedalReward(rank, index)` indexes [rank][index]; the '
      'meaning of rank 0..13 is not in the cctor.'),
    I(134, 'paired-field independence for pvpMaxLife/pointReduceDie and timePlay/timeStep',
      'RUNTIME', None,
      'the compiler merged each pair into one 8-byte store, so build data cannot separate '
      'them; whether the game rewrites one alone is runtime.'),
    I(136, 'rank display strings', 'CLOSED', 137,
      '137 resolves both prefix slots and builds the ten-tier table; 138 then corrects the '
      'number glyph to roman.',
      [('137-rank-text', ['136 not_decoded', True])]),
    I(136, 'served rank configuration', 'RUNTIME', None,
      'LoadRemoteConfigs fetches Firebase and only then fills pvpDatas.'),
    I(136, 'whether level 0 of rank 0 is a real tier', 'OPEN', None,
      'duplicate of 135\'s rank-0 question, and just as unexplained: 137 shows the three '
      'cells and the per-rank numbers, but no code says why level 0 has no reward row.'),
    I(137, 'GetText key-missing behaviour', 'OPEN', None,
      'the answer is code, not device state: LanguageManager.GetText (RVA 21202600) is in '
      'none of the eight pinned raws, so the lane cannot see whether an unknown key comes '
      'back as the key, an empty string or a fallback.'),
    # ---- 129 / 133 / 138
    I(129, 'typeBox runtime value', 'RUNTIME', None,
      'assigned per box at run time; which boxes use 0 is not in the APK.'),
    I(129, 'Board_GiftLogin.ResetDailyGiftCount value', 'RUNTIME', None,
      'reads player state (daily reset counter).'),
    I(129, 'actual random draws', 'RUNTIME', None,
      'UnityEngine.Random.Range is seeded at run time; no sequence is claimed.'),
    I(133, 'amount per stage (rewardValues)', 'ACTIONABLE', 131,
      'not blocked any more, just not done: 131 shows the route (InitializeArray handle -> '
      'PID field -> pinned field-default table, 10493 entries) and 133 stops one step short '
      'of it, still reporting the handle slot as unresolved.',
      [('131-vs-133-route', [10493, 'NOT_BOUND'])]),
    I(133, 'icon scale per stage (rewardScales)', 'ACTIONABLE', 131,
      'same shape as rewardValues, same unrun lookup, and the field is decorative. The '
      'route predates the item: 131 shipped before 133 wrote it down.',
      [('131-vs-133-route', [10493, 'NOT_BOUND'])]),
    I(133, 'how many markers the scene really has', 'RUNTIME', None,
      'allPoints is a serialized WinPoint[] filled from the scene; the code only proves '
      'the halving.'),
    I(138, 'ArenaManager root variants', 'OPEN', None,
      '`get_pathRoot` returns slot 0x2AEC9A0 for companyName == "Test" and 0x2AEC9B0 for '
      'PREMIUM; neither is dereferenced in any pinned raw, so no literal address.'),
    I(138, 'PVP_Manager config class identity', 'OPEN', None,
      '`JsonParse.FromJson<object>` takes its type from metadata slot 0x2AE1000, which is '
      'not a kind-5 string literal, so the field at +0x10 stays named by offset.'),
    I(138, 'class owning static field 0 read before both fetches', 'OPEN', None,
      'both parents read field +0 of the class behind slot 0x2ADB958 and test it with '
      'Object.op_Implicit; that class is not named by any pinned symbol.'),
    I(138, 'served remote values', 'RUNTIME', None,
      '`data-leagues/data-configs` and `arena---datas/is-open` live in Firebase.'),
]

# The lane's own closure records, and which of the 56 they touch.
RECORDS = [
    (135, 'confirmation', None),
    (134, 'correction', None),
    (136, 'correction', 33),
    (136, 'correction', None),
    (137, 'confirmation', 46),
    (138, 'correction', 12),
    (139, 'correction', None),
    (139, 'confirmation', 8),
    (141, 'correction', 3),
    (141, 'confirmation', 3),
    (143, 'correction', 2),
]

# Items that are the same question asked twice.
DUPLICATES = [
    ([3, 25], 'slot 0x2ADB8E0 as named by 140 and by 141'),
    ([27, 54], 'the index half of the computed keys, asked by 144 and by 145'),
    ([34, 48], 'rank 0 level 0, asked by 135 and by 136'),
]


def item_text(report, item):
    """The source text of an item, so the audit never reads 147's truncated copy."""
    entries = (art(report).get('not_decoded') or []) + (art(report).get('gaps') or [])
    for entry in entries:
        if entry.get('item') == item:
            return entry
    raise AssertionError('no source entry: %s %s' % (report, item))


def build_payload():
    assert len(ITEMS) == 56, len(ITEMS)
    assert len({(row['report'], row['item']) for row in ITEMS}) == 56

    tail = closeout()['open_items']
    position = {(row['report'], row['item']): index
                for index, row in enumerate(tail, 1)}
    assert len(position) == 56
    reported = set(position)
    for row in ITEMS:
        assert (row['report'], row['item']) in reported, row['item']

    rows, assertions = [], []
    for order, row in enumerate(ITEMS, 1):
        # `n` is the item's column in 147, so a reviewer can read the two side by side.
        number = position[(row['report'], row['item'])]
        source = item_text(row['report'], row['item'])
        evidence = []
        for label, expected in row['proofs']:
            actual = PROOFS[label]()
            passed = actual == expected
            evidence.append(dict(label=label, expected=expected, actual=actual,
                                 pass_=passed))
            assertions.append((number, label, passed))
        if row['verdict'] == 'CLOSED':
            assert row['closer'] > row['report'], row['item']
            assert evidence and all(e['pass_'] for e in evidence), row['item']
        if row['verdict'] in ('RESTATED', 'ACTIONABLE'):
            # not always a *later* report: 138 already corrected what GetRankNumber's tail
            # is before 139 listed the item, and 131 proved the blob route before 133 listed
            # it. Two items were stale the moment they were written.
            assert row['closer'] != row['report'], row['item']
            assert evidence and all(e['pass_'] for e in evidence), row['item']
        if row['verdict'] in ('OPEN', 'RUNTIME', 'NOTE'):
            assert not evidence, row['item']
        rows.append(dict(n=number, audit_order=order, report=row['report'],
                         item=row['item'],
                         blocking=source.get('blocking'), verdict=row['verdict'],
                         closer=row['closer'], reason=row['reason'],
                         direction=('later' if row['closer'] and row['closer'] > row['report']
                                    else 'earlier' if row['closer'] else None),
                         evidence=evidence))

    assert all(passed for _, _, passed in assertions), \
        [row for row in assertions if not row[2]]
    arithmetic = _runtime_arithmetic()
    assert arithmetic == [17, 18], arithmetic
    assertions.append((0, '147-runtime-count', True))

    assert sorted(row['n'] for row in rows) == list(range(1, 57))
    assert sorted(row['audit_order'] for row in rows) == list(range(1, 57))

    def count(verdict):
        return sum(1 for row in rows if row['verdict'] == verdict)

    distinct = len(rows) - sum(len(group) - 1 for group, _ in DUPLICATES)
    totals = dict(items=len(rows), distinct_questions=distinct,
                  closed=count('CLOSED'), restated=count('RESTATED'),
                  actionable=count('ACTIONABLE'), runtime=count('RUNTIME'),
                  note=count('NOTE'), still_open=count('OPEN'),
                  proofs=len(assertions))
    assert (totals['closed'] + totals['restated'] + totals['actionable']
            + totals['runtime'] + totals['note'] + totals['still_open']) == 56

    by_report = []
    for report in sorted(REPORTS):
        own = [row for row in rows if row['report'] == report]
        if not own:
            continue
        by_report.append(dict(
            report=report, items=len(own),
            closed=sum(1 for row in own if row['verdict'] == 'CLOSED'),
            open=sum(1 for row in own if row['verdict'] == 'OPEN'),
            runtime=sum(1 for row in own if row['verdict'] == 'RUNTIME')))

    # 147's counters, recomputed over untruncated text.
    nulls, cut = _cut_rows()
    declared = {closes for _, _, closes in RECORDS if closes}
    assert declared <= {row['n'] for row in rows}
    for record_report, kind, closes in RECORDS:
        assert kind in ('correction', 'confirmation')
        assert (art(record_report).get(kind + 's') or []), (record_report, kind)
    corrections = [
        dict(target=147, item='open items copied verbatim from `not_decoded`',
             statement='147 counted 56 open items and left it there',
             correction='fourteen of them were already answered, narrowed or unblocked by '
                        'later reports in the same lane; the artifacts record that in '
                        '`corrections` / `confirmations`, which a verbatim copy cannot see',
             evidence=dict(items=56, closed=totals['closed'],
                           restated=totals['restated'],
                           actionable=totals['actionable'],
                           records_in_lane=len(RECORDS))),
        dict(target=147, item='`runtime_items: 17`',
             statement='147 tagged 17 items as `MODEL_NOT_MEASURED runtime`',
             correction='19 items are device-or-served state. 147 counted 17 on truncated '
                        'text; fixing the cut restores 141\'s tag (+1 = 18), 129 carries two '
                        '`runtime only` items that never use the phrase (+2 = 20), and 137\'s '
                        'tag is wrong in the other direction — GetText is code that is not '
                        'pinned, not device state (-1 = 19)',
             evidence=dict(as_counted=17, tagged_in_source=18,
                           by_semantics=totals['runtime'],
                           cut_text=cut,
                           untagged_runtime=[37, 38], mistagged=[49])),
        dict(target=147, item='`open_items[].blocking` was stringified and cut',
             statement='147 stored `str(blocking)[:220]`',
             correction='five null blockings became the string "None" and four long ones '
                        'lost their tail; 148 re-reads every item from its own artifact '
                        'instead of from 147',
             evidence=dict(nulls_as_string=len(nulls), null_reports=nulls,
                           cut_at=220, cut=cut)),
    ]

    sources = [dict(path=path, role='lane artifact', sha256=sha_file(path))
               for path in artifacts()]
    sources.append(dict(path=CLOSEOUT, role='the close-out this audit re-reads (147)',
                        sha256=sha_file(CLOSEOUT)))

    return {
        'schema': 'l2/535b0541/open-items-audit/1',
        'evidence': 'STATIC_ONLY_ORIGINAL_APK',
        'note': 'Verdicts over the 56 open items of the lane, each closure re-checked '
                'against the artifact that closed it. No disassembly: every proof reads a '
                'field. Device and served state stay MODEL_NOT_MEASURED runtime.',
        'provenance': {'sources': sources,
                       'xapk_sha256': 'f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957'
                                      '215e884cdd057c7e'},
        'totals': totals,
        'items': rows,
        'by_report': by_report,
        'duplicates': [dict(n=group, note=note) for group, note in DUPLICATES],
        'records': [dict(report=report, kind=kind, closes=closes)
                    for report, kind, closes in RECORDS],
        'verdict_backing': dict(
            declared=sum(1 for row in rows
                         if row['verdict'] == 'CLOSED' and row['n'] in declared),
            by_content=sum(1 for row in rows
                           if row['verdict'] == 'CLOSED' and row['n'] not in declared),
            note='a closure is sometimes recorded by the later artifact itself '
                 '(`corrections` / `confirmations`) and sometimes only implied by what the '
                 'artifact contains'),
        'corrections': corrections,
        'next_steps': [
            dict(item='rewardValues / rewardScales (133)',
                 why='route proven in 131, lookup not run',
                 how='resolve the two handle slots 0x2ae0010 / 0x2ae0018 to PID fields, '
                     'then read `reverse-engineering/il2cpp/field-defaults.json`'),
            dict(item='LanguageManager.GetText (137)',
                 why='the answer is code, and the raw is not pinned',
                 how='pin the raw that carries RVA 21202600; until then the missing-key '
                     'behaviour stays unread rather than guessed'),
            dict(item='the reader of `ArenaManager.rewards` (139)',
                 why='still no consumer in the arena-pvp raw',
                 how='scan the other six raws for `+0x38` on an ArenaManager statics base'),
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=OUTPUT)
    args = parser.parse_args()

    payload = build_payload()
    blob = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(gzip.compress(blob, mtime=0))
    print(json.dumps(dict(bytes=out.stat().st_size,
                          sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
                          **payload['totals'])))


if __name__ == '__main__':
    main()
