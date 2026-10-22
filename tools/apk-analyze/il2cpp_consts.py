#!/usr/bin/env python3
"""Pull numeric constants out of IL2CPP method bodies.

The designer values for `Player_Get_Datas`, `Droid_Data_Balance`, `Tech_Datas`,
`Stage_Get_Datas`, `Enemy_Data_Balance`, `Device_Get_Data`, `GameDatas`,
`ArenaManager`, `RankManager` are **not serialized** anywhere in `data.unity3d`
(0 instances). They live in the method bodies of `libil2cpp.so`.

`dump.cs` gives every method an `Offset:` (file offset in the .so). We disassemble
that range with capstone and collect:

* float literals loaded from the literal pool  -> `ldr s0, [pc, #imm]`
* VFP immediates                              -> `fmov s0, #1.5`
* integer constants                           -> `movz/movk`, `mov w0, #N`, `orr`
* constants passed through `ldrsw`/`ldr` of a literal (ints)

Raw output (keep everything):
    reverse-engineering/raw/il2cpp-consts/<Class>.json       per class, every method
    reverse-engineering/raw/il2cpp-consts/<Class>.asm.txt    annotated disassembly
    docs/apk-analysis/19-il2cpp-constants.md                 readable summary

Usage:
    python3 tools/apk-analyze/il2cpp_consts.py [dump.cs] [libil2cpp.so]
"""
from __future__ import annotations

import json
import os
import re
import struct
import sys
from collections import Counter, defaultdict

DUMP = os.environ.get("IL2CPP_DUMP", "/tmp/apk/il2cpp/dump.cs")
SO = os.environ.get("IL2CPP_SO", "/tmp/apk/extract/libil2cpp.so")
OUT_RAW = os.environ.get("CONSTS_RAW", "reverse-engineering/raw/il2cpp-consts")
OUT_MD = os.environ.get("CONSTS_MD", "docs/apk-analysis/19-il2cpp-constants.md")

TARGET_CLASSES = {
    "Player_Get_Datas": "chỉ số tàu: HP, damage, tốc độ bắn, giá nâng cấp",
    "Droid_Data_Balance": "drone: damage, timeout, giá unlock/upgrade",
    "Tech_Datas": "tech lab: giá, delta giá, sao",
    "Stage_Get_Datas": "stage: bonus, delta level/coin/gem, số enemy",
    "Map_Get_Datas": "map: wave, danh sách map theo mode",
    "Enemy_Data_Balance": "enemy: bonus coin/exp, điểm survival/arena/pvp",
    "Device_Get_Data": "device: stat, giá",
    "GameDatas": "cờ save/anti-cheat, cheat counters",
    "ArenaManager": "arena: rank, mùa, thưởng",
    "RankManager": "rank: ngưỡng điểm, thời gian",
    "Player_Datas": "dữ liệu runtime của player",
    "IAP_Manager": "giá và product id runtime",
}

RVA_RE = re.compile(r"//\s*RVA:\s*0x([0-9A-Fa-f]+)\s+Offset:\s*0x([0-9A-Fa-f]+)")
CLASS_RE = re.compile(r"^(?:public|internal|private|protected)?\s*(?:sealed\s+|abstract\s+|static\s+)*"
                      r"(class|struct|interface)\s+([\w\.`<>]+)")
NS_RE = re.compile(r"^// Namespace:\s*(.*)$")


# --------------------------------------------------------------------- dump.cs
def parse_dump(path):
    """[(class, namespace, method_name, offset, rva, signature)]"""
    methods = []
    cls = ns = None
    pending = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            m = NS_RE.match(line)
            if m:
                ns = m.group(1).strip()
                continue
            m = CLASS_RE.match(line.strip())
            if m and not line.startswith("\t") and not line.startswith(" "):
                name = m.group(2)
                cls = name.split(".")[-1] if "." in name else name
                # nested classes come as Outer.Inner; keep the outer name too
                if "." in name:
                    cls = name
                continue
            m = RVA_RE.search(line)
            if m:
                pending = (int(m.group(1), 16), int(m.group(2), 16))
                continue
            if pending and line.strip() and not line.strip().startswith("//"):
                sig = line.strip()
                name = sig
                pm = re.search(r"([A-Za-z_<>.][\w<>,\.\[\]]*)\s*\(", sig)
                if pm:
                    name = pm.group(1).split(".")[-1]
                methods.append((cls, ns, name, pending[1], pending[0], sig))
                pending = None
    return methods


# --------------------------------------------------------------------- ELF/so
def elf_machine(path):
    with open(path, "rb") as f:
        head = f.read(20)
    if head[:4] != b"\x7fELF":
        return None
    return struct.unpack("<H", head[18:20])[0]


def read_at(f, off, n):
    f.seek(off)
    return f.read(n)


# ------------------------------------------------------------------ disassembly
def _as_float(u32: int):
    """Interpret a 32-bit immediate as IEEE-754 float; return it if it looks real."""
    try:
        val = struct.unpack("<f", struct.pack("<I", u32 & 0xFFFFFFFF))[0]
    except Exception:  # noqa: BLE001
        return None
    if val != val or abs(val) == float("inf") or val == 0.0:
        return None
    if abs(val) > 1e9 or abs(val) < 1e-6:
        return None
    return round(val, 6)


def constants_in(code_off, size, blob, md):
    """Return (consts, asm_lines) for one method body."""
    import capstone

    if md == 0xB7:
        cs = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
        sreg = "s"
    else:
        cs = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM | capstone.CS_MODE_THUMB)
        sreg = "s"
    cs.detail = True
    consts, lines = [], []
    chunk = blob[code_off:code_off + size]
    insns = list(cs.disasm(chunk, code_off))
    pending_floats: list = []
    emitted: set = set()
    for insn in insns:
        text = f"{insn.address:#x}: {insn.mnemonic:8s} {insn.op_str}"
        lines.append(text)
        # ---- float loaded from the literal pool: ldr sN, [pc, #imm]
        if insn.mnemonic == "ldr" and "[pc," in insn.op_str and md == 0xB7:
            m = re.search(r"\[pc, #(-?0x[0-9a-f]+|-?\d+)\]", insn.op_str)
            dst = insn.op_str.split(",")[0].strip()
            if m and dst.startswith("s"):
                raw = int(m.group(1), 0)
                target = insn.address + raw
                if 0 <= target <= len(blob) - 4:
                    val = struct.unpack("<f", blob[target:target + 4])[0]
                    if val == val and abs(val) < 1e12:      # skip NaN/inf
                        consts.append({"kind": "float", "value": round(val, 6),
                                       "via": "ldr", "addr": hex(insn.address)})
        # ---- VFP immediate: fmov s0, #1.5
        if insn.mnemonic.startswith("fmov") and "#" in insn.op_str:
            m = re.search(r"#(-?\d+(?:\.\d+)?)", insn.op_str)
            dst = insn.op_str.split(",")[0].strip()
            if m and dst.startswith("s"):
                consts.append({"kind": "float", "value": float(m.group(1)),
                               "via": "fmov", "addr": hex(insn.address)})
        # ---- float materialised through an int register:
        #        mov w8, #0x42c80000 ; fmov s1, w8   -> 100.0f
        if insn.mnemonic in ("mov", "movz") and md == 0xB7:
            m = re.search(r"#(0x[0-9a-fA-F]{6,8})$", insn.op_str)
            dst = insn.op_str.split(",")[0].strip()
            if m and dst.startswith("w"):
                bits = int(m.group(1), 16)
                probe = _as_float(bits)
                if probe is not None:
                    pending_floats.append({"reg": dst, "value": probe,
                                           "addr": hex(insn.address), "bits": hex(bits)})
                    continue
        # ---- integer immediates
        if insn.mnemonic in ("mov", "movz", "movn", "orr", "and", "cmp", "add", "sub", "movk"):
            m = re.search(r"#(0x[0-9a-fA-F]+|\d+)(?:, lsl #\d+)?$", insn.op_str)
            if m:
                val = int(m.group(1), 0)
                if 0 < val < (1 << 32):
                    consts.append({"kind": "int", "value": val,
                                   "via": insn.mnemonic, "addr": hex(insn.address),
                                   "reg": insn.op_str.split(",")[0].strip(),
                                   "op": insn.op_str})
    # `mov w1, #0xd87 ; movk w1, #1, lsl #16` -> 69007, not 3463.
    # Without this the high half is dropped and the number silently lies.
    merged = []
    by_reg = {}
    for c in consts:
        reg = c.get("reg")
        if c["kind"] == "int" and c["via"] in ("mov", "movz") and reg:
            by_reg[reg] = c
            merged.append(c)
        elif c["kind"] == "int" and c["via"] == "movk" and reg in by_reg:
            base = by_reg[reg]
            shift = 16
            m = re.search(r"lsl #(\d+)", c.get("op", ""))
            if m:
                shift = int(m.group(1))
            base["value"] = (base["value"] & ~(0xFFFF << shift)) | \
                            ((c["value"] & 0xFFFF) << shift)
            base["via"] = "mov+movk"
            base["note"] = "ghép 2 lệnh — có thể là metadata token/độ dài, không chắc là số thiết kế"
        else:
            merged.append(c)
    consts[:] = merged

    # a float bit-pattern only counts once we see `fmov sN, wReg`
    for pf in pending_floats:
        hit = False
        for insn in insns:
            if insn.mnemonic == "fmov" and insn.op_str.replace(" ", "").endswith(
                    "," + pf["reg"]):
                key = (pf["value"], pf["addr"])
                if key in emitted:
                    hit = True
                    break
                emitted.add(key)
                consts.append({"kind": "float", "value": pf["value"], "via": "mov+fmov",
                               "bits": pf["bits"], "addr": pf["addr"]})
                hit = True
                break
        if not hit:
            consts.append({"kind": "int", "value": int(pf["bits"], 16), "via": "mov",
                           "bits": pf["bits"], "addr": pf["addr"],
                           "note": "bit-pattern giống float nhưng không thấy fmov — để riêng"})
    return consts, lines


ARITH = ("fmul", "fadd", "fsub", "fdiv", "fnmul", "fmsub", "fmadd", "scvtf", "ucvtf")
CMP = ("cmp", "cmn", "fcmp", "fcmpe", "b.lt", "b.le", "b.gt", "b.ge", "b.hi", "b.ls")


def annotate(insn_text: str, consts: list) -> None:
    """Tag each constant with how the code uses it (return / arith / compare)."""
    lines = insn_text.split("\n")
    for c in consts:
        addr = c["addr"]
        idx = next((i for i, l in enumerate(lines) if l.startswith(addr + ":")), None)
        if idx is None:
            continue
        window = lines[idx:idx + 4]
        prev = lines[max(0, idx - 2):idx]
        if c["kind"] == "float":
            reg = None
            for l in [lines[idx]]:
                head = l.split(":", 1)[-1].strip()
                reg = head.split()[1].split(",")[0] if len(head.split()) > 1 else None
            if reg:
                for l in lines[idx + 1:idx + 12]:
                    body = l.split(":", 1)[-1].strip()
                    if any(body.startswith(m) for m in ARITH) and reg in body:
                        c["role"] = "arith:" + body.split()[0]
                        break
            c.setdefault("role", "load")
        else:
            body = lines[idx].split(":", 1)[-1].strip()
            if body.startswith(("cmp", "cmn", "tbnz", "tbz", "cbz", "cbnz")):
                c["role"] = "compare"
            elif body.startswith(("mul", "madd", "msub", "lsl", "lsr", "sdiv", "udiv")):
                c["role"] = "arith:" + body.split()[0]
            elif any(l.split(":", 1)[-1].strip().startswith("ret") for l in window):
                c["role"] = "return"
            else:
                c["role"] = "other"


PROLOGUE = ("sub ", "stp ", "ldp ", "add sp", "mov x29", "str x30", "ret", "nop")


def getter_kind(insn_text: str):
    """Classify a property getter.

    Every getter in this build is wrapped in the IL2CPP static-init guard
    (`ldrb w8,[guard]; tbnz w8,#0,tail; bl <init>; strb; <tail>`), so the old
    "<=8 instructions, one load" test never matched anything. We cut the guard
    and look at the tail instead:

    * ``const`` — tail is ``mov w0, #imm`` / ``fmov s0, #imm`` -> design constant
    * ``field`` — tail is a chain of loads into w0          -> live data (save/db)
    * ``None``  — anything else (arithmetic, calls)
    """
    body = [l.split(":", 1)[-1].strip() for l in insn_text.split("\n") if l.strip()]
    body = [l for l in body if not l.startswith(PROLOGUE)]
    if not body:
        return None
    # cut the static-init guard at the last guard marker (`strb` writing the flag)
    cut = max((i for i, l in enumerate(body) if l.startswith("strb")), default=-1)
    tail = body[cut + 1:]
    if not tail:
        return None
    tail = [l for l in tail if not l.startswith(("adrp", "mov x0, xzr", "mov x1, xzr"))]
    if any(re.match(r"(mov|fmov|movz)\s+(w0|s0),\s*#", l) for l in tail):
        return "const"
    if any(re.match(r"(add|sub|mul|madd|msub|fadd|fsub|fmul|fdiv|scvtf|fcvtzs|cmp|csel)\b", l)
           for l in tail):
        return "computed"
    if any(l.startswith("b ") for l in tail):
        return "call"
    if any(re.match(r"ldr\s+(w0|s0),", l) for l in tail):
        return "field"
    return None


def is_pure_getter(insn_text: str) -> bool:
    return getter_kind(insn_text) == "const"


def main() -> int:
    dump_path = sys.argv[1] if len(sys.argv) > 1 else DUMP
    so_path = sys.argv[2] if len(sys.argv) > 2 else SO
    for p in (dump_path, so_path):
        if not os.path.isfile(p):
            print(f"missing {p}")
            return 0

    md = elf_machine(so_path)
    print(f"ELF machine: {hex(md) if md else 'unknown'} ({'aarch64' if md == 0xB7 else 'arm'})")
    methods = parse_dump(dump_path)
    print(f"methods parsed: {len(methods)}")

    wanted = defaultdict(list)
    for cls, ns, name, offset, rva, sig in methods:
        if cls in TARGET_CLASSES or (ns and ns.split(".")[-1] in TARGET_CLASSES):
            wanted[cls].append((name, offset, rva, sig))
    total = sum(len(v) for v in wanted.values())
    print(f"methods in target classes: {total} across {len(wanted)} classes")

    os.makedirs(OUT_RAW, exist_ok=True)
    summary = {}
    with open(so_path, "rb") as f:
        blob = f.read()                     # read the .so once (45 MB) — never per method
        for cls, entries in sorted(wanted.items()):
            entries.sort(key=lambda e: e[1])
            offsets = [e[1] for e in entries]
            out = []
            asm_out = []
            for i, (name, offset, rva, sig) in enumerate(entries):
                nxt = offsets[i + 1] if i + 1 < len(offsets) else offset + 0x400
                size = min(max(nxt - offset, 8), 0x1200)     # cap 4.5 KB / method
                if offset <= 0 or size <= 0:
                    continue
                consts, lines = constants_in(offset, size, blob, md or 0xB7)
                annotate("\n".join(lines), consts)
                body_text = "\n".join(lines)
                pure = is_pure_getter(body_text)
                gkind = getter_kind(body_text)
                out.append({"method": name, "signature": sig, "offset": hex(offset),
                            "rva": hex(rva), "bytes": size, "pure_getter": pure,
                            "getter_kind": gkind,
                            "constants": consts})
                if consts:
                    asm_out.append(f";;; {name}  {sig}")
                    asm_out += [f"    {l}" for l in lines]
                    asm_out.append("")
            name_safe = re.sub(r"[^\w.]", "_", cls)
            with open(os.path.join(OUT_RAW, f"{name_safe}.json"), "w", encoding="utf-8") as fh:
                json.dump({"class": cls, "note": TARGET_CLASSES.get(cls, ""),
                           "methods": out}, fh, ensure_ascii=False, indent=1)
            if asm_out:
                with open(os.path.join(OUT_RAW, f"{name_safe}.asm.txt"), "w", encoding="utf-8") as fh:
                    fh.write("\n".join(asm_out))
            floats = sorted({c["value"] for m in out for c in m["constants"]
                             if c["kind"] == "float" and c["value"] not in (0.0,)})
            ints = sorted({c["value"] for m in out for c in m["constants"]
                           if c["kind"] == "int" and c["value"] > 1 and not c.get("note")})
            getters = [{"method": m["method"], "signature": m["signature"],
                        "kind": m.get("getter_kind"),
                        "value": next((c["value"] for c in m["constants"]
                                       if c.get("role") == "return"), None)}
                       for m in out if m.get("getter_kind")]
            gkind = Counter(g["kind"] for g in getters)
            arith = sorted({(c.get("role"), c["value"]) for m in out for c in m["constants"]
                            if str(c.get("role", "")).startswith("arith")})
            summary[cls] = {"methods": len(out), "floats": floats[:40], "ints": ints[:40],
                            "with_constants": sum(1 for m in out if m["constants"]),
                            "getters": getters, "getter_kinds": dict(gkind),
                            "arith": arith[:60]}
            print(f"{cls:22s} {len(out):3d} methods, "
                  f"{sum(1 for m in out if m['constants']):3d} with constants")

    lines = ["# Hằng số bóc từ thân hàm IL2CPP", "",
             "> **Kết luận tạm thời.** Các giá trị dưới đây là hằng số *nhìn thấy trong mã máy*,",
             "> chưa chắc là giá trị thiết kế cuối cùng: có thể là hằng số phụ (epsilon, clamp,",
             "> hệ số nội suy), và có thể bị che bởi phép tính khác. Dùng để **đối chiếu**, không",
             "> phải để chép nguyên. Dữ liệu thô: `reverse-engineering/raw/il2cpp-consts/`.", "",
             f"- .so: `{os.path.basename(so_path)}` — {'aarch64' if md == 0xB7 else 'arm'}",
             f"- class đích: **{len(summary)}**, method: **{total}**", ""]
    lines += ["## Getter: trả hằng số hay đọc dữ liệu?", "",
              "Mỗi getter trong build này đều bị bọc bởi guard khởi tạo static của IL2CPP",
              "(`ldrb`/`tbnz` → `bl <cctor>` → `strb`), nên ta cắt guard rồi phân loại **phần đuôi**:",
              "`const` = trả ngay một số, `field` = đọc field static, `computed` = có phép tính,",
              "`call` = nhảy sang hàm khác (`b`, tail-call).", "",
              "> **Kết luận tạm thời:** nếu `const` = 0 thì bảng cân bằng **không nằm trong hằng số**",
              "> của getter, mà nằm trong dữ liệu/asset — đúng với hướng đi của repo này.", "",
              "| class | field | computed | call | const |", "|---|---:|---:|---:|---:|"]
    total_kinds: Counter = Counter()
    for cls, info in sorted(summary.items()):
        k = info.get("getter_kinds") or {}
        total_kinds.update(k)
        if not k:
            continue
        lines.append(f"| `{cls}` | {k.get('field', 0)} | {k.get('computed', 0)} | "
                     f"{k.get('call', 0)} | **{k.get('const', 0)}** |")
    lines += ["| **tổng** | "
              f"{total_kinds.get('field', 0)} | {total_kinds.get('computed', 0)} | "
              f"{total_kinds.get('call', 0)} | **{total_kinds.get('const', 0)}** |", ""]

    consts_rows = [(cls, g) for cls, info in sorted(summary.items())
                   for g in info.get("getters", []) if g.get("kind") == "const"]
    if consts_rows:
        lines += ["### Getter trả hằng số (nếu có)", "",
                  "| class | method | giá trị |", "|---|---|---:|"]
        for cls, g in consts_rows[:60]:
            lines.append(f"| `{cls}` | `{g['method']}` | {g.get('value')} |")
        lines.append("")
    lines.append("")

    for cls, info in sorted(summary.items(), key=lambda kv: -kv[1]["methods"]):
        lines += [f"## `{cls}` — {TARGET_CLASSES.get(cls, '')}", "",
                  f"- method đọc được: **{info['methods']}**, có hằng số: **{info['with_constants']}**",
                  f"- float: `{', '.join(str(x) for x in info['floats'][:24]) or '—'}`",
                  f"- int: `{', '.join(str(x) for x in info['ints'][:24]) or '—'}`",
                  f"- hằng số dùng trong phép tính: "
                  f"`{', '.join(f'{r}:{v}' for r, v in info.get('arith', [])[:24]) or '—'}`", ""]
    lines += ["## Đọc tiếp", "",
              "- Mỗi class có file JSON: `reverse-engineering/raw/il2cpp-consts/<Class>.json`",
              "  (từng method, từng hằng số, kèm địa chỉ).",
              "- Disassembly có chú thích: `<Class>.asm.txt`.",
              "- Hằng số chỉ có nghĩa khi đọc cùng control flow — file `.asm.txt` để đối chiếu.",
              ""]
    os.makedirs(os.path.dirname(OUT_MD) or ".", exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("written", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
