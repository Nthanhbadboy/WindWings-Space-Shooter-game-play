"""Recover only board-power relocation/default bytes from the pinned APK."""
import argparse,gzip,hashlib,io,json,struct,zipfile
from pathlib import Path
from combat_coroutine_cells import APK_SHA,LIB_SHA,extract
ROOT=Path(__file__).resolve().parents[2]
META_SHA='449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69'
def sha(b):return hashlib.sha256(b).hexdigest()
def recover(xapk):
 data=xapk.read_bytes();assert sha(data)==APK_SHA;libs=[];metas=[]
 with zipfile.ZipFile(io.BytesIO(data)) as outer:
  for n in outer.namelist():
   if not n.endswith('.apk'):continue
   with zipfile.ZipFile(io.BytesIO(outer.read(n))) as z:
    for name,target in [('lib/arm64-v8a/libil2cpp.so',libs),('assets/bin/Data/Managed/Metadata/global-metadata.dat',metas)]:
     if name in z.namelist():target.append(z.read(name))
 assert len(libs)==len(metas)==1;b=libs[0];m=metas[0];assert sha(b)==LIB_SHA and sha(m)==META_SHA
 wanted={0x2adfd00,0x2adfd08,0x2addda0};rels=[];off=struct.unpack_from('<Q',b,40)[0];size,count=struct.unpack_from('<HH',b,58)
 for i in range(count):
  h=struct.unpack_from('<IIQQQQIIQQ',b,off+i*size)
  if h[1]!=4:continue
  for p in range(h[4],h[4]+h[5],h[9] or 24):
   va,kind,target=struct.unpack_from('<QQq',b,p)
   if va in wanted:
    assert kind==1027;rels.append(dict(got=hex(va),target=target,file_offset=p,hex=b[p:p+24].hex()))
 assert {int(r['got'],16) for r in rels}==wanted
 # v31 header positions: string2, fieldDefaultValues7, defaultData8, fields11.
 assert struct.unpack_from('<II',m)==(0xfab11baf,31)
 sec=lambda i:struct.unpack_from('<II',m,8+8*i)
 fdo,fds=sec(7);do,ds=sec(8);fo,fs=sec(11);so,ss=sec(2);defaults=json.loads((ROOT/'reverse-engineering/il2cpp/field-defaults.json').read_bytes())['fields'];arr=[]
 for name in ['allBasicAtk','allDeltaAtk']:
  old=next(r for r in json.loads((ROOT/'reverse-engineering/il2cpp/ia-resolved.json').read_bytes())['methods']['Board_Players.cctor'] if r['addr']==({'allBasicAtk':'0x12d63f4','allDeltaAtk':'0x12d641c'}[name]));field=old['field'];fi=defaults[field]['field_index'];entry=next((p,struct.unpack_from('<iii',m,p)) for p in range(fdo,fdo+fds,12) if struct.unpack_from('<i',m,p)[0]==fi);p,(_,typ,di)=entry
  assert 0<=di<=ds-96 and fi*12+12<=fs;ni=struct.unpack_from('<I',m,fo+fi*12)[0];assert ni<ss;end=m.index(b'\0',so+ni);text=m[so+ni:end].decode();assert text==field.split('.')[-1]
  bb=m[do+di:do+di+96];assert sha(bb).upper()==text
  arr.append(dict(name=name,field=field,field_index=fi,entry_file_offset=p,entry_hex=m[p:p+12].hex(),field_file_offset=fo+fi*12,field_hex=m[fo+fi*12:fo+fi*12+12].hex(),name_file_offset=so+ni,name_hex=m[so+ni:end+1].hex(),data_file_offset=do+di,hex=bb.hex()))
 methods=json.loads(gzip.decompress((ROOT/'reverse-engineering/raw/l3-ui-native/method-bytes.json.gz').read_bytes()))['methods'];checked=[]
 for r in methods:
  if r['cls']=='Board_Players' and r['method'] in {'cctor','GetPlayerPower','SetPlayerInfo','SetUpgradeCost'}:
   actual=extract(b,((int(r['va'],16),r['width']),))['cells'][0];assert actual['hex']==r['hex'];checked.append(dict(method=r['method'],va=r['va'],width=r['width'],sha256=sha(bytes.fromhex(r['hex']))))
 assert len(checked)==4
 out=dict(provisional=True,provenance='arena/ef6b75ef',xapk_sha256=APK_SHA,lib_sha256=LIB_SHA,metadata_sha256=META_SHA,tool_sha256=sha(Path(__file__).read_bytes()),header_hex=m[:104].hex(),relocations=rels,arrays=arr,checked_existing_methods=checked,scope='Original ELF RELA and metadata bytes. Existing export only supplies candidate field indexes/ranges; recovered bytes and field digest checked against pinned original inputs.')
 dest=ROOT/'reverse-engineering/raw/board-power107';dest.mkdir(parents=True,exist_ok=True);(dest/'cells.json').write_text(json.dumps(out,indent=2)+'\n');print('3 RELA / 2 metadata arrays / 4 source method checks PASS')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True);recover(p.parse_args().xapk)
