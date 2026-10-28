"""Audit exported Sprite PNGs against separately decoded raw geometry and texture PNGs.

Reproduces a format-tool crop/mask pipeline, not Unity's GPU rasterizer.
"""
import argparse
import base64
from collections import Counter
import gzip
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/verify'))
from sprite_geometry import build as geometry_build, load_objects


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def decode_mesh(render_data):
    vertex=render_data['m_VertexData']
    count=vertex['m_VertexCount']
    channels=[(i,c['stream'],c['offset'],c['format'],c['dimension']) for i,c in enumerate(vertex['m_Channels']) if c['dimension']]
    if channels != [(0,0,0,0,3),(4,1,0,0,2)]:
        raise ValueError('unreviewed vertex layout')
    blob=base64.b64decode(vertex['m_DataSize']['bytes_base64'],validate=True)
    uv_start=(count*12+15)//16*16
    if len(blob)<uv_start+count*8 or count<3:
        raise ValueError('truncated/invalid vertex data')
    positions=list(struct.iter_unpack('<3f',blob[:count*12]))
    uv=list(struct.iter_unpack('<2f',blob[uv_start:uv_start+count*8]))
    if any(u or v for u,v in uv):
        raise ValueError('nonzero UV needs a different rendering path')
    triangles=[]
    indexes=bytes(render_data['m_IndexBuffer'])
    for sub in render_data['m_SubMeshes']:
        if sub['topology']!=0 or sub['indexCount']%3 or sub['baseVertex']!=0:
            raise ValueError('unreviewed index topology/baseVertex')
        start=sub['firstByte'];size=sub['indexCount']*2
        if len(indexes)<start+size:
            raise ValueError('truncated index data')
        group=list(struct.iter_unpack('<3H',indexes[start:start+size]))
        if any(i>=count for t in group for i in t):
            raise ValueError('triangle index out of range')
        triangles.extend(group)
    return positions,triangles,dict(vertices=count,triangles=len(triangles),uv_all_zero=True,vertex_payload_sha256=sha(blob),index_payload_sha256=sha(indexes))


def crop_box(rect):
    return [rect['x'],rect['y'],rect['x']+rect['width'],rect['y']+rect['height']]


def rounded_box(rect):
    # Pillow Image.crop uses round() on each boundary, not round(width/height).
    return [round(v) for v in crop_box(rect)]


def edge_padding(rect,width,height):
    left,top,right,bottom=rounded_box(rect)
    return dict(left=max(0,-left),bottom=max(0,-top),right=max(0,right-width),top=max(0,bottom-height))


def reconstruct(texture, geometry, render_data, pixels_to_units):
    from PIL import Image,ImageDraw
    # Texture PNG export is top-origin; raw sprite rectangles are bottom-origin.
    image=texture.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    image=image.crop(tuple(crop_box(geometry['texture_rect'])))
    settings=geometry['settings']
    if settings['packed']:
        rotations={0:None,1:Image.Transpose.FLIP_LEFT_RIGHT,2:Image.Transpose.FLIP_TOP_BOTTOM,3:Image.Transpose.ROTATE_180,4:Image.Transpose.ROTATE_270}
        if settings['packing_rotation'] not in rotations:
            raise ValueError('unreviewed packing rotation')
        rotation=rotations[settings['packing_rotation']]
        if rotation is not None:image=image.transpose(rotation)
    positions,triangles,mesh=decode_mesh(render_data)
    if settings['packing_mode']==0:
        x_min=min(v[0] for v in positions);y_min=min(v[1] for v in positions)
        points=[((x-x_min)*pixels_to_units,(y-y_min)*pixels_to_units) for x,y,z in positions]
        mask=Image.new('1',image.size,0)
        draw=ImageDraw.Draw(mask)
        for tri in triangles:draw.polygon([points[i] for i in tri],fill=1)
        if image.mode=='RGBA':image=Image.composite(image,Image.new('RGBA',image.size,0),mask)
        else:image.putalpha(mask)
    elif settings['packing_mode']!=1:
        raise ValueError('unreviewed packing mode')
    return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM).convert('RGBA'),mesh


def audit(archive):
    import PIL
    from PIL import Image,ImageChops
    folder=ROOT/'reverse-engineering/raw/sprite-pixels'
    folder.mkdir(parents=True,exist_ok=True)
    catalog_blob=gzip.decompress((ROOT/'reverse-engineering/raw/asset-pack-v2/catalog.json.gz').read_bytes())
    catalog=json.loads(catalog_blob)
    previous=json.loads(gzip.decompress((ROOT/'reverse-engineering/raw/asset-pack-v2/archive-audit.json.gz').read_bytes()))
    assert sha(archive.read_bytes())==previous['archive_sha256']
    geometry=geometry_build()
    _,raw,_=load_objects()
    raw_sprites={(r['serialized_file'],r['path_id']):r for r in raw if r['type']=='Sprite'}
    # Legacy geometry file names may be mapped only if exactly one full logical file exists.
    file_map={}
    for r in catalog['serialized_files']:
        base=Path(r['serialized_file']).name
        if base in file_map:raise ValueError('serialized basename ambiguity')
        file_map[base]=r['serialized_file']
    outputs={(r['serialized_file'],r['type'],r['path_id']):r for r in catalog['objects']}
    rows=[]
    cache={}
    with zipfile.ZipFile(archive) as zipped:
        def source(file,kind,pid):
            row=outputs[file_map[file],kind,pid]
            assert row['status']=='exported' and len(row['outputs'])==1
            item=row['outputs'][0]
            blob=zipped.read(item['path'])
            assert len(blob)==item['bytes'] and sha(blob)==item['sha256']
            return blob,item
        for g in geometry['sprites']:
            identity=dict(serialized_file=file_map[g['serialized_file']],type='Sprite',path_id=g['path_id'])
            row=dict(identity=identity,name=g['name'],rotation=g['settings']['packing_rotation'],packed=g['settings']['packed'],
                     texture_rect=g['texture_rect'],source_rect=g['source_rect'],pivot=g['pivot'],
                     texture_rect_offset=g['texture_rect_offset'],atlas_rect_offset=g['atlas_rect_offset'],pixels_to_units=g['pixels_to_units'],
                     fractional_rect=any(float(v)!=int(v) for v in g['texture_rect'].values()),
                     geometry_rect_within=g['rect_within_texture'],rounded_crop_box=rounded_box(g['texture_rect']))
            rows.append(row)
            try:
                assert g['alpha_texture'] is None, 'separate alpha needs explicit audit'
                tex=g['texture'];tk=(tex['serialized_file'],tex['path_id'])
                if tk not in cache:
                    blob,texture_output=source(tex['serialized_file'],'Texture2D',tex['path_id'])
                    image=Image.open(io.BytesIO(blob));image.load()
                    cache[tk]=(image,texture_output)
                texture,texture_output=cache[tk]
                assert list(texture.size)==tex['dimensions']
                row['texture_output']=texture_output
                row['padding_pixels']=edge_padding(g['texture_rect'],*texture.size)
                obj=raw_sprites[g['serialized_file'],g['path_id']]
                row['raw_sprite_object_sha256']=obj['object_bytes_sha256']
                expected,mesh=reconstruct(texture,g,obj['tree']['m_RD'],g['pixels_to_units'])
                row['mesh']=mesh
                blob,sprite_output=source(g['serialized_file'],'Sprite',g['path_id'])
                with Image.open(io.BytesIO(blob)) as opened:actual=opened.convert('RGBA')
                row.update(sprite_output=sprite_output,expected_size=list(expected.size),actual_size=list(actual.size),
                           expected_rgba_sha256=sha(expected.tobytes()),actual_rgba_sha256=sha(actual.tobytes()),
                           alpha_bbox=actual.getchannel('A').getbbox())
                if row['alpha_bbox'] is not None:row['alpha_bbox']=list(row['alpha_bbox'])
                row['exact_rgba_match']=actual.size==expected.size and actual.tobytes()==expected.tobytes()
                if actual.size==expected.size:
                    diff=ImageChops.difference(actual,expected)
                    row['difference_extrema']=[list(x) for x in diff.getextrema()]
                row['status']='match' if row['exact_rgba_match'] else 'mismatch'
            except Exception as error:row.update(status='error',error=repr(error))
        summary=dict(schema_version=1,status='provisional_exporter_pixel_reproduction_not_Unity_GPU_fidelity',
                     toolchain=dict(Pillow=PIL.__version__,format_reference_UnityPy='1.25.4'),
                     source_archive_sha256=previous['archive_sha256'],catalog_sha256_decompressed=sha(catalog_blob),
                     geometry_inputs_sha256=geometry['inputs_sha256'],geometry_sources=geometry['sources'],
                     format_reference_files=[dict(path=p.name,sha256=sha(p.read_bytes())) for p in sorted((ROOT/'reverse-engineering/raw/sprite-geometry/toolchain').iterdir()) if p.is_file()],
                     serialized_file_map=file_map,summary=dict(total=len(rows),outcomes=dict(Counter(r['status'] for r in rows)),
                         fractionals=sum(r['fractional_rect'] for r in rows),outside_geometry=sum(not r['geometry_rect_within'] for r in rows),
                         rounded_padding=sum(any(r.get('padding_pixels',{}).values()) for r in rows),
                         rotation_counts=dict(Counter(str(r['rotation']) for r in rows))),
                     limits=['Matches reproduce a reviewed format-tool crop/flip/triangle-mask pipeline, not Unity GPU rendering.',
                             'Raw pivot/source rect/offsets remain metadata, not an assembled full-canvas sprite.',
                             'Fractional crop rounding is Pillow behavior, not a new gameplay/art rule.',
                             'Separate alpha/nonzero-UV/unreviewed layouts fail explicitly; no silent fallback.',
                             'PNG colors/alpha decode inherit v2 texture conversion; no original compressed GPU texel fidelity proof.'],sprites=rows)
    (folder/'audit.json.gz').write_bytes(gzip.compress((json.dumps(summary,indent=2)+'\n').encode(),mtime=0))
    print(json.dumps(summary['summary'],indent=2),flush=True)
    assert len(rows)==2185 and all(r['status']=='match' for r in rows), 'Pixel mismatches/errors preserved; not a passing reproduction audit'
    assert (folder/'audit.json.gz').stat().st_size<5_000_000


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--archive',required=True,type=Path)
    audit(parser.parse_args().archive)
