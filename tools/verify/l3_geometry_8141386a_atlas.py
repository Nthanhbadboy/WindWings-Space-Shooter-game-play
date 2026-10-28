"""#6 replication: static owning-file atlas map + independently decoded vertex bounds.
provenance: arena/8141386a-windwings-space-shooter-game-p
Disk-backed joins and one-record streams; no full Graph, all-Sprite fixture or native
remap/skinning/readback. Peer data is comparison evidence, NEVER a geometry source.
"""
from __future__ import annotations
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import sqlite3

from tools.verify.geometry_8141386a_atlas_io import (
    ROOT, RAW, BRANCH, JsonStream, canonical, full_file, identity, iter_arrays,
    iter_geometry, key, scratch, sha, sha_file, write_document,
)
from tools.verify.geometry_8141386a_atlas_sources import (
    DATA, XAPK, APK, QUERY, PINS, PEER, PEER_HEAD, verify_pins,
)
from tools.verify.l3_geometry_8141386a_atlas_binary import decode_mesh, encoded_object

OUT = ROOT / 'datas/l3_geometry_atlas_8141386a.json.gz'
WITNESS = RAW / 'byte-witness.json.gz'
MESH = ROOT / 'datas/sprite_mesh_contract.json.gz'
SURFACE = ROOT / 'reverse-engineering/raw/l3-visual-surface'


def document_header(path, stop='objects'):
    """Read only the small header preceding appended object records."""
    with gzip.open(path, 'rt', encoding='utf-8') as handle:
        s = JsonStream(handle)
        s.take('{')
        value = {}
        while True:
            name = s.value()
            s.take(':')
            if name == stop:
                s.take('[')
                return value
            if name in value:
                raise ValueError('duplicate witness header field')
            value[name] = s.value()
            s.take(',')


def render_key(value):
    if not isinstance(value, list) or len(value) != 2 or not isinstance(value[0], dict):
        raise ValueError('malformed complete render-data-key')
    guid, local = value
    if set(guid) != {f'data[{i}]' for i in range(4)}:
        raise ValueError('render-data-key GUID fields')
    words = [guid[f'data[{i}]'] for i in range(4)]
    if any(type(w) is not int or not 0 <= w < 2**32 for w in words):
        raise ValueError('render-data-key GUID word')
    if type(local) is not int or not -2**63 <= local < 2**63:
        raise ValueError('render-data-key local ID')
    return canonical(words + [local]).decode()


def resolve(owner_file, externals, pointer, files):
    """Exact owning-file/external path, never pathID-only or basename/name matching."""
    file_id, path_id = pointer['m_FileID'], pointer['m_PathID']
    if type(file_id) is not int or type(path_id) is not int or file_id < 0:
        raise ValueError('invalid PPtr integers')
    if path_id == 0:
        return None
    file = full_file(owner_file)
    if file_id:
        choices = [e['path'] for e in externals if e['file_id'] == file_id]
        if len(choices) != 1:
            raise ValueError('missing/ambiguous owning-file external PPtr')
        file = full_file(choices[0])
    if file not in files:
        raise ValueError('referenced file not captured: ' + file)
    return file, path_id


def static_zero(submeshes):
    if not submeshes:
        return False
    return all(all(s['localAABB'][field][axis] == 0 for axis in 'xyz')
               for s in submeshes for field in ('m_Center', 'm_Extent'))


def validate_witness(row, witness):
    if key(row) != key(witness['identity']) or row['type'] != witness['type']:
        raise ValueError('witness identity/type differs from source')
    if witness['object_sha256'] != row['object_bytes_sha256'] or witness['fresh_sha_matches_capture'] is not True:
        raise ValueError('fresh original SHA differs from source')
    expected, spans = encoded_object(row)
    if expected is None:
        if witness['whole_inverse_serialization_byte_equal'] is not None:
            raise ValueError('hash-only Texture2D misrepresented as decoded bytes')
        return
    if witness['whole_inverse_serialization_byte_equal'] is not True:
        raise ValueError('missing original full inverse-byte equality')
    if witness['object_table_entry']['byte_size'] != len(expected) or set(witness['spans']) != set(spans):
        raise ValueError('original object/span extent differs from source')
    for name, span in spans.items():
        observed = witness['spans'][name]
        if any(observed[k] != span[k] for k in ('offset', 'size', 'sha256')):
            raise ValueError('original span descriptor differs: ' + name)
        if not name.startswith('m_RenderDataMap['):
            part = bytes.fromhex(observed['hex'])
            if len(part) != span['size'] or sha(part) != span['sha256']:
                raise ValueError('original span hex invalid: ' + name)
            if part != expected[span['offset']:span['offset']+span['size']]:
                raise ValueError('original span bytes differ: ' + name)
    if row['type'] == 'Sprite' and witness['empty_counts_read_from_original'] != {
            'm_Bones.count': 0, 'm_RD.m_Bindpose.count': 0}:
        raise ValueError('original empty counts not corroborated')


def field_differences(ours, other):
    return [dict(field=k, own=ours.get(k), comparison=other.get(k))
            for k in sorted(set(ours) | set(other))
            if k not in ours or k not in other or canonical(ours[k]) != canonical(other[k])]


def build(path=OUT):
    selected = verify_pins()
    wh = document_header(WITNESS)
    if (wh['provenance'], wh['xapk_sha256'], wh['apk_sha256'], wh['bundle_sha256'], wh['query_sha256']) != (
            BRANCH, XAPK, APK, DATA, sha_file(QUERY)):
        raise ValueError('original witness source/provenance mismatch')
    for p, digest in wh['tool_pins'].items():
        if sha_file(ROOT / p) != digest:
            raise ValueError('original witness tool/query pin drift: ' + p)
    surface_index = json.loads((SURFACE / 'index.json').read_bytes())
    if surface_index['xapk_sha256'] != XAPK:
        raise ValueError('raw102 authority mismatch')
    files = {r['serialized_file'] for r in surface_index['files']}
    source_paths = {str(PINS.relative_to(ROOT)), str(QUERY.relative_to(ROOT)),
                    str(WITNESS.relative_to(ROOT)), str(PEER.relative_to(ROOT)),
                    str(MESH.relative_to(ROOT)), str((SURFACE / 'index.json').relative_to(ROOT)),
                    str((RAW/'source-ci-receipt.json.gz').relative_to(ROOT))}
    source_paths.update(selected['source_pins'])
    counts = Counter()
    outputs = Counter()

    with scratch('join-') as directory:
        db = sqlite3.connect(directory / 'atlas.sqlite')
        db.execute('PRAGMA cache_size=-4096')
        db.execute('CREATE TABLE raw(file TEXT,pid INTEGER,type TEXT,data TEXT,location TEXT,PRIMARY KEY(file,pid))')
        db.execute('CREATE TABLE witness(file TEXT,pid INTEGER,data TEXT,ordinal INTEGER,PRIMARY KEY(file,pid))')
        db.execute('CREATE TABLE compare(kind TEXT,file TEXT,pid INTEGER,data TEXT,PRIMARY KEY(kind,file,pid))')
        db.execute('CREATE TABLE packed(file TEXT,pid INTEGER,af TEXT,ap INTEGER,ordinal INTEGER,name TEXT,PRIMARY KEY(file,pid))')
        db.execute('CREATE TABLE maps(af TEXT,ap INTEGER,k TEXT,ordinal INTEGER,data TEXT,PRIMARY KEY(af,ap,k))')
        db.execute('CREATE TABLE used(af TEXT,ap INTEGER,k TEXT,PRIMARY KEY(af,ap,k))')
        db.execute('CREATE TABLE used_sprites(file TEXT,pid INTEGER,PRIMARY KEY(file,pid))')
        db.execute('CREATE TABLE out(kind TEXT,ordinal INTEGER,data TEXT,PRIMARY KEY(kind,ordinal))')

        def put(kind, row):
            db.execute('INSERT INTO out VALUES(?,?,?)', (kind, outputs[kind], canonical(row).decode()))
            outputs[kind] += 1

        def get(k, typ=None):
            if k is None:
                raise ValueError('unexpected null source target')
            result = db.execute('SELECT data,location FROM raw WHERE file=? AND pid=?', k).fetchone()
            if result is None:
                raise ValueError('target not captured: ' + str(k))
            row = json.loads(result[0])
            if typ is not None and row['type'] != typ:
                raise ValueError('PPtr target type mismatch: ' + str(k))
            return row, json.loads(result[1])

        def comparison(kind, k, ours):
            result = db.execute('SELECT data FROM compare WHERE kind=? AND file=? AND pid=?', (kind, *k)).fetchone()
            other = json.loads(result[0]) if result else {'comparison_record': 'MISSING'}
            diffs = field_differences(ours, other)
            for diff in diffs:
                put('differences', dict(comparison_kind=kind, identity=identity(k), **diff))
            put('comparisons', dict(comparison_kind=kind, identity=identity(k),
                                    matched=not diffs, fields_compared=sorted(ours)))
            counts[kind + '_rows'] += 1
            counts[kind + '_mismatch_rows'] += bool(diffs)

        def byte_ref(k):
            w = db.execute('SELECT ordinal FROM witness WHERE file=? AND pid=?', k).fetchone()
            if w is None:
                raise ValueError('original witness absent')
            return dict(path=str(WITNESS.relative_to(ROOT)), objects_ordinal=w[0])

        for row, location in iter_geometry():
            k = key(row)
            if k[0] not in files:
                raise ValueError('unqualified source file lacks file-table authority')
            db.execute('INSERT INTO raw VALUES(?,?,?,?,?)', (*k, row['type'], canonical(row).decode(), canonical(location).decode()))
            counts['source_' + row['type']] += 1
        db.commit()

        for _, ordinal, w in iter_arrays(WITNESS, {'objects'}):
            k = key(w['identity'])
            row, _ = get(k)
            validate_witness(row, w)
            db.execute('INSERT INTO witness VALUES(?,?,?,?)', (*k, canonical(w).decode(), ordinal))
            counts['original_' + row['type'] + '_hashes'] += 1
        if db.execute('SELECT count(*) FROM raw').fetchone() != db.execute('SELECT count(*) FROM witness').fetchone():
            raise ValueError('witness/source identity sets differ')
        # Full original external file tables are also pinned in the witness.
        for file in wh['files']:
            paths = [e['path'] for e in file['externals']]
            for (raw,) in db.execute('SELECT data FROM raw WHERE file=?', (file['serialized_file'],)):
                if [e['path'] for e in json.loads(raw)['externals']] != paths:
                    raise ValueError('captured/exact-original external file table differs')
        db.commit()

        for _, _, m in iter_arrays(MESH, {'sprites'}):
            k = key(m['identity'])
            value = dict(object_sha256=m['raw']['object_sha256'], positions=m['serialized_positions'],
                         triangles=m['triangle_indices'], minimum=m['metrics']['minimum'],
                         maximum=m['metrics']['maximum'], span=m['metrics']['span'],
                         vertex_count=m['decode_proof']['vertices'])
            db.execute('INSERT INTO compare VALUES(?,?,?,?)', ('mesh75', *k, canonical(value).decode()))
        for kind, _, p in iter_arrays(PEER, {'atlases', 'atlas_sprite_mappings', 'sprite_static_bounds_and_skin_metadata'}):
            if kind == 'atlases':
                k = key(p['identity'])
                value = dict(object_sha256=p['object_bytes_sha256'], name=p['name'],
                             packed_count=p['packed_sprite_count'], map_count=p['render_data_map_count'],
                             names_count=p['packed_name_count'], names_match=p['packed_name_order_matches_sprite_pptrs'])
                label = 'primary_atlas'
            elif kind == 'sprite_static_bounds_and_skin_metadata':
                k = key(p['identity'])
                value = dict(object_sha256=p['object_bytes_sha256'], name=p['name'],
                             route=p['atlas_route'], atlas=identity(key(p['atlas'])) if p['atlas'] else None,
                             render_key=p['render_data_key'], map_index=p['render_data_map_index'],
                             bones=p['serialized_bone_count'], bindposes=p['serialized_bindpose_count'],
                             active_channels=p['active_vertex_channel_indices'], bounds=p['static_vertex_aabb'],
                             serialized_submesh_zero=p['serialized_submesh_local_aabb_zero'])
                label = 'primary_bounds'
            else:
                k = key(p['sprite'])
                rd = p['resolved_render_data']
                value = dict(atlas=identity(key(p['atlas'])), atlas_sha256=p['atlas']['object_bytes_sha256'],
                             render_key=p['render_data_key'], map_index=p['render_data_map_index'], packed_index=p['packed_sprite_index'],
                             texture=identity(key(rd['texture'])), texture_sha256=rd['texture']['object_bytes_sha256'],
                             dimensions=rd['texture']['dimensions'], rect=rd['texture_rect'], rect_offset=rd['texture_rect_offset'],
                             atlas_rect_offset=rd['atlas_rect_offset'], uv_transform=rd['uv_transform'],
                             settings=rd['settings_raw'], downscale=rd['downscale_multiplier'],
                             alpha_texture_pptr=rd['alpha_texture_pptr'], secondary_textures=rd['secondary_textures'])
                label = 'primary_mapping'
            db.execute('INSERT INTO compare VALUES(?,?,?,?)', (label, *k, canonical(value).decode()))
        db.commit()

        # Inverse direction first: exact packed PPtr + ordered name -> Sprite ownership.
        for file, pid in db.execute("SELECT file,pid FROM raw WHERE type='SpriteAtlas' ORDER BY file,pid").fetchall():
            # Retain only addresses; decode exactly one atlas tree at a time.
            a, loc = get((file, pid), 'SpriteAtlas')
            t, ak = a['tree'], (file, pid)
            packed, names, entries = t['m_PackedSprites'], t['m_PackedSpriteNamesToIndex'], t['m_RenderDataMap']
            if not len(packed) == len(names) == len(entries):
                raise ValueError('atlas packed/name/map cardinalities differ')
            for i, pointer in enumerate(packed):
                sk = resolve(file, a['externals'], pointer, files)
                sprite, _ = get(sk, 'Sprite')
                if sprite['tree']['m_Name'] != names[i]:
                    raise ValueError('packed pointer/name order differs')
                if resolve(sk[0], sprite['externals'], sprite['tree']['m_SpriteAtlas'], files) != ak:
                    raise ValueError('packed Sprite points at another atlas')
                db.execute('INSERT INTO packed VALUES(?,?,?,?,?,?)', (*sk, *ak, i, names[i]))
            for i, (rk, rd) in enumerate(entries):
                tk = resolve(file, a['externals'], rd['texture'], files)
                texture, _ = get(tk, 'Texture2D')
                dimensions = [texture['tree']['m_Width'], texture['tree']['m_Height']]
                if any(type(d) is not int or d <= 0 for d in dimensions):
                    raise ValueError('invalid bound texture dimensions')
                entry = dict(render_key=rk, render_data=rd, texture=identity(tk), dimensions=dimensions,
                             texture_object_sha256=texture['object_bytes_sha256'])
                db.execute('INSERT INTO maps VALUES(?,?,?,?,?)', (*ak, render_key(rk), i, canonical(entry).decode()))
                counts['atlas_map_entries'] += 1
            projection = dict(object_sha256=a['object_bytes_sha256'], name=t['m_Name'],
                              packed_count=len(packed), map_count=len(entries), names_count=len(names), names_match=True)
            comparison('primary_atlas', ak, projection)
            put('atlases', dict(identity=identity(ak), raw_location=loc, original_bytes=byte_ref(ak),
                               tag=t['m_Tag'], is_variant=t['m_IsVariant'], **projection))
            counts['packed_pointers'] += len(packed)
            counts['ordered_name_matches'] += len(names)
        db.commit()

        cursor = db.execute("SELECT file,pid FROM raw WHERE type='Sprite' ORDER BY file,pid")
        for file, pid in cursor:
            sk = (file, pid)
            s, loc = get(sk, 'Sprite')
            t, rd = s['tree'], s['tree']['m_RD']
            mesh = decode_mesh(rd)
            ak = resolve(file, s['externals'], t['m_SpriteAtlas'], files)
            map_index = packed_index = None
            if ak:
                result = db.execute('SELECT ordinal,data FROM maps WHERE af=? AND ap=? AND k=?', (*ak, render_key(t['m_RenderDataKey']))).fetchone()
                if result is None:
                    raise ValueError('exact referenced atlas/render-data-key absent')
                map_index, entry = result[0], json.loads(result[1])
                packed_row = db.execute('SELECT af,ap,ordinal FROM packed WHERE file=? AND pid=?', sk).fetchone()
                if packed_row is None or tuple(packed_row[:2]) != ak:
                    raise ValueError('Sprite not in exact owning atlas packed inventory')
                packed_index = packed_row[2]
                db.execute('INSERT INTO used VALUES(?,?,?)', (*ak, render_key(t['m_RenderDataKey'])))
                db.execute('INSERT INTO used_sprites VALUES(?,?)', sk)
                route = 'atlas_pointer_and_exact_render_data_key'
                counts['atlas_backed_sprites'] += 1
            else:
                if t['m_AtlasTags']:
                    raise ValueError('direct Sprite has unexplained atlas tags')
                tk = resolve(file, s['externals'], rd['texture'], files)
                tex, _ = get(tk, 'Texture2D')
                entry = dict(render_key=t['m_RenderDataKey'], render_data={k: v for k, v in rd.items() if k not in (
                    'm_SubMeshes', 'm_IndexBuffer', 'm_VertexData', 'm_Bindpose')}, texture=identity(tk),
                    dimensions=[tex['tree']['m_Width'], tex['tree']['m_Height']], texture_object_sha256=tex['object_bytes_sha256'])
                route = 'direct_sprite_render_data'
                counts['direct_sprites'] += 1
            bounds = {k: mesh[k] for k in ('minimum', 'maximum', 'span', 'vertex_count')}
            active = [i for i, c in enumerate(rd['m_VertexData']['m_Channels']) if c['dimension']]
            sub_zero = static_zero(rd['m_SubMeshes'])
            projection = dict(object_sha256=s['object_bytes_sha256'], name=t['m_Name'], route=route,
                              atlas=identity(ak), render_key=t['m_RenderDataKey'], map_index=map_index,
                              bones=len(t['m_Bones']), bindposes=len(rd['m_Bindpose']), active_channels=active,
                              bounds=bounds, serialized_submesh_zero=sub_zero)
            comparison('primary_bounds', sk, projection)
            comparison('mesh75', sk, dict(object_sha256=s['object_bytes_sha256'], positions=mesh['positions'],
                                         triangles=mesh['triangles'], **bounds))
            if ak:
                a, _ = get(ak, 'SpriteAtlas')
                ar = entry['render_data']
                comparison('primary_mapping', sk, dict(
                    atlas=identity(ak), atlas_sha256=a['object_bytes_sha256'], render_key=t['m_RenderDataKey'],
                    map_index=map_index, packed_index=packed_index, texture=entry['texture'],
                    texture_sha256=entry['texture_object_sha256'], dimensions=entry['dimensions'],
                    rect=ar['textureRect'], rect_offset=ar['textureRectOffset'], atlas_rect_offset=ar['atlasRectOffset'],
                    uv_transform=ar['uvTransform'], settings=ar['settingsRaw'], downscale=ar['downscaleMultiplier'],
                    alpha_texture_pptr=ar['alphaTexture'], secondary_textures=ar['secondaryTextures']))
            put('sprites', dict(identity=identity(sk), raw_location=loc, original_bytes=byte_ref(sk),
                                **projection, packed_index=packed_index, resolved_static_data=entry,
                                source_positions=mesh['positions'], source_uv0=mesh['source_uv0'],
                                triangle_indices=mesh['triangles'], serialized_submeshes=rd['m_SubMeshes'],
                                vertex_payload_sha256=mesh['vertex_payload_sha256'], index_payload_sha256=mesh['index_payload_sha256'],
                                live_remap=None, runtime_deformed_bounds=None,
                                bounds_scope='static serialized local vertices; not runtime-deformed'))
            counts['bound_texture_pointer_resolutions'] += 1
            counts['static_vertices'] += mesh['vertex_count']
            counts['static_indices'] += mesh['index_count']
            counts['static_bounds'] += 1
            counts['empty_bones'] += not t['m_Bones']
            counts['empty_bindposes'] += not rd['m_Bindpose']
            counts['serialized_zero_local_aabb_sprites'] += sub_zero
            counts['stored_uv0_all_zero_sprites'] += mesh['stored_uv0_all_zero']
        db.commit()
        counts['unmatched_packed_pointers'] = db.execute('SELECT count(*) FROM packed p LEFT JOIN used_sprites u ON p.file=u.file AND p.pid=u.pid WHERE u.pid IS NULL').fetchone()[0]
        counts['unmatched_atlas_map_rows'] = db.execute('SELECT count(*) FROM maps m LEFT JOIN used u ON m.af=u.af AND m.ap=u.ap AND m.k=u.k WHERE u.k IS NULL').fetchone()[0]
        counts['cross_atlas_duplicate_keys'] = db.execute('SELECT count(*) FROM (SELECT k FROM maps GROUP BY k HAVING count(*)>1)').fetchone()[0]

        # Corroborate the overlapping raw102 capture without constructing its Graph.
        for part in surface_index['objects']:
            p = SURFACE / part['path']
            if sha_file(p) != part['sha256']:
                raise ValueError('raw102 compressed shard pin drift')
            source_paths.add(str(p.relative_to(ROOT)))
            n = 0
            with gzip.open(p, 'rb') as stream:
                for i, line in enumerate(stream):
                    n += 1
                    r = json.loads(line)
                    if r['type'] not in ('Sprite', 'SpriteAtlas'):
                        continue
                    k = key(r)
                    row, rawloc = get(k, r['type'])
                    ours, other = row['tree'], r['tree']
                    expected = dict(object_sha256=row['object_bytes_sha256'])
                    observed = dict(object_sha256=r['raw_object_sha256'])
                    if r['type'] == 'SpriteAtlas':
                        expected['tree'] = ours
                        observed['tree'] = other
                    else:
                        for field in ('m_Name', 'm_Rect', 'm_Offset', 'm_Border', 'm_PixelsToUnits',
                                      'm_Pivot', 'm_RenderDataKey', 'm_AtlasTags', 'm_SpriteAtlas', 'm_Bones'):
                            expected[field], observed[field] = ours[field], other[field]
                        expected['bindpose'], observed['bindpose'] = ours['m_RD']['m_Bindpose'], other['m_RD']['m_Bindpose']
                        m = decode_mesh(ours['m_RD'])
                        expected['positions'], observed['positions'] = m['positions'], r['geometry']['m_Vertices']
                        expected['indices'] = [v for tri in m['triangles'] for v in tri]
                        observed['indices'] = r['geometry']['m_IndexBuffer']
                        redactions = {x['location']: x['sha256'] for x in r['binary_buffer_redactions']}
                        expected['vertex_sha256'] = m['vertex_payload_sha256']
                        observed['vertex_sha256'] = redactions['.tree.m_RD.m_VertexData.m_DataSize']
                        expected['index_sha256'] = m['index_payload_sha256']
                        observed['index_sha256'] = redactions['.tree.m_RD.m_IndexBuffer']
                    diffs = field_differences(expected, observed)
                    for diff in diffs:
                        put('differences', dict(comparison_kind='raw102', identity=identity(k),
                                                own_raw_location=rawloc, comparison_raw_location=dict(path=str(p.relative_to(ROOT)), row=i), **diff))
                    put('raw102_crosschecks', dict(identity=identity(k), type=r['type'], matched=not diffs,
                                                  own_raw_location=rawloc, raw102_location=dict(path=str(p.relative_to(ROOT)), row=i),
                                                  object_sha256=row['object_bytes_sha256']))
                    counts['raw102_' + r['type'] + '_rows'] += 1
                    counts['raw102_mismatch_rows'] += bool(diffs)
            if n != part['rows']:
                raise ValueError('raw102 shard row count drift')
        db.commit()
        counts['differences'] = outputs['differences']
        # No comparison dataset is allowed to silently contribute or omit identities.
        for kind in ('mesh75', 'primary_bounds', 'primary_mapping', 'primary_atlas'):
            total = db.execute('SELECT count(*) FROM compare WHERE kind=?', (kind,)).fetchone()[0]
            if total != counts[kind + '_rows']:
                raise ValueError('comparison identity inventory differs: ' + kind)

        source_paths.update(str(p.relative_to(ROOT)) for p in (
            ROOT/'tools/verify/l3_geometry_8141386a_atlas.py', ROOT/'tools/verify/geometry_8141386a_atlas_sources.py'))
        h = dict(schema=1, item=6, provenance=BRANCH,
                 status='BYTE_CORROBORATED_STATIC_ATLAS_MAP_AND_VERTEX_BOUNDS_NOT_LIVE_OR_RUNTIME_DEFORMED',
                 xapk_sha256=XAPK, apk_sha256=APK, bundle_sha256=DATA,
                 primary_comparison=dict(branch='arena/a5a74747-windwings-space-shooter-game-p', scientific_commit=PEER_HEAD,
                                         handoff_comment=6416037439, ack_comment=6416110827,
                                         snapshot=str(PEER.relative_to(ROOT)), sha256=sha_file(PEER)),
                 lineage='Shared raw Sprite-geometry/mesh75/raw102 capture and schema, ef111/110 framing, font73 history for prior #4 only. No full Graph instantiated. Independent inverse/static-bound/join code; original cache recovery adds byte corroboration, not independent schema discovery.',
                 summary=dict(sorted(counts.items())),
                 source_pins={p: sha_file(ROOT / p) for p in sorted(source_paths)},
                 missing_for_native_closure=['Original native atlas request/registration/remap consumer with actual state/instance, or same-build live receipt identifying atlas+Sprite+render key+scene instance.',
                                             'Actual native deformation inputs/consumer and placement-authoritative vertex/bounds readback. Empty arrays only describe these captured Sprite objects.'],
                 boundary='Static serialized correspondence and local vertex AABBs only. NOT live-remapped; NOT runtime-deformed; no scene/world/skin/pixel/render result, no default mesh inference.')

        def rows(kind):
            for (data,) in db.execute('SELECT data FROM out WHERE kind=? ORDER BY ordinal', (kind,)):
                yield json.loads(data)
        write_document(path, h, [(kind, rows(kind)) for kind in (
            'atlases', 'sprites', 'comparisons', 'raw102_crosschecks', 'differences')])
        db.close()
    return h


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    with scratch('build-') as directory:
        target = directory/'artifact.json.gz'
        result = build(target)
        if args.check:
            if not OUT.exists() or sha_file(OUT) != sha_file(target):
                raise SystemExit('static atlas artifact drift')
        else:
            target.replace(OUT)
    print(json.dumps(result['summary'], sort_keys=True))
