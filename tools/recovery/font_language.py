"""Pinned font/fallback census and localization native recovery; no font programs/media."""
import argparse
from collections import Counter
import gzip
import io
import json
from pathlib import Path
import sys
import struct
import zipfile
from asset_pack_v2 import extract_payload,serialized_files,sha
from audio_native import INPUTS
from spine_identity import walk_pointers

ROOT=Path(__file__).resolve().parents[2]
ROOT_CLASSES={'TMP_FontAsset','TMP_Settings','FontAsset','LanguageAssets'}
TEXT_CLASSES={'TextMeshPro','TextMeshProUGUI'}
LABEL_CLASSES={'LanguageTextMeshPro','LanguageTextMeshProUI','LanguageTextMeshProFormats'}
NATIVE={
 'LanguageManager':None,'LanguageAssets':None,'LanguageTextMeshPro':None,'LanguageTextMeshProUI':None,'LanguageTextMeshProFormats':None,
 'TMP_Settings':{'get_defaultFontAsset','get_fallbackFontAssets'},
 'TMP_FontAsset':{'get_atlasPopulationMode','get_fallbackFontAssetTable','get_isMultiAtlasTexturesEnabled'},
 'TMP_FontAssetUtilities':{'GetCharacterFromFontAsset','GetCharacterFromFontAsset_Internal','GetCharacterFromFontAssets'},
}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--xapk',required=True,type=Path);parser.add_argument('--work',required=True,type=Path)
    args=parser.parse_args();work=args.work;out=ROOT/'reverse-engineering/raw/font-language';out.mkdir(parents=True,exist_ok=True)
    import UnityPy
    from UnityPy.classes.PPtr import PPtr
    from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
    inputs=extract_payload(args.xapk,work/'input')
    found={}
    with zipfile.ZipFile(args.xapk) as outer:
        for entry in outer.namelist():
            if not entry.endswith('.apk'):continue
            with zipfile.ZipFile(io.BytesIO(outer.read(entry))) as part:
                for name in INPUTS.keys() & set(part.namelist()):
                    blob=part.read(name);assert sha(blob)==INPUTS[name]
                    (work/Path(name).name).write_bytes(blob);found[name]=sha(blob)
    assert found==INPUTS
    env=UnityPy.load(*(str(p) for p in sorted((work/'input').iterdir())))
    gen=TypeTreeGenerator('2022.3.62f3',generator='AssetStudio');gen.load_il2cpp((work/'libil2cpp.so').read_bytes(),(work/'global-metadata.dat').read_bytes());env.typetree_generator=gen
    files=serialized_files(env);file_ids={id(sf):logical for logical,sf in files}
    def identity(obj):return dict(serialized_file=file_ids[id(obj.assets_file)],type=obj.type.name,path_id=int(obj.path_id))
    def key(obj):return(file_ids[id(obj.assets_file)],obj.path_id)
    scripts={};classes={};headers={};errors=[];roots=[];counts=Counter()
    for logical,sf in files:
        for obj in sf.objects.values():
            if obj.type.name=='Font':roots.append(obj);continue
            if obj.type.name!='MonoBehaviour':continue
            counts['MonoBehaviour_scanned']+=1
            try:
                head=obj.parse_monobehaviour_head();ptr=head.m_Script;sk=(id(sf),ptr.m_FileID,ptr.m_PathID)
                if sk not in scripts:
                    script=ptr.deref_parse_as_object();scripts[sk]=(script.m_Namespace,script.m_ClassName)
                namespace,cls=scripts[sk];classes[key(obj)]=(namespace,cls)
                if cls in ROOT_CLASSES|TEXT_CLASSES|LABEL_CLASSES:
                    counts[cls]+=1;roots.append(obj);headers[key(obj)]=dict(m_FileID=ptr.m_FileID,m_PathID=ptr.m_PathID)
            except Exception as error:errors.append(dict(**identity(obj),error=repr(error)))
    records={};links=[]
    def record(obj):
        ident=key(obj)
        if ident in records:return
        row=dict(**identity(obj),raw_object_sha256=sha(obj.get_raw_data()));records[ident]=row;kind=obj.type.name
        cls=''
        if kind=='MonoBehaviour':
            namespace,cls=classes.get(ident,('','unclassified'))
            row.update(namespace=namespace,class_name=cls)
            if ident in headers:row['parsed_script_pointer']=headers[ident]
        try:
            if kind=='Font':
                data=obj.read();program=bytes(data.m_FontData or b'')
                row.update(name=data.m_Name,projection='font_metadata_no_font_program',font_program_bytes=len(program),font_program_sha256=sha(program),
                           font_names=list(getattr(data,'m_FontNames',[]) or []))
            elif kind=='Texture2D':
                data=obj.read();row.update(name=data.m_Name,projection='texture_metadata_no_pixels',width=data.m_Width,height=data.m_Height)
            elif kind=='TextAsset':
                data=obj.read();value=data.m_Script;blob=value.encode('utf-8','surrogateescape') if isinstance(value,str) else bytes(value)
                row.update(name=data.m_Name,projection='textasset_payload_hash_no_original_asset',payload_bytes=len(blob),payload_sha256=sha(blob))
            elif kind in ('MonoBehaviour','Material'):
                tree=obj.read_typetree();row['name']=tree.get('m_Name','')
                if cls in TEXT_CLASSES:
                    keep={'m_fontAsset','m_sharedMaterial','m_fontSize','m_fontSizeBase','m_fontSizeMin','m_fontSizeMax','m_enableAutoSizing',
                          'm_fontStyle','m_isRightToLeft','m_enableWordWrapping','m_overflowMode','m_characterSpacing','m_lineSpacing','m_enableKerning'}
                    text=tree.get('m_text','') or ''
                    tree={k:v for k,v in tree.items() if k in keep}
                    row.update(projection='font_layout_and_text_codepoints',static_text_sha256=sha(text.encode('utf-8','surrogateescape')),
                               static_text_codepoints=sorted(set(map(ord,text))))
                elif cls in ROOT_CLASSES|LABEL_CLASSES or kind=='Material':row['projection']='full_typetree'
                else:
                    row.update(projection='referenced_component_identity_only',status='recovered');return
                row['tree']=tree
                for location,ptr in walk_pointers(tree):
                    if location in ('.m_Script','.m_GameObject'):continue
                    # Only font/layout/translation graph links, not every unrelated TMP sprite/style pointer.
                    if cls=='TMP_Settings' and not(location=='.m_defaultFontAsset' or location.startswith('.m_fallbackFontAssets[') or location in ('.m_leadingCharacters','.m_followingCharacters')):continue
                    if cls in TEXT_CLASSES and location not in ('.m_fontAsset','.m_sharedMaterial'):continue
                    if cls in LABEL_CLASSES and location!='.text':continue
                    if kind=='Material' and not location.startswith('.m_SavedProperties.m_TexEnvs'):continue
                    link=dict(owner=identity(obj),location=location,pointer=ptr);links.append(link)
                    if not ptr['m_PathID']:link['status']='null';continue
                    try:
                        target=PPtr(m_FileID=ptr['m_FileID'],m_PathID=ptr['m_PathID'],assetsfile=obj.assets_file).deref()
                        link.update(status='resolved',target=identity(target))
                        if target.type.name in ('MonoBehaviour','Font','Texture2D','Material','TextAsset'):record(target)
                    except Exception as error:link.update(status='unresolved',error=repr(error))
            else:row['projection']='identity_only'
            row['status']='recovered'
        except Exception as error:row.update(status='failed',error=repr(error))
    for obj in roots:record(obj)
    rows=sorted(records.values(),key=lambda r:(r['type'],r['serialized_file'],r['path_id']))
    chunks=[]
    for start in range(0,len(rows),100):
        group=rows[start:start+100];blob=''.join(json.dumps(r,ensure_ascii=True)+'\n' for r in group).encode()
        path=out/f'objects-{start//100:03}.jsonl.gz';path.write_bytes(gzip.compress(blob,mtime=0));assert path.stat().st_size<5_000_000
        chunks.append(dict(path=path.name,rows=len(group),sha256_decompressed=sha(blob)))
    link_blob=(json.dumps(links,ensure_ascii=True,indent=2)+'\n').encode();(out/'links.json.gz').write_bytes(gzip.compress(link_blob,mtime=0))
    info=dict(status='provisional_font_language_graph_not_glyph_render_approval',inputs=inputs,binary_inputs_sha256=found,
              toolchain=dict(UnityPy=UnityPy.__version__,TypeTreeGeneratorAPI='0.0.10',backend='AssetStudio'),scan_counts=dict(counts),header_errors=errors,
              all_MB_headers_classified=not errors,files=[dict(serialized_file=logical,externals=[dict(path=e.path,type=e.type) for e in sf.externals]) for logical,sf in files],
              chunks=chunks,links_sha256_decompressed=sha(link_blob),object_counts=dict(Counter(r.get('class_name',r['type']) for r in rows)),
              read_errors=[{k:r[k] for k in ('serialized_file','type','path_id','error')} for r in rows if r['status']=='failed'],
              unresolved_links=[l for l in links if l['status']=='unresolved'])
    (out/'graph-index.json').write_text(json.dumps(info,indent=2)+'\n')
    # Preserve exact method boundaries; select specific TMP getters instead of the entire runtime.
    sys.path.insert(0,str(ROOT/'tools/apk-analyze'));import il2cpp_consts as native
    dump=work/'dump.cs';dump.write_bytes(gzip.decompress((ROOT/'reverse-engineering/il2cpp/dump.cs.gz').read_bytes()))
    methods=native.parse_dump(str(dump));native.parse_dump=lambda _:[(cls if cls in NATIVE and (NATIVE[cls] is None or name in NATIVE[cls]) else '__not_selected__',ns,name,offset,rva,sig) for cls,ns,name,offset,rva,sig in methods]
    native.TARGET_CLASSES.clear();native.TARGET_CLASSES.update({c:'Pinned font/fallback/localization consumer recovery' for c in NATIVE})
    native.OUT_RAW=str(out/'native');native.OUT_MD=str(work/'native.md');native.OUT_CSV=str(work/'native.csv');sys.argv=['native',str(dump),str(work/'libil2cpp.so')]
    assert native.main()==0
    # Getter bounds systemLanguage 9..40 then indexes exactly 32 signed ints.
    va=0x779fb8;length=32*4
    segments=native.elf_segments(str(work/'libil2cpp.so'))
    segment=next(s for s in segments if s[0]<=va and va+length<=s[0]+s[2])
    offset=segment[1]+va-segment[0]
    with (work/'libil2cpp.so').open('rb') as binary:
        binary.seek(offset);blob=binary.read(length)
    (out/'native-data.json').write_text(json.dumps(dict(source='libil2cpp.so',source_sha256=INPUTS['lib/arm64-v8a/libil2cpp.so'],
        slices=[dict(consumer='LanguageManager.get_language',va=hex(va),file_offset=offset,bytes=length,hex=blob.hex(),sha256=sha(blob),
                     int32_le=list(struct.unpack('<32i',blob)))]),indent=2)+'\n')
    produced=[out/'native-data.json',out/'graph-index.json',out/'links.json.gz',*[out/c['path'] for c in chunks],*sorted((out/'native').iterdir())]
    files_manifest=[]
    for path in produced:
        blob=path.read_bytes();assert len(blob)<5_000_000
        if path.suffix=='.gz':blob=gzip.decompress(blob)
        files_manifest.append(dict(path=path.relative_to(out).as_posix(),sha256_decompressed=sha(blob)))
    (out/'index.json').write_text(json.dumps(dict(files=files_manifest,dump_sha256_decompressed=sha(dump.read_bytes())),indent=2)+'\n')
    print('::notice::'+json.dumps(dict(scan_counts=counts,objects=len(rows),read_errors=info['read_errors'][:3],unresolved_links=len(info['unresolved_links']),header_errors=len(errors))))
    assert not info['read_errors']


if __name__=='__main__':main()
