#!/usr/bin/env python3
"""Bounded, independent review of the published Gate-1 v4 evidence.

Uses only small committed source snapshots: no APK, peer verifier import, device,
network service, or generated native fixture.  --git optionally checks the
snapshots against the exact selected Git blobs.  PASS means the review receipt
is reproducible, not that a Gate has been accepted or runtime behavior measured.
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import re
import struct
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
MANIFEST = BASE / 'source-manifest.json'
RESULT = BASE / 'review-results.json'


class ReviewError(ValueError):
    """One of the fixed source or bounded reproduction checks did not hold."""


def require(condition, message):
    if not condition:
        raise ReviewError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git_blob_id(data):
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


class Sources:
    def __init__(self, manifest_path=MANIFEST):
        self.manifest = json.loads(manifest_path.read_bytes())
        self.rows = {row['name']: row for row in self.manifest['sources']}
        require(len(self.rows) == len(self.manifest['sources']), 'duplicate source aliases')

    @lru_cache(maxsize=None)
    def blob(self, name):
        row = self.rows[name]
        archive = (BASE / row['archive']).resolve()
        require(archive.is_relative_to(BASE / 'sources'), 'source path escapes snapshot directory')
        packed = archive.read_bytes()
        require(len(packed) == row['archive_bytes'], f'{name}: archive size')
        require(sha(packed) == row['archive_sha256'], f'{name}: archive digest')
        raw = gzip.decompress(packed)
        require(len(raw) == row['source_bytes'], f'{name}: source size')
        require(sha(raw) == row['sha256'], f'{name}: source digest')
        require(git_blob_id(raw) == row['git_blob'], f'{name}: git blob digest')
        return raw

    def text(self, name):
        raw = self.blob(name)
        if self.rows[name]['path'].endswith('.gz'):
            raw = gzip.decompress(raw)
        return raw.decode('utf-8')

    def json(self, name):
        return json.loads(self.text(name))

    def check_snapshots(self):
        for name in self.rows:
            self.blob(name)
        return len(self.rows)

    def check_actual_git(self, fetch=False):
        commits = sorted({row['commit'] for row in self.rows.values()})
        if fetch:
            subprocess.run(['git', '-c', 'gc.auto=0', 'fetch', '--no-tags', '--depth=1',
                            'origin', *commits], cwd=ROOT, check=True)
        for name, row in self.rows.items():
            data = subprocess.check_output(['git', '-c', 'gc.auto=0', 'show',
                                            f"{row['commit']}:{row['path']}"], cwd=ROOT)
            require(data == self.blob(name), f'{name}: snapshot differs from actual Git bytes')
        return len(self.rows)


def decode_bl(word, pc):
    """Decode an AArch64 BL word without executing or disassembling peer code."""
    require(word & 0xFC000000 == 0x94000000, f'not BL at {pc:#x}')
    imm = word & 0x03FFFFFF
    if imm & (1 << 25):
        imm -= 1 << 26
    return pc + imm * 4


def decode_store_x20_x19(word):
    """Decode STR Xt,[Xn,#imm12*8], constrained to the published registers."""
    require(word & 0xFFC00000 == 0xF9000000, 'not STR unsigned 64-bit')
    require(word & 31 == 20 and (word >> 5) & 31 == 19, 'unexpected STR registers')
    return ((word >> 10) & 0xFFF) * 8


def token_ordinal(token, field_count):
    kind, src = (token >> 29) & 7, token & 0x1FFFFFFF
    require(kind == 4, 'token is not published FieldInfo kind 4')
    require(src & 1 == 1, 'token source is not odd')
    ordinal = (src - 1) // 2
    require(0 <= ordinal < field_count, 'token ordinal outside selected PID')
    return kind, src, ordinal


def extract_pid_and_layout(dump):
    images = re.findall(r'^// Image (\d+): ([^\n]+?) - (\d+)$', dump, re.M)
    require(len(images) >= 2 and images[0] == ('0', 'Assembly-CSharp.dll', '0')
            and images[1][2] == '2462', 'image boundary changed')
    cls = re.search(r'^.*\bclass Board_PVP(?=[\s:<]).*// TypeDefIndex: (\d+)$', dump, re.M)
    require(cls is not None and int(cls.group(1)) == 852, 'Board_PVP type missing')
    pid_matches = list(re.finditer(
        r'^internal sealed class <PrivateImplementationDetails> // TypeDefIndex: (\d+)\n\{(.*?)^\}',
        dump, re.M | re.S))
    candidates = [m for m in pid_matches if 852 < int(m.group(1)) < 2462]
    require(len(candidates) == 1 and int(candidates[0].group(1)) == 2461,
            'image does not have the selected unique PID class')
    fields = re.findall(r'^\s*internal static readonly\s+(\S+)\s+([0-9A-F]{64})\b',
                        candidates[0].group(2), re.M)
    require(len(fields) == 740, 'PID field count changed; do not skip scalar declarations')
    end = dump.index('\n\t// Methods', cls.start())
    field_rows = re.findall(
        r'^\s*(?:public|private|protected|internal)\s+(?!static\b)'
        r'([\w.\[\]<>`]+)\s+(\w+)\s*;\s*//\s*0x([0-9A-Fa-f]+)',
        dump[cls.start():end], re.M)
    layout = {int(off, 16): (name, typ) for typ, name, off in field_rows}
    require(len(layout) == len(field_rows), 'duplicate instance offsets')
    return fields, layout


def word_at(code, base, rva):
    pos = rva - base
    require(0 <= pos <= len(code) - 4 and pos % 4 == 0, 'instruction outside published ctor')
    return int.from_bytes(code[pos:pos + 4], 'little')


def rebind_arrays(native, dump, defaults, previous, hunter, registry, ia):
    fields, layout = extract_pid_and_layout(dump)
    expected = {
        408: ('rewardIndexs', 'int[]'), 416: ('rewardValues', 'int[]'),
        424: ('rewardScales', 'float[]'), 520: ('allBetCoinValues', 'int[]'),
        528: ('allBetGemValues', 'int[]'), 536: ('allBetMedalValues', 'int[]'),
    }
    require({off: layout.get(off) for off in expected} == expected, 'dump layout mismatch')
    ctors = [m for m in native['methods'] if m['class_name'] == 'Board_PVP'
             and m['signature'] == 'public void .ctor() { }']
    require(len(ctors) == 1, 'expected exactly one published constructor')
    ctor = ctors[0]
    require(ctor['rva'] == 19796420 and ctor['size'] == 500, 'constructor identity')
    code = bytes.fromhex(ctor['bytes_hex'])
    require(len(code) == 500 and sha(code) == ctor['sha256'], 'constructor byte hash')
    events = ctor['initialize_arrays']
    require(len(events) == 6 and all('field_id' not in e for e in events),
            'event count or event schema changed')
    hrows = {row['field'].split('.')[-1]: row for row in hunter['arrays']}
    brows = {row['field']: row for row in registry['c1']['binding']}
    require(len(hrows) == len(brows) == 6, 'published binding rows not unique')
    offsets, out = set(), []
    for e in events:
        pc, slot, token = e['initialize_rva'], e['slot_va'], e['token_lo']
        kind, source, ordinal = token_ordinal(token, len(fields))
        declared_pid, field_id = fields[ordinal]
        require(declared_pid.endswith('=24'), 'PID entry is not a 24-byte blob')
        require(e['length'] == 6 and e['rva'] == pc, 'array event length or PC')
        token_bytes = bytes.fromhex(e['blobs'][0])
        require(int.from_bytes(token_bytes[:4], 'little') == token
                and int.from_bytes(token_bytes[8:12], 'little') == e['token_hi'],
                'published event token bytes do not agree with event fields')
        require(any(ref['slot_va'] == slot and ref['token_lo'] == token
                    for ref in ctor['slot_refs']), 'event lacks matching published slot reference')
        bl, store = word_at(code, ctor['rva'], pc), word_at(code, ctor['rva'], pc + 4)
        require(decode_bl(bl, pc) == 33927292, 'InitializeArray target changed')
        offset = decode_store_x20_x19(store)
        require(offset in expected and offset not in offsets, 'unexpected/duplicate store offset')
        offsets.add(offset)
        name, typ = expected[offset]
        entry = defaults['<PrivateImplementationDetails>.' + field_id]
        require(entry['field_index'] - ordinal == 16300, 'PID ordinal/index relationship changed')
        data = bytes.fromhex(entry['raw'])[:24]
        require(len(data) == 24, 'default payload too short')
        values = list(struct.unpack('<6f' if typ == 'float[]' else '<6i', data))
        h, b = hrows[name], brows[name]
        require(h['instance_offset'] == offset and h['slot_va'] == slot
                and h['blob']['field_id'] == field_id and h['values'] == values,
                f'{name}: independently rederived chain disagrees with 149')
        require(b['slot_va'] == slot and b['field_id'] == field_id and b['values'] == values,
                f'{name}: independently rederived chain disagrees with v4')
        out.append({'field': name, 'instance_offset': offset, 'declared': typ,
                    'initialize_rva': pc, 'slot_va': slot, 'token_lo': token,
                    'token_kind': kind, 'token_source': source, 'pid_type_index': 2461,
                    'field_ordinal': ordinal, 'field_id': field_id,
                    'field_index': entry['field_index'], 'first_24_bytes_hex': data.hex(),
                    'values': values, 'call_word': f'{bl:08x}', 'store_word': f'{store:08x}'})
    require(offsets == set(expected), 'missing store offset')
    out.sort(key=lambda row: row['instance_offset'])
    prior = previous['table']['reward_indexs']
    require(prior['identification'].startswith('only six-int')
            and prior['blob'].split('.')[-1] == out[0]['field_id']
            and prior['values'] == out[0]['values'], '133 content anchor differs')
    # This earlier export explicitly used the *same* token convention. It is a
    # cross-source consistency check, not an independent proof of that convention.
    old_rows = {int(row['addr'], 16): row for bucket in ia['methods'].values()
                for row in bucket if isinstance(row, dict) and 'addr' in row}
    overlap = []
    for method in native['methods']:
        for e in method.get('initialize_arrays') or []:
            if e['initialize_rva'] not in old_rows:
                continue
            try:
                _, _, ordinal = token_ordinal(e['token_lo'], len(fields))
            except ReviewError:
                continue
            old_id = old_rows[e['initialize_rva']]['field'].split('.')[-1]
            overlap.append({'class_name': method['class_name'], 'rva': e['initialize_rva'],
                            'field_id_matches': fields[ordinal][1] == old_id})
    require(len(overlap) == 1 and overlap[0]['class_name'] == 'GameDatas'
            and overlap[0]['field_id_matches'], 'same-rule export overlap changed')
    return {'constructor_rva': ctor['rva'], 'constructor_sha256': ctor['sha256'],
            'raw_event_contains_literal_field_id': False, 'pid_fields': len(fields),
            'image': 'Assembly-CSharp.dll', 'independent_content_anchor': '133/rewardIndexs',
            'same_rule_export_overlap': overlap, 'arrays': out,
            'boundary': 'existing published slice only; token/ordinal convention is shared, '
                        'not a new ELF/global-metadata decoder or runtime measurement'}


def classify(verdict, kind):
    if verdict == 'RUNTIME':
        return 'runtime-gated→USER'
    return {'PIN-RAW': 'missing-input', 'POLICY': 'policy',
            'INDEX': 'served', 'DATA': 'served'}.get(kind)


def check_ledger(registry, audit, drift):
    items, ledger, contract = audit['items'], registry['ledger'], drift['contract']
    by_item = {row['n']: row for row in items}
    by_contract = {row['n']: row for row in contract}
    by_ledger = {row['n']: row for row in ledger}
    require(len(items) == len(by_item) == 56 and set(by_item) == set(range(1, 57)),
            'audit item identity/coverage')
    require(len(by_contract) == len(contract) == 33, 'contract IDs not unique')
    expected = {n for n, row in by_item.items() if row['verdict'] not in ('CLOSED', 'NOTE')}
    require(len(ledger) == len(by_ledger) == 32 and set(by_ledger) == expected,
            'ledger is not exactly the nonclosed/nonnote set')
    require(set(by_contract) == expected | {56}, 'contract/ledger partition mismatch')
    counts = collections.Counter()
    owner_counts = collections.Counter()
    for n, row in by_ledger.items():
        original, plan = by_item[n], by_contract[n]
        for key in ('item', 'report', 'verdict', 'closer'):
            require(row.get(key) == original.get(key), f'{n}: audit field {key} mismatch')
        for key in ('kind', 'owner'):
            require(row.get(key) == plan.get(key), f'{n}: contract field {key} mismatch')
        require(isinstance(row.get('owner'), str) and row['owner'].strip()
                and isinstance(row.get('step'), str) and row['step'].strip(),
                f'{n}: missing owner or next step')
        require(row['label'] == classify(row['verdict'], row['kind']),
                f'{n}: label not derived from published rules')
        counts[row['label']] += 1
        owner_counts[row['owner']] += 1
    require(dict(counts) == registry['totals']['by_label'], 'label totals mismatch')
    verdicts = collections.Counter(row['verdict'] for row in items)
    require(verdicts == {'CLOSED': 23, 'RUNTIME': 20, 'OPEN': 9,
                         'RESTATED': 3, 'NOTE': 1}, 'audit verdict totals changed')
    require(registry['totals']['closed'] == 23 and registry['totals']['note'] == 1
            and registry['totals']['items'] == 56 and registry['totals']['ledger'] == 32,
            'registry partition totals mismatch')
    require(registry['not_in_ledger']['note_items'] == [56], 'NOTE 56 not explicit')
    require(all(by_item[n]['verdict'] == 'CLOSED' and by_item[n]['closer'] == 149
                for n in (30, 39, 40)), 'C1 closed rows changed')
    require('served, not shipped' in by_item[9]['reason'], 'item 9 original wording changed')
    require(all('blob unbound' in by_item[n]['blocking'] for n in (39, 40)),
            'closed rows no longer contain the original blocking text')
    return {'audit_items': len(items), 'distinct_audit_ids': len(by_item),
            'verdict_counts': dict(sorted(verdicts.items())), 'ledger_rows': len(ledger),
            'distinct_ledger_ids': len(by_ledger), 'labels': dict(sorted(counts.items())),
            'owners_literal': dict(sorted(owner_counts.items())),
            'note_item': 56, 'rows': sorted(ledger, key=lambda r: r['n']),
            'item9_original_reason': by_item[9]['reason'],
            'closed_rows_original_blocking': {str(n): by_item[n]['blocking'] for n in (30,39,40)},
            'boundary': 'classification/partition/owner strings mechanically checked for all '
                        'rows; source semantics not independently proved for every row'}


def lines_with(text, *needles):
    return [{'line': n, 'text': line} for n, line in enumerate(text.splitlines(), 1)
            if any(needle in line for needle in needles)]


def check_spec_dispositions(design, closure, start):
    """Verify the selected spec records requested scope; text is not runtime proof."""
    checks = {
        'C1_same_rule_not_runtime': all(x in closure for x in
            ('tái kiểm độc lập của reviewer', 'Cùng quy tắc đã công bố', 'không phải runtime')),
        'C2_shop_paths_and_unknown_live': all(x in closure for x in
            ('default build của các dòng shop đã xét là từ ctor', 'giá/stock SKU thực chưa đo',
             'event-pass/served (nếu có) cần nguồn riêng', 'Không khẳng định "mọi SKU buộc từ server"')),
        'C2_old_blocking_historical': all(x in closure for x in
            ('Items 39/40', 'quote lịch sử', 'KHÔNG còn blocker hiện hành')),
        'C2_item52_open_and_conflicting': all(x in closure for x in
            ('Item 52', 'CONFLICTING', 'item 52 **giữ trong sổ**', 'chưa đối chứng')),
        'C4_document_wide_supersession': all(x in design for x in
            ('SUPERSEDE TOÀN VĂN', 'mọi câu summary/tally/absolute',
             'không thấy trong mẫu 139 file asm', 'không phải kết luận toàn cục')),
        'C3_C5_bounded_supersession': all(x in closure for x in
            ('START_HERE.md:11', 'L2 không còn thiếu số', 'mọi hạng mục tĩnh đã đóng',
             'L1-tĩnh đã chọn', 'deferred/UNKNOWN/RUNTIME_UNVERIFIED')),
        'prior_start_absolute_still_present_but_scoped': 'Việc thiết kế duy nhất là ART' in start,
    }
    require(all(checks.values()), 'selected spec does not contain all scoped dispositions')
    return {'literal_scope_locators': checks,
            'boundary': 'locators record an explicit director disposition, not a proof '
                        'of token semantics, full-game absence, implementation, or runtime'}


def check_api_capture(api, sources):
    """Check captured API objects internally; this does not certify GitHub itself."""
    expected_heads = {'producer_cut': sources.manifest['producer_cut'],
                      'later_producer': sources.manifest['producer_later_cut'],
                      'spec_cut': sources.manifest['spec_cut'],
                      'prior_reviewer_head': '57aee0cc118bb261276fc9fbc452213a72507c9d'}
    require(api['heads'] == expected_heads, 'captured API head identities changed')
    required_comments = (6440973318, 6441583848, 6444077936, 6444126847,
                         6444295176, 6444324415, 6444436552, 6444472292)
    for n in required_comments:
        row = api['comments'][str(n)]
        require(row['id'] == n and row['issue_url'].endswith('/issues/12'),
                f'captured comment {n} identity')
    ids = collections.defaultdict(list)
    names = collections.defaultdict(set)
    skipped = []
    for key, item in api['runs'].items():
        run = item['run']
        label = item['source_head_label']
        require(str(run['id']) == key and run['head_sha'] == expected_heads[label],
                f'captured run {key} identity')
        require(run['status'] == 'completed' and run['conclusion'] == 'success',
                f'captured run {key} was not completed-success at capture')
        ids[label].append(run['id'])
        names[label].add(run['name'])
        if run['name'] == 'runtime-probe':
            probe = [step for job in item['jobs']['jobs'] for step in job['steps']
                     if step['name'] == 'Probe game state']
            require(len(probe) == 1 and probe[0]['conclusion'] == 'skipped',
                    f'captured runtime probe step {key} was not skipped')
            skipped.append(run['id'])
    for label in ('producer_cut', 'later_producer', 'spec_cut'):
        require({'docs-verify', 'bridge-build', 'runtime-probe'} <= names[label],
                f'captured workflows missing for {label}')
    require(len(ids['prior_reviewer_head']) >= 4, 'prior review archive workflows missing')
    return {'retrieved_utc': api['retrieved_utc'],
            'successful_run_ids_by_exact_head': {label: sorted(values)
                                                for label, values in sorted(ids.items())},
            'runtime_probe_state_skipped_run_ids': sorted(skipped),
            'comment_ids': sorted(int(n) for n in api['comments']),
            'boundary': 'historical GitHub API capture, not the future review commit CI; '
                        'success of skipped device jobs is not runtime evidence'}


def review(sources):
    count = sources.check_snapshots()
    registry, audit, drift = sources.json('registry'), sources.json('audit'), sources.json('drift')
    require(sources.blob('registry') == sources.blob('spec_registry'), 'spec v4 byte mismatch')
    require(sources.blob('registry') == sources.blob('later_registry')
            and sources.blob('audit') == sources.blob('later_audit'),
            'later producer registry/audit changed')
    later_drift = sources.json('later_drift')
    require(drift['contract'] == later_drift['contract'], 'later drift contract changed')
    require(drift['totals']['artifacts'] == 48 and later_drift['totals']['artifacts'] == 49,
            'later drift artifact totals changed')
    firebase = sources.json('later_firebase181')
    item52 = next(row for row in registry['ledger'] if row['n'] == 52)
    require('0x2ADB958 is unnamed' in item52['step'], 'item 52 old claim changed')
    require(firebase['cell']['va'] == 0x2ADB958
            and firebase['cell']['klass'] == 'FirebaseDatabaseManager'
            and firebase['cell']['field']['name'] == 'Instance', '181 publication changed')
    parents = {row['rva'] for row in firebase['census']['rows']
               if row['class_name'] in ('PVP_Manager', 'ArenaManager')
               and 'LoadRemoteConfigs' in row['signature']}
    require(parents == {19916080, 22691808}, '181 census parents changed')
    require('class này chưa được định danh bằng symbol đã pin' in sources.text('doc138'),
            '138 original unknown changed')
    for name, key in [('audit', 'audit'), ('residue', 'residue'),
                      ('hunter149', 'hunter'), ('defaults', 'defaults')]:
        require(registry['provenance'][key]['sha256'] == sources.rows[name]['sha256'],
                f'{name}: embedded provenance digest mismatch')
    c1 = rebind_arrays(sources.json('key_native'), sources.text('dump'),
                       sources.json('defaults')['fields'], sources.json('hunter133'),
                       sources.json('hunter149'), registry, sources.json('ia_resolved'))
    ledger = check_ledger(registry, audit, drift)
    shop = sources.json('shop157')
    shipped = {k: shop['shipped'][k]['value'] for k in
               ('MaxStockCount', 'ItemPlayerCost', 'ItemDroneCost')}
    require(shipped == {'MaxStockCount': 10, 'ItemPlayerCost': 50, 'ItemDroneCost': 30},
            'shop constructor publication changed')
    code = sources.text('registry_code')
    require("load(HUNTER_ART)['arrays']" in code and "row['blob']['field_id']" in code
            and "all('metadata usage' not in" in code, 'v4 verifier source locator changed')
    spec = check_spec_dispositions(sources.text('spec_design'), sources.text('spec_closure'),
                                   sources.text('spec_start'))
    api_bytes = (BASE / 'api-captures.json.gz').read_bytes()
    api = check_api_capture(json.loads(gzip.decompress(api_bytes)), sources)
    api['archive_sha256'] = sha(api_bytes)
    docs = {
        'prior_design': lines_with(sources.text('spec_previous_design'), '3 mục không tồn tại',
                                   'game gốc không có', 'aim assist'),
        'prior_coverage': lines_with(sources.text('spec_previous_coverage'), '3/6 không tồn tại'),
        'intermediate_design': lines_with(sources.text('spec_intermediate_design'),
                                          'SUPERSEDE', 'game gốc không có', '3 mục không tồn tại',
                                          'L2 (khớp số bản gốc)', 'STATIC-COMPLETE CEILING'),
        'intermediate_closure': lines_with(sources.text('spec_intermediate_closure'),
                                           'Lớp served', 'Đọc đúng', 'Items 39/40'),
        'design': lines_with(sources.text('spec_design'), 'SUPERSEDE', 'game gốc không có',
                             '3 mục không tồn tại', '3/6 không tồn tại',
                             'L2 (khớp số bản gốc)', 'STATIC-COMPLETE CEILING'),
        'coverage': lines_with(sources.text('spec_coverage'), '3/6 không'),
        'start': lines_with(sources.text('spec_start'), 'Việc thiết kế duy nhất là ART',
                            '0 site trong 139 file asm'),
        'closure': lines_with(sources.text('spec_closure'), 'Item 9', 'per-SKU',
                              '39/40', 'C3/C5', 'SUPERSEDE', 'supersede', 'scope', 'phạm vi'),
        'decisions': lines_with(sources.text('spec_decisions'), '| **C1**', '| **C2**',
                                '| **C3**', '| **C4**', '| **C5**'),
        'producer_158': lines_with(sources.text('doc158'), 'Giá một ô lấy từ đâu?',
                                   'EventRewards` ai dựng?', 'hai trần là cùng một field',
                                   'Không kết luận gì cho các dòng'),
    }
    return {'schema': '8141386a/gate1-v4-review-result/1',
            'reviewer_branch': sources.manifest['reviewer_branch'],
            'producer_cut': sources.manifest['producer_cut'],
            'later_producer_cut': sources.manifest['producer_later_cut'],
            'later_producer_check': {'registry_and_audit_identical': True,
                                     'drift_contract_identical': True,
                                     'drift_artifact_count_before': 48,
                                     'drift_artifact_count_after': 49,
                                     'item52_old_step': item52['step'],
                                     'item52_report181_claim': {'cell_va': firebase['cell']['va'],
                                                                'klass': firebase['cell']['klass'],
                                                                'field': firebase['cell']['field']['name'],
                                                                'census_parent_rvas': sorted(parents)},
                                     'report_181': 'producer publication only; not independently '
                                                   'reviewed, despite the conflicting old item-52 text'},
            'spec_cut': sources.manifest['spec_cut'],
            'source_snapshot_count': count,
            'source_manifest_sha256': sha(MANIFEST.read_bytes()),
            'producer_registry_sha256': sources.rows['registry']['sha256'],
            'original_125_sha256': sources.rows['original_review125']['sha256'],
            'github_api_snapshot': api, 'selected_spec_dispositions': spec,
            'c1': c1, 'c2': ledger, 'shop157_shipped_constructor_values': shipped,
            'source_quote_locators': docs,
            'limitations': ['The token-to-PID convention is reproduced from the same published '
                            'rule; neither a fresh metadata extractor nor a device was run.',
                            'A text supersession/waiver is a disposition, not proof that the '
                            'original runtime or every store SKU is known.',
                            'Producer and reviewer CI success proves the checked workflow ran, '
                            'not Gate approval; skipped device steps are not runtime evidence.']}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--write', action='store_true')
    p.add_argument('--git', action='store_true', help='compare every archive to its actual Git blob')
    p.add_argument('--fetch', action='store_true', help='fetch selected commits before --git')
    args = p.parse_args(argv)
    if args.fetch and not args.git:
        p.error('--fetch requires --git')
    sources = Sources()
    actual = review(sources)
    if args.git:
        print('PASS actual Git source bytes:', sources.check_actual_git(fetch=args.fetch))
    raw = (json.dumps(actual, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()
    if args.write:
        RESULT.write_bytes(raw)
        print('WROTE', RESULT.relative_to(ROOT), 'bytes', len(raw), 'sha256', sha(raw))
    else:
        require(RESULT.read_bytes() == raw, 'saved result differs from independent recomputation')
        print('PASS re-review result:', len(actual['c1']['arrays']), 'arrays,',
              actual['c2']['ledger_rows'], 'ledger rows,', actual['source_snapshot_count'], 'sources')
    print('Boundary: source reproduction and row bookkeeping only; no runtime/Gate approval.')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ReviewError, OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print('FAIL', exc, file=sys.stderr)
        raise SystemExit(1)
