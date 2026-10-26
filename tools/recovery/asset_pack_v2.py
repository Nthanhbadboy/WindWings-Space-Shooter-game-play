"""Narrow pinned Unity re-export with object identities and explicit exceptions.

Original media stays outside Git. This script does not call the legacy exporter.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import html
import io
import json
from pathlib import Path
import re
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[2]
XAPK_SHA = 'f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
DATA_SHA = '7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7'
TARGETS = {'Sprite', 'Texture2D', 'AudioClip', 'Font', 'TextAsset', 'SpriteAtlas'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def identity_path(serialized_file, kind, path_id):
    """Full logical file path is hashed, not just its potentially colliding basename."""
    label = re.sub(r'[^A-Za-z0-9._-]', '_', Path(serialized_file).name)[:48] or 'file'
    if kind not in TARGETS:
        raise ValueError(kind)
    return f'{kind}/{label}__{sha(serialized_file.encode())}__{int(path_id)}'


def serialized_files(env):
    """Walk bundle hierarchy. A SerializedFile.files property aliases its objects."""
    found = []
    visited = set()
    def visit(node, logical):
        if id(node) in visited:
            raise ValueError('aliased file node: ' + logical)
        visited.add(id(node))
        objects = getattr(node, 'objects', None)
        if isinstance(objects, dict):
            found.append((logical, node))
            return
        for key, child in sorted(getattr(node, 'files', {}).items(), key=lambda x: str(x[0])):
            visit(child, logical + '/' + str(key))
    for key, node in sorted(env.files.items(), key=lambda x: str(x[0])):
        # All extraction files are relative to one root; absolute runner dirs are not identities.
        visit(node, Path(str(key)).name)
    if len({p for p, _ in found}) != len(found):
        raise ValueError('duplicate serialized-file logical paths')
    return found


def extract_payload(xapk, directory):
    if sha(xapk.read_bytes()) != XAPK_SHA:
        raise ValueError('XAPK hash mismatch')
    directory.mkdir(parents=True, exist_ok=False)
    inputs = []
    with zipfile.ZipFile(xapk) as outer:
        for part_name in sorted(outer.namelist()):
            if not part_name.endswith('.apk'):
                continue
            with zipfile.ZipFile(io.BytesIO(outer.read(part_name))) as part:
                for name in sorted(part.namelist()):
                    prefix = 'assets/bin/Data/'
                    if not name.startswith(prefix) or name.endswith('/'):
                        continue
                    rel = name[len(prefix):]
                    # Only Unity bundle/serialized/resource inputs, not metadata or code.
                    if '/' in rel or not (rel == 'globalgamemanagers' or rel.endswith(('.unity3d', '.assets', '.resource', '.resS', '.bundle'))):
                        continue
                    data = part.read(name)
                    target = directory / rel
                    if target.exists():
                        raise ValueError('duplicate payload name ' + rel)
                    target.write_bytes(data)
                    inputs.append(dict(apk=part_name, entry=name, file=rel, bytes=len(data), sha256=sha(data)))
    if not any(r['file'] == 'data.unity3d' and r['sha256'] == DATA_SHA for r in inputs):
        raise ValueError('pinned Unity payload missing')
    return inputs


def text_bytes(value):
    return value.encode('utf-8', 'surrogateescape') if isinstance(value, str) else bytes(value)


def font_extension(data):
    if data[:4] == b'OTTO':
        return '.otf'
    if data[:4] in (b'\x00\x01\x00\x00', b'true', b'ttcf'):
        return '.ttc' if data[:4] == b'ttcf' else '.ttf'
    raise ValueError('unrecognized embedded font signature')


def pointer_ref(pointer, file_ids):
    if pointer is None:
        return None
    ref = dict(file_id=int(pointer.m_FileID), path_id=int(pointer.m_PathID))
    if not ref['path_id']:
        ref['resolution'] = 'null'
        return ref
    try:
        obj = pointer.deref()
        ref.update(serialized_file=file_ids[id(obj.assets_file)], type=obj.type.name,
                   resolved_path_id=int(obj.path_id), resolution='resolved')
    except Exception as error:
        ref.update(resolution='unresolved', error=repr(error))
    return ref


def export(env, destination, inputs):
    from UnityPy.export.AudioClipConverter import extract_audioclip_samples
    from PIL import Image
    destination.mkdir(parents=True, exist_ok=False)
    files = serialized_files(env)
    ids = {id(sf): logical for logical, sf in files}
    objects = [(logical, obj) for logical, sf in files for obj in sf.objects.values()]
    if {id(obj) for _, obj in objects} != {id(obj) for obj in env.objects}:
        raise ValueError('serialized traversal disagrees with env.objects')
    if len(objects) != len({id(obj) for _, obj in objects}):
        raise ValueError('duplicate object traversal')
    rows = []
    identities = set()
    used_paths = set()
    inventory = []
    for logical, sf in files:
        inventory.append(dict(serialized_file=logical, name=str(sf.name),
                              unity_version=str(sf.unity_version), object_count=len(sf.objects),
                              types=dict(Counter(o.type.name for o in sf.objects.values()))))
    for logical, obj in sorted(objects, key=lambda x: (x[0], x[1].type.name, int(x[1].path_id))):
        kind = obj.type.name
        if kind not in TARGETS:
            continue
        identity = (logical, kind, int(obj.path_id))
        if identity in identities:
            raise ValueError('duplicate object identity ' + str(identity))
        identities.add(identity)
        stem = identity_path(*identity)
        row = dict(serialized_file=logical, type=kind, path_id=int(obj.path_id), name='',
                   status='pending', outputs=[])
        rows.append(row)
        def write(suffix, content, **metadata):
            path = stem + suffix
            if path in used_paths:
                raise ValueError('output collision ' + path)
            used_paths.add(path)
            target = destination / path
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as handle:
                handle.write(content)
            row['outputs'].append(dict(path=path, bytes=len(content), sha256=sha(content), **metadata))
        try:
            data = obj.read()
            row['name'] = str(getattr(data, 'm_Name', '') or '')
            if kind in ('Texture2D', 'Sprite'):
                if kind == 'Texture2D':
                    row['source_dimensions'] = [data.m_Width, data.m_Height]
                    row['texture_format'] = int(data.m_TextureFormat)
                else:
                    rd = getattr(data, 'm_RD', None)
                    row['texture_pointer'] = pointer_ref(getattr(rd, 'texture', None), ids)
                    row['sprite_atlas_pointer'] = pointer_ref(getattr(data, 'm_SpriteAtlas', None), ids)
                image = data.image
                if image is None:
                    raise ValueError('image decoder returned None')
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                blob = buffer.getvalue()
                # Full re-decode gate, not just PNG header parsing.
                with Image.open(io.BytesIO(blob)) as checked:
                    checked.load()
                    if checked.size != image.size:
                        raise ValueError('PNG dimension roundtrip mismatch')
                write('.png', blob, width=image.width, height=image.height)
            elif kind == 'AudioClip':
                row['channels'] = data.m_Channels
                row['frequency'] = data.m_Frequency
                row['length_seconds'] = data.m_Length
                samples = extract_audioclip_samples(data)
                if not samples:
                    raise ValueError('audio converter returned no samples')
                for index, (sample_name, blob) in enumerate(sorted(samples.items())):
                    ext = Path(str(sample_name)).suffix.lower()
                    if ext not in ('.wav', '.ogg', '.m4a', '.mp3'):
                        raise ValueError('unrecognized audio extension ' + ext)
                    write(f'__sample{index}{ext}', bytes(blob), sample_name=str(sample_name))
            elif kind == 'Font':
                blob = bytes(data.m_FontData or b'')
                if not blob:
                    row['status'] = 'no_embedded_font_data'
                    row['reason'] = 'Object exists; cannot export an absent font program. Not silently skipped.'
                    continue
                write(font_extension(blob), blob)
            elif kind == 'TextAsset':
                blob = text_bytes(data.m_Script)
                stripped = blob.lstrip()
                ext = '.json' if stripped[:1] in (b'{', b'[') else '.atlas.txt' if row['name'].endswith('.atlas') else '.txt'
                write(ext, blob)
            elif kind == 'SpriteAtlas':
                tree = obj.read_typetree()
                write('.json', (json.dumps(tree, ensure_ascii=True, indent=2)+'\n').encode())
            row['status'] = 'exported'
        except Exception as error:
            row['status'] = 'failed'
            row['error'] = repr(error)
        if len(rows) % 200 == 0:
            print(f'processed {len(rows)} target objects', flush=True)
    source_counts = Counter(obj.type.name for _, obj in objects if obj.type.name in TARGETS)
    accounted = Counter(r['type'] for r in rows)
    assert source_counts == accounted
    outputs = [o for r in rows for o in r['outputs']]
    for output in outputs:
        content = (destination / output['path']).read_bytes()
        if len(content) != output['bytes'] or sha(content) != output['sha256']:
            raise ValueError('written content mismatch')
    source_media = {p.relative_to(destination).as_posix() for p in destination.rglob('*') if p.is_file()}
    if source_media != {o['path'] for o in outputs}:
        raise ValueError('filesystem population mismatch')
    summary = dict(schema_version=2, status='provisional_static_export_not_runtime_approval',
                   xapk_sha256=XAPK_SHA, inputs=inputs, serialized_files=inventory,
                   scope=sorted(TARGETS), source_counts=dict(source_counts),
                   outcomes=dict(Counter(r['status'] for r in rows)), output_files=len(outputs),
                   gates=dict(all_source_targets_accounted=source_counts == accounted,
                              object_identities_unique=True, output_paths_unique=True,
                              output_hashes_and_sizes_match=True, filesystem_population_matches=True,
                              all_target_objects_exported=all(r['status'] == 'exported' for r in rows)),
                   limits=['All counts apply to loaded pinned Unity payload, not every possible APK resource.',
                           'Sprite PNG decoder output is not proof of original pixel/crop/mask fidelity.',
                           'Audio decoding is not listening approval; no timing equivalence claimed.',
                           'Spine source text preserved; renamed page paths need identity joins before import.',
                           'No embedded font bytes does not mean no runtime font.'], objects=rows)
    return summary


def browser_html(data):
    # JSON embedded safely for offline file:// usage; names never assigned to innerHTML.
    payload = json.dumps(data, ensure_ascii=True, separators=(',', ':')).replace('<', '\\u003c')
    return '''<!doctype html><html lang="vi"><meta charset="utf-8"><title>WindWings identity-safe pack v2</title>
<style>body{margin:24px;background:#101724;color:#edf2fa;font:15px system-ui}input,select,button{padding:10px;margin:5px;background:#243249;color:white;border:1px solid #546782}#grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}article{background:#1b2638;padding:12px;border-radius:8px;overflow-wrap:anywhere}img{width:100%;height:180px;object-fit:contain;background:repeating-conic-gradient(#283244 0 25%,#182033 0 50%) 0/18px 18px}small{display:block;color:#adc0d9}a{color:#8ad8ff}audio{width:100%}h2{font-size:16px}</style>
<h1>WindWings — identity-safe pack v2</h1><p>Static APK reference, provisional. Copy this browser beside the exported folders. Git copy contains metadata only, not media.</p>
<p>Objects are keyed by serialized-file + type + pathID. Exported ≠ verified original pixels/crop/mask, audio listening, font fallback or Spine import. Spine page references have NOT been rewritten.</p>
<pre id="summary"></pre><input id="q" placeholder="Name / pathID / serialized file"><select id="type"><option value="">All types</option></select><select id="status"><option value="">All outcomes</option></select><button id="prev">Previous</button><button id="next">Next</button><p id="count"></p><main id="grid"></main>
<script id="data" type="application/json">''' + payload + '''</script><script>
const data=JSON.parse(document.getElementById('data').textContent),$=id=>document.getElementById(id);let page=0;
$('summary').textContent=JSON.stringify({source_counts:data.source_counts,outcomes:data.outcomes,gates:data.gates},null,2);
for(const [id,key] of [['type','type'],['status','status']]){for(const value of [...new Set(data.objects.map(r=>r[key]))].sort()){let o=document.createElement('option');o.value=value;o.textContent=value;$(id).append(o)}}
function text(parent,tag,value){let e=document.createElement(tag);e.textContent=value;parent.append(e);return e}
function draw(){let query=$('q').value.toLowerCase();let rows=data.objects.filter(r=>(!$('type').value||r.type===$('type').value)&&(!$('status').value||r.status===$('status').value)&&[r.name,r.path_id,r.serialized_file].join(' ').toLowerCase().includes(query));let pages=Math.max(1,Math.ceil(rows.length/100));page=Math.min(page,pages-1);$('count').textContent=`${rows.length} objects · page ${page+1}/${pages}`;$('grid').replaceChildren();for(const r of rows.slice(page*100,(page+1)*100)){let card=document.createElement('article');text(card,'h2',r.name||'(unnamed)');text(card,'small',r.type+' · '+r.path_id+' · '+r.status);text(card,'small',r.serialized_file);if(r.error||r.reason)text(card,'p',r.error||r.reason);for(const o of r.outputs){let url=o.path.split('/').map(encodeURIComponent).join('/');if(o.path.endsWith('.png')){let img=document.createElement('img');img.loading='lazy';img.src=url;img.alt=r.name;card.append(img)}else if(r.type==='AudioClip'){let audio=document.createElement('audio');audio.controls=true;audio.preload='none';audio.src=url;card.append(audio)}let a=text(card,'a',o.path+' ('+o.bytes+' B)');a.href=url;a.target='_blank';text(card,'small','SHA256 '+o.sha256)}$('grid').append(card)}}
for(const id of ['q','type','status'])$(id).addEventListener('input',()=>{page=0;draw()});$('prev').onclick=()=>{page=Math.max(0,page-1);draw()};$('next').onclick=()=>{page++;draw()};draw();</script></html>'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--xapk', required=True, type=Path)
    parser.add_argument('--work', required=True, type=Path)
    args = parser.parse_args()
    import UnityPy
    inputs = extract_payload(args.xapk, args.work / 'input')
    paths = sorted((args.work / 'input').iterdir())
    env = UnityPy.load(*(str(p) for p in paths))
    data = export(env, args.work / 'pack', inputs)
    data['toolchain'] = dict(UnityPy=UnityPy.__version__)
    metadata = ROOT / 'reverse-engineering/raw/asset-pack-v2'
    metadata.mkdir(parents=True, exist_ok=True)
    content = (json.dumps(data, ensure_ascii=True, indent=2)+'\n').encode()
    (metadata / 'catalog.json.gz').write_bytes(gzip.compress(content, mtime=0))
    (args.work / 'pack/manifest-v2.json').write_bytes(content)
    browser = browser_html(data)
    (args.work / 'pack/index.html').write_text(browser)
    (ROOT / 'docs/assets/pack-browser-v2.html').write_text(browser)
    print(json.dumps({k:v for k,v in data.items() if k not in ('objects', 'serialized_files')}, indent=2), flush=True)
    # Explicit failures remain visible but do not prevent shipping an honestly partial draft.
    assert all(data['gates'][key] for key in data['gates'] if key != 'all_target_objects_exported')
    for path in metadata.iterdir():
        assert path.stat().st_size < 5_000_000


if __name__ == '__main__':
    main()
