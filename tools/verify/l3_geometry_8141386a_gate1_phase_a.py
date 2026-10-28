"""Independent Gate1 Phase-A package review, not Phase-A self-acceptance.
provenance: arena/8141386a-windwings-space-shooter-game-p
AST-only whole declaration catalogue + bounded published-source conflicts/quotes.
Archived producer code stays inert. No raw/native/device/gameplay verification or
implementation is substituted for the stated publication/acceptance review scope.
"""
from __future__ import annotations
import argparse
import ast
from collections import Counter,defaultdict
import gzip
import json
from pathlib import Path
import re
import subprocess
from tools.verify.geometry_8141386a_atlas_io import ROOT,BRANCH,canonical,sha,sha_file
from tools.verify.geometry_8141386a_review_ef127_checks import blob_id,quote

RAW=ROOT/'reverse-engineering/raw/geometry-8141386a/gate1-phase-a'
OUTPUT=ROOT/'datas/l3_geometry_gate1_phase_a_8141386a.json.gz'
SPEC='12ccdc52006f898c6e67260910af23df18840c40'
AI4='22a94737713e1509dcf983e6d4b83ed6c30773f4'
CLAIM=6439774919
LABELS={'STATIC_CONFIRMED','RUNTIME_CONFIRMED','INFERRED','RUNTIME_UNVERIFIED','UNKNOWN','CONFLICTING'}
COMMENTS={'director-assignment':6439014055,'director-user-mandate':6438617060,
          'spec-ack124':6438111504,'producer-numeric-table':6370275480}


def unpack(path):
    b=path.read_bytes()
    if len(b)>2_000_000:raise ValueError('snapshot exceeds bounded compressed source budget')
    with gzip.open(path,'rb')as handle:
        data=handle.read(2_000_001)
    if len(data)>2_000_000:raise ValueError('snapshot exceeds bounded decoded source budget')
    return data


def sources(manifest=None):
    m=json.loads((RAW/'peer-pins.json').read_bytes())if manifest is None else manifest
    if (m['item'],m['provenance'],m['claim'],m['spec_commit'],m['ai4_commit'])!=(125,BRANCH,CLAIM,SPEC,AI4):
        raise ValueError('fixed Gate1 source identity changed')
    if len(m['pins'])!=61 or len({p['snapshot']for p in m['pins']})!=61:
        raise ValueError('complete61-source corpus coverage changed')
    out={}
    for p in m['pins']:
        if p['commit']not in(SPEC,AI4):raise ValueError('unselected source commit')
        path=ROOT/p['snapshot'];packed=path.read_bytes();data=unpack(path)
        if len(packed)!=p['snapshot_size']or sha(packed)!=p['snapshot_sha256']:
            raise ValueError('Gate1 snapshot compressed identity differs')
        original=packed if p['encoding']=='gzip-as-source'else data
        if len(original)!=p['source_size']or sha(original)!=p['source_sha256']or blob_id(original)!=p['git_blob']:
            raise ValueError('Gate1 original source/Git identity differs')
        out[Path(p['snapshot']).name]=dict(pin=p,data=data)
    return m,out


def comments():
    out={}
    for name,ident in COMMENTS.items():
        path=RAW/(name+'.json.gz');v=json.loads(unpack(path))
        if v['id']!=ident or v['html_url']!=f'https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-{ident}':
            raise ValueError('published comment identity differs')
        out[name]=v
    return out


def declarations(text):
    """Literal/AST catalogue only; never compile, import, eval or execute peer code."""
    tree=ast.parse(text);const={};definitions=defaultdict(list)
    for n in tree.body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):definitions[n.name].append(n)
        if isinstance(n,ast.Assign):
            try:value=ast.literal_eval(n.value)
            except (ValueError,TypeError):continue
            for target in n.targets:
                if isinstance(target,ast.Name):const[target.id]=value
    def literal(n):
        if isinstance(n,ast.Name)and n.id in const:return const[n.id]
        return ast.literal_eval(n)
    calls=sorted((n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='claim'),key=lambda n:n.lineno)
    top={id(n.value)for n in tree.body if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='claim'}
    if any(id(n)not in top for n in calls):raise ValueError('unsupported nested/conditional claim registration; not executed or guessed')
    lines=text.splitlines(keepends=True);occurrences=Counter();rows=[]
    for ordinal,n in enumerate(calls,1):
        if len(n.args)<5:raise ValueError('unsupported claim registration shape')
        cid,doc,anchor,stated=[literal(a)for a in n.args[:4]]
        if not isinstance(cid,str)or not isinstance(doc,str)or not isinstance(anchor,str):raise ValueError('nonliteral claim identity/anchor')
        note=literal(n.args[5])if len(n.args)>5 else'';occurrences[cid]+=1
        q=''.join(lines[n.lineno-1:n.end_lineno]);expr=ast.get_source_segment(text,n.args[4]);binding=None
        if isinstance(n.args[4],ast.Name):
            prior=[d for d in definitions[n.args[4].id]if d.lineno<n.lineno]
            if prior:
                d=prior[-1];binding=dict(name=d.name,start_line=d.lineno,end_line=d.end_lineno,
                    source_sha256=sha(''.join(lines[d.lineno-1:d.end_lineno]).encode()),semantics='FUNCTION_OBJECT_BOUND_AT_REGISTRATION_NOT_EXECUTED')
        rows.append(dict(row=ordinal,row_key=f'{cid}#{occurrences[cid]}',id=cid,occurrence=occurrences[cid],doc=doc,
            line_has=anchor,stated=stated,stated_python_type=type(stated).__name__,note=note,
            source_start_line=n.lineno,source_end_line=n.end_lineno,source_quote=q,source_quote_sha256=sha(q.encode()),
            measure_expression=expr,measure_ast_kind=type(n.args[4]).__name__,direct_function_binding=binding,
            binding_limit='Lambda globals/factory closures are not dynamically traced; no complete input provenance inferred.',
            independent_raw_remeasurement=False,review_status='DECLARATION_CATALOGUED_NOT_RAW_OR_RUNTIME_ACCEPTANCE'))
    if len(rows)!=211 or len(occurrences)!=209 or {k:v for k,v in occurrences.items()if v>1}!={'GE1':2,'GE2':2}:
        raise ValueError('full211-row/209-ID declaration coverage differs')
    return rows


def join_report(rows,body):
    reported=[]
    for n,line in enumerate(body.splitlines(),1):
        m=re.match(r'^(\S+)\s+(PASS|FAIL|SKIP|ERROR)\s+(.*)$',line)
        if m:reported.append(dict(id=m.group(1),status=m.group(2),tail=m.group(3),quote=line,
            quote_sha256=sha(line.encode()),comment_line=n))
    if len(reported)!=len(rows)or[r['id']for r in reported]!=[r['id']for r in rows]:
        raise ValueError('reported table cannot be joined to every declared row by ordinal/CID')
    if Counter(r['status']for r in reported)!=Counter(PASS=209,SKIP=2):raise ValueError('reported209/0/2 evaluation counts differ')
    by_id=defaultdict(set);joined=[]
    for r,p in zip(rows,reported):
        by_id[r['id']].add(p['status']);joined.append(dict(**r,reported_result=p,
            report_binding='ORDINAL_AND_ID_ONLY_MUTABLE_UPSERT_NOT_EXACT_INPUT_HEAD_MANIFEST'))
    unique=Counter(next(iter(s))if len(s)==1 else'MIXED'for s in by_id.values())
    if unique!=Counter(PASS=207,SKIP=2)or[r['id']for r in reported if r['status']=='SKIP']!=['B9','F4']:
        raise ValueError('distinct-ID or intentional missing-source scope differs')
    return joined,dict(evaluation_rows=211,unique_ids=209,reported_status_counts=dict(Counter(r['status']for r in reported)),
        distinct_id_status_counts=dict(unique),duplicate_ids={'GE1':2,'GE2':2},skipped_ids=['B9','F4'],
        target_document_paths=len({r['doc']for r in rows}),binding='SUPPLIED_PUBLISHED_TABLE_NOT_INDEPENDENT_MEASUREMENT_OR_IMMUTABLE_RUN_BINDING')


def locate(selector,src,pubs):
    name=selector['source'];needle=selector['needle'];before=selector.get('before',0);after=selector.get('after',0)
    if name.startswith('comment:'):
        v=pubs[name[8:]];text=v['body'];pin=dict(commit='API_COMMENT_'+str(v['id']),path='PR12/comment/'+str(v['id']),source_sha256=sha(text.encode()))
        c=quote(pin,text,needle,before,after);c.update(kind='PUBLISHED_API_COMMENT',comment_id=v['id'],url=v['html_url'])
    else:
        s=src[name];c=quote(s['pin'],s['data'].decode(),needle,before,after);c['kind']='FIXED_GIT_SOURCE'
    c['evidence_grade']='SOURCE_IDENTITY_AND_PUBLISHED_ASSERTION_ONLY_NOT_FRESH_RAW_NATIVE_RUNTIME_TRUTH'
    return c


def review_plan(src,pubs,plan=None):
    plan=json.loads((RAW/'review-map.json').read_bytes())if plan is None else plan
    if (plan['item'],plan['provenance'],plan['claim'])!=(125,BRANCH,CLAIM):raise ValueError('Gate1 human review identity differs')
    if len(plan['findings'])!=8 or len(plan['preserved_boundaries'])!=5 or len(plan['domain_matrix'])!=16:
        raise ValueError('complete acceptance finding/domain coverage differs')
    result={k:v for k,v in plan.items()if k not in('findings','preserved_boundaries','domain_matrix')};citations=[]
    for group in ('findings','preserved_boundaries','domain_matrix'):
        out=[]
        for row in plan[group]:
            label=row.get('label',row.get('evidence_label'))
            if label not in LABELS:raise ValueError('unknown mandate evidence label')
            r={k:v for k,v in row.items()if k!='selectors'}
            r['citations']=[locate(s,src,pubs)for s in row['selectors']]
            if not r['citations']:raise ValueError('uncited human acceptance assertion')
            citations.extend(r['citations']);out.append(r)
        result[group]=out
    blocking=[r for r in result['findings']if r['blocking']]
    if len(blocking)!=5 or {r['condition']for r in blocking}!={r['id']for r in result['blocking_conditions']}:
        raise ValueError('every blocking finding needs one explicit owner/exit condition')
    if any(r['independent_remeasurement']for r in result['domain_matrix']):raise ValueError('publication review promoted to fresh measurement')
    if any(r['evidence_label']=='RUNTIME_CONFIRMED'and'HISTORICAL_CROSS_BUILD_ONLY'not in r['applicability']for r in result['domain_matrix']):
        raise ValueError('historical runtime evidence promoted to same-build target parity')
    verdict='NOT_READY'if blocking else'READY_FOR_GATE1'
    if result['verdict']!=verdict:raise ValueError('human verdict/blocking list is inconsistent')
    result['quote_receipt_count']=len(citations)
    result['machine_semantic_acceptance_proof']=False
    result['user_gate_approval']=False
    return result


def published_conflict(src):
    a=json.loads(src['ai4-l2_535b0541_pvp_hunter_arrays.json.gz']['data'])
    b=json.loads(src['ai4-l2_535b0541_pvp_reward_arrays.json.gz']['data'])
    rows={r['field'].split('.')[-1]:r for r in a['arrays']}
    data=[dict(field=n,constructor_rva=19796420,offset=rows[n]['instance_offset'],
        artifact149_values=rows[n]['values'],artifact169_field=b['fields'][hex(rows[n]['instance_offset'])])for n in ('rewardValues','rewardScales')]
    if [r['offset']for r in data]!=[416,424]or data[0]['artifact149_values']!=[100,10000,10,100,10,10]:
        raise ValueError('published conflict field/array context differs')
    pa={r['path']:r['sha256']for r in a['provenance']['sources']}
    pb={r['path']:r['sha256']for r in b['provenance']['inputs']+b['provenance']['slices']}
    common={p:h for p,h in pa.items()if pb.get(p)==h}
    required={'reverse-engineering/il2cpp/field-defaults.json','reverse-engineering/il2cpp/dump.cs.gz',
              'reverse-engineering/raw/key-grant-535b0541/native.json.gz','reverse-engineering/raw/arena-pvp-535b0541/native.json.gz'}
    if not required<=set(common):raise ValueError('declared shared input identity context differs')
    if b['totals']['float_candidates']!=4 or len(b['blobs']['unclaimed_floats'])!=4:
        raise ValueError('169 unbound-candidate publication context differs')
    return dict(status='UNRECONCILED_PUBLISHED_CONFLICT_NO_WINNER_SELECTED',fields=data,
        shared_declared_input_sha256=common,artifact169_float_candidates=4,
        boundary='Comparing published result records and their declared common source digests, NOT rehashing raw inputs or independently proving either token/blob derivation.177 narrows build-vs-server scope but still says NOT_BOUND.')


def verify_git(fetch=False):
    m,_=sources()
    for head in sorted({p['commit']for p in m['pins']}):
        ok=subprocess.run(['git','-C',str(ROOT),'cat-file','-e',head+'^{commit}'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
        if not ok:
            if not fetch:raise ValueError('missing selected commit; explicit --fetch required')
            subprocess.run(['git','-C',str(ROOT),'fetch','--no-tags','--depth=1','--filter=blob:none','origin',head],check=True)
    for p in m['pins']:
        data=subprocess.check_output(['git','-C',str(ROOT),'show',p['commit']+':'+p['path']])
        if sha(data)!=p['source_sha256']or blob_id(data)!=p['git_blob']:raise ValueError('actual Gate1 Git bytes differ: '+p['path'])
    return len(m['pins'])


def build():
    m,src=sources();pubs=comments();decl=declarations(src['spec-tools__verify-claims.py.gz']['data'].decode())
    catalogue,counts=join_report(decl,pubs['producer-numeric-table']['body']);plan=review_plan(src,pubs)
    available={p['path']for p in m['pins']if p['commit']==SPEC}
    if not {r['doc']for r in catalogue}<=available:raise ValueError('one of36 complete claim-target docs was omitted')
    ids={r['id']for r in catalogue}
    if any(cid not in ids for f in plan['findings']for cid in f['claim_ids']):raise ValueError('finding links to undeclared claim ID')
    meta=json.loads(unpack(RAW/'current-ci-pr-metadata.json.gz'));run=meta['spec_run'];pr=meta['pr16']
    if (run['id'],run['head_sha'],run['status'],run['conclusion'])!=(40483833755,SPEC,'completed','success'):
        raise ValueError('actual current spec CI identity/status differs')
    if pr['number']!=16 or pr['headRefOid']!=AI4 or pr['state']!='OPEN'or not pr['isDraft']:
        raise ValueError('PR16 draft vehicle metadata differs')
    conflict=published_conflict(src)
    audit=json.loads(src['ai4-l2_535b0541_open_items_audit.json.gz']['data'])
    paths=[p['snapshot']for p in m['pins']]+[str((RAW/n).relative_to(ROOT))for n in ('peer-pins.json','review-map.json','current-ci-pr-metadata.json.gz')]
    paths += [str((RAW/(n+'.json.gz')).relative_to(ROOT))for n in COMMENTS]
    paths += ['tools/verify/l3_geometry_8141386a_gate1_phase_a.py','tools/verify/geometry_8141386a_review_ef127_checks.py',
        'reverse-engineering/raw/geometry-8141386a/scientific-ci-124.json.gz']
    return dict(schema=1,item=125,provenance=BRANCH,claim=CLAIM,verdict=plan['verdict'],spec_commit=SPEC,ai4_commit=AI4,
        scope='Independent acceptance-style publication/package review only; not selfACK of PhaseA, Gate1 user approval, implementation permission or new raw/native/runtime measurement.',
        claim_catalogue=catalogue,claim_catalogue_counts=counts,published_result_comment=dict(id=6370275480,updated_at=pubs['producer-numeric-table']['updated_at'],body_sha256=sha(pubs['producer-numeric-table']['body'].encode())),
        acceptance_review=plan,published_reward_conflict=conflict,
        registry_publication=dict(snapshot_sha256=sha_file(RAW/'ai4-l2_535b0541_open_items_audit.json.gz'),summary=audit.get('totals',audit.get('counts',{})),scope='Pinned published snapshot, not a latest-all-work closure or fresh semantic/raw verification.'),
        actual_ci_metadata=dict(run=40483833755,head=SPEC,status='success',ci_test_count=None,source_binding='Exact spec CI head verified; mutable numeric table is separately supplied and NOT an immutable per-input run receipt.'),
        pr16_metadata=dict(head=AI4,state='OPEN',is_draft=True,merge_or_acceptance_inferred=False,body_is_historical_vehicle=True),
        counts=dict(selected_complete_source_snapshots=61,declared_registration_rows=211,distinct_claim_ids=209,
            reported_pass_evaluations=209,reported_skip_evaluations=2,distinct_reported_pass_ids=207,
            findings=8,blocking_findings=5,preserved_boundaries=5,domain_rows=16,exact_quote_receipts=plan['quote_receipt_count'],
            independently_rerun_producer_claims=0,new_native_cases=0,new_runtime_measurements=0,new_original_source_capture=0),
        limits=plan['review_limits']+['Own historical-support209/0/2 remains compatibility evidence against its frozen snapshot, not the current producer211-row stream or PhaseA/native/runtime acceptance.',
            'No guarantee of finding every overclaim in the entire repository: the complete declaration stream and61 selected full snapshots bound the evidence; identified unresolved counterexamples suffice for NOT_READY.'],
        source_pins={p:sha_file(ROOT/p)for p in sorted(set(paths))})


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');p.add_argument('--git',action='store_true');p.add_argument('--fetch',action='store_true');a=p.parse_args()
    if a.fetch and not a.git:p.error('--fetch requires --git')
    v=build();b=gzip.compress(canonical(v)+b'\n',mtime=0)
    if a.check:
        if OUTPUT.read_bytes()!=b:raise SystemExit('Gate1 review artifact drift')
    else:OUTPUT.write_bytes(b)
    if a.git:print('PASS actual selected Gate1 Git source identities:',verify_git(a.fetch))
    print(v['verdict'],v['counts']);print('artifact',len(b),'SHA256',sha(b));print('Review/check PASS is not Gate1/PhaseA user acceptance.')


if __name__=='__main__':main()
