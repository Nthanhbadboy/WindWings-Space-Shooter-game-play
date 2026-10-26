import gzip,hashlib,json,unittest
from tools.verify import bootstrap126 as b
class Bootstrap126(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.a=json.load(gzip.open(b.OUT))
    def test_regenerate(self):self.assertEqual(b.build(),self.a)
    def test_claim(self):self.assertEqual(self.a['claim'],6425017706)
    def test_tool_pin(self):self.assertEqual(self.a['inputs']['tools/verify/bootstrap126.py'],hashlib.sha256((b.ROOT/'tools/verify/bootstrap126.py').read_bytes()).hexdigest())
    def test_target_and_refs(self):
        x=self.a;self.assertEqual(x['target'],0x6cf7b4);self.assertEqual(len(x['direct_refs']),2);self.assertEqual([y['pc'] for y in x['direct_refs']],[0x6cef84,0x6cefe4]);self.assertEqual(x['rela_matches'],[])
    def test_fde_extents(self):
        f=self.a['fde'];self.assertEqual(f['0x6cf7b4'],0x6cff44);self.assertEqual(f['0x6cef64'],0x6cefdc);self.assertEqual(f['0x6cefdc'],0x6ceffc)
    def test_n2_owner(self):
        x=self.a['n2_owner'];self.assertEqual(x['controller']['path_id'],1856);self.assertEqual(x['controller']['name'],'Body 1');self.assertEqual(x['animator_component']['component_path_id'],493584);self.assertEqual(x['animator_component']['gameobject_ref']['m_PathID'],76852);self.assertEqual(x['hierarchy']['root_gameobject_name'],'Boss-37004')
    def test_n2_unresolved(self):
        x=self.a['n2_source']['unresolved_edges'];self.assertFalse(x['graph_builder_range_to_controller_1856_instance']);self.assertFalse(x['runtime_graph_construction_or_playback_observed'])
    def test_n2_source_pins(self):
        x=self.a['n2_source'];self.assertEqual(len(x['artifact_sha256']),64);self.assertEqual(len(x['report_sha256']),64)
    def test_case_count(self):self.assertEqual(self.a['counts']['cases'],4)
    def test_graph_builder_sink_counts(self):self.assertEqual(self.a['counts']['graph_builder_sink_calls'],3)
    def test_virtual_service_counts(self):self.assertEqual(self.a['counts']['virtual_service_calls'],4)
    def test_full_case(self):
        c=self.a['cases'][0];self.assertEqual(c['entry'],0x6cef64);self.assertEqual(len(c['graph_builder_calls']),1);self.assertEqual(len(c['virtual_calls']),2);self.assertEqual(c['virtual_calls'][0]['kind'],'rebuild_notify');self.assertEqual(c['virtual_calls'][1]['kind'],'owner_release')
        self.assertEqual(c['virtual_calls'][1]['controller_path'],1856);self.assertEqual(c['virtual_calls'][1]['component_path'],493584);self.assertEqual(c['virtual_calls'][1]['gameobject_path'],76852)
    def test_full_native_pcs(self):
        h=self.a['cases'][0]['pc_hits'];self.assertIn('0x6d6bf8',h);self.assertIn('0x6cf768',h);self.assertIn('0x5710ec',h);self.assertIn('0x571128',h);self.assertNotIn('0x6cf7b4',h);self.assertNotIn('0x57112c',h)
    def test_full_node_after(self):
        n=self.a['cases'][0]['node_after'];self.assertEqual((n['byte102'],n['byte103']),(1,0));self.assertEqual(n['flags38'],0);self.assertEqual(n['halfword_a8'],0)
    def test_early_return(self):
        c=self.a['cases'][1];self.assertEqual(c['ret'],0x6cefc0);self.assertEqual(c['graph_builder_calls'],[]);self.assertEqual(c['virtual_calls'],[])
    def test_rebuild_wrapper(self):
        c=self.a['cases'][2];self.assertEqual(c['entry'],0x6cefdc);self.assertEqual(len(c['graph_builder_calls']),1);self.assertEqual(len(c['virtual_calls']),1);self.assertEqual(c['virtual_calls'][0]['kind'],'rebuild_notify_tail');self.assertIn('0x6ceff8',c['pc_hits']);self.assertNotIn('0x5710ec',c['pc_hits'])
    def test_null_owner(self):
        c=self.a['cases'][3];self.assertEqual(len(c['graph_builder_calls']),1);self.assertEqual(len(c['virtual_calls']),1);self.assertEqual(c['node_after']['slot118'],0);self.assertEqual(c['node_after']['byte102'],1)
    def test_no_service_or_failure(self):
        for c in self.a['cases']:self.assertEqual(c['service_calls'],[]);self.assertEqual(c['failure_calls'],[])
    def test_counts_partition(self):
        c=self.a['counts'];self.assertEqual((c['direct_refs'],c['rela_matches'],c['cases']),(2,0,4));self.assertEqual(len(c['native_instructions']),4)
    def test_relocation(self):
        f=b.Fixture(b.fixture_raw(b.merged()),0x4000000);p=b.prepare(f,base=0x4000000);r=b.run_case(f,p,entry=b.REBUILD_ENTRY);self.assertEqual(r['entry'],0x6cefdc);self.assertEqual(len(r['graph_builder_calls']),1)
    def test_scope_not_runtime(self):
        s=self.a['scope'];self.assertIn('NOT full graph-builder execution',s);self.assertIn('no selfACK/full#27closure',s)
