#!/usr/bin/env python3
"""Refresh wave manifests from the actual current JSON/CSV exports.

Keeps metadata and audit caveats next to the art instead of leaving stale
pass-1 numbers or claiming runtime approval.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
BRANCH = "arena/eca8588b-windwings-space-shooter-game-p"
LICENSE = "chờ user xác nhận quyền tên/art (Phase C USER-ONLY #3)"


def write_wave(wave, title, json_name, extra):
    folder = ROOT / "art" / wave
    records = json.loads((folder / json_name).read_text(encoding="utf-8"))
    lines = [f"# {title} — current audit-response manifest", "",
             f"- **Role / Branch:** Art-designer-B · `{BRANCH}`",
             f"- **License:** `{LICENSE}` · **Author:** `{BRANCH}`",
             "- **Status:** static inventory + visual evidence only; Art-style-auditor Layer-2 and runtime acceptance remain pending.",
             f"- **Records:** **{len(records)}** · metadata columns: `source`, `file`, `license`, `author`, `recipe`.", ""]
    lines += extra + ["", "| # | Row ID | Variant | Sprite | Master | Delivered px | Recipe | Val | Chroma |", "|---:|---|---|---|---|---|---|---:|---:|"]
    for i, r in enumerate(records, 1):
        lines.append("| {} | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | {} | {} |".format(
            i, r.get("row_id", ""), r.get("variant", ""), r.get("file", ""), r.get("source", ""),
            r.get("delivered_px", ""), r.get("recipe", ""), r.get("val", "—"), r.get("chroma", "—")))
    manifest_names = {
        "w1-player-b": "W1B_MANIFEST.md", "w2-enemy-b": "W2B_MANIFEST.md",
        "w3-boss-b": "W3B_MANIFEST.md", "w4-core-b": "W4B_MANIFEST.md",
        "w5-full-b": "W5B_MANIFEST.md",
    }
    (folder / manifest_names[wave]).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(wave, len(records))


def main():
    write_wave("w1-player-b", "W1 PLAYER (48/48)", "w1b_units.json", [
        "- **Decoded IDs:** `datas/ships.json` / `datas/drones.json` anchors are recorded per row as `GLYPH-ship-<id>` / `GLYPH-drone-<id>`; no invented Unity binding is claimed.",
        "- **P0 hero:** `Ship 10001` (`player_ship_01`) is the hero candidate for auditor calibration; the other ships are candidates, not a self-declared lock.",
        "- **Review boards:** `preview/w1b_side_by_side_ref.png` and `../audit_a71412d_response/comparisons/01_hero_calibration.png`.",
    ])
    write_wave("w2-enemy-b", "W2 ENEMY (34/34)", "w2b_units.json", [
        "- **AP-0067:** `Enemy_Hp` is a neutral white rounded HP fill, measured as UI by the audit wrapper; it is not an enemy body or a four-pip weapon.",
        "- **Review boards:** `preview/w2b_side_by_side_ref.png` and `../audit_a71412d_response/comparisons/03_enemy_anchors.png`.",
    ])
    write_wave("w3-boss-b", "W3 BOSS (42/42)", "w3b_units.json", [
        "- **Decoded boss mapping:** `GLYPH-boss-7001..7005` maps to `bosses-01.jpg #2..#6` through `datas/bosses.json` + `docs/assets/sprites-index.csv`; the board builder no longer uses row-index guessing.",
        "- **Review boards:** `preview/w3b_side_by_side_ref.png` and `../audit_a71412d_response/comparisons/02_boss_decoded_ids.png`.",
        "- **Runtime:** destructible parts, pivots, Spine/scene placement and animation are not verified by these static PNGs.",
    ])
    write_wave("w4-core-b", "W4 CORE (114 files / 112 planner rows)", "w4b_units.json", [
        "- **Background correction:** `bg_parallax_01_sky_far` is grounded dark cobalt so foreground characters retain the value/saturation hierarchy.",
        "- **9-slice:** static three-size probe is in `../audit_a71412d_response/nine_slice_contract.csv`; this is not an engine integration test.",
    ])
    write_wave("w5-full-b", "W5 FULL (274/274)", "w5b_units.json", [
        "- **Semantic corrections:** `ShopIcon`, `nennutevent`, `Blink`, `Goicoin1`, `CoinIcon`, and tech-node slots have separate function-specific art instead of a shared generic star/coin badge.",
        "- **Duplicate hashes:** remaining duplicate groups are inventoried in `../audit_a71412d_response/static_validation.json`; intentional frame reuse still needs integration review, not an automatic defect claim.",
        "- **Review board:** `../audit_a71412d_response/comparisons/04_w5_semantics.png`.",
    ])

    folder = ROOT / "art/w0-listing-b"
    records = json.loads((folder / "w0b_exports.json").read_text(encoding="utf-8"))
    lines = ["# W0 STORE LISTING — current audit-response manifest", "",
             f"- **Role / Branch:** Art-designer-B · `{BRANCH}`",
             f"- **License:** `{LICENSE}` · **Author:** `{BRANCH}`",
             "- **Contract:** exact 25 slot filenames, pixel dimensions and RGB/RGBA modes retained.",
             "- **S1–S4 status:** **CONCEPT composites from current Variant-B sprites, not Godot/runtime captures**. Recapture from the real release build before any store submission; do not upload these as claimed screenshots.",
             "- **Static result:** `../audit_a71412d_response/static_validation.json` reports 25/25 contract slots and zero static errors.",
             "", "| # | Store slot | File | Px | Mode | Source master | Recipe | Note |", "|---:|---|---|---|---|---|---|---|"]
    for i, r in enumerate(records, 1):
        lines.append(f"| {i} | `{r['slot']}` | `{r['file']}` | `{r['px']}` | `{r['mode']}` | `{r['source']}` | `{r['recipe']}` | {r.get('note','')} |")
    (folder / "W0B_MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("w0-listing-b", len(records))


if __name__ == "__main__": main()
