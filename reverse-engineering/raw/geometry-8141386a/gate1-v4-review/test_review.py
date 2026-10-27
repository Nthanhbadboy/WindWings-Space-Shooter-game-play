#!/usr/bin/env python3
"""Standard-library tests for the reviewer-owned, bounded verifier only."""
import copy
import gzip
import hashlib
import json
import unittest

import verify_review as v


class PrimitiveTests(unittest.TestCase):
    def test_decode_positive_bl(self):
        self.assertEqual(v.decode_bl(0x94000003, 0x100), 0x10c)

    def test_decode_negative_bl(self):
        self.assertEqual(v.decode_bl(0x97ffffff, 0x100), 0xfc)

    def test_non_bl_rejected(self):
        with self.assertRaises(v.ReviewError):
            v.decode_bl(0xd65f03c0, 0x100)

    def test_store_offset_and_registers(self):
        # STR X20,[X19,#408]
        word = 0xf9000000 | (51 << 10) | (19 << 5) | 20
        self.assertEqual(v.decode_store_x20_x19(word), 408)
        with self.assertRaises(v.ReviewError):
            v.decode_store_x20_x19(word ^ 1)
        with self.assertRaises(v.ReviewError):
            v.decode_store_x20_x19(0xd503201f)

    def test_token_valid(self):
        self.assertEqual(v.token_ordinal((4 << 29) | 3, 2), (4, 3, 1))

    def test_token_rejects_wrong_kind_even_or_out_of_range(self):
        for token in ((3 << 29) | 3, (4 << 29) | 2, (4 << 29) | 5):
            with self.subTest(token=token), self.assertRaises(v.ReviewError):
                v.token_ordinal(token, 2)

    def test_rule_order_and_unknown_kind(self):
        self.assertEqual(v.classify('RUNTIME', 'POLICY'), 'runtime-gated→USER')
        self.assertEqual(v.classify('OPEN', 'POLICY'), 'policy')
        self.assertEqual(v.classify('OPEN', 'PIN-RAW'), 'missing-input')
        self.assertEqual(v.classify('RESTATED', 'INDEX'), 'served')
        self.assertIsNone(v.classify('OPEN', 'UNKNOWN'))


class SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = v.Sources()
        cls.native = cls.sources.json('key_native')
        cls.dump = cls.sources.text('dump')
        cls.defaults = cls.sources.json('defaults')['fields']
        cls.previous = cls.sources.json('hunter133')
        cls.hunter = cls.sources.json('hunter149')
        cls.registry = cls.sources.json('registry')
        cls.audit = cls.sources.json('audit')
        cls.drift = cls.sources.json('drift')
        cls.ia = cls.sources.json('ia_resolved')

    def test_source_hashes_and_spec_identity(self):
        self.assertGreaterEqual(self.sources.check_snapshots(), 30)
        self.assertEqual(self.sources.blob('registry'), self.sources.blob('spec_registry'))
        self.assertEqual(self.sources.rows['registry']['sha256'],
                         'bcd0e0fd95af375b8841021856209eb701d284bf013966d48f868e9143e21a96')

    def test_later_producer_keeps_reviewed_core_but_adds_one_drift_artifact(self):
        s = self.sources
        self.assertEqual(s.blob('registry'), s.blob('later_registry'))
        self.assertEqual(s.blob('audit'), s.blob('later_audit'))
        self.assertEqual(s.json('drift')['contract'], s.json('later_drift')['contract'])
        self.assertEqual((s.json('drift')['totals']['artifacts'],
                          s.json('later_drift')['totals']['artifacts']), (48, 49))
        self.assertIn('Không đóng mục audit nào', s.text('later_doc181'))
        old = next(row for row in self.registry['ledger'] if row['n'] == 52)
        self.assertIn('0x2ADB958 is unnamed', old['step'])
        newer = s.json('later_firebase181')['cell']
        self.assertEqual((newer['va'], newer['klass'], newer['field']['name']),
                         (0x2ADB958, 'FirebaseDatabaseManager', 'Instance'))
        # These checks establish a discrepancy between publications, not a review
        # of the new identity claim or a verdict that item 52 is resolved.

    def test_manifest_escape_rejected(self):
        s = v.Sources()
        s.rows['audit']['archive'] = '/tmp/outside.bin.gz'
        with self.assertRaises(v.ReviewError):
            s.blob('audit')

    def test_corrupted_digest_rejected(self):
        s = v.Sources()
        s.rows['audit']['sha256'] = '0' * 64
        with self.assertRaises(v.ReviewError):
            s.blob('audit')

    def test_all_six_bindings_and_call_store_words(self):
        r = v.rebind_arrays(self.native, self.dump, self.defaults, self.previous,
                            self.hunter, self.registry, self.ia)
        self.assertEqual([a['field_ordinal'] for a in r['arrays']], [701, 688, 634, 479, 173, 370])
        self.assertEqual([a['field_index'] for a in r['arrays']],
                         [17001, 16988, 16934, 16779, 16473, 16670])
        self.assertEqual(len(r['same_rule_export_overlap']), 1)
        self.assertFalse(r['raw_event_contains_literal_field_id'])

    def test_corrupt_call_rejected_even_if_slice_hash_is_recomputed(self):
        native = copy.deepcopy(self.native)
        ctor = next(m for m in native['methods'] if m['class_name'] == 'Board_PVP'
                    and m['signature'] == 'public void .ctor() { }')
        b = bytearray.fromhex(ctor['bytes_hex'])
        pc = ctor['initialize_arrays'][0]['initialize_rva'] - ctor['rva']
        b[pc:pc+4] = bytes.fromhex('1f2003d5')  # NOP, not BL
        ctor['bytes_hex'] = b.hex()
        ctor['sha256'] = hashlib.sha256(b).hexdigest()
        with self.assertRaises(v.ReviewError):
            v.rebind_arrays(native, self.dump, self.defaults, self.previous,
                            self.hunter, self.registry, self.ia)

    def test_published_field_identifier_is_not_treated_as_raw_event_data(self):
        native = copy.deepcopy(self.native)
        ctor = next(m for m in native['methods'] if m['class_name'] == 'Board_PVP'
                    and m['signature'] == 'public void .ctor() { }')
        ctor['initialize_arrays'][0]['field_id'] = 'invented'
        with self.assertRaises(v.ReviewError):
            v.rebind_arrays(native, self.dump, self.defaults, self.previous,
                            self.hunter, self.registry, self.ia)

    def test_exact_ledger_partition_and_all_labels(self):
        r = v.check_ledger(self.registry, self.audit, self.drift)
        self.assertEqual(r['distinct_ledger_ids'], 32)
        self.assertEqual(r['labels'], {'runtime-gated→USER': 20, 'served': 7,
                                       'missing-input': 3, 'policy': 2})
        self.assertEqual(r['note_item'], 56)

    def test_missing_or_duplicate_ledger_row_rejected(self):
        for how in ('drop', 'duplicate'):
            reg = copy.deepcopy(self.registry)
            if how == 'drop':
                reg['ledger'].pop()
            else:
                reg['ledger'][-1] = copy.deepcopy(reg['ledger'][0])
            with self.subTest(how=how), self.assertRaises(v.ReviewError):
                v.check_ledger(reg, self.audit, self.drift)

    def test_wrong_label_owner_and_empty_step_rejected(self):
        for key, val in (('label', 'served'), ('owner', 'somebody else'), ('step', ' ')):
            reg = copy.deepcopy(self.registry)
            row = next(r for r in reg['ledger'] if r['label'] == 'runtime-gated→USER')
            row[key] = val
            with self.subTest(key=key), self.assertRaises(v.ReviewError):
                v.check_ledger(reg, self.audit, self.drift)

    def test_director_scope_dispositions_are_explicit_not_runtime_proof(self):
        design = self.sources.text('spec_design')
        closure = self.sources.text('spec_closure')
        start = self.sources.text('spec_start')
        result = v.check_spec_dispositions(design, closure, start)
        self.assertTrue(all(result['literal_scope_locators'].values()))
        for broken in (closure.replace('giá/stock SKU thực chưa đo', ''),
                       closure.replace('item 52 **giữ trong sổ**', ''),
                       closure.replace('deferred/UNKNOWN/RUNTIME_UNVERIFIED', '')):
            with self.subTest(missing=broken != closure), self.assertRaises(v.ReviewError):
                v.check_spec_dispositions(design, broken, start)
        with self.assertRaises(v.ReviewError):
            v.check_spec_dispositions(design.replace('SUPERSEDE TOÀN VĂN', ''), closure, start)

    def test_api_exact_head_and_skipped_device_step(self):
        api = json.loads(gzip.decompress((v.BASE / 'api-captures.json.gz').read_bytes()))
        receipt = v.check_api_capture(api, self.sources)
        self.assertGreaterEqual(len(receipt['runtime_probe_state_skipped_run_ids']), 3)
        broken = copy.deepcopy(api)
        run = next(item for item in broken['runs'].values()
                   if item['run']['name'] == 'runtime-probe')
        step = next(step for job in run['jobs']['jobs'] for step in job['steps']
                    if step['name'] == 'Probe game state')
        step['conclusion'] = 'success'
        with self.assertRaises(v.ReviewError):
            v.check_api_capture(broken, self.sources)
        broken = copy.deepcopy(api)
        next(iter(broken['runs'].values()))['run']['head_sha'] = '0' * 40
        with self.assertRaises(v.ReviewError):
            v.check_api_capture(broken, self.sources)

    def test_original_item9_and_published_defaults_preserved_as_tension(self):
        item = next(r for r in self.audit['items'] if r['n'] == 9)
        shipped = self.sources.json('shop157')['shipped']
        self.assertIn('served, not shipped', item['reason'])
        self.assertEqual(shipped['MaxStockCount']['value'], 10)
        self.assertEqual(shipped['ItemPlayerCost']['value'], 50)
        self.assertEqual(shipped['ItemDroneCost']['value'], 30)
        self.assertIn('hai trần là cùng một field', self.sources.text('doc158'))

    def test_stale_blocking_text_still_present_despite_closed_verdict(self):
        for n in (39, 40):
            row = next(r for r in self.audit['items'] if r['n'] == n)
            self.assertEqual(row['verdict'], 'CLOSED')
            self.assertIn('blob unbound', row['blocking'])

    def test_saved_result_is_byte_reproducible(self):
        result = v.review(self.sources)
        encoded = (json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()
        self.assertEqual(v.RESULT.read_bytes(), encoded)


if __name__ == '__main__':
    unittest.main()
