"""Expose serialized Sprite mesh coordinates, not a guessed trimmed-PNG pivot."""
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/recovery'))
from sprite_geometry import load_objects
from sprite_pixel_audit import decode_mesh
from sprite_pixel_contracts import build as pixel_build


def mesh_metrics(positions,triangles):
    if not positions or any(not math.isfinite(x) for p in positions for x in p):
        raise ValueError('empty/nonfinite mesh')
    minimum=[min(p[i] for p in positions) for i in range(3)]
    maximum=[max(p[i] for p in positions) for i in range(3)]
    span=[b-a for a,b in zip(minimum,maximum)]
    if span[0]<=0 or span[1]<=0:raise ValueError('zero XY mesh span needs separate review')
    anchor=[-minimum[i]/span[i] for i in range(2)]
    winding=Counter()
    for tri in triangles:
        if len(tri)!=3 or any(i<0 or i>=len(positions) for i in tri):raise ValueError('triangle index outside mesh')
        a,b,c=[positions[i] for i in tri]
        cross=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
        winding['positive' if cross>0 else 'negative' if cross<0 else 'zero']+=1
    return dict(minimum=minimum,maximum=maximum,span=span,origin_relative_to_mesh_aabb=anchor,
                origin_outside_xy_aabb=any(v<0 or v>1 for v in anchor),
                origin_outside_xy_aabb_gt_1e_5=any(v < -1e-5 or v > 1+1e-5 for v in anchor),triangle_cross_sign_counts=dict(winding))


def build():
    pixel=pixel_build();index,raw,sources=load_objects()
    objects={(r['serialized_file'],r['path_id']):r for r in raw if r['type']=='Sprite'}
    rows=[];counts=Counter();ppu=Counter();vertices=triangles_total=0;winding=Counter()
    for sprite in pixel['sprites']:
        ref=sprite['mesh_raw_ref'];r=objects[ref['serialized_file'],ref['path_id']]
        assert r['object_bytes_sha256']==ref['object_sha256']
        tree=r['tree'];positions,triangles,proof=decode_mesh(tree['m_RD']);metrics=mesh_metrics(positions,triangles)
        assert tree['m_PixelsToUnits']>0 and math.isfinite(tree['m_PixelsToUnits'])
        presentation=sprite['presentation'];assert tree['m_Pivot']==presentation['source_normalized_pivot']
        delta=[metrics['origin_relative_to_mesh_aabb'][i]-tree['m_Pivot'][axis] for i,axis in enumerate(('x','y'))]
        different=max(map(abs,delta))>1e-5
        counts['mesh_aabb_anchor_differs_from_source_pivot_gt_1e_5']+=different
        counts['origin_outside_mesh_xy_aabb']+=metrics['origin_outside_xy_aabb']
        counts['origin_outside_mesh_xy_aabb_gt_1e_5']+=metrics['origin_outside_xy_aabb_gt_1e_5']
        counts['serialized_submesh_aabb_all_zero']+=all(all(v==0 for v in sub['localAABB']['m_Center'].values()) and all(v==0 for v in sub['localAABB']['m_Extent'].values()) for sub in tree['m_RD']['m_SubMeshes'])
        counts['nonzero_z']+=any(p[2]!=0 for p in positions)
        counts['non_quad_mesh']+=len(positions)!=4
        vertices+=len(positions);triangles_total+=len(triangles);winding.update(metrics['triangle_cross_sign_counts']);ppu[str(tree['m_PixelsToUnits'])]+=1
        rows.append(dict(identity=sprite['identity'],name=sprite['name'],raw=ref,decode_proof=proof,
            serialized_positions=[list(v) for v in positions],triangle_indices=[list(t) for t in triangles],
            serialized_submeshes=tree['m_RD']['m_SubMeshes'],metrics=metrics,
            source_pivot=tree['m_Pivot'],pixels_to_units=tree['m_PixelsToUnits'],source_rect=tree['m_Rect'],
            source_offset=tree['m_Offset'],border=tree['m_Border'],png=sprite['png'],export_presentation=presentation,
            diagnostic_anchor_minus_source_pivot=delta,diagnostic_diff_gt_1e_5=different))
    source_blob=gzip.decompress((ROOT/'datas/sprite_export_contract.json.gz').read_bytes())
    assert json.loads(source_blob)==pixel
    return dict(schema_version=1,status='PROVISIONAL_SERIALIZED_MESH_REFERENCE_NOT_UNITY_SCENE_PLACEMENT_OR_PNG_PIVOT',
        source_geometry_chunks=sources,inputs_sha256=index['inputs_sha256'],
        pixel_contract_sha256_decompressed=hashlib.sha256(source_blob).hexdigest(),
        summary=dict(sprites=len(rows),vertices=vertices,triangles=triangles_total,diagnostics=dict(counts),
                     triangle_cross_sign_counts=dict(winding),pixels_to_units_counts=dict(ppu)),
        limits=['Serialized positions/indices are decoded directly from preserved Sprite m_RD; no recenter, scaling, coordinate reflection or winding repair is applied.',
                'origin_relative_to_mesh_aabb = -minimum / (maximum-minimum), an arithmetic diagnostic; it is NOT a normalized PNG pivot or a Unity Transform.',
                'The 1e-5 anchor difference threshold is a reporting tolerance, not an APK branch or approval criterion.',
                'Source pivot, source rect, PNG dimensions, trim/atlas offsets and mesh origin remain distinct fields.',
                'No atlas UVs are fabricated from all-zero stored UV0; no new texture sampling, GPU rendering, transform hierarchy, animation, flip or material behavior is validated.',
                'Serialized submesh localAABB is retained verbatim; measured vertex bounds are separate and do not overwrite it.'],sprites=rows)


def main():
    result=build();blob=(json.dumps(result,ensure_ascii=True,indent=2)+'\n').encode()
    (ROOT/'datas/sprite_mesh_contract.json.gz').write_bytes(gzip.compress(blob,mtime=0))
    raw=ROOT/'reverse-engineering/raw/sprite-meshes';raw.mkdir(parents=True,exist_ok=True)
    metadata=dict(status='DERIVATION_METADATA_NOT_NEW_APK_CAPTURE',contract_sha256_decompressed=hashlib.sha256(blob).hexdigest(),
        geometry_chunks=result['source_geometry_chunks'],pixel_contract_sha256_decompressed=result['pixel_contract_sha256_decompressed'],
        decoder=dict(path='tools/recovery/sprite_pixel_audit.py',sha256=hashlib.sha256((ROOT/'tools/recovery/sprite_pixel_audit.py').read_bytes()).hexdigest()),summary=result['summary'])
    (raw/'derivation.json').write_text(json.dumps(metadata,indent=2)+'\n')
    summary={k:v for k,v in result['summary'].items() if k!='pixels_to_units_counts'}
    summary['distinct_pixels_to_units']=len(result['summary']['pixels_to_units_counts'])
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
