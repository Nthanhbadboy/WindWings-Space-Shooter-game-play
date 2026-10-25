"""File-scoped Spine reference joins, deliberately not a runtime renderer."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT/'reverse-engineering/raw/spine-identity'


def oid(value):
    return value['serialized_file'], value['type'], int(value['path_id'])


def select_local_page(page_name, material_textures):
    """Matches ONLY textures reached through the owning atlas' material pointers."""
    if '/' in page_name or '\\' in page_name or page_name in ('.','..'):
        raise ValueError('page path needs explicit handling')
    name = page_name.rsplit('.', 1)[0] if '.' in page_name else page_name
    matches = [m for m in material_textures if m['texture_name'] == name]
    if len(matches) != 1:
        raise ValueError(f'page must have one local candidate, found {len(matches)}')
    return matches[0]


def derive(chains, catalog):
    rows = {oid(r):r for r in chains['objects']}
    assert len(rows) == len(chains['objects'])
    media = {oid(r):r for r in catalog['objects']}
    links = {(oid(l['owner']),l['location']):l for l in chains['links']}
    assert len(links) == len(chains['links'])
    def target(owner,location,kind):
        link=links[oid(owner),location]
        assert link['status']=='resolved'
        assert link['target']['type']==kind
        if link['pointer']['m_FileID']==0:
            assert owner['serialized_file']==link['target']['serialized_file']
        assert link['pointer']['m_PathID']==link['target']['path_id']
        return rows[oid(link['target'])]
    def source_output(obj):
        row=media[oid(obj)]
        assert row['status']=='exported' and len(row['outputs'])==1
        output=row['outputs'][0]
        if obj['type']=='TextAsset':
            assert output['sha256']==obj['payload_sha256'] and output['bytes']==obj['payload_bytes']
        return dict(identity={k:obj[k] for k in ('serialized_file','type','path_id')},**output)
    rigs=[]
    for root in chains['objects']:
        if root.get('class_name')!='SkeletonDataAsset':
            continue
        tree=root['tree']
        skeleton=target(root,'.skeletonJSON','TextAsset')
        assert skeleton.get('skeleton_header')
        atlases=[]
        for index,_ in enumerate(tree['atlasAssets']):
            atlas=target(root,f'.atlasAssets[{index}]','MonoBehaviour')
            assert atlas['class_name']=='SpineAtlasAsset'
            atlas_file=target(atlas,'.atlasFile','TextAsset')
            local=[]
            for mi,_ in enumerate(atlas['tree']['materials']):
                material=target(atlas,f'.materials[{mi}]','Material')
                tex_envs=material['tree']['m_SavedProperties']['m_TexEnvs']
                nonnull=[(ti,prop,env) for ti,(prop,env) in enumerate(tex_envs) if env['m_Texture']['m_PathID']]
                # This observed build has one saved texture property, _MainTex.
                # Do not extend that assumption silently to arbitrary shaders/materials.
                assert len(nonnull)==1 and nonnull[0][1]=='_MainTex'
                ti,_,env=nonnull[0]
                texture=target(material,f'.m_SavedProperties.m_TexEnvs[{ti}][1].m_Texture','Texture2D')
                shader=target(material,'.m_Shader','Shader')
                props=shader['properties']['m_Props']
                assert not any(prop['m_Flags'] & 128 for prop in props)
                assert any(prop['m_Name']=='_MainTex' and prop['m_Type']==4 for prop in props)
                local.append(dict(material={k:material[k] for k in ('serialized_file','type','path_id')},
                                  shader={k:shader[k] for k in ('serialized_file','type','path_id')},
                                  texture_name=texture['name'], texture=source_output(texture),
                                  width=texture['width'],height=texture['height'], texture_property='_MainTex',material_properties=material['tree']['m_SavedProperties'],shader_properties=props))
            pages=[]
            for page in atlas_file['atlas_pages']:
                match=select_local_page(page['name'],local)
                size=next(line for line in page['header_lines'] if line.startswith('size:'))
                expected=[int(x.strip()) for x in size.split(':',1)[1].split(',')]
                pages.append(dict(page=page['name'],atlas_dimensions=expected,
                                  dimension_match=expected==[match['width'],match['height']],**match))
            assert pages
            atlases.append(dict(identity={k:atlas[k] for k in ('serialized_file','type','path_id')},
                                atlas_text=source_output(atlas_file),pages=pages))
        blends=[]
        blend=tree.get('blendModeMaterials',{})
        for mode in ('additiveMaterials','multiplyMaterials','screenMaterials'):
            for index,entry in enumerate(blend.get(mode,[])):
                material=target(root,f'.blendModeMaterials.{mode}[{index}].material','Material')
                textures=[l['target'] for l in chains['links'] if oid(l['owner'])==oid(material) and l['location'].startswith('.m_SavedProperties.m_TexEnvs') and l['status']=='resolved']
                blends.append(dict(mode=mode,page_name=entry['pageName'],material={k:material[k] for k in ('serialized_file','type','path_id')},texture_targets=textures,material_properties=material['tree']['m_SavedProperties']))
        rigs.append(dict(identity={k:root[k] for k in ('serialized_file','type','path_id')},
                         skeleton=source_output(skeleton),skeleton_header=skeleton['skeleton_header'],
                         animation_names=skeleton['animation_names'],atlases=atlases,
                         unity_settings={k:tree[k] for k in ('scale','defaultMix','fromAnimation','toAnimation','duration','blendModeMaterials','skeletonDataModifiers','controller')},
                         blend_replacements=blends,status='static_chain_resolved_not_runtime_verified'))
    return dict(schema_version=1,status='provisional_APK_file_scoped_reference_association',rigs=rigs,
                summary=dict(rigs=len(rigs),pages=sum(len(a['pages']) for r in rigs for a in r['atlases']),
                             blend_replacement_materials=sum(len(r['blend_replacements']) for r in rigs),
                             observed_skeleton_versions=dict(Counter(r['skeleton_header'].get('spine','unknown') for r in rigs))),
                scan_scope=dict(counts=chains['scan_counts'],all_MB_headers_classified=chains['all_MB_headers_classified'],unclassified_MB=chains['header_errors']),
                limits=['Local owning-atlas material search, not global texture basename matching.',
                        'Shader/blend/PMA, crop fidelity and animation playback are not runtime approved.',
                        'One unclassified built-in-resource MonoBehaviour remains explicit; 27 selected rigs are not an exhaustiveness theorem.'])


def build():
    chains=json.loads(gzip.decompress((RAW/'chains.json.gz').read_bytes()))
    index=json.loads((RAW/'index.json').read_text())
    for record in index['files']:
        blob=(RAW/record['path']).read_bytes()
        if record['path'].endswith('.gz'):blob=gzip.decompress(blob)
        assert hashlib.sha256(blob).hexdigest()==record['sha256_decompressed']
    catalog=json.loads(gzip.decompress((ROOT/'reverse-engineering/raw/asset-pack-v2/catalog.json.gz').read_bytes()))
    result=derive(chains,catalog)
    dump_blob=gzip.decompress((ROOT/'reverse-engineering/il2cpp/dump.cs.gz').read_bytes())
    assert hashlib.sha256(dump_blob).hexdigest()==index['dump_sha256_decompressed']
    dump=dump_blob.decode()
    loader=(RAW/'native/MaterialsTextureLoader.asm.txt').read_text()
    material=(RAW/'native/Material.asm.txt').read_text()
    relocation_blob=gzip.decompress((ROOT/'reverse-engineering/raw/ui-audit/native-relocations.json.gz').read_bytes())
    metadata_blob=gzip.decompress((ROOT/'reverse-engineering/raw/ui-audit/metadata-index.json.gz').read_bytes())
    relocations=json.loads(relocation_blob)
    assert relocations['native_sha256']==chains['binary_inputs_sha256']['lib/arm64-v8a/libil2cpp.so']
    metadata=json.loads(metadata_blob)
    checks={
        'path_basename_without_extension': '0x222f61c: bl       #0x20848cc' in loader and 'public static string GetFileNameWithoutExtension(string path)' in dump,
        'owner_atlas_material_array': '0x222f628: ldr      x25, [x8, #0x20]' in loader,
        'get_main_texture': '0x222f668: bl       #0x2769448' in loader,
        'texture_get_name': '0x222f6ac: bl       #0x2784a54' in loader and 'public string get_name()' in dump,
        'string_equality': '0x222f6b8: bl       #0x1feca34' in loader,
        'first_match_break': '0x222f6bc: tbnz     w0, #0, #0x222f6d4' in loader,
        'page_material_assignment': '0x222f76c: str      x21, [x19, #0x30]' in loader,
        'width_height_guard_not_unconditional_resize': all(x in loader for x in ['0x222f768: ldr      w8, [x19, #0x38]', '0x222f770: cbz      w8, #0x222f77c', '0x222f778: cbnz     w8, #0x222f7c0']),
        'main_texture_attribute_128': '0x2769494: mov      w1, #0x80' in material and 'MainTexture = 128;' in dump,
        'negative_attribute_search_fallback': '0x27694a0: tbnz     w0, #0x1f, #0x27694dc' in material,
        'fallback_GetTexture_string': '0x27694f4: b        #0x276953c' in material and 'public Texture GetTexture(string name)' in dump,
        'fallback_string_pointer': relocations['relocations']['0x2adcd60']=='0x2bea600' and any(r['Address']==0x2bea600 and r['Value']=='_MainTex' for r in metadata['tables']['ScriptString']),
    }
    assert all(checks.values()), checks
    native_methods=[m for path in (RAW/'native').glob('*.json') for m in json.loads(path.read_text())['methods']]
    assert all(not m['size_capped'] for m in native_methods)
    result['native_policy']=dict(checks=checks,native_method_count=len(native_methods),loader_rva='0x222f580',main_texture_rva='0x2769448',
                                 duplicate_local_policy='Native picks first matching material; derived exporter conservatively rejects ambiguous candidates.',
                                 atlas_dimensions_policy='If both parsed page width and height are nonzero, loader does not replace them with texture dimensions.')
    result['sources']=[dict(path='reverse-engineering/raw/ui-audit/native-relocations.json.gz',sha256_decompressed=hashlib.sha256(relocation_blob).hexdigest()),
                       dict(path='reverse-engineering/raw/ui-audit/metadata-index.json.gz',sha256_decompressed=hashlib.sha256(metadata_blob).hexdigest()),dict(path='reverse-engineering/raw/spine-identity/index.json',sha256=hashlib.sha256((RAW/'index.json').read_bytes()).hexdigest()),
                       dict(path='reverse-engineering/raw/asset-pack-v2/catalog.json.gz',sha256_decompressed=hashlib.sha256(gzip.decompress((ROOT/'reverse-engineering/raw/asset-pack-v2/catalog.json.gz').read_bytes())).hexdigest())]
    return result


if __name__=='__main__':
    output=ROOT/'datas/spine_identity.json'
    output.write_text(json.dumps(build(),ensure_ascii=False,indent=2)+'\n')
    print(output.relative_to(ROOT))
