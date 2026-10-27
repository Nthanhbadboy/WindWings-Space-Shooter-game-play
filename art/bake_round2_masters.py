#!/usr/bin/env python3
"""Bake the new painted commercial masters used by the audit response.

Raw inputs are branch-owned AI-painted sources in masters/_raw, never original
APK/GCenter art. The baked transparent masters are the only runtime art inputs.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "art"))
from commercial_raw import extract_painted
from PIL import Image, ImageDraw, ImageFilter


def main():
    jobs = []
    for idx in (8, 12, 13):
        jobs.append((
            ROOT / f"art/w1-player-b/masters/_raw/ship_{idx:02d}_raw.png",
            ROOT / f"art/w1-player-b/masters/hero_painted_{idx:02d}_1024.png",
            dict(fill=0.88),
        ))
    for idx in (4, 5):
        jobs.append((
            ROOT / f"art/w1-player-b/masters/_raw/drone_{idx:02d}_raw.png",
            ROOT / f"art/w1-player-b/masters/drone_painted_{idx:02d}_1024.png",
            dict(fill=0.86),
        ))
    for gid in (7001, 7002, 7003, 7004):
        jobs.append((
            ROOT / f"art/w3-boss-b/masters/_raw/boss_{gid}_raw.png",
            ROOT / f"art/w3-boss-b/masters/boss_painted_{gid}_1024.png",
            dict(fill=0.90),
        ))
    jobs.append((
        ROOT / "art/w3-boss-b/masters/_raw/boss_7005_raw.png",
        ROOT / "art/w3-boss-b/masters/boss_painted_7005_1024.png",
        dict(fill=0.90, crop_box=(300, 180, 1110, 768), cut_black=True, keep_largest=True, widen=0.78),
    ))
    for source, target, kwargs in jobs:
        target.parent.mkdir(parents=True, exist_ok=True)
        im = extract_painted(str(source), canvas=1024, **kwargs)
        if "boss_7005" in source.name:
            # Remove the surrounding generated ring fragments while retaining
            # the complete central fortress and its two forward cannon barrels.
            mask = Image.new("L", im.size, 0)
            md = ImageDraw.Draw(mask)
            md.ellipse((40, 110, 984, 740), fill=255)
            md.rectangle((280, 560, 744, 880), fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(1.2))
            alpha = im.getchannel("A")
            from PIL import ImageChops
            im.putalpha(ImageChops.multiply(alpha, mask))
        im.save(target, "PNG", optimize=True)
        print(f"{target.relative_to(ROOT)} <- {source.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
