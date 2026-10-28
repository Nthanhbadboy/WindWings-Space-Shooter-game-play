"""Recover file-scoped Spine chain metadata and narrow native loader evidence.

No original PNG, font, audio or skeleton payload is committed.
"""
import argparse
from collections import Counter
import gzip
import io
import json
from pathlib import Path
import sys
import zipfile

from asset_pack_v2 import extract_payload, serialized_files, sha
from audio_native import INPUTS

ROOT = Path(__file__).resolve().parents[2]
SELECTED = {'SkeletonDataAsset', 'SpineAtlasAsset', 'SpineSpriteAtlasAsset'}
NATIVE = {'SpineAtlasAsset', 'MaterialsTextureLoader', 'Material'}


def walk_pointers(value, location=''):
    if isinstance(value, dict):
        if 'm_FileID' in value and 'm_PathID' in value:
            yield location, value
        else:
            for key, child in value.items():
                yield from walk_pointers(child, location + '.' + str(key))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            yield from walk_pointers(child, location + f'[{index}]')


def atlas_pages(text):
    """Preserve page names/headers, not region image content; no basename joining."""
    lines = text.replace('\r\n', '\n').split('\n')
    pages = []
    for index, line in enumerate(lines):
        if not line or line[:1].isspace() or ':' in line:
            continue
        if index and lines[index-1].strip():
            continue
        if index+1 >= len(lines) or not lines[index+1].startswith('size:'):
            continue
        headers = []
        for follow in lines[index+1:]:
            if ':' not in follow or follow[:1].isspace():
                break
            headers.append(follow)
        pages.append(dict(line_index=index, name=line, header_lines=headers))
    return pages


def recover(xapk, work, out):
    import UnityPy
    from UnityPy.classes.PPtr import PPtr
    from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
    inputs = extract_payload(xapk, work / 'input')
    with zipfile.ZipFile(xapk) as outer:
        found = {}
        for entry in outer.namelist():
            if not entry.endswith('.apk'):
                continue
            with zipfile.ZipFile(io.BytesIO(outer.read(entry))) as part:
                for name in INPUTS.keys() & set(part.namelist()):
                    blob = part.read(name)
                    assert sha(blob) == INPUTS[name]
                    (work / Path(name).name).write_bytes(blob)
                    found[name] = sha(blob)
    assert found == INPUTS
    env = UnityPy.load(*(str(p) for p in sorted((work / 'input').iterdir())))
    generator = TypeTreeGenerator('2022.3.62f3', generator='AssetStudio')
    generator.load_il2cpp((work/'libil2cpp.so').read_bytes(), (work/'global-metadata.dat').read_bytes())
    env.typetree_generator = generator
    files = serialized_files(env)
    file_ids = {id(sf): logical for logical, sf in files}
    def identity(obj):
        return dict(serialized_file=file_ids[id(obj.assets_file)], type=obj.type.name, path_id=int(obj.path_id))
    def key(obj):
        return (file_ids[id(obj.assets_file)], int(obj.path_id))
    script_cache = {}
    class_cache = {}
    head_errors = []
    counts = Counter()
    roots = []
    for _, sf in files:
        for obj in sf.objects.values():
            if obj.type.name != 'MonoBehaviour':
                continue
            counts['MonoBehaviour_scanned'] += 1
            try:
                head = obj.parse_monobehaviour_head()
                ptr = head.m_Script
                script_key = (id(sf), ptr.m_FileID, ptr.m_PathID)
                if script_key not in script_cache:
                    script = ptr.deref_parse_as_object()
                    script_cache[script_key] = (script.m_Namespace, script.m_ClassName)
                namespace, cls = script_cache[script_key]
                class_cache[key(obj)] = (namespace, cls)
                if cls in SELECTED and namespace == 'Spine.Unity':
                    roots.append(obj)
                    counts[cls] += 1
            except Exception as error:
                head_errors.append(dict(**identity(obj), error=repr(error)))
    rows = {}
    links = []
    def record(obj):
        ident = key(obj)
        if ident in rows:
            return
        row = dict(**identity(obj), raw_object_sha256=sha(obj.get_raw_data()))
        rows[ident] = row
        kind = obj.type.name
        if kind == 'MonoBehaviour':
            row['namespace'], row['class_name'] = class_cache[ident]
            head = obj.parse_monobehaviour_head()
            row['parsed_header'] = dict(m_Script=dict(m_FileID=head.m_Script.m_FileID,m_PathID=head.m_Script.m_PathID))
        try:
            if kind == 'Texture2D':
                data = obj.read()
                row.update(name=data.m_Name, projection='metadata_only_no_pixels', width=data.m_Width, height=data.m_Height)
            elif kind == 'Shader':
                tree = obj.read_typetree()
                row.update(name=tree.get('m_Name',''), projection='shader_property_metadata_no_shader_program',
                           properties=tree.get('m_ParsedForm',{}).get('m_PropInfo',{}))
            elif kind == 'TextAsset':
                data = obj.read()
                script = data.m_Script
                blob = script.encode('utf-8', 'surrogateescape') if isinstance(script, str) else bytes(script)
                row.update(name=data.m_Name, projection='payload_hash_and_headers_no_original_asset', payload_sha256=sha(blob), payload_bytes=len(blob))
                text = blob.decode('utf-8', 'surrogateescape')
                row['atlas_pages'] = atlas_pages(text)
                if not row['atlas_pages']:
                    sk = json.loads(text)
                    row['skeleton_header'] = sk.get('skeleton', {})
                    row['animation_names'] = list(sk.get('animations', {}))
            else:
                tree = obj.read_typetree()
                row.update(name=tree.get('m_Name',''), projection='full_typetree', tree=tree)
                for location, ptr in walk_pointers(tree):
                    if kind == 'MonoBehaviour':
                        if not (location.startswith('.atlasAssets[') or location == '.skeletonJSON' or location == '.atlasFile' or location.startswith('.materials[') or location == '.spriteAtlasFile' or (location.startswith('.blendModeMaterials.') and location.endswith('.material'))):
                            continue
                    elif kind == 'Material':
                        if not (location.startswith('.m_SavedProperties.m_TexEnvs') or location == '.m_Shader'):
                            continue
                    else:
                        continue
                    link = dict(owner=identity(obj), location=location, pointer=ptr)
                    links.append(link)
                    if not ptr['m_PathID']:
                        link['status']='null'
                        continue
                    try:
                        target = PPtr(m_FileID=ptr['m_FileID'], m_PathID=ptr['m_PathID'], assetsfile=obj.assets_file).deref()
                        link.update(status='resolved', target=identity(target))
                        if target.type.name in ('MonoBehaviour','Material','Texture2D','TextAsset','Shader'):
                            record(target)
                    except Exception as error:
                        link.update(status='unresolved', error=repr(error))
            row['status']='recovered'
        except Exception as error:
            row.update(status='failed', error=repr(error))
    for obj in roots:
        record(obj)
    info = dict(status='provisional_file_scoped_Spine_chain_not_import_approval', inputs=inputs,
                binary_inputs_sha256=found, toolchain=dict(UnityPy=UnityPy.__version__,TypeTreeGeneratorAPI='0.0.10',backend='AssetStudio'),
                scan_counts=dict(counts), header_errors=head_errors, all_MB_headers_classified=not head_errors,
                files=[dict(serialized_file=logical,externals=[dict(path=e.path,type=e.type) for e in sf.externals]) for logical,sf in files],
                objects=sorted(rows.values(),key=lambda r:(r['serialized_file'],r['path_id'])),links=links)
    out.mkdir(parents=True,exist_ok=True)
    (out/'chains.json.gz').write_bytes(gzip.compress((json.dumps(info,ensure_ascii=True,indent=2)+'\n').encode(),mtime=0))
    # Missing built-in resources keep header classification explicitly incomplete;
    # do not discard the fully resolved selected graph or assert it is exhaustive.
    assert counts['SkeletonDataAsset'] > 0
    assert all(r['status']=='recovered' for r in rows.values())
    assert all(l['status'] in ('resolved','null') for l in links)
    # Keep full method boundaries, while hiding unrelated classes from auto-selection.
    sys.path.insert(0,str(ROOT/'tools/apk-analyze'))
    import il2cpp_consts as native
    dump = work/'dump.cs'
    dump.write_bytes(gzip.decompress((ROOT/'reverse-engineering/il2cpp/dump.cs.gz').read_bytes()))
    all_rows = native.parse_dump(str(dump))
    native.parse_dump = lambda _: [(cls if cls in NATIVE and (cls != 'Material' or name == 'get_mainTexture') else '__not_selected__',ns,name,offset,rva,sig) for cls,ns,name,offset,rva,sig in all_rows]
    native.TARGET_CLASSES.clear()
    native.TARGET_CLASSES.update({cls:'Pinned Spine loader native recovery' for cls in NATIVE})
    native.OUT_RAW=str(out/'native')
    native.OUT_MD=str(work/'native.md')
    native.OUT_CSV=str(work/'native.csv')
    sys.argv=['native',str(dump),str(work/'libil2cpp.so')]
    assert native.main()==0
    manifest=[]
    for path in [out/'chains.json.gz', *sorted((out/'native').iterdir())]:
        if not path.is_file():
            continue
        assert path.stat().st_size < 5_000_000
        blob=path.read_bytes()
        if path.suffix=='.gz':blob=gzip.decompress(blob)
        manifest.append(dict(path=path.relative_to(out).as_posix(),sha256_decompressed=sha(blob)))
    (out/'index.json').write_text(json.dumps(dict(files=manifest,scan_counts=dict(counts),dump_sha256_decompressed=sha(dump.read_bytes())),indent=2)+'\n')
    print(json.dumps(dict(scan_counts=counts,objects=len(rows),links=len(links),header_errors=len(head_errors)),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--xapk',required=True,type=Path)
    parser.add_argument('--work',required=True,type=Path)
    args=parser.parse_args()
    recover(args.xapk,args.work,ROOT/'reverse-engineering/raw/spine-identity')
