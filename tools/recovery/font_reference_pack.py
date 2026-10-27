"""Assemble scoped font references from audited media, never synthesize font bytes."""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/verify'))
from font_browser import render


def sha(blob):return hashlib.sha256(blob).hexdigest()
def write_json(path,value):path.write_text(json.dumps(value,ensure_ascii=True,indent=2)+'\n')
def load_objects():
    base=ROOT/'reverse-engineering/raw/font-language'
    index=json.loads((base/'graph-index.json').read_text());objects={}
    for chunk in index['chunks']:
        blob=gzip.decompress((base/chunk['path']).read_bytes());assert sha(blob)==chunk['sha256_decompressed']
        for line in blob.splitlines():
            row=json.loads(line);objects[(row['serialized_file'],row['type'],row['path_id'])]=row
    return objects

def key(identity):return(identity['serialized_file'],identity['type'],identity['path_id'])
def folder(identity):return 'font__'+sha(identity['serialized_file'].encode())+'__'+str(identity['path_id'])


def reference_json(font,raw,material):
    return dict(status='PROVISIONAL_REFERENCE_JSON_NOT_A_UNITY_IMPORT_ASSET',identity=font['identity'],font=font,
            raw_font_projection=raw,raw_primary_material_projection=material,
            notes=['Generated tree m_Script is not authoritative; use parsed_script_pointer and owning-file identity.',
                   'Full font typetree retains font features/kerning and serialized settings; primary material retains saved properties.',
                   'Shader native code and Unity rendering are not reproduced. External PPtrs are reference identities, not portable resolved imports.'])


def assemble(archive,destination,contract,catalog,objects,expected_archive_sha):
    assert sha(archive.read_bytes())==expected_archive_sha,'source archive digest mismatch'
    # Validate every member before creating any destination (including duplicate ZIP names).
    copies=[];font_records=[];browser=copy.deepcopy(contract)
    for index,font in enumerate(contract['fonts']):
        assert len(font['atlases'])==1,'multiple atlases need a reviewed layout'
        label=folder(font['identity']);source=font['atlases'][0]['png']
        target=label+'/atlas.png';copies.append(dict(path=target,source=source,identity=font['atlases'][0]['identity']))
        browser['fonts'][index]['atlases'][0]['png']['path']=target
        raw=objects[key(font['identity'])];material=objects[key(font['material'])]
        assert raw['class_name']=='TMP_FontAsset' and material['type']=='Material'
        font_records.append(dict(folder=label,identity=font['identity'],atlas=target,metadata=label+'/font-reference.json',
            font=font,raw_font=raw,raw_primary_material=material))
    programs=[]
    for obj in catalog['objects']:
        if obj['type']!='Font':continue
        assert obj['status']=='exported' and len(obj['outputs'])==1
        source=obj['outputs'][0];suffix=Path(source['path']).suffix.lower();assert suffix in ('.ttf','.otf')
        target='font-programs/'+folder(obj)+suffix
        identity={k:obj[k] for k in ('serialized_file','type','path_id')}
        copies.append(dict(path=target,source=source,identity=identity));programs.append(dict(identity=identity,name=obj['name'],path=target,source=source,
            association='exported_font_program_not_a_sourceFontFile_binding_for_the_seven_TMP_assets'))
    assert len({c['path'] for c in copies})==len(copies)
    with zipfile.ZipFile(archive) as zipped:
        names=zipped.namelist();assert len(names)==len(set(names)),'duplicate source ZIP names'
        payloads={}
        for c in copies:
            source=c['source'];blob=zipped.read(source['path'])
            assert len(blob)==source['bytes'] and sha(blob)==source['sha256'],'source member mismatch'
            payloads[c['path']]=blob
    destination.mkdir(parents=True,exist_ok=False)
    for target,blob in payloads.items():
        path=destination/target;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(blob)
    generated=[]
    for r in font_records:
        value=reference_json(r['font'],r['raw_font'],r['raw_primary_material'])
        write_json(destination/r['metadata'],value);generated.append(r['metadata'])
    write_json(destination/'font-programs.json',programs);generated.append('font-programs.json')
    page=render(browser)
    intro_start=page.index('<p>Copy this HTML file')
    intro_end=page.index('</p>',intro_start)+4
    page=page[:intro_start]+'<p>This folder is self-contained: open index.html offline. Atlas links point to the seven local font folders. See font-programs.json for the separately inventoried exported font program; it is not an inferred sourceFontFile binding.</p>'+page[intro_end:]
    (destination/'index.html').write_text(page);generated.append('index.html')
    (destination/'README.txt').write_text('WindWings 1.3.118: provisional font reference, not runtime-approved. Open index.html offline. Seven SDF atlas PNGs and one separately inventoried font program are exact copies from audited assets-v2.zip. Each font folder has face/glyph/character/fallback metadata plus full raw font and primary-material projections, including serialized font features. JSON is not a Unity .asset importer. SourceFontFile pointers are null on the seven TMP assets; no association with the separate TTF is invented. SDF atlases are not CSS fonts, and no shaping, RTL, shader, kerning or glyph layout is executed here. Copyright and original asset rights remain unchanged. No resampling, conversion or glyph repair.\n');generated.append('README.txt')
    all_files=[dict(path=c['path'],bytes=len(payloads[c['path']]),sha256=sha(payloads[c['path']]),kind='exact_v2_media',source=c['source'],identity=c['identity']) for c in copies]
    for target in generated:
        blob=(destination/target).read_bytes();all_files.append(dict(path=target,bytes=len(blob),sha256=sha(blob),kind='generated_reference_metadata'))
    manifest=dict(schema_version=1,status='PROVISIONAL_STATIC_FONT_REFERENCE_NOT_RUNTIME_OR_LICENSE_APPROVAL',source_archive_sha256=expected_archive_sha,
        contract_sha256_decompressed=sha((json.dumps(contract,ensure_ascii=True,indent=2)+'\n').encode()),
        fonts=[{k:r[k] for k in ('folder','identity','atlas','metadata')} for r in font_records],font_programs=programs,files=all_files,
        sources_sha256_decompressed=contract['sources_sha256_decompressed'],static_chain_order=contract['static_chain_order'])
    write_json(destination/'manifest.json',manifest)
    return manifest


def audit(archive,manifest):
    expected={f['path']:f for f in manifest['files']};assert len(expected)==len(manifest['files'])
    with zipfile.ZipFile(archive) as zipped:
        names=zipped.namelist();assert len(names)==len(set(names));assert set(names)==set(expected)|{'manifest.json'}
        assert zipped.testzip() is None
        assert json.loads(zipped.read('manifest.json'))==manifest
        for name,record in expected.items():
            blob=zipped.read(name);assert len(blob)==record['bytes'] and sha(blob)==record['sha256']
            if record['kind']=='exact_v2_media':
                assert record['source']['sha256']==record['sha256'] and record['source']['bytes']==record['bytes']
    return dict(archive_sha256=sha(archive.read_bytes()),bytes=archive.stat().st_size,members=len(expected)+1,
        fonts=len(manifest['fonts']),font_programs=len(manifest['font_programs']),
        gates=dict(exact_population=True,zip_crc=True,all_member_hashes=True,exact_source_media_hashes=True),
        limits=['Not a Unity import/render/shaping/RTL approval. Uploaded archive must be independently redownloaded to verify delivery.'])


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--archive',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    contract=json.load(gzip.open(ROOT/'datas/font_language_contract.json.gz','rt'));catalog=json.load(gzip.open(ROOT/'reverse-engineering/raw/asset-pack-v2/catalog.json.gz','rt'))
    expected=json.load(gzip.open(ROOT/'reverse-engineering/raw/asset-pack-v2/archive-audit.json.gz','rt'))['archive_sha256']
    manifest=assemble(args.archive,args.output,contract,catalog,load_objects(),expected)
    archive=args.output.parent/'font-reference-v1.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as zipped:
        for path in sorted(args.output.rglob('*')):
            if path.is_file():zipped.write(path,path.relative_to(args.output).as_posix())
    result=audit(archive,manifest)
    raw=ROOT/'reverse-engineering/raw/font-reference';raw.mkdir(parents=True,exist_ok=True)
    (raw/'manifest.json.gz').write_bytes(gzip.compress((json.dumps(manifest,indent=2)+'\n').encode(),mtime=0));write_json(raw/'archive-audit.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
