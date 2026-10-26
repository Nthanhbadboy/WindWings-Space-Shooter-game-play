"""Check introductory tutorial gates separately from the shared campaign result path."""
import gzip
import hashlib
import json
from pathlib import Path
from early_ui_native import section

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'reverse-engineering/raw'
SELECT = {
    'DataTutorials': ('il2cpp-consts', ['get_hasTutStage1', 'get_hasTutStage2', 'get_hasTutStage3']),
    'GP_Tutorials': ('il2cpp-consts', ['GameStarted', 'CheckRunTutorialNew', 'IsTutTouchSkillDone']),
    'GP_Endgame': ('ui-audit/extra-native', ['StartCheckEndgame', 'MoveOutPlayer', 'OpenBoardVictory', 'VictoryNow', '<VictoryNow>b__5_0']),
    'GP_Endgame._CheckEndgame_d__4': ('ui-audit/extra-native', ['MoveNext']),
    'GP_Endgame.__c__DisplayClass4_0': ('ui-audit/extra-native', ['<CheckEndgame>b__0']),
    'Board_Endgame': ('il2cpp-consts', ['Init', 'GetMissionCompleted', 'SetMissions', 'SetupTut', '_2', 'Continue']),
    'GP_Manager': ('ui-audit/extra-native', ['<Start>b__11_7']),
    'GP_Setup': ('ui-audit/extra-native', ['get_stageIndex']),
}


def intro_gate(stage_index, tutorial_index, touch_done):
    """The three DataTutorials predicates, not full tutorial dispatch or replay."""
    return dict(stage1=stage_index == 0 and tutorial_index == 0,
                stage2=stage_index == 1 and tutorial_index == 1,
                stage3=stage_index == 2 and not touch_done)


def build():
    methods, records, sources = {}, [], []
    for cls, (folder, names) in SELECT.items():
        path = RAW / folder / (cls + '.asm.txt')
        inv_path = RAW / folder / (cls + '.json')
        inventory = json.loads(inv_path.read_text())['methods']
        for p in (path, inv_path):
            sources.append(dict(path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
        for name in names:
            asm = section(path.read_text(), name)
            inv = next(m for m in inventory if m['method'] == name)
            assert not inv['size_capped']
            methods[cls, name] = asm
            records.append(dict(class_name=cls, method=name, inventory=inv, asm=asm, source=str(path.relative_to(ROOT))))
    def has(cls, name, *parts):
        return all(p in methods[cls, name] for p in parts)
    check_cls = 'GP_Endgame._CheckEndgame_d__4'
    core = [methods[check_cls, 'MoveNext'], methods['GP_Endgame', 'OpenBoardVictory'], methods['Board_Endgame', 'GetMissionCompleted']]
    checks = dict(
        stage1_stage_zero_and_tutorial_zero=has('DataTutorials', 'get_hasTutStage1', '0x1327ec4: bl       #0x14f0da0', '0x1327ec8: cbz      w0, #0x1327ed4', '0x1327ef0: bl       #0x14f4a14', '0x1327ef4: cmp      w0, #0'),
        stage2_index_one_pair=has('DataTutorials', 'get_hasTutStage2', '0x1327f50: cmp      w0, #1', '0x1327f68: bl       #0x14f0da0', '0x1327f6c: cmp      w0, #1'),
        stage3_stage_two_touch_flag=has('DataTutorials', 'get_hasTutStage3', '0x1327fc0: bl       #0x14f0da0', '0x1327fc4: cmp      w0, #2', '#0x14fa7b0') and '#0x14f4a14' not in methods['DataTutorials', 'get_hasTutStage3'],
        tutorial_dispatch_is_ordered=has('GP_Tutorials', 'CheckRunTutorialNew', '0x14fa124: bl       #0x1327e90', '0x14fa1bc: bl       #0x1327f08', '0x14fa26c: bl       #0x1327f8c'),
        stage1_move_and_transform_tutorial=has('GP_Tutorials', 'CheckRunTutorialNew', '0x14fa158: bl       #0x14faa94', '0x14fa19c: fmov     s0, #9.00000000', '0x14fa1b0: bl       #0x14faaf4'),
        common_check_starts_from_manager=has('GP_Manager', '<Start>b__11_7', '0x14f6188: b        #0x14f052c'),
        common_completion_gate=has(check_cls, 'MoveNext', '0x14f151c: cbnz     w8, #0x14f1714', '0x14f1554: cmp      w8, #1', '0x14f1558: b.ne     #0x14f1714'),
        normal_kill_result_calls_shared_scorer=has(check_cls, 'MoveNext', '0x14f1818: ldr      w21, [x8, #0x1c]', '0x14f182c: ldr      w22, [x0, #0x58]', '0x14f1850: bl       #0x12734f8'),
        player_health_zero_overrides_false=has(check_cls, 'MoveNext', '0x14f18e8: blr      x8', '0x14f18ec: fcmp     s0, #0.0', '0x14f18fc: strb     wzr, [x8, #0x10]'),
        same_moveout_after_result=has(check_cls, 'MoveNext', '0x14f170c: bl       #0x14f0768'),
        result_closure_enters_one_openboard=has('GP_Endgame.__c__DisplayClass4_0', '<CheckEndgame>b__0', '0x14f13b8: ldrb     w1, [x0, #0x10]', '0x14f13c4: b        #0x14f0830'),
        shared_snapshot=has('GP_Endgame', 'OpenBoardVictory', '0x14f09e4: strb     w24, [x8]', '0x14f0b20: str      w9, [x8, #0x14]', '0x14f0b38: str      w9, [x8, #0x18]', '0x14f0b50: str      w0, [x8, #0x1c]'),
        board_init_uses_same_missions=has('Board_Endgame', 'Init', '0x126c538: bl       #0x1272714'),
        no_intro_predicate_calls_in_three_core_methods=all(all('#'+r not in asm for r in ('0x1327e90', '0x1327f08', '0x1327f8c', '0x14f4a14')) for asm in core),
        board_tutorial_overlay_has_own_gate=has('Board_Endgame', 'SetupTut', '0x126cb0c: bl       #0x14f4a14', '0x126cb10: cmp      w0, #1', '0x126cb14: b.le     #0x126cb2c'),
        through_tut_changes_buttons_and_index_not_new_scoring=has('Board_Endgame', '_2', '0x126d4f8: bl       #0x2781804', '0x126d51c: bl       #0x2781804', '0x126d538: add      w0, w0, #1', '0x126d540: bl       #0x14f9f84'),
        continue_has_tutorial_routing=has('Board_Endgame', 'Continue', '0x126f240: bl       #0x14f4a14', '0x126f244: cmp      w0, #2', '0x126f248: b.le     #0x126f258', '0x126f298: bl       #0x126f3c8'),
        forced_victory_also_uses_same_board=has('GP_Endgame', '<VictoryNow>b__5_0', '0x14f1318: mov      w1, #1', '0x14f131c: b        #0x14f0830'),
    )
    return dict(status='PROVISIONAL_STATIC_SHARED_CAMPAIGN_FLOW', scope='GameMode0, nonbranch, normal LevelCurrent0; not every game mode or identical tutorial UI',
                sources=sources, methods=records, checks=checks,
                stages=[dict(display=i+1, internal=i, victory_entry='GP_Endgame.OpenBoardVictory', board='Board_Endgame', mission_scorer='Board_Endgame.GetMissionCompleted') for i in range(3)],
                limitation='Absence check is only for direct calls in three named core methods, not a whole-program absence proof; stage-specific tutorial UI and navigation remain.')


if __name__ == '__main__':
    result = build()
    assert all(result['checks'].values()), result['checks']
    path = RAW / 'endgame-missions/shared-stage-victory.json.gz'
    with gzip.GzipFile(filename=str(path), mode='wb', mtime=0) as f:
        f.write(json.dumps(result, ensure_ascii=False, indent=2).encode())
    print(len(result['methods']), 'methods;', len(result['checks']), 'checks')
