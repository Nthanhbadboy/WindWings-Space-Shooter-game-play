import gzip,hashlib,json,unittest
from tools.verify import motion128 as m
class Motion128(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.a=json.load(gzip.open(m.OUT))
    def test_regenerate(self):self.assertEqual(m.build(),self.a)
    def test_claim(self):self.assertEqual(self.a['claim'],6426286596)
    def test_provenance(self):self.assertEqual(self.a['provenance'],'arena/ef6b75ef')
    def test_tool_pin(self):self.assertEqual(self.a['inputs']['tools/verify/motion128.py'],hashlib.sha256((m.ROOT/'tools/verify/motion128.py').read_bytes()).hexdigest())
    def test_no_new_recovery(self):
        x=self.a['fde_recovery'];self.assertEqual((x['run'],x['source']),(40391655099,'b0a585e5e'));self.assertEqual(x['raw_sha256'],m.RAW_SHA)
    def test_capture_counts(self):self.assertEqual(self.a['captured'],dict(windows=44,unique_windows=42,followed_entries=39,original_fde_entries=37,bounded_windows=2))
    def test_builder_extents(self):
        b={x['entry']:x for x in self.a['builders']}
        self.assertEqual((b[0xb98c98]['fde_end'],b[0xb98c98]['ret'],b[0xb98c98]['instructions']),(0xb98d6c,0xb98d68,53))
        self.assertEqual((b[0xb98db4]['fde_end'],b[0xb98db4]['instructions']),(0xb98fc8,133))
        self.assertEqual((b[0xb99120]['fde_end'],b[0xb99120]['instructions']),(0xb9944c,203))
        self.assertEqual((b[0x6cff44]['fde_end'],b[0x6cff44]['instructions']),(0x6d006c,74))
    def test_motion_base_is_read_only(self):
        b={x['entry']:x for x in self.a['builders']}
        self.assertNotIn('x21',b[0xb98c98]['store_bases']);self.assertNotIn('x21',b[0xb98db4]['store_bases'])
        self.assertNotIn('x21',b[0xb99120]['store_bases']);self.assertNotIn('x22',b[0x6cff44]['store_bases'])
    def test_witnesses(self):
        w=self.a['witnesses'];self.assertEqual(len(w),61);self.assertTrue(all(len(x['word_hex'])==8 and x['instruction'] for x in w))
        pcs={x['pc'] for x in w};self.assertIn(0x6cf814,pcs);self.assertIn(0xb98e98,pcs);self.assertIn(0xb993ac,pcs);self.assertIn(0x6ef95c,pcs)
    def test_motion_header(self):
        h={x['offset']:x for x in self.a['motion_header']}
        self.assertEqual(sorted(h),['0x00','0x08','0x10','0x18','0x20','0x28'])
        self.assertEqual([h[k]['width'] for k in ['0x00','0x08','0x10','0x18','0x20','0x28']],[4,8,4,8,8,8])
    def test_records(self):
        self.assertEqual(len(self.a['child_record']),7);self.assertEqual(len(self.a['secondary_record']),3)
        self.assertEqual(sum(1 for x in self.a['allocations'] if x['builder']=='0xb99120'),4)
    def test_clips(self):
        c=self.a['clips'];self.assertEqual([x['path_id'] for x in c],m.CLIP_IDS)
        self.assertEqual([x['bindings'] for x in c],[8,8,13,17,88,93,89,86])
        self.assertEqual([x['pptr_curve_mapping'] for x in c],[0]*8)
        self.assertTrue(all(x['binding_coverage_exact'] and x['channel_count']==x['binding_channel_count'] for x in c))
    def test_totals(self):
        t=self.a['clip_totals'];self.assertEqual((t['clips'],t['bindings'],t['pptr_curve_mappings'],t['streamed_frames'],t['constant_values'],t['channel_count'],t['events']),(8,402,0,142,177,654,4))
    def test_controller_tree(self):
        c=self.a['controller_1856'];self.assertEqual((c['layers'],c['state_constants'],c['blend_tree_constants'],c['blend_nodes'],c['total_child_indices'],c['controller_size']),(1,8,8,8,0,4110))
        self.assertFalse(c['has_clip_binding_constant']);self.assertEqual(c['clip_ids'],[7,1,2,3,4,5,6,0])
    def test_negative_artifacts(self):
        n=self.a['negative_artifacts'];g=n['controller_graphs'];l=n['enemy_clip_links']
        self.assertEqual((g['sha256'],g['controllers'],g['has_clip_binding_constant']),('72b9cfad8bb7f9e2f0e390ecc6ea680ed2ad6198dd8ad3c83d152f7b76860ae7',52,False))
        self.assertEqual((l['sha256'],l['animators'],l['muscle_bytes'],l['curves_decoded_false']),('fe001faf73dc727974156cdcc37d60b1a59463c00b867f7ded35b0ed2a2576b4',154,72300,8))
    def test_m2_split(self):
        m2={x['id']:x for x in self.a['m2']}
        self.assertEqual(sorted(m2),['M2a','M2b','M2c'])
        self.assertEqual((m2['M2a']['status'],m2['M2b']['status'],m2['M2c']['status']),('AVAILABLE_SERIALIZED_CONTENT','MISSING_RUNTIME_OBJECT','MISSING_PRODUCER'))
    def test_correction_to_127(self):
        s=self.a['correction_to_127'];self.assertIn('too broad',s);self.assertIn('M2a',s);self.assertIn('unchanged',s)
    def test_not_run_covers_builders(self):
        f={x['fde'] for x in self.a['not_run']}
        for k in ('0xb98c98','0xb98db4','0xb99120','0x6cff44','0x6f15cc'):self.assertIn(k,f)
    def test_scope_static_only(self):
        s=self.a['scope'];self.assertIn('No FDE is executed',s);self.assertIn('fabricating',s)
    def test_delivery_contract(self):
        d=self.a['delivery_contract']
        self.assertEqual((d['node_field'],d['chunk_field'],d['virtual_slot'],d['loop_bound']),('0x30','0x20','0x18','motion+0x00'))
        self.assertEqual(d['witness_pcs'],[0x6cff88,0x6cff8c,0x6cff90,0x6cfff0,0x6cfffc,0x6d000c,0x6d0038])
        self.assertTrue(d['status'].startswith('MISSING_TARGET_IDENTITY'))
    def test_inputs_pinned(self):
        self.assertEqual(self.a['inputs']['reverse-engineering/raw/graph127/probe.json.gz'],m.RAW_SHA)
        self.assertEqual(self.a['inputs']['reverse-engineering/raw/l3-ef6b75ef128-verification/claim.json'],hashlib.sha256((m.VER/'claim.json').read_bytes()).hexdigest())
    def test_counts(self):
        c=self.a['counts'];self.assertEqual((c['builders'],c['witnesses'],c['clips'],c['pinned_bindings'],c['m2_items']),(4,61,8,402,3))
