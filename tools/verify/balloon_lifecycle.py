"""Raw-backed pool parenting, map scroll and BB gun lifecycle audit. Static only."""
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
from early_ui_native import section
from ui_loader_analysis import metadata_loads
from ui_routing import direct_calls

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'reverse-engineering/raw'
SELECT = {
    'PoolingManager': ['getObject', 'poolObject', 'GetObject', 'ctor'],
    'AirFree_Spawner': ['OnSpawn'],
    'PinMap_Spawner': ['OnSpawn'],
    'PinTerrain_Spawner': ['Start', 'OnSpawn'],
    'MapController': ['Awake', 'Update', 'ScrollMap', 'ScrollBackgrounds', 'IsScrolling', 'SetSpeedMap'],
    'Enemy_Movement': ['OnEnable', 'Update', 'PathFollow', 'FixedUpdate', 'SetPosition', 'ctor'],
    'Machine_Gun_Attack': ['OnEnable', 'FixedUpdate', 'IsOutScreen', 'Shoot', 'NormalShoot', 'BarrelShoot', 'Shooting', 'OnBulletNormalDestroyed', 'OnBulletNormalCollided', 'OnStartTurnShoot', 'OnEndTurnShoot'],
    'Boss_BodyPhysics': ['OnEnable', 'OnDefeat', 'OnCollisionStay2D', 'OnTriggerStay2D', 'OnTriggerExit2D'],
    'Obj_Collider': ['Init', 'GetRootTransform', 'GetIDamageable', 'GetIHealth'],
}


def scroll_y(y, dt, multiple, speed, boost=1):
    """Algebra only; not float32 Unity timing or an instance/world transform model."""
    return y - multiple * dt * speed * boost


def gun_fixed_gate(is_attack, type_delay, now, time_to_start, outside, stunned):
    return bool(is_attack and not (type_delay == 1 and now < time_to_start)
                and not (type_delay == 0 and outside) and not stunned)


def movement_routes(moving, move_type, path_present, is_turret, movein):
    """Routes enabled, not whether callback actually fires; no runtime state reset assumption."""
    if not moving:
        return []
    routes = []
    if move_type == 0 and path_present:
        routes.append('path')
    if move_type == 1:
        routes.append('waypoints')
    if move_type == 2:
        routes.append('linear_update')
    if is_turret:
        routes.append('turret_boundary')
    if movein and move_type == 2:
        routes.append('linear_boundary')
    return routes


def build():
    dump_path = ROOT / 'reverse-engineering/il2cpp/dump.cs.gz'
    dump = gzip.open(dump_path, 'rt').read()
    declarations, addresses = {}, {}
    for block in re.split(r'(?=// Namespace:)', dump):
        cls = re.search(r'(?:class|enum|interface) ([^ :\n]+)', block)
        if not cls:
            continue
        namespace = re.match(r'// Namespace:([^\n]*)', block)[1].strip()
        declarations[namespace + '.' + cls[1] if namespace else cls[1]] = block
        for match in re.finditer(r'// RVA: (0x[\dA-Fa-f]+)[^\n]*\n([^\n]+)', block):
            addresses[int(match[1], 16)] = dict(class_name=cls[1], signature=match[2].strip())
    metadata_path = RAW / 'ui-audit/metadata-index.json.gz'
    reloc_path = RAW / 'ui-audit/native-relocations.json.gz'
    reloc = json.load(gzip.open(reloc_path, 'rt'))
    index = {}
    for group, rows in json.load(gzip.open(metadata_path, 'rt'))['tables'].items():
        for row in rows:
            index.setdefault(row['Address'], []).append(dict(row, group=group))
    sources = {dump_path, metadata_path, reloc_path}
    methods, records = {}, []
    for cls, names in SELECT.items():
        path = RAW / f'ui-audit/extra-native/{cls}.asm.txt'
        inventory_path = path.with_suffix('').with_suffix('.json')
        sources.update((path, inventory_path))
        inventory = json.loads(inventory_path.read_text())
        for name in names:
            candidates = [m for m in inventory['methods'] if m['method'] == name]
            inv = candidates[0]  # Only first GetObject overload (int); preserve its signature.
            assert not inv['size_capped']
            asm = section(path.read_text(), name)
            methods[cls, name] = asm
            records.append(dict(class_name=cls, method=name, signature=inv['signature'],
                                source=str(path.relative_to(ROOT)), inventory=inv, asm=asm,
                                calls=direct_calls(asm, addresses),
                                metadata_loads=metadata_loads(asm, reloc['relocations'], index)))
    balloon_path = RAW / 'balloon-animation/bb-36001-animation.json.gz'
    sources.add(balloon_path)
    balloon = json.load(gzip.open(balloon_path, 'rt'))
    assert balloon['inputs_sha256']['libil2cpp.so'] == reloc['native_sha256']
    root_transform = next(c for c in balloon['nodes'][0]['components'] if c['type'] == 'Transform')
    guns = [dict(path=n['path'], **c) for n in balloon['nodes'] for c in n['components'] if c.get('script_class') == 'Machine_Gun_Attack']
    def has(cls, method, *parts):
        return all(p in methods[cls, method] for p in parts)
    def targets(cls, method):
        return {c['target_rva'] for r in records if (r['class_name'], r['method']) == (cls, method) for c in r['calls']}
    checks = dict(
        prefab_root_no_parent=root_transform['tree']['m_Father'] == dict(m_FileID=0, m_PathID=0),
        airfree_gets_pool_object='0x123a9fc' in targets('AirFree_Spawner', 'OnSpawn'),
        airfree_no_direct_reparent='0x2789b64' not in targets('AirFree_Spawner', 'OnSpawn'),
        pool_get_no_direct_reparent='0x2789b64' not in targets('PoolingManager', 'getObject'),
        pool_return_reparents=has('PoolingManager', 'poolObject', '0x123a944: mov      x0, x19', '0x123a95c: bl       #0x277f14c', '0x123a970: bl       #0x2789b64'),
        pool_return_deactivates_before_reparent=has('PoolingManager', 'poolObject', '0x123a748: mov      w1, wzr', '0x123a750: bl       #0x2781804'),
        pool_get_inactive_clone=has('PoolingManager', 'getObject', '0x123a5d0: mov      w1, wzr', '0x123a5dc: bl       #0x2781804'),
        pool_get_common_world_position_rotation=has('PoolingManager', 'getObject', '0x123a614: bl       #0x2789258', '0x123a63c: bl       #0x27894d4'),
        pinmap_reparents_to_spawner_parent=has('PinMap_Spawner', 'OnSpawn', '0x1466b3c: bl       #0x277f14c', '0x1466b48: bl       #0x27890c4', '0x1466b60: bl       #0x2789b64'),
        pinterrain_reparents_to_serialized_field=has('PinTerrain_Spawner', 'OnSpawn', '0x146714c: ldr      x1, [x19, #0x30]', '0x1467154: bl       #0x2789b64'),
        map_awake_extracts_enemy_layer_index1=has('MapController', 'Awake', '0x1329fd0: mov      w1, #1', '0x1329fe0: str      x0, [x19, #0x28]', '0x132a004: bl       #0x1bd9440'),
        map_update_enters_scroll_directly=has('MapController', 'Update', '0x132ba34: b        #0x132ba38'),
        map_scroll_deltaTime=has('MapController', 'ScrollMap', '0x132ba7c: bl       #0x2786de8', '0x132ba8c: fmul     s9, s8, s0'),
        map_layers_subtract_with_boost=has('MapController', 'ScrollMap', '0x132bae8: ldr      s1, [x19, #0x7c]', '0x132baf4: fmul     s0, s0, s1', '0x132baf8: fsub     s0, s8, s0'),
        enemy_layer_flag_and_no_boost=has('MapController', 'ScrollMap', '0x132bb40: ldrb     w8, [x19, #0x78]', '0x132bb44: cbz      w8, #0x132bb90', '0x132bb74: fmul     s3, s9, s3', '0x132bb78: fsub     s1, s1, s3'),
        position_activates_without_setting_move_type=has('Enemy_Movement', 'SetPosition', '0x15840a8: bl       #0x2789258', '0x15840c4: mov      w1, #1', '0x15840d0: b        #0x2781804') and '#0x4c]' not in methods['Enemy_Movement', 'SetPosition'],
        movement_onenable_only_zfixed=has('Enemy_Movement', 'OnEnable', '0x1586074: str      s0, [x19, #0x48]') and '#0x4c]' not in methods['Enemy_Movement', 'OnEnable'] and '#0x50]' not in methods['Enemy_Movement', 'OnEnable'],
        path_null_early_return=has('Enemy_Movement', 'PathFollow', '0x15861ec: ldr      x8, [x0, #0x50]', '0x15861f0: cbz      x8, #0x158641c', '0x1586434: ret'),
        gun_onenable_time_reset=has('Machine_Gun_Attack', 'OnEnable', '0x1453e80: bl       #0x2786dc0', '0x1453e94: fadd     s0, s0, s1', '0x1453e98: str      s0, [x19, #0x78]'),
        gun_onenable_resets_counts_stun=has('Machine_Gun_Attack', 'OnEnable', '0x1453e88: stur     xzr, [x19, #0x7c]', '0x1453e8c: str      wzr, [x19, #0xa0]', '0x1453e9c: strb     wzr, [x19, #0xb8]'),
        gun_gate_isattack_delay_outscreen_stun=has('Machine_Gun_Attack', 'FixedUpdate', '#0x30]', '#0x38]', '#0xa8]', '0x1454060: bl       #0x1453f54', '#0xb8]'),
        gun_normal_or_barrel_by_brate=has('Machine_Gun_Attack', 'Shoot', '#0x40]', '0x14540dc: b        #0x14540e8', '0x14540e4: b        #0x14541a8'),
        gun_no_declared_ondisable=' OnDisable(' not in declarations['SpaceShooter.Machine_Gun_Attack'],
        both_guns_empty_mode_overrides=len(guns) == 2 and all(g['tree']['allGunDatas'] == [] for g in guns),
        both_guns_empty_persistent_turn_hooks=all(g['tree'][e]['m_PersistentCalls']['m_Calls'] == [] for g in guns for e in ('eventStart', 'eventEnded')),
        start_end_hooks_invoke_unityevent=all('0x278ef98' in targets('Machine_Gun_Attack', n) for n in ('OnStartTurnShoot', 'OnEndTurnShoot')),
    )
    hashes = []
    for path in sorted(sources):
        b = path.read_bytes()
        if path.suffix == '.gz':
            b = gzip.decompress(b)
        hashes.append(dict(path=str(path.relative_to(ROOT)), hash_bytes='gzip-decompressed' if path.suffix == '.gz' else 'file', sha256=hashlib.sha256(b).hexdigest()))
    return dict(status='PROVISIONAL_STATIC_NOT_PLAYBACK', native_sha256=reloc['native_sha256'],
                sources=hashes, methods=records, root_transform=root_transform, guns=guns,
                declarations={k: declarations[k] for k in ('PoolingManager', 'MapController', 'MapController.MapLayer', 'SpaceShooter.Machine_Gun_Attack', 'Machine_Gun_Attack.TypeDelay', 'SpaceShooter.EnemySystem.Enemy_Movement', 'SpaceShooter.SpawnSystem.PinTerrain_Spawner')},
                integer_float_bits=dict(pool_pref_pos=struct.unpack('<f', struct.pack('<I', (-0x3d3a0000) & 0xffffffff))[0], get_object_default_pos=struct.unpack('<f', struct.pack('<I', (-0x3c810000) & 0xffffffff))[0]),
                checks=checks)


if __name__ == '__main__':
    result = build()
    assert all(result['checks'].values()), result['checks']
    with gzip.GzipFile(filename=str(RAW / 'balloon-animation/lifecycle-parent-scroll.json.gz'), mode='wb', mtime=0) as f:
        f.write(json.dumps(result, ensure_ascii=False, indent=2).encode())
    print(len(result['methods']), 'methods;', len(result['checks']), 'checks')
