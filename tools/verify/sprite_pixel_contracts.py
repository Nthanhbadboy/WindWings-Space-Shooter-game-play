"""Verify preserved pixel-audit provenance; expose import metadata, not final pivots."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/recovery'))
from sprite_pixel_audit import decode_mesh,edge_padding,rounded_box
from sprite_geometry import load_objects,build as build_geometry


def sha(blob):return hashlib.sha256(blob).hexdigest()


def build():
    path=ROOT/'reverse-engineering/raw/sprite-pixels/audit.json.gz'
    blob=gzip.decompress(path.read_bytes());audit=json.loads(blob)
    cblob=gzip.decompress((ROOT/'reverse-engineering/raw/asset-pack-v2/catalog.json.gz').read_bytes());catalog=json.loads(cblob)
    assert sha(cblob)==audit['catalog_sha256_decompressed']
    previous=json.loads(gzip.decompress((ROOT/'reverse-engineering/raw/asset-pack-v2/archive-audit.json.gz').read_bytes()))
    assert audit['source_archive_sha256']==previous['archive_sha256']
    for ref in audit['format_reference_files']:
        assert sha((ROOT/'reverse-engineering/raw/sprite-geometry/toolchain'/ref['path']).read_bytes())==ref['sha256']
    geometry=build_geometry()
    assert audit['geometry_inputs_sha256']==geometry['inputs_sha256']
    assert audit['geometry_sources']==geometry['sources']
    _,raw,_=load_objects()
    raw_objects={(r['serialized_file'],r['path_id']):r for r in raw if r['type']=='Sprite'}
    mapping=audit['serialized_file_map']
    assert len(set(mapping.values()))==len(mapping)
    assert all(Path(v).name==k for k,v in mapping.items())
    assert set(mapping.values())=={r['serialized_file'] for r in catalog['serialized_files']}
    pngs={(r['serialized_file'],r['type'],r['path_id']):r for r in catalog['objects']}
    proof={(r['identity']['serialized_file'],r['identity']['path_id']):r for r in audit['sprites']}
    assert len(proof)==2185 and len(audit['sprites'])==2185
    rows=[];outliers=[];trimmed=0
    for g in geometry['sprites']:
        full=mapping[g['serialized_file']]
        row=proof[full,g['path_id']]
        raw_sprite=raw_objects[g['serialized_file'],g['path_id']]
        assert row['status']=='match' and row['exact_rgba_match'] is True
        assert row['expected_rgba_sha256']==row['actual_rgba_sha256']
        assert row['raw_sprite_object_sha256']==raw_sprite['object_bytes_sha256']
        assert row['mesh']==decode_mesh(raw_sprite['tree']['m_RD'])[2]
        for key in ('texture_rect','source_rect','pivot','texture_rect_offset','atlas_rect_offset','pixels_to_units'):
            assert row[key]==g[key]
        assert row['rounded_crop_box']==rounded_box(g['texture_rect'])
        assert row['padding_pixels']==edge_padding(g['texture_rect'],*g['texture']['dimensions'])
        exported=pngs[full,'Sprite',g['path_id']]
        texture=pngs[mapping[g['texture']['serialized_file']],'Texture2D',g['texture']['path_id']]
        assert exported['outputs']==[row['sprite_output']] and texture['outputs']==[row['texture_output']]
        assert row['actual_size']==row['expected_size']==[row['sprite_output']['width'],row['sprite_output']['height']]
        presentation=dict(source_rect=g['source_rect'],source_normalized_pivot=g['pivot'],pixels_to_units=g['pixels_to_units'],
                          trim_offset=g['texture_rect_offset'],atlas_offset=g['atlas_rect_offset'],export_size=row['actual_size'],alpha_bbox=row['alpha_bbox'])
        rows.append(dict(identity=row['identity'],name=row['name'],png=row['sprite_output'],presentation=presentation,
                         mesh_raw_ref=dict(serialized_file=g['serialized_file'],path_id=g['path_id'],object_sha256=raw_sprite['object_bytes_sha256'])))
        if row['actual_size']!=[round(g['source_rect']['width']),round(g['source_rect']['height'])]:trimmed+=1
        if not row['geometry_rect_within']:
            rect=row['rounded_crop_box'];w,h=g['texture']['dimensions']
            clamped=[max(0,rect[0]),max(0,rect[1]),min(w,rect[2]),min(h,rect[3])]
            outliers.append(dict(identity=row['identity'],float_rect=row['texture_rect'],rounded_box=rect,padding=row['padding_pixels'],
                                 export_size=row['actual_size'],counterfactual_clamped_size=[clamped[2]-clamped[0],clamped[3]-clamped[1]]))
    assert len(rows)==2185
    return dict(schema_version=1,status='provisional_export_reference_not_Unity_render_approval',
                sources=[dict(path=str(path.relative_to(ROOT)),sha256_decompressed=sha(blob))],toolchain=audit['toolchain'],summary=dict(audit['summary'],export_size_differs_from_rounded_source_rect=trimmed),
                limits=['Source-normalized pivot is NOT a pivot normalized to the exported PNG.',
                        'PNG crops/masks are not restored full source canvases; preserve rect/offset/mesh references.',
                        'Counterfactual clamped dimensions are diagnostics, not approved replacements.',
                        'All 2185 RGBA matches reproduce format-tool behavior, not Unity GPU/PMA/filtering/scene placement.'],
                fractional_outside=outliers,sprites=rows)


if __name__=='__main__':
    data=build()
    target=ROOT/'datas/sprite_export_contract.json.gz'
    target.write_bytes(gzip.compress((json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode(),mtime=0))
    print(json.dumps(data['summary'],indent=2))
