"""#4 actual byte tables / all-text static plans / deliberately bounded CPU previews.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
import copy
import gzip
import json
import struct
import unittest

from tools.verify.geometry_8141386a_sources import canonical,sha
from tools.verify.geometry_8141386a_tmp_sources import load
from tools.verify.l3_chain_graph import key
from tools.verify.l3_geometry_8141386a_tmp import font_bank,resolve,text_fallback,build,OUT,WITNESS
from tools.verify.l3_geometry_8141386a_tmp_binary import glyph_table,character_table,decode_glyphs,decode_characters,exact_table_witness


class TMPGeometry8141386a(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selected=load();cls.bank=font_bank(cls.selected);cls.value=build()
        cls.font={'serialized_file':'data.unity3d/sharedassets0.assets','path_id':105}
        cls.rows={key(r['identity']):r['record'] for r in cls.selected['records']}
        cls.case=next(c for c in cls.selected['texts'] if c['identity']=={'serialized_file':'data.unity3d/level0','path_id':86})

    def literal(self,text,**props):
        row=copy.deepcopy(self.rows[key(self.case['identity'])]);row['tree'].update(m_text=text,**props)
        return text_fallback(self.bank,self.case,row)

    def test_font_character_glyph_counts_not_conflated(self):
        c=self.value['counts']
        self.assertEqual((c['fonts'],c['glyph_rows'],c['character_rows'],c['unicode_union']),(7,2352,2354,2285))
        self.assertEqual([len(f['characters']) for f in self.value['fonts']],[234,66,329,435,1174,19,97])
        self.assertEqual(len(self.bank[('data.unity3d/sharedassets0.assets',109)]['glyphs']),1172)

    def test_every_glyph_rect_is_bound_to_actual_owning_texture(self):
        for f in self.bank.values():
            for g in f['glyphs']:
                self.assertTrue(g['within_bound'])
                self.assertTrue(all(0<=n<=1 for n in g['uv_rect']))
                self.assertIn(g['texture'],[a['identity'] for a in f['atlases']])
            self.assertEqual(f['population_mode'],0)
            self.assertEqual(f['source_font_pptr'],{'m_FileID':0,'m_PathID':0})

    def test_complete_original_source_byte_tables_redecode_exactly(self):
        v=json.loads(gzip.decompress(WITNESS.read_bytes()))
        self.assertEqual(len(v['objects']),1751)
        font_objects=[o for o in v['objects'] if o['role']=='font']
        self.assertEqual(len(font_objects),7)
        for o in font_objects:
            tree=self.rows[key(o['identity'])]['tree']
            for name,field,decoder,encoder in [('glyphs','m_GlyphTable',decode_glyphs,glyph_table),('characters','m_CharacterTable',decode_characters,character_table)]:
                t=o['tables'][name];b=bytes.fromhex(t['hex'])
                self.assertEqual(t['object_offset']%4,0)
                self.assertEqual(sha(b),t['sha256'])
                self.assertEqual(encoder(tree[field]),b)
                self.assertEqual(decoder(b),tree[field])

    def test_table_search_requires_whole_unique_array(self):
        data=glyph_table(self.rows[key(self.font)]['tree']['m_GlyphTable'])
        self.assertEqual(exact_table_witness(b'abcd'+data+b'tail',data)['object_offset'],4)
        for blob in [b'absent',data+data,b'x'+data]:
            with self.subTest(blob_len=len(blob)),self.assertRaises(ValueError):exact_table_witness(blob,data)

    def test_truncated_or_wrong_count_tables_reject(self):
        for decoder in (decode_glyphs,decode_characters):
            for data in [b'',b'\0',struct.pack('<I',3),struct.pack('<I',0)+b'extra']:
                with self.subTest(decoder=decoder.__name__,size=len(data)),self.assertRaises((ValueError,struct.error)):decoder(data)

    def test_actual_serialized_fallback_order_and_first_match(self):
        source=self.bank[key(self.font)]
        self.assertEqual([f['path_id'] for f in source['fallbacks']],[110,106,108,109,111,107])
        hit,visited=resolve(self.bank,self.font,ord('A'))
        self.assertEqual(hit['font'],self.font);self.assertEqual(len(visited),1)
        missing,visited=resolve(self.bank,self.font,0x10ffff)
        self.assertIsNone(missing);self.assertEqual([i[1] for i in visited],[105,110,106,108,109,111,107])

    def test_real_currency_korean_and_arabic_fallbacks(self):
        primary={c['m_Unicode'] for c in self.bank[key(self.font)]['characters']}
        for target in (110,108,107):
            f=self.bank[('data.unity3d/sharedassets0.assets',target)]
            candidates=[c['m_Unicode'] for c in f['characters'] if c['m_Unicode'] not in primary]
            self.assertTrue(candidates)
            cp=next(cp for cp in candidates if resolve(self.bank,self.font,cp)[0]['font']['path_id']==target)
            hit,visited=resolve(self.bank,self.font,cp)
            self.assertEqual(hit['font']['path_id'],target)
            self.assertIn(('data.unity3d/sharedassets0.assets',target),visited)

    def test_fallback_cycle_terminates_without_new_font_guess(self):
        bank=copy.deepcopy(self.bank);bank[key(self.font)]['fallbacks'].insert(0,self.font)
        hit,visited=resolve(bank,self.font,0x10ffff)
        self.assertIsNone(hit);self.assertEqual(len(visited),7)
        self.assertEqual(resolve(self.bank,None,ord('A')),(None,[]))

    def test_1737_source_rows_each_have_literal_static_plan(self):
        self.assertEqual(len(self.value['texts']),1737)
        for t in self.value['texts']:
            self.assertEqual(len(t['literal_text']),len(t['fallback_plan']))
            self.assertEqual([p['unicode'] for p in t['fallback_plan']],[ord(c) for c in t['literal_text']])
            self.assertIsNone(t['scene_geometry']);self.assertIsNone(t['runtime_text'])

    def test_one_null_component_font_is_not_defaulted(self):
        rows=[t for t in self.value['texts'] if t['font'] is None]
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['identity']['path_id'],699094)
        self.assertIsNone(rows[0]['geometry'])
        self.assertFalse(rows[0]['missing_indices'])
        self.assertTrue(any('null serialized' in r for r in rows[0]['reason']))
        self.assertFalse(any('font' in p for p in rows[0]['fallback_plan']))

    def test_version_is_a_metric_uv_preview_not_scene_unit_mesh(self):
        row=next(t for t in self.value['texts'] if t['identity']==self.case['identity'])
        m=row['geometry'];self.assertEqual(row['literal_text'],'Version')
        self.assertEqual((len(m['vertices']),len(m['uvs']),len(m['indices'])),(28,28,42))
        self.assertIn('NOT_TMP_MESH',m['status']);self.assertIn('NOT em',m['policy'])
        first=row['fallback_plan'][0];f=self.bank[key(first['font'])];metrics=f['glyphs'][first['glyph_row']]['source']['m_Metrics']
        self.assertAlmostEqual(m['vertices'][0][0],metrics['m_HorizontalBearingX']/f['face']['m_PointSize'])
        self.assertIsNone(row['scene_geometry'])

    def test_spaces_advance_without_fake_quads(self):
        m=self.literal(' ')['geometry'];self.assertIsNotNone(m)
        self.assertEqual(m['vertices'],[]);self.assertEqual(m['indices'],[]);self.assertIsNone(m['aabb'])
        hit,_=resolve(self.bank,self.font,32);f=self.bank[key(hit['font'])]
        expected=hit['glyph']['source']['m_Metrics']['m_HorizontalAdvance']/f['face']['m_PointSize']
        self.assertGreater(expected,0);self.assertAlmostEqual(m['pointSize_normalized_pen_end'][0],expected)

    def test_crlf_is_one_model_linebreak_not_two_quads(self):
        m=self.literal('A\r\nB')['geometry'];self.assertEqual(m['line_count'],2)
        self.assertEqual(len(m['quads']),2)
        self.assertEqual([q['character_index'] for q in m['quads']],[0,3])
        f=self.bank[key(self.font)];self.assertAlmostEqual(m['advances'][-1]['start'][1],-f['face']['m_LineHeight']/f['face']['m_PointSize'])

    def test_rich_text_and_case_flags_reject_mesh_not_parsed_by_guess(self):
        for text,props,reason in [('A<size=9>B</size>',{},'rich-text'),('abc',{'m_fontStyle':16},'style'),
                                  ('A',{'m_enableAutoSizing':True},'auto-sizing'),('A',{'m_enableWordWrapping':True},'word-wrap'),
                                  ('A',{'m_characterSpacing':1},'spacing')]:
            row=self.literal(text,**props)
            with self.subTest(reason=reason):
                self.assertIsNone(row['geometry']);self.assertTrue(any(reason in r for r in row['reason']))
                self.assertEqual(row['literal_text'],text)

    def test_complex_shaping_and_unknown_control_are_not_visual_missing_claims(self):
        for text in ['A\u0301','\u0627','A\vB']:
            row=self.literal(text);self.assertIsNone(row['geometry'])
            self.assertTrue(any('shaping' in r or 'control' in r for r in row['reason']))
        control=self.literal('\v');self.assertFalse(control['missing_indices'])
        self.assertIn('NOT_a_missing_visual_glyph',control['fallback_plan'][0]['status'])

    def test_unknown_visible_codepoint_has_no_replacement_or_advance(self):
        row=self.literal('\U0010ffff')
        self.assertEqual(row['missing_indices'],[0]);self.assertIsNone(row['geometry'])
        self.assertNotIn('font',row['fallback_plan'][0]);self.assertNotIn('advance',row['fallback_plan'][0])

    def test_bad_atlas_bounds_or_dangling_glyph_fail_closed(self):
        for mutation in ['bounds','glyph','atlas']:
            selected=copy.deepcopy(self.selected)
            font_id=selected['fonts'][0]['identity'];r=next(r for r in selected['records'] if r['identity']==font_id)['record']['tree']
            if mutation=='bounds':r['m_GlyphTable'][0]['m_GlyphRect']['m_X']=100000
            elif mutation=='glyph':r['m_CharacterTable'][0]['m_GlyphIndex']=100000
            else:r['m_GlyphTable'][0]['m_AtlasIndex']=100000
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):font_bank(selected)

    def test_duplicate_glyph_index_rejects_ambiguous_lookup(self):
        selected=copy.deepcopy(self.selected);font_id=selected['fonts'][0]['identity']
        r=next(r for r in selected['records'] if r['identity']==font_id)['record']['tree']
        r['m_GlyphTable'][1]['m_Index']=r['m_GlyphTable'][0]['m_Index']
        with self.assertRaisesRegex(ValueError,'duplicate'):font_bank(selected)

    def test_real_preview_counts_and_explicit_noncoverage(self):
        c=self.value['counts']
        self.assertEqual(c['statuses'],{'bounded_literal_preview':797,'static_plan_only_geometry_not_generated':940})
        self.assertEqual(c['preview_quads'],1608)
        self.assertEqual(c['null_font_rows'],1);self.assertEqual(c['literal_missing_rows'],0)
        self.assertEqual(c['unresolved_component_or_control_lookup_rows'],2)
        for t in self.value['texts']:
            if t['geometry'] is not None:
                m=t['geometry'];self.assertEqual(len(m['vertices']),4*len(m['quads']))
                self.assertEqual(len(m['indices']),6*len(m['quads']))
                self.assertTrue(all(0<=i<len(m['vertices']) for i in m['indices']))
            else:self.assertTrue(t['reason'])

    def test_artifact_is_deterministic_and_final_witness_not_pending(self):
        self.assertEqual(OUT.read_bytes(),gzip.compress(canonical(self.value),mtime=0))
        self.assertNotIn('PENDING',self.value['byte_witness']['status'])
        self.assertEqual(self.value['byte_witness']['objects'],1751)


if __name__=='__main__':unittest.main()
