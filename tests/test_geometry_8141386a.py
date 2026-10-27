"""#5 replication: real source witness + explicit CPU policy boundaries.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
import copy
import gzip
import json
import math
import random
import struct
import unittest

from tools.verify.geometry_8141386a_sources import load, sha, SELECTED
from tools.verify.l3_geometry_8141386a import build, specification, byte_witness, OUT, WITNESS
from tools.verify.l3_geometry_8141386a_math import sliced, tiled, UnsupportedGeometry, invariants
from tools.recovery.geometry_8141386a_bytes import sprite_prefix


class Geometry8141386a(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selected = load()
        cls.source, cls.request, cls.evidence = specification(cls.selected, cls.selected['cases'][0])
        cls.document = build()

    def s(self):
        return copy.deepcopy(self.source)

    def test_exact_root_identity(self):
        self.assertEqual(self.evidence['renderer'], {'serialized_file':'data.unity3d/level2','path_id':5739})
        self.assertEqual(self.evidence['sprite']['path_id'],3564)
        self.assertEqual(self.evidence['atlas']['path_id'],580605)
        self.assertEqual(self.evidence['texture']['path_id'],844)
        self.assertEqual(self.evidence['exact_render_key_slot'],10)

    def test_raw_sprite_is_nonzero_border_not_a_quad_substitute(self):
        self.assertEqual(self.source['border_px_lbrt'],[45,20,45,20])
        self.assertEqual(self.source['source_rect_px'],[94,50])
        self.assertEqual(self.source['pixels_per_unit'],100)
        self.assertEqual(self.request['size'],[10,5])
        self.assertEqual(self.request['draw_mode'],1)

    def test_source_pins_and_fresh_original_object_sha(self):
        witness = byte_witness(self.selected)
        self.assertEqual(witness['xapk_sha256'],'f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e')
        self.assertEqual(witness['bundle_sha256'],'7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7')
        self.assertEqual(len(witness['objects']),4)
        self.assertTrue(all(o['fresh_source_sha_matches_raw102'] for o in witness['objects']))

    def test_border_is_redecoded_from_original_little_endian_bytes(self):
        witness=json.loads(gzip.decompress(WITNESS.read_bytes()))
        p=next(o['prefix'] for o in witness['objects'] if o['role']=='sprite')
        self.assertEqual(sprite_prefix(bytes.fromhex(p['prefix_hex'])),p)
        b=p['fields']['m_Border']
        self.assertEqual((b['offset'],b['size']),(40,16))
        self.assertEqual(b['hex'],'000034420000a041000034420000a041')
        self.assertEqual(list(struct.unpack('<4f',bytes.fromhex(b['hex']))),[45,20,45,20])
        self.assertEqual(sha(bytes.fromhex(b['hex'])),b['sha256'])

    def test_truncated_original_prefix_rejected(self):
        for blob in [b'',b'\x00',struct.pack('<i',-1),struct.pack('<i',5000),struct.pack('<i',4)+b'ab',b'\x00'*16]:
            with self.subTest(blob=blob), self.assertRaises(ValueError):
                sprite_prefix(blob)

    def test_sliced_root_grid_topology(self):
        m=sliced(self.source,[10,5])
        self.assertEqual(len(m['vertices']),16)
        self.assertEqual(len(m['uvs']),16)
        self.assertEqual(len(m['indices']),54)
        self.assertEqual(len(m['cells']),9)
        self.assertEqual(m['indices'][:6],[0,4,1,1,4,5])
        self.assertEqual(m['details']['destination_cuts'],[[-5,-4.55,4.55,5],[-2.5,-2.3,2.3,2.5]])

    def test_nonzero_borders_preserve_pixel_to_local_scale(self):
        m=sliced(self.source,[10,5]);x,y=m['details']['destination_cuts']
        for actual,expected in [(x[1]-x[0],.45),(x[3]-x[2],.45),(y[1]-y[0],.2),(y[3]-y[2],.2)]:
            self.assertAlmostEqual(actual,expected)
        self.assertEqual(m['details']['source_pixel_cuts'],[[0,45,49,94],[0,20,30,50]])

    def test_exact_atlas_uv_cut_coordinates_not_uv0(self):
        m=sliced(self.source,[10,5])
        self.assertEqual([v[0] for v in m['uvs'][:4]],[886/1024,931/1024,935/1024,980/1024])
        self.assertEqual([m['uvs'][i*4][1] for i in range(4)],[0,20/1024,30/1024,50/1024])
        self.assertTrue(any(any(v) for v in m['uvs']))
        self.assertEqual(self.source['texture_size'],[1024,1024])

    def test_quad_stretch_is_a_real_counterexample(self):
        # A simple stretched quad would put source-pixel45 at x=-5+10*45/94.
        stretched=-5+10*45/94
        self.assertGreater(abs(stretched-(-4.55)),4)
        self.assertEqual(sliced(self.source,[10,5])['vertices'][1][0],-4.55)

    def test_sliced_area_bounds_and_winding(self):
        v=sliced(self.source,[10,5])['invariants']
        self.assertEqual(v['aabb'],[[-5,-2.5,0],[5,2.5,0]])
        self.assertAlmostEqual(v['triangle_area_sum'],50)
        self.assertEqual(v['negative_winding_triangles'],18)
        self.assertEqual(v['positive_winding_triangles'],0)
        self.assertEqual(v['zero_area_triangles'],0)

    def test_undersized_is_explicit_compressed_border_policy(self):
        m=sliced(self.source,[.4,.2]);x,y=m['details']['destination_cuts']
        self.assertEqual(x[1],x[2]);self.assertEqual(y[1],y[2])
        self.assertAlmostEqual(m['details']['border_compression_factors'][0],.4/.9)
        self.assertAlmostEqual(m['details']['border_compression_factors'][1],.2/.4)
        self.assertEqual(m['invariants']['zero_area_triangles'],10)
        self.assertAlmostEqual(m['invariants']['triangle_area_sum'],.08)
        self.assertIn('model policy',m['details']['compression_scope'])

    def test_one_axis_border_compression_is_independent(self):
        m=sliced(self.source,[.4,5])
        self.assertLess(m['details']['border_compression_factors'][0],1)
        self.assertEqual(m['details']['border_compression_factors'][1],1)
        self.assertAlmostEqual(m['invariants']['triangle_area_sum'],2)

    def test_nonzero_border_continuous_partial_tile(self):
        m=tiled(self.source,[1.13,.77])
        xs,ys=m['details']['axes']
        self.assertEqual((len(xs),len(ys)),(8,6))
        self.assertEqual(len(m['vertices']),192)
        self.assertEqual(len(m['indices']),288)
        self.assertAlmostEqual(xs[-2]['fraction'],.75)
        self.assertAlmostEqual(ys[-2]['fraction'],.7)
        self.assertEqual(xs[0]['region'],'first_border')
        self.assertEqual(xs[-1]['region'],'last_border')
        self.assertAlmostEqual(xs[0]['destination'][1]-xs[0]['destination'][0],.45)
        self.assertAlmostEqual(xs[-1]['destination'][1]-xs[-1]['destination'][0],.45)
        self.assertAlmostEqual(m['invariants']['triangle_area_sum'],1.13*.77)

    def test_tiles_repeat_source_center_not_stretched_uv(self):
        m=tiled(self.source,[1.13,.77]);xs=m['details']['axes'][0]
        centers=[s for s in xs if s['region']=='repeat_center']
        self.assertEqual(len(centers),6)
        for s in centers[:-1]:
            self.assertAlmostEqual(s['source'][0],45)
            self.assertAlmostEqual(s['source'][1],49)
        self.assertAlmostEqual(centers[-1]['source'][1],48)
        self.assertGreater(len({tuple(v) for v in m['vertices']}),16)

    def test_tiled_compressed_request_has_only_four_corner_cells(self):
        m=tiled(self.source,[.4,.2])
        self.assertEqual(len(m['cells']),4)
        self.assertEqual(len(m['vertices']),16)
        self.assertEqual(m['invariants']['zero_area_triangles'],0)
        self.assertAlmostEqual(m['invariants']['triangle_area_sum'],.08)

    def test_adaptive_mode_is_fail_closed(self):
        for mode in [1,2,-1,True,'0']:
            with self.subTest(mode=mode),self.assertRaisesRegex(UnsupportedGeometry,'adaptive'):
                tiled(self.source,[1.13,.77],tile_mode=mode)

    def test_trim_and_sprite_offset_rejected_not_guessed(self):
        for field in ['trim_offset_px','sprite_offset_px']:
            s=self.s();s[field]=[1,0]
            with self.subTest(field=field),self.assertRaisesRegex(UnsupportedGeometry,'trim'):
                sliced(s,[10,5])

    def test_rotation_or_tight_settings_fail_closed(self):
        for settings in [3,5,17,19,True]:
            s=self.s();s['settings_raw']=settings
            with self.subTest(settings=settings),self.assertRaisesRegex(UnsupportedGeometry,'unrotated'):
                sliced(s,[10,5])

    def test_atlas_size_and_affine_disagreement_rejected(self):
        for field,value in [('texture_rect_px',[886,0,93,50]),('uv_transform_xyzw',[100,934,100,25]),
                            ('texture_rect_px',[2000,0,94,50]),('texture_size',[0,1024]),('downscale_multiplier',.5)]:
            s=self.s();s[field]=value
            with self.subTest(field=field,value=value),self.assertRaises(UnsupportedGeometry):
                sliced(s,[10,5])

    def test_invalid_border_ppu_or_pivot_rejected(self):
        for field,value in [('border_px_lbrt',[-1,20,45,20]),('border_px_lbrt',[50,20,50,20]),
                            ('pixels_per_unit',0),('pixels_per_unit',float('nan')),('pixels_per_unit',True),
                            ('pivot_normalized',[2,.5]),('source_rect_px',[0,50])]:
            s=self.s();s[field]=value
            with self.subTest(field=field,value=value),self.assertRaises(UnsupportedGeometry):
                sliced(s,[10,5])

    def test_zero_negative_nonfinite_and_boolean_size_rejected(self):
        for size in [[0,5],[-1,5],[float('nan'),5],[float('inf'),5],[True,5],[10],[10,5,3]]:
            with self.subTest(size=size),self.assertRaises(UnsupportedGeometry):
                sliced(self.source,size)

    def test_tile_budget_has_no_unbounded_allocation(self):
        for size in [[100000,100000],[10,5]]:
            with self.subTest(size=size),self.assertRaisesRegex(UnsupportedGeometry,'budget'):
                tiled(self.source,size)

    def test_zero_source_center_cannot_be_invented(self):
        s=self.s();s['border_px_lbrt']=[47,25,47,25]
        with self.assertRaisesRegex(UnsupportedGeometry,'seed'):
            tiled(s,[10,5])

    def test_flips_preserve_uv_bindings_and_area(self):
        original=sliced(self.source,[10,5])
        for flip in [(True,False),(False,True),(True,True)]:
            m=sliced(self.source,[10,5],flip=flip)
            self.assertEqual(m['uvs'],original['uvs'])
            self.assertEqual(m['indices'],original['indices'])
            self.assertAlmostEqual(m['invariants']['triangle_area_sum'],50)
            self.assertEqual(m['vertices'][0][:2],[5 if flip[0] else -5,2.5 if flip[1] else -2.5])
        with self.assertRaises(UnsupportedGeometry):
            sliced(self.source,[10,5],flip=[1,False])

    def test_random_sliced_requests_retain_area_bounds_and_source_uv(self):
        rng=random.Random(8141386)
        expected=sliced(self.source,[10,5])['uvs']
        for _ in range(100):
            size=[10**rng.uniform(-2,2),10**rng.uniform(-2,2)]
            m=sliced(self.source,size)
            self.assertEqual(m['uvs'],expected)
            self.assertLessEqual(abs(m['invariants']['area_error']),m['invariants']['area_tolerance'])
            self.assertEqual(m['invariants']['index_count'],54)

    def test_index_and_area_corruption_rejected(self):
        for change in ['index','position']:
            m=sliced(self.source,[10,5])
            if change=='index':m['indices'][0]=1000
            else:m['vertices'][0][0]-=100
            with self.subTest(change=change),self.assertRaises(ValueError):
                invariants(m,self.source)

    def test_all_26_observed_tiles_explicitly_reject_unsupported_trim(self):
        self.assertEqual(self.document['counts']['serialized_draw_modes'],{'1':1,'2':26})
        rejected=[c for c in self.document['cases'] if c['geometry']['status']=='not_generated']
        self.assertEqual(len(rejected),26)
        for c in rejected:
            self.assertIsNone(c['geometry']['vertices'])
            self.assertIsNone(c['geometry']['uvs'])
            self.assertIsNone(c['geometry']['indices'])
            self.assertIn('trim',c['geometry']['reason'])
            self.assertEqual(c['source']['border_px_lbrt'],[0,0,0,0])

    def test_inputs_do_not_uniquely_determine_native_vertex_sharing(self):
        m=sliced(self.source,[10,5]);expanded=copy.deepcopy(m)
        for channel in ('vertices','uvs','source_pixels'):
            expanded[channel]=[m[channel][i] for i in m['indices']]
        expanded['indices']=list(range(54))
        v=invariants(expanded,self.source)
        self.assertEqual(v['vertex_count'],54)
        self.assertEqual(v['triangle_count'],m['invariants']['triangle_count'])
        self.assertEqual(v['aabb'],m['invariants']['aabb'])
        self.assertAlmostEqual(v['triangle_area_sum'],m['invariants']['triangle_area_sum'])
        # Same surfaces / UV inputs, distinct valid vertex arrays: no native topology proof.
        self.assertNotEqual(expanded['vertices'],m['vertices'])

    def test_synthetic_requests_cannot_be_mistaken_for_runtime(self):
        for e in self.document['experiments']:
            self.assertEqual(e['evidence_level'],'EXPLICIT_SYNTHETIC_REQUEST_USING_PINNED_SPRITE_NOT_RUNTIME')
        self.assertTrue(any('native' in x for x in self.document['boundaries']))
        self.assertNotIn('Unity_readback',self.document['disposition'])

    def test_deterministic_artifact_matches_checked_in_bytes(self):
        from tools.verify.geometry_8141386a_sources import canonical
        expected=gzip.compress(canonical(self.document),mtime=0)
        self.assertEqual(OUT.read_bytes(),expected)
        self.assertEqual(build(),self.document)
        self.assertEqual(sha(SELECTED.read_bytes()),
                         self.document['inputs']['reverse-engineering/raw/geometry-8141386a/selected-inputs.json.gz'])


if __name__=='__main__':
    unittest.main()
