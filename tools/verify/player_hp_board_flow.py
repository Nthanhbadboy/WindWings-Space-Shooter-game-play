"""Native evidence contract for spec request6400762294; not peer text as gameplay source."""
import bisect,gzip,hashlib,json,re,struct
from tools.verify.combat_argument_audit import ROOT,instructions
from tools.verify.combat_rate_consumers import class_text,fields
RAW=ROOT/'reverse-engineering/raw/player-hp-board';CHAIN=ROOT/'reverse-engineering/raw/combat-chain'
OUT=ROOT/'datas/player_hp_board_flow.json'
ANCHORS={
 'Player_Health':{
  0x14c5950:('bl','#0x14e628c'),0x14c5954:('str','wzr, [x19, #0x58]'),0x14c5958:('str','wzr, [x19, #0x28]'),0x14c59d8:('sub','w9, w8, #0x3e8'),0x14c59e0:('b.hi','#0x14c5a18'),0x14c5a00:('bl','#0x125001c'),0x14c5a10:('str','s0, [x19, #0x58]'),0x14c5a48:('ldr','s9, [x9]'),0x14c5a60:('bl','#0x125001c'),0x14c5a64:('fmul','s0, s9, s0'),0x14c5a6c:('fdiv','s0, s0, s1'),0x14c5a74:('str','s0, [x19, #0x28]'),
  0x14c6c48:('mov','w1, #0x24'),0x14c6c58:('bl','#0x1434c84'),0x14c6c8c:('mov','w1, #0x40'),0x14c6c98:('b','#0x1434c84'),0x14c6cec:('ldr','s0, [x8]'),0x14c6cf0:('str','s0, [x8, #4]'),
  0x14c7d10:('ldr','d0, [x9, #0x9f0]'),0x14c7d1c:('str','d0, [x8]'),0x14c7dd8:('cmp','w9, #1'),0x14c7df4:('ldr','w8, [x8, #8]'),0x14c7df8:('cbz','w8, #0x14c7e78'),0x14c7e1c:('ldp','s9, s8, [x9]'),0x14c7e38:('fdiv','s1, s8, s9'),0x14c7e3c:('fmul','s1, s1, s0'),0x14c7e48:('stp','s0, s1, [x8]'),0x14c7e64:('mov','w1, #0x15'),0x14c7e70:('bl','#0x1434cb4'),0x14c7eac:('str','s8, [x8]'),0x14c7eb0:('bl','#0x14c6ca0'),0x14c7ed8:('bl','#0x14e378c'),0x14c7f08:('fmul','s0, s8, s0'),0x14c7f0c:('str','s0, [x19, #0x24]'),0x14c7f14:('fmov','s0, #5.00000000'),0x14c7f18:('bl','#0x2782388'),0x14c7f2c:('bl','#0x14e3890'),0x14c7f34:('str','s0, [x19, #0x2c]'),
  0x14c7c2c:('b.le','#0x14c7c90'),0x14c7c5c:('fadd','s0, s0, s1'),0x14c7c60:('fadd','s0, s0, s2'),0x14c7c68:('fcsel','s0, s0, s3, mi'),0x14c7c6c:('str','s0, [x8, #4]'),0x14c6430:('str','s0, [x8, #4]'),0x14c6470:('ldr','s0, [x8, #4]')},
 'Player_Health.__c':{0x14c8060:('cmp','w8, #7'),0x14c8064:('b.ne','#0x14c80b0'),0x14c8084:('bl','#0x14e311c'),0x14c80ac:('str','s8, [x8]')},
 'Player_Get_Datas':{0x14e3168:('ldr','s8, [x8, #0x6c]'),0x14e316c:('bl','#0x14e318c'),0x14e3180:('fmul','s0, s8, s0'),0x14e31f8:('mov','w0, wzr'),0x14e3200:('bl','#0x1399aa4'),0x14e3228:('ldr','s8, [x8, #0x68]'),0x14e3230:('ldr','s9, [x8, #0x314]'),0x14e323c:('mov','w0, #7'),0x14e3258:('fmul','s0, s8, s0'),0x14e325c:('fmul','s1, s9, s1'),0x14e3260:('fadd','s0, s0, s1')},
 'Board_Drones':{0x1264aac:('mov','w8, #0x4e21'),0x1264ab4:('str','w8, [x19, #0x1c8]'),0x1264abc:('mov','w1, #0x18'),0x1264ad0:('bl','#0x205b07c'),0x1264ad4:('str','x20, [x19, #0x238]'),0x1264bb8:('str','x19, [x8, #0x10]'),0x1264be0:('str','x19, [x8, #0x18]'),0x12638c8:('bl','#0x14da8ac'),0x12638fc:('sub','w10, w19, w9'),0x12638ec:('ldr','x8, [x11, #0x10]'),0x126391c:('ldr','x11, [x11, #0x18]'),0x1263960:('fmul','s0, s1, s0'),0x1263968:('fadd','s9, s0, s1'),0x126398c:('fmul','s9, s8, s9'),0x12639fc:('tst','x8, #1'),0x1263a00:('fcsel','d0, d0, d1, eq'),0x125ea60:('ldr','x8, [x19, #0x238]'),0x125ea74:('sub','w9, w10, w9'),0x125eb30:('ldr','s8, [x8, #0x20]'),0x12605d8:('bl','#0x1263860')}
}


def build():
    used={ROOT/'tools/verify/player_hp_board_flow.py',ROOT/'tools/verify/player_hp_board_models.py',RAW/'index.json',RAW/'cells.json'}
    def read(p):used.add(p);return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
    dump_p=ROOT/'reverse-engineering/il2cpp/dump.cs.gz';used.add(dump_p);dump=gzip.decompress(dump_p.read_bytes()).decode()
    idx=read(RAW/'index.json');raw=read(RAW/'cells.json')
    for x in idx['files']:
        p=ROOT/x['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256'];used.add(p)
    starts=sorted(set(int(x,16) for x in re.findall(r'// RVA: 0x([0-9A-Fa-f]+)',dump)))
    select={'Player_Health':{'Start','ResetStaticVariables','OnChangeDataDevice','GainHealth','AutoGainHealth','cctor','<Start>b__14_1'},'Player_Health.__c':{'<Start>b__14_0'},'Player_Get_Datas':{'GetStartHp','GetHpStatPercent','GetHpRecoverSpeed','TimeToImmuneOneHit'},'Tech_Datas':{'GetTechStatPoints','GetTechStatLevel'},'Board_Drones':{'ctor','cctor','SetPlayerInfo','GetPlayerPower','SetUpgradeCost'}}
    bodies={};ranges=[];anchors=[]
    for cls,names in select.items():
        p=RAW/'native'/(cls+'.asm.txt');used.add(p);code=instructions(p);bodies[cls]=code
        for m in read(RAW/'native'/(cls+'.json'))['methods']:
            if m['method'] not in names:continue
            a=int(m['rva'],16);b=min(a+m['bytes'],starts[bisect.bisect_right(starts,a)])
            assert not m['size_capped'] and all(at in code for at in range(a,b,4))
            ranges.append(dict(cls=cls,method=m['method'],rva=hex(a),instructions=(b-a)//4))
        for a,expected in ANCHORS.get(cls,{}).items():
            assert code[a]==expected,(cls,hex(a),code[a],expected);anchors.append(dict(cls=cls,at=hex(a),op=expected[0],args=expected[1]))
    symbols=read(CHAIN/'symbols.json.gz')['records'];sy={x['Address']:x for k in ('ScriptMetadata','ScriptMetadataMethod') for x in symbols[k]}
    reloc={x['got']:x for x in raw['relocations']}
    def join(got,name=None):
        rr=reloc[got];va,kind,target=struct.unpack('<QQq',bytes.fromhex(rr['rela_hex']));assert hex(va)==got and kind==1027 and hex(target)==rr['effective'];row=sy[target]
        if name:assert row['Name']==name,(got,row)
        return row
    joins=[]
    for got,name in [('0x2ae8580','SpaceShooter.Player.Player_Health_TypeInfo'),('0x2adc840','GameMode_TypeInfo'),('0x2add7d8','Board_Drones_TypeInfo')]:joins.append(dict(got=got,**join(got,name)))
    for got,addr in [('0x2ae85d0',0x14c7d28),('0x2ae85d8',0x14c7fe8)]:
        row=join(got);assert row['MethodAddress']==addr;joins.append(dict(got=got,**row))
    fields_hp=fields(class_text(dump,'Player_Health'));assert fields_hp[0]['name']=='StartHealth' and fields_hp[4]['name']=='CurrentHealth'
    gm=fields(class_text(dump,'GameMode'));assert gm[8]['name']=='waveIndex'
    infos=fields(class_text(dump,'Player_Get_Datas'));assert infos[0x68]['name']=='stepCommon' and infos[0x6c]['name']=='StartHp' and infos[0x314]['name']=='abi7AddPlayerStartHp'
    old=read(CHAIN/'referenced-cells.json.gz');cells={(int(x['va'],16),x['width']):x for x in old['cells']}
    cells.update({(int(x['va'],16),x['width']):x for x in raw['float_load_candidates']})
    constants={}
    for va,width,expected in [(0x7579f0,8,(2000,0)),(0x757bc0,8,(.18,2500)),(0x778b70,16,(.3,1,50,.2)),(0x756c78,4,(.1,)),(0x756cc8,4,(.06,)),(0x756ecc,4,(.03,)),(0x75706c,4,(.08,))]:
        bb=bytes.fromhex(cells[va,width]['hex']);assert bb==struct.pack('<'+'f'*len(expected),*expected);constants[hex(va)]=dict(hex=bb.hex(),values=list(struct.unpack('<'+'f'*len(expected),bb)))
    pgp=CHAIN/'native/Player_Get_Datas.asm.txt';used.add(pgp);pg=instructions(pgp)
    for a,v in {0x14e5e58:('ldr','d0, [x9, #0xbc0]'),0x14e5e70:('str','d0, [x8, #0x68]'),0x14e6210:('ldr','q0, [x9, #0xb70]'),0x14e6234:('stp','q0, q1, [x8, #0x310]'),0x14e5e74:('str','w9, [x8, #0x70]')}.items():assert pg[a]==v
    # Immediate BaseHpRecoverSpeed bits from MOV/MOVK, not an assumed percentage.
    assert pg[0x14e5e5c]==('mov','w9, #0xd70a') and pg[0x14e5e64]==('movk','w9, #0x3c23, lsl #16')
    assert struct.pack('<I',0x3c23d70a)==struct.pack('<f',.01)
    bf=fields(class_text(dump,'Board_Drones'));assert bf[0x238]['name']=='playerPriceMultipleA' and bf[0x10]['name']=='allBasicAtk' and bf[0x18]['name']=='allDeltaAtk'
    defaults=read(ROOT/'reverse-engineering/il2cpp/field-defaults.json')['fields'];arrays=[]
    for got,count,name,dest in [('0x2add988',24,'playerPriceMultipleA','instance238'),('0x2add998',12,'allBasicAtk','static10'),('0x2add9a0',12,'allDeltaAtk','static18')]:
        field=join(got)['Name'].removeprefix('Field$');bb=bytes.fromhex(defaults[field]['raw'])[:count*4]
        assert hashlib.sha256(bb).hexdigest().upper()==field.split('.')[-1]
        arrays.append(dict(got=got,field=field,name=name,destination=dest,length=count,hex=bb.hex(),values=list(struct.unpack('<'+'f'*count,bb))))
    literals=raw['literals'];assert len(literals)==1
    l=literals[0];encoded=struct.unpack('<Q',bytes.fromhex(l['pointee']['hex']))[0];assert encoded>>29==5 and ((encoded&0x1ffffffe)>>1)==l['index']
    magic,version,ls,lc,ds,dc=struct.unpack('<6I',bytes.fromhex(raw['metadata_header_hex']));assert magic==0xfab11baf and version==31
    length,offset=struct.unpack('<II',bytes.fromhex(l['definition_hex']));assert ds+offset==l['data_file_offset'] and offset+length<=dc and l['index']<lc//8
    assert length==len(bytes.fromhex(l['hex'])) and bytes.fromhex(l['hex']).decode()=='AutoGainHealth'
    # Direct census only, NOT indirect-call absence or entire UI-program closure.
    board=bodies['Board_Drones'];calls=[dict(at=hex(a),op=op,target=args) for a,(op,args) in board.items() if op in ('bl','b') and args.startswith('#0x')]
    direct_damage=[x for x in calls if x['target']=='#0x14da6f0'];assert not direct_damage
    return dict(schema='windwings.player-hp-board.v1',status='PROVISIONAL_NAMED_HP_WRITERS_AND_UI_CONSUMERS_NOT_GLOBAL_WRITER_OR_RUNTIME_CLOSURE',xapk_sha256=raw['xapk_sha256'],lib_sha256=raw['lib_sha256'],peer_review=dict(commit='ecff896c36cac3e58d991beac3328ec62f5cdb62',request=6400762294,role='Request only; not APK gameplay evidence'),methods=ranges,anchors=anchors,joins=joins,constants=constants,arrays=arrays,literals=literals,board_direct_calls=calls,board_direct_GetBaseDamage_sites=direct_damage,hp_rule='2500f*(1f+f32(.18f*Tech.GetTechStatPoints(0)+1f*Ability7)); per-op f32',scope=['Shared HP formula has no ship ID argument/index. No claim that every possible writer or runtime HP history is identical.','cctor StartHealth=2000/CurrentHealth=0 differs from GetStartHp base2500; event36/64 and reset are separate operations.','Board UI power uses its own allBasicAtk/allDeltaAtk and rounded numeric display, not drone combat BaseDamages/rank/ability formula.','Field-address joins and direct call census do not prove indirect reachability, event delivery, actual timer firing or save schema.'],source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(used)})


def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();r=build();text=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
    if a.check:assert OUT.read_text()==text,'HP/board contract drift'
    else:OUT.write_text(text)
    print(f"player_hp_board_flow: {len(r['methods'])} ranges/{sum(x['instructions'] for x in r['methods'])} instructions/{len(r['anchors'])} anchors PASS")
if __name__=='__main__':main()
