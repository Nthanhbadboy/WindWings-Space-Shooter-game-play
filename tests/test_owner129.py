import gzip,hashlib,json,unittest
from tools.verify import owner129 as m
class Owner129(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a=json.load(gzip.open(m.OUT))
        cls.w={x['pc']:x for x in cls.a['witnesses']}
        cls.vt={x['table_start']:x for x in cls.a['vtable_family']}
    def test_regenerate(self):self.assertEqual(m.build(),self.a)
    def test_claim(self):self.assertEqual(self.a['claim'],6426998422)
    def test_provenance(self):self.assertEqual(self.a['provenance'],'arena/ef6b75ef')
    def test_branch(self):self.assertEqual(self.a['branch'],'arena/ef6b75ef-windwings-space-shooter-game-p')
    def test_tool_pin(self):self.assertEqual(self.a['inputs']['tools/verify/owner129.py'],hashlib.sha256((m.ROOT/'tools/verify/owner129.py').read_bytes()).hexdigest())
    def test_probe_pins(self):
        for p in self.a['probes']:self.assertEqual(p['sha256'],hashlib.sha256((m.ROOT/p['path']).read_bytes()).hexdigest())
        self.assertEqual([p['windows'] for p in self.a['probes']],[8,24,16])
    def test_witnesses(self):
        self.assertEqual(len(self.a['witnesses']),49)
        self.assertTrue(all(len(x['word_hex'])==8 and x['instruction'] for x in self.a['witnesses']))
        for pc in (0x6ceba4,0x6cebb0,0x6bba4c,0x6b8268,0x6cef80,0x6cf80c,0x6cf828,0x6b6c58,0x572a44):
            self.assertIn(pc,self.w)
    def test_single_owner_store(self):
        self.assertEqual(self.a['calibration']['stores_118'],1)
        self.assertEqual(self.w[0x6cef80]['word_hex'],'018c00f9')
    def test_ctor_zero_init(self):
        c=self.a['node_constructor']
        self.assertEqual(c['zero_init'],dict(owner_field=0x118,pair_store_pc=0x6ceba4,pair_word='7fa611a9'))
        self.assertEqual([(v['offset'],v['table'],v['slots']) for v in c['vptrs']],[(0,0x10b0f98,43),(0x110,0x10b1100,4),(0x120,0x10b1130,2)])
    def test_ctor_shape(self):
        c=self.a['node_constructor']
        self.assertEqual((c['entry'],c['fde_end'],c['bytes'],c['instructions']),(0x6ceb88,0x6cec1c,148,37))
        self.assertEqual(c['base_ctor'],0x6d6aa0)
        self.assertEqual(len(c['field_writes']),8)
        self.assertEqual({f['offset'] for f in c['field_writes']},{0x00,0x110,0x118,0x158,0x160,0x1c0,0x1c8,0x3c})
    def test_allocator(self):
        a=self.a['node_allocator']
        self.assertEqual((a['entry'],a['fde_end'],a['instructions']),(0x6bba20,0x6bba90,28))
        self.assertEqual([c['target'] for c in a['calls']],[0x3c986c,0x6ceb88,0x570ff0,0x572a38])
        self.assertEqual((a['size_expression'],a['size_pc'],a['alignment'],a['source_line'],a['source_label_va']),('x2 + 0x1d0',0x6bba34,0x10,0xab,0x12da21))
        self.assertEqual(a['guard']['cleanup'],0x570ff0)
    def test_owner_resolver(self):
        r=self.a['owner_resolver']
        self.assertEqual((r['entry'],r['fde_end'],r['instructions']),(0x6b6c40,0x6b6cc4,33))
        self.assertEqual([c['target'] for c in r['calls']],[0x38cbb4,0x3d8614])
        self.assertEqual((r['id_field'],r['id_load_pc'],r['registry_slot_va']),(0x19c,0x6b6c4c,0x10e18b0))
        self.assertEqual(r['fallback'],0x3d8614)
    def test_dispatch(self):
        d=self.a['dispatch']
        self.assertEqual([x['slot'] for x in d['set_owner']['virtual_slots']],[0xe0,0xd8])
        self.assertEqual([x['slot'] for x in d['rebuild']['virtual_slots']],[0xe0])
        self.assertEqual((d['set_owner']['store_pc'],d['set_owner']['store_word']),(0x6cef80,'018c00f9'))
        self.assertEqual((d['set_owner']['builder'],d['rebuild']['builder']),(0x6cf7b4,0x6cf7b4))
    def test_graph_builder(self):
        g=self.a['graph_builder']
        self.assertEqual((g['entry'],g['fde_end'],g['bytes']),(0x6cf7b4,0x6cff44,1936))
        self.assertEqual([(s['slot'],s['args']) for s in g['owner_slots']],[(0xb0,[]),(0xa8,['w1=1'])])
        self.assertEqual([b['entry'] for b in g['builders']],[0xb98c98,0xb98db4,0xb99120])
        self.assertEqual([b['slot'] for b in g['builders']],[0x130,0x138,0x140])
        self.assertEqual((g['count_field'],g['record_bytes']),('motion+0x10',0x10))
        self.assertEqual((g['child_factory']['entry'],g['child_factory']['arg']),(0x6d25f4,'node+0x20'))
    def test_vtable_sizes(self):
        self.assertEqual({hex(k):v['slot_count'] for k,v in self.vt.items()},
            {'0x10b0f98':43,'0x10b1100':4,'0x10b1130':2,'0x10b0c80':35,'0x10b0f30':11,'0x10b1240':28,'0x10b1420':2,'0x10b1150':28,'0x10b1330':28})
        self.assertEqual(sum(v['slot_count'] for v in self.vt.values()),181)
    def test_called_slot_targets(self):
        self.assertEqual([(x['offset'],x['target']) for x in self.vt[0x10b0f98]['called_slots']],[(0xe0,0x6d017c),(0x138,0x6d137c)])
        self.assertEqual([(x['offset'],x['target']) for x in self.vt[0x10b0c80]['called_slots']],[(0x50,0x3e079c),(0x108,0x6b6ab8)])
        self.assertEqual([(x['offset'],x['target']) for x in self.vt[0x10b0f30]['called_slots']],[(0x28,0x6ce4fc)])
    def test_installers(self):
        self.assertIn(0x6ceb98,{x['pc'] for x in self.vt[0x10b0f98]['installed_at']})
        self.assertIn(0x6d3550,{x['pc'] for x in self.vt[0x10b1240]['installed_at']})
        self.assertIn(0x6ce47c,{x['pc'] for x in self.vt[0x10b0f30]['installed_at']})
    def test_strings(self):
        s={x['va']:x['ascii'] for x in self.a['strings']}
        self.assertEqual(s,{0xc0fce:'%s.Animator',0x101411:'AnimatorOuput',0x12da21:''})
    def test_m1_split(self):
        x=self.a['m1']
        self.assertEqual(x['M1a']['status'],'CLOSED_BYTE_EVIDENCE')
        self.assertEqual(x['M1a']['owner_field']['writer_pc'],0x6cef80)
        self.assertEqual(x['M1a']['value_source']['function'],0x6b6c40)
        self.assertEqual(x['M1b']['status'],'OPEN_RUNTIME_ONLY')
        self.assertIn('no class name is assigned',x['M1b']['not_claimed'])
    def test_m2_contract(self):
        x=self.a['m2'];self.assertEqual(x['status'],'CONTRACT_ONLY_RUNTIME_INPUT_MISSING')
        self.assertEqual(x['allocation']['size'],'count<<4')
        self.assertEqual([b['fde_end'] for b in x['builders']],[0xb98d6c,0xb98fc8,0xb9944c])
    def test_not_run(self):
        n=self.a['not_run'];self.assertEqual(len(n),8);self.assertTrue(all(x['reason'] for x in n))
        self.assertIn(0x6bba20,{x['function'] for x in n});self.assertIn(0x6cef64,{x['function'] for x in n})
    def test_correction(self):
        c=self.a['correction_to_127'];self.assertIn('6ceba4',c);self.assertIn('6cef80',c);self.assertIn('6b6c40',c)
    def test_counts(self):
        self.assertEqual(self.a['counts'],dict(probes=3,witnesses=49,field_writes_ctor=8,vptrs=3,family_tables=9,family_slots=181,called_slots=5,builder_calls=3,not_run=8,region_tables=23))
    def test_check_mode(self):
        b=gzip.compress((json.dumps(self.a,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
        self.assertEqual(b,m.OUT.read_bytes())
