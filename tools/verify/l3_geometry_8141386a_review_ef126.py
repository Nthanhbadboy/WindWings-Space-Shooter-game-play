"""R1/122 independent bounded ef126 caller-dispatch review.
provenance: arena/8141386a-windwings-space-shooter-game-p
Own fresh original ELF spans and separate guarded harness, not producer126 verifier
execution, serialized-owner rediscovery, full builder/heap/runtime or #27-full closure.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import json
import struct
import subprocess

from tools.verify.geometry_8141386a_atlas_io import ROOT, BRANCH, canonical, sha, sha_file
from tools.verify.geometry_8141386a_review_ef123_checks import branch
from tools.verify.l3_geometry_8141386a_review_ef126_native import RAW, SOURCE_HEAD, SOURCE_RUN, TARGET, CASES, replay, read

OUTPUT = ROOT / 'datas/l3_geometry_review_ef126_8141386a.json.gz'
SCI = '01448eec4273ba2fdbebe6c3a442c8bf8e658d3e'
REPORT = '8bec5129adde46ff660608582ba07e32481b966b'
N2_HEAD = '7e5abde50232ed6b10fe631973a27e5f5e99b1f0'
PEER_SHA = 'f209ea3fbc57b3b934c0f4a049f617ff54639e00e83be5fe4430da2a95c60bf5'
PROBE_SHA = '05c3ae3e4af03fffa2a880003c78e82f71044647f39e896e3180dd28d0977eb7'
TERMINATORS = {0x6cef64: (0x6cefdc, 0x6cefd8, 0x17fa8845, 'B_TO_TAIL'),
    0x6cefdc: (0x6ceffc, 0x6ceff8, 0xd61f0020, 'BR_X1_TO_SERVICE'),
    0x6d6bf8: (0x6d6c2c, 0x6d6c28, 0xd65f03c0, 'RET'),
    0x6cf768: (0x6cf7b4, 0x6cf7b0, 0xd65f03c0, 'RET'),
    0x5710ec: (0x57112c, 0x571128, 0xd65f03c0, 'RET')}


def blob_id(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def validate_pins(manifest=None):
    m = manifest or json.loads((RAW / 'peer-pins.json').read_bytes())
    if (m['item'], m['provenance'], m['scientific_commit'], m['report_commit']) != (122, BRANCH, SCI, REPORT):
        raise ValueError('fixed ef126 review target changed')
    if len(m['pins']) != 9:
        raise ValueError('selected fixed source pin coverage changed')
    for p in m['pins']:
        if p['commit'] not in (SCI, REPORT):
            raise ValueError('unselected producer commit')
        data = (ROOT / p['snapshot']).read_bytes()
        if len(data) != p['size'] or sha(data) != p['sha256']:
            raise ValueError('peer126 snapshot changed')
        original = data if p['encoding'] == 'gzip-as-source' else gzip.decompress(data)
        if sha(original) != p['source_sha256'] or blob_id(original) != p['git_blob']:
            raise ValueError('peer126 source/Git identity changed')
    if sha_file(RAW / 'peer-artifact126.json.gz') != PEER_SHA or sha_file(RAW / 'peer-probe126.json.gz') != PROBE_SHA:
        raise ValueError('fixed scientific126 artifact/raw identity changed')
    return m


def verify_git(fetch=False):
    m = validate_pins(); n2 = json.loads((RAW / 'n2-publication-check.json').read_bytes())
    pins = m['pins'] + n2['refs']
    for head in sorted({p['commit'] for p in pins}):
        exists = subprocess.run(['git', '-C', str(ROOT), 'cat-file', '-e', head+'^{commit}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
        if not exists:
            if not fetch:
                raise ValueError('missing selected Git commit; explicit --fetch required')
            subprocess.run(['git', '-C', str(ROOT), 'fetch', '--no-tags', '--depth=1', '--filter=blob:none', 'origin', head], check=True)
    for p in pins:
        data = subprocess.check_output(['git', '-C', str(ROOT), 'show', p['commit']+':'+p['path']])
        if sha(data) != p['source_sha256'] or blob_id(data) != p['git_blob']:
            raise ValueError('actual fixed Git source bytes differ: '+p['path'])
    return len(pins)


def static_audit(peer, probe, fresh):
    requested = {}
    for r in probe['windows'] + probe['cells']:
        key = (r['va'], len(r['hex'])//2)
        if key in requested and requested[key] != r['hex']:
            raise ValueError('conflicting peer requested spans')
        requested[key] = r['hex']
    actual = {(r['va'], r['size']): r['hex'] for r in fresh['peer_selected_spans']}
    if actual != requested or len(actual) != 17:
        raise ValueError('fresh17-span original coverage mismatch')
    for r in fresh['peer_selected_spans']:
        if sha(bytes.fromhex(r['hex'])) != r['sha256']:
            raise ValueError('fresh original span digest differs')
    fdes = {r['start']: r for r in fresh['selected_fdes']}
    if set(fdes) != {r['entry'] for r in probe['followed']} or len(fdes) != 10:
        raise ValueError('fresh original10-FDE coverage mismatch')
    for p in probe['followed']:
        a = p['unwind']; b = fdes[p['entry']]
        if (a['end'], a['fde_hex'], a['fde_va'], a['table_hex'], a['table_va']) != (b['end_exclusive'], b['fde_hex'], b['fde_va'], b['table_hex'], b['table_va']):
            raise ValueError('original FDE/table identity differs')
        delta, size = struct.unpack_from('<iI', bytes.fromhex(b['fde_hex']), 8)
        if b['fde_va']+8+delta != b['start'] or b['start']+size != b['end_exclusive']:
            raise ValueError('FDE initial-location/range arithmetic differs')
    image = {}
    for r in fresh['peer_selected_spans']:
        for i, value in enumerate(bytes.fromhex(r['hex'])):
            a = r['va']+i
            if a in image and image[a] != value:
                raise ValueError('fresh byte overlap conflict')
            image[a] = value
    def word(pc): return struct.unpack('<I', bytes(image[pc+i] for i in range(4)))[0]
    refs = fresh['target_direct_branches']
    normalized = [{k: r[k if k != 'owner_end' else 'owner_end_exclusive'] for k in ('pc','target','owner_start','owner_end')} for r in refs]
    if normalized != peer['direct_refs'] or normalized != probe['direct_refs'] or [r['pc'] for r in refs] != [0x6cef84,0x6cefe4]:
        raise ValueError('fresh whole-executable two-reference census differs')
    for r in refs:
        b = branch(word(r['pc']), r['pc'])
        if not r['link'] or not b or not b['link'] or b['target'] != TARGET or bytes(image[r['pc']+i] for i in range(4)).hex() != r['hex']:
            raise ValueError('fresh direct BL instruction arithmetic differs')
    if fresh['target_addend_matches_all_rela_types'] or peer['rela_matches'] or probe['rela_matches']:
        raise ValueError('unexpected RELA addend target match')
    if fresh['all_rela_total'] != 29626 or fresh['rela_type_counts'] != {'257':10,'1025':11,'1026':338,'1027':29267}:
        raise ValueError('original all-type RELA census differs')
    if fresh['executable_instruction_words_scanned'] != sum(s['filesz']//4 for s in fresh['segments'] if s['flags']&1) or fresh['executable_instruction_words_scanned'] != 3456888:
        raise ValueError('file-backed executable scan coverage differs')
    selected = {r['address']: r['addend'] for r in fresh['selected_relative_relas']}
    if selected != {r['address']: r['addend'] for r in probe['relocations']} or len(selected) != 236:
        raise ValueError('selected original relative-relocation equality differs')
    imports = [{k:r[k] for k in ('address','name','symbol_entry_offset','symbol_hex','name_file_offset','name_hex')} for r in fresh['imports']]
    if imports != probe['imports']:
        raise ValueError('original dynamic import identities differ')
    for r in imports:
        if bytes.fromhex(r['name_hex']) != r['name'].encode()+b'\0':
            raise ValueError('import name bytes differ')
    ends = []
    for entry, (end, pc, opcode, kind) in TERMINATORS.items():
        if fdes[entry]['end_exclusive'] != end or word(pc) != opcode or pc != end-4:
            raise ValueError('FDE end/last instruction kind differs')
        ends.append(dict(entry=entry,end_exclusive=end,last_instruction_pc=pc,opcode=opcode,kind=kind))
    # Exact original linkage and load/store witnesses, not invented class semantics.
    expected = {0x6cef6c:0xf9408c08,0x6cef80:0xf9008c01,0x6cef90:0xf9407108,
        0x6cef94:0xd63f0100,0x6cefac:0xf9406d08,0x6cefb0:0xd63f0100,
        0x6ceff0:0xf9407101,0x6d6c08:0x39040808,0x6d6c20:0x39040c08,0x571114:0xb9003808}
    if any(word(pc) != op for pc, op in expected.items()):
        raise ValueError('original field/virtual-slot instruction witness differs')
    tail = branch(word(0x6cefd8),0x6cefd8)
    if not tail or (tail['pc'],tail['target'],tail['link']) != (0x6cefd8,0x5710ec,False):
        raise ValueError('set-wrapper tail branch differs')
    return dict(fresh_matched_spans=17,fresh_matched_fdes=10,selected_relative_relas=236,
        imports=imports,all_rela_total=fresh['all_rela_total'],rela_type_counts=fresh['rela_type_counts'],
        target_rela_matches_all_types=0,executable_words_scanned=fresh['executable_instruction_words_scanned'],
        direct_bls=refs,executed_body_terminators=ends,
        field_and_virtual_witnesses=[dict(pc=pc,word=op,hex=struct.pack('<I',op).hex()) for pc,op in expected.items()],
        boundary='Whole file-backed executable and ELF RELA target census was freshly performed by own source collector; only selected bytes are retained locally. This is linkage scope, not all indirect users or whole-program runtime invocation.')


def n2_audit(peer):
    n2 = read('peer-n2-artifact.json.gz'); pub = json.loads((RAW/'n2-publication-check.json').read_bytes())
    if pub['provenance'] != BRANCH or any(r['commit'] != N2_HEAD for r in pub['refs']):
        raise ValueError('fixed inherited N2 publication changed')
    for r in pub['refs']:
        data = gzip.decompress((ROOT/r['snapshot']).read_bytes())
        if sha(data) != r['source_sha256'] or blob_id(data) != r['git_blob']:
            raise ValueError('inherited N2 publication bytes differ')
    if n2['serialized_owner'] != peer['n2_owner'] or n2['serialized_owner'] != peer['n2_source']['owner']:
        raise ValueError('peer126/N2 owner equality differs')
    if n2['unresolved_edges'] != peer['n2_source']['unresolved_edges'] or any(n2['unresolved_edges'].values()):
        raise ValueError('unproven N2 edges were promoted')
    if sha(gzip.decompress((RAW/'peer-n2-artifact.json.gz').read_bytes())) != peer['n2_source']['artifact_sha256'] or sha(gzip.decompress((RAW/'peer-n2-report158.md.gz').read_bytes())) != peer['n2_source']['report_sha256']:
        raise ValueError('126 inherited N2 source identity differs')
    return dict(upstream_commit=N2_HEAD,owner=n2['serialized_owner'],unresolved_edges=n2['unresolved_edges'],
        evidence='Actual published N2 Git-byte equality plus inherited recorded identity. No own serialized-source census or native-instance/constructor join.')


def replay_audit(peer):
    if len(peer['cases']) != 4:
        raise ValueError('producer canonical four-case coverage differs')
    rows = []
    for case, old in zip(CASES, peer['cases']):
        r = replay(case)
        if r['native_instruction_count'] != old['run']['instruction_count'] or r['executed_addresses'] != old['run']['executed_addresses']:
            raise ValueError('own/producer exact native count or PC-set differs: '+case)
        if any(r['pc_counts'].get(pc,0) != n for pc,n in old['pc_hits'].items()):
            raise ValueError('own/producer selected PC multiplicity differs')
        if r['graph_builder_sinks'] != old['graph_builder_calls'] or r['node_after'] != old['node_after']:
            raise ValueError('own/producer canonical sink arguments or node effects differ')
        if (r['entry'],r['last_native_pc'],r['return_value'],r['stack_pointer_after'],r['stop_pc']) != (old['entry'],old['ret'],old['run']['return_value'],old['stack_pointer_after'],old['stop_pc']):
            raise ValueError('own/producer return/last-PC/stack/stop protocol differs')
        normalized = []
        for v in r['virtual_services']:
            d = dict(v)
            if d['kind'] == 'owner_release':
                obs = r['synthetic_d8_identity_observations'][0]
                d.update({k:obs[k] for k in ('controller_path','component_path','gameobject_path','root_gameobject','controller_ref_path')})
            normalized.append(d)
        if normalized != old['virtual_calls'] or r['import_services_called'] or old['service_calls'] or old['failure_calls']:
            raise ValueError('own/producer virtual/service boundary differs')
        forbidden = {TARGET,0x57112c,0x109acc0,0x109ace0,r['addresses']['e0'],r['addresses']['d8'],r['addresses']['stop']}
        if forbidden.intersection(r['executed_addresses']):
            raise ValueError('synthetic/excluded PC counted as original native code')
        owner = r['addresses']['owner']; c = r['addresses']['controller']
        if any(owner+8 <= x['address'] < owner+0x70 for x in r['native_memory_reads']):
            raise ValueError('selected native path unexpectedly read prepared N2 identity fields')
        if any(x['address'] == c+0x103 for x in r['native_memory_writes']):
            raise ValueError('prepared zero103 was misclassified as an executed native write')
        expected = [(c+0x118,8,0 if case=='set_null' else owner),(c+0x102,1,1),(c+0x38,4,0)] if case in ('set_full','set_null') else []
        node_writes = [(x['address'],x['size'],x['value']) for x in r['native_memory_writes'] if c<=x['address']<c+0x200]
        if node_writes != expected:
            raise ValueError('exact native controller write trace differs')
        rows.append(r)
    if [r['native_instruction_count'] for r in rows] != [70,8,8,66]:
        raise ValueError('canonical native totals differ')
    return rows


def build():
    manifest = validate_pins(); peer = read('peer-artifact126.json.gz'); probe = read('peer-probe126.json.gz')
    fresh = read('fresh-original.json.gz'); ci = read('source-ci-receipt.json.gz')
    if (ci['run']['id'],ci['run']['head_sha'],ci['run']['status'],ci['run']['conclusion']) != (SOURCE_RUN,SOURCE_HEAD,'completed','success') or ci['fresh_original_sha256'] != sha_file(RAW/'fresh-original.json.gz'):
        raise ValueError('own fresh exact-source GREEN receipt differs')
    if (ci['peer_verify_run']['head_sha'],ci['peer_verify_run']['status'],ci['peer_verify_run']['conclusion']) != (SCI,'completed','success'):
        raise ValueError('producer scientific Verify is not actual exact-source GREEN')
    for p,h in fresh['tool_pins'].items():
        if sha_file(ROOT/p) != h:
            raise ValueError('fresh source tool/probe bytes changed')
    for p in manifest['pins']:
        if p['path'] in peer['inputs'] and p['source_sha256'] != peer['inputs'][p['path']]:
            raise ValueError('selected producer artifact input pin differs')
    static = static_audit(peer,probe,fresh); inherited = n2_audit(peer); rows = replay_audit(peer)
    paths = [p['snapshot'] for p in manifest['pins']]
    paths += [str((RAW/n).relative_to(ROOT)) for n in ('peer-pins.json','fresh-original.json.gz','source-ci-receipt.json.gz','n2-publication-check.json')]
    paths += ['tools/verify/l3_geometry_8141386a_review_ef126.py','tools/verify/l3_geometry_8141386a_review_ef126_native.py',
        'tools/verify/geometry_8141386a_review_ef123_checks.py','tools/recovery/geometry_8141386a_review_ef126_bytes.py','tools/recovery/geometry_8141386a_review_ef123_bytes.py']
    return dict(schema=1,item=122,provenance=BRANCH,claim=6426714971,
        verdict='APPROVE_BOUNDED_EF126_CALLER_DISPATCH_ON_PREPARED_STATE_NOT_27_FULL',
        target=dict(scientific_commit=SCI,report_commit=REPORT,artifact_sha256=PEER_SHA,raw_sha256=PROBE_SHA),
        original_source=dict(run=SOURCE_RUN,source_head=SOURCE_HEAD,raw_commit=ci['preserved_raw_commit'],
            fresh_original_sha256=sha_file(RAW/'fresh-original.json.gz'),xapk_sha256=fresh['xapk_sha256'],libunity_sha256=fresh['libunity_sha256']),
        static_audit=static,inherited_n2_check=inherited,canonical_own_native_replays=rows,
        counts=dict(canonical_native_cases=4,native_instructions=[r['native_instruction_count'] for r in rows],
            canonical_native_instruction_sum=sum(r['native_instruction_count'] for r in rows),
            graph_builder_sinks=sum(len(r['graph_builder_sinks']) for r in rows),virtual_services=sum(len(r['virtual_services']) for r in rows),
            direct_bls=2,target_rela_matches_all_types=0,new_numeric_contradictions=0,native_n2_identity_field_reads=0,native_byte103_writes=0),
        precision_notes=['Producer ret field is last native PC: rebuild ends in BR X1 at6ceff8 then syntheticE0, not a native RET. Setter last instruction6cefd8 is B to tail5710ec, whose RET is571128.',
            'N2 IDs are inherited publication fields installed by the harness and read by Python D8 instrumentation. The selected native path reads no identity fields; virtual implementations are sinks, not reconstructed methods.',
            'Byte103/halfwordA8 remain prepared zero, not native clears. Native writes for full/null are slot118,byte102 and flags38; equal/rebuild have no controller write.'],
        independence='Own fresh streamed original ELF extraction and separate guarded fresh-span-only Unicorn harness. Shared original build, frozen own119 ELF reader/integer branch helper, Unicorn2.1.4 and explicitly disclosed producer prepared-input protocol. No producer126 verifier/Fixture imports/execution or original native ABI/game-state discovery.',
        limits=['Only file-backed executable direct-B/BL and ELF RELA addend census at one fixed target; indirect dispatch/global game use is not exhausted.',
            'Four canonical fixtures, not all caller inputs. Graph-builder/E0/D8 are explicit uncounted synthetic sinks; reserved PLT/failure paths not entered. TLS/stack/controller/owner/chunk/vtables/IDs are prepared state.',
            'Inherited N2 owner equality is not own serialized-source rediscovery, live controller1856 instance construction or game-side Boss_AttackPhases join. Unresolved N2 edges remain false.',
            'No graph-builder body, real virtual implementations, heap/allocator, parent930DWORD re-execution, scheduling/playback, clip/clock writers, pose/apply/Unity readback, device/runtime/render or #27-full acceptance.',
            'Fixed126 review only.127/128/M1 and other peer lanes remain separate. No frozen118-121 evidence edits, producer cross-edit or selfACK.'],
        source_pins={p:sha_file(ROOT/p) for p in sorted(paths)})


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');p.add_argument('--git',action='store_true');p.add_argument('--fetch',action='store_true');a=p.parse_args()
    if a.fetch and not a.git: p.error('--fetch requires --git')
    value=build();body=gzip.compress(canonical(value)+b'\n',mtime=0)
    if a.check:
        if OUTPUT.read_bytes()!=body: raise SystemExit('R1 ef126 artifact drift')
    else: OUTPUT.write_bytes(body)
    if a.git: print('PASS actual fixed selected Git sources:',verify_git(a.fetch))
    print(value['verdict'],value['counts']);print('artifact',len(body),'SHA256',sha(body))


if __name__=='__main__': main()
