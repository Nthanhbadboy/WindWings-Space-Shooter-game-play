"""Check preserved font-pack metadata against source graphs, not a rendered font."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/recovery'))
from font_reference_pack import folder,key,load_objects,reference_json


def sha(blob):return hashlib.sha256(blob).hexdigest()

def verify():
    raw=ROOT/'reverse-engineering/raw/font-reference'
    manifest=json.load(gzip.open(raw/'manifest.json.gz','rt'));audit=json.loads((raw/'archive-audit.json').read_text());release=json.loads((raw/'release.json').read_text())
    contract_bytes=gzip.decompress((ROOT/'datas/font_language_contract.json.gz').read_bytes());contract=json.loads(contract_bytes)
    assert sha(contract_bytes)==manifest['contract_sha256_decompressed']
    assert manifest['sources_sha256_decompressed']==contract['sources_sha256_decompressed']
    for name,digest in manifest['sources_sha256_decompressed'].items():
        path=ROOT/name;blob=path.read_bytes()
        if path.suffix=='.gz':blob=gzip.decompress(blob)
        assert sha(blob)==digest,name
    source=json.load(gzip.open(ROOT/'reverse-engineering/raw/asset-pack-v2/archive-audit.json.gz','rt'))
    assert manifest['source_archive_sha256']==source['archive_sha256']
    assert manifest['static_chain_order']==contract['static_chain_order']
    catalog_blob=gzip.decompress((ROOT/'reverse-engineering/raw/asset-pack-v2/catalog.json.gz').read_bytes())
    assert sha(catalog_blob)==contract['catalog_sha256_decompressed']
    catalog=json.loads(catalog_blob);objects=load_objects()
    records={r['path']:r for r in manifest['files']};assert len(records)==len(manifest['files'])
    media={};expected={'README.txt','index.html','font-programs.json'}
    assert len(manifest['fonts'])==len(contract['fonts'])==7
    serialized_pairs=[]
    for f,ref in zip(contract['fonts'],manifest['fonts']):
        assert ref['identity']==f['identity'] and ref['folder']==folder(f['identity'])
        assert ref['atlas']==ref['folder']+'/atlas.png' and ref['metadata']==ref['folder']+'/font-reference.json'
        expected.update((ref['atlas'],ref['metadata']));media[ref['atlas']]=(f['atlases'][0]['identity'],f['atlases'][0]['png'])
        raw_font=objects[key(f['identity'])];tree=raw_font['tree']
        serialized_pairs.append(dict(font=f['identity']['path_id'],legacy_kerning_pairs=len(tree['m_KerningTable']['kerningPairs']),glyph_pair_adjustments=len(tree['m_FontFeatureTable']['m_GlyphPairAdjustmentRecords'])))
        data=reference_json(f,raw_font,objects[key(f['material'])])
        blob=(json.dumps(data,ensure_ascii=True,indent=2)+'\n').encode()
        r=records[ref['metadata']];assert r['kind']=='generated_reference_metadata'
        assert sha(blob)==r['sha256'] and len(blob)==r['bytes']
    programs=[o for o in catalog['objects'] if o['type']=='Font'];assert len(programs)==len(manifest['font_programs'])==1
    for program,ref in zip(programs,manifest['font_programs']):
        identity={k:program[k] for k in ('serialized_file','type','path_id')};source=program['outputs'][0]
        assert ref['identity']==identity and ref['source']==source
        assert ref['path']=='font-programs/'+folder(identity)+Path(source['path']).suffix.lower()
        assert 'not_a_sourceFontFile_binding' in ref['association']
        expected.add(ref['path']);media[ref['path']]=(identity,source)
    assert set(records)==expected
    for path,(identity,source) in media.items():
        r=records[path];assert r['kind']=='exact_v2_media' and r['identity']==identity and r['source']==source
        assert (r['sha256'],r['bytes'])==(source['sha256'],source['bytes'])
    assert audit['members']==len(records)+1==19 and audit['fonts']==7 and audit['font_programs']==1
    assert all(audit['gates'].values()) and release['post_upload_redownload_audit']==audit
    assert release['draft'] is True and release['release_id']==421174835 and release['existing_assets_unchanged'] is True
    asset=release['asset'];assert asset['name']=='font-reference-v1.zip'
    assert asset['digest']=='sha256:'+audit['archive_sha256'] and asset['size']==audit['bytes']
    assert len({a['id'] for a in release['previous_assets']})==len(release['previous_assets'])==7
    return dict(fonts=7,source_media=8,members=19,archive_sha256=audit['archive_sha256'],bytes=audit['bytes'],
        post_upload_redownload_verified=True,serialized_pair_inventory=serialized_pairs,scope='preserved_contracts_and_delivery_hashes_not_Unity_font_rendering')


if __name__=='__main__':print(json.dumps(verify(),indent=2))
