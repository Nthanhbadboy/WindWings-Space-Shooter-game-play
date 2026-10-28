#!/usr/bin/env python3
"""Cập nhật cột `N dòng · M bảng` trong bảng tài liệu của docs/spec/README.md.

Vì sao có file này: claim RD1 đo lại đúng 2 con số đó cho 39 file, nên mỗi lần sửa
một tài liệu mà quên cập nhật README là docs-verify đỏ. Chạy tay sau mỗi lần sửa;
`--check` để chỉ báo lệch mà không ghi (CI dùng được).

Bảng đếm theo dòng bắt đầu bằng `|---` — cùng định nghĩa với `readme_sizes()`
trong tools/verify-claims.py.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "docs/spec/README.md"
PAT = re.compile(r"`([A-Za-z_0-9./-]+\.md)`.*?(\d+) dòng · (\d+) bảng")


def measure(name: str):
    rel = name if "/" in name else "docs/spec/" + name
    body = (ROOT / rel).read_text(encoding="utf-8").splitlines()
    return len(body), sum(1 for line in body if line.lstrip().startswith("|---"))


def main() -> int:
    check = "--check" in sys.argv
    text = README.read_text(encoding="utf-8")
    drift = []

    def sub(m):
        name = m.group(1)
        want = (int(m.group(2)), int(m.group(3)))
        got = measure(name)
        if want != got:
            drift.append((name, want, got))
            return m.group(0).replace(
                f"{m.group(2)} dòng · {m.group(3)} bảng", f"{got[0]} dòng · {got[1]} bảng"
            )
        return m.group(0)

    new = PAT.sub(sub, text)
    for name, want, got in drift:
        print(f"{name}: README {want[0]} dòng/{want[1]} bảng → thật {got[0]}/{got[1]}")
    if check:
        print(f"{len(drift)} lệch")
        return 1 if drift else 0
    if drift:
        README.write_text(new, encoding="utf-8")
        print(f"đã cập nhật {len(drift)} dòng trong {README.relative_to(ROOT)}")
    else:
        print("không lệch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
