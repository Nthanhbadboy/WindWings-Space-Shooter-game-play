"""#4 static TMP fallback plans + bounded glyph-metric CPU previews.
provenance: arena/8141386a-windwings-space-shooter-game-p
NOT original TMP.GenerateTextMesh / shaping / scene-unit scale / native SDF padding.
"""
from __future__ import annotations
import argparse
from collections import Counter
import gzip
import json
import math
import unicodedata

from tools.verify.geometry_8141386a_sources import ROOT,RAW,BRANCH,sha,canonical
from tools.verify.geometry_8141386a_tmp_sources import load,OUT as SELECTED,QUERY
from tools.verify.l3_chain_graph import key
from tools.verify.l3_geometry_8141386a_tmp_binary import decode_glyphs,decode_characters

OUT=ROOT/'datas/l3_geometry_tmp_8141386a.json.gz'
WITNESS=RAW/'tmp/byte-witness.json.gz'


def font_bank(selected):
    records={key(r['identity']):r for r in selected['records']};bank={}
    for f in selected['fonts']:
        record=records[key(f['identity'])];t=record['record']['tree'];atlases=f['atlases']
        glyphs=[]
        if len({g['m_Index'] for g in t['m_GlyphTable']})!=len(t['m_GlyphTable']):raise ValueError('duplicate glyph index')
        if len({c['m_Unicode'] for c in t['m_CharacterTable']})!=len(t['m_CharacterTable']):raise ValueError('ambiguous character Unicode')
        for glyph in t['m_GlyphTable']:
            gi=glyph['m_AtlasIndex']
            if not 0<=gi<len(atlases):raise ValueError('glyph atlas index unresolved')
            atlas=atlases[gi];rect=glyph['m_GlyphRect'];x,y,w,h=(rect[n] for n in ('m_X','m_Y','m_Width','m_Height'))
            if min(x,y,w,h)<0 or x+w>atlas['width'] or y+h>atlas['height']:raise ValueError('glyph outside owning atlas')
            if atlas['width']!=t['m_AtlasWidth'] or atlas['height']!=t['m_AtlasHeight']:raise ValueError('declared/actual font atlas dimensions differ')
            glyphs.append(dict(source=glyph,texture=atlas['identity'],rect_px=[x,y,w,h],
                               uv_rect=[x/atlas['width'],y/atlas['height'],(x+w)/atlas['width'],(y+h)/atlas['height']],
                               within_bound=True,zero_area_rect=w==0 or h==0))
        indices={g['source']['m_Index'] for g in glyphs}
        if any(c['m_GlyphIndex'] not in indices for c in t['m_CharacterTable']):raise ValueError('character glyph unresolved')
        face=t['m_FaceInfo']
        if face['m_PointSize']<=0 or not math.isfinite(face['m_Scale']):raise ValueError('invalid face normalization')
        bank[key(f['identity'])]=dict(identity=f['identity'],name=t['m_Name'],face=face,glyphs=glyphs,
                                     characters=t['m_CharacterTable'],fallbacks=f['fallbacks'],atlases=atlases,
                                     atlas_padding_px=t['m_AtlasPadding'],population_mode=t['m_AtlasPopulationMode'],
                                     source_font_pptr=t['m_SourceFontFile'],font_feature_table=t['m_FontFeatureTable'],
                                     raw_object_sha256=record['record']['raw_object_sha256'],raw_location=record['raw_location'])
    return bank


def resolve(bank,start,cp):
    visited=[]
    def visit(k):
        if k is None or k in visited or k not in bank:return None
        visited.append(k);font=bank[k]
        for i,c in enumerate(font['characters']):
            if c['m_Unicode']==cp:
                j=next(j for j,g in enumerate(font['glyphs']) if g['source']['m_Index']==c['m_GlyphIndex'])
                return dict(font=font['identity'],character_row=i,glyph_row=j,character=c,glyph=font['glyphs'][j])
        for fallback in font['fallbacks']:
            result=visit(key(fallback))
            if result is not None:return result
        return None
    result=visit(key(start) if start is not None else None);return result,visited


def preview(bank,start,text,plan):
    font=bank[key(start)];line_step=font['face']['m_LineHeight']/font['face']['m_PointSize']*font['face']['m_Scale']
    x=y=0.0;vertices=[];uvs=[];indices=[];quads=[];advances=[];lines=1
    for i,(ch,p) in enumerate(zip(text,plan)):
        cp=ord(ch)
        if cp==13 and i+1<len(text) and text[i+1]=='\n':continue
        if cp in (10,13):x=0.0;y-=line_step;lines+=1;continue
        if cp<32:raise ValueError('control outside bounded preview')
        f=bank[key(p['font'])];g=f['glyphs'][p['glyph_row']];c=f['characters'][p['character_row']]
        metrics=g['source']['m_Metrics'];factor=f['face']['m_Scale']/f['face']['m_PointSize']*g['source']['m_Scale']*c['m_Scale']
        advance=metrics['m_HorizontalAdvance']*factor
        if not math.isfinite(advance):raise ValueError('nonfinite advance')
        if not g['zero_area_rect'] and metrics['m_Width']>0 and metrics['m_Height']>0:
            x0=x+metrics['m_HorizontalBearingX']*factor;y1=y+metrics['m_HorizontalBearingY']*factor
            x1=x0+metrics['m_Width']*factor;y0=y1-metrics['m_Height']*factor
            u0,v0,u1,v1=g['uv_rect'];base=len(vertices)
            vertices.extend([[x0,y0,0.0],[x1,y0,0.0],[x0,y1,0.0],[x1,y1,0.0]])
            uvs.extend([[u0,v0],[u1,v0],[u0,v1],[u1,v1]])
            indices.extend([base,base+2,base+1,base+1,base+2,base+3])
            quads.append(dict(character_index=i,font=p['font'],texture=g['texture'],glyph_row=p['glyph_row'],vertex_start=base,index_start=len(indices)-6))
        advances.append(dict(character_index=i,start=[x,y],advance=advance));x+=advance
    if any(not math.isfinite(n) for p in vertices+uvs for n in p):raise ValueError('nonfinite glyph geometry')
    if any(not 0<=i<len(vertices) for i in indices):raise ValueError('glyph index out of range')
    bounds=[[min(v[i] for v in vertices) for i in range(3)],[max(v[i] for v in vertices) for i in range(3)]] if vertices else None
    return dict(status='METRIC_RECT_CPU_PREVIEW_NOT_TMP_MESH',vertices=vertices,uvs=uvs,indices=indices,quads=quads,
                advances=advances,pointSize_normalized_pen_end=[x,y],line_count=lines,aabb=bounds,
                invariant=dict(vertices=len(vertices),uvs=len(uvs),indices=len(indices),quads=len(quads),
                               indices_in_range=True,all_finite=True,source_glyph_rects_within_atlases=True),
                policy='LTR literal/no kerning, wrap, alignment, auto-size, glyph padding/style, shaping or scene-unit scale; normalized per owning face pointSize, NOT em (UnitsPerEM=0)')


def text_fallback(bank,case,row):
    t=row['tree'];text=t['m_text'];plan=[];missing=[]
    for i,ch in enumerate(text):
        hit,visited=resolve(bank,case['font'],ord(ch))
        record=dict(index=i,unicode=ord(ch),search_order=[bank[k]['identity'] for k in visited])
        if hit is not None:record.update({k:hit[k] for k in ('font','character_row','glyph_row')});record['status']='static_character_resolved'
        elif case['font'] is None:record['status']='unresolved_component_font_NOT_a_font_bank_missing_glyph_claim'
        elif ch in '\r\n':record['status']='control_linebreak_not_a_missing_visual_glyph'
        elif ord(ch)<32:record['status']='unmodelled_control_NOT_a_missing_visual_glyph_claim'
        else:record['status']='missing_no_replacement_or_advance_invented';missing.append(i)
        plan.append(record)
    reasons=[]
    if case['font'] is None:reasons.append('null serialized component font; settings default is not automatically assigned')
    if missing:reasons.append('one or more literal codepoints absent from source-owned fallback chain')
    if t['m_isRichText'] and '<' in text:reasons.append('rich-text tokens require native/parser evidence; not drawn as literal tags')
    if t['m_fontStyle']!=0:reasons.append('font style/case/small-caps policy not executed')
    if t['m_enableAutoSizing']:reasons.append('native auto-sizing not executed')
    if t['m_enableWordWrapping']:reasons.append('word-wrap requires actual layout container/native policy')
    if t['m_isRightToLeft'] or any(unicodedata.combining(c) or unicodedata.bidirectional(c) in ('R','AL') for c in text):
        reasons.append('complex/RTL shaping not executed')
    if any(ord(c)<32 and c not in '\r\n' for c in text):reasons.append('control outside CR/LF preview domain')
    # Serialized spacing is retained, not secretly ignored in a "complete" layout.
    if any(t.get(n,0)!=0 for n in ('m_characterSpacing','m_wordSpacing','m_lineSpacing','m_paragraphSpacing')):
        reasons.append('serialized spacing beyond bounded zero-spacing policy')
    geometry=preview(bank,case['font'],text,plan) if not reasons else None
    properties={n:t.get(n) for n in ('m_fontSize','m_fontStyle','m_fontWeight','m_enableAutoSizing','m_enableWordWrapping',
                                    'm_isRichText','m_isRightToLeft','m_enableKerning','m_characterSpacing','m_wordSpacing',
                                    'm_lineSpacing','m_paragraphSpacing','m_HorizontalAlignment','m_VerticalAlignment','m_margin')}
    return dict(**case,literal_text=text,utf8_sha256=sha(text.encode()),raw_object_sha256=row['raw_object_sha256'],properties=properties,
                fallback_plan=plan,missing_indices=missing,status='bounded_literal_preview' if geometry is not None else 'static_plan_only_geometry_not_generated',
                geometry=geometry,reason=reasons,scene_geometry=None,runtime_text=None)


def byte_witness(selected,required=True):
    if not WITNESS.exists():
        if required:raise ValueError('fresh TMP source byte witness pending')
        return dict(status='PENDING_NOT_HANDOFF_READY')
    v=json.loads(gzip.decompress(WITNESS.read_bytes()))
    if v['provenance']!=BRANCH or v['item']!=4 or v['xapk_sha256']!=selected['xapk_sha256']:raise ValueError('TMP witness identity mismatch')
    for p,h in v['tool_pins'].items():
        if sha((ROOT/p).read_bytes())!=h:raise ValueError('TMP recovery tool/query drift: '+p)
    rows={key(r['identity']):r['record'] for r in selected['records']}
    if len(v['objects'])!=len(rows):raise ValueError('fresh object coverage incomplete')
    font_tables=[]
    for o in v['objects']:
        row=rows[key(o['identity'])]
        if row['raw_object_sha256']!=o['object_sha256']:raise ValueError('fresh raw object SHA mismatch')
        if o['role']!='font':continue
        for name,decoder,source in [('glyphs',decode_glyphs,'m_GlyphTable'),('characters',decode_characters,'m_CharacterTable')]:
            table=o['tables'][name];body=bytes.fromhex(table['hex'])
            if sha(body)!=table['sha256'] or decoder(body)!=row['tree'][source]:raise ValueError('font table re-decode differs from source metadata')
        font_tables.append(dict(identity=o['identity'],object_sha256=o['object_sha256'],
                                tables={n:{k:v for k,v in t.items() if k!='hex'} for n,t in o['tables'].items()}))
    return dict(status='FRESH_ORIGINAL_TABLE_BYTES_CORROBORATE_CAPTURE_NOT_NATIVE_LAYOUT',receipt_sha256=sha(WITNESS.read_bytes()),
                xapk_sha256=v['xapk_sha256'],bundle_sha256=v['bundle_sha256'],objects=len(v['objects']),font_tables=font_tables,
                scope=v['scope'])


def build(require_witness=True):
    selected=load();bank=font_bank(selected);rows={key(r['identity']):r['record'] for r in selected['records']}
    texts=[text_fallback(bank,c,rows[key(c['identity'])]) for c in selected['texts']]
    counts=dict(fonts=len(bank),glyph_rows=sum(len(f['glyphs']) for f in bank.values()),character_rows=sum(len(f['characters']) for f in bank.values()),
                unicode_union=len({c['m_Unicode'] for f in bank.values() for c in f['characters']}),texts=len(texts),
                statuses=dict(Counter(t['status'] for t in texts)),null_font_rows=sum(t['font'] is None for t in texts),
                literal_missing_rows=sum(bool(t['missing_indices']) for t in texts),
                unresolved_component_or_control_lookup_rows=sum(any(p['status'].startswith(('unresolved_component','unmodelled_control')) for p in t['fallback_plan']) for t in texts),
                empty_literal_rows=sum(not t['literal_text'] for t in texts),
                nonempty_previews=sum(bool(t['geometry'] and t['geometry']['quads']) for t in texts),
                preview_quads=sum(len(t['geometry']['quads']) for t in texts if t['geometry']),
                reason_counts=dict(Counter(r for t in texts for r in t['reason'])))
    paths=[SELECTED,QUERY,ROOT/'tools/verify/l3_geometry_8141386a_tmp.py',ROOT/'tools/verify/geometry_8141386a_tmp_sources.py',ROOT/'tools/verify/l3_geometry_8141386a_tmp_binary.py']
    if WITNESS.exists():paths.append(WITNESS)
    return dict(schema=1,item=4,provenance=BRANCH,disposition='SOURCE_PINNED_STATIC_FALLBACK_AND_BOUNDED_LITERAL_PREVIEW_NOT_TMP_RUNTIME',
                counts=counts,fonts=list(bank.values()),texts=texts,byte_witness=byte_witness(selected,require_witness),
                lineage=selected['lineage'],source_pins=selected['source_pins'],inputs={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths},
                settings_default_font_FACT_NOT_ASSIGNMENT=selected['settings_default_font_FACT_NOT_ASSIGNMENT'],
                boundary=['Every1737 row has a static source-font fallback plan; not all rows have generated geometry.',
                          'No font assigned to the single null-font component. No missing character advance, tofu or default mesh invented.',
                          'Preview is glyph metric rectangles paired to serialized atlas rect UVs, NOT native SDF padded quads, scene scale, alignment or kerning.',
                          'Styles/casing/rich-text/auto-size/wrap/complex shaping/nonzero spacing/control domains reject geometry explicitly.',
                          'Live/localized/formatted strings, native TMP mesh generation and renderer/material/pixel acceptance need approved same-build execution/readback.'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');p.add_argument('--allow-pending-witness',action='store_true');a=p.parse_args()
    value=build(not a.allow_pending_witness);body=gzip.compress(canonical(value),mtime=0)
    if a.check:
        if OUT.read_bytes()!=body:raise SystemExit('TMP artifact drift')
    else:OUT.write_bytes(body)
    print(json.dumps(value['counts'],sort_keys=True));print('sha256',sha(body),'bytes',len(body))
