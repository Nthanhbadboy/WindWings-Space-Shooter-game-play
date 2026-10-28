"""Border-aware sliced / continuous-tiled CPU reference, NOT Unity native geometry.
provenance: arena/8141386a-windwings-space-shooter-game-p

Policies (not recovered engine code): binary64 operations, proportional border compression
when requested size < opposing borders, tail-clip continuous tiles, deterministic row-major
negative-Z winding. Adaptive tiles/trimmed/rotated/tight packing fail closed. UVs are
computed from source-pixel coordinates, NEVER stretched destination coordinates or zero UV0.
"""
from __future__ import annotations

import math

MAX_QUADS = 4096


class UnsupportedGeometry(ValueError):
    """Source or explicit policy is outside the demonstrated domain."""


def vector(value, count, label):
    if not isinstance(value, (list, tuple)) or len(value) != count:
        raise UnsupportedGeometry(f"{label}: vector length {count} required")
    if any(type(x) not in (float, int) or not math.isfinite(x) for x in value):
        raise UnsupportedGeometry(f"{label}: finite numeric components required")
    return list(value)


def validate(source, size):
    size = vector(size, 2, "requested size")
    if min(size) <= 0:
        raise UnsupportedGeometry("positive requested size required")
    rect = vector(source["source_rect_px"], 2, "source rect")
    border = vector(source["border_px_lbrt"], 4, "serialized border")
    pivot = vector(source["pivot_normalized"], 2, "source pivot")
    ppu = source["pixels_per_unit"]
    if type(ppu) not in (int, float) or not math.isfinite(ppu) or ppu <= 0:
        raise UnsupportedGeometry("positive serialized pixels-per-unit required")
    if min(rect) <= 0 or min(border) < 0:
        raise UnsupportedGeometry("positive rect and nonnegative border required")
    if border[0]+border[2] > rect[0] or border[1]+border[3] > rect[1]:
        raise UnsupportedGeometry("opposing serialized borders exceed source rect")
    if any(not 0 <= n <= 1 for n in pivot):
        raise UnsupportedGeometry("bounded normalized pivot domain is 0..1")
    texture_size = vector(source["texture_size"], 2, "texture dimensions")
    if any(type(n) is not int or n <= 0 for n in texture_size):
        raise UnsupportedGeometry("positive integer texture dimensions required")
    settings = source["settings_raw"]
    if type(settings) is not int or settings not in (0, 1):
        raise UnsupportedGeometry("only unrotated rectangular unpacked0/packed1 demonstrated")
    for label in ("trim_offset_px", "sprite_offset_px"):
        if vector(source[label], 2, label) != [0, 0]:
            raise UnsupportedGeometry("trimmed/offset source requires a separately proven trim model")
    atlas_rect = vector(source["texture_rect_px"], 4, "atlas rect")
    # Bound tolerance addresses serialized float rounding, not silently missing trim.
    if any(abs(atlas_rect[i+2]-rect[i]) > 2e-5 for i in range(2)):
        raise UnsupportedGeometry("trimmed/downscaled atlas rect outside demonstrated domain")
    if any(atlas_rect[i] < 0 or atlas_rect[i]+atlas_rect[i+2] > texture_size[i]+2e-5
           for i in range(2)):
        raise UnsupportedGeometry("atlas rect outside owning texture")
    transform = vector(source["uv_transform_xyzw"], 4, "UV transform")
    if transform[0] <= 0 or transform[2] <= 0 or source.get("downscale_multiplier") != 1:
        raise UnsupportedGeometry("positive unscaled affine UV transform required")
    # This check connects the untrimmed source coordinate system to the exact atlas entry.
    for axis in range(2):
        lo = -rect[axis] * pivot[axis] / ppu
        hi = rect[axis] * (1-pivot[axis]) / ppu
        ends = [lo*transform[axis*2]+transform[axis*2+1],
                hi*transform[axis*2]+transform[axis*2+1]]
        if any(abs(a-b) > 2e-4 for a, b in zip(ends, [atlas_rect[axis], atlas_rect[axis]+atlas_rect[axis+2]])):
            raise UnsupportedGeometry("source-pivot affine UV extent does not match exact atlas rect")
    return size, rect, border, pivot, ppu


def cuts(length, first, last, pivot):
    total = first+last
    factor = min(1.0, length/total) if total else 1.0
    start = -pivot*length
    # Avoid a negative central interval from roundoff when borders consume the size.
    a = start+first*factor
    b = start+length-last*factor
    if factor < 1:
        b = a
    return [start, a, b, start+length], factor


def uv(source, pixel):
    ppu = source["pixels_per_unit"]
    rect, pivot, transform = source["source_rect_px"], source["pivot_normalized"], source["uv_transform_xyzw"]
    local = [(pixel[i]-rect[i]*pivot[i])/ppu for i in range(2)]
    return [(local[0]*transform[0]+transform[1])/source["texture_size"][0],
            (local[1]*transform[2]+transform[3])/source["texture_size"][1]]


def apply_flip(vertices, flip):
    if len(flip) != 2 or any(type(n) is not bool for n in flip):
        raise UnsupportedGeometry("explicit Boolean flip pair required")
    return [[-v[0] if flip[0] else v[0], -v[1] if flip[1] else v[1], v[2]] for v in vertices]


def finish(kind, source, size, vertices, source_pixels, indices, cells, details, flip):
    uvs = [uv(source, p) for p in source_pixels]
    vertices = apply_flip(vertices, flip)
    if any(not math.isfinite(n) for row in vertices+uvs for n in row):
        raise UnsupportedGeometry("derived coordinate overflow")
    result = dict(status="generated_metadata_driven_CPU_model_NOT_Unity_readback", kind=kind,
                  size=size, border_px_lbrt=source["border_px_lbrt"],
                  border_local_lbrt=[n/source["pixels_per_unit"] for n in source["border_px_lbrt"]],
                  vertices=vertices, uvs=uvs, source_pixels=source_pixels, indices=indices,
                  triangles=[indices[i:i+3] for i in range(0, len(indices), 3)],
                  cells=cells, flip=list(flip), details=details,
                  policy="Binary64 CPU model; negative-Z row-major topology, not original engine index order")
    result["invariants"] = invariants(result, source)
    return result


def sliced(source, size, flip=(False, False)):
    size, rect, border, pivot, ppu = validate(source, size)
    x, sx = cuts(size[0], border[0]/ppu, border[2]/ppu, pivot[0])
    y, sy = cuts(size[1], border[1]/ppu, border[3]/ppu, pivot[1])
    px = [0, border[0], rect[0]-border[2], rect[0]]
    py = [0, border[1], rect[1]-border[3], rect[1]]
    vertices = [[xx, yy, 0.0] for yy in y for xx in x]
    pixels = [[xx, yy] for yy in py for xx in px]
    indices, cells = [], []
    for iy in range(3):
        for ix in range(3):
            bl, br = iy*4+ix, iy*4+ix+1
            tl, tr = bl+4, br+4
            first = len(indices)
            indices.extend([bl, tl, br, br, tl, tr])
            cells.append(dict(column=ix, row=iy, index_start=first, index_count=6,
                              degenerate=x[ix] == x[ix+1] or y[iy] == y[iy+1]))
    return finish("sliced", source, size, vertices, pixels, indices, cells,
                  dict(destination_cuts=[x, y], source_pixel_cuts=[px, py],
                       border_compression_factors=[sx, sy],
                       compression_scope="Proportional compression is explicit model policy, not native-generator proof"), flip)


def tiled_axis(length, extent_px, first_px, last_px, ppu, pivot):
    axis, factor = cuts(length, first_px/ppu, last_px/ppu, pivot)
    segments = []
    if axis[1] > axis[0]:
        segments.append(dict(destination=[axis[0], axis[1]], source=[0, first_px], region="first_border"))
    center_length = axis[2]-axis[1]
    center_px = extent_px-first_px-last_px
    if center_length > 0:
        if center_px <= 0:
            raise UnsupportedGeometry("positive destination center has no source tile seed")
        seed = center_px/ppu
        if not math.isfinite(center_length/seed) or center_length/seed > MAX_QUADS:
            raise UnsupportedGeometry("tile axis budget exceeded")
        count = math.ceil(center_length/seed)
        for i in range(count):
            start = axis[1]+i*seed
            end = min(axis[1]+(i+1)*seed, axis[2])
            if end <= start:
                continue
            # No UV endpoint crosses into neighboring atlas content for a partial tile.
            fraction = min(1.0, (end-start)/seed)
            segments.append(dict(destination=[start, end],
                                 source=[first_px, first_px+center_px*fraction],
                                 region="repeat_center", tile=i, fraction=fraction))
    if axis[3] > axis[2]:
        segments.append(dict(destination=[axis[2], axis[3]], source=[extent_px-last_px, extent_px], region="last_border"))
    return segments, factor


def tiled(source, size, tile_mode=0, flip=(False, False), adaptive_threshold=None):
    size, rect, border, pivot, ppu = validate(source, size)
    if type(tile_mode) is not int or tile_mode != 0:
        raise UnsupportedGeometry("adaptive tiled mode requires native threshold/rounding evidence")
    xs, sx = tiled_axis(size[0], rect[0], border[0], border[2], ppu, pivot[0])
    ys, sy = tiled_axis(size[1], rect[1], border[1], border[3], ppu, pivot[1])
    if not xs or not ys or len(xs)*len(ys) > MAX_QUADS:
        raise UnsupportedGeometry("quad budget exceeded or empty tile axis")
    vertices, pixels, indices, cells = [], [], [], []
    for iy, yy in enumerate(ys):
        for ix, xx in enumerate(xs):
            x0, x1 = xx["destination"]
            y0, y1 = yy["destination"]
            u0, u1 = xx["source"]
            v0, v1 = yy["source"]
            base = len(vertices)
            vertices.extend([[x0,y0,0.0], [x1,y0,0.0], [x0,y1,0.0], [x1,y1,0.0]])
            pixels.extend([[u0,v0], [u1,v0], [u0,v1], [u1,v1]])
            indices.extend([base,base+2,base+1,base+1,base+2,base+3])
            cells.append(dict(column=ix, row=iy, x_region=xx["region"], y_region=yy["region"],
                              vertex_start=base, index_start=len(indices)-6, index_count=6))
    return finish("continuous_tiled", source, size, vertices, pixels, indices, cells,
                  dict(axes=[xs,ys], border_compression_factors=[sx,sy],
                       adaptive_threshold_serialized_not_used=adaptive_threshold,
                       repeat_policy="Full source-center repeats then UV-clipped final tile; shared borders not repeated across center"), flip)


def invariants(mesh, source):
    vertices, uvs, indices = mesh["vertices"], mesh["uvs"], mesh["indices"]
    if len(vertices) != len(uvs) or len(indices) % 3 or not vertices:
        raise ValueError("invalid channel/index lengths")
    if any(type(i) is not int or not 0 <= i < len(vertices) for i in indices):
        raise ValueError("out-of-range index")
    mins = [min(v[i] for v in vertices) for i in range(3)]
    maxs = [max(v[i] for v in vertices) for i in range(3)]
    area, zero, positive, negative = 0.0, 0, 0, 0
    for i in range(0, len(indices), 3):
        a, b, c = (vertices[j] for j in indices[i:i+3])
        cross = (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
        area += abs(cross)*0.5
        zero += cross == 0
        positive += cross > 0
        negative += cross < 0
    expected = mesh["size"][0]*mesh["size"][1]
    tolerance = 1e-10*max(1.0, expected)
    if not math.isfinite(area) or abs(area-expected) > tolerance:
        raise ValueError("cell triangle areas do not cover requested rectangle")
    if any(abs(maxs[i]-mins[i]-mesh["size"][i]) > tolerance for i in range(2)):
        raise ValueError("position extent differs from requested rectangle")
    if any(not -1e-12 <= n <= 1+1e-12 for pair in uvs for n in pair):
        raise ValueError("UV outside owning texture")
    return dict(vertex_count=len(vertices), uv_count=len(uvs), index_count=len(indices),
                triangle_count=len(indices)//3, cell_count=len(mesh["cells"]),
                all_indices_in_range=True, all_finite=True, aabb=[mins,maxs],
                triangle_area_sum=area, requested_rectangle_area=expected,
                area_error=area-expected, area_tolerance=tolerance,
                zero_area_triangles=zero, positive_winding_triangles=positive,
                negative_winding_triangles=negative,
                uv_min=[min(p[i] for p in uvs) for i in range(2)],
                uv_max=[max(p[i] for p in uvs) for i in range(2)],
                scope="Topology/arithmetic invariants only. No texel, shader, culling or rendered-coverage proof")
