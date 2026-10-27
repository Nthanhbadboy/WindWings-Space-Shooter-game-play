import gzip
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/verify'))
from scene_map_flow import immediate_array, asm_range


class SceneMapFlowTests(unittest.TestCase):
    def test_literal_arrays_are_redecoded_from_raw_not_inherited_maps(self):
        with gzip.open('reverse-engineering/raw/ui-audit/scene-map-flow.json.gz','rt') as f:
            evidence=json.load(f)
        self.assertTrue(all(evidence['checks'].values()))
        rows=evidence['campaign_immediates']['rows']
        self.assertEqual([r['internal_stage_index'] for r in rows],[1,2])
        self.assertEqual([immediate_array(r['literal_store_asm']) for r in rows],[[164],[113,5]])

    def test_immediate_parser_fails_closed_on_missing_or_clobbered_store(self):
        prefix='0x10: mov w1, #1\n0x14: bl #0x110d09c\n'
        valid=prefix+'0x18: mov w8, #0xa4\n0x1c: str w8, [x1, #0x20]\n'
        self.assertEqual(immediate_array(valid),[164])
        for invalid in (prefix,valid.replace('0x1c: str','0x1a: ldr w8, [x0]\n0x1c: str'),valid.replace('#0x20','#0x24')):
            with self.assertRaises(ValueError):immediate_array(invalid)

    def test_asm_range_has_explicit_bounds(self):
        s='0x10: mov w1, #1\n0x14: bl #0x110d09c\n0x18: ret\n'
        self.assertEqual(asm_range(s,0x14,0x14),'0x14: bl #0x110d09c\n')
        with self.assertRaises(ValueError):asm_range(s,0x20,0x30)

    def test_wave_names_and_fade_callback_are_metadata_backed(self):
        with gzip.open('reverse-engineering/raw/ui-audit/scene-map-flow.json.gz','rt') as f:
            evidence=json.load(f)
        slots=evidence['slots']
        self.assertEqual(slots['0x2adf9a0']['records'][0]['Value'],'Datas/Maps/Waves/Wave_')
        self.assertEqual(slots['0x2adf9c0']['records'][0]['Value'],'0000')
        self.assertEqual(slots['0x2addcf0']['records'][0]['MethodAddress'],0x1276e1c)
