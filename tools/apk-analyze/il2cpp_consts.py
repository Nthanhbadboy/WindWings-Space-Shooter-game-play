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
from collections import defaultdict

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
    for insn in cs.disasm(chunk, code_off):
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
        # ---- integer immediates
        if insn.mnemonic in ("mov", "movz", "movn", "orr", "and", "cmp", "add", "sub", "movk"):
            m = re.search(r"#(0x[0-9a-fA-F]+|\d+)$", insn.op_str)
            if m:
                val = int(m.group(1), 0)
                if 0 < val < (1 << 32):
                    consts.append({"kind": "int", "value": val,
                                   "via": insn.mnemonic, "addr": hex(insn.address)})
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


def is_pure_getter(insn_text: str) -> bool:
    """Body that just returns one immediate (the classic Unity property getter)."""
    lines = [l.split(":", 1)[-1].strip() for l in insn_text.split("\n") if l.strip()]
    body = [l for l in lines if not l.startswith(("sub", "stp", "ldp", "add sp", "mov x29"))]
    if not any(l.startswith("ret") for l in body):
        return False
    if len(body) > 8:
        return False
    loads = [l for l in body if l.startswith(("adrp", "ldr x", "ldr w", "bl "))]
    return len(loads) <= 1 and any(l.startswith(("mov w0", "mov x0", "ldr s0")) for l in body)


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
                pure = is_pure_getter("\n".join(lines))
                out.append({"method": name, "signature": sig, "offset": hex(offset),
                            "rva": hex(rva), "bytes": size, "pure_getter": pure,
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
                           if c["kind"] == "int" and c["value"] > 1})
            getters = [{"method": m["method"], "signature": m["signature"],
                        "value": next((c["value"] for c in m["constants"]
                                       if c.get("role") == "return"), None)}
                       for m in out if m["pure_getter"]]
            arith = sorted({(c.get("role"), c["value"]) for m in out for c in m["constants"]
                            if str(c.get("role", "")).startswith("arith")})
            summary[cls] = {"methods": len(out), "floats": floats[:40], "ints": ints[:40],
                            "with_constants": sum(1 for m in out if m["constants"]),
                            "getters": getters, "arith": arith[:60]}
            print(f"{cls:22s} {len(out):3d} methods, "
                  f"{sum(1 for m in out if m['constants']):3d} with constants")

    lines = ["# Hằng số bóc từ thân hàm IL2CPP", "",
             "> **Kết luận tạm thời.** Các giá trị dưới đây là hằng số *nhìn thấy trong mã máy*,",
             "> chưa chắc là giá trị thiết kế cuối cùng: có thể là hằng số phụ (epsilon, clamp,",
             "> hệ số nội suy), và có thể bị che bởi phép tính khác. Dùng để **đối chiếu**, không",
             "> phải để chép nguyên. Dữ liệu thô: `reverse-engineering/raw/il2cpp-consts/`.", "",
             f"- .so: `{os.path.basename(so_path)}` — {'aarch64' if md == 0xB7 else 'arm'}",
             f"- class đích: **{len(summary)}**, method: **{total}**", ""]
    lines += ["## Hàm trả về hằng số (độ tin cậy cao)", "",
              "Những method mà toàn bộ thân hàm chỉ là `mov w0, #imm; ret` — đây gần như chắc chắn",
              "là giá trị thiết kế, không phải hằng số phụ.", "",
              "| class | method | giá trị |", "|---|---|---:|"]
    any_getter = False
    for cls, info in sorted(summary.items()):
        for g in info.get("getters", [])[:40]:
            if g.get("value") is None:
                continue
            any_getter = True
            lines.append(f"| `{cls}` | `{g['method']}` | {g['value']} |")
    if not any_getter:
        lines.append("| — | chưa tìm thấy | — |")
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
