"""Regenerate file-scoped font/translation contracts. Static evidence, not rendering."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
from early_ui_native import section
from ui_loader_analysis import metadata_loads
from ui_routing import direct_calls

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'reverse-engineering/raw/font-language'
TEXT={'TextMeshPro','TextMeshProUGUI'}
LABEL={'LanguageTextMeshPro','LanguageTextMeshProFormats','LanguageTextMeshProUI'}


def sha(blob):return hashlib.sha256(blob).hexdigest()
def unpack(path):
    blob=path.read_bytes()
    return gzip.decompress(blob) if path.suffix=='.gz' else blob

def ident(row):return(row['serialized_file'],row['type'],row['path_id'])
def identity(row):return{k:row[k] for k in ('serialized_file','type','path_id')}

def first_values(keys,values):
    assert len(keys)==len(values)
    result={}
    for key,value in zip(keys,values):result.setdefault(key,value)
    return result

def lookup(keys,values,key):return first_values(keys,values).get(key)
def translated(keys,values,default_keys,default_values,key,force_default=False):
    value=None if force_default else lookup(keys,values,key)
    if value is None or value=='':value=lookup(default_keys,default_values,key)
    return key if value is None or value=='' else value


def enum(dump,name):
    block=re.search(r'\benum '+name+r'[^}]+}',dump)[0]
    return {m[1]:int(m[2]) for m in re.finditer(r'public const '+name+r' (\w+) = (-?\d+);',block)}


def build():
    manifest=json.loads((RAW/'index.json').read_text());source_hashes={}
    for f in manifest['files']:
        blob=unpack(RAW/f['path']);assert sha(blob)==f['sha256_decompressed'],f['path']
        source_hashes['reverse-engineering/raw/font-language/'+f['path']]=sha(blob)
    dump_blob=unpack(ROOT/'reverse-engineering/il2cpp/dump.cs.gz');assert sha(dump_blob)==manifest['dump_sha256_decompressed'];dump=dump_blob.decode()
    graph=json.loads((RAW/'graph-index.json').read_text());rows=[];locations={}
    for c in graph['chunks']:
        blob=unpack(RAW/c['path']);assert sha(blob)==c['sha256_decompressed']
        group=[json.loads(line) for line in blob.splitlines()];assert len(group)==c['rows']
        for row in group:
            locations[ident(row)]=dict(chunk=c['path'],identity=identity(row),raw_object_sha256=row['raw_object_sha256'])
        rows.extend(group)
    objects={ident(row):row for row in rows};assert len(objects)==len(rows)
    assert all(r['status']=='recovered' for r in rows) and not graph['read_errors'] and not graph['unresolved_links']
    assert dict(Counter(r.get('class_name',r['type']) for r in rows))==graph['object_counts']
    links_blob=unpack(RAW/'links.json.gz');assert sha(links_blob)==graph['links_sha256_decompressed'];links=json.loads(links_blob)
    files={f['serialized_file']:f for f in graph['files']};link_index={}
    for l in links:
        owner=ident(l['owner']);assert owner in objects
        assert (owner,l['location']) not in link_index
        link_index[owner,l['location']]=l
        if l['status']=='null':assert l['pointer']['m_PathID']==0;continue
        assert l['status']=='resolved' and ident(l['target']) in objects
        value=objects[owner]['tree']
        for field,index in re.findall(r'\.([^\[.]+)|\[(\d+)\]',l['location']):
            value=value[field] if field else value[int(index)]
        assert value==l['pointer'],l
        ptr=l['pointer'];target=l['target'];assert ptr['m_PathID']==target['path_id']
        expected=owner[0] if not ptr['m_FileID'] else 'data.unity3d/'+files[owner[0]]['externals'][ptr['m_FileID']-1]['path']
        assert expected==target['serialized_file'],l
    def linked(row,location):
        l=link_index[ident(row),location]
        return None if l['status']=='null' else objects[ident(l['target'])]
    catalog_blob=unpack(ROOT/'reverse-engineering/raw/asset-pack-v2/catalog.json.gz');catalog=json.loads(catalog_blob)
    assert graph['inputs']==catalog['inputs']
    outputs={ident(r):r for r in catalog['objects']}
    fonts=sorted((r for r in rows if r.get('class_name')=='TMP_FontAsset'),key=ident)
    settings=next(r for r in rows if r.get('class_name')=='TMP_Settings');default=linked(settings,'.m_defaultFontAsset')
    font_rows=[]
    for r in fonts:
        t=r['tree'];glyphs={g['m_Index'] for g in t['m_GlyphTable']}
        assert len(glyphs)==len(t['m_GlyphTable'])
        assert all(c['m_GlyphIndex'] in glyphs for c in t['m_CharacterTable'])
        atlases=[]
        for i,_ in enumerate(t['m_AtlasTextures']):
            a=linked(r,f'.m_AtlasTextures[{i}]');export=outputs[ident(a)]
            assert export['status']=='exported' and len(export['outputs'])==1
            assert [a['width'],a['height']]==export['source_dimensions']
            atlases.append(dict(identity=identity(a),png=export['outputs'][0],source_dimensions=[a['width'],a['height']]))
        for glyph in t['m_GlyphTable']:
            atlas=atlases[glyph['m_AtlasIndex']];rect=glyph['m_GlyphRect'];w,h=atlas['source_dimensions']
            assert 0<=rect['m_X']<=rect['m_X']+rect['m_Width']<=w
            assert 0<=rect['m_Y']<=rect['m_Y']+rect['m_Height']<=h
        fallbacks=[linked(r,f'.m_FallbackFontAssetTable[{i}]') for i in range(len(t['m_FallbackFontAssetTable']))]
        font_rows.append(dict(identity=identity(r),name=r['name'],raw=locations[ident(r)],family=t['m_FaceInfo']['m_FamilyName'],
            atlas_population_mode=t['m_AtlasPopulationMode'],render_mode=t['m_AtlasRenderMode'],source_font_file=t['m_SourceFontFile'],
            multi_atlas=t['m_IsMultiAtlasTexturesEnabled'],clear_dynamic_on_build=t['m_ClearDynamicDataOnBuild'],
            glyph_count=len(glyphs),character_count=len(t['m_CharacterTable']),character_table=t['m_CharacterTable'],
            face_info=t['m_FaceInfo'],weight_table=t['m_FontWeightTable'],glyph_table=t['m_GlyphTable'],atlas_dimensions=[t['m_AtlasWidth'],t['m_AtlasHeight']],atlas_padding=t['m_AtlasPadding'],
            atlases=atlases,material=identity(linked(r,'.material')),fallbacks=[identity(f) if f else None for f in fallbacks]))
    languages=enum(dump,'Language');system_languages=enum(dump,'SystemLanguage')
    chain=[default]+[linked(default,f'.m_FallbackFontAssetTable[{i}]') for i in range(len(default['tree']['m_FallbackFontAssetTable']))]
    assert len(chain)==len(fonts) and {ident(f) for f in chain}=={ident(f) for f in fonts}
    assert all(not f['tree']['m_FallbackFontAssetTable'] for f in chain[1:])
    cp={c['m_Unicode'] for f in chain for c in f['tree']['m_CharacterTable']}
    locale_rows=[]
    assets=[r for r in rows if r.get('class_name')=='LanguageAssets']
    english=next(r for r in assets if r['name']=='Language Assets English');e=english['tree']
    label_keys=Counter(r['tree']['key'] for r in rows if r.get('class_name') in LABEL)
    for r in sorted(assets,key=lambda r:languages[r['name'].removeprefix('Language Assets ')]):
        t=r['tree'];keys,values=t['listKey'],t['listValue'];assert keys==e['listKey'];first=first_values(keys,values);dupes=Counter(keys)
        # Raw stored string inventory: no rich-text parsing, normalization, case conversion or shaping.
        raw_cp=set(map(ord,''.join(first.values())))
        nonempty={k:v for k,v in first.items() if k}
        effective={k:translated(keys,values,e['listKey'],e['listValue'],k) for k in nonempty}
        locale_rows.append(dict(identity=identity(r),name=r['name'].removeprefix('Language Assets '),language=languages[r['name'].removeprefix('Language Assets ')],raw=locations[ident(r)],
            rows=len(keys),unique_keys_including_empty=len(first),nonempty_unique_keys=len(nonempty),empty_key_rows=dupes.get('',0),empty_value_rows=sum(v=='' for v in values),
            duplicates=[dict(key=k,indices=[i for i,x in enumerate(keys) if x==k],values=[values[i] for i,x in enumerate(keys) if x==k],first_value=first[k]) for k,n in dupes.items() if n>1],
            first_nonempty_key_values=nonempty,effective_nonempty_key_values=effective,
            serialized_label_keys_absent=[dict(key=k,component_count=n) for k,n in sorted(label_keys.items()) if k not in first],
            stored_value_codepoints=sorted(raw_cp),codepoints_absent_from_static_chain=sorted(raw_cp-cp)))
    refs=Counter();null_texts=[]
    for r in rows:
        if r.get('class_name') not in TEXT:continue
        target=linked(r,'.m_fontAsset')
        if target:refs[ident(target)]+=1
        else:null_texts.append(identity(r))
    snippets={p.stem.removesuffix('.asm'):p.read_text() for p in (RAW/'native').glob('*.asm.txt')}
    native_count=0
    for p in (RAW/'native').glob('*.json'):
        data=json.loads(p.read_text());assert data['methods'] and all(not m['size_capped'] for m in data['methods']);native_count+=len(data['methods'])
    la=section(snippets['LanguageAssets'],'GetText');lm=snippets['LanguageManager'];fu=snippets['TMP_FontAssetUtilities']
    checks={
        'asset_contains_then_first_index':all(x in la for x in ('[x20, #0x18]','#0x1bd81e0','#0x1bd8920','[x20, #0x20]','#0x1bd7b94','mov      x0, xzr')),
        'manager_empty_value_fallback_then_key':all(x in lm for x in ('#0x1fed004','#0x1438358','#0x1437f14','csel     x0, x19, x20, ne','csel     x0, x19, x21, ne')),
        'force_default_skips_selected_asset':'0x14385dc: tbnz     w20, #0, #0x143860c' in lm,
        'default_language_initializes_zero':'str      wzr, [x8]' in section(lm,'cctor'),
        'language_preference_and_system_default':all(x in section(lm,'get_language') for x in ('#0x275cd38','#0x13f1a1c','#0x779000','#0xfb8','cmp      w8, #0x1f')),
        'set_language_notifies_before_persist':lm.index('0x1438238: blr')<lm.index('0x1438268: bl       #0x13f1a04'),
        'font_fallback_list_is_0x138':'[x0, #0x138]' in snippets['TMP_FontAsset'],
        'character_dynamic_attempt_requires_mode_one':all(x in fu for x in ('ldr      w8, [x22, #0x48]','cmp      w8, #1','0x2715774: b.ne','bl       #0x270fc44')),
        'recursive_ordered_font_fallback':all(x in fu for x in ('[x22, #0x138]','mov      w25, wzr','bl       #0x2715520','add      w25, w25, #1')),
        'text_wrappers_call_gettext':all('#0x14386a8' in snippets[c] for c in LABEL),
    };assert all(checks.values()),checks
    metadata_blob=unpack(ROOT/'reverse-engineering/raw/ui-audit/metadata-index.json.gz');metadata=json.loads(metadata_blob)
    reloc_blob=unpack(ROOT/'reverse-engineering/raw/ui-audit/native-relocations.json.gz');reloc=json.loads(reloc_blob)
    assert reloc['native_sha256']==graph['binary_inputs_sha256']['lib/arm64-v8a/libil2cpp.so']
    meta_index={}
    for group,entries in metadata['tables'].items():
        for entry in entries:meta_index.setdefault(entry['Address'],[]).append(dict(entry,group=group))
    by_rva={}
    for block in re.split(r'(?=// Namespace:)',dump):
        cls=re.search(r'(?:class|enum) ([^ :\n]+)',block)
        if not cls:continue
        for m in re.finditer(r'// RVA: (0x[0-9a-f]+)[^\n]*\n([^\n]+)',block,re.I):
            by_rva[int(m[1],16)]=dict(class_name=cls[1],signature=m[2].strip())
    calls={cls:direct_calls(text,by_rva) for cls,text in snippets.items()}
    loads={cls:metadata_loads(text,reloc['relocations'],meta_index) for cls,text in snippets.items()}
    native_data=json.loads((RAW/'native-data.json').read_text());assert native_data['source_sha256']==reloc['native_sha256']
    table=native_data['slices'][0];data=bytes.fromhex(table['hex']);assert sha(data)==table['sha256']
    assert table['va']=='0x779fb8' and table['bytes']==len(data)==128
    switch=list(struct.unpack('<32i',data));assert table['int32_le']==switch
    def system_default(n):return switch[n-9] if 9<=n<=40 else 6 if n==1 else 13 if n==7 else 0
    for name in ('en','vi'):
        loc=next(l for l in locale_rows if l['name']=={'en':'English','vi':'Vietnamese'}[name]);public=json.loads((ROOT/f'i18n/{name}.json').read_text())
        assert public['strings']==loc['first_nonempty_key_values'],f'i18n/{name}.json must use native first-match values'
    return dict(status='PROVISIONAL_STATIC_NOT_RENDERING_RTL_SHAPING_OR_COMPLETE_RUNTIME_GLYPH_COVERAGE',
        sources_sha256_decompressed=source_hashes,dump_sha256_decompressed=sha(dump_blob),catalog_sha256_decompressed=sha(catalog_blob),
        scope=dict(object_counts=graph['object_counts'],scan_counts=graph['scan_counts'],header_errors=graph['header_errors'],all_MB_headers_classified=graph['all_MB_headers_classified']),
        enums={name:enum(dump,name) for name in ('Language','SystemLanguage','AtlasPopulationMode','GlyphRenderMode','FontStyles')},
        settings=dict(identity=identity(settings),raw=locations[ident(settings)],default_font=identity(default),global_fallback_pointers=settings['tree']['m_fallbackFontAssets'],
                      missing_glyph_character=settings['tree']['m_missingGlyphCharacter'],warnings_disabled=settings['tree']['m_warningsDisabled']),
        fonts=font_rows,static_chain_order=[identity(f) for f in chain],static_chain_unique_codepoints=len(cp),languages=locale_rows,
        text_components=dict(count=sum(refs.values())+len(null_texts),font_assignments=[dict(identity=dict(zip(('serialized_file','type','path_id'),k)),count=v) for k,v in sorted(refs.items())],null_font_components=null_texts,
                             right_to_left_counts=dict(Counter(str(r['tree']['m_isRightToLeft']) for r in rows if r.get('class_name') in TEXT)),
                             label_components=sum(label_keys.values())),
        native=dict(methods=native_count,checks=checks,resolved_direct_calls=calls,metadata_loads=loads,metadata_index_sha256_decompressed=sha(metadata_blob),relocations_sha256_decompressed=sha(reloc_blob),
                    system_default_by_enum=[dict(system_language=k,system_value=v,language_value=system_default(v)) for k,v in system_languages.items()]),
        limits=['Source class census has one explicit unresolved built-in script header; not an exhaustive runtime font claim.',
                'Stored-string codepoint deltas are not rendered missing glyphs: rich text, format arguments, style/case conversion, normalization, fallback mutation and shaping are not simulated.',
                'Global null fallback entry does not negate the main font asset six-entry fallback table.',
                'Native snippets are static checks, not an executed Unity font renderer; no new font programs or atlas pixels are generated.'])


def main():
    result=build();path=ROOT/'datas/font_language_contract.json.gz'
    path.write_bytes(gzip.compress((json.dumps(result,ensure_ascii=True,indent=2)+'\n').encode(),mtime=0))
    print(json.dumps(dict(fonts=len(result['fonts']),languages=len(result['languages']),text_components=result['text_components'],native_checks=result['native']['checks']),indent=2))


if __name__=='__main__':main()
