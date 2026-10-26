#!/usr/bin/env python3
"""Preserve/check APK callback consumer, equipment and Continue control flow."""
import gzip
import hashlib
import json
import re
from pathlib import Path
from early_ui_native import section
from ui_loader_analysis import metadata_loads
from ui_routing import direct_calls

ROOT = Path(__file__).resolve().parents[2]
SELECT = {
    'GP_Manager': ['Start', 'GameStarted', 'OnThroughTut'],
    'GP_Loader': ['StartDrones'],
    'GP_Spawner': ['SpawnEnemies'],
    'GP_Endgame': ['VictoryNow', 'OpenBoardVictory', 'OpenEndgame'],
    'Drone_Saved_Datas': ['GetDroneUsed', 'SetDroneUsed', 'SetDroneUnlocked'],
    'Board_Talents': ['get_GetTalentIndex', 'set_GetTalentIndex'],
    'Board_Endgame': ['Continue', 'LoadToLoading'],
    'GP_Setup': ['get_indexDrones'],
    'GP_Tutorials._TutDrones_d__48': ['MoveNext'],
}


def decode_manager_dispatch(bytes_hex, base):
    data = bytes.fromhex(bytes_hex)
    if len(data) != 10:
        raise ValueError('Expected ten entries for eventState -1 through 8')
    return [{'event_state': i-1, 'target': hex(base+4*b)} for i, b in enumerate(data)]


def main():
    audit = ROOT/'reverse-engineering/raw/ui-audit'
    dump = gzip.open(ROOT/'reverse-engineering/il2cpp/dump.cs.gz', 'rt').read()
    rv, decl, index = {}, {}, {}
    for b in re.split(r'(?=// Namespace:)', dump):
        c = re.search(r'(?:class|enum) ([^ :\n]+)', b)
        if not c:
            continue
        decl[c[1]] = b
        for m in re.finditer(r'// RVA: (0x[\dA-Fa-f]+)[^\n]*\n([^\n]+)', b):
            rv[int(m[1], 16)] = {'class': c[1], 'signature': m[2].strip()}
    meta = json.load(gzip.open(audit/'metadata-index.json.gz', 'rt'))
    rel = json.load(gzip.open(audit/'native-relocations.json.gz', 'rt'))
    for group, rows in meta['tables'].items():
        for row in rows:
            index.setdefault(row['Address'], []).append(dict(row, group=group))
    records, methods = [], {}
    for cls, names in SELECT.items():
        folder = ROOT/'reverse-engineering/raw/il2cpp-consts' if cls == 'Board_Endgame' or cls.startswith('GP_Tutorials.') else audit/'extra-native'
        p = folder/f'{cls}.asm.txt'
        inventory = json.loads((folder/f'{cls}.json').read_text())
        for name in names:
            asm = section(p.read_text(), name)
            inv = next(m for m in inventory['methods'] if m['method'] == name)
            assert not inv.get('size_capped'), (cls, name)
            methods[cls, name] = asm
            records.append({'class': cls, 'method': name, 'asm': asm,
                'source': str(p.relative_to(ROOT)), 'source_sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                'export_inventory': inv, 'calls': direct_calls(asm, rv),
                'metadata_loads': metadata_loads(asm, rel['relocations'], index)})
    ro = json.loads((audit/'stage23-rodata.json').read_text())
    assert ro['native_sha256'] == rel['native_sha256']
    table = ro['manager_dispatch']
    assert decode_manager_dispatch(table['bytes_hex'], int(table['branch_base'], 16)) == table['entries']
    expected = ['0x14f482c','0x14f48d0','0x14f48b8','0x14f4920','0x14f4930',
                '0x14f4980','0x14f49a0','0x14f49b8','0x14f4968','0x14f49fc']
    assert [r['target'] for r in table['entries']] == expected
    consumer = methods['GP_Manager', 'OnThroughTut']
    cont = methods['Board_Endgame', 'Continue']
    load = methods['Board_Endgame', 'LoadToLoading']
    used = methods['Drone_Saved_Datas', 'SetDroneUsed']
    assert any(r.get('MethodAddress') == 0x14f47cc for r in index[int(rel['relocations']['0x2ae8fb8'],16)])
    checks = {
        'signed_callback_range_minus_one_through_eight': all(s in consumer for s in
            ('add      w8, w20, #1', 'cmp      w8, #9', 'b.hi     #0x14f49f0')),
        'drone_overlay_emits_state4': '0x14fc69c: mov      w1, #4' in methods['GP_Tutorials._TutDrones_d__48','MoveNext'],
        'state8_starts_drones': all(s in consumer for s in
            ('0x14f49fc: ldr      x0, [x19, #0x30]', '0x14f4a0c: b        #0x14f2864')),
        'state5_hides_skill_buttons': '0x14f49b4: b        #0x14d54c0' in consumer,
        'state7_shows_skill_buttons': '0x14f497c: b        #0x14d6004' in consumer,
        'startup_rejoins_after_veneer': ro['game_started_veneer']['instructions'][:2] == [
            {'address':'0x2990898','mnemonic':'ldr','op_str':'x22, [x22, #0xfb8]'},
            {'address':'0x299089c','mnemonic':'b','op_str':'#0x14f4008'}],
        'continue_conditional_empty_slot_equips_20001': all(s in cont for s in
            ('0x126f270: cmp      w0, #1','0x126f280: bl       #0x14dabd4',
             '0x126f284: cbnz     w0, #0x126f294','mov      w1, #0x4e21',
             '0x126f290: bl       #0x14db228','0x126f298: bl       #0x126f3c8')),
        'equipment_setter_writes_pref_not_unlock': '#0x13f1a04' in used and '#0x14db13c' not in used,
        'continue_min_target_current_plus_one_branch': all(s in cont for s in
            ('add      w10, w9, #1','cmp      w0, w10','csinc    w9, w0, w9, lt','str      w9, [x8, #0x24]')),
        'load_to_loading_direct_scene_is_game': all(s in load for s in
            ('mov      w0, #2','0x126f528: b        #0x141b488')) and 'Scene Game = 2' in decl['ScenesManager.Scene'],
        'talent_default_minus_one': 'mov      w1, #-1' in methods['Board_Talents','get_GetTalentIndex'],
    }
    assert all(checks.values()), checks
    out = {'status':'PROVISIONAL — static APK evidence, not runtime replay',
        'native_sha256':rel['native_sha256'], 'dump_uncompressed_sha256':hashlib.sha256(dump.encode()).hexdigest(),
        'checks':checks, 'rodata':ro, 'methods':records,
        'declarations':{c:decl[c] for c in (*[c for c in SELECT if not c.startswith('GP_Tutorials.')], 'GP_Tutorials.<TutDrones>d__48', 'GP_Display','GP_Datas','GP_Controller','Stage_Datas','ScenesManager.Scene')},
        'startup_callback_slot':{'slot':'0x2ae8fb8','effective_address':rel['relocations']['0x2ae8fb8'],
            'records':index[int(rel['relocations']['0x2ae8fb8'],16)]},
        'warning':'Metadata scanner is conservative; omissions are not proof of no reference. No ownership grant or unconditional next-stage claim.'}
    with gzip.open(audit/'tutorial-consumer-flow.json.gz','wt') as f:
        json.dump(out,f,ensure_ascii=False,indent=2)
    print(json.dumps(checks,indent=2));print('preserved methods:',len(records))


if __name__ == '__main__':
    main()
