"""Independent124 addendum static/fixture/boundary regression checks.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
import gzip
import json
import unittest
from tools.verify.geometry_8141386a_atlas_io import ROOT,sha
from tools.verify.l3_geometry_8141386a_review_ef124 import build,read,audit_static,audit_replays,precision_notes,OUTPUT


class R1AddendumReview(unittest.TestCase):
    def test_complete_artifact_reproduction_and_fixed_scope(self):
        v=build();self.assertEqual(v,json.loads(gzip.decompress(OUTPUT.read_bytes())))
        self.assertEqual(v['target']['scientific_commit'],'98e5ba9666103ca354ce3fd6116ca295b497c30d')
        self.assertIn('NOT_27_FULL',v['verdict']);self.assertIn('Newer ef126',v['limits'][-1])

    def test_original_fresh_recovery_is_actual_green_not_review_ci(self):
        c=read('source-ci-receipt.json.gz');self.assertEqual(c['run']['id'],40386262470)
        self.assertEqual(c['run']['conclusion'],'success');self.assertEqual(c['peer_verify_run']['head_sha'],'98e5ba9666103ca354ce3fd6116ca295b497c30d')
        self.assertTrue(all(j['conclusion']=='success' for j in c['jobs']['jobs']))
        self.assertIn('Not own final',c['scope'])

    def test_149_spans_132_fdes_four_groups_64_relative_slots(self):
        v=build()['static_audit'];self.assertEqual((v['matched_unique_spans'],v['matched_fdes']),(149,132))
        self.assertEqual(sum(len(g['original_relas']) for g in v['vtable_groups']),64)
        self.assertEqual(v['relative_rela_total'],29267)

    def test_altered_fresh_span_is_rejected(self):
        f=read('fresh-original.json.gz');f['peer_span_matches'][0]['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'span coverage/hash'):audit_static(read('peer-nodefactories124-probe.json.gz'),read('peer-nodefactories124-artifact.json.gz'),f)

    def test_fde_end_is_exclusive_and_alteration_is_rejected(self):
        v=build()['static_audit']
        for r in v['factories']:self.assertEqual(r['ret']+4,r['fde']['end_exclusive']);self.assertEqual(r['constructor_ret']+4,r['constructor_fde']['end_exclusive'])
        f=read('fresh-original.json.gz');f['selected_fdes'][0]['end_exclusive']-=4
        with self.assertRaisesRegex(ValueError,'FDE/table'):audit_static(read('peer-nodefactories124-probe.json.gz'),read('peer-nodefactories124-artifact.json.gz'),f)

    def test_nonrelative_vtable_slot_is_rejected(self):
        f=read('fresh-original.json.gz');s=f['vtable_groups'][0]['slots'][0];b=bytearray.fromhex(s['hex']);b[8]=0;s['hex']=b.hex()
        with self.assertRaisesRegex(ValueError,'relative vtable'):audit_static(read('peer-nodefactories124-probe.json.gz'),read('peer-nodefactories124-artifact.json.gz'),f)

    def test_graph_bl_mismatch_is_rejected(self):
        p=read('peer-nodefactories124-artifact.json.gz');p['graph_builder_callsites'][0]['pc']+=4
        with self.assertRaisesRegex(ValueError,'graph BLs'):audit_static(read('peer-nodefactories124-probe.json.gz'),p,read('fresh-original.json.gz'))

    def test_prepared_allocator_request_mismatch_is_rejected(self):
        p=read('peer-nodefactories124-artifact.json.gz');p['standalone'][0]['allocator_records'][0]['size']+=16
        with self.assertRaisesRegex(ValueError,'allocator exact request'):audit_replays(p)

    def test_pc_effects_and_shared_counts_are_not_additive_or_fresh_extraction(self):
        v=build();self.assertEqual(v['counts']['own_instruction_counts'],[181,200,196,171,181,171])
        self.assertEqual([r['owner']['count'] for r in v['own_native_fixture_replays']],[42]*6)
        self.assertTrue(all(r['native_writes'] for r in v['own_native_fixture_replays']))
        s=v['shared_source_check'];self.assertEqual((s['calls'],s['dwords']),(10,930))
        self.assertEqual(s['post_factory_bound_offsets'],[0x118,0x128,0x130,0x1d0]);self.assertIn('not fresh',s['evidence'])

    def test_additive_118_wording_does_not_rewrite_frozen_data(self):
        n=precision_notes();self.assertIn('ADDITIVE',n['kind']);self.assertEqual(n['review_source_comment'],6424830494)
        self.assertEqual(sha((ROOT/'datas/l3_geometry_sprite_consumers_8141386a.json.gz').read_bytes()),'c33ad8a80c35990cf5dd94165234878a62785a5bb39ddef5f2bb73752408019d')
        d={r['id']:r for r in n['corrections']};self.assertEqual(d['D3']['negative_rows_with_atlas_membership'],115)
        self.assertIn('class_id/type-table',d['D2']['wording']);self.assertIn('252fresh',d['D1']['wording'])


if __name__=='__main__':unittest.main()
