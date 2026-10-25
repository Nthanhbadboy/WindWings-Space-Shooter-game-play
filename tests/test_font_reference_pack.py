import copy
import gzip
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/recovery'))
import font_reference_pack as pack


def fixture(root):
    archive=root/'source.zip';atlas=b'synthetic atlas fixture; not rendered media';ttf=b'synthetic font fixture; not a real TTF'
    with zipfile.ZipFile(archive,'w') as z:z.writestr('Texture2D/font.png',atlas);z.writestr('Font/font.ttf',ttf)
    def source(path,blob):return dict(path=path,bytes=len(blob),sha256=pack.sha(blob))
    identity=dict(serialized_file='data.unity3d/test.assets',type='MonoBehaviour',path_id=105)
    material=dict(serialized_file=identity['serialized_file'],type='Material',path_id=2)
    texture=dict(serialized_file=identity['serialized_file'],type='Texture2D',path_id=3)
    f=dict(identity=identity,material=material,name='Synthetic SDF',family='Synthetic',character_count=1,glyph_count=1,
        atlas_padding=1,atlases=[dict(identity=texture,png=source('Texture2D/font.png',atlas),source_dimensions=[1,1])])
    contract=dict(fonts=[f],static_chain_order=[identity],sources_sha256_decompressed={})
    catalog=dict(objects=[dict(serialized_file=identity['serialized_file'],type='Font',path_id=4,name='Synthetic program',status='exported',outputs=[source('Font/font.ttf',ttf)])])
    objects={pack.key(identity):dict(class_name='TMP_FontAsset',tree={'m_FontFeatureTable':{'test':1}}),pack.key(material):dict(type='Material',tree={'m_SavedProperties':{'test':2}})}
    return archive,contract,catalog,objects,pack.sha(archive.read_bytes())


class FontReferenceTests(unittest.TestCase):
    def test_exact_media_self_contained_browser_and_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);args=fixture(root);archive,c,cat,objects,expected=args;out=root/'out'
            before=copy.deepcopy(c);manifest=pack.assemble(archive,out,c,cat,objects,expected)
            self.assertEqual(c,before)
            f=manifest['fonts'][0]
            self.assertEqual((out/f['atlas']).read_bytes(),b'synthetic atlas fixture; not rendered media')
            metadata=json.loads((out/f['metadata']).read_text())
            self.assertEqual(metadata['raw_font_projection']['tree']['m_FontFeatureTable'],{'test':1})
            self.assertEqual(metadata['raw_primary_material_projection']['tree']['m_SavedProperties'],{'test':2})
            page=(out/'index.html').read_text();self.assertIn('This folder is self-contained',page)
            self.assertIn('src="'+f['atlas']+'"',page);self.assertNotIn('Copy this HTML file',page)
            self.assertIn('not_a_sourceFontFile_binding',manifest['font_programs'][0]['association'])
            zip_path=root/'bundle.zip'
            with zipfile.ZipFile(zip_path,'w') as z:
                for p in out.rglob('*'):
                    if p.is_file():z.write(p,p.relative_to(out).as_posix())
            audit=pack.audit(zip_path,manifest);self.assertTrue(all(audit['gates'].values()))
            with zipfile.ZipFile(zip_path,'a') as z:z.writestr('unexpected.txt','not in population')
            with self.assertRaises(AssertionError):pack.audit(zip_path,manifest)

    def test_rejects_bad_archive_and_member_before_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);archive,c,cat,objects,expected=fixture(root);out=root/'out'
            with self.assertRaises(AssertionError):pack.assemble(archive,out,c,cat,objects,'wrong')
            self.assertFalse(out.exists())
            c['fonts'][0]['atlases'][0]['png']['sha256']='wrong'
            with self.assertRaises(AssertionError):pack.assemble(archive,out,c,cat,objects,expected)
            self.assertFalse(out.exists())

    def test_existing_destination_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);archive,c,cat,objects,expected=fixture(root);out=root/'out';out.mkdir()
            sentinel=out/'existing';sentinel.write_text('keep')
            with self.assertRaises(FileExistsError):pack.assemble(archive,out,c,cat,objects,expected)
            self.assertEqual(sentinel.read_text(),'keep')

    def test_real_raw_font_features_and_primary_materials_available(self):
        objects=pack.load_objects();c=json.load(gzip.open(ROOT/'datas/font_language_contract.json.gz','rt'))
        self.assertEqual(len(c['fonts']),7)
        for f in c['fonts']:
            raw=objects[pack.key(f['identity'])];material=objects[pack.key(f['material'])]
            self.assertIn('m_FontFeatureTable',raw['tree'])
            self.assertIn('m_SavedProperties',material['tree'])
            self.assertEqual(raw['raw_object_sha256'],f['raw']['raw_object_sha256'])

class PreservedFontReferenceTests(unittest.TestCase):
    def test_real_bundle_metadata_and_delivery(self):
        sys.path.insert(0,str(ROOT/'tools/verify'))
        import font_reference_contracts
        result=font_reference_contracts.verify()
        self.assertEqual(result['fonts'],7)
        self.assertEqual(result['source_media'],8)
        self.assertTrue(result['post_upload_redownload_verified'])

    def test_publisher_is_manual_and_never_clobbers(self):
        workflow=(ROOT/'.github/workflows/assemble-font-reference.yml').read_text()
        self.assertIn('workflow_dispatch:',workflow)
        self.assertNotIn('  push:',workflow)
        self.assertNotIn('--clobber',workflow)
        self.assertIn("assert after['draft'] is True",workflow)


if __name__=='__main__':unittest.main()
