"""Audit an existing split release pack without adding original assets to Git."""
import argparse
from collections import Counter
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import struct
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def safe_path(name):
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and '..' not in path.parts and '\\' not in name


def inspect_media(data, name):
    suffix = PurePosixPath(name).suffix.lower()
    if suffix == '.png':
        assert data[:8] == b'\x89PNG\r\n\x1a\n', name
        width, height = struct.unpack('>II', data[16:24])
        assert width > 0 and height > 0
        return dict(kind='image', width=width, height=height, validation='PNG signature/IHDR only, not visual crop validation')
    if suffix == '.wav':
        with wave.open(io.BytesIO(data)) as clip:
            return dict(kind='audio', channels=clip.getnchannels(), rate=clip.getframerate(), frames=clip.getnframes(),
                        sample_width=clip.getsampwidth(), seconds=clip.getnframes()/clip.getframerate(), validation='WAV header plus archive CRC, not listening validation')
    if suffix in ('.ttf','.otf'):
        return dict(kind='font', signature_hex=data[:4].hex(), validation='extension/signature inventory only')
    return dict(kind='text_or_other', validation='archive CRC only; Spine binding/runtime compatibility not established')



def annotate_manifest_collisions(audit):
    for row in audit['files']:
        ids=row.get('identities',[])
        row['identity_status']=('ambiguous_manifest_path_collision' if len(ids)>1 else
            'not_in_export_manifest' if not ids else
            'manifest_size_mismatch' if str(ids[0].get('bytes'))!=str(row['bytes']) else
            'single_manifest_row_size_matches_only')
    collision_paths=[r['path'] for r in audit['files'] if len(r.get('identities',[]))>1]
    audit['collision_summary']=dict(paths=len(collision_paths),extra_manifest_rows=sum(max(0,len(r.get('identities',[]))-1) for r in audit['files']),paths_list=collision_paths)
    audit['validation_gates']=dict(archive_crc_valid=audit['archive_crc_valid'],manifest_path_mapping_injective=not collision_paths,manifest_size_matches=not audit['manifest_size_mismatches'],complete_APK_reference='NOT_ESTABLISHED')
    return audit


def browser_html(catalog):
    embedded = json.dumps(catalog, ensure_ascii=False).replace('<','\\u003c')
    return '''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>WindWings — pack reference browser</title><style>
body{margin:0;background:#101725;color:#e7edfa;font:15px system-ui}header{padding:24px;position:sticky;top:0;background:#101725f5;z-index:1}h1{margin:0 0 8px;font-size:24px}p{color:#afbdd4}input,select,button{padding:10px;margin:4px;border:1px solid #465574;border-radius:6px;background:#202e47;color:white}input{width:min(480px,70vw)}main{padding:20px;display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}article{padding:12px;background:#1a273d;border-radius:8px;overflow:hidden}img{width:100%;height:190px;object-fit:contain;background:repeating-conic-gradient(#26344c 0 25%,#1e2a40 0 50%) 50%/16px 16px}a{color:#94d8ff;overflow-wrap:anywhere}small{display:block;color:#b3c1d8;margin:8px 0}audio{width:100%}.notice{border-left:3px solid #ecb45f;padding-left:12px}#page{padding:0 24px 30px}
</style><header><h1>WindWings · full pack reference</h1><p class="notice">Provisional archive inventory, NOT complete APK coverage / visual or listening approval. Known manifest path collisions mean this is NOT a complete pack. Original media belongs to GCenter; reference only. Keep this HTML in the root of the extracted draft release pack. Missing media is not proof that the APK lacks it.</p><input id="q" placeholder="Search name / path / path ID"><select id="kind"><option value="">All file types</option></select><span id="count"></span></header><main id="grid"></main><div id="page"><button id="prev">Previous</button><span id="position"></span><button id="next">Next</button></div><script type="application/json" id="catalog">'''+embedded+'''</script><script>
const rows=JSON.parse(document.querySelector('#catalog').textContent).files;let page=0;const size=48;
const kind=document.querySelector('#kind'),q=document.querySelector('#q'),grid=document.querySelector('#grid');
for(const value of [...new Set(rows.map(r=>r.category))].sort()){let opt=document.createElement('option');opt.value=value;opt.textContent=value;kind.append(opt)}
function draw(){const query=q.value.toLowerCase(),found=rows.filter(r=>(!kind.value||r.category===kind.value)&&[r.path,...(r.identities||[]).map(i=>JSON.stringify(i))].join(' ').toLowerCase().includes(query));page=Math.max(0,Math.min(page,Math.ceil(found.length/size)-1));grid.replaceChildren();document.querySelector('#count').textContent=` ${found.length} / ${rows.length} files`;
for(const r of found.slice(page*size,(page+1)*size)){const card=document.createElement('article'),url=r.path.split('/').map(encodeURIComponent).join('/');
if(r.kind==='image'){const img=document.createElement('img');img.src=url;img.loading='lazy';img.alt=r.path;card.append(img)}else if(r.kind==='audio'){const audio=document.createElement('audio');audio.controls=true;audio.preload='none';audio.src=url;card.append(audio)}
const link=document.createElement('a');link.textContent=r.path;link.href=url;link.target='_blank';link.rel='noopener';card.append(link);const info=document.createElement('small');info.textContent=`${r.bytes} bytes · ${r.kind} · ${r.identity_status||"unreviewed identity"}`+(r.width?` · ${r.width}×${r.height}`:'')+(r.seconds!==undefined?` · ${r.seconds.toFixed(2)}s · ${r.rate}Hz`:'');card.append(info);if(r.identities?.length){const meta=document.createElement('small');meta.textContent=JSON.stringify(r.identities);card.append(meta)}grid.append(card)}document.querySelector('#position').textContent=` ${found.length?page+1:0} / ${Math.ceil(found.length/size)} `;document.querySelector('#prev').disabled=page===0;document.querySelector('#next').disabled=(page+1)*size>=found.length}
q.oninput=kind.onchange=()=>{page=0;draw()};document.querySelector('#prev').onclick=()=>{page--;draw()};document.querySelector('#next').onclick=()=>{page++;draw()};draw();
</script>'''


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--directory')
    parser.add_argument('--refresh-catalog',action='store_true')
    args=parser.parse_args()
    if args.refresh_catalog:
        path=ROOT/'reverse-engineering/raw/asset-pack/catalog.json.gz'
        audit=annotate_manifest_collisions(json.load(gzip.open(path,'rt')))
        path.write_bytes(gzip.compress(json.dumps(audit,ensure_ascii=False,indent=2).encode(),mtime=0))
        (ROOT/'docs/assets/pack-browser.html').write_text(browser_html(audit))
        return 0
    assert args.directory, '--directory is required unless refreshing preserved catalog'
    folder=Path(args.directory)
    release=json.loads((folder/'release.json').read_text())
    assert release['draft'], 'Do not publish or treat a published replacement as the pinned draft'
    out=ROOT/'reverse-engineering/raw/asset-pack'
    out.mkdir(parents=True,exist_ok=True)
    manifest=(folder/'manifest-full.csv').read_bytes()
    rows=list(csv.DictReader(io.StringIO(manifest.decode('utf-8-sig'))))
    # Keep raw CSV exactly; manifests may use png for non-PNG exported media.
    (out/'manifest-full.csv').write_bytes(manifest)
    indexed={}
    for row in rows:
        name=row.get('png') or row.get('file') or row.get('relative_path') or row.get('path')
        if name:
            indexed.setdefault(name.removeprefix('./'),[]).append(row)
    parts=[]
    for name in ('assets.z01','assets.zip','manifest-full.csv'):
        data=(folder/name).read_bytes()
        asset=next(a for a in release['assets'] if a['name']==name)
        assert len(data)==asset['size']
        sha=hashlib.sha256(data).hexdigest()
        if asset.get('digest'):
            assert asset['digest']=='sha256:'+sha
        parts.append(dict(name=name,asset_id=asset['id'],bytes=len(data),sha256=sha,release_digest=asset.get('digest')))
    files=[]
    with zipfile.ZipFile(folder/'assets-full.zip') as archive:
        assert archive.testzip() is None
        entries=[e for e in archive.infolist() if not e.is_dir()]
        assert len({e.filename for e in entries})==len(entries)
        for entry in entries:
            name=entry.filename.removeprefix('./')
            assert safe_path(name), name
            assert (entry.external_attr >> 16) & 0o170000 != 0o120000, name
            data=archive.read(entry)
            files.append(dict(path=name,bytes=len(data),crc32=f'{entry.CRC:08x}',sha256=hashlib.sha256(data).hexdigest(),
                category=name.split('/')[0] if '/' in name else '(root)',identities=indexed.get(name,[]),**inspect_media(data,name)))
    paths={r['path']:r for r in files}
    embedded=paths.get('manifest-full.csv')
    assert embedded and embedded['sha256']==hashlib.sha256(manifest).hexdigest()
    audit=dict(status='PROVISIONAL_EXISTING_DRAFT_ARCHIVE_AUDIT_NOT_COMPLETE_APK_COVERAGE',release_tag=release['tag_name'],release_id=release['id'],draft=True,
        parts=parts,manifest_columns=list(rows[0]) if rows else [],manifest_rows=len(rows),archive_crc_valid=True,
        files=files,counts_by_category=dict(sorted(Counter(r['category'] for r in files).items())),
        counts_by_kind=dict(sorted(Counter(r['kind'] for r in files).items())),
        manifest_missing_files=[name for name in indexed if name not in paths],
        manifest_size_mismatches=[dict(path=name,manifest=row.get('bytes'),actual=paths[name]['bytes']) for name,items in indexed.items() if name in paths for row in items if row.get('bytes','').isdigit() and int(row['bytes'])!=paths[name]['bytes']],
        limitations=['Archive validity is not original APK export completeness.','PNG headers/CRC do not prove sprite trim/flip/mask/crop correctness.','WAV headers/CRC are not listening validation.','Font/Spine presence is not runtime compatibility or rig binding validation.','No original media committed; browser requires separately downloaded and extracted draft release pack.'])
    annotate_manifest_collisions(audit)
    (out/'catalog.json.gz').write_bytes(gzip.compress(json.dumps(audit,ensure_ascii=False,indent=2).encode(),mtime=0))
    browser=ROOT/'docs/assets/pack-browser.html'
    browser.write_text(browser_html(audit))
    assert browser.stat().st_size<5_000_000
    print(json.dumps({k:v for k,v in audit.items() if k not in ['files','parts']},indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
