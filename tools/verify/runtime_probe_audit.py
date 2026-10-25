#!/usr/bin/env python3
"""Separate CI readiness from game evidence; derive watchpoints from the APK dump."""
import gzip
import hashlib
import json
import re
from pathlib import Path
from early_ui_native import section
from ui_routing import direct_calls
from ui_loader_analysis import metadata_loads

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'reverse-engineering/raw/runtime-probe'
WATCH={
    'Stage_Datas': ['StageCurrent','ModeCurrent','StageBranchCurrent','IsContinue','IsReplay','stageTarget','zoneUnlock'],
    'GP_Tutorials': ['inTutorial','indexTut'],
    'Board_Endgame': ['victory','stageIndex','stageMode'],
    'Home_Loader': ['defaultBoard','isBackFromEndgame'],
}
HOOKS={
    'GP_Tutorials': ['set_IndexTutorial','GameStarted'],
    'Board_Endgame': ['OnPressedButtonContinue','Continue','<CheckPremiumPopup>g__ThroughTut|91_2'],
    'Home_Loader': ['CheckSpecPopup'],
    'Home_Loader.<>c': ['<CheckSpecPopup>b__13_0','<CheckSpecPopup>b__13_1'],
    'BoardManager': ['OpenBoard','GetAndOpenBoardSingle','GetAndOpenBoardAdditive','GetAndOpenBoardPopUp'],
    'PlayerPrefs': ['Save'],
}


def classify_jobs(jobs):
    device=next((j for j in jobs if j['name']=='ramus device probe'),None)
    steps={s['name']:s for s in (device or {}).get('steps',[])}
    probe=steps.get('Probe game state',{})
    session=steps.get('Start session',{})
    return {'device_job_conclusion':(device or {}).get('conclusion'),
            'session_step':session.get('conclusion','missing'),
            'probe_step':probe.get('conclusion','missing'),
            'classification':'payload_review_required' if probe.get('conclusion')=='success' else 'no_successful_game_state_probe',
            'warning':'CI success is not acceptance of runtime evidence; payload, APK identity and transport must be reviewed separately'}


def watchpoints(dump):
    fields=[];methods=[];declarations={}
    for block in re.split(r'(?=// Namespace:)',dump):
        match=re.search(r'\bclass ([^ :\n]+)',block)
        if not match:continue
        cls=match[1]
        if cls not in WATCH and cls not in HOOKS:continue
        # Keep full original declaration block so signature/namespace/offset are auditable.
        declarations[cls]=block
        for name in WATCH.get(cls,[]):
            m=re.search(r'(?m)^\s*(?:public|private|protected|internal) static ([\w.<>\[\]]+) '+re.escape(name)+r'; // (0x[\dA-Fa-f]+)',block)
            if not m:raise ValueError(f'Watch field missing in authoritative dump: {cls}.{name}')
            fields.append({'class':cls,'field':name,'type':m[1],'static_offset':m[2],
                           'capture':'native field read, not arbitrary managed property evaluation'})
        for name in HOOKS.get(cls,[]):
            pattern=r'// RVA: (0x[\dA-Fa-f]+)[^\n]*\n([^\n]*\s'+re.escape(name)+r'\([^\n]*)'
            m=re.search(pattern,block)
            if not m:raise ValueError(f'Hook missing in authoritative dump: {cls}.{name}')
            methods.append({'class':cls,'method':name,'rva':m[1],'declaration':m[2].strip(),
                            'capture':'observe entry/exit and relevant values; never invoke or replace method'})
    assert len(fields)==sum(map(len,WATCH.values()))
    assert len(methods)==sum(map(len,HOOKS.values()))
    return {'fields':fields,'methods':methods,'declarations':declarations}


def main():
    run_dir=BASE/'40181812673'
    run=json.loads((run_dir/'ci-run.json').read_text())
    jobs=json.loads((run_dir/'ci-jobs.json').read_text())
    sources=[]
    for p in [ROOT/'runtime-probe/RamusBridge.cs',ROOT/'runtime-probe/Adapters/BepInEx6/BepInEx6Plugin.cs',
              ROOT/'runtime-probe/Adapters/MelonLoader/MelonPlugin.cs',ROOT/'.github/scripts/build-bridge.sh']:
        sources.append({'source':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                        'text':p.read_text()})
    out={'status':'PROVISIONAL','source_run':run,'ci_assessment':classify_jobs(jobs),
         'accepted_primary_apk_gameplay_payloads':0,'local_bridge_source_snapshots':sources,
         'remote_bridge_source_snapshots':json.load(gzip.open(BASE/'other-branch-code.json.gz','rt')),
         'not_game_evidence':'CI and toolchain source establish readiness gaps only, not gameplay values'}
    (BASE/'readiness-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    p=ROOT/'reverse-engineering/il2cpp/dump.cs.gz'
    dump=gzip.open(p,'rt').read()
    watch=watchpoints(dump)
    watch.update({'status':'PROVISIONAL — capture plan, NOT observed runtime',
                  'source':str(p.relative_to(ROOT)),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                  'warning':'Match exact APK/native hashes before using RVAs. No property getters, class initialization or Save calls may be invoked to collect evidence.'})
    with gzip.open(BASE/'stage1-3-watchpoints.json.gz','wt') as f:json.dump(watch,f,ensure_ascii=False,indent=2)
    print(json.dumps(out['ci_assessment'],indent=2))
    print('APK watchpoints:',len(watch['fields']),'fields;',len(watch['methods']),'method entries')
    # Prove observer-effect risk from the authoritative APK, not from phone/mod values.
    asm_path=ROOT/'reverse-engineering/raw/il2cpp-consts/GP_Tutorials.asm.txt'
    asm=section(asm_path.read_text(),'get_IndexTutorial')
    by_rva={}
    for block in re.split(r'(?=// Namespace:)',dump):
        cls=re.search(r'(?:class|enum) ([^ :\n]+)',block)
        if not cls:continue
        for m in re.finditer(r'// RVA: (0x[\dA-Fa-f]+)[^\n]*\n([^\n]+)',block):
            by_rva[int(m[1],16)]={'class':cls[1],'signature':m[2].strip()}
    audit=ROOT/'reverse-engineering/raw/ui-audit'
    meta=json.load(gzip.open(audit/'metadata-index.json.gz','rt'))
    reloc=json.load(gzip.open(audit/'native-relocations.json.gz','rt'))
    index={}
    for group,rows in meta['tables'].items():
        for row in rows:index.setdefault(row['Address'],[]).append(dict(row,group=group))
    checks={
        'calls_stage_target_getter':'#0x12b1f68' in asm,
        'stage_target_guard':'cmp      w0, #2' in asm and 'b.lt     #0x14f4c20' in asm,
        'cached_index_zero_guard':'cbnz     w9, #0x14f4c20' in asm,
        'stores_cached_six':'mov      w9, #6' in asm and 'str      w9, [x8, #0x10]' in asm,
        'calls_int_setter_with_six':'mov      w1, #6' in asm and '#0x13f1a04' in asm,
    }
    assert all(checks.values()),checks
    loads=metadata_loads(asm,reloc['relocations'],index)
    assert any(r.get('Value')=='TUTORIAL' for load in loads for r in load['records'])
    evidence={'status':'PROVISIONAL — static observer-effect path, not a recorded probe execution',
              'source':str(asm_path.relative_to(ROOT)),'sha256':hashlib.sha256(asm_path.read_bytes()).hexdigest(),
              'asm':asm,'checks':checks,'calls':direct_calls(asm,by_rva),
              'metadata_loads':loads,
              'native_sha256':reloc['native_sha256'],
              'finding':'get_IndexTutorial may write cached index and PlayerPrefs TUTORIAL=6 when StageTarget>=2 and cached index==0. Do not evaluate this property as a passive measurement.'}
    with gzip.open(BASE/'getter-observer-effect.json.gz','wt') as f:json.dump(evidence,f,ensure_ascii=False,indent=2)
    print('Getter observer-effect checks:',checks)


if __name__=='__main__':main()
