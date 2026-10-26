import gzip,hashlib,json,struct,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'datas/l3_ef6b75ef131_native_vtable_dispatch.json.gz'
PROBE=ROOT/'reverse-engineering/raw/owner131/probe.json.gz'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.load(gzip.open(p))
class Owner131Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=ART.read_bytes();cls.art=load(ART);cls.p=load(PROBE)
        cls.snips=[]
        for slot,v in cls.p['sites'].items():
            for r in v['qualified']+v['other']:
                if r.get('window_hex'):cls.snips.append((r['ldr_pc']-4,bytes.fromhex(r['window_hex'])))
        for g in (cls.p['vtable_refs'],cls.p['global_refs']):
            for rows in g.values():
                for r in rows:cls.snips.append((r['pc'],bytes.fromhex(r['hex'])))
        for w in cls.p['windows']:cls.snips.append((w['va'],bytes.fromhex(w['hex'])))
    def at(self,va,n=4):
        for st,b in self.snips:
            if st<=va and va+n<=st+len(b):return b[va-st:va-st+n]
        return None
    def test_schema(self):
        self.assertEqual(sorted(self.art),['callers','counts','dispatch','facts','globals','limits','pins','provisional','scan','vtable_materialization'])
        self.assertIs(self.art['provisional'],True)
        self.assertTrue(self.art['limits'])
    def test_pins(self):
        pins=self.art['pins']
        self.assertEqual(pins['xapk_sha256'],'f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e')
        self.assertEqual(pins['libunity_sha256'],'d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7')
        self.assertEqual(pins['libunity_size'],17783496)
        self.assertEqual(pins['probe']['sha256'],sha(PROBE.read_bytes()))
        self.assertEqual(pins['probe']['size'],PROBE.stat().st_size)
        self.assertEqual(pins['tools']['tools/verify/owner131.py'],sha((ROOT/'tools/verify/owner131.py').read_bytes()))
    def test_facts(self):
        f=self.art['facts']
        self.assertEqual(f['count'],35)
        self.assertEqual(len(f['rows']),35)
        for r in f['rows']:
            self.assertTrue(r['verified'],hex(r['va']))
            b=self.at(r['va'])
            self.assertIsNotNone(b,hex(r['va']))
            self.assertEqual(b.hex(),r['bytes_hex'],hex(r['va']))
    def test_known_bytes(self):
        self.assertEqual(self.at(0x6b9acc).hex(),'a84f00f0')
        self.assertEqual(self.at(0x6b15f8).hex(),'e84f00f0')
        self.assertEqual(self.at(0x47f7f0).hex(),'087d40f9')
        self.assertEqual(self.at(0x47f7f4).hex(),'00013fd6')
        self.assertEqual(self.at(0x3e07b0).hex(),'096800b0')
        self.assertEqual(self.at(0x6b27f0).hex(),'c05100d0')
    def test_vtable_materialization(self):
        vm=self.art['vtable_materialization']
        self.assertEqual(vm['total'],16)
        self.assertEqual(len(vm['tables']),8)
        self.assertEqual([hex(x) for x in vm['unreferenced']],['0x10b1100'])
        by={m['table']:m for m in vm['tables']}
        self.assertEqual(by[0x10b0c80]['count'],2)
        self.assertEqual([x['pc'] for x in by[0x10b0c80]['refs']],[0x6b15f8,0x6b9acc])
        self.assertEqual([x['owner'] for x in by[0x10b0c80]['refs']],[0x6b15d4,0x6b9ac4])
        self.assertEqual(by[0x10b0f98]['count'],3)
        self.assertEqual(by[0x10b1330]['count'],4)
        for m in vm['tables']:
            self.assertTrue(all(x['recomputed'] for x in m['refs']),hex(m['table']))
    def test_per_slot_numbers(self):
        d={x['slot']:x for x in self.art['dispatch']['per_slot']}
        self.assertEqual([d[s]['matches'] for s in (2,3,31,33)],[25214,14770,537,885])
        self.assertEqual([d[s]['with_blr'] for s in (2,3,31,33)],[1859,3922,61,223])
        self.assertEqual([d[s]['qualified_stored'] for s in (2,3,31,33)],[64,64,21,64])
        self.assertEqual([d[s]['other_stored'] for s in (2,3,31,33)],[12,12,12,12])
        self.assertEqual([d[s]['in_cluster'] for s in (2,3,31,33)],[0,0,0,1])
        self.assertTrue(all(d[s]['slot_bytes_ok'] for s in (2,3,31,33)))
        self.assertEqual({d[s]['offset'] for s in (2,3,31,33)},{0x10,0x18,0xf8,0x108})
    def test_slot31_rows(self):
        rows=self.art['dispatch']['slot31']
        self.assertEqual(len(rows),21)
        self.assertEqual(rows[0]['ldr_pc'],0x47f7f0)
        self.assertTrue(all(0 < r['blr_pc']-r['ldr_pc'] <= 32 for r in rows))
        self.assertTrue(any(r['blr_pc']-r['ldr_pc']>4 for r in rows))
        for r in rows:
            self.assertEqual((r['blr_pc']-r['ldr_pc'])%4,0,hex(r['ldr_pc']))
            self.assertIn('window_hex',next(x for x in self.p['sites']['31']['qualified'] if x['ldr_pc']==r['ldr_pc']))
    def test_slot31_ldr_and_blr_decode(self):
        p=self.p['sites']['31']['qualified']
        for r in p:
            code=bytes.fromhex(r['window_hex']);base=r['ldr_pc']-4
            w=struct.unpack_from('<I',code,r['ldr_pc']-base)[0]
            self.assertEqual(w&0xFFC00000,0xF9400000)
            self.assertEqual(((w>>10)&0xFFF)*8,0xf8)
            rt=w&31
            blr=struct.unpack_from('<I',code,r['blr_pc']-base)[0]
            self.assertEqual(blr&0xFFFFFC1F,0xD63F0000)
            self.assertEqual((blr>>5)&31,rt)
    def test_globals(self):
        g={x['addr']:x for x in self.art['globals']}
        self.assertEqual([g[a]['count'] for a in (0x10e18b0,0x10e18f8,0x10e19c8,0x10e18b8,0x10e19d0,0x10ecb08)],[64,64,64,63,32,10])
        self.assertTrue(g[0x10e18b0]['capped'])
        self.assertFalse(g[0x10ecb08]['capped'])
        self.assertEqual(g[0x10ecb08]['count'],10)
    def test_callers(self):
        c=self.art['callers']
        self.assertEqual(c['count'],107)
        self.assertEqual(len(c['rows']),107)
        self.assertLessEqual(len(c['capped']),1)
        for r in c['rows'][:5]:
            self.assertIn(r['kind'],('bl','b'))
    def test_counts(self):
        c=self.art['counts']
        self.assertEqual(c['facts'],35)
        self.assertEqual(c['tables'],8)
        self.assertEqual(c['materializations'],16)
        self.assertEqual(c['slot31_matches'],537)
        self.assertEqual(c['slot31_with_blr'],61)
        self.assertEqual(c['slot31_qualified'],21)
        self.assertEqual(c['owners'],200)
        self.assertEqual(c['callers'],107)
        self.assertEqual(c['global_rows'],297)
    def test_scan(self):
        s=self.art['scan']
        self.assertEqual(s['text'],[{'size':13827552,'va':3589088}])
        self.assertEqual(s['slots'],[2,3,31,33])
        self.assertEqual(s['slot_offsets'],{'2':16,'3':24,'31':248,'33':264})
        self.assertEqual(len(s['family']),9)
        self.assertEqual(len(s['globals']),7)
        self.assertEqual(s['cluster'],[0x6b0000,0x6c0000])
        self.assertEqual(s['owners'],200)
    def test_render_deterministic(self):
        import tools.verify.owner131 as v
        one=v.render(v.build());two=v.render(v.build())
        self.assertEqual(one,two);self.assertEqual(one,self.raw)
        self.assertEqual(self.raw[:8].hex(),'1f8b080000000000')
    def test_check_mode(self):
        out=subprocess.run([sys.executable,'tools/verify/owner131.py','--check'],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(out.returncode,0,out.stderr)
        self.assertIn('check ok',out.stdout)
    def test_no_floats(self):
        def walk(x):
            if isinstance(x,dict):
                for v in x.values():walk(v)
            elif isinstance(x,list):
                for v in x:walk(v)
            elif isinstance(x,float):self.fail('float in artifact')
        walk(self.art)
if __name__=='__main__':unittest.main()
