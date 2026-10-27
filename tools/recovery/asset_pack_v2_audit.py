"""Independent archive audit and narrowly scoped zero-size Texture2D evidence."""
import argparse
from collections import Counter
import gzip
import hashlib
import io
import json
from pathlib import Path
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def audit_archive(archive, catalog):
    from PIL import Image
    from fontTools.ttLib import TTFont
    actual_digest = sha(archive.read_bytes())
    expected = {o['path']: (r, o) for r in catalog['objects'] for o in r['outputs']}
    if len(expected) != catalog['output_files']:
        raise ValueError('manifest output collision')
    audio = []
    fonts = []
    atlas_pages = []
    text_kinds = Counter()
    png_count = 0
    with zipfile.ZipFile(archive) as zipped:
        names = zipped.namelist()
        if len(names) != len(set(names)):
            raise ValueError('duplicate ZIP member names')
        if any(n.startswith('/') or '..' in Path(n).parts for n in names):
            raise ValueError('unsafe ZIP member name')
        if zipped.testzip() is not None:
            raise ValueError('ZIP CRC failure')
        if json.loads(zipped.read('manifest-v2.json')) != catalog:
            raise ValueError('archive manifest differs from preserved catalog')
        file_names = {i.filename for i in zipped.infolist() if not i.is_dir()}
        if file_names != set(expected) | {'manifest-v2.json', 'index.html'}:
            raise ValueError('ZIP population mismatch')
        texture_names = {}
        for r in catalog['objects']:
            if r['type'] == 'Texture2D':
                texture_names.setdefault(r['name'], []).append(dict(serialized_file=r['serialized_file'], path_id=r['path_id'], status=r['status'], outputs=r['outputs']))
        for path, (row, output) in expected.items():
            blob = zipped.read(path)
            if len(blob) != output['bytes'] or sha(blob) != output['sha256']:
                raise ValueError('member hash/size mismatch: ' + path)
            if row['type'] in ('Sprite', 'Texture2D'):
                with Image.open(io.BytesIO(blob)) as image:
                    image.load()
                    if list(image.size) != [output['width'], output['height']]:
                        raise ValueError('PNG dimension mismatch')
                png_count += 1
            elif row['type'] == 'AudioClip':
                if not path.endswith('.wav'):
                    raise ValueError('audio codec needs separate audit: ' + path)
                with wave.open(io.BytesIO(blob), 'rb') as wav:
                    audio.append(dict(path=path, channels=wav.getnchannels(), frequency=wav.getframerate(),
                                      frames=wav.getnframes(), duration_seconds=wav.getnframes()/wav.getframerate()))
            elif row['type'] == 'Font':
                font = TTFont(io.BytesIO(blob))
                fonts.append(dict(path=path, glyphs=len(font.getGlyphOrder()), tables=sorted(font.keys()),
                                  unicode_codepoints=len(font.getBestCmap() or {})))
                font.close()
            elif row['type'] == 'SpriteAtlas':
                json.loads(blob)
            elif row['type'] == 'TextAsset':
                # Source atlas text is not rewritten. Page name only gives candidates,
                # never a proof of SkeletonDataAsset -> AtlasAsset -> Material identity.
                text = blob.decode('utf-8', 'surrogateescape')
                try:
                    parsed = json.loads(text)
                except (ValueError, UnicodeError):
                    parsed = None
                if isinstance(parsed, dict) and 'skeleton' in parsed and 'bones' in parsed:
                    text_kinds['spine_skeleton_json'] += 1
                elif '\nsize:' in text and ('\nformat:' in text or '\nfilter:' in text):
                    text_kinds['atlas_text'] += 1
                    # Spine atlas page: first line, or line after an empty separator;
                    # check that the next line contains a page-level size field.
                    lines = text.replace('\r\n', '\n').split('\n')
                    for index, line in enumerate(lines):
                        if not line.strip() or line[:1].isspace() or ':' in line:
                            continue
                        if index and lines[index-1].strip():
                            continue
                        if index+1 >= len(lines) or not lines[index+1].startswith('size:'):
                            continue
                        candidates = texture_names.get(Path(line).stem, [])
                        atlas_pages.append(dict(textasset=dict(serialized_file=row['serialized_file'],path_id=row['path_id'],name=row['name']),
                                                page=line, join_status='name_candidates_only_not_identity_proof', texture_candidates=candidates))
                else:
                    text_kinds['other_text'] += 1
    return dict(schema_version=1, status='provisional_archive_validation_not_visual_or_runtime_approval',
                archive_sha256=actual_digest, archive_bytes=archive.stat().st_size,
                media_files_verified=len(expected), png_full_decodes=png_count,
                audio=audio, audio_duration_seconds=sum(a['duration_seconds'] for a in audio), fonts=fonts,
                text_classification=dict(text_kinds), spine_atlas_page_candidates=atlas_pages,
                gates=dict(zip_crc=True, unique_zip_names=True, exact_media_population=True,
                           member_sha256_and_sizes=True, png_full_decode=True, wav_headers=True,
                           embedded_font_parse=True, preserved_manifest_equal=True),
                limits=['Atlas page names give candidates only; no global basename identity proof.',
                        'No listening, rendered crop/mask/fractional rect or Spine import approval.',
                        'Zero-size Texture2D exception remains visible in source catalog.'])


def recover_exception(xapk, work):
    from asset_pack_v2 import extract_payload, serialized_files
    import UnityPy
    extract_payload(xapk, work / 'input')
    env = UnityPy.load(*(str(p) for p in sorted((work / 'input').iterdir())))
    sf = dict(serialized_files(env))['data.unity3d/resources.assets']
    obj = sf.objects[535]
    assert obj.type.name == 'Texture2D'
    tree = obj.read_typetree()
    assert tree['m_Name'] == 'Font Texture' and tree['m_Width'] == 0 and tree['m_Height'] == 0
    # Metadata only: refuse accidentally embedding any original pixel payload.
    image = tree.get('image data', tree.get('m_ImageData', []))
    assert not image
    def safe(value):
        if isinstance(value, bytes):
            assert not value
            return []
        if isinstance(value, dict):
            return {k:safe(v) for k,v in value.items()}
        if isinstance(value, list):
            return [safe(v) for v in value]
        return value
    return dict(serialized_file='data.unity3d/resources.assets', type='Texture2D', path_id=535,
                typetree=safe(tree), raw_object_sha256=sha(obj.get_raw_data()),
                conclusion='Serialized dimensions are zero; no PNG invented. Runtime font texture generation not established here.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', required=True, type=Path)
    parser.add_argument('--xapk', required=True, type=Path)
    parser.add_argument('--work', required=True, type=Path)
    args = parser.parse_args()
    folder = ROOT / 'reverse-engineering/raw/asset-pack-v2'
    catalog = json.loads(gzip.decompress((folder / 'catalog.json.gz').read_bytes()))
    upload = json.loads((folder / 'release-upload.json').read_text())
    result = audit_archive(args.archive, catalog)
    asset = next(a for a in upload['assets'] if a['name'] == args.archive.name)
    assert asset['size'] == result['archive_bytes']
    assert asset['digest'] == 'sha256:' + result['archive_sha256']
    browser = (ROOT / 'docs/assets/pack-browser-v2.html').read_bytes()
    with zipfile.ZipFile(args.archive) as zipped:
        assert zipped.read('index.html') == browser
    result['gates']['release_digest_matches'] = True
    result['gates']['browser_matches'] = True
    (folder / 'archive-audit.json.gz').write_bytes(gzip.compress((json.dumps(result, indent=2)+'\n').encode(), mtime=0))
    exception = recover_exception(args.xapk, args.work)
    (folder / 'font-texture-exception.json').write_text(json.dumps(exception, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('audio','spine_atlas_page_candidates')}, indent=2))
    print(json.dumps(exception, indent=2))


if __name__ == '__main__':
    main()
