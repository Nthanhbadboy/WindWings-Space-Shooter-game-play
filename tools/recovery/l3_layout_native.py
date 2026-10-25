"""Narrow pinned native layout helpers and exact anchor literal/table cells."""
import argparse,gzip,hashlib,io,json,zipfile,tempfile
from pathlib import Path
import l3_ui_native as collector
from combat_coroutine_cells import APK_SHA,LIB_SHA,extract
ROOT=Path(__file__).resolve().parents[2]

def recover(binary,xapk):
    collector.CLASSES={'SafeArea','ObjectScaler'}
    out=ROOT/'reverse-engineering/raw/l3-layout-native';collector.recover(binary,out)
    cells=extract(binary,[(0x756ebc,4),(0x756d60,4),(0x756fb8,4),(0x756f00,4),(0x77a39e,8)])
    p=out/'anchor-cells.json';p.write_text(json.dumps(cells,indent=2)+'\n')
    from l3_layout_objects import recover as recover_objects
    with tempfile.TemporaryDirectory() as work:recover_objects(xapk,Path(work),out,binary)
    index=json.loads((out/'index.json').read_bytes())
    index['wrapper_tool_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    index['object_tool_sha256']=hashlib.sha256((ROOT/'tools/recovery/l3_layout_objects.py').read_bytes()).hexdigest()
    index['files']=[dict(path=str(p.relative_to(out)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='index.json']
    (out/'index.json').write_text(json.dumps(index,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--xapk',required=True);a=p.parse_args();data=Path(a.xapk).read_bytes();assert hashlib.sha256(data).hexdigest()==APK_SHA;found=[]
    with zipfile.ZipFile(io.BytesIO(data)) as outer:
        for name in outer.namelist():
            if not name.endswith('.apk'):continue
            with zipfile.ZipFile(io.BytesIO(outer.read(name))) as apk:
                if 'lib/arm64-v8a/libil2cpp.so' in apk.namelist():found.append(apk.read('lib/arm64-v8a/libil2cpp.so'))
    assert len(found)==1;recover(found[0],a.xapk)
