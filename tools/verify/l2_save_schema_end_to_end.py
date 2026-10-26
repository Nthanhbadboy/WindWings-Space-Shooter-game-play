"""Build a bounded static save->load trace for the player-device save family."""
import gzip
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path('datas/l2_save_schema_end_to_end.json.gz')
SOURCES = {
    'docs/apk-analysis/PHAN_TICH_WINDWINGS_APK.md': 'f799e2a25cb60c9957b29d8c11afd683c289e8c60ae400562e4bf8dec8bcb3bd',
    'reverse-engineering/raw/player-loadout/index.json': 'f3a049c8c6f4380946395d5e47b6e86230f164fb376dd1ad901bdaa12d4843cd',
    'reverse-engineering/raw/player-loadout/contracts.json.gz': '045dd36ff3f81eb4193953860856009dde6ed8c541e2749291eeb9dae22eb276',
    'reverse-engineering/raw/player-loadout/native/Player_Device_Saved_Datas.asm.txt': '4cd845eca6efa22b279ccef7fe0ad91845f1efdf6c523ab095ec47cd52bc9113',
    'reverse-engineering/raw/player-loadout/native/Player_Device_Saved_Datas.json': 'a410ecc45e6956f56b38947813f36fe9838696052e0ae2b74e946f7c134185cf',
    'reverse-engineering/raw/player-loadout/native/Player_Saved_Datas.asm.txt': 'bf90fe4d926e000765a6772330090566d072d0bc3d5ab0f6fc4615326f16db99',
    'reverse-engineering/raw/ui-audit/extra-native/PlayerPreferences.asm.txt': 'aa983280bda35434d4011944a212b85381a726778c7c6b612c786afa5e4d70ac',
    'reverse-engineering/il2cpp/dump.cs.gz': 'e08f23fb6c90e07288e5b202e0ce1e7c5e82a7feb5ccae7aa08aaec3ad166454',
    'reverse-engineering/il2cpp/stringliteral.json': '5e62507e148b530203a608e57e11a98a38910c34dc79fe04d27c16084cccb6d5',
    'reverse-engineering/raw/il2cpp-consts/Device_Get_Data.asm.txt': 'a72bee63f439588733b1d7968f400d74ac94b55a3081494f7376238a0b9e2f63',
    'reverse-engineering/raw/il2cpp-consts/Player_Attack.asm.txt': '26d50d790a50b3af6535653b0766f0f79370da81d49ee02bb02991592666dbf5',
    'reverse-engineering/raw/il2cpp-consts/Player_Health.asm.txt': 'badd5311dfc2a7b5b991304607cf85025885f0a6e729226ace7320bfa7e9b7ac',
    'reverse-engineering/raw/il2cpp-consts/Board_Players.asm.txt': 'dd8e6e492e4e7d5c887088798e1fa43065340f376a1e16bdc5e0e88c99406001',
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def _inputs():
    raw, rows = {}, []
    for path, expected in SOURCES.items():
        data = (ROOT / path).read_bytes()
        actual = sha256(data)
        if actual != expected:
            raise ValueError(f'Pinned source changed: {path}: {actual}')
        raw[path] = data
        rows.append({'path': path, 'sha256': actual})
    index = json.loads(raw['reverse-engineering/raw/player-loadout/index.json'])
    contracts = json.loads(gzip.decompress(raw['reverse-engineering/raw/player-loadout/contracts.json.gz']))
    dump = gzip.decompress(raw['reverse-engineering/il2cpp/dump.cs.gz']).decode('utf-8')
    strings = json.loads(raw['reverse-engineering/il2cpp/stringliteral.json'])
    return raw, rows, index, contracts, dump, strings


def _method_lines(text, method):
    lines = text.splitlines()
    matches = [i for i, line in enumerate(lines) if line.startswith(f';;; {method} ')]
    if len(matches) != 1:
        raise ValueError(f'Expected one method block {method}; found {len(matches)}')
    start = matches[0]
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith(';;; ')), len(lines))
    return lines[start:end]


def _instructions(lines):
    return {m.group(1): line.strip() for line in lines
            if (m := re.match(r'\s*(0x[0-9a-f]+):\s+(.*)$', line))}


def _require(ins, address, text):
    line = ins.get(address)
    if line is None or text not in line:
        raise ValueError(f'Expected {address} to contain {text!r}; got {line!r}')
    return line


def _window(ins, start, end):
    lo, hi = int(start, 16), int(end, 16)
    lines = [line for addr, line in ins.items() if lo <= int(addr, 16) <= hi]
    lines.sort(key=lambda line: int(line.split(':', 1)[0], 16))
    if not lines or lines[0].split(':', 1)[0] != start or lines[-1].split(':', 1)[0] != end:
        raise ValueError(f'Missing exact evidence window {start}..{end}')
    return lines


def _rva_decl(dump, rva, signature):
    pattern = rf'// RVA: {re.escape(rva)}[^\n]*\n\s*{re.escape(signature)}'
    if not re.search(pattern, dump):
        raise ValueError(f'Missing dump declaration {rva} {signature}')


def build():
    raw, source_rows, index, contract_doc, dump, strings = _inputs()
    if index.get('status') != 'PROVISIONAL_PINNED_NATIVE_RECOVERY_NOT_RUNTIME':
        raise ValueError('Unexpected pinned player-loadout recovery status')
    device_contract = next((x for x in contract_doc['contracts']
                            if x.get('key_format') == 'PLAYER_DEVICE_{ship}_{slot}'), None)
    if not device_contract:
        raise ValueError('Pinned provisional device contract not found')

    device_asm = raw['reverse-engineering/raw/player-loadout/native/Player_Device_Saved_Datas.asm.txt'].decode()
    prefs_asm = raw['reverse-engineering/raw/ui-audit/extra-native/PlayerPreferences.asm.txt'].decode()
    stat_asm = raw['reverse-engineering/raw/il2cpp-consts/Device_Get_Data.asm.txt'].decode()
    attack_asm = raw['reverse-engineering/raw/il2cpp-consts/Player_Attack.asm.txt'].decode()
    health_asm = raw['reverse-engineering/raw/il2cpp-consts/Player_Health.asm.txt'].decode()
    board_asm = raw['reverse-engineering/raw/il2cpp-consts/Board_Players.asm.txt'].decode()

    _rva_decl(dump, '0x14E628C', 'public static int[] GetPlayerDevices(int playerIndex) { }')
    _rva_decl(dump, '0x14E64A4', 'public static void SetPlayerDevices(int playerIndex, int[] devices) { }')
    _rva_decl(dump, '0x12546D0', 'public static Device GetDevice(int instanceId) { }')
    _rva_decl(dump, '0x1250134', 'public static float GetStatValue2(Device _data) { }')
    _rva_decl(dump, '0x13F1A04', 'public static void SetInt(string key, int value) { }')
    _rva_decl(dump, '0x13F1A1C', 'public static int GetInt(string key, int valueDefault) { }')

    device_decl = re.search(r'public class Device\s*// TypeDefIndex: 581\s*\{(.*?)\n\}', dump, re.S)
    if not device_decl:
        raise ValueError('Could not locate Device type declaration')
    expected_fields = ['int id; // 0x10', 'int lv; // 0x14', 'int rank; // 0x18', 'int instanceId; // 0x1C']
    for field in expected_fields:
        if field not in device_decl.group(1):
            raise ValueError(f'Missing Device field declaration {field}')
    stats_decl = re.search(r'public class Device_Get_Data : MonoBehaviour // TypeDefIndex: 580\s*\{(.*?)\n\}', dump, re.S)
    if not stats_decl:
        raise ValueError('Could not locate Device_Get_Data type declaration')
    stat_fields = ['List<float[]> listStatValues; // 0x0', 'float[] percentByLevels2; // 0x10']
    for field in stat_fields:
        if field not in stats_decl.group(1):
            raise ValueError(f'Missing stat-table field declaration {field}')
    unity_playerprefs = dump[dump.find('public class PlayerPrefs // TypeDefIndex: 7791'):]
    for signature in ['public static void SetInt(string key, int value) { }',
                      'public static int GetInt(string key, int defaultValue) { }']:
        if signature not in unity_playerprefs:
            raise ValueError(f'Missing UnityEngine.PlayerPrefs declaration: {signature}')

    literal_prefix = any(isinstance(x, dict) and x.get('value') == 'PLAYER_DEVICE_' for x in strings)
    if not literal_prefix:
        raise ValueError('PLAYER_DEVICE_ string literal missing from pinned string table')

    get_i = _instructions(_method_lines(device_asm, 'GetPlayerDevices'))
    set_i = _instructions(_method_lines(device_asm, 'SetPlayerDevices'))
    pref_get_i = _instructions(_method_lines(prefs_asm, 'GetInt'))
    pref_set_i = _instructions(_method_lines(prefs_asm, 'SetInt'))
    stat_i = _instructions(_method_lines(stat_asm, 'GetStatValue2'))
    attack_i = _instructions(_method_lines(attack_asm, 'GetDeviceAddPowerPercent'))
    health_i = _instructions(_method_lines(health_asm, 'OnChangeDataDevice'))
    board_i = _instructions(_method_lines(board_asm, 'SetPlayerDeviceSlots'))

    anchors = {
        'getter_four_slot_loop': _require(get_i, '0x14e634c', 'cmp      w8, #4'),
        'getter_calls_GetInt_default_minus_one': _require(get_i, '0x14e6444', 'mov      w1, #-1'),
        'getter_GetInt_call': _require(get_i, '0x14e6450', 'bl       #0x13f1a1c'),
        'getter_stores_slot_value': _require(get_i, '0x14e6468', 'str      w0, [x8, #0x20]'),
        'setter_four_slot_limit': _require(set_i, '0x14e65d4', 'cmp      w8, #4'),
        'setter_calls_SetInt': _require(set_i, '0x14e65c8', 'bl       #0x13f1a04'),
        'setter_length_guard': _require(set_i, '0x14e653c', 'cmp      w8, w9'),
        'PlayerPreferences_SetInt_tailcalls_Unity_PlayerPrefs': _require(pref_set_i, '0x13f1a08', 'b        #0x277cc10'),
        'PlayerPreferences_GetInt_tailcalls_Unity_PlayerPrefs': _require(pref_get_i, '0x13f1a20', 'b        #0x277cca0'),
        'GetStatValue2_reads_Device_id': _require(stat_i, '0x125017c', 'ldrsw    x20, [x19, #0x10]'),
        'GetStatValue2_reads_Device_rank': _require(stat_i, '0x12501d4', 'ldrsw    x8, [x19, #0x18]'),
        'GetStatValue2_reads_Device_lv': _require(stat_i, '0x1250258', 'ldr      w11, [x19, #0x14]'),
        'attack_GetPlayerDevices': _require(attack_i, '0x1479e94', 'bl       #0x14e628c'),
        'attack_GetDevice': _require(attack_i, '0x1479ef8', 'bl       #0x12546d0'),
        'attack_GetStatValue2': _require(attack_i, '0x1479f50', 'bl       #0x1250134'),
        'health_GetPlayerDevices': _require(health_i, '0x14c5950', 'bl       #0x14e628c'),
        'health_GetDevice': _require(health_i, '0x14c59c8', 'bl       #0x12546d0'),
        'board_ui_GetPlayerDevices': _require(board_i, '0x12d5d88', 'bl       #0x14e628c'),
    }

    source_identity = {
        'recovery_status': index['status'],
        'xapk_sha256': index['xapk_sha256'],
        'global_metadata_sha256': index['inputs_sha256']['assets/bin/Data/Managed/Metadata/global-metadata.dat'],
        'libil2cpp_sha256': index['inputs_sha256']['lib/arm64-v8a/libil2cpp.so'],
        'dump_decompressed_sha256': index['dump_sha256_decompressed'],
        'apk_version': '1.3.118',
        'apk_version_code': 312,
        'apk_identity_note': 'Version and versionCode are sourced from the pinned APK-analysis note; XAPK/binary identities come from the pinned recovery index.',
    }

    return {
        'schema_version': 1,
        'task': '#22 save schema end-to-end',
        'status': 'bounded_static_device_save_load_trace_not_global_schema_or_runtime',
        'source_apk_identity': source_identity,
        'scope': {
            'save_family': 'player device loadout slots only',
            'scope_note': 'This is not a complete inventory of all global save keys, profile fields, cloud save, or migration formats.',
            'prior_contract_status': contract_doc['status'],
            'schema': {
                'key_format': device_contract['key_format'],
                'key_components': {'ship': 'playerIndex argument', 'slot': 'slot index 0..3'},
                'value_type': 'int32',
                'slot_count': 4,
                'normal_missing_default': -1,
                'backend': 'PlayerPreferences.GetInt/SetInt wrappers tail-branch to UnityEngine.PlayerPrefs.GetInt/SetInt.',
                'value_semantics': 'The saved integer is passed as GetDevice(instanceId) input by recovered consumers; Device.id is a distinct stat/category identifier.',
                'key_format_evidence_level': 'prior pinned partial contract + string literal + recovered key-builder call path; no independent runtime key readback.',
            },
            'writer': {
                'type': 'Player_Device_Saved_Datas', 'method': 'SetPlayerDevices',
                'signature': 'public static void SetPlayerDevices(int playerIndex, int[] devices)',
                'rva': '0x14E64A4',
                'behavior': [
                    'For each slot index 0..3, forms the per-player/per-slot key and writes devices[slot] through PlayerPreferences.SetInt.',
                    'Tracks whether any written value differs from -1.',
                    'If any value is present and FIRST_INSTALL_DEVICE currently reads zero, invokes the first-install event path and writes that flag to 1.',
                    'A null input takes an exception path; an input shorter than four can write earlier slots and then bounds-fault on a later iteration; an input longer than four is read only for slots 0..3.',
                ],
                'explicit_flush': 'No PlayerPrefs.Save call is present in this recovered SetPlayerDevices/PlayerPreferences.SetInt path. Flush/durability timing is not established.',
            },
            'reader': {
                'type': 'Player_Device_Saved_Datas', 'method': 'GetPlayerDevices',
                'signature': 'public static int[] GetPlayerDevices(int playerIndex)',
                'rva': '0x14E628C',
                'normal_behavior': 'Allocates a fresh int[4], reads each key using PlayerPreferences.GetInt(key, -1), and writes each value into the corresponding array slot.',
                'override': 'A recovered mode-4 + active-Game condition returns a fresh four-element array initialized to -1 without reading the saved keys; this condition is described by the pinned provisional contract and branch/array evidence.',
            },
            'storage_wrapper_chain': [
                {'method': 'Player_Device_Saved_Datas.SetPlayerDevices', 'rva': '0x14E64A4', 'calls': 'PlayerPreferences.SetInt', 'call_rva': '0x13F1A04'},
                {'method': 'PlayerPreferences.SetInt', 'rva': '0x13F1A04', 'tail_branch_to': 'UnityEngine.PlayerPrefs.SetInt', 'target_rva': '0x277CC10'},
                {'method': 'Player_Device_Saved_Datas.GetPlayerDevices', 'rva': '0x14E628C', 'calls': 'PlayerPreferences.GetInt(key, -1)', 'call_rva': '0x13F1A1C'},
                {'method': 'PlayerPreferences.GetInt', 'rva': '0x13F1A1C', 'tail_branch_to': 'UnityEngine.PlayerPrefs.GetInt', 'target_rva': '0x277CCA0'},
            ],
        },
        'load_consumers': [
            {
                'type': 'Player_Attack', 'method': 'GetDeviceAddPowerPercent', 'rva': '0x1479E34',
                'static_path': ['GetPlayerDevices(playerIndex)', 'skip saved value -1', 'GetDevice(saved value) as instanceId',
                                'read returned Device.id', 'branch by id category', 'call GetStatValue1 and/or GetStatValue2',
                                'add normalized stat values into Player_Attack object fields'],
                'observed_categories': {
                    '2000..2999': {'stat_calls': ['GetStatValue1', 'GetStatValue2'], 'written_offsets': ['0x5C', '0x6C']},
                    '3000..3999': {'stat_calls': ['GetStatValue1'], 'written_offsets': ['0x60']},
                    '4000..4999': {'stat_calls': ['GetStatValue1', 'GetStatValue2'], 'written_offsets': ['0x68', '0x64']},
                },
                'effect_boundary': 'This proves a saved-loadout-to-stat-consumer path and writes on the attack object; it does not by itself prove when this method is invoked or a final combat damage result.',
            },
            {
                'type': 'Player_Health', 'method': 'OnChangeDataDevice', 'rva': '0x14C58EC',
                'static_path': ['GetPlayerDevices(_idPlayer)', 'skip -1', 'GetDevice(saved value)', 'inspect Device.id', 'use GetStatValue1 in health-related accumulator paths'],
                'observed_category': 'Device.id 1000..1999',
                'effect_boundary': 'Assembly shows health-object fields updated; runtime timing/visible health outcome are not asserted.',
            },
            {
                'type': 'Board_Players', 'method': 'SetPlayerDeviceSlots', 'rva': '0x12D5BD4',
                'static_path': 'Obtains a player id from its player-info object, calls GetPlayerDevices, and stores the returned array on the UI/controller object before slot iteration.',
                'effect_boundary': 'A recovered UI/model consumer only; no screenshot or render claim.',
            },
        ],
        'device_record_and_stat': {
            'device_type': 'Device', 'type_def_index': 581,
            'fields': [
                {'name': 'id', 'type': 'int', 'offset': '0x10', 'role': 'stat/category id used by consumers'},
                {'name': 'lv', 'type': 'int', 'offset': '0x14', 'role': 'level input to GetStatValue2'},
                {'name': 'rank', 'type': 'int', 'offset': '0x18', 'role': 'rank-indexed base-stat selector'},
                {'name': 'instanceId', 'type': 'int', 'offset': '0x1C', 'role': 'declared instance identifier; GetDevice body is unavailable here'},
            ],
            'lookup': {
                'signature': 'public static Device GetDevice(int instanceId)', 'rva': '0x12546D0',
                'evidence_level': 'dump declaration and observed callsites only',
                'gap': 'The implementation body was not present in the method-body exports consulted for this report; do not infer lookup tables, identity equality, cache invalidation, or null/error handling.',
            },
            'stat_table_fields': [
                {'name': 'listStatValues', 'type': 'List<float[]>', 'offset': '0x0', 'type_def_index': 580},
                {'name': 'percentByLevels2', 'type': 'float[]', 'offset': '0x10', 'type_def_index': 580},
            ],
            'GetStatValue2': {
                'signature': 'public static float GetStatValue2(Device _data)', 'rva': '0x1250134',
                'observed_formula': 'Let q be integer Device.id / 1000. Read listStatValues[q + 4][Device.rank] as base. If base == 0, return 0; otherwise add percentByLevels2[q - 1][Device.lv + 1] * (Device.lv + 1).',
                'evidence_level': 'recovered native ARM64 method body; collection/helper names use the recovered dump/context and index operations.',
                'bounds': 'The recovered method contains null and bounds exception paths; dataset contents and all valid id/rank/level domains are not exhaustively enumerated here.',
            },
        },
        'evidence': {
            'anchors': anchors,
            'windows': [
                {'source': 'reverse-engineering/raw/player-loadout/native/Player_Device_Saved_Datas.asm.txt', 'method': 'GetPlayerDevices', 'start': '0x14e6348', 'end': '0x14e63c0', 'purpose': 'mode/active-scene override and fresh sentinel-array return', 'instructions': _window(get_i, '0x14e6348', '0x14e63c0')},
                {'source': 'reverse-engineering/raw/player-loadout/native/Player_Device_Saved_Datas.asm.txt', 'method': 'GetPlayerDevices', 'start': '0x14e634c', 'end': '0x14e647c', 'purpose': 'normal four-key read path', 'instructions': _window(get_i, '0x14e634c', '0x14e647c')},
                {'source': 'reverse-engineering/raw/player-loadout/native/Player_Device_Saved_Datas.asm.txt', 'method': 'SetPlayerDevices', 'start': '0x14e6534', 'end': '0x14e65dc', 'purpose': 'four-slot writer and input bounds path', 'instructions': _window(set_i, '0x14e6534', '0x14e65dc')},
                {'source': 'reverse-engineering/raw/player-loadout/native/Player_Device_Saved_Datas.asm.txt', 'method': 'SetPlayerDevices', 'start': '0x14e65e0', 'end': '0x14e6638', 'purpose': 'FIRST_INSTALL_DEVICE read/feature/write path', 'instructions': _window(set_i, '0x14e65e0', '0x14e6638')},

                {'source': 'reverse-engineering/raw/ui-audit/extra-native/PlayerPreferences.asm.txt', 'method': 'SetInt/GetInt', 'start': '0x13f1a04', 'end': '0x13f1a20', 'instructions': _window({**pref_set_i, **pref_get_i}, '0x13f1a04', '0x13f1a20')},
                {'source': 'reverse-engineering/raw/il2cpp-consts/Player_Attack.asm.txt', 'method': 'GetDeviceAddPowerPercent', 'start': '0x1479e94', 'end': '0x1479f60', 'instructions': _window(attack_i, '0x1479e94', '0x1479f60')},
                {'source': 'reverse-engineering/raw/il2cpp-consts/Device_Get_Data.asm.txt', 'method': 'GetStatValue2', 'start': '0x125017c', 'end': '0x1250284', 'instructions': _window(stat_i, '0x125017c', '0x1250284')},
                {'source': 'reverse-engineering/raw/il2cpp-consts/Player_Health.asm.txt', 'method': 'OnChangeDataDevice', 'start': '0x14c5948', 'end': '0x14c5a78', 'instructions': _window(health_i, '0x14c5948', '0x14c5a78')},
                {'source': 'reverse-engineering/raw/il2cpp-consts/Board_Players.asm.txt', 'method': 'SetPlayerDeviceSlots', 'start': '0x12d5d80', 'end': '0x12d5d90', 'instructions': _window(board_i, '0x12d5d80', '0x12d5d90')},
            ],
            'evidence_levels': [
                'Native body: direct instruction-level semantics for the recovered method body.',
                'Managed declaration: method and field names/signatures/offsets from pinned dump.cs.gz.',
                'Pinned contract corroboration: exact key family and mode/scene override semantics from contracts.json.gz, which itself is marked provisional static partial.',
                'Callsite-only: GetDevice implementation is not available in consulted recovered bodies.',
            ],
        },
        'source_pins': source_rows,
        'scope_limits': [
            'This is a device-slot save/load trace, not a complete global save schema or complete inventory of PlayerPrefs keys.',
            'Static pinned native recovery only: no live app execution, persistence round-trip, readback, render, or screenshot verification occurred.',
            'No schema version, migration, cross-device/cloud sync, transactional atomicity, or runtime durability guarantee is established.',
            'No explicit PlayerPrefs.Save call was observed on the scoped setter chain; this does not establish the engine/platform flush policy.',
            'GetDevice implementation body and its caching/identity semantics remain unresolved; only its declared signature and callsites are established.',
            'No exhaustive global caller/callee search is claimed beyond the specific pinned exports listed in source_pins.',
            'Existing report 66 and datas/player_loadout_persistence.json are prior evidence and were not overwritten; this artifact is a scoped follow-on trace.',
        ],
    }


def write():
    data = build()
    encoded = (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path = ROOT / OUTPUT
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(encoded, mtime=0))
    return data


if __name__ == '__main__':
    artifact = write()
    print(f'Wrote {OUTPUT} ({len(artifact["source_pins"])} pinned source files)')
