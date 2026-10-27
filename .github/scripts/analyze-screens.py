#!/usr/bin/env python3
"""analyze-screens.py — turn probe screenshots into numbers a report can argue with.

    analyze-screens.py <dir-with-screen-*.jpg>

Prints a small table:

    file  WxH  mean  dark%  colors  vs-prev%

`mean` is average luminance (0–255). `dark%` is the share of pixels below 20.
`colors` counts distinct colours after 4-bit quantisation — a black or uniform
frame collapses to a handful, a rendered game or launcher has hundreds.
`vs-prev%` is the mean absolute difference against the previous shot: 0 % means
the screen never moved.

Why: "the app did not start" cannot be inferred from logcat when the transport
only returns the `system` buffer, and a screenshot that differs between two calls
proves the device display is live. These numbers separate a black screen from a
rendered one without shipping the image anywhere.

Exit code is always 0 — this is evidence, not a gate. Missing Pillow degrades to
a byte-level summary rather than failing the job.
"""

import glob
import os
import sys

try:
    from PIL import Image, ImageChops, ImageStat
except ImportError:  # pragma: no cover - runner without Pillow
    Image = None


def quantised_colours(img, bits=4):
    small = img.convert("RGB").resize((96, 96))
    seen = set()
    for r, g, b in small.getdata():
        seen.add((r >> bits, g >> bits, b >> bits))
    return len(seen)


def main() -> int:
    d = sys.argv[1] if len(sys.argv) > 1 else "."
    files = sorted(glob.glob(os.path.join(d, "screen-*.jpg")))
    if not files:
        print("(no screenshots)")
        return 0

    print("file                 WxH        mean  dark%  colors  vs-prev%")
    prev = None
    for f in files:
        name = os.path.basename(f)
        size = os.path.getsize(f)
        if Image is None:
            print(f"{name:<20} {size:>7} B   (Pillow missing: byte count only)")
            continue
        try:
            img = Image.open(f).convert("RGB")
        except Exception as exc:  # noqa: BLE001
            print(f"{name:<20} unreadable: {exc}")
            continue

        stat = ImageStat.Stat(img.convert("L"))
        mean = stat.mean[0]
        hist = img.convert("L").histogram()
        total = sum(hist) or 1
        dark = sum(hist[:20]) * 100.0 / total

        diff = ""
        if prev is not None:
            delta = ImageChops.difference(prev, img)
            dstat = ImageStat.Stat(delta)
            diff = f"{sum(dstat.mean) / 3.0 * 100.0 / 255.0:8.2f}"
        else:
            diff = "       —"

        print(
            f"{name:<20} {img.width:>4}x{img.height:<4} "
            f"{mean:6.1f} {dark:5.1f} {quantised_colours(img):7d} {diff}"
        )
        prev = img

    if Image is not None and len(files) >= 2:
        print()
        print("reading: mean < 8 and dark% > 90 ⇒ black frame (nothing rendered).")
        print("         colors < 12 ⇒ uniform frame. vs-prev% ≈ 0 ⇒ screen never changed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
