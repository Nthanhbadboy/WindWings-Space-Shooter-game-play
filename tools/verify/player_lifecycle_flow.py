"""Exact ELF RELA metadata bindings and native HP lifecycle source anchors."""
import gzip,hashlib,json,re,struct
from tools.verify.combat_argument_audit import ROOT,instructions
OUT=ROOT/'datas/player_lifecycle_flow.json'
RAW=ROOT/'reverse-engineering/raw'

ANCHORS={
 'combat-receivers/Player_Controller.asm.txt':{
  0x14c2054:('ldr','x20, [x20, #0x418]'),0x14c2074:('str','x20, [x23, #0x38]'),
  0x14c2084:('ldr','x20, [x20, #0x480]'),0x14c20b4:('str','x20, [x23, #0x40]'),
  0x14c4328:('b.ne','#0x14c433c'),0x14c4338:('b','#0x14c435c'),
  0x14c43e0:('bl','#0x1434ce4'),0x14c4430:('bl','#0x14c63b4'),
  0x14c4440:('strb','w9, [x8, #0x30]'),0x14c4600:('bl','#0x14c46f4'),
  0x14c469c:('bl','#0x27bfdd4'),0x14c46b4:('bl','#0x27bfd98'),
  0x14c46cc:('bl','#0x27bfd5c'),0x14c46e0:('bl','#0x27c0320'),
  0x14c4750:('str','s8, [x20, #0x20]'),0x14c52e4:('b','#0x14c4690')},
 'combat-receivers/Player_Controller._DoExtraLife_d__62.asm.txt':{
  0x14c6088:('bl','#0x14c63b4'),0x14c6098:('strb','w9, [x8, #0x30]'),
  0x14c6184:('bl','#0x2786ed8'),0x14c625c:('bl','#0x2786670'),
  0x14c6354:('bl','#0x2786ed8'),0x14c6358:('fmov','s0, #0.50000000'),
  0x14c6374:('bl','#0x278276c'),0x14c638c:('strh','wzr, [x8, #2]')},
 'combat-receivers/Player_Controller._HealHp_d__63.asm.txt':{
  0x14c65a8:('fmul','s0, s1, s0'),0x14c65ac:('fdiv','s1, s0, s2'),
  0x14c65b0:('fdiv','s1, s1, s3'),0x14c65b4:('str','w9, [x19, #0x34]'),
  0x14c65d8:('b.pl','#0x14c661c'),0x14c65e4:('bl','#0x2786de8'),
  0x14c65ec:('fmul','s0, s8, s0'),0x14c65f0:('fadd','s1, s1, s0'),
  0x14c6608:('bl','#0x14c63b4'),0x14c6610:('str','xzr, [x19, #0x18]')},
 'combat-receivers/Player_Controller._IEHealInZoneInvisible_d__34.asm.txt':{
  0x14c66f8:('b','#0x14c6750'),0x14c6748:('fmul','s0, s0, s1'),
  0x14c674c:('bl','#0x14c63b4'),0x14c6770:('bl','#0x2786508')},
 'combat-chain/native/Player_Health.asm.txt':{
  0x14c6424:('fadd','s0, s0, s8'),0x14c642c:('fcsel','s0, s0, s1, mi'),
  0x14c6430:('str','s0, [x8, #4]'),0x14c6470:('ldr','s0, [x8, #4]'),
  0x14c648c:('bl','#0x1434cb4')},
}


def build():
    path=RAW/'player-lifecycle/cells.json';r=json.loads(path.read_text())
    symbols_path=RAW/'combat-chain/symbols.json.gz'
    symbols=json.loads(gzip.decompress(symbols_path.read_bytes()))['records']['ScriptMetadataMethod']
    bindings=[]
    expected={'0x2ae8480':('OnExtralife()',0x14c42d4),
              '0x2ae8418':('DestroyShieldOneHit()',0x1471884),
              '0x2ae85a8':('<DoExtraLife>b__62_0()',0x14c52e4)}
    for rel in r['relocations']:
        va,info,target=struct.unpack('<QQq',bytes.fromhex(rel['raw_hex']))
        assert hex(va)==rel['offset'] and hex(target)==rel['addend'] and info==1027
        matches=[s for s in symbols if s['Address']==target];assert len(matches)==1
        s=matches[0];suffix,rva=expected[rel['offset']]
        assert s['Name'].endswith('.'+suffix) and s['MethodAddress']==rva
        bindings.append({'got':rel['offset'],'effective':rel['addend'],'symbol':s['Name'],'method_rva':hex(rva)})
    values=[dict(c,value=struct.unpack('<f',bytes.fromhex(c['hex']))[0]) for c in r['cells'] if c['width']==4]
    sources={path,symbols_path,ROOT/'tools/verify/player_lifecycle_models.py'};anchors=[]
    for f,rows in ANCHORS.items():
        p=RAW/f;sources.add(p);asm=instructions(p)
        for a,v in rows.items():
            assert asm[a]==v,(f,hex(a),asm[a],v)
            anchors.append({'path':str(p.relative_to(ROOT)),'at':hex(a),'op':v[0],'args':v[1]})
    return {'status':'PROVISIONAL_APK_PLAYER_HP_LIFECYCLE_NOT_UNITY_EXECUTION',
      'bindings':bindings,'literals':values,'anchors':anchors,
      'source_artifacts':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(sources)]}


if __name__=='__main__':
    import sys
    r=build()
    if '--check' in sys.argv:assert r==json.loads(OUT.read_text())
    else:OUT.write_text(json.dumps(r,indent=2)+'\n')
    print(f"{len(r['bindings'])} exact callback bindings, {len(r['anchors'])} lifecycle anchors PASS")
