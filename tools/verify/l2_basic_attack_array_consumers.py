"""Trace Board_Players attack arrays through recovered ARM64, without name-only inference."""
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path('datas/l2_basic_attack_array_consumers.json.gz')
SOURCES = {
    'docs/apk-analysis/PHAN_TICH_WINDWINGS_APK.md': 'f799e2a25cb60c9957b29d8c11afd683c289e8c60ae400562e4bf8dec8bcb3bd',
    'reverse-engineering/il2cpp/dump.cs.gz': 'e08f23fb6c90e07288e5b202e0ce1e7c5e82a7feb5ccae7aa08aaec3ad166454',
    'reverse-engineering/raw/il2cpp-consts/Board_Players.asm.txt': 'dd8e6e492e4e7d5c887088798e1fa43065340f376a1e16bdc5e0e88c99406001',
    'reverse-engineering/il2cpp/ia-resolved.json': '2583a4c472400fe85f96b96f0a8d2839963eddae95760483424119501d989e37',
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def _inputs():
    raw = {}
    source_rows = []
    for path, expected in SOURCES.items():
        data = (ROOT / path).read_bytes()
        actual = sha256(data)
        if actual != expected:
            raise ValueError(f'Pinned source changed: {path}: {actual}')
        raw[path] = data
        source_rows.append({'path': path, 'sha256': actual})
    apk_note = raw['docs/apk-analysis/PHAN_TICH_WINDWINGS_APK.md'].decode('utf-8')
    apk_identity = {
        'version': '1.3.118',
        'version_code': 312,
        'base_apk_sha256': '6843e79347f5b0bb68e4a2f9e1b1a3152e31d0875d4821b9928ad5799a95e1e1',
        'identity_source': 'docs/apk-analysis/PHAN_TICH_WINDWINGS_APK.md',
        'identity_note': 'The original APK bytes are not re-opened by this report generator; this is the pinned workspace source identity.',
    }
    for needle in (apk_identity['base_apk_sha256'], '1.3.118', 'versionCode **312**'):
        if needle not in apk_note:
            raise ValueError(f'APK identity is not present in pinned source note: {needle}')
    dump = gzip.decompress(raw['reverse-engineering/il2cpp/dump.cs.gz']).decode('utf-8')
    asm = raw['reverse-engineering/raw/il2cpp-consts/Board_Players.asm.txt'].decode('utf-8')
    ia = json.loads(raw['reverse-engineering/il2cpp/ia-resolved.json'])['methods']
    return dump, asm, ia, source_rows, apk_identity


def _method_lines(asm, method):
    lines = asm.splitlines()
    header = f';;; {method} '
    starts = [i for i, line in enumerate(lines) if line.startswith(header)]
    if len(starts) != 1:
        raise ValueError(f'Expected one ARM64 method block for {method}, found {len(starts)}')
    start = starts[0]
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith(';;; ')), len(lines))
    return lines[start:end]


def _instructions(method_lines):
    found = {}
    for line in method_lines:
        match = re.match(r'\s*(0x[0-9a-f]+):\s+(.*)$', line)
        if match:
            found[match.group(1)] = line.strip()
    return found


def _window(instructions, start, end):
    lo, hi = int(start, 16), int(end, 16)
    rows = [line for addr, line in instructions.items() if lo <= int(addr, 16) <= hi]
    rows.sort(key=lambda line: int(line.split(':', 1)[0], 16))
    if not rows or rows[0].split(':', 1)[0] != start or rows[-1].split(':', 1)[0] != end:
        raise ValueError(f'Missing exact instruction window {start}..{end}')
    return rows


def _require(instructions, address, fragment):
    line = instructions.get(address)
    if line is None or fragment not in line:
        raise ValueError(f'Expected {address} to contain {fragment!r}; got {line!r}')
    return line


def _float_payload(record):
    if record.get('length_valid') is not True or record.get('len') != 24:
        raise ValueError(f'Expected initialized float[24]: {record}')
    raw = bytes.fromhex(record['raw'])
    payload = raw[:24 * 4]
    if len(payload) != 96:
        raise ValueError('Expected exactly 96 initialized payload bytes')
    values = list(struct.unpack('<24f', payload))
    return {
        'element_type': 'float32',
        'length': 24,
        'payload_sha256': sha256(payload),
        'first_value': values[0],
        'unique_value_count': len(set(values)),
    }


def build():
    dump, asm, ia, sources, apk_identity = _inputs()
    class_match = re.search(r'public class Board_Players\s*:\s*Board[^\n]*\n\{(.*?)\n\}', dump, re.S)
    if not class_match:
        raise ValueError('Board_Players declaration not found in dump.cs.gz')
    declaration = class_match.group(1)
    field_declarations = {
        'allBasicAtk': 'private static float[] allBasicAtk; // 0x10',
        'allDeltaAtk': 'private static float[] allDeltaAtk; // 0x18',
    }
    for name, line in field_declarations.items():
        if line not in declaration:
            raise ValueError(f'Missing target declaration: {line}')

    get_power_decl = re.search(r'// RVA: 0x12D5DFC[^\n]*\n\s*private string GetPlayerPower\(int _indexPlayer\)', declaration)
    set_info_decl = re.search(r'// RVA: 0x12D1048[^\n]*\n\s*private void SetPlayerInfo\(\)', declaration)
    if not get_power_decl or not set_info_decl:
        raise ValueError('Expected GetPlayerPower/SetPlayerInfo declarations and RVAs')
    level_decl = re.search(r'// RVA: 0x14E3B20[^\n]*\n\s*public static int GetPlayerLevel\(int _playerIndex\)', dump)
    if not level_decl:
        raise ValueError('GetPlayerLevel declaration at RVA 0x14E3B20 not found')

    cctor_i = _instructions(_method_lines(asm, 'cctor'))
    power_i = _instructions(_method_lines(asm, 'GetPlayerPower'))
    set_i = _instructions(_method_lines(asm, 'SetPlayerInfo'))
    anchors = {
        'cctor_class_static_fields': _require(cctor_i, '0x12d63cc', 'ldr      x8, [x8, #0xb8]'),
        'cctor_basic_store': _require(cctor_i, '0x12d6404', 'str      x19, [x8, #0x10]'),
        'cctor_delta_store': _require(cctor_i, '0x12d642c', 'str      x19, [x8, #0x18]'),
        'power_class_reference': _require(power_i, '0x12d5e74', 'ldr      x22, [x22, #0xda0]'),
        'power_static_fields': _require(power_i, '0x12d5ea8', 'ldr      x11, [x8, #0xb8]'),
        'basic_array_load': _require(power_i, '0x12d5eac', 'ldr      x8, [x11, #0x10]'),
        'delta_array_load': _require(power_i, '0x12d5edc', 'ldr      x11, [x11, #0x18]'),
        'player_level_call': _require(power_i, '0x12d5e88', 'bl       #0x14e3b20'),
        'delta_element_load': _require(power_i, '0x12d5f0c', 'ldr      s1, [x9, #0x20]'),
        'basic_element_load': _require(power_i, '0x12d5f18', 'ldr      s8, [x8, #0x20]'),
        'delta_times_level': _require(power_i, '0x12d5f20', 'fmul     s0, s1, s0'),
        'add_one': _require(power_i, '0x12d5f28', 'fadd     s9, s0, s1'),
        'scale_by_basic': _require(power_i, '0x12d5f4c', 'fmul     s9, s8, s9'),
        'set_info_call': _require(set_i, '0x12d13fc', 'bl       #0x12d5dfc'),
        'text_player_power_field': _require(set_i, '0x12d13f4', 'ldr      x21, [x19, #0x40]'),
        'text_setter_call': _require(set_i, '0x12d142c', 'blr      x9'),
    }

    cctor_rows = ia.get('Board_Players.cctor')
    if not isinstance(cctor_rows, list) or len(cctor_rows) != 2:
        raise ValueError('Expected exactly two recovered Board_Players.cctor InitializeArray records')
    initializer_by_addr = {row['addr']: row for row in cctor_rows}
    basic_init = initializer_by_addr.get('0x12d63f4')
    delta_init = initializer_by_addr.get('0x12d641c')
    if not basic_init or not delta_init:
        raise ValueError('Expected cctor array initializers at 0x12d63f4 and 0x12d641c')

    cctor_lines = _window(cctor_i, '0x12d63e0', '0x12d642c')
    power_lines = _window(power_i, '0x12d5ea8', '0x12d5f4c')
    set_lines = _window(set_i, '0x12d13f0', '0x12d142c')
    return {
        'schema_version': 1,
        'task': '#20 Board_Players attack-array consumers',
        'status': 'confirmed_consumer_in_recovered_ARM64',
        'source_apk_identity': apk_identity,
        'target': {
            'type': 'Board_Players',
            'fields': [
                {'name': 'allBasicAtk', 'declaration': field_declarations['allBasicAtk'],
                 'static_offset': '0x10', 'element_type': 'float32', 'length': 24,
                 'initialized_by': {'address': '0x12d63f4', 'store_address': '0x12d6404',
                                    **_float_payload(basic_init)}},
                {'name': 'allDeltaAtk', 'declaration': field_declarations['allDeltaAtk'],
                 'static_offset': '0x18', 'element_type': 'float32', 'length': 24,
                 'initialized_by': {'address': '0x12d641c', 'store_address': '0x12d642c',
                                    **_float_payload(delta_init)}},
            ],
        },
        'consumer': {
            'type': 'Board_Players',
            'method': 'GetPlayerPower',
            'signature': 'private string GetPlayerPower(int _indexPlayer)',
            'rva': '0x12D5DFC',
            'direct_array_reads': {
                'allBasicAtk': {'instruction_address': '0x12d5eac', 'static_offset': '0x10',
                                'value_load_address': '0x12d5f18'},
                'allDeltaAtk': {'instruction_address': '0x12d5edc', 'static_offset': '0x18',
                                'value_load_address': '0x12d5f0c'},
            },
            'level_source': {'method': 'Player_Get_Datas.GetPlayerLevel', 'rva': '0x14E3B20',
                             'call_address': '0x12d5e88'},
            'indexing': 'Subtracts this.indexDefault (Board_Players instance offset 0x138) from _indexPlayer, then bounds-checks each array access.',
            'observed_float_operations': [
                'delta[i] * GetPlayerLevel(_indexPlayer)',
                '1.0f + previous_product',
                'basic[i] * previous_sum',
            ],
            'evidence_windows': [
                {'source': 'reverse-engineering/raw/il2cpp-consts/Board_Players.asm.txt',
                 'method': 'cctor', 'start': '0x12d63e0', 'end': '0x12d642c', 'instructions': cctor_lines},
                {'source': 'reverse-engineering/raw/il2cpp-consts/Board_Players.asm.txt',
                 'method': 'GetPlayerPower', 'start': '0x12d5ea8', 'end': '0x12d5f4c', 'instructions': power_lines},
            ],
        },
        'downstream_display': {
            'method': 'SetPlayerInfo', 'rva': '0x12D1048',
            'calls_GetPlayerPower_at': '0x12d13fc',
            'textPlayerPower_field_offset': '0x40',
            'field_name_source': 'dump.cs.gz Board_Players field declaration',
            'evidence_window': {'source': 'reverse-engineering/raw/il2cpp-consts/Board_Players.asm.txt',
                                'method': 'SetPlayerInfo', 'start': '0x12d13f0', 'end': '0x12d142c',
                                'instructions': set_lines},
        },
        'anchors': anchors,
        'sources': sources,
        'scope_limits': [
            'This establishes a real direct reader in the recovered ARM64 method body; it does not claim an exhaustive global cross-reference over native code not present in the workspace.',
            'The field identity comes from Board_Players declarations and matching static-field offsets, not Board_Drones naming or values.',
            'This is source/disassembly evidence, not a live runtime readback or screenshot.',
            'No conclusion about combat damage is made; the confirmed caller displays the computed power through textPlayerPower.',
        ],
    }


def write_artifact():
    data = build()
    encoded = (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    out = ROOT / OUTPUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(gzip.compress(encoded, mtime=0))
    return out


if __name__ == '__main__':
    print(write_artifact().relative_to(ROOT))
