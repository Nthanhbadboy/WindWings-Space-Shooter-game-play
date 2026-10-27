#!/usr/bin/env python3
"""Test hợp đồng của bộ phân loại sprite (`tools/classify-assets.py`).

Lý do có file này: review `25c367aca` (R4) bắt được **luật bị che** — bảng tài liệu
liệt kê `Coda_*` dưới luật font (R22), nhưng R14 (`^(Coin|Goigem|Coda_)`) đứng trước
nên dữ liệu ra `ui`. Test dưới đây khoá lại:

  1. `Coda_*` → `font`, `XVideo_*` → `ui`;
  2. **không luật nào bị che** trên toàn bộ tên sprite thật;
  3. nhãn passthrough (`category_passthrough`) **không** mang confidence A;
  4. CSV xuất ra có đủ cột provenance.

Chạy:  python3 -m unittest discover -s tests -q
"""
from __future__ import annotations

import csv
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, "docs/assets/sprites-classified.csv")


def _load_tool():
    spec = importlib.util.spec_from_file_location(
        "classify_assets", os.path.join(ROOT, "tools", "classify-assets.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestRuleContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tool = _load_tool()

    def test_coda_is_font(self):
        for name in ("Coda_0", "Coda_1", "Coda_2", "Coda_3"):
            cat, rule, level = self.tool.classify(name, "", None, 0)
            self.assertEqual(cat, "font", f"{name} phải là font, không phải ui")
            self.assertTrue(rule.startswith("R22"), f"{name} phải do R22 xử lý, nhận {rule}")

    def test_xvideo_is_ui(self):
        cat, rule, _ = self.tool.classify("XVideo_3", "", None, 0)
        self.assertEqual(cat, "ui")
        self.assertTrue(rule.startswith("R18"), rule)

    def test_no_rule_is_shadowed(self):
        with open(CSV, encoding="utf-8") as fh:
            names = [r["name"] for r in csv.DictReader(fh)]
        shadowed = self.tool.shadowed_rules(names)
        self.assertEqual(shadowed, [], f"luật bị che: {shadowed}")

    def test_passthrough_has_no_confidence(self):
        with open(CSV, encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        passed = [r for r in rows if r["label_source"] == "category_passthrough"]
        self.assertGreater(len(passed), 0, "phải có nhãn passthrough")
        bad = [r["name"] for r in passed if r["confidence"]]
        self.assertEqual(bad, [], f"passthrough không được có confidence: {bad[:5]}")
        self.assertTrue(all(r["reviewed"] == "false" for r in passed))

    def test_csv_has_provenance_columns(self):
        with open(CSV, encoding="utf-8") as fh:
            cols = next(csv.reader(fh))
        for c in ("label_source", "rule_id", "evidence_ref", "reviewed"):
            self.assertIn(c, cols)


if __name__ == "__main__":
    unittest.main()
