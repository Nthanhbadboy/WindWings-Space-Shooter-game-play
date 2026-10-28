#!/usr/bin/env python3
"""Turn an art_report.gd log into a per-variant slot table.

`ART_SUMMARY` is a single line that GitHub truncates in check annotations, so the
split between "art present" and "vector fallback" has to be published somewhere
readable. This tool parses the log the game itself printed and emits Markdown
plus a machine-readable count line.

Input : game/tools/art_report.gd stdout (ART_* lines)
Output: a Markdown table on stdout (or --out), one row per slot

Usage:
    python3 game/tools/art_slots_table.py --log dist/art_report.log --variant A \
        --out motion/A/ART_SLOTS.md
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SLOT_RE = re.compile(r"^ART_SLOT (\S+) (present|fallback)\b(.*)$")


def parse(log_text: str) -> tuple[list[tuple[str, bool, str]], dict]:
    rows: list[tuple[str, bool, str]] = []
    info: dict = {}
    for line in log_text.splitlines():
        line = line.strip()
        match = SLOT_RE.match(line)
        if match:
            slot, state, rest = match.groups()
            detail = rest.strip()
            if detail.startswith("vector"):
                detail = "vector fallback"
            elif detail and not detail.startswith("res://") and not detail.startswith("user://"):
                detail = detail.strip("()")
            rows.append((slot, state == "present", detail))
            continue
        if line.startswith("ART_CONTRACT "):
            info["contract"] = line
        elif line.startswith("ART_PACKAGE "):
            info["package"] = line
        elif line.startswith("ANIM_VARIANT "):
            info["variant"] = line
        elif line.startswith("ANIM_VARIANT_PLACEHOLDER "):
            info["placeholder"] = line
        elif line.startswith("ART_SUMMARY "):
            info.setdefault("summary", line)
    return rows, info


def render(rows: list[tuple[str, bool, str]], info: dict, variant: str) -> str:
    present = [row for row in rows if row[1]]
    fallback = [row for row in rows if not row[1]]
    lines = [
        f"# Art slots — ANIM-{variant}",
        "",
        f"`{info.get('variant', 'ANIM_VARIANT unknown')}`",
        "",
    ]
    if "package" in info:
        lines.append(f"`{info['package']}`")
        lines.append("")
    if "placeholder" in info:
        lines += [
            "> **Placeholder build**: no art package was supplied for this variant, so",
            "> every slot below falls back to vector art.",
            "",
        ]
    if "contract" in info:
        lines.append(f"`{info['contract']}`")
        lines.append("")
    lines += [
        f"**Present {len(present)} / {len(rows)} slots; {len(fallback)} fall back to vector art.**",
        "",
        "| Slot | Art | Detail |",
        "|---|---|---|",
    ]
    for slot, is_present, detail in rows:
        state = "present" if is_present else "**fallback**"
        lines.append(f"| `{slot}` | {state} | {detail or '—'} |")
    lines += [
        "",
        "Enemy, bullet, FX, background and menu slots have no art in the delivered",
        "packages; they are listed as fallback on purpose rather than hidden.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True)
    parser.add_argument("--variant", required=True)
    parser.add_argument("--out", default="")
    args = parser.parse_args(argv)

    log_path = Path(args.log)
    if not log_path.exists():
        print(f"missing art report log: {log_path}", file=sys.stderr)
        return 1
    rows, info = parse(log_path.read_text(encoding="utf-8", errors="replace"))
    if not rows:
        print("the art report log lists no slots", file=sys.stderr)
        return 1

    present = sum(1 for row in rows if row[1])
    fallback = len(rows) - present
    text = render(rows, info, args.variant)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    else:
        print(text)
    print(f"ART_TABLE variant={args.variant} total={len(rows)} present={present} fallback={fallback}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
