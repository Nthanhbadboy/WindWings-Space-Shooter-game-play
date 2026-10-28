"""Reproducible proof for five actual pooled packet leaves (extension of94)."""
import gzip,hashlib,json,struct
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
from tools.verify.combat_argument_audit import ROOT
OUT=ROOT/'datas/wing_pooled_leaves.json'
def build():
    paths=[ROOT/p for p in ['tools/verify/wing_pooled_leaves.py','tools/verify/wing_pooled_leaf_fixture.py','tools/verify/wing_emission_fixture.py','datas/wing_implementations.json','reverse-engineering/raw/wing-implementations/method-bytes.json.gz','reverse-engineering/raw/wing-implementations/index.json','reverse-engineering/raw/wing-emission/formation-trampoline.json','reverse-engineering/raw/combat-chain/symbols.json.gz','reverse-engineering/il2cpp/dump.cs.gz']]
    raw=json.loads(gzip.decompress(paths[4].read_bytes()));index=json.loads(paths[5].read_bytes());assert hashlib.sha256(paths[4].read_bytes()).hexdigest()==index['sha256']
    tramp=json.loads(paths[6].read_bytes());assert tramp['lib_sha256']==raw['lib_sha256'] and tramp['xapk_sha256']==raw['xapk_sha256']
    md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN);c=tramp['cells'][0];decode=list(md.disasm(bytes.fromhex(c['hex']),int(c['va'],16)));assert [(x.mnemonic,x.op_str) for x in decode[:2]]==[('ldr','x10, [x10, #0xbf0]'),('b','#0x14a600c')]
    leaves=[]
    for m in raw['methods']:
        if m['cls'] not in ('Player_Attack_22','Player_Attack_23','Player_Attack_24') or 'g__Shoot' not in m['signature']:continue
        b=bytes.fromhex(m['hex']);ins=list(md.disasm(b,int(m['va'],16)));assert len(ins)*4==len(b)
        leaves.append(dict(cls=m['cls'],signature=m['signature'],va=m['va'],instructions=len(ins),sha256=hashlib.sha256(b).hexdigest(),calls=[dict(at=hex(x.address),kind=x.mnemonic,target=x.op_str) for x in ins if x.mnemonic in ('bl','blr','br') or (x.mnemonic=='b' and int(x.op_str[1:],16) not in range(int(m['va'],16),int(m['va'],16)+len(b)))]))
    assert len(leaves)==5
    rel={r['offset']:r for r in raw['relocations']};sy=json.loads(gzip.decompress(paths[7].read_bytes()))['records'];sy={x['Address']:x for k in ('ScriptMetadata','ScriptMetadataMethod') for x in sy[k]};joins=[]
    for got,name in [('0x2ae8030','Method$UnityEngine.GameObject.GetComponent<Bullet_Formation>()'),('0x2ae8020','Method$Bullet_Formation.OnCollided()'),('0x2ae8028','Method$Bullet_Formation.OnDestroyed()'),('0x2adcbe8','Method$UnityEngine.GameObject.GetComponent<IBullet>()')]:
        r=rel[got];a,k,t=struct.unpack('<QQq',bytes.fromhex(r['rela_hex']));assert hex(a)==got and k==1027 and hex(t)==r['addend'] and sy[t]['Name']==name;joins.append(dict(got=got,**sy[t]))
    dump=gzip.decompress(paths[8].read_bytes()).decode();assert 'public void CreateBullets(BulletForceType bulletForce, Transform target, LayerMask targetLayer, float speed, float lifetime, Action<GameObject, Vector3> onCollision)' in dump
    return dict(schema=1,provisional=True,scope='all five22/23/24 Basic/Circle leaves execute through Pool/IBullet/CreateBullets SDK adapters; no concrete projectile physics/collision/callback invocation',leaves=leaves,instructions=sum(m['instructions'] for m in leaves),trampoline=dict(va='0x2990890',executed_bytes=bytes.fromhex(c['hex'])[:8].hex(),instructions=2,return_va='0x14a600c'),joins=joins,rules=dict(lifetime={'22_basic':5,'22_circle':5,'23_basic':4,'23_circle':10,'24_basic':4},speed='Basic live owner.btlSpeed; Circle captured speed argument',through='direct owner.throughShield in every leaf; no local super gate',rotation='Basic point.euler.z+packetAngle; Circle packetAngle only; SetBullet angle re-read from pooled transform.euler.z',activation='SetActive(true) before GetComponent in all five leaves',missing_IBullet='22 and Circle23 return after activation; Basic23/24 PoolObject',missing_formation='Basic23/24 PoolObject even with IBullet present',callbacks='Basic23/24 formation methods first, caller callbacks second; CreateBullets receives caller collision only; other leaves pass caller callbacks directly',create='Basic23/24 CreateBullets after IBullet.SetBullet; force1,targetnull,mask/speed from owner,lifetime4',pool_null='throws; does not become missing-component return'),inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
if __name__=='__main__':OUT.write_text(json.dumps(build(),indent=2)+'\n');print(OUT)
