"""R1 independent retained-byte checks and own native fixture replay.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
from pathlib import Path
import gzip
import hashlib
import json
import unittest
from tools.verify.geometry_8141386a_review_ef123_checks import candidate_sets,constant_stores,branch,decode_rela,decode_usage
from tools.verify.l3_geometry_8141386a_review_ef123_native import RAW,replay


def raw():return json.loads(gzip.decompress((RAW/'peer-vtable123-probe.json.gz').read_bytes()))
def artifact():return json.loads(gzip.decompress((RAW/'peer-vtable123-artifact.json.gz').read_bytes()))


class R1Sources(unittest.TestCase):
    def test_selected_peer_snapshot_pins(self):
        v=json.loads((RAW/'peer-pins.json').read_bytes())
        for p in v['pins']:
            b=Path(p['snapshot']).read_bytes();self.assertEqual(hashlib.sha256(b).hexdigest(),p['sha256'])
            if p.get('encoding')=='gzip':self.assertEqual(hashlib.sha256(gzip.decompress(b)).hexdigest(),p['original_sha256'])

    def test_53_and_3_are_disjoint_universes_not_narrowing(self):
        v=candidate_sets(raw()['relocations']);self.assertEqual(len(v['naive']),53);self.assertEqual(v['exact_reserve_notify'],[0x10b1150,0x10b1240,0x10b1330]);self.assertEqual(v['intersection'],[])
        self.assertNotIn(0x10b1150,v['naive'])

    def test_constructor_original_adrp_add_store_selects_vptr(self):
        w=next(w for w in raw()['windows'] if w['va']==0x6d2894);s=constant_stores(bytes.fromhex(w['hex']),w['va'])
        self.assertIn(dict(pc=0x6d28e0,value=0x10b1150,base_register=19,offset=0,hex='690200f9'),s)

    def test_two_original_direct_bl_in_graph_builder(self):
        w=next(w for w in raw()['windows'] if w['va']==0x6cf7b4);b=bytes.fromhex(w['hex']);hits=[]
        for off in range(0,len(b),4):
            r=branch(int.from_bytes(b[off:off+4],'little'),w['va']+off)
            if r and r['target']==0x6d2950:hits.append(r)
        self.assertEqual([r['pc'] for r in hits],[0x6cfc34,0x6cfc44]);self.assertTrue(all(r['link'] for r in hits))

    def test_callback_token_is_not_raw_string_at_addend(self):
        m=json.loads((RAW/'peer-marker-decode.json').read_bytes());d=decode_rela(m['cells'][0]['rela_hex']);self.assertEqual((d['address'],d['type'],d['addend']),(0x2adfb48,1027,0x2be5cb8))
        v=decode_usage(m['drone_literal']['pointee']['hex']);self.assertEqual((v['kind'],v['index'],v['lowbit']),(5,7763,1));self.assertFalse(v['cell_is_utf8_literal'])
        self.assertNotEqual(bytes.fromhex(m['drone_literal']['pointee']['hex']),b'Stop')

    def test_own_zero_loop_replay_preserves_a5_byte_no_zero_writes(self):
        r=replay(0);self.assertEqual(r['instruction_count'],34);self.assertEqual(r['manager']['byte100'],0xa5);self.assertEqual(r['byte_writes'],[])

    def test_own_one_loop_replay_pc_and_set_then_zero(self):
        r=replay(1);self.assertEqual(r['instruction_count'],457)
        self.assertEqual([(w['pc'],w['value']) for w in r['byte_writes']],[(0x6d6c9c,1),(0x6d81c4,0),(0x6d81c8,0)])
        self.assertEqual(r['pc_counts']['0x570a70'],2);self.assertEqual(r['manager']['byte100'],0)

    def test_own_three_loop_replay_matches_peer_not_importing_peer_tools(self):
        peer=artifact()['standalone'][2];r=replay(3);self.assertEqual(r['instruction_count'],1281);self.assertEqual(r['unique_executed_addresses'],peer['run']['executed_addresses'])
        self.assertTrue(all(r['pc_counts'][pc]==n for pc,n in peer['pc_hits'].items()));self.assertEqual(len(r['byte_writes']),9);self.assertEqual(len(r['allocator_calls']),3)
        self.assertEqual([x['target'] for x in r['virtual_calls']],[0x571b3c]+[x for _ in range(3) for x in (0x6d5134,0x571a80)])

    def test_own_zero_prefill_three_loop_does_not_change_native_counts(self):
        r=replay(3,0);self.assertEqual(r['instruction_count'],1281);self.assertEqual(r['queue']['acquired'],3);self.assertEqual(r['owner']['count'],44)
        self.assertTrue(all(x['byte100']==0 for x in r['node_states']))

    def test_scope_is_fixture_not_original_heap_or_runtime(self):
        r=replay(1);self.assertIn('NOT',r['evidence_tier']);self.assertIn('fixture',r['evidence_tier']);self.assertEqual(r['service_calls'][0]['symbol'],'memset')
        for pc in ('0x573a34','0x3f1d78','0x570ff0','0x109acc0'):self.assertNotIn(pc,r['pc_counts'])


if __name__=='__main__':unittest.main()
