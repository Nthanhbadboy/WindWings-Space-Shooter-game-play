"""Hermetic review of pinned peer onboarding, not execution of peer tooling."""
import ast
import gzip
import hashlib
import json
from pathlib import Path
import re
from early_ui_native import section

ROOT = Path(__file__).resolve().parents[2]
PEER = 'cf27b97553ef25107b45b039f316d9ca7850a885'
SNAPSHOT = ROOT / 'reverse-engineering/raw/peer-review/spec-cf27b9755.json.gz'
EVIDENCE = {
    'reverse-engineering/raw/il2cpp-consts/Player_Get_Datas.asm.txt': ['GetMainCannonDamage', 'GetMainCannonRate', 'GetWingCannonDamage'],
    'reverse-engineering/raw/ui-audit/scene-map-flow.json.gz': None,
    'reverse-engineering/raw/endgame-missions/mission-progress-flow.json.gz': None,
    'reverse-engineering/raw/endgame-missions/shared-stage-victory.json.gz': None,
    'reverse-engineering/raw/sprite-geometry/index.json': None,
}


def build():
    pinned = json.load(gzip.open(SNAPSHOT, 'rt'))
    assert hashlib.sha256(gzip.decompress(SNAPSHOT.read_bytes())).hexdigest() == '24c20c21fbef3e2a51baab477f51367ee8ea78662597f39075d85dd5ae14a999'
    assert pinned['peer_commit'] == PEER
    for value in pinned['snapshots'].values():
        assert hashlib.sha256(value['text'].encode()).hexdigest() == value['sha256']
    docs = {p: x['text'] for p, x in pinned['snapshots'].items()}
    tree = ast.parse(docs['tools/classify-assets.py'])
    rules = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'RULES' for t in n.targets))
    def classify(name):
        return next((dict(category=c, rule=r, confidence=v) for pattern, c, r, v in rules if re.search(pattern, name)), None)
    evidence = []
    for path, methods in EVIDENCE.items():
        data = (ROOT / path).read_bytes()
        if path.endswith('.gz'):
            data = gzip.decompress(data)
        text = data.decode()
        evidence.append(dict(path=path, sha256_decompressed=hashlib.sha256(data).hexdigest(),
                             content={m: section(text, m) for m in methods} if methods else json.loads(text)))
    player = evidence[0]['content']['GetMainCannonDamage']
    checks = dict(
        preserved_fifteen_peer_inputs=len(docs) == 15,
        classifier_coda_now_font=classify('Coda_A')['category'] == 'font',
        classifier_xvideo_ui=classify('XVideo')['category'] == 'ui',
        errors_no_longer_silently_skip='c.status, c.why = "ERROR"' in docs['tools/verify-claims.py'],
        required_and_empty_selection_guards_present='if not selected:' in docs['tools/verify-claims.py'] and 'if unknown:' in docs['tools/verify-claims.py'],
        peer_corrected_normal_percent_table='0.20/0.45/0.80' in docs['docs/spec/MISSIONS_STARS.md'],
        player_index_retained='0x14e396c: mov      w19, w0' in player,
        player_index_addresses_base_array=all(s in player for s in ('0x14e3a78: ldr      x8, [x8, #0x78]', '0x14e3a84: cmp      w9, w19', '0x14e3a8c: add      x8, x8, w19, sxtw #2', '0x14e3a90: ldr      s8, [x8, #0x20]')),
        stale_map_blocker_still_present='bytes** của 576 blob' in docs['docs/spec/MISSING_FOR_NEW_GAME.md'],
        unsupported_ship_inference_still_present='tàu **không** có HP/damage riêng' in docs['docs/spec/MISSING_FOR_NEW_GAME.md'],
        aesthetic_pass_claim_still_present='đạt 4 khoảng' in docs['docs/spec/START_HERE.md'],
        preview_metrics_not_original_pixels='42 contact sheet' in docs['docs/spec/ART_STUDY.md'],
        all_build_absence_overclaim_still_present='không tồn tại trong build' in docs['docs/spec/MISSING_FOR_NEW_GAME.md'],
        known_map_consumer_checks=all(evidence[1]['content']['checks'].values()),
        known_save_flow_checks=all(evidence[2]['content']['checks'].values()),
        known_shared_victory_checks=all(evidence[3]['content']['checks'].values()),
    )
    return dict(status='PROVISIONAL_PINNED_HANDOFF_REVIEW_NOT_FULL_PEER_AUDIT', peer_commit=PEER,
                peer_inputs_sha256=hashlib.sha256(gzip.decompress(SNAPSHOT.read_bytes())).hexdigest(),
                evidence=evidence, checks=checks, classifier_no_eye={'Coda_A': classify('Coda_A'), 'XVideo': classify('XVideo')},
                limitations=['Peer tools/tests not executed; code fixes checked statically only.',
                             'Checks that detect bad prose are findings, not endorsements.',
                             'Player-indexed lookup does not alone establish unequal values or runtime HP for every ship.',
                             'Source joins and counts do not prove image crop correctness, aesthetic quality, or runtime replay.'])


if __name__ == '__main__':
    result = build()
    assert all(result['checks'].values()), result['checks']
    target = ROOT / 'reverse-engineering/raw/peer-review/handoff-cf27b9755.json.gz'
    target.write_bytes(gzip.compress(json.dumps(result, ensure_ascii=False, indent=2).encode(), mtime=0))
    print(PEER, len(result['checks']), 'review checks')
