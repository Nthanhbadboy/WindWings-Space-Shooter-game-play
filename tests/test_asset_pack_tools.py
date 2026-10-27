import importlib.util
import io
from pathlib import Path
import struct
import unittest
import wave

spec=importlib.util.spec_from_file_location('asset_pack_audit',Path('tools/recovery/asset_pack_audit.py'))
pack=importlib.util.module_from_spec(spec)
spec.loader.exec_module(pack)


class AssetPackToolTests(unittest.TestCase):
    def test_paths_reject_traversal_absolute_and_windows(self):
        for name in ('../escape','/tmp/escape','one/../../escape','one\\escape',''):
            self.assertFalse(pack.safe_path(name))
        self.assertTrue(pack.safe_path('AudioClip/name with spaces.wav'))

    def test_png_check_is_explicitly_header_only(self):
        data=b'\x89PNG\r\n\x1a\n'+b'\0'*8+struct.pack('>II',17,25)
        self.assertEqual(pack.inspect_media(data,'Sprite/a.png')['width'],17)
        self.assertIn('not visual',pack.inspect_media(data,'Sprite/a.png')['validation'])
        with self.assertRaises(AssertionError):
            pack.inspect_media(b'not PNG','Sprite/a.png')

    def test_wave_metadata_from_bytes_not_filename_guess(self):
        output=io.BytesIO()
        with wave.open(output,'wb') as w:
            w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000);w.writeframes(b'\0'*16000)
        result=pack.inspect_media(output.getvalue(),'AudioClip/anything.wav')
        self.assertEqual(result['seconds'],1)
        self.assertEqual(result['rate'],8000)
        self.assertIn('not listening',result['validation'])

    def test_browser_escapes_embedded_markup_and_needs_no_external_scripts(self):
        html=pack.browser_html({'files':[{'path':'</script><evil>','category':'other','kind':'other','bytes':0}]})
        self.assertNotIn('</script><evil>',html)
        self.assertIn('\\u003c/script>',html)
        self.assertNotIn('src="https://',html)
        self.assertIn('createElement',html)


if __name__=='__main__':
    unittest.main()
