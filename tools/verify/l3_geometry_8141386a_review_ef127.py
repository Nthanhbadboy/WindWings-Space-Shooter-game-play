"""R1/123 fixed127 null-domain execution and prerequisite-wording review.
provenance: arena/8141386a-windwings-space-shooter-game-p
Own fresh original bytes and separate guarded path; published128/129 are text-only
supersession context, not new native/serialized audits or #27-full acceptance.
"""
from __future__ import annotations

import argparse
import gzip
import json
import struct
import subprocess

from tools.verify.geometry_8141386a_atlas_io import ROOT, BRANCH, canonical, sha, sha_file
from tools.verify.geometry_8141386a_review_ef127_checks import blob_id, decode_word, normalize, quote
from tools.verify.l3_geometry_8141386a_review_ef127_native import RAW, GB, CLEANUP, FREE, EPILOGUE, RET, SOURCE_HEAD, SOURCE_RUN, VARIANTS, replay, read

OUTPUT=ROOT/'datas/l3_geometry_review_ef127_8141386a.json.gz'
SCI='6781d828f6e283d11e6508c051e3000df233714c'
REPORT='f1d35dd7a69b355f6d824527b74bfc368781f3be'
CONTEXT128='34a97a99211de059e21cfcc08635791d1b94a5e0'
CONTEXT129='2c710a7c20c123a65db45ddeca1f18c0807abe02'
PEER_SHA='8b9df00387893418d21608ddda6d7287c5c313ecd213770091b60720370f344e'
PROBE_SHA='43adb19f62684262066e4ca71bec636b87e3e5bf0d2a06946de65e24c77fe2e1'
CALLEES={0x6ceeb0:0x6cef64,0xb98c98:0xb98d6c,0xb98db4:0xb98fc8,
         0xb99120:0xb9944c,0x6f15cc:0x6f16bc,0x6cff44:0x6d006c}


def validate_pins(manifest=None):
    m=manifest if manifest is not None else json.loads((RAW/'peer-pins.json').read_bytes())
    if (m['item'],m['provenance'],m['claim'],m['scientific_commit'],m['report_commit'])!=(123,BRANCH,6427652461,SCI,REPORT):
        raise ValueError('fixed127 review target changed')
    if len(m['pins'])!=8 or len({p['snapshot'] for p in m['pins']})!=8:
        raise ValueError('fixed127 selected-source coverage changed')
    for p in m['pins']:
        if p['commit'] not in (SCI,REPORT,CONTEXT128,CONTEXT129):
            raise ValueError('unselected peer source commit')
        is_context=p['role']=='published_text_only_not_native_verification'
        if (p['commit'] in (CONTEXT128,CONTEXT129))!=is_context:
            raise ValueError('published context was promoted to native source')
        data=(ROOT/p['snapshot']).read_bytes()
        if len(data)!=p['size'] or sha(data)!=p['sha256']:
            raise ValueError('selected127 source snapshot changed')
        original=data if p['encoding']=='gzip-as-source'else gzip.decompress(data)
        if sha(original)!=p['source_sha256'] or blob_id(original)!=p['git_blob']:
            raise ValueError('selected127 source/Git blob identity changed')
    if sha_file(RAW/'peer-artifact127.json.gz')!=PEER_SHA or sha_file(RAW/'peer-probe127.json.gz')!=PROBE_SHA:
        raise ValueError('fixed127 scientific artifact/raw changed')
    return m


def verify_git(fetch=False):
    pins=validate_pins()['pins']
    for head in sorted({p['commit'] for p in pins}):
        exists=subprocess.run(['git','-C',str(ROOT),'cat-file','-e',head+'^{commit}'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
        if not exists:
            if not fetch:raise ValueError('missing selected commit; explicit --fetch required')
            subprocess.run(['git','-C',str(ROOT),'fetch','--no-tags','--depth=1','--filter=blob:none','origin',head],check=True)
    for p in pins:
        b=subprocess.check_output(['git','-C',str(ROOT),'show',p['commit']+':'+p['path']])
        if sha(b)!=p['source_sha256'] or blob_id(b)!=p['git_blob']:
            raise ValueError('actual fixed127/context Git bytes differ: '+p['path'])
    return len(pins)


def static_audit(peer,probe,fresh):
    requested={(w['va'],len(w['hex'])//2):w['hex'] for w in probe['windows']+probe['cells']}
    actual={(w['va'],w['size']):w['hex'] for w in fresh['peer_selected_spans']}
    if actual!=requested or len(actual)!=104 or len(fresh['peer_selected_spans'])!=104:
        raise ValueError('fresh104-span original127 coverage differs')
    image={}
    for w in fresh['peer_selected_spans']:
        b=bytes.fromhex(w['hex'])
        if sha(b)!=w['sha256'] or len(b)!=w['size']:raise ValueError('fresh127 span digest/size differs')
        for i,v in enumerate(b):
            a=w['va']+i
            if a in image and image[a]!=v:raise ValueError('original127 overlap conflict')
            image[a]=v
    def word(pc):return struct.unpack('<I',bytes(image[pc+i] for i in range(4)))[0]
    fdes={f['start']:f for f in fresh['selected_fdes']}
    claimed={r['entry']:r['unwind'] for r in probe['followed'] if r['unwind'] is not None}
    if set(fdes)!=set(claimed) or len(fdes)!=37:
        raise ValueError('fresh37 original FDE coverage differs')
    if fresh['bounded_non_fde_entries']!=[0x109acc0,0x109ace0]:
        raise ValueError('bounded PLT windows confused with function extents')
    for a,f in fdes.items():
        c=claimed[a]
        if (f['end_exclusive'],f['fde_va'],f['fde_hex'],f['table_va'],f['table_hex'])!=(c['end'],c['fde_va'],c['fde_hex'],c['table_va'],c['table_hex']):
            raise ValueError('original127 FDE/table equality differs')
        delta,size=struct.unpack_from('<iI',bytes.fromhex(f['fde_hex']),8)
        if f['fde_va']+8+delta!=a or a+size!=f['end_exclusive']:
            raise ValueError('original127 FDE arithmetic differs')
    callees=[];return_discrepancies=[]
    for a,end in CALLEES.items():
        reported=peer['graph_builder']['callees'][hex(a)]
        if fdes[a]['end_exclusive']!=end or reported!={'fde_end':end,'ret':end-4}:
            raise ValueError('fixed six-callee FDE/reported-metadata snapshot changed')
        # R1 finding6427990146: end-4 is a stack-check BL, not RET, for b98c98.
        # Preserve the original incorrect claim and classify it as DRIFT. Do not
        # rewrite peer evidence or turn a non-RET into a passing RET expectation.
        actual_ret=0xb98d64 if a==0xb98c98 else end-4
        if word(actual_ret)!=0xd65f03c0:
            raise ValueError('actual original callee RET word differs')
        decoded=decode_word(word(reported['ret']),reported['ret'])
        status='MATCH'if reported['ret']==actual_ret else'CONFIRMED_RETURN_PC_METADATA_DRIFT'
        row=dict(entry=a,end_exclusive=end,published_ret_pc=reported['ret'],actual_ret_pc=actual_ret,
            actual_ret_word_hex=struct.pack('<I',word(actual_ret)).hex(),published_ret_word_hex=struct.pack('<I',word(reported['ret'])).hex(),
            published_ret_actual_decode=decoded,status=status,
            execution='EXECUTED_NULL_CLEANUP_ONLY'if a==CLEANUP else'STATIC_ONLY_NOT_EXECUTED')
        callees.append(row)
        if status!='MATCH':return_discrepancies.append(row)
    if len(return_discrepancies)!=1 or return_discrepancies[0]['entry']!=0xb98c98 or return_discrepancies[0]['published_ret_actual_decode']!={'kind':'BL','target':0x109acc0,'text':'bl 0x109acc0'}:
        raise ValueError('observed fixed127 return-PC discrepancy evidence changed')
    if (fdes[GB]['end_exclusive'],peer['graph_builder']['ret'],word(RET),word(0x6cff40))!=(0x6cff44,RET,0xd65f03c0,0x94272b60):
        raise ValueError('graph RET vs exclusive end/failure BL differs')
    witnesses=[]
    if len(peer['witnesses'])!=33 or len({r['pc']for r in peer['witnesses']})!=33:
        raise ValueError('33 unique instruction witnesses required')
    for w in peer['witnesses']:
        got=struct.pack('<I',word(w['pc'])).hex();d=decode_word(word(w['pc']),w['pc'])
        if got!=w['word_hex'] or normalize(d['text'])!=normalize(w['text']):
            raise ValueError('original witness bytes/own decoded operands differ')
        witnesses.append(dict(pc=w['pc'],word_hex=got,published_text=w['text'],own_decode=d))
    fields=peer['required_fields']
    if len(fields)!=11 or len({r['offset']for r in fields})!=11:
        raise ValueError('published11 field-role bookkeeping differs')
    bound=[r for r in fields if r['witness_pc']is not None]
    unbound=[r for r in fields if r['witness_pc']is None]
    if len(bound)!=6 or len(unbound)!=5 or any(r['witness_pc']not in {w['pc']for w in witnesses}for r in bound):
        raise ValueError('field roles without individual witness were promoted')
    relas={r['address']:r['addend']for r in fresh['selected_relative_relas']}
    if relas!={r['address']:r['addend']for r in probe['relocations']}or len(relas)!=11:
        raise ValueError('selected original127 RELA equality differs')
    imports=[{k:r[k]for k in ('address','name','symbol_entry_offset','symbol_hex','name_file_offset','name_hex')}for r in fresh['imports']]
    if imports!=probe['imports'] or len(imports)!=56:
        raise ValueError('selected original127 import identity differs')
    for r in imports:
        if bytes.fromhex(r['name_hex'])!=r['name'].encode()+b'\0':raise ValueError('original import string bytes differ')
    entry_call=decode_word(word(0x6cf7e4),0x6cf7e4);free_call=decode_word(word(0x6cef44),0x6cef44)
    if (entry_call['kind'],entry_call['target'],free_call['kind'],free_call['target'])!=('BL',CLEANUP,'BL',FREE):
        raise ValueError('original cleanup/null-deallocator BL targets differ')
    return dict(fresh_spans=104,fresh_fdes=37,bounded_non_fde_entries=fresh['bounded_non_fde_entries'],
        selected_relative_relas=11,selected_imports=56,six_callees=callees,confirmed_return_pc_discrepancies=return_discrepancies,graph_fde_end_exclusive=0x6cff44,
        graph_ret_pc=RET,graph_failure_bl_pc=0x6cff40,graph_fde_instruction_words=484,cleanup_fde_instruction_words=45,
        witnesses=witnesses,published_field_roles=fields,field_roles_with_individual_witness=6,field_roles_without_individual_witness=5,
        extra_callsite_decodes=[dict(pc=0x6cf7e4,decode=entry_call),dict(pc=0x6cef44,decode=free_call)],
        boundary='Original selected bytes/table extents and33 bounded word decodes, not semantic sufficiency of11 field roles or non-null build-path/whole-program coverage.37 FDEs plus2 bounded PLT entries are not39 complete functions.')


def context_audit(manifest,plan=None):
    plan=plan if plan is not None else json.loads((RAW/'context-review.json').read_bytes())
    if (plan['item'],plan['provenance'],plan['authority'])!=(123,BRANCH,'MANUAL_PUBLISHED_TEXT_RECONCILIATION_NOT_NATIVE_OR_SERIALIZED_VERIFICATION'):
        raise ValueError('published context evidence grade changed')
    if [r['id']for r in plan['entries']]!=['M1','M2','M3','M4','M5']or [r['id']for r in plan['precision_notes']]!=['Q1','Q2']:
        raise ValueError('prerequisite/precision review coverage differs')
    pins={p['snapshot'].rsplit('/',1)[-1]:p for p in manifest['pins']};seen=[]
    result=dict(authority=plan['authority'],limit=plan['limit'],entries=[],precision_notes=[])
    for group in ('entries','precision_notes'):
        for row in plan[group]:
            r={k:v for k,v in row.items()if k!='selectors'};r['citations']=[]
            for s in row['selectors']:
                if s['source']not in ('peer-report127.md.gz','context-report128.md.gz','context-report129.md.gz'):
                    raise ValueError('unselected published text source')
                p=pins[s['source']];text=gzip.decompress((ROOT/p['snapshot']).read_bytes()).decode()
                c=quote(p,text,s['needle'],s.get('before',0),s.get('after',0));r['citations'].append(c)
                seen.append((c['commit'],c['path'],c['start_line'],c['end_line'],c['quote_sha256']))
            if not r['citations']:raise ValueError('missing exact published source citation')
            result[group].append(r)
    if len(seen)!=17 or len(set(seen))!=17:raise ValueError('17 distinct published quote receipts required')
    result['exact_citations']=len(seen)
    result['classification_is_human_not_machine_truth']=True
    return result


def replay_audit(peer):
    if len(peer['cases'])!=3:raise ValueError('canonical three-case producer coverage differs')
    rows=[]
    for (prefill,base),old in zip(VARIANTS,peer['cases']):
        r=replay(prefill,base)
        if (old['prefill'],old['base'])!=(prefill,base):raise ValueError('canonical variant ordering differs')
        if r['native_instruction_count']!=old['run']['instruction_count']or r['native_instruction_count']!=51 or r['executed_addresses']!=old['run']['executed_addresses']:
            raise ValueError('own original127 PC-set/count differs')
        if any(r['pc_counts'].get(pc,0)!=n for pc,n in old['pc_hits'].items()):raise ValueError('own original127 PC multiplicity differs')
        node=r['addresses']['node']
        if {k:r['node_after'][k]for k in old['node_after']}!=old['node_after']:
            raise ValueError('own original127 canonical node effects differ')
        if (r['last_native_pc'],r['return_value'],r['stack_pointer_after'])!=(old['ret'],old['run']['return_value'],old['stack_pointer_after']):
            raise ValueError('own original127 return/stack protocol differs')
        services=[{k:s[k]for k in ('symbol','object','category')}for s in r['service_calls']]
        if services!=old['service_calls']or len(services)!=1 or services[0]['object']!=0:
            raise ValueError('own null-deallocator boundary differs')
        if r['host_pc_writes']!=[dict(origin='SYNTHETIC_FREE_RETURN_TO_ORIGINAL_LR',from_pc=FREE,to_pc=0x6cef48)]or r['emu_start_calls']!=1 or r['entry_count']!=1:
            raise ValueError('entry staging or unapproved host PC write')
        expected_edges=[(0x6cf7e4,CLEANUP),(0x6ceec8,0x6ceee8),(0x6ceef0,0x6cef30),(0x6cef60,0x6cf7e8),(0x6cf7ec,EPILOGUE)]
        if [(e['from_pc'],e['to_pc'])for e in r['original_nonsequential_edges']]!=expected_edges:
            raise ValueError('original selected control-flow transitions differ')
        writes=[(w['pc'],w['address']-node,w['size'],w['value'])for w in r['native_memory_writes']if w['tier']=='PREPARED_NODE']
        if writes!=[(0x6cef48,0x1c0,8,0),(0x6cef4c,0x1c8,4,0)]:
            raise ValueError('native127 node zero stores differ')
        for key in ('slot118','slot1a0','category_c8','slot128','slot130','slot138','slot140','slot180'):
            if r['node_before'][key]!=r['node_after'][key]:raise ValueError('untouched prefill was promoted to native clear')
        if r['body_coverage'][hex(GB)]['executed_unique']!=28 or r['body_coverage'][hex(CLEANUP)]['executed_unique']!=23:
            raise ValueError('selected path vs complete-body coverage differs')
        if any(0x6cf7f0<=pc<EPILOGUE or pc==FREE or pc==0x6cff40 for pc in r['executed_addresses']):
            raise ValueError('non-null build/heap/failure path was counted')
        if len(r['canary_checks'])!=1 or r['canary_checks'][0]['tls_value']!=r['canary_checks'][0]['saved_value'] or r['callee_saved_before']!=r['callee_saved_after']:
            raise ValueError('original selected epilogue preservation differs')
        rows.append(r)
    if any(r['pc_counts']!=rows[0]['pc_counts']for r in rows):raise ValueError('canonical variant PC multiplicities differ')
    return rows


def build():
    m=validate_pins();peer=read('peer-artifact127.json.gz');probe=read('peer-probe127.json.gz');fresh=read('fresh-original.json.gz');ci=read('source-ci-receipt.json.gz')
    r=ci['run']
    if (r['id'],r['head_sha'],r['status'],r['conclusion'])!=(SOURCE_RUN,SOURCE_HEAD,'completed','success')or ci['fresh_original_sha256']!=sha_file(RAW/'fresh-original.json.gz'):
        raise ValueError('own fresh-source exact-head GREEN receipt differs')
    r=ci['peer_verify_run']
    if (r['head_sha'],r['status'],r['conclusion'])!=(SCI,'completed','success'):
        raise ValueError('producer127 actual scientific Verify differs')
    for path,digest in fresh['tool_pins'].items():
        if sha_file(ROOT/path)!=digest:raise ValueError('fresh127 collector/parser/input pins changed')
    for p in m['pins']:
        if p['path']in peer['inputs']and p['source_sha256']!=peer['inputs'][p['path']]:raise ValueError('selected producer input pin differs')
    static=static_audit(peer,probe,fresh);context=context_audit(m);rows=replay_audit(peer)
    paths=[p['snapshot']for p in m['pins']]+[str((RAW/n).relative_to(ROOT))for n in ('peer-pins.json','fresh-original.json.gz','source-ci-receipt.json.gz','context-review.json')]
    paths+=['tools/verify/l3_geometry_8141386a_review_ef127.py','tools/verify/l3_geometry_8141386a_review_ef127_native.py',
        'tools/verify/geometry_8141386a_review_ef127_checks.py','tools/verify/geometry_8141386a_review_ef123_checks.py',
        'tools/recovery/geometry_8141386a_review_ef127_bytes.py','tools/recovery/geometry_8141386a_review_ef123_bytes.py']
    return dict(schema=1,item=123,provenance=BRANCH,claim=6427652461,
        verdict='SUPPORT_EF127_NULL_ENTRY_RET_ONLY_CALLEE_RET_METADATA_CORRECTION_PENDING_NOT_27_FULL',
        target=dict(scientific_commit=SCI,report_commit=REPORT,artifact_sha256=PEER_SHA,raw_sha256=PROBE_SHA),
        original_source=dict(run=SOURCE_RUN,source_head=SOURCE_HEAD,raw_commit=ci['preserved_raw_commit'],
            fresh_original_sha256=sha_file(RAW/'fresh-original.json.gz'),xapk_sha256=fresh['xapk_sha256'],libunity_sha256=fresh['libunity_sha256']),
        static_audit=static,published_context_reconciliation=context,canonical_own_native_replays=rows,
        counts=dict(canonical_native_cases=3,native_instructions=[r['native_instruction_count']for r in rows],
            canonical_native_instruction_sum=sum(r['native_instruction_count']for r in rows),null_deallocator_sinks=3,
            original_graph_unique_words_per_case=28,original_graph_fde_words=484,original_cleanup_unique_words_per_case=23,original_cleanup_fde_words=45,
            fresh_spans=104,fresh_fdes=37,bounded_non_fde_windows=2,static_callees=6,callees_executed=1,word_witnesses=33,
            published_field_roles=11,field_roles_with_individual_witness=6,field_roles_without_individual_witness=5,
            missing_x_labels_reconciled=5,published_text_citations=17,new_canonical_numeric_contradictions=0,confirmed_published_return_pc_discrepancies=1),
        independence='Own fresh streamed original ELF capture and separate guarded fresh-span-only Unicorn harness; no producer graph127/Fixture imports/execution. Shared original build, frozen own119 ELF reader/integer branch arithmetic, Unicorn2.1.4 and selected span/node-TLS-stack protocol. Explicit nonzero callee-saved register sentinels add preservation checks, not game-state evidence.',
        limits=['Fixed127 has one confirmed return-PC metadata error: b98d68 is BL stack-check, actual RET is b98d64. Original drift is retained; producer correction is required before approving that label.51-instruction execution and FDE ends are unaffected.',
            'One uninterrupted original entry-to-RET selected path with a declared null-deallocator LR return, not full instruction coverage. Only null+118/+1a0/+1c0 and zero+1c8 on three explicit prefill/base variants.',
            'Only two native node stores: +1c0/+1c8. Other output fields can remain A5; prepared0 is not a native clear. 6ceeb0 runs; the other five listed callees do not.',
            '33 machine words/operands and37 selected FDEs checked, not semantic completeness/sufficiency of the11-role or M1-M5 maps. Two PLT windows are bounded captures, not function extents.',
            '128/129 are full published text snapshots only. M2a availability, M1a registry/linkage and class/serialized counts are not independently reverified here; no global absence or sufficiency of runtime objects is inferred.',
            'No original deallocator/heap, non-null graph/owner/motion object, serialized game instance, playback, scheduling/dispatch/clock/pose/apply/Unity readback/render/runtime or #27-full acceptance.',
            'No frozen118-122 scientific edits, old receipt regeneration, producer/peer cross-edit, lane takeover, budget escalation or selfACK. Review-queue completion is not implementation/runtime completion.'],
        source_pins={p:sha_file(ROOT/p)for p in sorted(paths)})


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');p.add_argument('--git',action='store_true');p.add_argument('--fetch',action='store_true');a=p.parse_args()
    if a.fetch and not a.git:p.error('--fetch requires --git')
    v=build();b=gzip.compress(canonical(v)+b'\n',mtime=0)
    if a.check:
        if OUTPUT.read_bytes()!=b:raise SystemExit('own ef127 artifact drift')
    else:OUTPUT.write_bytes(b)
    if a.git:print('PASS actual fixed target/context Git source identities:',verify_git(a.fetch))
    print(v['verdict'],v['counts']);print('artifact',len(b),'SHA256',sha(b))


if __name__=='__main__':main()
