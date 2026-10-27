"""Report118 source/native prototypes; bounded genuine fixtures, no Graph.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
from copy import deepcopy
import gzip
import json
import unittest
from tools.verify.geometry_8141386a_consumers_sources import RAW,SCHEMAS,load_inputs,catalog,catalog_rows,source_inputs
from tools.verify.geometry_8141386a_atlas_io import sha,sha_file,key
from tools.verify.l3_geometry_8141386a_gaps_binary import encode
from tools.recovery.geometry_8141386a_consumers_bytes import recovered


def prototypes():
    p=json.loads(gzip.decompress((RAW/'native-prototypes.json.gz').read_bytes()));s=json.loads(gzip.decompress(SCHEMAS.read_bytes()))
    if p['schemas_sha256']!=sha_file(SCHEMAS):raise ValueError('native prototype schema drift')
    return p['records'],s['classes']


class ConsumerSources(unittest.TestCase):
    def test_metadata_catalog_reproduces_without_full_sprite_fixture(self):
        self.assertEqual(list(catalog_rows()),list(catalog()));self.assertEqual(len(list(catalog())),2185)

    def test_source_pins_and_measured_native_metadata_counts(self):
        v=load_inputs();m=source_inputs();self.assertEqual(m,{k:v[k] for k in m})
        self.assertEqual(v['expected_original_sprite_renderers'],62815)
        self.assertEqual(v['expected_original_sprite_renderer_counts']['data.unity3d/resources.assets'],61430)
        self.assertEqual(sum(n for f,n in v['expected_original_sprite_renderer_counts'].items() if '/level'in f),1377)

    def test_all_native_sprite_keys_are_unique_and_file_qualified(self):
        rows=list(catalog());self.assertEqual(len({key(r['identity']) for r in rows}),len(rows))
        a=dict(serialized_file='a.assets',path_id=12);b=dict(serialized_file='b.assets',path_id=12)
        self.assertNotEqual(key(a),key(b))

    def test_four_real_renderer_whole_hash_inverse_prototypes(self):
        rows,schemas=prototypes();n=0
        for r in rows:
            q=r['record']
            if q['type']!='SpriteRenderer':continue
            blob=encode(schemas['212'],q['tree']);self.assertEqual(sha(blob),q['raw_object_sha256'])
            value,spans=recovered(blob,schemas['212']);self.assertEqual(value,q['tree']);self.assertEqual(spans['m_Sprite']['size'],12)
            self.assertEqual(spans['m_Sprite']['sha256'],sha(blob[spans['m_Sprite']['offset']:spans['m_Sprite']['offset']+12]));n+=1
        self.assertEqual(n,4)

    def test_two_real_gameobject_native_schema_prototypes(self):
        rows,schemas=prototypes();n=0
        for r in rows:
            q=r['record']
            if q['type']!='GameObject':continue
            blob=encode(schemas['1'],q['tree']);self.assertEqual(sha(blob),q['raw_object_sha256'])
            value,spans=recovered(blob,schemas['1']);self.assertEqual(value,q['tree']);self.assertIn('m_Name',spans);n+=1
        self.assertEqual(n,2)

    def test_no_partial_or_padded_original_extent_is_accepted(self):
        rows,schemas=prototypes();q=next(r['record'] for r in rows if r['record']['type']=='SpriteRenderer');b=encode(schemas['212'],q['tree'])
        with self.assertRaises(ValueError):recovered(b[:-1],schemas['212'])
        with self.assertRaises(ValueError):recovered(b+b'\0'*4,schemas['212'])

    def test_null_sprite_fixture_is_not_assigned_an_arbitrary_default(self):
        rows,schemas=prototypes();q=deepcopy(next(r['record'] for r in rows if r['record']['type']=='SpriteRenderer'));q['tree']['m_Sprite']=dict(m_FileID=0,m_PathID=0)
        b=encode(schemas['212'],q['tree']);v,_=recovered(b,schemas['212']);self.assertEqual(v['m_Sprite'],dict(m_FileID=0,m_PathID=0))

    def test_noncanonical_boolean_is_rejected(self):
        rows,schemas=prototypes();q=next(r['record'] for r in rows if r['record']['type']=='SpriteRenderer');b=bytearray(encode(schemas['212'],q['tree']));b[12]=2
        with self.assertRaises(ValueError):recovered(bytes(b),schemas['212'])


if __name__=='__main__':unittest.main()
