"""#4 narrow source selection, owning-file PPtrs, and fresh-byte queries.
provenance: arena/8141386a-windwings-space-shooter-game-p
Shared ef raw102/Graph and font73 are acknowledged; no peer captures are rewritten.
"""
from __future__ import annotations
import argparse
import gzip
import json
from collections import defaultdict
from tools.verify.geometry_8141386a_sources import ROOT,RAW,BRANCH,sha,canonical
from tools.verify.l3_visual_surface import read_source
from tools.verify.l3_chain_graph import identity,key
from tools.verify.l3_geometry_8141386a_tmp_binary import glyph_table,character_table

OUT=RAW/'tmp/selected-inputs.json.gz'
QUERY=RAW/'tmp/byte-queries.json.gz'


def build():
    index,g,loc,_=read_source();selected={};used={'reverse-engineering/raw/l3-visual-surface/index.json'}
    def keep(k):
        selected[k]=g.rows[k];used.add(loc[k]['path']);return g.rows[k]
    fonts=[];texts=[];queries=[]
    for k,r in sorted(g.rows.items()):
        if 'm_CharacterTable' not in r.get('tree',{}):continue
        t=keep(k)['tree'];atlases=[]
        for i in range(len(t['m_AtlasTextures'])):
            tex=g.target(k,f'.m_AtlasTextures[{i}]')
            if tex is None:raise ValueError('font atlas PPtr unresolved')
            row=keep(tex);atlases.append(dict(identity=identity(tex),width=row['width'],height=row['height'],
                                              raw_object_sha256=row['raw_object_sha256']))
        fallbacks=[identity(g.target(k,f'.m_FallbackFontAssetTable[{i}]')) for i in range(len(t['m_FallbackFontAssetTable']))]
        fonts.append(dict(identity=identity(k),atlases=atlases,fallbacks=fallbacks))
        queries.append(dict(identity=identity(k),class_id=r['class_id'],expected_object_sha256=r['raw_object_sha256'],role='font',
                            tables={'glyphs':glyph_table(t['m_GlyphTable']).hex(),'characters':character_table(t['m_CharacterTable']).hex()}))
    fontkeys={key(f['identity']) for f in fonts}
    for k,r in sorted(g.rows.items()):
        if 'm_text' not in r.get('tree',{}):continue
        keep(k);font=g.target(k,'.m_fontAsset')
        if font is not None and font not in fontkeys:raise ValueError('text font outside captured bank')
        texts.append(dict(identity=identity(k),font=identity(font),gameobject=identity(g.target(k,'.m_GameObject')),
                          class_name=r['class_name'],source_context='serialized_scene' if '/level' in k[0] else 'asset_template_NOT_placed'))
        queries.append(dict(identity=identity(k),class_id=r['class_id'],expected_object_sha256=r['raw_object_sha256'],role='text_hash_only'))
    for k,r in sorted(selected.items()):
        if r['type']=='Texture2D':queries.append(dict(identity=identity(k),class_id=r['class_id'],expected_object_sha256=r['raw_object_sha256'],role='atlas_hash_only'))
    contract=ROOT/'datas/font_language_contract.json.gz';used.add(str(contract.relative_to(ROOT)))
    old=json.loads(gzip.decompress(contract.read_bytes()))
    value=dict(schema=1,item=4,provenance=BRANCH,xapk_sha256=index['xapk_sha256'],fonts=fonts,texts=texts,
               settings_default_font_FACT_NOT_ASSIGNMENT=old['settings']['default_font'],
               records=[dict(identity=identity(k),record=selected[k],raw_location=loc[k]) for k in sorted(selected)],
               source_pins={p:sha((ROOT/p).read_bytes()) for p in sorted(used)},
               lineage='ef6b75ef raw102 + Graph from f5a447c15a; font73 contract. Shared capture/schema, not independent decoding')
    query=dict(schema=1,item=4,provenance=BRANCH,xapk_sha256=index['xapk_sha256'],objects=queries)
    return value,query


def load():
    value=json.loads(gzip.decompress(OUT.read_bytes()))
    for p,h in value['source_pins'].items():
        if sha((ROOT/p).read_bytes())!=h:raise ValueError('TMP source pin drift: '+p)
    grouped=defaultdict(list)
    for record in value['records']:grouped[record['raw_location']['path']].append(record)
    for p,records in grouped.items():
        lines=gzip.decompress((ROOT/p).read_bytes()).splitlines()
        for r in records:
            if json.loads(lines[r['raw_location']['row']])!=r['record']:raise ValueError('TMP selected source row drift')
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');a=parser.parse_args()
    value,query=build()
    for p,v in ((OUT,value),(QUERY,query)):
        body=gzip.compress(canonical(v),mtime=0)
        if a.check:
            if p.read_bytes()!=body:raise SystemExit('TMP selection/query drift')
        else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(body)
    print(len(value['fonts']),'fonts,',len(value['texts']),'text records,',len(value['records']),'distinct objects')
