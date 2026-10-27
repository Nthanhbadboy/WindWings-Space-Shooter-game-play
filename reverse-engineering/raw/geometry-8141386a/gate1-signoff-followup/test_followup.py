#!/usr/bin/env python3
"""Local tests for the fixed-cut follow-up; no device, network or APK probing."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest import mock

import verify_followup as review


class Followup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.values = review.load_sources()
        cls.capture = review.load_capture()

    def derive(self, values=None, capture=None):
        return review.derive(self.manifest, values or self.values, capture or self.capture)

    def test_result_is_deterministic_and_committed(self):
        result = self.derive()
        encoded = (json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
        self.assertEqual(encoded, (review.HERE / "followup-results.json").read_bytes())
        self.assertEqual(len(result["findings"]), 4)

    def test_signoff_is_reported_not_reopened(self):
        result = self.derive()
        self.assertEqual(result["decision"]["source_comment"], 6445403414)
        self.assertIn("not independently verified or reopened", result["decision"]["boundary"])
        self.assertIn("non-reopening", result["requested_action"])

    def test_note_and_policy_are_not_interchangeable(self):
        reg = review.nested_json(self.values["registry"])
        self.assertEqual(reg["not_in_ledger"]["note_items"], [56])
        self.assertEqual(next(x for x in reg["ledger"] if x["n"] == 52)["label"], "policy")
        self.assertEqual(reg["totals"]["closed"] + reg["totals"]["note"] + reg["totals"]["ledger"], 56)

    def test_wrong_note_id_fails(self):
        values = dict(self.values)
        reg = review.nested_json(values["registry"])
        reg["not_in_ledger"]["note_items"] = [52]
        values["registry"] = gzip.compress(json.dumps(reg).encode(), mtime=0)
        with self.assertRaisesRegex(ValueError, "NOTE must be item 56"):
            self.derive(values)

    def test_wrong_missing_input_class_fails(self):
        values = dict(self.values)
        reg = review.nested_json(values["registry"])
        next(x for x in reg["ledger"] if x["n"] == 49)["kind"] = "DATA"
        values["registry"] = gzip.compress(json.dumps(reg).encode(), mtime=0)
        with self.assertRaisesRegex(ValueError, "missing-input classes"):
            self.derive(values)

    def test_constructor_default_is_not_a_zero_taxonomy_count(self):
        shop = review.nested_json(self.values["shop_defaults"])
        self.assertEqual(shop["shipped"]["MaxStockCount"]["value"], 10)
        self.assertEqual(shop["shipped"]["ItemPlayerCost"]["value"], 50)
        self.assertIn("0 shipped-default is a label count", self.derive()["findings"][0]["partition"])

    def test_item51_is_unknown_not_proof_of_no_later_attempt(self):
        finding = self.derive()["findings"][2]
        self.assertEqual(finding["label"], "UNKNOWN")
        self.assertIn("cannot rule out an unreported later attempt", finding["boundary"])
        self.assertIn("no retry is requested", finding["boundary"])

    def test_altering_producer_claim_is_detected(self):
        capture = copy.deepcopy(self.capture)
        capture["comments"]["6445013675"]["body"] = "51/52 retry đã làm"
        with self.assertRaisesRegex(ValueError, "producer 51/52 statement"):
            self.derive(capture=capture)

    def test_other_proposal_edit_is_detected(self):
        values = dict(self.values)
        values["signed_proposal"] += b"\nextra content\n"
        with self.assertRaisesRegex(ValueError, "proposal diff beyond sign-off"):
            self.derive(values)

    def test_c1_shared_convention_and_runtime_are_bounded(self):
        result = self.derive()
        self.assertIn("shared published C1 token convention", result["findings"][3]["observed"])
        self.assertIn("not proof", result["findings"][3]["boundary"])
        self.assertIn("RUNTIME_UNVERIFIED", result["runtime"])

    def test_failed_run_is_rejected(self):
        capture = copy.deepcopy(self.capture)
        capture["runs"]["40522786309"]["run"]["conclusion"] = "failure"
        with self.assertRaisesRegex(ValueError, "run status"):
            self.derive(capture=capture)

    def test_wrong_head_is_rejected(self):
        capture = copy.deepcopy(self.capture)
        capture["runs"]["40526758183"]["run"]["head_sha"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "run head"):
            self.derive(capture=capture)

    def test_executed_device_step_cannot_be_marked_skipped(self):
        capture = copy.deepcopy(self.capture)
        for job in capture["runs"]["40522799018"]["jobs"]["jobs"]:
            for step in job.get("steps", []):
                if step["name"] == "Probe game state":
                    step["conclusion"] = "success"
        with self.assertRaisesRegex(ValueError, "device step"):
            self.derive(capture=capture)

    def test_incomplete_job_listing_rejected(self):
        capture = copy.deepcopy(self.capture)
        capture["runs"]["40526758183"]["jobs"]["total_count"] += 1
        with self.assertRaisesRegex(ValueError, "job pagination"):
            self.derive(capture=capture)

    def test_changed_source_archive_is_rejected(self):
        original = Path.read_bytes
        def altered(path):
            data = original(path)
            return data[:-1] + bytes([data[-1] ^ 1]) if path.name == "signed_proposal.blob.gz" else data
        with mock.patch.object(Path, "read_bytes", altered):
            with self.assertRaisesRegex(ValueError, "archive hash: signed_proposal"):
                review.load_sources()


if __name__ == "__main__":
    unittest.main()
