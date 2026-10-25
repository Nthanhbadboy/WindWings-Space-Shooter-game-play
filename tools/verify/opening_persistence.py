"""Scoped APK persistence contracts for opening-stage reconstruction, not a save emulator."""
import gzip
import hashlib
import json
from pathlib import Path
import re
from early_ui_native import section
from ui_loader_analysis import metadata_loads
from ui_routing import direct_calls

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'reverse-engineering/raw'
SELECT = {
    'GP_Tutorials': ('il2cpp-consts', ['get_IndexTutorial', 'set_IndexTutorial', 'IsTutTouchSkillDone', 'RefreshDatas', 'CheckRunTutorialNew', 'cctor']),
    'GP_Tutorials.__c__DisplayClass39_0': ('il2cpp-consts', ['<CheckRunTutorialNew>b__1']),
    'Stage_Datas': ('ui-audit/extra-native', ['get_StageTarget', 'set_StageTarget', 'get_ZoneUnlocked', 'set_ZoneUnlocked', 'GetStarStageMaster', 'SetStarStageMaster', 'RefreshDatas', 'cctor']),
    'GameDatas': ('ui-audit/extra-native', ['get_StarCount', 'set_StarCount', 'RefreshDatas', 'cctor']),
    'Drone_Saved_Datas': ('ui-audit/extra-native', ['GetDroneUsed', 'SetDroneUsed', 'IsDroneUnlocked', 'SetDroneUnlocked']),
    'PlayerPreferences': ('ui-audit/extra-native', ['get_path', 'Awake', 'LoadFromDisk', 'SetValue', 'GetValue', 'SetInt', 'GetInt', 'SetFloat', 'GetFloat', 'SetString', 'GetString', 'DeleteAll', 'DeleteKey', 'SaveToDisk', 'GetRawData', 'OnApplicationQuit', 'OnApplicationFocus', 'cctor']),
}


def stage_target_read(cached, stored, zone, *, max_stage, max_zone=24):
    """Valid nonnegative bounded normal inputs; max_stage must be supplied for writes.

    One getter invocation, not a while-loop/migration or whole-game simulation.
    """
    value = stored if cached == -1 else cached
    write = None
    if zone < max_zone and value < zone * 10:
        value = min(value + 1, max_stage)
        write = value
    return value, write


def tutorial_read(cached, stored, stage_target):
    """Normal company!=Test branch after resolving StageTarget; models one read."""
    value = stored if cached == -1 else cached
    return (6, 6) if stage_target >= 2 and value == 0 else (value, None)


def drone_used_read(stored=0):
    return (0, 0) if stored < 0 else (stored, None)


def drone_unlocked_read(drone_id, stored=0):
    """Non-Test branch; does not validate IDs against the actual roster."""
    if drone_id == 20001:
        return True, 1 if stored == 0 else None
    if drone_id < 20002:
        return True, None
    return stored == 1, None


def persistence_key(family, **args):
    """Literal key construction; valid integer parameters only, no clamping/validation."""
    formats = {'stars': 'StarStageMaster{stage}_{mode}', 'drone_used': 'DroneUsed{slot}', 'drone_unlocked': 'DroneUnlocked{drone}'}
    return formats[family].format(**args)


def build():
    dump_path = ROOT / 'reverse-engineering/il2cpp/dump.cs.gz'
    dump_bytes = gzip.decompress(dump_path.read_bytes())
    declarations, by_rva = {}, {}
    for block in re.split(r'(?=// Namespace:)', dump_bytes.decode()):
        cls = re.search(r'(?:class|enum) ([^ :\n]+)', block)
        if not cls:
            continue
        declarations[cls[1]] = block
        for m in re.finditer(r'// RVA: (0x[\dA-Fa-f]+)[^\n]*\n([^\n]+)', block):
            by_rva[int(m[1], 16)] = dict(class_name=cls[1], signature=m[2].strip())
    audit = RAW / 'ui-audit'
    rel_path = audit / 'native-relocations.json.gz'
    meta_path = audit / 'metadata-index.json.gz'
    relocations = json.load(gzip.open(rel_path, 'rt'))['relocations']
    index = {}
    for group, rows in json.load(gzip.open(meta_path, 'rt'))['tables'].items():
        for row in rows:
            index.setdefault(row['Address'], []).append(dict(row, group=group))
    sources = []
    def pin(path):
        data = path.read_bytes()
        if path.suffix == '.gz':
            data = gzip.decompress(data)
        sources.append(dict(path=str(path.relative_to(ROOT)), sha256_decompressed=hashlib.sha256(data).hexdigest()))
    for path in (dump_path, rel_path, meta_path):
        pin(path)
    records, methods = [], {}
    for cls, (folder, names) in SELECT.items():
        path = RAW / folder / (cls + '.asm.txt')
        inv_path = RAW / folder / (cls + '.json')
        pin(path); pin(inv_path)
        inventory = json.loads(inv_path.read_text())['methods']
        for name in names:
            asm = section(path.read_text(), name)
            inv = next(m for m in inventory if m['method'] == name)
            assert not inv['size_capped']
            record = dict(class_name=cls, method=name, asm=asm, inventory=inv, source=str(path.relative_to(ROOT)),
                          calls=direct_calls(asm, by_rva), metadata_loads=metadata_loads(asm, relocations, index))
            records.append(record)
            methods[cls, name] = record
    def has(cls, name, *parts):
        return all(p in methods[cls, name]['asm'] for p in parts)
    def strings(cls, name):
        return {r['Value'] for item in methods[cls, name]['metadata_loads'] for r in item['records'] if r['group'] == 'ScriptString'}
    def target(cls, name, address, expected_cls):
        return any(c['target_rva'] == address and c['declaration'] and c['declaration']['class_name'] == expected_cls for c in methods[cls, name]['calls'])
    checks = {
        'typed_wrappers_six_unity_tailcalls': all(target('PlayerPreferences', method, addr, 'PlayerPrefs') for method, addr in [('SetInt','0x277cc10'),('GetInt','0x277cca0'),('SetFloat','0x277cce4'),('GetFloat','0x277cd7c'),('SetString','0x277cdc8'),('GetString','0x277ce58')]),
        'tutorial_key_and_cache': 'TUTORIAL' in strings('GP_Tutorials','get_IndexTutorial') & strings('GP_Tutorials','set_IndexTutorial') and has('GP_Tutorials','get_IndexTutorial','0x14f4ab0: cmn      w8, #1','0x14f4b10: mov      w1, wzr'),
        'tutorial_getter_repairs_zero_after_target2': has('GP_Tutorials','get_IndexTutorial','0x14f4bac: cmp      w0, #2','0x14f4bb0: b.lt     #0x14f4c20','0x14f4bd0: cbnz     w9, #0x14f4c20','0x14f4be8: mov      w9, #6','0x14f4c1c: bl       #0x13f1a04'),
        'tutorial_cache_reset_not_delete': has('GP_Tutorials','RefreshDatas','0x14f9f74: mov      w9, #-1','0x14f9f78: str      w9, [x8, #0x10]') and not target('GP_Tutorials','RefreshDatas','0x13f1b44','PlayerPreferences'),
        'touch_flag_int_exact_one_not_truthy': 'TUT_TOUCH_SKILL' in strings('GP_Tutorials','IsTutTouchSkillDone') and has('GP_Tutorials','IsTutTouchSkillDone','0x14fa808: mov      w1, wzr','0x14fa818: cmp      w0, #1','0x14fa81c: cset     w0, eq'),
        'touch_completion_and_bypass_write_one': 'TUT_TOUCH_SKILL' in strings('GP_Tutorials.__c__DisplayClass39_0','<CheckRunTutorialNew>b__1') and has('GP_Tutorials.__c__DisplayClass39_0','<CheckRunTutorialNew>b__1','0x14fb958: mov      w1, #1','0x14fb960: bl       #0x13f1a04') and has('GP_Tutorials','CheckRunTutorialNew','0x14fa490: mov      w1, #1','0x14fa4a0: b        #0x13f1a04'),
        'touch_callback_increment_has_two_guards': has('GP_Tutorials.__c__DisplayClass39_0','<CheckRunTutorialNew>b__1','0x14fb978: cmp      w0, #2','0x14fb97c: b.ne     #0x14fb9c8','0x14fb9a0: ldr      w8, [x8, #0x24]','0x14fb9a4: cmp      w8, #2','0x14fb9a8: b.ne     #0x14fb9c8','0x14fb9c0: add      w0, w0, #1','0x14fb9c4: bl       #0x14f9f84'),
        'delete_key_only_unity_tailcall': target('PlayerPreferences','DeleteKey','0x277cf08','PlayerPrefs'),
        'stage_target_and_zone_default_zero_normal': 'StageTarget' in strings('Stage_Datas','get_StageTarget') and 'ZoneUnlocked' in strings('Stage_Datas','get_ZoneUnlocked') and has('Stage_Datas','get_StageTarget','0x12b2054: mov      w1, wzr') and has('Stage_Datas','get_ZoneUnlocked','0x12b925c: mov      w1, wzr'),
        'company_test_defaults_are_separate': all('Test' in strings(cls,name) for cls,name in [('GP_Tutorials','get_IndexTutorial'),('Stage_Datas','get_StageTarget'),('Stage_Datas','get_ZoneUnlocked'),('GameDatas','get_StarCount')]),
        'stage_read_has_one_step_write_not_clamp_to_zone': has('Stage_Datas','get_StageTarget','0x12b20f4: ldr      w10, [x9, #8]','0x12b20fc: b.ge     #0x12b2154','0x12b2124: cmp      w19, w8, lsl #1','0x12b2128: b.ge     #0x12b2154','0x12b2148: add      w0, w9, #1','0x12b2150: bl       #0x12bac5c'),
        'stage_setter_upper_bound_only': has('Stage_Datas','set_StageTarget','0x12baccc: ldr      w9, [x8, #4]','0x12bacd0: cmp      w9, w19','0x12bacd4: csel     w19, w19, w9, gt','0x12bad04: b        #0x13f1a04'),
        'zone_setter_no_extra_clamp': has('Stage_Datas','set_ZoneUnlocked','0x12bac2c: str      w19, [x8, #0x40]','0x12bac58: b        #0x13f1a04'),
        'stage_cache_refresh_resets_two_ints': has('Stage_Datas','RefreshDatas','0x12c502c: movi     v0.2d, #0xffffffffffffffff','0x12c5030: stur     d0, [x8, #0x3c]'),
        'stars_key_prefix_and_separator': {'StarStageMaster','_'} <= strings('Stage_Datas','GetStarStageMaster') & strings('Stage_Datas','SetStarStageMaster') and has('Stage_Datas','GetStarStageMaster','0x12b786c: stp      w1, w0, [sp, #8]','0x12b78c0: add      x0, sp, #0xc','0x12b78d0: add      x0, sp, #8','0x12b7914: mov      w1, wzr'),
        'star_count_key_default_and_cache': 'StarCount' in strings('GameDatas','get_StarCount') & strings('GameDatas','set_StarCount') and has('GameDatas','get_StarCount','0x1325658: mov      w1, wzr','0x13256c4: str      w19, [x9, #0x4c]'),
        'drone_used_key_slot_and_negative_repair': 'DroneUsed' in strings('Drone_Saved_Datas','GetDroneUsed') & strings('Drone_Saved_Datas','SetDroneUsed') and has('Drone_Saved_Datas','GetDroneUsed','0x14dac5c: mov      w1, wzr','0x14dac68: tbz      w0, #0x1f, #0x14dacb4','0x14daca8: mov      w1, wzr','0x14dacb0: bl       #0x13f1a04','0x14dacf8: bl       #0x13f1a1c'),
        'drone_first_id_autowrites_unlock': 'DroneUnlocked' in strings('Drone_Saved_Datas','IsDroneUnlocked') and has('Drone_Saved_Datas','IsDroneUnlocked','0x14d9b6c: mov      w8, #0x4e21','0x14d9bd0: cbnz     w0, #0x14d9c1c','0x14d9c0c: mov      w1, #1','0x14d9c18: bl       #0x13f1a04','0x14d9c20: mov      w8, #0x4e22','0x14d9c28: b.lt     #0x14d9c90','0x14d9c84: cmp      w0, #1'),
        'custom_path_persistent_directory_suffix': '/Prefs' in strings('PlayerPreferences','get_path') and target('PlayerPreferences','get_path','0x275cb1c','Application'),
        'custom_raw_serializes_dictionary_field': 'Dictionary<string, object> dictionary; // 0x0' in declarations['PlayerPreferences'] and has('PlayerPreferences','GetRawData','0x13f1b98: ldr      x0, [x8]') and target('PlayerPreferences','GetRawData','0x13ebc6c','JsonParse'),
        'custom_save_encodes_ascii_and_writes_file': target('PlayerPreferences','SaveToDisk','0x13f1b4c','PlayerPreferences') and target('PlayerPreferences','SaveToDisk','0x20058fc','Encoding') and target('PlayerPreferences','SaveToDisk','0x2077620','File'),
        'custom_load_exists_reads_and_sets_dictionary': target('PlayerPreferences','LoadFromDisk','0x20718b0','File') and target('PlayerPreferences','LoadFromDisk','0x2076f28','File') and has('PlayerPreferences','LoadFromDisk','0x13f1810: str      x19, [x8]'),
        'focus_quit_trigger_custom_save': has('PlayerPreferences','OnApplicationFocus','0x13f1cd0: b        #0x13f1ab8') and has('PlayerPreferences','OnApplicationQuit','0x13f1c84: b        #0x13f1ab8'),
        'deleteall_clears_unity_and_dictionary': target('PlayerPreferences','DeleteAll','0x277cf44','PlayerPrefs') and has('PlayerPreferences','DeleteAll','0x13f1aa4: bl       #0x1960960','0x13f1ab0: b        #0x13f1ab8'),
        'no_unity_save_call_in_selected_wrapper_lifecycle': all(not (c['declaration'] and c['declaration']['class_name']=='PlayerPrefs' and ' Save(' in c['declaration']['signature']) for n in ('SaveToDisk','OnApplicationFocus','OnApplicationQuit') for c in methods['PlayerPreferences',n]['calls']),
    }
    assert all(checks.values()), checks
    contracts = []
    def add(key_format, owner, read, write, cache, effects, key_parts):
        refs = [f'{owner}.{read}'] + [f'{owner}.{m}' for m in write]
        contracts.append(dict(key_format=key_format, value_type='int32', store='Unity.PlayerPrefs',
                              backend_GetInt_default_normal_company_not_Test=0, reader_return_type='bool' if read in ('IsTutTouchSkillDone','IsDroneUnlocked') else 'int32', owner=owner, reader=read, writers=write,
                              reader_method_id=f'{owner}.{read}', writer_method_ids=[f'{owner}.{m}' for m in write],
                              cache=cache, read_effects=effects, key_parameters=key_parts,
                              evidence_method_ids=refs))
    add('TUTORIAL','GP_Tutorials','get_IndexTutorial',['set_IndexTutorial','get_IndexTutorial'], 'static indexTut+0x10, sentinel -1', ['loads cached value; reads StageTarget', 'if StageTarget>=2 and cached tutorial==0: cache and write 6'], [])
    add('TUT_TOUCH_SKILL','GP_Tutorials','IsTutTouchSkillDone',['CheckRunTutorialNew'], 'none in predicate', ['returns value==1, not value!=0; callback b__1 also writes 1', 'callback increments IndexTutorial only if IndexTutorial==2 and StageCurrent==2; flag write itself is before those guards'], [])
    add('StageTarget','Stage_Datas','get_StageTarget',['set_StageTarget','get_StageTarget'], 'static stageTarget+0x3c, sentinel -1', ['if ZoneUnlocked<MAX_ZONE_INDEX and target<ZoneUnlocked*10: increment once and persist through capped setter'], [])
    add('ZoneUnlocked','Stage_Datas','get_ZoneUnlocked',['set_ZoneUnlocked'], 'static zoneUnlock+0x40, sentinel -1', [], [])
    add('StarStageMaster{stage}_{mode}','Stage_Datas','GetStarStageMaster',['SetStarStageMaster'], 'none in these methods', [], ['stage: internal stageIndex int32','mode: modeIndex int32'])
    add('StarCount','GameDatas','get_StarCount',['set_StarCount'], 'static starCount+0x4c, sentinel -1', [], [])
    add('DroneUsed{slot}','Drone_Saved_Datas','GetDroneUsed',['SetDroneUsed','GetDroneUsed'], 'none in these methods', ['stored<0 writes 0 then rereads; missing0 does not autoequip 20001'], ['slot: slotIndex int32, not drone ID'])
    add('DroneUnlocked{drone}','Drone_Saved_Datas','IsDroneUnlocked',['SetDroneUnlocked','IsDroneUnlocked'], 'none in these methods', ['normal branch: ID20001 writes1 if stored0 then returns true', 'ID<20002 returns true (no valid roster inference)', 'ID>=20002 returns stored==1'], ['drone: index/id int32, not slot'])
    callback_id = 'GP_Tutorials.__c__DisplayClass39_0.<CheckRunTutorialNew>b__1'
    contracts[1]['evidence_method_ids'].append(callback_id)
    contracts[1]['writer_method_ids'].append(callback_id)
    return dict(schema_version=1, status='PROVISIONAL_STATIC_PARTIAL_SAVE_CONTRACT_NOT_FULL_SCHEMA', scope='Opening campaign persistence; company!=Test defaults; getters may mutate; no runtime durability/migration proof.',
                checks=checks, methods=records, sources=sources,
                declarations={cls: text.split('// Properties')[0] for cls,text in declarations.items() if cls in SELECT},
                contracts=contracts,
                stores=[dict(id='Unity.PlayerPrefs', access='typed wrappers tailcall Unity; GameDatas star count calls Unity directly', flush='not established by selected custom SaveToDisk/lifecycle bodies'),
                        dict(id='PlayerPreferences.dictionary', access='SetValue/GetValue use static dictionary+0x0', file='Application.persistentDataPath + /Prefs', save='GetRawData -> JsonParse.ToJson(dictionary) -> Encrypt -> ASCII bytes -> File.WriteAllBytes', load='File.Exists/ReadAllBytes -> ASCII decode -> Decrypt -> deserialize dictionary; missing file initializes empty dictionary')],
                limitations=['Not a complete save schema, no cloud/IAP/Premium analysis.', 'No automatic lower-bound validation inferred from capped StageTarget setter.', 'Getters can change persistent progress; read order matters.', 'Key formatting derived from native Concat/int ToString; parameters in bounded ordinary range.', 'No native-wide absence proof of PlayerPrefs.Save; only three named wrapper/lifecycle bodies checked.', 'DeleteKey only targets Unity; DeleteAll clears Unity+dictionary but selected body does not invalidate other class caches.', 'No custom encryption security claim, crash safety, migration, or atomic disk-write guarantee.'])


def main():
    data = build()
    folder = RAW / 'persistence'; folder.mkdir(exist_ok=True)
    evidence = folder / 'opening-contracts.json.gz'
    evidence.write_bytes(gzip.compress(json.dumps(data, ensure_ascii=False, indent=2).encode(), mtime=0))
    out = dict(schema_version=data['schema_version'], status=data['status'], scope=data['scope'],
               raw_evidence=str(evidence.relative_to(ROOT)), raw_evidence_sha256_decompressed=hashlib.sha256(gzip.decompress(evidence.read_bytes())).hexdigest(),
               contracts=data['contracts'], stores=data['stores'], limitations=data['limitations'])
    (ROOT / 'datas/opening_persistence.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(len(data['methods']), 'methods;', len(data['checks']), 'checks;', len(data['contracts']), 'key families')


if __name__ == '__main__':
    main()
