"""Own guarded126 dispatch fixtures; not full graph/runtime proof.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
import gzip
import unittest
from tools.verify import l3_geometry_8141386a_review_ef126 as review
from tools.verify import l3_geometry_8141386a_review_ef126_native as native


class Guarded126Review(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.peer=native.read('peer-artifact126.json.gz')
        cls.rows=review.replay_audit(cls.peer)
        cls.by_case={r['case']:r for r in cls.rows}

    def test_deterministic_separate_artifact(self):
        self.assertEqual(review.OUTPUT.read_bytes(),gzip.compress(review.canonical(review.build())+b'\n',mtime=0))

    def test_four_exact_native_counts_and_all_original_pc_sets(self):
        self.assertEqual([r['native_instruction_count']for r in self.rows],[70,8,8,66])
        for r,p in zip(self.rows,self.peer['cases']):
            self.assertEqual(r['executed_addresses'],p['run']['executed_addresses'])
            self.assertEqual(r['node_after'],p['node_after'])
            self.assertEqual(r['graph_builder_sinks'],p['graph_builder_calls'])

    def test_three_graph_and_four_virtual_sinks_not_native_instructions(self):
        self.assertEqual(sum(r['native_instruction_count']for r in self.rows),152)
        self.assertEqual(sum(len(r['graph_builder_sinks'])for r in self.rows),3)
        self.assertEqual(sum(len(r['virtual_services'])for r in self.rows),4)
        for r in self.rows:
            forbidden={native.TARGET,r['addresses']['e0'],r['addresses']['d8'],r['addresses']['stop'],0x57112c}
            self.assertFalse(forbidden.intersection(r['executed_addresses']))
            self.assertFalse(r['import_services_called'])

    def test_rebuild_last_native_pc_is_br_not_ret(self):
        r=self.by_case['rebuild']
        self.assertEqual(r['last_native_pc'],0x6ceff8)
        self.assertEqual(r['termination_kind'],'INDIRECT_TAIL_BRANCH_TO_SYNTHETIC_E0')
        self.assertEqual(r['virtual_services'][0]['pc'],0x6ceff8)
        self.assertNotIn(0x571128,r['executed_addresses'])
        self.assertEqual(r['return_value'],0)  # synthetic service result, not a native virtual body.

    def test_full_native_writes_are_slot118_byte102_flags38_only(self):
        r=self.by_case['set_full'];c=r['addresses']['controller'];owner=r['addresses']['owner']
        ws=[(w['pc'],w['address']-c,w['size'],w['value'])for w in r['native_memory_writes']if c<=w['address']<c+0x200]
        self.assertEqual(ws,[(0x6cef80,0x118,8,owner),(0x6d6c08,0x102,1,1),(0x571114,0x38,4,0)])
        self.assertEqual(r['last_native_pc'],0x571128)

    def test_equal_case_has_no_builder_virtual_or_node_write(self):
        r=self.by_case['set_equal'];c=r['addresses']['controller']
        self.assertEqual(r['last_native_pc'],0x6cefc0)
        self.assertFalse(r['graph_builder_sinks']);self.assertFalse(r['virtual_services'])
        self.assertFalse([w for w in r['native_memory_writes']if c<=w['address']<c+0x200])
        self.assertEqual(r['node_after']['slot118'],r['addresses']['owner'])

    def test_null_owner_skips_d8_but_keeps_original_helper_and_tail(self):
        r=self.by_case['set_null']
        self.assertEqual(len(r['virtual_services']),1)
        self.assertNotIn(0x6cefb0,r['executed_addresses'])
        self.assertEqual(r['pc_counts']['0x6cf768'],2)
        self.assertIn(0x6d6bf8,r['executed_addresses']);self.assertIn(0x5710ec,r['executed_addresses'])
        self.assertEqual(r['node_after']['slot118'],0)

    def test_n2_identity_is_read_by_python_d8_not_by_original_native_code(self):
        self.assertEqual(sum(len(r['synthetic_d8_identity_observations'])for r in self.rows),1)
        ids=self.by_case['set_full']['synthetic_d8_identity_observations'][0]
        self.assertEqual(ids['origin'],'PYTHON_SYNTHETIC_D8_SERVICE_ONLY')
        self.assertEqual((ids['controller_path'],ids['component_path'],ids['gameobject_path'],ids['root_gameobject']),(1856,493584,76852,73241))
        for r in self.rows:
            owner=r['addresses']['owner']
            self.assertFalse([x for x in r['native_memory_reads']if owner+8<=x['address']<owner+0x70])

    def test_unchanged_103_and_a8_are_prepared_zero_not_native_clears(self):
        for r in self.rows:
            c=r['addresses']['controller']
            self.assertEqual((r['node_after']['byte103'],r['node_after']['halfword_a8']),(0,0))
            self.assertFalse([w for w in r['native_memory_writes']if w['address']in(c+0x103,c+0xa8)])

    def test_original_stack_restoration_and_explicit_stop(self):
        for r in self.rows:
            self.assertEqual(r['stack_pointer_after'],r['base']+0x1f000)
            self.assertEqual(r['stop_pc'],r['addresses']['stop'])
            self.assertNotIn(r['stop_pc'],r['executed_addresses'])

    def test_relocated_prepared_base_keeps_bounded_native_shape(self):
        r=native.replay('set_full',base=0x4000000);old=self.by_case['set_full']
        self.assertEqual(r['native_instruction_count'],70)
        self.assertEqual(r['pc_counts'],old['pc_counts'])
        self.assertEqual(r['node_after']['slot118']-r['base'],old['node_after']['slot118']-old['base'])

    def test_missing_instruction_is_not_authorized_by_mapped_zero_page(self):
        with self.assertRaisesRegex(ValueError,'uncaptured original instruction'):
            native.replay('set_full',drop_instruction=0x6cef64)

    def test_unprepared_native_data_and_disabled_builder_sink_are_rejected(self):
        with self.assertRaisesRegex(ValueError,'uncaptured/unprepared native data'):
            native.replay('set_full',fault_unprepared_chunk=True)
        with self.assertRaisesRegex(ValueError,'graph-builder body prohibited'):
            native.replay('set_full',graph_sink=False)

    def test_unknown_case_or_unapproved_base_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'bounded caller inputs'):native.replay('runtime_game')
        with self.assertRaisesRegex(ValueError,'bounded caller inputs'):native.replay('set_full',base=0x7000000)


if __name__=='__main__':unittest.main()
