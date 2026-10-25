#!/usr/bin/env python3
"""Sinh `docs/spec/RAW_AUDIT.md` — sổ kiểm **claim nào đo từ raw**.

Nguồn phân loại duy nhất: `classify_claims()` trong `tools/verify-claims.py`.
Không định nghĩa lại luật ở đây, để sổ và claim **RB1** không bao giờ lệch nhau.
"""

from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFIER = os.path.join(ROOT, "tools", "verify-claims.py")
OUT = os.path.join(ROOT, "docs", "spec", "RAW_AUDIT.md")


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_claims", VERIFIER)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # dataclass cần module đã đăng ký
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    mod = load_verifier()
    rows = mod.classify_claims()
    counts = {k: sum(1 for r in rows if r[1] == k) for k in ("RAW", "DOC", "CONST")}
    total = len(rows)

    lines = [
        "# RAW_AUDIT — claim nào **đo từ dữ liệu gốc**, claim nào chỉ là văn",
        "",
        "> Sinh bằng `python3 tools/raw-audit.py`; luật phân loại nằm ở `classify_claims()`",
        "> trong `tools/verify-claims.py`. **Đừng sửa tay** số trong file này.",
        "> Mục đích: trả lời câu *\"tài liệu dựa vào raw hay nói mồm?\"* bằng máy, không bằng lời.",
        "",
        "## 0. Tổng",
        "",
        f"**RAW {counts['RAW']} · DOC {counts['DOC']} · CONST {counts['CONST']} · tổng {total}**",
        "",
        "| loại | số claim | nghĩa |",
        "|---|---:|---|",
        f"| **RAW** | **{counts['RAW']}** | hàm đo **mở file** trong `datas/` · `reverse-engineering/` · `docs/assets/` |",
        f"| **DOC** | **{counts['DOC']}** | chỉ đọc `docs/**` — kiểm tính nhất quán tài liệu, **không** phải dữ liệu gốc |",
        f"| **CONST** | **{counts['CONST']}** | **không mở file** — số đo một lần, không tái đo bằng máy |",
        f"| **cộng** | **{total}** | |",
        "",
        (
            f"⇒ **{counts['RAW']}/{total}** claim tái đo được từ raw. "
            f"**{counts['CONST']}** claim là hằng số (xem §2) — dùng để **tham khảo**, "
            "không dùng làm bằng chứng khi thiết kế."
        ),
        "",
        "## 1. Cách phân loại",
        "",
        "Đọc **source của hàm đo** (và các hàm nó gọi, sâu 3 tầng). Nếu source có đường dẫn tới",
        "`datas/`, `reverse-engineering/`, `docs/assets/`, hoặc gọi `ref_lines`/`ref_json`/`_csv_rows`",
        "⇒ **RAW**. Chỉ có `docs/` ⇒ **DOC**. Không có gì ⇒ **CONST**.",
        "",
        "> **Giới hạn:** đây là kiểm **tĩnh theo source**, không chứng minh hàm đo *dùng dữ liệu đúng cách*.",
        "> Một claim RAW vẫn có thể diễn giải sai (đã từng: `23.757` dòng vs lượt). Nó chỉ bảo đảm **có file thật**",
        "> đứng sau con số và chạy lại được trên máy khác.",
        "",
        "## 2. Claim **CONST** — \"đo một lần\", không tái lập",
        "",
    ]

    consts = [r for r in rows if r[1] == "CONST"]
    if consts:
        lines += ["| claim | tài liệu | ghi chú |", "|---|---|---|"]
        lines += [f"| **{cid}** | `{os.path.basename(doc)}` | {note or '—'} |" for cid, _k, doc, note in consts]
    else:
        lines.append("_Không có claim CONST._")

    lines += ["", "## 3. Claim **DOC** — tự nhất quán, không phải bằng chứng dữ liệu", ""]
    docs = [r for r in rows if r[1] == "DOC"]
    if docs:
        lines += ["| claim | tài liệu | ghi chú |", "|---|---|---|"]
        lines += [f"| **{cid}** | `{os.path.basename(doc)}` | {note or '—'} |" for cid, _k, doc, note in docs]
    else:
        lines.append("_Không có claim DOC._")

    lines += [
        "",
        "## 4. Luật dùng số",
        "",
        "1. Số để **quyết định thiết kế** phải là claim **RAW** — hoặc ghi rõ \"đo một lần, ngày …\".",
        "2. Số **CONST** được phép tồn tại, nhưng **không** được dùng để bác một kết luận khác.",
        "3. Thêm claim mới: **đừng** viết `lambda: <hằng số>`; mở file raw và đo, hoặc khai báo là CONST.",
        "",
        "```bash",
        "python3 tools/raw-audit.py      # sinh lại file này",
        "python3 tools/verify-claims.py  # claim RB1 khoá dòng \"RAW … · tổng …\" ở §0",
        "```",
        "",
    ]

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    print(f"RAW {counts['RAW']} · DOC {counts['DOC']} · CONST {counts['CONST']} · tổng {total}")
    print(f"đã ghi {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
