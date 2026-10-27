"""R1 addendum120 source/fixture checks, no producer verifier imports.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
from pathlib import Path
from collections import Counter
import gzip
import json
import unittest
from tools.verify.geometry_8141386a_atlas_io import ROOT,sha,iter_arrays
from tools.verify.geometry_8141386a_review_ef123_checks import branch,constant_stores,add_imm
from tools.verify.l3_geometry_8141386a_review_ef124_native import RAW,FACTORIES,replay


def raw():return json.loads(gzip.decompress((RAW/'peer-nodefactories124-probe.json.gz').read_bytes()))
def artifact():return json.loads(gzip.decompress((RAW/'peer-nodefactories124-artifact.json.gz').read_bytes()))


class R1AddendumSources(unittest.TestCase):
    def test_pinned_peer_source_snapshots(self):
        p=json.loads((RAW/'peer-pins.json').read_bytes())
        for r in p['pins']:
            b=(ROOT/r['snapshot']).read_bytes();self.assertEqual(sha(b),r['sha256'])
            self.assertEqual(sha(gzip.decompress(b)) if r['encoding']=='gzip' else sha(b),r['source_sha256'])

    def test_seven_graph_builder_callsites_recomputed(self):
        r=raw();w=next(w for w in r['windows'] if w['va']==0x6cf7b4);b=bytes.fromhex(w['hex']);hits=[]
        for i in range(0,len(b),4):
            p=branch(int.from_bytes(b[i:i+4],'little'),w['va']+i)
            if p and p['link'] and p['target']in FACTORIES:hits.append((p['pc'],p['target']))
        self.assertEqual(Counter(t for _,t in hits),{0x6d25f4:1,0x6d2664:1,0x6d26d4:2,0x6d2744:3})
        self.assertEqual(hits,[(x['pc'],x['target'])for x in artifact()['graph_builder_callsites']])

    def test_constructor_constant_stores_and_vptrs(self):
        r=raw()
        for ctor,vptr,_,_ in FACTORIES.values():
            w=next(w for w in r['windows'] if w['va']==ctor);stores=constant_stores(bytes.fromhex(w['hex']),ctor)
            self.assertTrue(any(s['value']==vptr and s['base_register']==19 and s['offset']==0 for s in stores))

    def test_four_factory_allocator_offsets_from_instructions(self):
        r=raw()
        for entry,(_,_,offset,_)in FACTORIES.items():
            w=next(w for w in r['windows'] if w['va']==entry);b=bytes.fromhex(w['hex']);adds=[add_imm(int.from_bytes(b[i:i+4],'little'))for i in range(0,len(b),4)]
            self.assertIn((0,2,offset),adds)

    def test_four_default_factory_native_replay_counts_and_state(self):
        for entry,expected in zip(FACTORIES,(181,200,196,171)):
            r=replay(entry);self.assertEqual(r['instruction_count'],expected);self.assertEqual(r['node']['vptr'],FACTORIES[entry][1]);self.assertEqual(r['pool']['acquired'],1);self.assertEqual(r['owner']['count'],42)
            self.assertEqual(r['node']['halfword_a8'],0);self.assertEqual(r['node']['flags38']&1,1)

    def test_extra_label_tag_variant_has_exact_allocator_request(self):
        r=replay(0x6d25f4,prefill=0,label=7,extra=0x40,tag=41)
        self.assertEqual(r['instruction_count'],181);self.assertEqual(r['allocator_calls'][0]['args'],[0x1b8,16,94,0,0x12da21,0xab]);self.assertEqual(r['node']['label'],7);self.assertEqual(r['pool']['tag'],42)

    def test_relocated_base_variant_keeps_count_not_pointer_identity(self):
        a=replay(0x6d2744);b=replay(0x6d2744,base=0x4000000)
        self.assertEqual((a['instruction_count'],b['instruction_count']),(171,171));self.assertNotEqual(a['node']['address'],b['node']['address']);self.assertEqual(a['node']['vptr'],b['node']['vptr'])

    def test_natural_cleanup_branch_no_service_or_error_execution(self):
        r=replay(0x6d2664)
        for pc in (0x570ff0,0x109ace0,0x109acc0,0x573a1c,0x575b34):self.assertNotIn(hex(pc),r['pc_counts'])
        self.assertIn('0x57054c',r['pc_counts']);self.assertIn('0x572a38',r['pc_counts']);self.assertEqual(r['node']['byte16c'],0)

    def test_specific_constructor_fields_not_fabricated_empty_defaults(self):
        a=replay(0x6d25f4);c=replay(0x6d26d4);d=replay(0x6d2744)
        self.assertEqual((a['node']['word118'],a['node']['byte170']),(0x4b,1));self.assertEqual((c['node']['word16c'],c['node']['qword178']),(0x3f800000,0));self.assertEqual(d['node']['word118'],0)

    def test_118_precision_notes_are_additive_with_correct_counts(self):
        v=json.loads((RAW/'producer-118-precision.json').read_bytes());self.assertIn('ADDITIVE',v['kind'])
        d={x['id']:x for x in v['corrections']};self.assertEqual(d['D3']['negative_rows'],288);self.assertEqual(d['D3']['negative_rows_with_atlas_membership'],115)
        self.assertEqual(d['D1']['measured_inherited_pin_groups']['reverse-engineering/raw/l3-chain/'],901)
        self.assertEqual(d['D1']['measured_inherited_pin_groups']['reverse-engineering/raw/l3-visual-surface/'],411)


if __name__=='__main__':unittest.main()
