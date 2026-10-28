"""APK byte-checked per-implementation wing config and native consumer matrix."""
import gzip,hashlib,json,re,struct
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
from tools.verify.combat_argument_audit import ROOT,instructions
from tools.verify.combat_rate_consumers import class_text,fields,owner_states
from tools.verify.wing_config_models import CONFIG
RAW=ROOT/'reverse-engineering/raw/wing-implementations';CHAIN=ROOT/'reverse-engineering/raw/combat-chain'
OUT=ROOT/'datas/wing_implementations.json'
SPECIAL={2:'particle: UpdateParticle / OnParticleCollision / OnParticleCollision2',4:'lightning: FindAndAttackEnemies / LevelUp',6:'saw: SetSizeSaw / OnCollision',8:'saw + lightning: SetSizeSaw / FindAndAttackEnemies / OnCollision',10:'zone: AttackNormal / AttackEnemy / HitEnemy / UpdateRange',12:'normal/super + animation-event: AttackNormal / AttackSuper / SyncAttack / OnHitSuper',15:'laser guns: GunCheckEnemies / UpdateLaserPositions'}

def numeric_array(code,method,offset,symbols,rel,defaults):
    """Straight-line constructor reference provenance; never execute SDK helpers."""
    regs={0:('owner',)};arrays={};answer=None
    for at in sorted(code):
        if not int(method['va'],16)<=at<int(method['va'],16)+method['width']:continue
        op,args=code[at]
        m=re.fullmatch(r'x(\d+), #0x([0-9a-f]+)',args)
        if op=='adrp' and m:regs[int(m[1])]=('page',int(m[2],16));continue
        m=re.fullmatch(r'([xw])(\d+), #(-?(?:0x[0-9a-f]+|\d+))',args)
        if op=='mov' and m:regs[int(m[2])]=('int',int(m[3],0));continue
        m=re.fullmatch(r'x(\d+), x(\d+)',args)
        if op=='mov' and m:regs[int(m[1])]=regs.get(int(m[2]));continue
        m=re.fullmatch(r'x(\d+), \[x(\d+)(?:, #((?:0x)?[0-9a-f]+))?\]',args)
        if op=='ldr' and m:
            b=regs.get(int(m[2]));v=None
            if b and b[0]=='page':v=('got',b[1]+int(m[3] or '0',0))
            if b and b[0]=='got' and m[3] is None:v=('value',rel.get(b[1]))
            regs[int(m[1])]=v;continue
        if op=='bl':
            result=None
            if args=='#0x110d09c':
                n=regs.get(1);assert n and n[0]=='int';result=('array',at);arrays[at]={'length':n[1]}
            if args=='#0x205b07c':
                a=regs.get(0);f=regs.get(1);assert a and a[0]=='array' and f and f[0]=='value',(hex(at),a,f)
                field=symbols[f[1]]['Name'].removeprefix('Field$');blob=bytes.fromhex(defaults['fields'][field]['raw']);row=arrays[a[1]]
                blob=blob[:row['length']*4];assert hashlib.sha256(blob).hexdigest().upper()==field.split('.')[-1]
                row.update(field=field,hex=blob.hex(),values=list(struct.unpack('<'+'i'*row['length'],blob)))
            for r in range(19):regs[r]=None
            regs[0]=result;continue
        m=re.fullmatch(r'x(\d+), \[x(\d+), #0x([0-9a-f]+)\]',args)
        if op=='str' and m and int(m[3],16)==offset and regs.get(int(m[2]))==('owner',):
            a=regs.get(int(m[1]));assert a and a[0]=='array';answer=arrays[a[1]].copy();answer['store']=hex(at)
        if not op.startswith(('st','b')) and op not in ('cmp','cmn','tst','ret','cbz','cbnz','tbz','tbnz','nop'):
            for dest in args.split(',')[:2 if op.startswith('ldp') else 1]:
                mm=re.fullmatch(r'[xw](\d+)',dest.strip())
                if mm:regs[int(mm[1])]=None
    assert answer and 'field' in answer;return answer

def build():
    used={ROOT/'tools/verify/wing_implementations.py',ROOT/'tools/verify/wing_config_models.py',ROOT/'tools/verify/wing_native_fixture.py'}
    def read(p):used.add(p);return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
    payload=read(RAW/'method-bytes.json.gz');idx=read(RAW/'index.json');assert hashlib.sha256((RAW/'method-bytes.json.gz').read_bytes()).hexdigest()==idx['sha256']
    dp=ROOT/'reverse-engineering/il2cpp/dump.cs.gz';used.add(dp);dump=gzip.decompress(dp.read_bytes()).decode()
    chain=read(ROOT/'datas/combat_chain_contract.json.gz');symbols=read(CHAIN/'symbols.json.gz')['records'];symbols={x['Address']:x for k in ('ScriptMetadata','ScriptMetadataMethod') for x in symbols[k]}
    reloc=read(CHAIN/'relocations.json.gz')['entries'];rel={int(x['offset'],16):int(x['addend'],16) for x in reloc if x['type']==1027}
    for x in payload['relocations']:
        va,kind,target=struct.unpack('<QQq',bytes.fromhex(x['rela_hex']));assert hex(va)==x['offset'] and kind==1027 and hex(target)==x['addend'];rel[va]=target
    defaults=read(ROOT/'reverse-engineering/il2cpp/field-defaults.json');md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN);rows=[];total=0
    for i in range(1,25):
        cls=f'Player_Attack_{i}';fs=fields(class_text(dump,cls));members=[x for x in payload['methods'] if x['cls']==cls or x['cls'].startswith(cls+'.')]
        proofs=[];dispatch=[];field_accesses=[]
        for m in members:
            p=CHAIN/'native'/(re.sub(r'[^a-zA-Z0-9_.-]','_',m['cls'])+'.asm.txt');used.add(p);code=instructions(p)
            b=bytes.fromhex(m['hex']);dis=list(md.disasm(b,int(m['va'],16)));assert sum(x.size for x in dis)==len(b),(cls,m['method'],'decode gap')
            for ins in dis:assert code[ins.address]==(ins.mnemonic,ins.op_str),(m['cls'],hex(ins.address))
            total+=len(dis)
            proofs.append(dict(cls=m['cls'],method=m['method'],va=m['va'],instructions=len(dis),sha256=hashlib.sha256(b).hexdigest()))
            body={x.address:(x.mnemonic,x.op_str) for x in dis}
            if m['cls']==cls:
                aliases=owner_states(body,int(m['va'],16))
                for a,(op,args) in body.items():
                    mt=re.search(r'\[x(\d+), #0x([0-9a-f]+)\]',args)
                    if mt and aliases.get(a,[None]*31)[int(mt[1])]=='owner' and int(mt[2],16) in fs:
                        field_accesses.append(dict(method=m['method'],at=hex(a),op=op,args=args,field=fs[int(mt[2],16)]['name']))
                    mt=re.fullmatch(r'x(\d+), x\d+, \[x\d+, #0x(178|188)\]',args)
                    if op=='ldp' and mt:
                        candidates=[k for k in range(a+4,a+16,4) if body.get(k)==('blr','x'+mt[1])]
                        if candidates:
                            call=candidates[0];owner=aliases.get(call,[None]*31)[0]
                            dispatch.append(dict(method=m['method'],load=hex(a),call=hex(call),entry='0x'+mt[2],receiver_must_owner=owner=='owner',getter='get_GetWingCannonDamage' if mt[2]=='178' else 'get_GetWingCannonMaxPowerDamage'))
        source=next(x for x in chain['ships'] if x['implementation']==cls);components=source['source_components'] or source['prefix_only_components'];ids=sorted({x['id'] for x in components});assert len(ids)==1
        if not source['source_components']:
            for x in source['source_errors']:
                b=bytes.fromhex(x['raw_object_hex']);assert hashlib.sha256(b).hexdigest()==x['raw_object_sha256'];assert struct.unpack_from('<i',b,32)[0]==ids[0]
        array=None
        if 'allNumberBullets' in [x['name'] for x in fs.values()]:
            off=next(k for k,x in fs.items() if x['name']=='allNumberBullets');ctor=next(x for x in members if x['cls']==cls and x['method']=='ctor');array=numeric_array(instructions(CHAIN/'native'/(cls+'.asm.txt')),ctor,off,symbols,rel,defaults)
        config=dict(delta_rate=CONFIG[i][0],delta_speed=CONFIG[i][1],speed_cap=CONFIG[i][2],rate_floor=CONFIG[i][3],spread=list(CONFIG[i][4]) if CONFIG[i][4] else None) if i in CONFIG else None
        rows.append(dict(implementation=cls,source_id=ids[0],number_index_policy=('compressed_two_level_reads' if i in (1,3,11,16,17,18,20,22,23,24) else 'clamp_level' if i in (13,21) else 'max_level_minus_one_no_upper_cap' if array else None),super_still_updates_spread=(i==20),identity_provenance='full_tree' if source['source_components'] else 'raw_prefix_id_not_full_particle_curve_tree',fields={hex(k):v for k,v in fs.items()},numeric_array=array,normal_set_barrels=config,special_path=SPECIAL.get(i),methods=proofs,field_accesses=field_accesses,virtual_damage_dispatch=dispatch))
    return dict(schema=1,provisional=True,status='ALL24_NATIVE_METHODS_BYTE_CHECKED_17_SETBARRELS_CONFIGS_NOT_ALL24_SCHEDULER_REWRITE',xapk_sha256=payload['xapk_sha256'],lib_sha256=payload['lib_sha256'],method_count=sum(len(x['methods']) for x in rows),instruction_count=total,implementations=rows,inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(used)})
if __name__=='__main__':OUT.write_text(json.dumps(build(),indent=2)+'\n');print(OUT)
