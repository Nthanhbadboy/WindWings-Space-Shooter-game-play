#!/usr/bin/env python3
"""Static Arena/PvP decoder for build 1.3.118. No native code is executed.

Sources are the pinned original APK bytes already recovered on this branch:
`reverse-engineering/raw/arena-pvp-535b0541/native.json.gz` (method RVAs, code
SHA-256, instruction stream, literal bytes, metadata slots). Everything this tool
prints is re-derived from those records, never from a device, emulator or probe.
"""
import argparse
import gzip
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arena_pvp_initializers import decode_class  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'reverse-engineering/raw/arena-pvp-535b0541/native.json.gz'
ARTIFACT = ROOT / 'datas/l2_535b0541_arena_pvp.json.gz'
BRANCH = 'arena/535b0541-windwings-space-shooter-game-p'
RUN_ID = 40343270200


def load_native():
    return json.loads(gzip.decompress(RAW.read_bytes()))


def method(native, cls, name):
    return next(m for m in native['methods'] if m['class_name'] == cls and
                re.search(r'(?<!\w)' + re.escape(name) + r'\(', m['signature']))


def f32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]


def score(mode, enemy_id, rank, time_life=0.0):
    """GetArenaScore (mode 5) / GetPVPPlayScore (6) / GetArenaPlayScore (5).

    `rank` is Enemy_Data_Balance.listStaticEmemies.Count, i.e. the loaded enemy
    roster size, NOT the player league. TimeLife is only consumed by PvP.
    Rounding is Math.Round: ties-to-even, unlike Python's round for .5 ties.
    """
    scale = 5. if rank < 6 else 2. if rank < 15 else 1. if rank < 23 else .5 if rank < 29 else .2
    if enemy_id == 39000 or enemy_id > 39999:
        return 1
    if enemy_id <= 30999:
        base = 9.
    elif enemy_id <= 35999:
        base = 25.
    elif enemy_id <= 36999:
        base = 65.
    elif enemy_id <= 37999:
        base = 350. if mode == 6 else 180.
    elif enemy_id <= 38999:
        base = 6.
    else:
        base = 350. if mode == 6 else 300.
    product = f32(f32(scale) * f32(base))
    if mode == 6:
        life = f32(time_life)
        factor = 1.
        for upper, value in ((.01, 2.3), (.1, 2.), (.56, 1.8), (1.6, 1.7), (2.8, 1.6),
                             (4.2, 1.5), (6., 1.4), (11., 1.3), (30., 1.2), (56., 1.1)):
            if life < f32(upper):
                factor = f32(value)
                break
        product = f32(product * factor)
    return round(product)  # Python 3 rounds halves to even, same as Math.Round.


def to_points(rank, level, star, point):
    return rank * 1000000 + level * 100000 + star * 10000 + min(max(point, 0), 100)


def data_from_points(points):
    return dict(pvpRank=points // 1000000, pvpLevel=(points % 1000000) // 100000,
                pvpStars=(points % 100000) // 10000, pvpPoints=points % 100,
                totalPoints=points)


def decode_map_pools(native):
    m = method(native, 'Map_Get_Datas', '.cctor')
    instructions = m['instructions']
    arrays = json.loads((ROOT / 'reverse-engineering/il2cpp/ia-resolved.json').read_text())['methods']['Map_Get_Datas.cctor']
    by_addr = {int(a['addr'], 16): a for a in arrays}
    registers, objects, fields, adds, pc = {}, [], {}, [], 0
    slots = {0: 'listMapTryPlayerDatas', 8: 'AllArenaStartMaps', 16: 'AllArenaRandomMaps', 24: 'AllPvPStartMaps'}
    jumps = {i['rva']: n for n, i in enumerate(instructions)}

    def key(name):
        match = re.fullmatch(r'[wx](\d+)', name)
        return 'r' + match[1] if match else name

    def reg(name):
        return registers.get(key(name))

    def put(name, value):
        registers[key(name)] = value

    def obj(value):
        return objects[value[1]] if isinstance(value, tuple) and value[0] == 'object' else None

    end_rva = None
    while pc < len(instructions):
        i = instructions[pc]
        pc += 1
        op, args, rva = i['mnemonic'], i['op_str'], i['rva']
        parts = args.split(', ')
        if op == 'b':
            target = int(args.lstrip('#'), 0)
            if target not in jumps:
                break
            pc = jumps[target]
        elif op == 'adrp':
            put(parts[0], ('address', int(parts[1].lstrip('#'), 0)))
        elif op == 'mov':
            put(parts[0], int(parts[1][1:], 0) if parts[1].startswith('#') else reg(parts[1]))
        elif op == 'add':
            base = reg(parts[1])
            put(parts[0], base if isinstance(base, tuple) and base[0] == 'backing' else None)
        elif op in ('ldr', 'ldrsw'):
            match = re.fullmatch(r'(\w+), \[(\w+)(?:, #(0x[0-9a-f]+|\d+))?\]', args)
            if not match:
                continue
            dest, source, off = match.groups()
            off = int(off or '0', 0)
            base = reg(source)
            value = None
            if isinstance(base, tuple):
                tag, ident = base
                if tag == 'address':
                    value = ('metadata', ident + off)
                elif tag == 'metadata':
                    value = ('type', ident)
                elif tag == 'type' and off == 184:
                    value = ('statics', ident)
                elif tag == 'object' and off == 16:
                    value = ('backing', ident)
            put(dest, value)
        elif op == 'bl':
            call = int(args.lstrip('#'), 0)
            if call in (17879616, 17879196):
                value = dict(kind='array' if call == 17879196 else 'list', new_rva=rva, values=[])
                if value['kind'] == 'array':
                    value['length'] = reg('x1')
                    value['values'] = [0] * value['length']
                objects.append(value)
                put('x0', ('object', len(objects) - 1))
            elif call == 33927292:
                array = obj(reg('x0'))
                a = by_addr[rva]
                assert array is not None and array['length'] == a['len']
                array.update(values=a['ints'][:a['len']], initialize_rva=rva, field=a['field'], raw=a['raw'])
            elif call in (17879080, 29193868):
                pass
            else:
                raise ValueError(f'unexpected call {call} at {rva}')
        elif op == 'str':
            match = re.fullmatch(r'(\w+), \[(\w+)(?:, #(0x[0-9a-f]+|\d+))?\]', args)
            if not match:
                continue
            source, dest, off = match.groups()
            off = int(off or '0', 0)
            base, value = reg(dest), reg(source)
            if isinstance(base, tuple) and base[0] == 'backing' and off == 32:
                assert obj(value) is not None, (rva, value)
                objects[base[1]]['values'].append(value)
                adds.append(dict(rva=rva, list_new_rva=objects[base[1]]['new_rva'],
                                 value_new_rva=obj(value)['new_rva']))
            elif isinstance(base, tuple) and base[0] == 'statics' and off in slots:
                fields[slots[off]] = dict(store_rva=rva, ref=value)
                if off == 24:
                    end_rva = rva
                    break
        elif op == 'ret':
            break

    def expand(ref):
        o = obj(ref)
        assert o is not None
        data = {k: v for k, v in o.items() if k != 'values'}
        data['values'] = [int(v) for v in o['values']] if o['kind'] == 'array' else [expand(v) for v in o['values']]
        return data

    assert set(fields) == set(slots.values())
    return dict(method_rva=m['rva'], method_sha256=m['sha256'], scope_end_rva=end_rva,
                evidence='STATIC_LIST_INITIALIZER_IR_NOT_RUNTIME',
                fields={k: dict(store_rva=v['store_rva'], tree=expand(v['ref'])) for k, v in fields.items()},
                additions=adds)


def accessor_rules(native):
    """Fallback and source-field rules read from the four Map_Get_Datas accessors."""
    out = {}
    for name, slot, mode in (('GetListMapArenaRandom', 8, 'random'), ('GetListMapArena', 8, 0),
                             ('GetListMapPvPRandom', 24, 'random'), ('GetListMapPvP', 24, 0)):
        m = method(native, 'Map_Get_Datas', name)
        text = ' '.join(f"{i['mnemonic']} {i['op_str']}" for i in m['instructions'])
        out[name] = dict(rva=m['rva'], sha256=m['sha256'], bytes=m['size'], pool_offset=hex(slot),
                         uses_AllPvPStartMaps_for_random=(name == 'GetListMapPvPRandom'),
                         negative_rank_guarded='#0x1f' in text,
                         out_of_range_falls_back_to_index_zero=('mov w1, wzr' in text),
                         evidence='STATIC_READ_OF_PINNED_BYTES')
    return out


def score_constants(native):
    """Literal values that the three score functions load, with their RVAs."""
    out = {}
    for name in ('GetArenaScore', 'GetPVPPlayScore', 'GetArenaPlayScore'):
        m = method(native, 'Enemy_Data_Balance', name)
        out[name] = dict(rva=m['rva'], sha256=m['sha256'], bytes=m['size'],
                         literals=[{k: l[k] for k in ('instruction_rva', 'hex')} for l in m['literals']])
    return out


def static_fields(native):
    return {cls: decode_class(native, cls) for cls in ('ArenaConfig', 'ArenaManager', 'PVP_Manager')}


def build():
    native = load_native()
    stats = static_fields(native)
    pvp = stats['PVP_Manager']['fields']
    arena = stats['ArenaManager']['fields']
    medal_rows = [[int(v) for v in row['items']] for row in pvp['TournamentRewardMedals']['value']['items']]
    reward_rows = []
    for row in pvp['AllRewards']['value']['items']:
        values = row['fields'].get('0x10', {}).get('ints')
        if values:
            reward_rows.append(dict(rank=values[0], level=values[1], medal=values[2], gem=values[3],
                                    new_rva=row['new_rva'], pool_va=row['fields']['0x10']['va']))
    season_rows = []
    for row in pvp['AllSeasonRewards']['value']['items']:
        pair = row['fields'].get('0x10', {}).get('ints')
        gifts = []
        gifts_node = row['fields'].get('0x18')
        for gift in (gifts_node or {}).get('items') or []:
            values = gift['fields'].get('0x10', {}).get('ints')
            if values:
                gifts.append(dict(type=values[0], number=values[1], pool_va=gift['fields']['0x10']['va'],
                                  new_rva=gift['new_rva']))
        if pair:
            season_rows.append(dict(rankStart=pair[0], rankEnd=pair[1], gifts=gifts, new_rva=row['new_rva']))
    points = [0, 1, 99, 100, 999, 100000, 1234567, 1999999, 9876543]
    output = dict(
        schema=1, build='1.3.118', evidence='STATIC_ONLY_ORIGINAL_APK',
        runtime='MODEL_NOT_MEASURED runtime', branch=BRANCH,
        provenance=dict(
            xapk_sha256=native['xapk_sha256'], libil2cpp_sha256=native['libil2cpp_sha256'],
            dump_sha256=native['dump_sha256'], raw_path=str(RAW.relative_to(ROOT)),
            raw_sha256=hashlib.sha256(RAW.read_bytes()).hexdigest(),
            recovery_workflow='.github/workflows/arena-pvp-static-recovery.yml',
            recovery_tool='tools/recovery/arena_pvp_native.py', recovery_run_id=RUN_ID,
            boundary=native['boundary']),
        inventory=dict(methods=len(native['methods']),
                       classes=len({m['class_name'] for m in native['methods']}),
                       methods_by_class=sorted({} or {m['class_name']: sum(1 for x in native['methods'] if x['class_name'] == m['class_name']) for m in native['methods']}.items())),
        method_index=[{k: m[k] for k in ('class_name', 'signature', 'rva', 'size', 'sha256')}
                      for m in native['methods']],
        map_pools=decode_map_pools(native),
        map_accessors=accessor_rules(native),
        score=dict(constants=score_constants(native),
                   model='score(mode,enemyId,rank,timeLife); rank=listStaticEmemies.Count; ties-to-even',
                   samples=[[mode, enemy, rank, t, score(mode, enemy, rank, t)]
                            for mode in (5, 6) for enemy, rank, t in
                            ((30001, 0, 0.), (30500, 6, 0.), (35000, 15, 0.), (36999, 23, .5),
                             (37999, 29, 1.6), (38999, 4, 5.5), (39500, 40, 30.), (39000, 10, 56.))]),
        arena=dict(config=stats['ArenaConfig']['fields'], manager=arena),
        pvp=dict(scalars={k: pvp[k] for k in ('pvpMaxLife', 'pointReduceDie', 'RankShowCount', 'timePlay',
                                             'timeStep', 'pvpTimeScale', 'IsOpen')},
                 tournamentAddStarPoints=[int(v) for v in pvp['TournamentAddStarPoints']['value']['items']],
                 tournamentRewardMedals=medal_rows, allRewards=reward_rows,
                 seasonRewards=season_rows,
                 rankStars=dict(lengths=[a['length'] for a in pvp['MaxRankStars']['value']['items']],
                                values=None,
                                not_decoded='InitializeArray blob token not resolved; lengths only')),
        rules=dict(room=dict(isFull='players.Count >= max', isEmpty='players.Count == 0',
                             rva_full=method(native, 'Room', 'IsFull')['rva'],
                             rva_empty=method(native, 'Room', 'IsEmpty')['rva']),
                   seasonReward='GetSeasonRewards(rank): first SeasonRewards whose rankStart <= rank+1 <= rankEnd; returns its Gift list',
                   tournamentMedal='GetTournamentMedalReward(rank,index): TournamentRewardMedals[rank][index]',
                   points=dict(to='rank*1000000 + level*100000 + star*10000 + clamp(point,0,100)',
                               from_='pvpRank=points//1000000; pvpLevel=(points%1000000)//100000; pvpStars=(points%100000)//10000; pvpPoints=points%100; totalPoints=points',
                               samples=[dict(points=p, decoded=data_from_points(p),
                                             reencoded=to_points(d['pvpRank'], d['pvpLevel'],
                                                                 d['pvpStars'], d['pvpPoints']))
                                        for p in points for d in [data_from_points(p)]],
                               asymmetry='ToPoints clamps point to 0..100 but DataFromPoints keeps point = points%100, so point=100 does not round-trip')),
        not_decoded=[
            dict(item='ArenaManager.rewards[10] string values',
                 reason='metadata usage slot resolves to a string literal object created at startup; token table not consulted here'),
            dict(item='ArenaConfig.RankSplit / SeasonTime strings', reason='same metadata-usage limitation'),
            dict(item='PVP_Manager.MaxRankStars array contents',
                 reason='InitializeArray blob token not resolved for this class; only array lengths decoded'),
            dict(item='SeasonTimes / RankUpIndexs / RankDropIndexs values',
                 reason='null after .cctor: filled by ArenaManager.LoadRemoteConfigs from Firebase, not a build constant'),
            dict(item='medal shop prices / stock',
                 reason='Popup_ArenaShopExchange & Popup_PVPShopExchange read serialized Board_EventSeasonPass.EventRewards fields, not native constants'),
        ])
    ARTIFACT.write_bytes(gzip.compress(json.dumps(output, sort_keys=True, separators=(',', ':')).encode(), mtime=0))
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='rebuild datas artifact from pinned raw')
    args = parser.parse_args()
    if args.write:
        data = build()
        print(json.dumps(dict(artifact=str(ARTIFACT.relative_to(ROOT)), bytes=ARTIFACT.stat().st_size,
                              methods=data['inventory']['methods'], classes=data['inventory']['classes'],
                              medal_rows=len(data['pvp']['tournamentRewardMedals']),
                              reward_rows=len(data['pvp']['allRewards']),
                              season_rows=len(data['pvp']['seasonRewards'])), indent=1))
    else:
        data = json.loads(gzip.decompress(ARTIFACT.read_bytes()))
        assert data['evidence'] == 'STATIC_ONLY_ORIGINAL_APK'
        assert decode_map_pools(load_native()) == data['map_pools']
        print('Arena/PvP static decode reproduces artifact')


if __name__ == '__main__':
    main()
