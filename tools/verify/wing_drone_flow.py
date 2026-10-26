"""APK-native wing1 + all12 current drone base-fire laws; legacy kept separate."""
import bisect,gzip,hashlib,json,re,struct
from tools.verify.combat_argument_audit import ROOT,instructions
from tools.verify.combat_rate_consumers import class_text,fields
from tools.verify.wing_drone_models import Wing1,configure_wing1
BASE=ROOT/'reverse-engineering/raw/wing-drone';CHAIN=ROOT/'reverse-engineering/raw/combat-chain'
OUT=ROOT/'datas/wing_drone_flow.json'
PROJECTILES=(1,2,3,5,6,8,10,11,12)
ANCHORS={
 'Player_Attack_1':{0x147b294:('str','wzr, [x19, #0x10c]'),0x147b2a8:('str','s0, [x19, #0xbc]'),0x147b2c0:('str','s0, [x19, #0x10c]'),0x147b3c4:('str','wzr, [x0, #0xec]'),0x147b3d4:('bl','#0x14b1eb0'),0x147b45c:('ldr','w8, [x8, #0x20]'),0x147b464:('str','w8, [x19, #0xb8]'),0x147b4c4:('fminnm','s0, s0, s1'),0x147b514:('stp','s1, s0, [x19, #0xc4]'),0x147adc0:('fcmp','s0, s1'),0x147add4:('fcmp','s0, s1'),0x147ae14:('fdiv','s1, s1, s2'),0x147ae1c:('str','s0, [x20, #0xc0]'),0x147ae3c:('cinc','w25, w10, ne'),0x147ae44:('str','w8, [x20, #0xec]'),0x147ae48:('b.ne','#0x147ae64'),0x147ae60:('str','s0, [x20, #0xbc]'),0x147b230:('b.ne','#0x147af1c'),0x147c6ac:('bl','#0x205b07c'),0x147c6b4:('str','x20, [x19, #0x78]')},
 'Player_Ingame':{0x14b1f0c:('cmn','w9, #1'),0x14b1f30:('bl','#0x14e5404'),0x14b1f54:('str','w19, [x9, #4]'),0x14b2224:('str','w19, [x8, #4]')},
 'Player_Get_Datas':{0x14e5500:('strb','wzr, [x8, #0x23]'),0x14e551c:('bl','#0x14e553c'),0x14e55e4:('bl','#0x14c7758'),0x14e55f4:('bl','#0x14c7758'),0x14e5608:('csel','w8, w8, w9, lt')},
 'Drone_Attack':{0x1468ab8:('b.pl','#0x1468ae0'),0x1468ac4:('fmov','s1, #0.50000000'),0x1468acc:('str','s0, [x19, #0x5c]')},
 'Drone_Attack7':{0x146e30c:('b.le','#0x146e328'),0x146e31c:('strb','wzr, [x19, #0x94]'),0x146e330:('b','#0x146e378'),0x146e344:('b.le','#0x146e368'),0x146e3c0:('bl','#0x146e5d8'),0x146e674:('cbz','w8, #0x146eb00')},
 'Drone_Attack9':{0x146fa90:('ret',''),0x146fad0:('b.le','#0x146fb50'),0x146fae4:('strb','wzr, [x19, #0x98]'),0x146fb20:('b','#0x2781804'),0x146fb2c:('b.le','#0x146fb70'),0x146fb4c:('b','#0x146fcbc'),0x146fb6c:('b','#0x146fce4')},
 'Drone_Get_Datas':{0x14da794:('mov','w10, #-0x4e21'),0x14da798:('add','w10, w20, w10'),0x14da7a0:('b.hs','#0x14da8a8'),0x14da7c4:('fmul','s0, s0, s1'),0x14da7d4:('fmul','s9, s0, s2'),0x14da848:('bl','#0x14c7758'),0x14da878:('ldr','s0, [x8, #0x338]'),0x14da898:('fmul','s0, s1, s0')},
 'Drone_Attack4':{0x146ccec:('str','wzr, [x19, #0x90]'),0x146ce94:('fnmul','s1, s0, s3'),0x146cef8:('b.ne','#0x146cf38'),0x146cf34:('str','w8, [x19, #0xbc]'),0x146cf3c:('b.ne','#0x146cfac'),0x146cf44:('strb','wzr, [x19, #0xb8]'),0x146cfa4:('strb','w8, [x19, #0xb8]')},
 'Droid_Attack':{0x145523c:('stur','xzr, [x0, #0x8c]'),0x1455240:('stur','xzr, [x0, #0x84]'),0x1455270:('blr','x9'),0x14552cc:('mov','w1, wzr'),0x145541c:('blr','x9'),0x1455420:('str','wzr, [x19, #0x94]'),0x145586c:('str','wzr, [x19, #0x90]'),0x1455870:('cbnz','w8, #0x145588c')},
}


def initializer(code,cells,start,end,field_info):
    """Strict straight-line byte provenance for ONLY Drone_Get_Datas.cctor numeric tail."""
    pages={};regs={};memory={};stores=[]
    def value(r):return regs[r]
    for at in range(start,end+4,4):
        op,args=code[at]
        m=re.fullmatch(r'(x\d+), #0x([0-9a-f]+)',args)
        if op=='adrp' and m:pages[m[1]]=int(m[2],16);continue
        m=re.fullmatch(r'([dsq]\d+), \[(x\d+), #0x([0-9a-f]+)\]',args)
        if op=='ldr' and m:
            va=pages[m[2]]+int(m[3],16);width={'s':4,'d':8,'q':16}[m[1][0]]
            row=cells[(va,width)];regs[m[1]]=bytes.fromhex(row['hex']);continue
        m=re.fullmatch(r'([wx]\d+), #(0x[\da-f]+|\d+)(?:, lsl #(\d+))?',args)
        if op in ('mov','movk') and m:
            reg=m[1];width=4 if reg[0]=='w' else 8;old=int.from_bytes(regs.get(reg,b'\0'*width),'little');shift=int(m[3] or 0)
            val=int(m[2],0)<<shift
            if op=='movk':val=old&~(0xffff<<shift)|val
            regs[reg]=val.to_bytes(width,'little');continue
        m=re.fullmatch(r'v(\d+).2s, (w\d+)',args)
        if op=='dup' and m:regs['d'+m[1]]=value(m[2])*2;continue
        m=re.fullmatch(r'v(\d+).2s, #([\d.]+)',args)
        if op=='fmov' and m:regs['d'+m[1]]=struct.pack('<ff',float(m[2]),float(m[2]));continue
        m=re.fullmatch(r'([dsqwx]\d+)(?:, ([dsqwx]\d+))?, \[x8, #0x([0-9a-f]+)\]',args)
        if op in ('str','stur','stp') and m and int(m[3],16)>=0x48:
            off=int(m[3],16);raw=value(m[1])+(value(m[2]) if m[2] else b'')
            for i,b in enumerate(raw):memory[off+i]=b
            stores.append(dict(at=hex(at),offset=hex(off),hex=raw.hex(),op=op,args=args))
    result=[]
    for offset,info in field_info.items():
        if offset<0x48:continue
        raw=bytes(memory[offset+i] for i in range(4));is_float=' float ' in info['declaration']
        result.append(dict(offset=hex(offset),name=info['name'],hex=raw.hex(),value=struct.unpack('<f' if is_float else '<i',raw)[0]))
    return result,stores


def build():
    dump_p=ROOT/'reverse-engineering/il2cpp/dump.cs.gz';dump=gzip.decompress(dump_p.read_bytes()).decode();used={ROOT/'tools/verify/wing_drone_flow.py',dump_p,BASE/'index.json',BASE/'cells.json',ROOT/'tools/verify/wing_drone_models.py'}
    raw=json.loads((BASE/'cells.json').read_text());index=json.loads((BASE/'index.json').read_text())
    for row in index['files']:
        p=ROOT/row['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'];used.add(p)
    starts=sorted(set(int(x,16) for x in re.findall(r'// RVA: 0x([0-9A-Fa-f]+)',dump)))
    selection={**{f'Drone_Attack{i}':{'OnEnable','FixedUpdate','Update','Shoot','AttackLaser','ctor'} for i in range(1,13)},'Drone_Attack':{'Start','FixedUpdate','Update','StartAttack','StopAttack','ctor'},'Drone_Get_Datas':{'cctor','GetBaseDamage'},'Player_Attack_1':{'SetBarrels','Shoot','ctor','OnEnable','StartAttack','StopAttack'},'Player_Ingame':{'get_Level','set_Level'},'Player_Get_Datas':{'GetStartPowerUpPoints','GetMaxPowerUpPoints'},'Droid_Attack':{'FixedUpdate','GunAttack','AutoAttack','MagEnded','StartSyncAttack','OnEnable'}}
    bodies={};ranges=[];anchors=[];method_ranges={}
    for cls,names in selection.items():
        folder=CHAIN/'native' if cls in ('Player_Attack_1','Player_Ingame') else BASE/'native'
        path=folder/(cls+'.asm.txt');meta=folder/(cls+'.json');used|={path,meta};code=instructions(path);bodies[cls]=code
        for m in json.loads(meta.read_text())['methods']:
            if m['method'] not in names:continue
            start=int(m['rva'],16);end=min(start+m['bytes'],starts[bisect.bisect_right(starts,start)])
            assert not m['size_capped'] and all(at in code for at in range(start,end,4))
            method_ranges[(cls,m['method'])]=(start,end)
            ranges.append(dict(cls=cls,method=m['method'],rva=hex(start),instructions=(end-start)//4,calls=[dict(at=hex(at),op=code[at][0],args=code[at][1]) for at in range(start,end,4) if code[at][0] in ('bl','blr','br')]))
        for at,v in ANCHORS.get(cls,{}).items():
            assert code[at]==v,(cls,hex(at),code[at],v);anchors.append(dict(cls=cls,at=hex(at),op=v[0],args=v[1]))
    oldcells_p=CHAIN/'referenced-cells.json.gz';used.add(oldcells_p)
    cells={(int(c['va'],16),c['width']):c for c in json.loads(gzip.decompress(oldcells_p.read_bytes()))['cells']}
    cells.update({(int(c['va'],16),c['width']):c for c in raw['float_load_candidates']})
    static,stores=initializer(bodies['Drone_Get_Datas'],cells,0x14db028,0x14db128,fields(class_text(dump,'Drone_Get_Datas')))
    assert len(static)==44
    # abi25: packed q3 -> static+340, lane2 is +348, no guessed +percentage.
    abi_raw=bytes.fromhex(cells[(0x779100,16)]['hex'])[8:12];assert struct.unpack('<f',abi_raw)[0]==2.5
    p=CHAIN/'native/Player_Get_Datas.asm.txt';used.add(p);pc=instructions(p)
    assert pc[0x14e622c]==('ldr','q3, [x9, #0x100]') and pc[0x14e6264]==('stp','q2, q3, [x8, #0x330]')
    assert fields(class_text(dump,'Player_Get_Datas'))[0x348]['name']=='abi25AddDroneShotRate'
    # RELA proves the InitializeArray source field, then length10 and SHA-named blob.
    symbols_p=CHAIN/'symbols.json.gz';defaults_p=ROOT/'reverse-engineering/il2cpp/field-defaults.json';used|={symbols_p,defaults_p}
    ss=json.loads(gzip.decompress(symbols_p.read_bytes()))['records'];sy={r['Address']:r for k in ('ScriptMetadata','ScriptMetadataMethod') for r in ss[k]};rel={r['got']:r for r in raw['relocations']}
    rr=rel['0x2ae7c58'];va,kind,target=struct.unpack('<QQq',bytes.fromhex(rr['rela_hex']));assert va==0x2ae7c58 and kind==1027 and hex(target)==rr['effective']
    field=sy[target]['Name'].removeprefix('Field$');blob=bytes.fromhex(json.loads(defaults_p.read_text())['fields'][field]['raw'])[:40]
    assert hashlib.sha256(blob).hexdigest().upper()==field.split('.')[-1]
    numbers=list(struct.unpack('<10i',blob));assert numbers==[3,4,5,6,7,8,9,12,13,14]
    rr=rel['0x2ae8a48'];va,kind,target=struct.unpack('<QQq',bytes.fromhex(rr['rela_hex']));assert va==0x2ae8a48 and kind==1027 and hex(target)==rr['effective']
    damage_field=sy[target]['Name'].removeprefix('Field$');damage_blob=bytes.fromhex(json.loads(defaults_p.read_text())['fields'][damage_field]['raw'])[:48]
    assert hashlib.sha256(damage_blob).hexdigest().upper()==damage_field.split('.')[-1]
    dc=bodies['Drone_Get_Datas'];assert dc[0x14dae24]==('ldr','x24, [x24, #0xa48]') and dc[0x14daf5c]==('ldr','x1, [x24]') and dc[0x14daf48]==('mov','w1, #0xc') and dc[0x14daf78]==('str','x19, [x8, #0x20]')
    # Preserve raw coefficient bits, not convenient decimal rank/level assumptions.
    damage_constants={}
    for va,expected in ((0x756e88,.16),(0x756b0c,.35),(0x75700c,.2),(0x757060,.56)):
        raw4=bytes.fromhex(cells[va,4]['hex']);v=struct.unpack('<f',raw4)[0];assert raw4==struct.pack('<f',expected)
        damage_constants[hex(va)]=dict(hex=raw4.hex(),value=v)
    abi21=bytes.fromhex(cells[(0x779830,16)]['hex'])[8:12];assert struct.unpack('<f',abi21)[0]==2.5 and fields(class_text(dump,'Player_Get_Datas'))[0x338]['name']=='abi21AddDmgDrone'
    assert pc[0x14e6224]==('ldr','q2, [x9, #0x830]')
    laser7=list(struct.unpack('<2f',bytes.fromhex(cells[0x7571f8,8]['hex'])))
    assert laser7==[struct.unpack('<f',struct.pack('<f',.2))[0],1.0]
    assert bodies['Drone_Attack7'][0x146ee44]==('stur','d0, [x0, #0x84]')
    laser_defaults=dict(drone7_timeAttack=laser7[0],drone7_timeCharge=laser7[1],drone9_timeAttack=1.5,drone9_timeCharge=1.5,drone9_width=10)
    for at,v in {0x1470464:('fmov','v0.2s, #1.50000000'),0x147046c:('stur','d0, [x0, #0x84]'),0x1470470:('str','w8, [x0, #0x8c]')}.items():assert bodies['Drone_Attack9'][at]==v
    # Keep wing field's relocation separate from the drone array join above.
    target=int(rel['0x2ae7c58']['effective'],16)
    assert bodies['Player_Attack_1'][0x147c698]==('mov','w1, #0xa')
    wing_constants={}
    for va,width,values in ((0x779b40,16,(.12,14,.06,20)),(0x756abc,4,(-.0035,)),(0x756b50,4,(1.1,))):
        raw_bytes=bytes.fromhex(cells[va,width]['hex']);assert raw_bytes==struct.pack('<'+'f'*len(values),*values)
        wing_constants[hex(va)]=dict(hex=raw_bytes.hex(),values=list(struct.unpack('<'+'f'*len(values),raw_bytes)))
    start_delay_raw=bytes.fromhex(cells[0x756f34,4]['hex']);wing_constants['start_attack_delay']=dict(hex=start_delay_raw.hex(),value=struct.unpack('<f',start_delay_raw)[0])
    assert bodies['Player_Attack_1'][0x147c720]==('ldr','q0, [x8, #0xb40]') and bodies['Player_Attack_1'][0x147c748]==('stur','q0, [x19, #0x98]')
    projectile_proofs=[]
    for i in PROJECTILES:
        cls='Drone_Attack'+str(i);code=bodies[cls];start,end=method_ranges[cls,'Shoot'];rows=[(a,*code[a]) for a in range(start,end,4)]
        pool=next(a for a,op,args in rows if op=='bl' and args=='#0x123a9fc')
        deadlines=[dict(at=hex(a),op=op,args=args) for a,op,args in rows if a<pool and op in ('fcmp','b.mi','b.gt','fadd','str')]
        assert sum(r['op']=='fcmp' for r in deadlines)==(1 if i==1 else 2)
        assert any(op=='cmp' and args=='x24, x25' for a,op,args in rows)
        assert any(op=='bl' and args=='#0x2781804' for a,op,args in rows)
        counter=[]
        if i!=1:
            at=next(a for a,op,args in rows if op=='add' and args=='w8, w8, #1')
            assert code[at+4]==('cmp','w8, w9') and code[at+12][0]=='b.lt'
            counter=[dict(at=hex(a),op=code[a][0],args=code[a][1]) for a in range(at-8,at+44,4)]
        projectile_proofs.append(dict(cls=cls,deadline_prefix=deadlines,counter_inside_barrel_loop=counter,pool_call=hex(pool)))
    examples=[]
    for lv in range(11):
        state=Wing1();configure_wing1(state,lambda:lv,lambda:False,numbers)
        examples.append(dict(level=lv,number=state.number,shot_rate=state.rate,bullet_speed=state.speed,angle=state.angle))
    legacy_fields=fields(dump.split('public class Droid_Attack : MonoBehaviour // TypeDefIndex: 1633')[1].split('// Namespace:')[0])
    assert legacy_fields[0x90]['name']=='countOfMags'
    return dict(schema='windwings.wing-drone.v1',status='PROVISIONAL_NATIVE_BASE_FIRE_NOT_DPS_OR_WHOLE_UNITY_REWRITE',xapk_sha256=raw['xapk_sha256'],lib_sha256=raw['lib_sha256'],methods=ranges,native_anchors=anchors,
      drone_numeric_fields=static,drone_base_damage=dict(field=damage_field,hex=damage_blob.hex(),values=list(struct.unpack('<12f',damage_blob)),index='source_id-20001',coefficients=damage_constants,abi21_amount=2.5),laser_defaults=laser_defaults,drone_initializer_stores=stores,projectile_scheduler_proofs=projectile_proofs,abi25=dict(field='Player_Get_Datas.abi25AddDroneShotRate',value=2.5,hex=abi_raw.hex(),q_source='0x779100',q_load='0x14e622c',q_store='0x14e6264'),wing1_numbers=dict(field=field,hex=blob.hex(),values=numbers,got='0x2ae7c58',effective=hex(target)),wing1_examples=examples,wing1_constants=wing_constants,
      scope=['Current Drone_Attack1..12 are separate from legacy SpaceShooter.Droid_Attack; neither class suffix nor inventory proves serialized source ID or spawning.',
       'Base-fire scheduler laws and config initializer values; no collision-geometry/beam-render/full damage-subscriber rewrite claimed.',
       'Wing SetBarrels/Shoot translated for Player_Attack_1 (source10003 per81); not extrapolated to the other23 ships.',
       'Models finite inputs and native-order callback/deadline edges. Unity tick spacing, observed fire frequency, hits and DPS are not inferred.'],
      source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(used)})


def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args();r=build();text=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
    if args.check:assert OUT.read_text()==text,'wing/drone contract drift'
    else:OUT.write_text(text)
    print(f"wing_drone_flow: {len(r['methods'])} ranges / {len(r['native_anchors'])} anchors / {len(r['drone_numeric_fields'])} numeric fields PASS")
if __name__=='__main__':main()
