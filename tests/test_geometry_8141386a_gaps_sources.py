"""#8 streamed source scope and opaque native-header boundaries.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
import struct
import unittest
from tools.verify.geometry_8141386a_gaps_sources import load,select
from tools.verify.l3_geometry_8141386a_gaps_header import header
from tools.verify.geometry_8141386a_atlas_io import sha


def fixture(name='',tail=b''):
    name=name.encode();b=struct.pack('<iqB3xiqi',0,42,1,1,280,len(name))+name
    return b+b'\0'*(-len(b)%4)+tail


class GapsSources(unittest.TestCase):
    def test_streamed_report98_reproduction(self):self.assertEqual(select(),load())

    def test_five_headers_are_three_explicit_class_groups(self):
        v=load();self.assertEqual(v['summary']['header_only'],5)
        self.assertEqual(v['summary']['header_class_counts'],{'GunEventCatcher':1,'Player_Attack_2':3,'Boss19_AttackTypes':1})
        self.assertEqual(len(v['header_records']),5)
        self.assertTrue(all(r['capture_exception'] for r in v['header_records']))

    def test_52_default_references_are_not_52_unique_meshes(self):
        s=load()['summary'];self.assertEqual(s['default_mesh_refs'],52)
        self.assertEqual(s['mesh_owner_types'],{'ParticleSystemRenderer':51,'MeshFilter':1})
        self.assertEqual(s['target_path_id_histogram'],{'10210':46,'10202':5,'10209':1})

    def test_distinct_closures_are_measured_not_forced_to_be_nested(self):
        s=load()['summary'];self.assertEqual(s['overlap_closed7'],2)
        self.assertEqual(s['closed7_outside_report98'],5);self.assertEqual(s['additional_refs_beyond7'],50)
        self.assertEqual(s['captured_objects'],128724);self.assertEqual(s['captured_links'],511781)

    def test_raw_unresolved_link_and_actual_owner_field_agree(self):
        for r in load()['mesh_references']:
            e=r['reference'];self.assertEqual(e['external_path'],'Library/unity default resources')
            self.assertEqual(e['record']['status'],'unresolved');self.assertEqual(e['record']['location'],'.m_Mesh')
            self.assertEqual(r['record']['tree']['m_Mesh'],e['record']['pointer'])
            self.assertEqual(e['record']['pointer']['m_FileID'],2)

    def test_csharp_declarations_are_consulted_not_serialized_memory_offsets(self):
        v=load();names={r['class_name'] for r in v['csharp_declarations']}
        self.assertTrue({'GunEventCatcher','Player_Attack','Player_Attack_2','Boss_AttackTypes','Boss19_AttackTypes',
                         'UnityEventBase','PersistentCall','PersistentCallGroup','ArgumentCache'}<=names)
        g=next(r for r in v['csharp_declarations'] if r['class_name']=='GunEventCatcher')
        self.assertIn('UnityEvent<Vector3> onDestroy',g['text']);self.assertEqual(g['text_sha256'],sha(g['text'].encode()))

    def test_native_header_is_exact_but_nonempty_custom_tail_stays_opaque(self):
        tail=b'\x01\x02\x03\x04';r=header(fixture(tail=tail))
        self.assertEqual(r['header_end'],32);self.assertEqual(r['tail_size'],4);self.assertEqual(r['tail_sha256'],sha(tail))
        self.assertIsNone(r['custom_fields']);self.assertEqual(r['fields']['m_Script'],{'m_FileID':1,'m_PathID':280})

    def test_header_name_alignment_is_not_a_guessed_custom_field(self):
        r=header(fixture('X',b'1234'));self.assertEqual(r['header_end'],36);self.assertEqual(r['fields']['m_Name'],'X')
        self.assertEqual(r['tail_size'],4)

    def test_empty_tail_does_not_claim_no_runtime_state(self):
        r=header(fixture());self.assertEqual(r['tail_size'],0);self.assertIsNone(r['custom_fields'])
        self.assertIn('gameplay state',r['scope'])

    def test_truncated_invalid_boolean_padding_and_name_fail_closed(self):
        with self.assertRaises(ValueError):header(b'\0'*31)
        for offset in (12,13):
            b=bytearray(fixture());b[offset]=2
            with self.assertRaises(ValueError):header(bytes(b))
        b=bytearray(fixture());struct.pack_into('<i',b,28,-1)
        with self.assertRaises(ValueError):header(bytes(b))
        b=bytearray(fixture());struct.pack_into('<i',b,28,500)
        with self.assertRaises(ValueError):header(bytes(b))


if __name__=='__main__':unittest.main()
