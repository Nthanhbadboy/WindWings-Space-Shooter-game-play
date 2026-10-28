"""Byte-checked wing13/22/23/24 Shoot-to-iterator/geometry boundary evidence."""
import gzip,hashlib,json,re,struct
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
from tools.verify.combat_argument_audit import ROOT,instructions
from tools.verify.combat_rate_consumers import class_text,fields
OUT=ROOT/'datas/wing_emission_flow.json'

def build():
    used={ROOT/'tools/verify/wing_emission_flow.py',ROOT/'tools/verify/wing_emission_models.py',ROOT/'tools/verify/wing_emission_fixture.py',ROOT/'tools/verify/wing_native_fixture.py'}
    def read(p):used.add(p);return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
    read(ROOT/'datas/wing_implementations.json')
    raw=read(ROOT/'reverse-engineering/raw/wing-implementations/method-bytes.json.gz');idx=read(ROOT/'reverse-engineering/raw/wing-implementations/index.json');assert hashlib.sha256((ROOT/'reverse-engineering/raw/wing-implementations/method-bytes.json.gz').read_bytes()).hexdigest()==idx['sha256']
    pool=read(ROOT/'reverse-engineering/raw/wing-emission/pool.json');assert (raw['xapk_sha256'],raw['lib_sha256'])==(pool['xapk_sha256'],pool['lib_sha256'])
    interval=next(x for x in pool['cells'] if x['va']=='0x7575e0');assert interval['hex']=='0ad7233d0ad7a33d'
    md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN);methods=[];pools=[]
    for m in raw['methods']:
        root=m['cls'].split('.')[0]
        if root not in {f'Player_Attack_{i}' for i in (13,22,23,24)}:continue
        select=(m['method'] in ('Shoot','ShotAllBarrels','IEShootBarrels','ShootBasicBullets','ShootCircleBullets','ctor') or 'g__Shoot' in m['signature']) if m['cls']==root else ('ShotAllBarrels' in m['cls'] or 'IEShootBarrels' in m['cls'])
        if not select:continue
        p=ROOT/'reverse-engineering/raw/combat-chain/native'/(re.sub(r'[^a-zA-Z0-9_.-]','_',m['cls'])+'.asm.txt');used.add(p);code=instructions(p)
        b=bytes.fromhex(m['hex']);decoded=list(md.disasm(b,int(m['va'],16)));assert sum(x.size for x in decoded)==len(b)
        for x in decoded:assert code[x.address]==(x.mnemonic,x.op_str)
        methods.append(dict(cls=m['cls'],method=m['method'],signature=m['signature'],va=m['va'],instructions=len(decoded),sha256=hashlib.sha256(b).hexdigest()))
        for x in decoded:
            if x.mnemonic=='bl' and x.op_str in ('#0x123ab5c','#0x123a9fc'):pools.append(dict(cls=m['cls'],method=m['method'],signature=m['signature'],at=hex(x.address),target=x.op_str[1:]))
    sy=read(ROOT/'reverse-engineering/raw/combat-chain/symbols.json.gz')['records'];sy={x['Address']:x for k in ('ScriptMetadata','ScriptMetadataMethod') for x in sy[k]};rel={x['offset']:x for x in raw['relocations']};joins=[]
    for got,name in [('0x2adcbe8','Method$UnityEngine.GameObject.GetComponent<IBullet>()'),('0x2adcdb0','GameLayer_TypeInfo'),('0x2ae7d58','Method$SpaceShooter.Player.Player_Attack_13.OnBulletNormalCollided()'),('0x2ae7d60','Method$SpaceShooter.Player.Player_Attack_13.OnBulletNormalDestroyed()'),('0x2ae8050','Method$SpaceShooter.Player.Player_Attack_23.OnBulletNormalCollided()'),('0x2ae8058','Method$SpaceShooter.Player.Player_Attack_23.OnBulletNormalDestroyed()')]:
        rr=rel[got];a,kind,target=struct.unpack('<QQq',bytes.fromhex(rr['rela_hex']));assert hex(a)==got and kind==1027 and hex(target)==rr['addend'] and sy[target]['Name']==name;joins.append(dict(got=got,**sy[target]))
    direction_anchors=[]
    for i,minus,store_minus,plus,store_plus,store_array in [(22,0x14a4968,0x14a4970,0x14a497c,0x14a4984,0x14a4988),(23,0x14a670c,0x14a6714,0x14a6724,0x14a6728,0x14a672c),(24,0x14a905c,0x14a9064,0x14a9070,0x14a9078,0x14a907c)]:
        code=instructions(ROOT/f'reverse-engineering/raw/combat-chain/native/Player_Attack_{i}.asm.txt')
        assert code[minus]==('mov','w9, #-1') and code[store_minus]==('str','w9, [x0, #0x20]')
        assert code[plus][0]=='mov' and code[plus][1].endswith(', #1')
        assert code[store_plus][0]=='str' and code[store_plus][1].endswith('[x0, #0x24]') and code[store_array]==('str','x0, [x19, #0xe8]')
        direction_anchors.append(dict(implementation=i,minus=hex(minus),plus=hex(plus),store=hex(store_array)))
    dp=ROOT/'reverse-engineering/il2cpp/dump.cs.gz';used.add(dp);dump=gzip.decompress(dp.read_bytes()).decode();assert fields(class_text(dump,'GameLayer'))[0x14]['name']=='layerBullet'
    return dict(schema=1,provisional=True,scope='4 Shoot entry methods, 3 coroutine bodies plus wrappers, 3 basic packet geometries and 2 circle geometries; 13 present/missing IBullet branches through SetBullet/SetActive adapters; Basic/circle terminal helpers are observation boundaries, not hit simulations',method_count=len(methods),instruction_count=sum(x['instructions'] for x in methods),methods=methods,terminal_pool_sites=pools,symbol_joins=joins,sound=dict(super_interval=struct.unpack('<f',bytes.fromhex(interval['hex'])[:4])[0],normal_interval=struct.unpack('<f',bytes.fromhex(interval['hex'])[4:])[0],clip=5,volume_normal_hex='9a99193f',volume_super=1.),dispatch={'13':'StartCoroutine before outer deadline write; two Pool.GetObject attempts per successful yield, number yield-count', '22':'outer deadline before direct live-child loop; basic packet per child','23/24':'outer deadline before StartCoroutine; one child packet per yield; rate/live childCount reread after emission'},direction_anchors=direction_anchors,iterator13=dict(positions='two child points each index i; child0.x - scaleX/number*i, child1.x + scaleX/number*i',angles_degrees=['+4*i','-4*i'],z='demo: barrel parent.position.z + .1; normal: GameLayer.layerBullet',set_bullet=dict(force=1,target=0,lifetime=2,speed='live btlSpeed',through='super && throughShield'),width_step='owner.transform.localScale.x/number frozen at state0',interval='min(shotRate/number, f32(.05)) frozen at state0'),basic_geometry=dict(center='odd number OR spacing.x/2 == 0; unless id==-1',pairs='floor(number/2) rings, two directs entries; even nonzero spacing starts ring0, otherwise ring1',z='demo: fresh point.position.z + f32(.1); normal: GameLayer.layerBullet',direction_array_ctor=[-1,1],closure_layout={'22':{'destroyed':32,'collided':24,'owner':16},'23/24':{'destroyed':16,'collided':24,'owner':32}}),circle_geometry=dict(implementations=[22,23],angle='startAngle + f32(f32(arcRange/number) * f32(index)); no repeated endpoint',position='final fresh transform.position vector; no Basic z override',nonpositive_number='no terminal attempts',id_minus_one='not filtered by circle wrapper'),inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(used)})
if __name__=='__main__':OUT.write_text(json.dumps(build(),indent=2)+'\n');print(OUT)
