"""Contracts for report 161: `dump.cs` names the call targets the slices could not.

Two address tables live in the dump — the per-method `// RVA:` comment and the
`/* GenericInstMethod :` appendix — and together they resolve every `bl` operand in the
eight `*535b0541` slices except a closed family of 18 helpers and four targets past the
last method start. Everything here is static.
"""
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'verify'))
import dump_rva_index as DX  # noqa: E402

ARTIFACT = ROOT / 'datas/l2_535b0541_dump_rva_index.json.gz'
PIN_BYTES = 5183
PIN_SHA = 'de3afba626d19ec59bee67daeb3f1cd4873b7358a580415c1d286938b536e50b'

METHOD_NAMED = [19464628, 20189848, 22732732, 19941788, 20084804, 20085132,
                22771696, 22772596, 22835700, 19888660, 33442960, 41424900, 20903608]
GENERIC_NAMED = {25841028: 'Action<int>..ctor',
                 29195864: 'List<object>.AddWithResize',
                 28921100: 'List<int>.AddWithResize'}


def payload():
    return json.loads(gzip.decompress(ARTIFACT.read_bytes()))


class ArtifactPin(unittest.TestCase):
    def test_byte_size(self):
        self.assertEqual(ARTIFACT.stat().st_size, PIN_BYTES)

    def test_byte_stable(self):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), PIN_SHA)

    def test_rebuild_reproduces_bytes(self):
        blob = json.dumps(DX.build(), sort_keys=True, separators=(',', ':'))
        self.assertEqual(gzip.compress(blob.encode(), mtime=0), ARTIFACT.read_bytes())

    def test_static_only(self):
        blob = payload()
        self.assertEqual(blob['evidence'], 'STATIC_ONLY_ORIGINAL_APK')
        self.assertIn('MODEL_NOT_MEASURED runtime', json.dumps(blob['open_items']))

    def test_every_check_passed(self):
        checks = payload()['checks']
        self.assertEqual(len(checks), 24)
        self.assertTrue(all(row['passed'] for row in checks), checks)


class Tables(unittest.TestCase):
    def test_method_and_generic_table_sizes(self):
        totals = payload()['totals']
        self.assertEqual(totals['method_rvas'], 64727)
        self.assertEqual(totals['generic_rvas'], 49561)
        self.assertEqual(totals['tables'], 114288)
        self.assertEqual(totals['classes'], 10906)

    def test_image_bounds(self):
        image = payload()['image']
        self.assertEqual(image['first_method'], 0x1216610)
        self.assertEqual(image['last_method'], 0x299080C)

    def test_tables_do_not_overlap(self):
        methods, generics, _ = DX.dump_tables()
        self.assertFalse(set(methods) & set(generics))


class StaticClasses(unittest.TestCase):
    '''Erratum: the first cut of this index skipped `static class` declarations.'''

    def test_static_class_declarations_are_parsed(self):
        methods, _, _ = DX.dump_tables()
        self.assertEqual(methods[0x277D2C0]['class_name'], 'Random')
        self.assertEqual(methods[0x277D280]['class_name'], 'Random')

    def test_no_method_is_attributed_to_the_previous_class(self):
        methods, _, _ = DX.dump_tables()
        for rva in (0x277D2C0, 0x277D280, 0x277D304):
            self.assertNotEqual(methods[rva]['class_name'], 'PropertyName')


class Slices(unittest.TestCase):
    def test_eight_slice_files_hold_2499_records(self):
        cross = payload()['cross_check']
        self.assertEqual(cross['slice_records'], 2499)
        self.assertEqual(len(cross['per_file']), 8)
        self.assertEqual(cross['per_file']['arena-pvp-535b0541'], 1361)

    def test_711_records_are_duplicates_of_other_slices(self):
        cross = payload()['cross_check']
        self.assertEqual(cross['distinct_slice_methods'], 1788)
        self.assertEqual(cross['duplicates'], 711)

    def test_every_slice_method_is_in_the_dump_with_the_same_class(self):
        cross = payload()['cross_check']
        self.assertEqual(cross['present_in_dump'], 1788)
        self.assertEqual(cross['class_mismatch'], [])

    def test_every_slice_method_has_the_same_signature(self):
        self.assertEqual(payload()['cross_check']['signature_mismatch'], [])


class Calls(unittest.TestCase):
    def test_bl_sites_split_by_source(self):
        buckets = payload()['calls']['bl']['buckets']
        self.assertEqual(buckets, {'slice': 1104, 'dump': 5638, 'generic': 3218,
                                   'unresolved': 10214})

    def test_no_bl_target_falls_between_two_named_methods(self):
        self.assertEqual(payload()['totals']['in_gap_sites'], 0)

    def test_unnamed_bl_sites_split_between_helpers_and_the_tail(self):
        totals = payload()['totals']
        self.assertEqual(totals['helper_sites'], 10176)
        self.assertEqual(totals['tail_branch_sites'], 38)
        self.assertEqual(totals['helper_sites'] + totals['tail_branch_sites'],
                         totals['unnamed_bl_sites'])

    def test_almost_half_of_all_bl_sites_are_named_by_the_dump(self):
        totals = payload()['totals']
        self.assertEqual(totals['bl_sites'], 20174)
        self.assertEqual(totals['named_bl_sites'], 9960)

    def test_top_generic_instantiations(self):
        top = payload()['calls']['top_generic']
        self.assertEqual(top['List<object>.AddWithResize'], 1305)
        self.assertEqual(top['List<int>.AddWithResize'], 596)
        self.assertEqual(top['List<object>.get_Item'], 187)
        self.assertEqual(top['Func<bool>..ctor'], 113)


class Named(unittest.TestCase):
    def test_thirteen_method_table_names(self):
        named = payload()['named']
        for rva in METHOD_NAMED:
            row = named[str(rva)]
            self.assertEqual(row['source'], 'method-table')
            self.assertTrue(row['matches_class'], row)
            self.assertTrue(row['matches_signature'], row)

    def test_three_generic_table_names(self):
        named = payload()['named']
        for rva, label in GENERIC_NAMED.items():
            row = named[str(rva)]
            self.assertEqual(row['source'], 'generic-table')
            self.assertEqual(row['label'], label)
            self.assertTrue(row['matches_signature'], row)

    def test_action_ctor_has_no_method_row(self):
        methods, generics, _ = DX.dump_tables()
        self.assertNotIn(25841028, methods)
        self.assertEqual(generics[25841028], 'Action<int>..ctor')

    def test_160_display_class_ctors_are_now_named(self):
        named = payload()['named']
        self.assertEqual(named['22771696']['class_name'],
                         'Arena_Shop.<>c__DisplayClass31_2')
        self.assertEqual(named['22772596']['class_name'],
                         'Arena_Shop.<>c__DisplayClass31_3')


class Helpers(unittest.TestCase):
    def test_eighteen_helpers_below_the_first_method(self):
        helpers = payload()['helpers']
        self.assertEqual(len(helpers), 18)
        self.assertEqual(sum(row['calls'] for row in helpers), 10176)
        self.assertTrue(all(row['rva'] < 0x1216610 for row in helpers))

    def test_biggest_helper_is_the_one_thousand_six_hundred_twenty_eight(self):
        helpers = {row['rva']: row for row in payload()['helpers']}
        self.assertEqual(helpers[17879080]['calls'], 4631)
        self.assertEqual(helpers[17879080]['hex'], '0x110d028')

    def test_17879340_looks_like_a_class_init_guard(self):
        helpers = {row['rva']: row for row in payload()['helpers']}
        context = helpers[17879340]['context']
        self.assertEqual(context['sites'], 1695)
        self.assertGreaterEqual(context['with_class_init_flag'], 1600)
        self.assertGreaterEqual(context['with_cbnz'], 1600)

    def test_17879616_is_the_allocation_helper(self):
        helpers = {row['rva']: row for row in payload()['helpers']}
        self.assertEqual(helpers[17879616]['calls'], 1547)
        self.assertEqual(helpers[17879616]['hex'], '0x110d240')


class PastEnd(unittest.TestCase):
    def test_four_targets_past_the_last_method(self):
        rows = payload()['past_end']
        self.assertEqual(len(rows), 4)
        self.assertEqual(sum(row['calls'] for row in rows), 38)
        self.assertTrue(all(row['rva'] > 0x299080C for row in rows))

    def test_math_round_helper_is_still_unnamed(self):
        rows = {row['rva']: row for row in payload()['past_end']}
        self.assertIn(43584368, rows)
        self.assertEqual(rows[43584368]['calls'], 5)
        self.assertEqual(rows[43584368]['delta_past_last_method'], 868)
        self.assertIn('43584368', payload()['still_unnamed'])

    def test_nearest_named_method_is_the_last_one_in_the_dump(self):
        rows = {row['rva']: row for row in payload()['past_end']}
        self.assertEqual(rows[43584368]['nearest_named_method']['class_name'],
                         '__Il2CppComDelegate')


class TailBranches(unittest.TestCase):
    def test_tail_branch_sample_lands_mid_body(self):
        sample = payload()['in_gap']
        self.assertEqual(len(sample), 20)
        methods, _, _ = DX.dump_tables()
        self.assertTrue(all(row['rva'] not in methods for row in sample))
        self.assertEqual(payload()['calls']['b']['buckets']['unresolved'], 3065)
        self.assertEqual(sample[0]['rva'], 19877540)


class PreviousReport(unittest.TestCase):
    def test_160_artifact_still_passes(self):
        previous = json.loads(gzip.decompress((ROOT / DX.PREV).read_bytes()))
        self.assertEqual(len(previous['checks']), 25)
        self.assertTrue(all(row['passed'] for row in previous['checks']))


if __name__ == '__main__':
    unittest.main()
