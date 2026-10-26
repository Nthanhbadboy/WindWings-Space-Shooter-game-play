import json
from pathlib import Path
import unittest
from tools.verify.combat_argument_audit import build, must_w0, transfer

ROOT=Path(__file__).resolve().parents[1]


class CombatArgumentAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.audit=build()

    def test_regeneration(self):
        self.assertEqual(self.audit,json.loads((ROOT/'datas/combat_argument_audit.json').read_text()))

    def test_all_72_stat_getters_proved(self):
        self.assertEqual(self.audit['summary'],dict(stat_calls=72,proved=72,rate_calls=24))
        for row in self.audit['proofs']:
            self.assertEqual(row['value'],int(row['implementation'].rsplit('_',1)[1])-1)
            self.assertTrue(row['reachable'])

    def test_branch_bypassing_mov_does_not_prove_constant(self):
        body={0:('cbz','w1, #0xc'),4:('mov','w0, #2'),8:('b','#0x10'),
              12:('nop',''),16:('bl','#0x100'),20:('ret','')}
        self.assertIsNone(must_w0(body,0)[16])

    def test_equal_branch_values_do_prove_constant(self):
        body={0:('cbz','w1, #0xc'),4:('mov','w0, #2'),8:('b','#0x10'),
              12:('mov','w0, #2'),16:('bl','#0x100'),20:('ret','')}
        self.assertEqual(must_w0(body,0)[16],2)

    def test_alias_call_and_unknown_write_kill(self):
        self.assertIsNone(transfer(2,'mov','x0, x19'))
        self.assertIsNone(transfer(2,'bl','#0x100'))
        self.assertIsNone(transfer(2,'ldp','x19, x0, [sp]'))
        self.assertEqual(transfer(2,'str','w0, [x19]'),2)
        self.assertIsNone(transfer(2,'str','w1, [x0], #4'))

    def test_loop_backedge_can_destroy_constant(self):
        body={0:('mov','w0, #2'),4:('cbz','w1, #0x10'),8:('mov','w0, #3'),
              12:('b','#0x4'),16:('bl','#0x100'),20:('ret','')}
        self.assertIsNone(must_w0(body,0)[16])

    def test_disagreeing_branches_not_textual_last_mov(self):
        body={0:('cbz','w1, #0xc'),4:('mov','w0, #1'),8:('b','#0x10'),
              12:('mov','w0, #2'),16:('bl','#0x100'),20:('ret','')}
        self.assertIsNone(must_w0(body,0)[16])

    def test_rate_modifier_exact_pool_and_field_store(self):
        model=self.audit['main_rate_modifier']
        self.assertEqual([r['hex'] for r in model['tiers']],
                         ['8fc2f53c','cdcc4c3d','0ad7a33d','cdcccc3d','8fc2f53d'])
        self.assertEqual(len(model['base_rates']),24)
        asm=(ROOT/'reverse-engineering/raw/combat-chain/native/Player_Get_Datas.asm.txt').read_text()
        for regex in [r'0x14e5ec4: str\s+x19, \[x8, #0x80\]',
                      r'0x14e3dac: mov\s+w0, #1',r'0x14e3db4: bl\s+#0x139d96c',
                      r'0x14e3d54: fsub\s+s0, s1, s0',r'0x14e3d58: fmul\s+s0, s8, s0']:
            self.assertRegex(asm,regex)

    def test_unclean_flag_is_heuristic_not_missing_body(self):
        spans=self.audit['unclean_span_audit']
        resets=[r for r in spans if r['method']=='Reset']
        gizmos=[r for r in spans if r['method']=='OnDrawGizmos']
        self.assertEqual((len(spans),len(resets),len(gizmos)),(38,36,2))
        for r in resets:
            self.assertTrue(r['not_supported_ctor_sites'])
            self.assertEqual(r['last_instruction']['operands'],'#0x110d11c')
        for r in gizmos:
            self.assertTrue(r['returns'])
            self.assertEqual(r['last_instruction']['operands'],'#0x110d250')

    def test_source_root_absence_is_classified_not_generic_unknown(self):
        roots=self.audit['receiver_absence_audit']
        self.assertEqual(sum(r['reason']=='SERIALIZED_ROOT_POINTER_NULL' for r in roots),64)
        nonnull=[r for r in roots if r['reason']=='ROOT_HAS_NO_MONOBEHAVIOUR']
        self.assertEqual(len(nonnull),4)
        for r in nonnull:
            self.assertFalse(any(c['type']=='MonoBehaviour' for c in r['root']['components']))

    def test_enemy_flag_declared_and_loaded_at_exact_offset(self):
        import gzip
        dump=gzip.decompress((ROOT/'reverse-engineering/il2cpp/dump.cs.gz').read_bytes()).decode()
        enemy=dump.split('public class Enemy_Datas :',1)[1].split('// Methods',1)[0]
        self.assertIn('public bool IsCaAttack; // 0x2F',enemy)
        native=(ROOT/'reverse-engineering/raw/combat-chain/native/Enemy_Controller.asm.txt').read_text()
        self.assertRegex(native,r'0x1582b60: ldrb\s+w8, \[x8, #0x2f\]')
        self.assertRegex(native,r'0x1582b64: cbz\s+w8, #0x1582e1c')

    def test_operandless_ret_does_not_swallow_next_instruction(self):
        import tempfile
        from tools.verify.combat_argument_audit import instructions
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'sample.asm'
            path.write_text('    0x100: ret      \n    0x104: bl       #0x110d250\n')
            self.assertEqual(instructions(path),{0x100:('ret',''),0x104:('bl','#0x110d250')})
