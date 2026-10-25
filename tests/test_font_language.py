import gzip
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/verify'))
import font_language as fl


class FontLanguageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.contract=fl.build()

    def test_reproduces_contract(self):
        self.assertEqual(self.contract,json.load(gzip.open(ROOT/'datas/font_language_contract.json.gz','rt')))

    def test_offline_browser_is_regenerated_metadata_not_a_renderer(self):
        import font_browser
        page=font_browser.render(self.contract)
        self.assertEqual(page,(ROOT/'docs/assets/font-browser.html').read_text())
        self.assertEqual(page.count('<article>'),7)
        self.assertIn('Not a game-font rendering preview.',page)
        self.assertNotIn('https://',page)

    def test_first_index_not_last_or_first_nonempty_value(self):
        self.assertEqual(fl.lookup(['a','a'],['first','last'],'a'),'first')
        self.assertEqual(fl.lookup(['a','a'],['','later'],'a'),'')
        self.assertIsNone(fl.lookup(['a'],['one'],'unknown'))
        with self.assertRaises(AssertionError):fl.first_values(['a'],[])

    def test_translation_fallback_not_font_fallback(self):
        args=(['a','b'],['','translated'],['a','b'],['default a','default b'])
        self.assertEqual(fl.translated(*args,'a'),'default a')
        self.assertEqual(fl.translated(*args,'b'),'translated')
        self.assertEqual(fl.translated(*args,'b',True),'default b')
        self.assertEqual(fl.translated(*args,'missing'),'missing')
        self.assertEqual(fl.translated(['a'],[' '],['a'],['fallback'],'a'),' ')

    def test_font_asset_local_fallback_survives_null_global_entry(self):
        c=self.contract
        self.assertEqual(c['settings']['global_fallback_pointers'],[{'m_FileID':0,'m_PathID':0}])
        self.assertEqual([x['path_id'] for x in c['static_chain_order']],[105,110,106,108,109,111,107])
        self.assertEqual(c['static_chain_unique_codepoints'],2285)
        for f in c['fonts']:
            self.assertEqual(f['atlas_population_mode'],0)
            self.assertEqual(f['source_font_file'],{'m_FileID':0,'m_PathID':0})
            self.assertEqual(f['render_mode'],4165)
            self.assertEqual(len(f['atlases']),1)
            self.assertEqual(f['atlases'][0]['source_dimensions'],f['atlas_dimensions'])

    def test_serialized_components_not_live_screen_population(self):
        t=self.contract['text_components']
        self.assertEqual(t['count'],9797)
        self.assertEqual(t['font_assignments'][0]['count'],9796)
        self.assertEqual(t['null_font_components'][0]['path_id'],699094)
        self.assertEqual(t['right_to_left_counts'],{'False':9797})
        self.assertFalse(self.contract['scope']['all_MB_headers_classified'])
        self.assertEqual(len(self.contract['scope']['header_errors']),1)

    def test_locale_duplicate_override(self):
        c=self.contract
        self.assertEqual(len(c['languages']),19)
        for l in c['languages']:
            self.assertEqual(l['rows'],1426)
            self.assertEqual(l['nonempty_unique_keys'],1415)
            self.assertEqual(l['empty_key_rows'],9)
        en=next(l for l in c['languages'] if l['name']=='English')
        self.assertEqual(en['first_nonempty_key_values']['txt_free_after'],'Free after')
        d=next(d for d in en['duplicates'] if d['key']=='txt_free_after')
        self.assertEqual(d['indices'],[690,1243])
        self.assertEqual(d['values'],['Free after','Free After'])
        self.assertEqual(len(en['serialized_label_keys_absent']),11)

    def test_system_selection_default_differs_from_english_fallback(self):
        n=self.contract['native']
        self.assertEqual(n['methods'],34)
        self.assertTrue(all(n['checks'].values()))
        values={r['system_language']:r['language_value'] for r in n['system_default_by_enum']}
        self.assertEqual(values['Vietnamese'],1)
        self.assertEqual(values['ChineseSimplified'],18)
        self.assertEqual(values['Chinese'],0)
        self.assertEqual(values['ChineseTraditional'],0)
        self.assertEqual(values['Arabic'],6)

    def test_data_pack_prefers_raw_arrays_not_deduplicated_csv(self):
        spec=importlib.util.spec_from_file_location('font_test_data_pack',ROOT/'tools/apk-analyze/data_pack.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);docs=root/'docs/apk-analysis';docs.mkdir(parents=True)
            (docs/'12-localization.csv').write_text('Key,English,Vietnamese\ncsv_only,legacy,legacy\n')
            raw=root/'reverse-engineering/raw';raw.mkdir(parents=True)
            (raw/'font-language').symlink_to(ROOT/'reverse-engineering/raw/font-language',target_is_directory=True)
            old=sys.argv;sys.argv=['data_pack','--root',tmp]
            try:
                with redirect_stdout(io.StringIO()):self.assertEqual(module.main(),0)
            finally:sys.argv=old
            for short,language in [('en','English'),('vi','Vietnamese')]:
                generated=json.loads((root/f'i18n/{short}.json').read_text())
                expected=next(l for l in self.contract['languages'] if l['name']==language)
                self.assertEqual(generated['strings'],expected['first_nonempty_key_values'])
                self.assertIn('first IndexOf',generated['_source'])


if __name__=='__main__':unittest.main()
