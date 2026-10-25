#!/usr/bin/env python3
"""Pin peer review inputs without checkout or writes to the peer branch."""
import ast
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
from early_ui_native import section
ROOT=Path(__file__).resolve().parents[2]
PEER='25c367aca99f06f14df546d2f30e60b427827157'
PATHS=['docs/spec/MISSIONS_STARS.md','docs/spec/ENCOUNTERS.md',
       'docs/spec/DESIGN_READINESS.md','docs/spec/ASSET_TRIAGE.md',
       'docs/spec/DATA_SYNC.md','tools/classify-assets.py','tools/verify-claims.py',
       'docs/assets/sprites-index.csv','docs/assets/sprites-classified.csv']


def build():
    snapshots={}
    for p in PATHS:
        blob=subprocess.check_output(['git','show',f'{PEER}:{p}'],cwd=ROOT)
        snapshots[p]={'sha256':hashlib.sha256(blob).hexdigest(),'text':blob.decode()}
    code=snapshots['tools/classify-assets.py']['text'];tree=ast.parse(code)
    rules=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='RULES' for t in n.targets))
    def classify_no_eye(name):
        return next(({'category':cat,'rule':rule,'confidence':level} for pattern,cat,rule,level in rules if re.search(pattern,name)),None)
    rows=list(csv.DictReader(io.StringIO(snapshots['docs/assets/sprites-classified.csv']['text'])))
    retained=[r for r in rows if r['category']!='unclassified']
    asm=ROOT/'reverse-engineering/raw/il2cpp-consts/Player_Get_Datas.asm.txt'
    arrays=ROOT/'reverse-engineering/raw/ui-audit/enemy-exit-missions.json.gz'
    a=json.load(gzip.open(arrays,'rt'))['normal_mission_arrays']
    return {'status':'PROVISIONAL peer review, not a full branch audit',
            'peer_commit':PEER,'data_snapshot':'61fce8ae7','snapshots':snapshots,
            'experiments':{'Coda_A_no_eye':classify_no_eye('Coda_A'),
                           'XVideo_no_eye':classify_no_eye('XVideo'),
                           'Coda_rows_in_output':[{k:r[k] for k in ('name','proposed_category','confidence','rule')} for r in rows if r['name'].startswith('Coda_')],
                           'retained_original_count':len(retained),
                           'retained_original_confidences':sorted(set(r['confidence'] for r in retained))},
            'native_evidence':{'source':str(asm.relative_to(ROOT)),'sha256':hashlib.sha256(asm.read_bytes()).hexdigest(),
                               'GetKillPercentMissionComplete':section(asm.read_text(),'GetKillPercentMissionComplete'),
                               'resolved_normal_arrays':a},
            'review_findings':['P0 mission-mode fallback wrong and resolved arrays still marked missing',
                               'P0 wave name dedup/divide2 is not serialized-resource identity',
                               'P1 atlas string matching cannot prove no extracted sprites',
                               'P1 classifier shadowed rules and unconditional inherited confidenceA',
                               'P1 readiness D3 both partial and closed',
                               'P1 verifier exceptions become SKIP and do not fail acceptance'],
            'limitations':['review pinned snapshot only; peer may advance',
                           'did not inspect every image or every claim',
                           'did not merge or modify peer branch',
                           'classification experiment is no-eye rule path; actual CSV checked separately']}


if __name__=='__main__':
    d=build();p=ROOT/'reverse-engineering/raw/peer-review/spec-25c367aca.json.gz';p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(gzip.compress(json.dumps(d,ensure_ascii=False,indent=2).encode(),mtime=0))
    print(d['peer_commit'],len(d['snapshots']),'pinned files',d['experiments'])
