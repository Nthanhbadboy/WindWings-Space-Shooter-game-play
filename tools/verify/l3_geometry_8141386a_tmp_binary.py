"""Narrow byte-table view seeded from captured TMP schema, NOT schema discovery.
provenance: arena/8141386a-windwings-space-shooter-game-p
52-byte glyph /16-byte character records are matched as complete count-prefixed arrays;
whole-array uniqueness + whole-object SHA required, never ambiguous float searching.
"""
import struct

METRICS=('m_Width','m_Height','m_HorizontalBearingX','m_HorizontalBearingY','m_HorizontalAdvance')
RECT=('m_X','m_Y','m_Width','m_Height')


def glyph_table(rows):
    out=bytearray(struct.pack('<I',len(rows)))
    for r in rows:
        out+=struct.pack('<I5f4ifiI',r['m_Index'],*(r['m_Metrics'][n] for n in METRICS),
                         *(r['m_GlyphRect'][n] for n in RECT),r['m_Scale'],r['m_AtlasIndex'],r['m_ClassDefinitionType'])
    if len(out)!=4+52*len(rows):raise ValueError('glyph record layout drift')
    return bytes(out)


def character_table(rows):
    return struct.pack('<I',len(rows))+b''.join(struct.pack('<IIIf',r['m_ElementType'],r['m_Unicode'],r['m_GlyphIndex'],r['m_Scale']) for r in rows)


def decode_glyphs(data):
    count=struct.unpack_from('<I',data)[0]
    if len(data)!=4+52*count:raise ValueError('glyph table span/count disagreement')
    result=[]
    for i in range(count):
        row=struct.unpack_from('<I5f4ifiI',data,4+52*i)
        result.append(dict(m_Index=row[0],m_Metrics=dict(zip(METRICS,row[1:6])),m_GlyphRect=dict(zip(RECT,row[6:10])),
                           m_Scale=row[10],m_AtlasIndex=row[11],m_ClassDefinitionType=row[12]))
    return result


def decode_characters(data):
    count=struct.unpack_from('<I',data)[0]
    if len(data)!=4+16*count:raise ValueError('character table span/count disagreement')
    names=('m_ElementType','m_Unicode','m_GlyphIndex','m_Scale')
    return [dict(zip(names,struct.unpack_from('<IIIf',data,4+16*i))) for i in range(count)]


def exact_table_witness(blob,expected):
    offset=blob.find(expected)
    if offset<0 or blob.find(expected,offset+1)>=0:raise ValueError('whole count-prefixed table missing or non-unique')
    if offset%4:raise ValueError('unexpected unaligned table')
    return dict(object_offset=offset,byte_size=len(expected),hex=blob[offset:offset+len(expected)].hex())
