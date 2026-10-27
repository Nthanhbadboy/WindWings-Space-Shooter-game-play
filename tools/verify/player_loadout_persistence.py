"""Provisional pinned ship/loadout save evidence, not a runnable save subsystem."""
import gzip
import hashlib
import json
from pathlib import Path
from opening_persistence import collect, ROOT, RAW

SHIP = 'Player_Saved_Datas'
SELECT = {
    SHIP: ('player-loadout/native', ['IsPlayerUnlocked', 'SetPlayerUnlocked', 'GetPlayerUsed', 'SetPlayerUsed', 'CheckDoubleIDShip',
        'GetPlayerLevel', 'SetPlayerLevel', 'GetPlayerRank', 'SetPlayerRank', 'GetPlayerCards', 'SetPlayerCards',
        'GetPlayerDefaultSkin', 'SetPlayerDefaultSkin', 'GetTechStatPoints', 'SetTechStatPoints', 'GetTechStatLevel',
        'SetTechStatLevel', 'GetTechLabLevel', 'SetTechLabLevel', 'get_MAX_RANK_INDEX', 'cctor']),
    'Player_Device_Saved_Datas': ('player-loadout/native', ['GetPlayerDevices', 'SetPlayerDevices']),
    'GP_Setup': ('ui-audit/extra-native', ['get_indexPlayers', 'set_indexPlayers']),
    'GP_Loader': ('ui-audit/extra-native', ['LoadObjects']),
    'Tech_Datas': ('il2cpp-consts', ['GetTechStatLevel']),
    'Board_Talents': ('ui-audit/extra-native', ['get_GetTalentIndex', 'set_GetTalentIndex', 'OnClickTalent']),
    'Player_Talent': ('il2cpp-consts', ['<Start>b__8_3']),
    'Player_Get_Datas': ('il2cpp-consts', ['GetMainCannonRatePercent', 'GetMaxCountRockets']),
}


def ship_used_read(store, slot):
    """Ordinary int32 IDs/slots: one getter, copy state so caller sees exact writes."""
    state = dict(store)
    default = 10001 if slot == 0 else 10002
    writes = {}
    if state.get(f'PlayerUsed{slot}', default) <= 0:
        writes = {'PlayerUsed0': 10001, 'PlayerUsed1': 10002}
        state.update(writes)
    return state.get(f'PlayerUsed{slot}', default), state, writes


def ship_rank_read(store, ship):
    """Base rank repair occurs BEFORE the trial override; no upper cap here."""
    state = dict(store)
    key = f'PLAYER_RANK{ship}'
    writes = {}
    if state.get(key, 2) <= 1:
        writes[key] = state[key] = 2
    return (state.get(f'TRIAL_RANK_{ship}', 0) if state.get(f'TRIAL_ID_{ship}', 0) == 1
            else state.get(key, 2)), state, writes


def ship_unlocked_normal(ship, stored=0):
    """Non-Test, non-Premium branch only; not roster membership validation."""
    return ship < 10003 or stored == 1


def ship_level_read(store, ship):
    prefix = 'TRIAL_LEVEL_' if store.get(f'TRIAL_ID_{ship}', 0) == 1 else 'PLAYER_LEVEL'
    return store.get(f'{prefix}{ship}', 0)


def rocket_count(tech_level):
    """Exact static branch including non-monotonic 6..8 result; do not 'repair'."""
    if tech_level > 8:
        return 10
    if tech_level > 5:
        return 3
    return 8 if tech_level > 0 else 7


def build():
    declarations, sources, records, methods = collect(SELECT)
    def asm(cls, method, *parts):
        return all(s in methods[cls, method]['asm'] for s in parts)
    def strings(cls, name):
        return {r['Value'] for item in methods[cls, name]['metadata_loads'] for r in item['records'] if r['group'] == 'ScriptString'}
    def calls(cls, name, target, owner):
        return any(c['target_rva'] == target and c['declaration'] and c['declaration']['class_name'] == owner for c in methods[cls, name]['calls'])
    folder = RAW / 'player-loadout'
    manifest = json.loads((folder / 'index.json').read_text())
    arrays = json.load(gzip.open(folder / 'array-blobs.json.gz', 'rt'))
    for path in (folder / 'index.json', folder / 'array-blobs.json.gz'):
        data = path.read_bytes()
        if path.suffix == '.gz':
            data = gzip.decompress(data)
        sources.append(dict(path=str(path.relative_to(ROOT)), sha256_decompressed=hashlib.sha256(data).hexdigest()))
    def original_files_valid():
        for row in manifest['files']:
            path = ROOT / row['path']
            data = path.read_bytes()
            if path.suffix == '.gz':
                data = gzip.decompress(data)
            if hashlib.sha256(data).hexdigest() != row['sha256_decompressed']:
                return False
        return manifest['dump_sha256_decompressed'] == sources[0]['sha256_decompressed']
    resolved = arrays['resolved']['methods']
    rank_arrays = resolved[f'{SHIP}.cctor']
    checks = {
        'original_recovery_files_match_pinned_manifest': original_files_valid(),
        'array_blobs_have_expected_length': all(r['length_valid'] for rows in resolved.values() for r in rows),
        'cctor_array_field_offsets_in_dump': all(s in declarations[SHIP] for s in ['int[] MaxLevelPerRanks; // 0x0', 'int[] CardUpgrades; // 0x8', 'int[] StartRanks; // 0x10']),
        'cctor_array_store_order': asm(SHIP, 'cctor', '0x14e81c0: str      x19, [x8]', '0x14e81e8: str      x19, [x8, #8]', '0x14e8214: str      x19, [x8, #0x10]'),
        'cctor_array_callsites_bind_order': [r['addr'] for r in rank_arrays] == ['0x14e81b0','0x14e81d8','0x14e8200'],
        'raw_tech_missing_defaults_zero': asm(SHIP,'GetTechStatPoints','0x14e7e1c: mov      w1, wzr') and asm(SHIP,'GetTechStatLevel','0x14e7f68: mov      w1, wzr') and asm(SHIP,'GetTechLabLevel','0x14e8088: mov      w1, wzr'),
        'rank_array_values': [r['ints'] for r in rank_arrays] == [[10,20,30,60,120,250,500], [0,20,50,80,250,500,800], [2]*24],
        'max_rank_length_minus_one': asm(SHIP, 'get_MAX_RANK_INDEX', '0x14e6d64: sub      w0, w8, #1'),
        'used_default_slot_zero_and_other': asm(SHIP, 'GetPlayerUsed', '0x14e7124: mov      w8, #0x2711', '0x14e7128: cinc     w20, w8, ne'),
        'used_nonpositive_resets_both_then_rereads': asm(SHIP, 'GetPlayerUsed', '0x14e7144: cmp      w0, #0', '0x14e7148: b.gt     #0x14e71cc', '0x14e7188: mov      w1, #0x2711', '0x14e71c0: mov      w1, #0x2712', '0x14e721c: bl       #0x13f1a1c'),
        'rank_base_default_and_repair': asm(SHIP, 'GetPlayerRank', '0x14e6e18: mov      w1, #2', '0x14e6e28: cmp      w0, #1', '0x14e6e2c: b.gt     #0x14e6e78', '0x14e6e68: mov      w1, #2'),
        'trial_rank_selected_exact_one': asm(SHIP, 'GetPlayerRank', '0x14e6ed0: cmp      w19, #1', '0x14e6ed8: b.ne     #0x14e6f14', '0x14e6f0c: mov      w1, wzr'),
        'trial_level_selected_exact_one': asm(SHIP, 'GetPlayerLevel', '0x14e3bdc: cmp      w19, #1', '0x14e3be4: b.ne     #0x14e3bf4', '0x14e3c24: mov      w1, wzr'),
        'cards_company_not_test_default_zero': asm(SHIP, 'GetPlayerCards', '0x14e7a14: tbz      w20, #0, #0x14e7a30', '0x14e7a28: mov      w20, wzr') and 'Test' in strings(SHIP, 'GetPlayerCards'),
        'skin_missing_minus_one': asm(SHIP, 'GetPlayerDefaultSkin', '0x14e7880: mov      w1, #-1'),
        'unlock_normal_threshold_exact_one': asm(SHIP, 'IsPlayerUnlocked', '0x14e266c: mov      w8, #0x2713', '0x14e2674: b.lt     #0x14e26dc', '0x14e26d0: cmp      w0, #1', '0x14e26d4: cset     w0, eq'),
        'unlock_setter_analytics_precedes_flag': asm(SHIP, 'SetPlayerUnlocked', '0x14e730c: cbz      x0, #0x14e73b8', '0x14e7394: mov      w1, #1', '0x14e73a0: bl       #0x13f1a04'),
        'duplicate_repair_changes_slot_zero': asm(SHIP, 'CheckDoubleIDShip', '0x14e74e4: cmp      w19, w0', '0x14e74e8: b.ne     #0x14e75a4', '0x14e75f0: mov      w0, wzr') and calls(SHIP, 'CheckDoubleIDShip', '0x14e73bc', SHIP),
        'setup_two_slots_from_saved_readers': asm('GP_Setup','get_indexPlayers', '0x14f278c: mov      w1, #2', '0x14f2808: mov      w0, wzr', '0x14f2824: mov      w0, #1') and calls('GP_Setup','get_indexPlayers','0x14e70a0', SHIP),
        'loader_saved_or_trial_rank_and_floor_two': calls('GP_Loader','LoadObjects','0x14e24fc',SHIP) and calls('GP_Loader','LoadObjects','0x14e6d74',SHIP) and asm('GP_Loader','LoadObjects', '0x14f238c: cmp      w0, #2', '0x14f2394: csel     w26, w0, w8, gt'),
        'device_keys_and_missing_minus_one': {'PLAYER_DEVICE_','_','Game'} <= strings('Player_Device_Saved_Datas','GetPlayerDevices') and asm('Player_Device_Saved_Datas','GetPlayerDevices','0x14e6444: mov      w1, #-1', '0x14e6474: cmp      w24, #4'),
        'device_mode_four_game_override': asm('Player_Device_Saved_Datas','GetPlayerDevices','0x14e634c: cmp      w8, #4', '0x14e6398: tbz      w0, #0, #0x14e63c4') and resolved['Player_Device_Saved_Datas.GetPlayerDevices'][0]['ints'] == [-1]*4,
        'device_writer_four_slots_not_variable_length': asm('Player_Device_Saved_Datas','SetPlayerDevices', '0x14e65d4: cmp      w8, #4', '0x14e65dc: b.lt     #0x14e6538'),
        'tech_level_wrapper_mode_four_game_zero_override': calls('Tech_Datas','GetTechStatLevel','0x14e7ee0',SHIP) and asm('Tech_Datas','GetTechStatLevel', '0x139d9e8: cmp      w8, #4', '0x139da38: mov      w0, wzr'),
        'talent_saved_minus_one': 'TALENT_SELECTED' in strings('Board_Talents','get_GetTalentIndex') and asm('Board_Talents','get_GetTalentIndex','0x1397494: mov      w1, #-1'),
        'talent_game_callback_consumes_selection': calls('Player_Talent','<Start>b__8_3','0x1397438','Board_Talents') and asm('Player_Talent','<Start>b__8_3','0x14bf4a8: cmp      w8, #4','0x14bf4d0: str      w0, [x19, #0x28]'),
        'stat_one_consumed_by_main_cannon': calls('Player_Get_Datas','GetMainCannonRatePercent','0x139d96c','Tech_Datas') and asm('Player_Get_Datas','GetMainCannonRatePercent','0x14e3dac: mov      w0, #1'),
        'stat_five_rockets_non_monotonic_branch': calls('Player_Get_Datas','GetMaxCountRockets','0x139d96c','Tech_Datas') and asm('Player_Get_Datas','GetMaxCountRockets','0x14e53c0: mov      w0, #5', '0x14e53cc: cmp      w0, #8', '0x14e53d4: cmp      w0, #5', '0x14e53f4: mov      w0, #3'),
    }
    contracts = []
    def add(key, cls, reader, writers, default, semantics, literals=None):
        expected = set(literals or [key.split('{')[0]])
        assert expected <= strings(cls, reader), (key, strings(cls, reader))
        for writer in writers:
            assert expected <= strings(cls, writer), (key, writer)
        checks['literal_' + key] = True
        contracts.append(dict(key_format=key, value_type='int32', reader_return_type=methods[cls, reader]['inventory']['signature'].split('(')[0].split()[-2], backend='Unity.PlayerPrefs via typed PlayerPreferences wrappers',
            reader_method_id=f'{cls}.{reader}', writer_method_ids=[f'{cls}.{x}' for x in writers],
            normal_missing_default=default, semantics=semantics))
    add('PlayerUsed{slot}',SHIP,'GetPlayerUsed',['SetPlayerUsed'],{'slot_0':10001,'other_slots':10002}, 'Read<=0 resets keys PlayerUsed0=10001 and PlayerUsed1=10002, then rereads requested slot; no unlock/duplicate check in setter.')
    add('PlayerUnlocked{ship}',SHIP,'IsPlayerUnlocked',['SetPlayerUnlocked'],0,'Normal non-Premium: ship<10003 => true (not roster validation); otherwise saved==1. Setter invokes analytics/LastShipUnlocked before flag write; can throw if analyser null.')
    add('PLAYER_RANK{ship}',SHIP,'GetPlayerRank',['SetPlayerRank'],2,'Base<=1 writes2 before checking trial flag; trial==1 returns separate trial rank default0, no final clamp in getter. Setter has offer-reset/analytics side effects, no numeric cap shown.')
    add('PLAYER_LEVEL{ship}',SHIP,'GetPlayerLevel',['SetPlayerLevel'],0,'Reads trial level instead only when TRIAL_ID_{ship}==1; no clamp in selected getter/setter.')
    for key, reader in [('TRIAL_ID_{ship}','GetPlayerLevel'),('TRIAL_RANK_{ship}','GetPlayerRank'),('TRIAL_LEVEL_{ship}','GetPlayerLevel')]:
        add(key, SHIP, reader, [], 0, 'Trial flag exact1; trial writer/migration lifecycle outside this extraction.')
    add('PLAYER_CARDS{ship}',SHIP,'GetPlayerCards',['SetPlayerCards'],0,'Normal company!=Test only; Test missing default comes from CheatGameInfo static+0x24, not an override of existing saved value.')
    add('PLAYER_DEFAULT_SKIN{ship}',SHIP,'GetPlayerDefaultSkin',['SetPlayerDefaultSkin'],-1,'Missing -1 is used by GP_Loader to choose default rank skin path; do not turn it into skin0.')
    for key, reader, writer in [('PlayerStatPoints{stat}','GetTechStatPoints','SetTechStatPoints'),('PlayerStatLevel{stat}','GetTechStatLevel','SetTechStatLevel'),('TECHLAB_LV','GetTechLabLevel','SetTechLabLevel')]:
        add(key,SHIP,reader,[writer],0,'Raw saved integer, no clamp in these bodies; gameplay wrapper may override in mode4/Game.')
    add('PLAYER_DEVICE_{ship}_{slot}','Player_Device_Saved_Datas','GetPlayerDevices',['SetPlayerDevices'],-1,'Four slots0..3. Mode4 AND active scene Game returns new [-1,-1,-1,-1] without reading saved slots. Setter loops exactly four, bounds faults/partial writes possible for short arrays.', ['PLAYER_DEVICE_','_'])
    add('FIRST_INSTALL_DEVICE','Player_Device_Saved_Datas','SetPlayerDevices',['SetPlayerDevices'],0,'Internal first-use flag: after four writes, if any value!=-1 and old flag==0, emit feature0 then write1.')
    add('TALENT_SELECTED','Board_Talents','get_GetTalentIndex',['set_GetTalentIndex'],-1,'Persisted selection, not the tech stat level. Player_Talent startup callback checks StageTarget>=Board_Begin.stageUnlockTalents (static+0x4, numeric unresolved), selection!=-1 and mode!=4 before assigning component talentIndex.')
    assert all(checks.values()), [k for k,v in checks.items() if not v]
    return dict(schema_version=1, status='PROVISIONAL_STATIC_PARTIAL_PLAYER_LOADOUT_NOT_RUNTIME', sources=sources,
        methods=records, checks=checks, contracts=contracts,
        declarations={c: declarations[c].split('// Properties')[0] for c in [*SELECT, 'Board_Begin']},
        array_evidence=arrays,
        rank_tables=dict(MaxLevelPerRanks=rank_arrays[0]['ints'],CardUpgrades=rank_arrays[1]['ints'],StartRanks=rank_arrays[2]['ints'],MAX_RANK_INDEX=len(rank_arrays[0]['ints'])-1,
                         evidence_method_id=f'{SHIP}.cctor', binding='InitializeArray callsite order -> static field offsets0,8,16; metadata token -> same-image private field blob; values truncated to allocation length, padding retained in raw.'),
        consumers=[dict(method_id='GP_Setup.get_indexPlayers', role='Two-slot array, normal reads slots0/1; mode4 first slot comes from separate mode state. Instance initialization flag/static cached array; not a fresh saved read every call.'),
                   dict(method_id='GP_Loader.LoadObjects', role='Consumes configured ship IDs; unlocked -> rank getter, locked -> TRIAL_RANK_ default0; effective rank floored2; skin -1 selects default path.'),
                   dict(method_id='Tech_Datas.GetTechStatLevel', role='Saved level except mode4 AND active scene Game ->0, not save overwrite.'),
                   dict(method_id='Player_Get_Datas.GetMainCannonRatePercent', role='Consumes effective tech stat1; float branch constants retained in native JSON, no full combat formula claim here.'),
                   dict(method_id='Player_Get_Datas.GetMaxCountRockets', role='Consumes effective tech stat5: level<=0=>7,1..5=>8,6..8=>3,>=9=>10; non-monotonic native result preserved.'),
                   dict(method_id='Player_Talent.<Start>b__8_3', role='Consumes TALENT_SELECTED after stage/selection/mode gates; separate from unlock/tech persistence.')],
        limitations=['Contract schema_version is pack format version, not APK save version.', 'Static normal non-Test/non-Premium analysis; Premium/offer economy not reconstructed.', 'No first-install runtime profile, atomicity, save migration or cloud/durability proof.', 'Trial writers and expiry not reconstructed; never infer trial state only from unlock status.', 'Rank tables alone do not enforce caps or establish whole upgrade payment/transaction flow.', 'No roster validity inferred from broad ID comparisons; no invented validation or monotonic correction.', 'Gameplay cache refresh/switching lifecycle is partial; snapshots may outlive saved changes.', 'Tech/talent consumers are scoped examples, not full combat formula coverage.'])


def main():
    data = build()
    evidence = RAW / 'player-loadout/contracts.json.gz'
    evidence.write_bytes(gzip.compress(json.dumps(data, ensure_ascii=False, indent=2).encode(), mtime=0))
    out = {key:data[key] for key in ['schema_version','status','contracts','rank_tables','consumers','limitations']}
    out.update(raw_evidence=str(evidence.relative_to(ROOT)), raw_evidence_sha256_decompressed=hashlib.sha256(gzip.decompress(evidence.read_bytes())).hexdigest())
    (ROOT / 'datas/player_loadout_persistence.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(len(data['methods']), 'methods;', len(data['checks']), 'checks;', len(data['contracts']), 'key families')


if __name__ == '__main__':
    main()
