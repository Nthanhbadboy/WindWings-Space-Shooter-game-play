#!/usr/bin/env python3
"""Turn captured PNG frames into the motion-acceptance evidence.

Input : a frame folder per segment (`<frames>/<segment>/frame_0000.png` + frames.txt)
Output: `motion/<segment>.gif`, `motion/<segment>-sheet.png` (frame strip),
        `motion/README.md` with per-segment frame counts and simulated time.

Usage: python3 game/tools/build_motion_gifs.py --frames /abs/frames --out /abs/motion
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover - CI installs Pillow
    print("Pillow is required: python3 -m pip install pillow", file=sys.stderr)
    raise

MAX_WIDTH = 288
SHEET_COLUMNS = 8


def load_segment(folder: Path) -> tuple[list[Image.Image], list[float]]:
    frames: list[Image.Image] = []
    times: list[float] = []
    manifest = folder / "frames.txt"
    if manifest.exists():
        for line in manifest.read_text().splitlines():
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) == 2:
                times.append(float(parts[1]))
    for path in sorted(folder.glob("frame_*.png")):
        image = Image.open(path).convert("RGB")
        if image.width > MAX_WIDTH:
            ratio = MAX_WIDTH / image.width
            image = image.resize((MAX_WIDTH, int(image.height * ratio)), Image.LANCZOS)
        frames.append(image)
    return frames, times


def build_gif(frames: list[Image.Image], out_path: Path, fps: float) -> None:
    if not frames:
        raise SystemExit(f"no frames for {out_path}")
    duration = max(1, int(round(1000.0 / max(fps, 1.0))))
    paletted = [frame.convert("P", palette=Image.ADAPTIVE, colors=128) for frame in frames]
    paletted[0].save(
        out_path,
        save_all=True,
        append_images=paletted[1:],
        duration=duration,
        loop=0,
        optimize=True,
        disposal=2,
    )


def build_sheet(frames: list[Image.Image], out_path: Path, columns: int = SHEET_COLUMNS) -> None:
    if not frames:
        return
    width, height = frames[0].size
    rows = (len(frames) + columns - 1) // columns
    sheet = Image.new("RGB", (width * columns, height * rows), (8, 12, 24))
    for index, frame in enumerate(frames):
        sheet.paste(frame, ((index % columns) * width, (index // columns) * height))
    sheet.save(out_path, optimize=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--fps", type=float, default=12.0)
    args = parser.parse_args()

    frames_root = Path(args.frames)
    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Motion evidence — launch slice",
        "",
        "Frames rendered from the real scenes by `game/tools/motion_capture.gd` on the CI",
        "runner (xvfb + llvmpipe, `--fixed-fps 60`, captured at the frame rate below).",
        "Each GIF is the acceptance clip; the `-sheet.png` file is the same frames laid out",
        "in order, so the motion can be read without playing the GIF.",
        "",
        f"- Capture rate: {args.fps:g} fps",
        f"- Frame width: {MAX_WIDTH}px",
        "",
        "| Segment | Frames | Simulated seconds | GIF | Frame sheet |",
        "|---|---:|---:|---|---|",
    ]
    summary = []
    for folder in sorted(p for p in frames_root.iterdir() if p.is_dir()):
        frames, times = load_segment(folder)
        if not frames:
            continue
        gif_path = out_root / f"{folder.name}.gif"
        sheet_path = out_root / f"{folder.name}-sheet.png"
        build_gif(frames, gif_path, args.fps)
        build_sheet(frames, sheet_path)
        seconds = times[-1] if times else len(frames) / args.fps
        summary.append((folder.name, len(frames), seconds, gif_path, sheet_path))
        lines.append(
            f"| {folder.name} | {len(frames)} | {seconds:.2f} | `{gif_path.name}` | `{sheet_path.name}` |"
        )
    lines += [
        "",
        "Scenes: `hangar` = ship idle animation, `flight` = ship gliding and firing,",
        "`boss` = boss descent and the Attack2 volley.",
        "",
    ]
    (out_root / "README.md").write_text("\n".join(lines), encoding="utf-8")

    for name, frames, seconds, gif_path, sheet_path in summary:
        print(
            f"MOTION_GIF {name} frames={frames} seconds={seconds:.2f} "
            f"gif={gif_path.stat().st_size}B sheet={sheet_path.stat().st_size}B"
        )
    if not summary:
        print("MOTION_GIF none", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
