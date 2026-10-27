import gzip
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/verify'))
from stage23_ui_flow import compare_after_call,decode_byte_dispatch


class Stage23FlowTests(unittest.TestCase):
    def test_compare_is_bound_to_the_called_getter(self):
        asm='0x10: bl #0x100\n0x14: cmp w0, #1\n0x18: bl #0x200\n0x1c: cmp w0, #2'
        self.assertEqual(compare_after_call(asm,'0x100'),1)
        self.assertEqual(compare_after_call(asm,'0x200'),2)
        with self.assertRaises(ValueError):compare_after_call(asm,'0x300')

    def test_preserved_native_dispatch_is_not_textual_block_order(self):
        raw=json.loads(Path('reverse-engineering/raw/ui-audit/stage23-rodata.json').read_text())
        d=raw['drone_dispatch']
        entries=decode_byte_dispatch(d['bytes_hex'],int(d['branch_base'],16))
        self.assertEqual(entries,d['entries'])
        self.assertEqual([r['target'] for r in entries],['0x14fc574','0x14fc5b0','0x14fc62c','0x14fc66c','0x14fc7e4'])
        self.assertAlmostEqual(raw['drone_post_appear_wait']['float32'],3.9,places=5)

    def test_stage_panel_join_and_conditional_gate_are_preserved(self):
        raw=json.load(gzip.open('reverse-engineering/raw/ui-audit/stage23-ui-flow.json.gz','rt'))
        self.assertTrue(all(raw['checks'].values()))
        self.assertEqual([(r['display_stage'],r['internal_stage_index']) for r in raw['stage_gates']],[(2,1),(3,2)])
        self.assertNotIn('tutorial_index_required',raw['stage_gates'][1])
        panels={r['field']:r['reference'] for r in raw['panel_source']['panels']}
        self.assertEqual(panels['tutobjUseDroneSkill'],{'m_FileID':0,'m_PathID':1906})
        self.assertEqual(panels['tutobjTouchSkill'],{'m_FileID':0,'m_PathID':1911})
        self.assertEqual(raw['panel_source']['serialized_file'],'level2')


if __name__=='__main__':unittest.main()
