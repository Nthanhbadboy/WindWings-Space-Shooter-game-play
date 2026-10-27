"""R1 fresh original static evidence and corrected-boundary regression checks.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
import gzip
import json
import struct
import unittest
from tools.verify.geometry_8141386a_atlas_io import sha
from tools.verify.geometry_8141386a_review_ef123_checks import candidate_sets,decode_usage,decode_rela
from tools.verify.l3_geometry_8141386a_review_ef123 import build,OUTPUT,RAW,read


class R1Review(unittest.TestCase):
    def test_complete_review_artifact_reproduction(self):
        self.assertEqual(build(),json.loads(gzip.decompress(OUTPUT.read_bytes())))

    def test_fresh_global_rela_negative_not_only_152_selected(self):
        v=build();s=v['fresh_original_scope']
        self.assertEqual(s['rela_total'],29626);self.assertEqual(s['relative_rela_total'],29267)
        self.assertEqual(s['global_graph_relative_matches'],0);self.assertEqual(s['global_graph_direct_matches'],2)

    def test_all_unique_peer_windows_and_fde_bytes_corroborated(self):
        f=read('fresh-original.json.gz');r=read('peer-vtable123-probe.json.gz');original={(x['va'],len(x['hex'])//2):sha(bytes.fromhex(x['hex'])) for x in r['windows']}
        self.assertEqual(len(original),106);self.assertEqual(len(f['unity']['peer_window_matches']),106)
        for x in f['unity']['peer_window_matches']:self.assertEqual(original[x['va'],x['size']],x['sha256'])
        self.assertEqual(len(f['unity']['selected_fdes']),104)

    def test_fde_exclusive_end_is_not_final_ret_address(self):
        rows=read('fresh-original.json.gz')['unity']['selected_fdes'];d={x['start']:x for x in rows}
        for start,end in ((0x6d2894,0x6d28fc),(0x6d26d4,0x6d2744),(0x6d2950,0x6d29e4),(0x571a80,0x571aac),(0x6d5134,0x6d51a4)):
            self.assertEqual(d[start]['end_exclusive'],end)
            delta,size=struct.unpack_from('<iI',bytes.fromhex(d[start]['fde_hex']),8);self.assertEqual(d[start]['fde_va']+8+delta,start);self.assertEqual(start+size,end)

    def test_exact_token_to_metadata_payload_not_direct_string_pointer(self):
        m=read('fresh-original.json.gz')['marker'];self.assertEqual(m['target_cell']['hex'],'a73c00a000000000');self.assertEqual(m['encoded_usage'],0xa0003ca7)
        self.assertEqual(m['kind'],5);self.assertEqual(m['index'],7763);self.assertEqual(m['metadata_version'],31)
        self.assertEqual(m['definition_hex'],'040000009b3a0300');self.assertEqual(m['payload_file_offset'],332323);self.assertEqual(m['payload_hex'],'53746f70');self.assertEqual(m['utf8'],'Stop')
        self.assertNotEqual(m['target_cell']['hex'],m['payload_hex'])

    def test_original_marker_relative_relocation_type_and_symbol(self):
        r=decode_rela(read('fresh-original.json.gz')['marker']['rela']['hex']);self.assertEqual(r['type'],1027);self.assertEqual(r['symbol'],0)
        self.assertEqual(r['address'],0x2adfb48);self.assertEqual(r['addend'],0x2be5cb8)

    def test_altering_predicate_does_not_produce_a_valid_narrowing(self):
        v=candidate_sets(read('fresh-original.json.gz')['unity']['vtable_window_relas']);self.assertEqual(set(v['naive'])&set(v['exact_reserve_notify']),set())
        self.assertFalse(set(v['exact_reserve_notify'])<=set(v['naive']))

    def test_usage_decoder_rejects_other_formats(self):
        with self.assertRaises(ValueError):decode_usage('53746f70')
        with self.assertRaises(ValueError):decode_usage('0000000000000000')
        with self.assertRaises(ValueError):decode_usage('a73c00a001000000')

    def test_producer_ack_and_corrected_report_are_not_self_ack(self):
        v=build();self.assertEqual(v['counts']['description_findings_corrected'],2)
        self.assertTrue(all(r['status']=='CORRECTED_BY_PRODUCER' for r in v['findings'][:2]));self.assertEqual(v['target']['producer_correction_commit'],'ea6a3835f786306b07df9658262a6e3f6658f809')
        self.assertIn('NOT_27_FULL',v['verdict'])

    def test_pc_count_scope_shared_dwords_not_own_parent_reexecution(self):
        v=build();self.assertEqual(v['counts']['own_instruction_counts'],[34,457,1281,1281]);self.assertEqual(v['shared_source_check']['dwords'],930)
        self.assertIn('not fresh',v['shared_source_check']['evidence']);self.assertEqual(v['own_native_fixture_replays'][0]['manager']['byte100'],165)


if __name__=='__main__':unittest.main()
