#!/usr/bin/env python3
"""Dựng **timeline animation** của enemy/boss từ event clip đã giải mã.

Nguồn duy nhất: `reverse-engineering/raw/animation-audit/event-receivers.json.gz`
(795 event · 34 prefab · 97 clip). Mỗi event có `time` (giây, đúng thời điểm trong clip),
`clip_name` và `functionName` — tên hàm C# mà AnimationEvent gọi.

Đây là thứ biến "animation" thành **script**: biết lúc nào boss gọi `StartAttack8`,
lúc nào `StopAttack8`, nên dựng lại được **cửa sổ gây sát thương** và **nhịp ra đòn**.

Ví dụ
-----
    python3 tools/boss-anim-timeline.py --stats
    python3 tools/boss-anim-timeline.py --prefab Boss-39012
    python3 tools/boss-anim-timeline.py --prefab Boss-39012 --clip attack1
    python3 tools/boss-anim-timeline.py --doc Boss-39012 Boss-39019   # markdown
    python3 tools/boss-anim-timeline.py --csv datas/boss_anim_events.csv
"""
import argparse
import collections
import csv
import gzip
import json
import re
import statistics
import sys

SRC = "reverse-engineering/raw/animation-audit/event-receivers.json.gz"


def load(src=SRC):
    with gzip.open(src, "rt", encoding="utf-8") as fh:
        return json.load(fh)["events"]


def by_prefab(events, prefab):
    return [e for e in events if e["prefab"] == prefab]


def groups(events):
    """{(prefab, clip): [(time, functionName), ...]} đã sắp theo thời gian."""
    g = collections.defaultdict(list)
    for e in events:
        g[(e["prefab"], e["clip_name"])].append(
            (round(e["event"]["time"], 2), e["event"]["functionName"])
        )
    for k in g:
        g[k].sort()
    return g


def attack_windows(events):
    """Cặp `StartX` → `StopX` cùng clip: (prefab, clip, tên, giây)."""
    slot = collections.defaultdict(dict)
    for e in events:
        m = re.match(r"^(Start|Stop)(\w+)$", e["event"]["functionName"])
        if m:
            key = (e["prefab"], e["clip_name"], m.group(2))
            slot[key][m.group(1)] = e["event"]["time"]
    out = []
    for (p, c, suf), t in slot.items():
        if "Start" in t and "Stop" in t:
            out.append((p, c, suf, round(t["Stop"] - t["Start"], 2)))
    return sorted(out, key=lambda r: -r[3])


def stats(events):
    per = collections.Counter(e["prefab"] for e in events)
    fn = collections.Counter(e["event"]["functionName"] for e in events)
    g = groups(events)
    lasts = [v[-1][0] for v in g.values()]
    hits = []
    for k, v in g.items():
        ts = [t for t, f in v if f.startswith(("AttackHand", "Shoot", "Ban"))]
        hits += [round(b - a, 2) for a, b in zip(ts, ts[1:])]
    return {
        "prefab": len(per),
        "event": len(events),
        "clip": len({e["clip_name"] for e in events}),
        "pair": len(g),
        "fn": len(fn),
        "per_prefab": per,
        "top_fn": fn,
        "last_median": statistics.median(lasts),
        "hit_n": len(hits),
        "hit_median": statistics.median(hits) if hits else 0.0,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--prefab")
    ap.add_argument("--clip")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--doc", nargs="+", metavar="PREFAB")
    ap.add_argument("--detail", nargs="+", metavar="PREFAB")
    ap.add_argument("--csv")
    a = ap.parse_args(argv)

    events = load(a.src)

    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["prefab", "clip", "time", "function", "data", "float", "int"])
            for e in sorted(events, key=lambda e: (e["prefab"], e["clip_name"], e["event"]["time"])):
                ev = e["event"]
                w.writerow([e["prefab"], e["clip_name"], round(ev["time"], 3),
                            ev["functionName"], ev["data"], ev["floatParameter"],
                            ev["intParameter"]])
        print(f"đã ghi {len(events)} event → {a.csv}", file=sys.stderr)
        if not (a.stats or a.doc or a.prefab):
            return 0

    if a.stats:
        s = stats(events)
        print(f"prefab {s['prefab']} · event {s['event']} · clip {s['clip']} · "
              f"cặp (prefab,clip) {s['pair']} · tên hàm {s['fn']}")
        print(f"mốc cuối clip: trung vị {s['last_median']:.2f}s · "
              f"nhịp multi-hit: {s['hit_n']} khoảng, trung vị {s['hit_median']:.2f}s")
        print("event / prefab:", s["per_prefab"].most_common(10))
        print("hàm nhiều nhất:", s["top_fn"].most_common(6))
        for p, c, suf, sec in attack_windows(events):
            print(f"cửa sổ {p} {c} {suf}: {sec}s")

    if a.prefab:
        for clip, seq in sorted(groups(by_prefab(events, a.prefab)).items()):
            if a.clip and a.clip not in clip[1]:
                continue
            print(f"\n{clip[0]} · {clip[1]}  ({len(seq)} event)")
            for t, f in seq:
                print(f"  {t:6.2f}s  {f}")

    if a.detail:
        for p in a.detail:
            print(f"\n### `{p}` — {len(by_prefab(events, p))} event · "
                  f"{len(groups(by_prefab(events, p)))} clip\n")
            print("| Clip | # | Timeline (`giây` → hàm) |")
            print("|---|---:|---|")
            for (_, c), v in sorted(groups(by_prefab(events, p)).items(),
                                    key=lambda kv: kv[1][0][0]):
                tl = " · ".join(f"`{t:g}` {f}" for t, f in v)
                print(f"| `{c}` | {len(v)} | {tl} |")

    if a.doc:
        print(f"| Boss | Event | Clip | Mốc cuối | Chuỗi đòn (thời điểm giây) |")
        print("|---|---:|---:|---:|---|")
        for p in a.doc:
            g = groups(by_prefab(events, p))
            seqs = []
            for (_, c), v in sorted(g.items(), key=lambda kv: kv[1][0][0]):
                seqs.append(f"`{c}` " + "·".join(f"{t:g}" for t, _ in v[:6]))
            print(f"| `{p}` | {len(by_prefab(events, p))} | {len(g)} | "
                  f"{max(v[-1][0] for v in g.values()):g}s | " + "<br>".join(seqs) + " |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
