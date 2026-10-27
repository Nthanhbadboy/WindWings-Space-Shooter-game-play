import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/verify'))
from ui_loader_analysis import metadata_loads


class MetadataLoadsTests(unittest.TestCase):
    def test_relocation_required_and_overwritten_page_not_reused(self):
        text='0x10: adrp x8, #0x2000\n0x14: ldr x8, [x8, #0x10]\n0x18: ldr x0, [x8, #0x10]'
        hits=metadata_loads(text,{'0x2010':'0x3000'},{0x3000:[{'Name':'A'}]})
        self.assertEqual(len(hits),1)
        self.assertEqual(hits[0]['slot'],'0x2010')
        self.assertEqual(metadata_loads(text,{},{}),[])

    def test_call_clobbers_volatile_page_register(self):
        text='0x10: adrp x8, #0x2000\n0x14: bl #0x100\n0x18: ldr x0, [x8, #0x10]'
        self.assertEqual(metadata_loads(text,{'0x2010':'0x3000'},{0x3000:[{}]}),[])


if __name__=='__main__':unittest.main()
