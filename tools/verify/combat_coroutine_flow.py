"""Source-walk reconstruction of all 25 preserved player combat MoveNext bodies.

CFG is mechanical (including three byte-table BRs). Semantic recipes are a manual
native source walk anchored to preserved instructions, NOT decompiler equivalence.
"""
import bisect
import gzip
import hashlib
import json
import re
import struct
from tools.verify.combat_argument_audit import ROOT, RAW, instructions, successors
from tools.verify.combat_rate_consumers import class_text, fields, owner_states

OUT = ROOT/'datas/combat_coroutine_flow.json'
JUMPS = RAW/'coroutine-jump-tables.json'
# role, resumed control flow. Event denotes a helper invocation, not a hit.
RECIPES = {
'10.AttackMainCannon': ('emission_loop','On entry choose 1/2/3 rounds for rank<3/==3/>3, initialize ignored-enemy list and i=0. Each round acquires enemy via GetEnemy(radius=20), runs target/fallback emitter branch, then yields Wait(0.25), including after last round. Resume increments i; stop when i>=rounds.'),
'10.IEUpdateRange': ('scale_animation','States0/1: compare squared scale distance to pool epsilon; if close return false. Otherwise set localScale=Lerp(current,scale,Clamp01(deltaTime*8)), yield null to state1 and repeat. No emitter call.'),
'11.IEMainCannonAttack': ('duration_emission_loop','Entry builds 3 Barrel descriptors; packed fields id=88017,maxRdAngle=20,rate=f32(0.04),bulletSpeed=35. EndTime=Time.time+(rank<3?f32(0.4):rank==3?1:f32(0.6)). Before each pass test now<EndTime; emit over descriptor array, yield Wait(rate), resume state1 and recheck deadline. No catch-up pass after deadline.'),
'12.SyncAttack': ('delayed_emission','State0 yields Wait(f32(0.2)) BEFORE emission. State1 tests _isLeft and matching live bullet/root lists, aborts normally when empty, otherwise executes side-dependent sync emission branch; returns false. No repeated 0.2-second firing loop.'),
'13.IEMainCannonAttack': ('launch_moving_objects','State0 uses rank-indexed parentPoints, records child positions and launches pooled main objects with MoveObject(speed=8) and callbacks; then yields null state1. State1 finishes. Movement and later callbacks are separate from this one-frame launcher.'),
'13.MoveObject': ('movement_callback','Entry sets startSlow=Time.time+1. States0/1: if speed<=0 or XY distance<=0.5, invoke required callback(objMove), return false. Otherwise MoveTowards 3D target by speed*deltaTime. After startSlow, speed=max(speed+timeScale*negative_literal,0); yield null state1 and repeat. XY arrival and 3D movement are distinct.'),
'13.ShotAllBarrels': ('paired_emission_loop','Entry computes width=owner.localScale.x/number, speed=4, rate=minNumber(owner.shotRate/number,f32(0.05)), i=0. While i<number, run two barrel-side emitter paths, yield Wait(rate); resume increments i. Wait also follows last pair; main rate is NOT the wait field. Division precedes loop guard; no invented zero clamp.'),
'14.IEMainCannonAttack': ('launch_moving_objects','State0 snapshots child positions from parentPoints[min(rank-2,2)] (no lower clamp), launches pooled objects and MoveObject; main launch call passes delayCallback=5.5. Yield null state1 then finish. Do not attribute delayCallback to the launcher yield.'),
'14.MoveObject': ('movement_delay_callback','States0/1 move _objMove toward live _target.position at _speed*deltaTime, yielding null state1 while outside XY threshold0.5. On arrival yield Wait(_delayCallback) to state2. State2 invokes required _callback(_objMove), then completes. OnDisable/return callbacks construct this with speed12 and delay0; main launch delay5.5.'),
'15.IEUpdateRange': ('scale_animation','Same scale update/control topology as implementation10: states0/1, squared-distance epsilon, Lerp Clamp01(deltaTime*8), yield null; no timed projectile emission.'),
'15.UpdateLaserPositions': ('laser_transform_update','Entry duration=Time.time+1. Before each update pass test duration>now. For each live laser/root pair, apply hold-dependent Euler/attack-point orientation then copy root position to laser; yield null state1, repeat until deadline. No WaitForSeconds and no spawn in this MoveNext.'),
'17.IEMainCannonAttack': ('staggered_emission','Entry snapshots rank-indexed child positions and initializes id88029. Iterate position array: run emitter branch; only ODD zero-based indices yield Wait(f32(0.2)) state1. Even indices increment and continue in the same MoveNext: pairs are emitted before each wait. Resume increments index. After array completion yield null state2; state2 clears stored array and completes. Empty array still reaches terminal frame yield. Do not omit final null yield.'),
'17.RotateClamp': ('rotation_oscillator','Entry initializes angle6,max7,step0.1,signedStep0.1 and Euler storage. Per resume use Time.timeScale (NOT deltaTime), add signedStep*timeScale, clamp to7 or0, flip sign at endpoint; apply opposite offset for first clamp and positive offset for later clamps atop stored base angles. Yield null state1 forever unless exception/cancelled; no firing timer.'),
'18.IESpawnHeart': ('particle_emission_toggle','State0 caches ParticleSystem.EmissionModule. States0/2 set rateOverDistance=2, yield Wait(0.5) to state1. State1 sets rateOverDistance=0, yields Wait(1) to state2. Repeat. This body does NOT call GetObject, projectile setup or enemy damage: name SpawnHeart does not establish bullet spawning.'),
'23.IEMainCannonAttack': ('launch_moving_objects','State0 snapshots rank-indexed parentPoints children, runs pooled-object setup, movement/tween operations and callback registration; yields null state1 once, then completes. Separate IEShootBarrels is the timed child emitter; do not attach that wait to this launcher.'),
'23.IEShootBarrels': ('live_child_emission_loop','Entry i=0. While i<owner.barrel.childCount (read live each round), GetChild(i), call ShootBasicBullets(child,idBlt,number,callbacks), reread childCount AFTER helper, yield Wait(owner.shotRate/float(childCount)); resume state1 increments i. Wait after final child also happens. number is forwarded emission argument, NOT wait denominator.'),
'24.IEShootBarrels': ('live_child_emission_loop','Same child traversal/timing as23, but helper is implementation24 ShootBasicBullets. Live count reread after helper; number forwarded, not denominator. No rate-field@0x9c read in this wait path.'),
'6.ControlMainCannonBullet': ('existing_projectile_control','State0 optionally yields Wait(_delay)>0 to state1, then initializes enemy exclusion list. Per-target search/reselection uses radius10 or20 based list emptiness, owner.GetEnemy and live object tests; movement toward selected enemy at15*deltaTime yields null state2; fallback movement at12*deltaTime toward saved endPos yields null state3. Resumes reset state and continue control/reselection. On invalid/arrived target increment index, clear enemy, repeat while index<owner.numberTargets and breakList is false; otherwise PoolObject and return false. Operates on passed _bltObj, not a repeated pool-spawn loop.'),
'6.SawAppear': ('one_frame_saw_setup','State0 clears saw-hidden flag, activates saw GameObject, detaches parent, sets owner rotation-speed bits to float600, calls SetSizeSaw and assigns scale(size,size,1). Yield null state1 once; state1 finishes. Not an interpolation loop.'),
'6.SawHide': ('one_frame_saw_setup','State0 sets saw-hidden flag, reparents saw to owner transform, clears rotation speed, scale=(0,0,1), yields null state1 once then finishes. No SetActive(false) call in this body.'),
'7.ControlMainCannonBullet': ('existing_projectile_control','State0 initializes attack=false/speed6 and starts attack movement toward _target, null yield state1; state1 resumes attack movement. Within distance<1 set attack=true/speed4 and Animator.SetTrigger once. At distance<=0.1 yield Wait(f32(0.35)) to state2. State2 optionally Wait(_delay)>0 to state3, then return toward owner at24*deltaTime, null yield state4. States3/4 enter return path; when within0.1 call PoolObject then required _ended, finish. _delay is AFTER attack, not initial: exact byte table proves state0 != state2.'),
'8.SawAppear': ('one_frame_saw_setup','Same saw appear control as6: activate/detach/set rotation speed600/SetSizeSaw/scale, yield one null then complete.'),
'8.SawHide': ('one_frame_saw_setup','Same saw hide control as6: hidden flag/reparent/rotation0/scale(0,0,1), one null yield then complete, not GameObject deactivation.'),
'9.ControlMainCannonBullet': ('existing_projectile_control','Same control topology as7 after address normalization: state0 attack init,1 attack loop; arrival Wait(0.35)→state2, then optional _delay→state3, return loop null→state4, PoolObject+ended on owner arrival within0.5. _delay factory exists but has no recovered direct call site in preserved methods; do not invent an external invocation schedule.'),
'9.ShipCloneAttack': ('clone_launch','State0 gets pooled clone, activates and positions/scales/orients it, sets damage field from rank multiplier and virtual damage getter, resolves Player9_Clone and calls StartAttack(duration from statics), yields null state1; state1 completes. Clone firing loop is in Player9_Clone, not repeated in this iterator.'),
}


# Exact native anchors for facts most vulnerable to timer/name/loop confusion.
ANCHORS = {
 '11.IEMainCannonAttack': {
  0x148253c: ('stp','d0, d1, [x19, #0x30]'),
  0x1482594: ('b.pl','#0x148295c'),
  0x148292c: ('ldr','s8, [x19, #0x38]')},
 '12.SyncAttack': {0x1486db8:('bl','#0x2786508'),0x1486dd8:('str','w9, [x20, #0x10]')},
 '13.ShotAllBarrels': {0x1489ee0:('fdiv','s0, s0, s1'),0x1489ee4:('fminnm','s0, s0, s2'),0x1489ee8:('str','s0, [x19, #0x38]'),0x148a17c:('cmp','w21, #2'),0x148a20c:('ldr','s8, [x19, #0x38]')},
 '14.MoveObject': {0x148d208:('bl','#0x2786508'),0x148d218:('str','w8, [x19, #0x10]'),0x148d1dc:('blr','x9')},
 '17.IEMainCannonAttack': {0x14961c4:('and','w8, w8, #0xfffffffe'),0x14961c8:('sub','w8, w9, w8'),0x14961cc:('cmp','w8, #1'),0x14961d0:('b.eq','#0x14961f4'),0x14961ec:('mov','w8, #2'),0x1496214:('bl','#0x2786508')},
 '17.RotateClamp':{0x1496308:('bl','#0x2786eb0'),0x14963f4:('str','xzr, [x19, #0x18]')},
 '18.IESpawnHeart':{0x1499aac:('bl','#0x27c2208'),0x1499ac4:('fmov','s0, #2.00000000'),0x1499ae8:('bl','#0x27c2564'),0x1499af0:('fmov','s8, #0.50000000'),0x1499b04:('fmov','s0, wzr'),0x1499b28:('bl','#0x27c2564'),0x1499b30:('fmov','s8, #1.00000000')},
 '23.IEShootBarrels':{0x14a7130:('bl','#0x14a5a84'),0x14a713c:('ldr','s8, [x20, #0xac]'),0x14a7144:('bl','#0x278a75c'),0x14a7160:('scvtf','s0, w20'),0x14a7164:('fdiv','s0, s8, s0')},
 '24.IEShootBarrels':{0x14a9288:('ldr','s8, [x20, #0xac]'),0x14a9290:('bl','#0x278a75c'),0x14a92ac:('scvtf','s0, w20'),0x14a92b0:('fdiv','s0, s8, s0')},
 '6.ControlMainCannonBullet':{0x14b3da8:('ldr','s8, [x19, #0x20]'),0x14b415c:('fmov','s0, #12.00000000'),0x14b42b4:('fmov','s0, #15.00000000')},
 '7.ControlMainCannonBullet':{0x14b6318:('mov','w9, #0x40c00000'),0x14b652c:('ldr','s8, [x19, #0x34]'),0x14b6564:('mov','w8, #3'),0x14b67b4:('mov','w8, #2')},
 '9.ControlMainCannonBullet':{0x14bb03c:('mov','w9, #0x40c00000'),0x14bb250:('ldr','s8, [x19, #0x34]'),0x14bb288:('mov','w8, #3'),0x14bb4d8:('mov','w8, #2')},
}


def build():
    contract_path=ROOT/'datas/combat_chain_contract.json.gz'
    dump_path=ROOT/'reverse-engineering/il2cpp/dump.cs.gz'
    cells_path=RAW/'referenced-cells.json.gz'
    contract=json.loads(gzip.decompress(contract_path.read_bytes()));dump=gzip.decompress(dump_path.read_bytes()).decode()
    cells=json.loads(gzip.decompress(cells_path.read_bytes()))['cells']
    jump=json.loads(JUMPS.read_text());jump_cells={int(c['va'],16):bytes.fromhex(c['hex']) for c in jump['cells']}
    rows=[];used={contract_path,dump_path,cells_path,JUMPS,ROOT/'tools/verify/combat_rate_consumers.py',ROOT/'tools/verify/combat_coroutine_models.py'}
    for method in contract['methods']:
        cls=method['class_name']
        if not cls.startswith('Player_Attack_') or '.' not in cls or method['method']!='MoveNext':continue
        key=re.sub(r'Player_Attack_(\d+)\.<(\w+)>.*',r'\1.\2',cls)
        role,flow=RECIPES[key]
        path=RAW/'native'/(re.sub(r'[^\w.]','_',cls)+'.asm.txt');used.add(path)
        start=int(method['rva'],16);end=start+method['clipped_bytes'];body={a:v for a,v in instructions(path).items() if start<=a<end}
        assert set(body)==set(range(start,end,4)),cls
        # Treat x0 as the iterator here; no owner-field recovery is wanted.
        dispatch_edges={}
        for at,(op,args) in body.items():
            if op=='br':
                assert key in ('6.ControlMainCannonBullet','7.ControlMainCannonBullet','9.ControlMainCannonBullet')
                is6=key.startswith('6.');table=0x77a07d if is6 else 0x77a081
                base=0x14b3da8 if is6 else 0x14b6308 if key.startswith('7.') else 0x14bb02c
                dispatch_edges[at]=[base+v*4 for v in jump_cells[table]]
        restores={};spill_proofs=[]
        if key=='23.IEMainCannonAttack':
            before=owner_states(body,start)
            save,restore=0x14a69c4,0x14a6f58
            assert body[save]==('str','x21, [sp, #8]')
            assert before[save][21]=='owner'
            assert body[restore]==('ldr','x21, [sp, #8]')
            # No path can reach the reload without the iterator spill.
            reached=set();todo=[start]
            while todo:
                at=todo.pop()
                if at in reached or at==save:continue
                reached.add(at);todo.extend(successors(at,*body[at],body))
            assert restore not in reached
            # Exhaustive SP-use check excludes alias escapes, overlap writes and SP
            # adjustment through the spill/reload interval, not just same-offset STR.
            assert [(a,v) for a,v in body.items() if save<=a<=restore and 'sp' in v[1]]==[(save,body[save]),(restore,body[restore])]
            restores[restore]=(21,'owner')
            spill_proofs.append({'save':hex(save),'restore':hex(restore),'register':'x21','slot':'sp+8','save_dominates_restore':True,'no_intervening_sp_use':True})
        aliases=owner_states(body,start,computed_edges=dispatch_edges,proven_restores=restores)
        state_writes=[];current_writes=[];edges=[];computed=[]
        for at,(op,args) in sorted(body.items()):
            mem=re.search(r'\[x(\d+), #0x(10|18)\]',args)
            if op=='str' and mem and aliases.get(at,(None,)*31)[int(mem[1])]=='owner':
                record={'at':hex(at),'op':op,'operands':args,'context':[{'at':hex(a),'op':body[a][0],'operands':body[a][1]} for a in range(max(start,at-12),at+4,4)]}
                (state_writes if mem[2]=='10' else current_writes).append(record)
            if op=='br':
                assert key in ('6.ControlMainCannonBullet','7.ControlMainCannonBullet','9.ControlMainCannonBullet'),(cls,hex(at))
                is6=key.startswith('6.');table=0x77a07d if is6 else 0x77a081
                base=0x14b3da8 if is6 else 0x14b6308 if key.startswith('7.') else 0x14bb02c
                assert ('ldrb','w11, [x9, x8]') in body.values()
                assert ('add','x10, x10, x11, lsl #2') in body.values()
                assert ('adr','x10, #0x'+format(base,'x')) in body.values()
                assert ('adrp','x9, #0x77a000') in body.values()
                assert ('add','x9, x9, #0x'+format(table-0x77a000,'x')) in body.values()
                targets=[base+v*4 for v in jump_cells[table]]
                assert all(t in body for t in targets)
                computed.append({'br':hex(at),'table':hex(table),'base':hex(base),'states':{str(i):hex(t) for i,t in enumerate(targets)}})
                edges.extend({'from':hex(at),'to':hex(t),'state':i} for i,t in enumerate(targets))
            elif op=='b' or op.startswith('b.') or op in ('cbz','cbnz','tbz','tbnz'):
                edges.extend({'from':hex(at),'to':hex(t)} for t in successors(at,op,args,body))
        for at,expected in ANCHORS.get(key,{}).items():
            assert body[at] == expected,(key,hex(at),body.get(at),expected)
        fs=fields(class_text(dump,cls))
        assert fs[0x10]['name']=='<>1__state' and fs[0x18]['name']=='<>2__current'
        rows.append({'key':key,'class':cls,'rva':method['rva'],'raw':str(path.relative_to(ROOT)),'instructions':len(body),'role':role,'reconstructed_control_flow':flow,'semantic_anchors':[{'at':hex(a),'op':v[0],'operands':v[1]} for a,v in ANCHORS.get(key,{}).items()],'iterator_fields':{hex(k):v for k,v in fs.items()},'iterator_spill_proofs':spill_proofs,'state_writes':state_writes,'current_writes':current_writes,'branch_edges':edges,'resolved_computed_dispatch':computed,'calls':method['direct_calls'],'indirect_calls':method['indirect_sites']})
    assert {r['key'] for r in rows}==set(RECIPES) and len(rows)==25
    factories=[]
    expected={
      (6,'ControlMainCannonBullet'):{0x14b3280:('str','s8, [x21, #0x20]')},
      (7,'ControlMainCannonBullet'):{0x14b5890:('stp','s9, s8, [x22, #0x30]')},
      (9,'ControlMainCannonBullet'):{0x14ba7a8:('stp','s9, s8, [x22, #0x30]')},
      (13,'ShotAllBarrels'):{0x1487ea0:('stp','w19, w20, [x22, #0x28]')},
      (14,'MoveObject'):{0x148a97c:('stp','s9, s8, [x22, #0x30]')},
      (23,'IEShootBarrels'):{0x14a5744:('stp','w20, w19, [x22, #0x28]')},
      (24,'IEShootBarrels'):{0x14a7f1c:('stp','w20, w19, [x22, #0x28]')},
    }
    for (number,name),anchors in expected.items():
        cls='Player_Attack_'+str(number)
        method=next(m for m in contract['methods'] if m['class_name']==cls and m['method']==name)
        path=RAW/'native'/(cls+'.asm.txt');used.add(path)
        start=int(method['rva'],16);end=start+method['clipped_bytes'];body={a:v for a,v in instructions(path).items() if start<=a<end}
        for at,value in anchors.items():assert body[at]==value
        callers=[{'class':m['class_name'],'method':m['method'],'at':c['at']} for m in contract['methods'] for c in m['direct_calls'] if c['target']==method['rva']]
        factories.append({'implementation':cls,'factory':name,'rva':method['rva'],'raw':str(path.relative_to(ROOT)),'native_parameter_copy':[{'at':hex(a),'op':v[0],'operands':v[1]} for a,v in sorted(body.items())],'direct_callers':callers})

    delegate_dir=ROOT/'reverse-engineering/raw/combat-delegates'
    manifest_path=delegate_dir/'index.json';manifest=json.loads(manifest_path.read_text());used.add(manifest_path)
    for entry in manifest['files']:
        path=ROOT/entry['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256'];used.add(path)
    global_rvas=sorted({int(a,16) for a in re.findall(r'// RVA: 0x([0-9a-fA-F]+)',dump)})
    delegated=[]
    for path in sorted(delegate_dir.glob('*.asm.txt')):
        metadata=json.loads(path.with_suffix('').with_suffix('.json').read_text())
        native=instructions(path);collected=[]
        for method in metadata['methods']:
            start=int(method['rva'],16);idx=bisect.bisect_right(global_rvas,start)
            end=min(start+method['bytes'],global_rvas[idx] if idx<len(global_rvas) else start+method['bytes'])
            body={a:v for a,v in native.items() if start<=a<end}
            assert set(body)==set(range(start,end,4)),(path.name,method['method'])
            collected.append({'name':method['method'],'rva':method['rva'],'clipped_bytes':end-start,'signature':method['signature'],'calls':[{'at':hex(a),'op':op,'operands':args} for a,(op,args) in sorted(body.items()) if op in ('bl','blr','br')],'branch_edges':[{'from':hex(a),'to':hex(t)} for a,(op,args) in sorted(body.items()) if op.startswith('b.') or op in ('b','cbz','cbnz','tbz','tbnz') for t in successors(a,op,args,body)]})
        delegated.append({'class':metadata['class'],'raw':str(path.relative_to(ROOT)),'fields':{hex(k):v for k,v in fields(class_text(dump,metadata['class'])).items()},'methods':collected})
    clone=instructions(delegate_dir/'Player9_Clone.asm.txt')
    for at,v in {0x14709ac:('ldrb','w8, [x0, #0x44]'),0x1470a5c:('b.mi','#0x1470d38'),0x1470a74:('str','s0, [x20, #0x40]'),0x1470e2c:('strb','w8, [x19, #0x44]'),0x1470ef8:('strb','wzr, [x19, #0x44]'),0x1470af4:('mov','w0, #0x57d4'),0x1470af8:('movk','w0, #1, lsl #16')}.items():assert clone[at]==v
    pumpkin=instructions(delegate_dir/'Player23_Pumpkin._IEStartAttack_d__22.asm.txt')
    for at,v in {0x14ddbc8:('b.le','#0x14ddc40'),0x14ddbe0:('b.pl','#0x14ddc00'),0x14ddbec:('fmov','s1, #0.50000000'),0x14ddc18:('b.le','#0x14ddc34'),0x14ddc84:('b.le','#0x14ddcbc'),0x14ddc68:('mov','x0, x8'),0x14ddc6c:('blr','x9'),0x14ddcb0:('bl','#0x14dc2a8')}.items():assert pumpkin[at]==v
    delegated_flows={
      'Player9_Clone':'StartAttack sets isAttack=true and starts DelayPool(duration); Update calls Shoot(numberNormal) only while isAttack. Shoot checks now>=timeToShot, updates deadline=now+shotRate, iterates number bullets using fixed poolID88020 (idBlt parameter is not consumed as pool index). Ctor numberNormal6, shotRate~0.15 and speed18 from exact cells. No reset of timeToShot in StartAttack: do not invent lifecycle reset.',
      'Player9_Clone.<DelayPool>d__12':'State0 Wait(duration)→state1; state1 StopAttack (isAttack=false + animator trigger), Wait(cleanup literal f32(0.34))→state2; state2 PoolObject(gameObject), finish. Stop and pool are distinct deadlines.',
      'Player23_Pumpkin':'StartAttack starts IEStartAttack. Check returns immediately unless actived; AttackLaser calls Check before target/visual-width gates. FindAndAttackEnemy reacquires target; RotateToTarget updates orientation. Hide spawns effect91105 when owner GameObject is valid, then pools owner. No pool-history assumptions.',
      'Player23_Pumpkin.<IEStartAttack>d__22':'State0 sets position=start; states0/1 MoveTowards target at8*deltaTime until squared 3D distance<pool epsilon, yielding null state1. On arrival timeout=now+duration4. While now<timeout, reacquire when now>timeToCheck and set nextCheck=now+0.5. If actived, expiry now>timeToDeactive clears actived and sets nextActive=now+timeCharge1, but still calls AttackLaser on that branch. If inactive and now>timeToActive set actived=true,nextDeactive=now+timeAttack2. RotateToTarget then yield null state2. At timeout invoke optional callback(owner GameObject), then Hide and return false. No WaitForSeconds in this body.'}
    def literal(va,width=4):
        cell=next(c for c in cells if int(c['va'],16)<=va and va+width<=int(c['va'],16)+c['width'])
        off=va-int(cell['va'],16);raw=bytes.fromhex(cell['hex'])[off:off+width]
        return {'va':hex(va),'hex':raw.hex(),'f32':list(struct.unpack('<'+'f'*(width//4),raw))}
    literals=[literal(va,width) for va,width in [(0x756b0c,4),(0x75700c,4),(0x756c44,4),(0x756fbc,4),(0x757918,8),(0x756e18,4),(0x7796b0,16),(0x756a58,4),(0x756fd0,4)]]
    delegate_literals=[{'va':c['va'],'hex':c['hex'],'f32':list(struct.unpack('<'+'f'*(c['width']//4),bytes.fromhex(c['hex'])))} for c in jump['cells'] if int(c['va'],16) not in (0x77a07d,0x77a081)]
    return {'status':'PROVISIONAL_NATIVE_SOURCE_WALK_WITH_MECHANICAL_CFG_NOT_EXECUTION_EQUIVALENCE','scope':'All25 preserved player combat MoveNext yield/resume/control roles; exact BR tables; helper bodies and clone firing remain separately scoped, no encounter DPS','inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(used)},'literal_cells':literals,'delegated_literal_cells':delegate_literals,'delegated_classes':delegated,'delegated_control_flow':delegated_flows,'factory_parameter_bindings':factories,'coroutines':rows}


if __name__=='__main__':
    import sys
    text=json.dumps(build(),ensure_ascii=False,indent=2)+'\n'
    if '--check' in sys.argv:assert OUT.read_text()==text
    else:OUT.write_text(text)
    print('25 coroutine source walks; all three computed dispatches resolved from 9 pinned bytes')
