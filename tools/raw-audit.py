#!/usr/bin/env python3
"""Sinh `docs/spec/RAW_AUDIT.md` — sổ kiểm **claim nào đo từ raw**.

Nguồn phân loại duy nhất: `classify_claims()` trong `tools/verify-claims.py`.
Không định nghĩa lại luật ở đây, để sổ và claim **RB1** không bao giờ lệch nhau.
"""

from __future__ import annotations

import importlib.util
import os
import re
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


RB1_PAT = re.compile(
    r'"\*\*RAW \d+ · DOC \d+ · CONST \d+ · tổng \d+\*\*",\s*'
    r"\(\d+, \d+, \d+, \d+\), raw_audit_counts"
)

# Cùng 4 số, hai cách viết, rải ở 3 tài liệu ⇒ sửa tay là chắc chắn lệch. Sửa một lần ở đây.
COUNT_PATTERNS = (
    (re.compile(r"RAW \d+ · DOC \d+ · CONST \d+ · tổng \d+"),
     "RAW {raw} · DOC {doc} · CONST {const} · tổng {total}"),
    (re.compile(r"\*\*\d+ RAW · \d+ DOC · \d+ CONST / \d+\*\*"),
     "**{raw} RAW · {doc} DOC · {const} CONST / {total}**"),
    (re.compile(r"Nó phân loại \*\*\d+ claim\*\*"),
     "Nó phân loại **{total} claim**"),
    (re.compile(r"\| \*\*RAW\*\* \| \*\*\d+\*\* \|"),
     "| **RAW** | **{raw}** |"),
    (re.compile(r"\| \*\*DOC\*\* \| \*\*\d+\*\* \|"),
     "| **DOC** | **{doc}** |"),
    (re.compile(r"\| \*\*CONST\*\* \| \*\*\d+\*\* \|"),
     "| **CONST** | **{const}** |"),
)


def sync_rb1(raw: int, doc: int, const: int, total: int) -> None:
    """Ghi 4 số vừa đo vào claim RB1 + mọi chỗ trong docs (một nguồn, khỏi sửa tay)."""
    vals = dict(raw=raw, doc=doc, const=const, total=total)
    path = os.path.join(ROOT, "tools/verify-claims.py")
    with open(path, encoding="utf-8") as fh:
        body = fh.read()
    latest = (
        f'"**RAW {raw} · DOC {doc} · CONST {const} · tổng {total}**",\n'
        f"      ({raw}, {doc}, {const}, {total}), raw_audit_counts"
    )
    new, n = RB1_PAT.subn(lambda m: latest, body)
    if n != 1:
        print("CẢNH BÁO: không tìm thấy đúng 1 claim RB1 để đồng bộ")
    elif new != body:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new)
        print("đã đồng bộ claim RB1 trong tools/verify-claims.py")

    for rel in ("docs/spec/START_HERE.md", "docs/spec/DATA_SYNC.md", "docs/HANDOFF_REPLY_7c7c9f064.md"):
        fp = os.path.join(ROOT, rel)
        if not os.path.exists(fp):
            continue
        with open(fp, encoding="utf-8") as fh:
            text = fh.read()
        out = text
        for pat, tpl in COUNT_PATTERNS:
            out = pat.sub(lambda m, t=tpl: t.format(**vals), out)
        if out != text:
            with open(fp, "w", encoding="utf-8") as fh:
                fh.write(out)
            print(f"đã đồng bộ số claim trong {rel}")


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

    sync_rb1(counts["RAW"], counts["DOC"], counts["CONST"], total)
    print(f"RAW {counts['RAW']} · DOC {counts['DOC']} · CONST {counts['CONST']} · tổng {total}")
    print(f"đã ghi {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
