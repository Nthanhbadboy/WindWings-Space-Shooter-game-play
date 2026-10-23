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
OUT_CSV = os.environ.get("CONSTS_CSV", "docs/apk-analysis/il2cpp-pool-floats.csv")

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
    "Player_Health": "HP runtime: StartHp gán ở đâu, hồi máu, nhận damage",
    "Player_Talent": "talent: cây điểm, invisible, stun",
    "Player_Ability": "ability: khiên, drone skill, dodge",
    "Player_Ingame": "trạng thái trong trận: level, power-up theo tàu",
    "Player_Attack": "bắn trong trận: nhịp, đạn, overdrive",
    "Enemy_Get_Datas": "enemy: HP khởi đầu theo prefab (Dictionary dựng ở .cctor)",
    "Enemy_Controller": "enemy runtime: GetStartHealth/TakeDamage/UpdateHpBar",
    "Enemy_Health": "enemy runtime: armor/noDamage, nhận damage",
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


def elf_segments(path):
    """[(vaddr, file_off, filesz)] của các PT_LOAD — để đổi VA -> offset file."""
    segs = []
    try:
        with open(path, "rb") as f:
            hdr = f.read(64)
            if hdr[:4] != b"\x7fELF":
                return segs
            phoff = struct.unpack_from("<Q", hdr, 0x20)[0]
            phentsize = struct.unpack_from("<H", hdr, 0x36)[0]
            phnum = struct.unpack_from("<H", hdr, 0x38)[0]
            for i in range(phnum):
                f.seek(phoff + i * phentsize)
                ph = f.read(56)
                if len(ph) < 56 or struct.unpack_from("<I", ph, 0)[0] != 1:
                    continue                       # PT_LOAD
                vaddr = struct.unpack_from("<Q", ph, 0x10)[0]
                off = struct.unpack_from("<Q", ph, 0x08)[0]
                filesz = struct.unpack_from("<Q", ph, 0x20)[0]
                flags = struct.unpack_from("<I", ph, 0x04)[0]      # PF_X=1 PF_W=2 PF_R=4
                segs.append((vaddr, off, filesz, flags))
    except OSError:
        pass
    return segs


PF_W = 0x2

# slot VA -> addend của R_AARCH64_RELATIVE. Các slot con trỏ metadata trong file
# chứa 0; giá trị sau khi linker nạp nằm ở bảng .rela.dyn chứ không ở bytes file.
RELOCS: dict[int, int] = {}


def elf_relocs(path):
    """Đọc .rela.dyn: {r_offset: r_addend} cho R_AARCH64_RELATIVE (1027)."""
    out = {}
    try:
        with open(path, "rb") as f:
            blob = f.read()
        if blob[:4] != b"\x7fELF":
            return out
        shoff = struct.unpack_from("<Q", blob, 0x28)[0]
        shentsize = struct.unpack_from("<H", blob, 0x3A)[0]
        shnum = struct.unpack_from("<H", blob, 0x3C)[0]
        for i in range(shnum):
            base = shoff + i * shentsize
            if base + 64 > len(blob):
                break
            sh_type = struct.unpack_from("<I", blob, base + 4)[0]
            if sh_type != 4:            # SHT_RELA
                continue
            sh_off = struct.unpack_from("<Q", blob, base + 0x18)[0]
            sh_size = struct.unpack_from("<Q", blob, base + 0x20)[0]
            sh_entsize = struct.unpack_from("<Q", blob, base + 0x38)[0] or 24
            for pos in range(sh_off, sh_off + sh_size - 23, sh_entsize):
                r_off, r_info, r_add = struct.unpack_from("<QQq", blob, pos)
                if (r_info & 0xFFFFFFFF) == 1027:
                    out[r_off] = r_add
    except OSError:
        pass
    return out


def slot_value(blob, segs, va):
    """Giá trị 8-byte hiệu dụng tại slot: ưu tiên relocation, fallback bytes file."""
    if va in RELOCS:
        return RELOCS[va]
    raw = va_read(blob, segs, va, 8, ro_only=False)
    return struct.unpack("<Q", raw)[0] if raw and len(raw) == 8 else None


def va_read(blob, segs, va, n=4, ro_only=False):
    """Đọc n byte tại địa chỉ ảo `va` (theo PT_LOAD); fallback coi va là offset.

    ``ro_only``: chỉ đọc trong segment **không ghi được**. Cần thiết vì
    `adrp x8,#0x2adb000; ldr w9,[x8,#0xe0]` là bảng con trỏ metadata
    (`.data.rel.ro`) — đọc 4 byte ở đó ra rác (288733) chứ không phải hằng số.
    Bảng float/int thật nằm trong `.rodata` (segment read-only).
    """
    for vaddr, off, filesz, flags in segs:
        if ro_only and flags & PF_W:
            continue
        if vaddr <= va < vaddr + filesz:
            pos = off + (va - vaddr)
            if pos + n <= len(blob):
                return blob[pos:pos + n]
            return None
    if not ro_only and 0 <= va <= len(blob) - n:
        return blob[va:va + n]
    return None


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


def constants_in(code_off, size, blob, md, segs=None, base=None, name=""):
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
    # Disassemble at the *virtual* address so `adrp` resolves into .rodata.
    # Slicing still uses the file offset.  base defaults to the offset (same on
    # most builds, but the ARM64 adrp immediate is PC-page relative).
    insns = list(cs.disasm(chunk, base if base is not None else code_off))
    adrp_pages: dict = {}
    slot_regs: dict = {}  # reg -> VA slot nạp từ page adrp (chuỗi InitializeArray)
    reg_token: dict = {}  # reg -> qword tại [slot-target] (token metadata 0x80000xxx?)
    pending_len = [None, -99]  # (độ dài mảng từ mov w1,#N, chỉ số lệnh)
    debug_rva: list = []  # chỉ đầy khi RVA_DEBUG=1 (chẩn đoán layout blob)
    pending_floats: list = []
    emitted: set = set()
    for _idx, insn in enumerate(insns):
        text = f"{insn.address:#x}: {insn.mnemonic:8s} {insn.op_str}"
        lines.append(text)
        # ---- token InitializeArray: mov w1,#len ... ldr x1,[slot] ... bl
        if insn.mnemonic in ("mov", "movz") and insn.op_str.startswith("w1, #"):
            try:
                pending_len[0] = int(insn.op_str.split("#", 1)[1], 0)
                pending_len[1] = _idx
            except ValueError:
                pass
        if insn.mnemonic == "bl" and "x1" in reg_token \
                and pending_len[0] is not None and _idx - pending_len[1] <= 14:
            consts.append({"kind": "init_array", "len": pending_len[0],
                           "slot_val": hex(reg_token["x1"]),
                           "addr": hex(insn.address)})
            pending_len[0] = None
        # ---- adrp/ldr: hằng số float nằm trong literal pool (.rodata)
        if insn.mnemonic == "adrp" and md == 0xB7:
            parts = [x.strip() for x in insn.op_str.split(",")]
            if len(parts) == 2 and parts[1].startswith("#"):
                try:
                    adrp_pages[parts[0]] = int(parts[1][1:], 0)
                except ValueError:
                    pass
        if insn.mnemonic.startswith("add") and md == 0xB7:
            parts = [x.strip() for x in insn.op_str.split(",")]
            if len(parts) == 3 and parts[1] in adrp_pages and parts[2].startswith("#"):
                try:
                    adrp_pages[parts[0]] = adrp_pages[parts[1]] + int(parts[2][1:], 0)
                except ValueError:
                    pass
        if insn.mnemonic == "ldr" and segs and md == 0xB7:
            m = re.search(r"\[(x\d+)(?:, #(0x[0-9a-f]+|\d+))?\]", insn.op_str)
            dst = insn.op_str.split(",")[0].strip()
            if m and m.group(1) in adrp_pages and dst.startswith(("s", "d")):
                va = adrp_pages[m.group(1)] + (int(m.group(2), 0) if m.group(2) else 0)
                if dst.startswith("d"):
                    # ldr d nạp CẶP float liên tiếp (vd cặp nằm ở static offset
                    # 0x68/0x6c trong Player_Get_Datas..cctor — thiếu nửa trên
                    # là mất StartHp). Ghi cả hai nửa kèm VA riêng.
                    raw8 = va_read(blob, segs, va, 8, ro_only=True)
                    if raw8 and len(raw8) == 8:
                        lo, hi = struct.unpack("<ff", raw8)
                        for k, val in enumerate((lo, hi)):
                            if val == val and 1e-6 < abs(val) < 1e6:
                                consts.append({"kind": "float", "value": round(val, 5),
                                               "via": "ldr_pool_d", "va": hex(va + 4 * k),
                                               "addr": hex(insn.address)})
                    continue
                raw = va_read(blob, segs, va, 4, ro_only=True)
                if raw and len(raw) == 4:
                    val = struct.unpack("<f", raw)[0]
                    if val == val and 1e-6 < abs(val) < 1e6:
                        consts.append({"kind": "float", "value": round(val, 5),
                                       "via": "ldr_pool", "va": hex(va),
                                       "addr": hex(insn.address)})
        # ---- RVA field data (InitializeArray): adrp page -> ldr xM,[slot]
        # -> ldr xN,[xM]. [slot] là con trỏ tới object metadata, [object] là
        # con trỏ tới blob [int32 count][int32 x count] trong .rodata. Đây là
        # nguồn của các mảng literal (bảng map->wave, bảng stat device...).
        if insn.mnemonic == "ldr" and segs:
            m = re.search(r"\[(x\d+)(?:, #(0x[0-9a-f]+|\d+))?\]", insn.op_str)
            dst = insn.op_str.split(",")[0].strip()
            if m and dst.startswith("x"):
                base, off = m.group(1), int(m.group(2), 0) if m.group(2) else 0
                # Deref [xM] (off=0) phải xét TRƯỚC: sau `ldr xM,[page,#off]`
                # thì xM không còn giữ page nữa dù adrp_pages vẫn còn ghi.
                if base in slot_regs and off == 0 and dst != base:
                    pass  # rơi xuống nhánh deref bên dưới
                elif base in adrp_pages:
                    slot_regs[dst] = adrp_pages[base] + off
                    adrp_pages.pop(dst, None)
                if base in slot_regs and off == 0 and dst != base:
                    a = slot_value(blob, segs, slot_regs[base])
                    if a:
                        _raw_tok = va_read(blob, segs, a, 8, ro_only=False)
                        if _raw_tok and len(_raw_tok) == 8:
                            reg_token[dst] = struct.unpack("<Q", _raw_tok)[0]
                        if os.environ.get("RVA_DEBUG") and name == "cctor" and len(debug_rva) < 3000:
                            raw_v = va_read(blob, segs, a, 16, ro_only=False)
                            debug_rva.append({"addr": hex(insn.address),
                                              "slot": hex(slot_regs[base]),
                                              "a": hex(a),
                                              "a_bytes": raw_v.hex() if raw_v else None})
                        for start in (a,):
                            v = slot_value(blob, segs, start)
                            cands = [start] + ([v] if v else [])
                            for ptr in cands:
                                raw_hdr = va_read(blob, segs, ptr, 4, ro_only=True)
                                if not raw_hdr or len(raw_hdr) != 4:
                                    continue
                                cnt = struct.unpack("<i", raw_hdr)[0]
                                if not (1 <= cnt <= 512):
                                    continue
                                raw_body = va_read(blob, segs, ptr + 4, 4 * cnt,
                                                   ro_only=True)
                                if not raw_body or len(raw_body) != 4 * cnt:
                                    continue
                                vals = list(struct.unpack(f"<{cnt}i", raw_body))
                                if all(-1000 <= v <= 100000000 for v in vals):
                                    consts.append({"kind": "int_array", "value": vals,
                                                   "via": "rva_data", "va": hex(ptr),
                                                   "addr": hex(insn.address)})
                                    break
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
    for dbg in debug_rva:
        consts.append({"kind": "debug_rva", **dbg})
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


def _tail_body(insn_text: str):
    """Bỏ prologue + guard khởi tạo static (cắt tại `strb` ghi cờ cuối cùng)."""
    body = [l.split(":", 1)[-1].strip() for l in insn_text.split("\n") if l.strip()]
    body = [l for l in body if not l.startswith(PROLOGUE)]
    if not body:
        return []
    cut = max((i for i, l in enumerate(body) if l.startswith("strb")), default=-1)
    return body[cut + 1:]


def _return_tail(tail):
    """Chỉ phần *sau* lệnh `bl` cuối cùng.

    `mov w0, #7 ; bl GetStatValue` là **tham số** của lời gọi, không phải giá trị
    trả về — bản trước nhầm chỗ này nên báo sai `GetHpStatPercent = 7`.
    """
    last = max((i for i, l in enumerate(tail) if l.startswith("bl ")), default=-1)
    return tail[last + 1:]


def getter_kind(insn_text: str):
    """Phân loại getter theo **phần đuôi thật sự trả về**.

    * ``const``    — trả thẳng một hằng số (``mov w0, #imm`` / ``fmov s0, #k``)
    * ``field``    — đọc field/array static rồi trả
    * ``computed`` — có phép tính trước khi trả
    * ``call``     — tail-call sang hàm khác (``b``), hoặc trả kết quả hàm khác
    """
    tail = _tail_body(insn_text)
    if not tail:
        return None
    tail = [l for l in tail if not l.startswith("mov x0, xzr")]
    rt = _return_tail(tail)
    if not rt:
        return "call"
    if any(re.match(r"(mov|movz)\s+w0,\s*#", l) for l in rt):
        return "const"
    if any(re.match(r"fmov\s+s0,\s*#-?[\d.]+", l) for l in rt):
        return "const"
    for l in rt:
        m = re.match(r"fmov\s+s0,\s*w(\d+)", l)
        if m and any(re.match(rf"mov\s+w{m.group(1)},\s*#0x[0-9a-f]{{6,8}}", x) for x in tail):
            return "const"
    if any(re.match(r"(add|sub|mul|madd|msub|fadd|fsub|fmul|fdiv|fnmul|scvtf|fcvtzs|csel)\b", l)
           for l in rt):
        return "computed"
    if any(l.startswith("b ") for l in rt):
        return "call"
    if any(re.match(r"ldr\s+(w0|s0),", l) for l in rt):
        return "field"
    return None


def getter_value(insn_text: str):
    """Giá trị trả về thật sự — chỉ đọc lệnh ghi `w0`/`s0` nằm sau `bl` cuối."""
    tail = _tail_body(insn_text)
    if not tail:
        return None
    rt = _return_tail(tail)
    regs = {}
    for l in rt:
        m = re.match(r"mov\s+w(\d+),\s*#(0x[0-9a-f]+|\d+)", l)
        if m:
            if m.group(1) == "0":
                return int(m.group(2), 0)
            regs["w" + m.group(1)] = int(m.group(2), 0)
            continue
        m = re.match(r"fmov\s+s0,\s*#(-?[\d.]+)", l)
        if m:
            return float(m.group(1))
        m = re.match(r"fmov\s+s0,\s*w(\d+)", l)
        if m and ("w" + m.group(1)) in regs:
            return _as_float(regs["w" + m.group(1)])
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
    segs = elf_segments(so_path)
    RELOCS.update(elf_relocs(so_path))
    print(f"R_AARCH64_RELATIVE relocs: {len(RELOCS)}")
    print(f"PT_LOAD segments: {len(segs)}")
    print(f"ELF machine: {hex(md) if md else 'unknown'} ({'aarch64' if md == 0xB7 else 'arm'})")
    methods = parse_dump(dump_path)
    print(f"methods parsed: {len(methods)}")

    wanted = defaultdict(list)
    for cls, ns, name, offset, rva, sig in methods:
        if cls in TARGET_CLASSES or (ns and ns.split(".")[-1] in TARGET_CLASSES):
            wanted[cls].append((name, offset, rva, sig))
    total = sum(len(v) for v in wanted.values())
    print(f"methods in target classes: {total} across {len(wanted)} classes")

    # Độ dài method = khoảng tới method KẾ TIẾP trong toàn bộ dump (không chỉ
    # cùng class). Bản cũ cap cứng 0x1200 (4.608 byte) làm .cctor và mọi method
    # dài bị cắt cụt giữa chừng mà không có dấu hiệu nào — các kết luận âm tính
    # ("không thấy lệnh ghi X") dựa trên asm đó đều vô hiệu. Xem 19/28.
    all_offsets = sorted({m[3] for m in methods if m[3] > 0})

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
                import bisect as _bisect
                j = _bisect.bisect_right(all_offsets, offset)
                nxt = all_offsets[j] if j < len(all_offsets) else offset + 0x20000
                size = min(max(nxt - offset, 8), 0x20000)   # cap 128 KB / method
                if offset <= 0 or size <= 0:
                    continue
                consts, lines = constants_in(offset, size, blob, md or 0xB7, segs,
                                             base=rva or offset, name=name)
                annotate("\n".join(lines), consts)
                body_text = "\n".join(lines)
                # Tự kiểm cắt cụt: thân method gần như luôn kết thúc bằng
                # ret/b/br. Không có -> nhiều khả năng bị cắt, và MỌI kết luận
                # âm tính ("không thấy lệnh X") trên method đó đều vô hiệu.
                # Vùng disasm kéo đúng tới method kế tiếp nên sau `ret` thật
                # còn lẫn thunk/đệm — chỉ cần thấy ret ở 48 lệnh cuối là đủ.
                _mns = []
                for _l in lines:
                    _p = _l.split(":", 1)[-1].strip().split()
                    if _p:
                        _mns.append(_p[0])
                # Method kết thúc bằng ret, hoặc nhảy đuôi (b/br) ra ngoài;
                # cả hai đều phải xuất hiện gần cuối vùng đã đọc.
                ends_clean = any(m in ("ret", "b", "br") for m in _mns[-12:])
                pure = is_pure_getter(body_text)
                gkind = getter_kind(body_text)
                gvalue = getter_value(body_text) if gkind else None
                out.append({"method": name, "signature": sig, "offset": hex(offset),
                            "getter_value": gvalue,
                            "rva": hex(rva), "bytes": size, "pure_getter": pure,
                            "getter_kind": gkind,
                            "size_capped": size >= 0x20000,
                            "ends_clean": ends_clean,
                            "constants": consts})
                # Luôn ghi asm cho MỌI method: method vắng mặt khỏi file asm
                # từng làm cờ ends_clean "đúng rỗng" (VERIFY_ROUND1 §2.1).
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
                        "value": m.get("getter_value")}
                       for m in out if m.get("getter_kind")]
            gkind = Counter(g["kind"] for g in getters)
            arith = sorted({(c.get("role"), c["value"]) for m in out for c in m["constants"]
                            if str(c.get("role", "")).startswith("arith")})
            pool = [(m["method"], c["value"], c.get("va"), c.get("via"))
                    for m in out for c in m["constants"] if c.get("via", "").startswith("ldr_pool")]
            summary[cls] = {"methods": len(out), "floats": floats[:40], "ints": ints[:40],
                            "pool_floats": pool[:40],
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

    pool_rows = [(cls, meth, val, va, via) for cls, info in sorted(summary.items())
                 for meth, val, va, via in info.get("pool_floats", [])]
    if pool_rows:
        lines += ["### Float đọc từ literal pool (`.rodata`) — số thật, không phải suy luận", "",
                  "`adrp xN, #page` + `ldr sM, [xN, #off]` trỏ vào bảng float trong `.rodata`;",
                  "script đổi VA → offset qua `PT_LOAD` rồi đọc 4 byte, **chỉ trong segment read-only**",
                  "(bảng con trỏ metadata nằm ở segment ghi được — đọc vào đó ra rác như `288733`).",
                  "Đây là số **có thật trong file**, nhưng ý nghĩa (hệ số nào) vẫn phải đọc thêm control flow.", "",
                  "| class | method | giá trị | VA |", "|---|---|---:|---|"]
        seen = set()
        for cls, meth, val, va, via in pool_rows:
            if (cls, meth, val) in seen:
                continue
            seen.add((cls, meth, val))
            lines.append(f"| `{cls}` | `{meth}` | {val} | `{va}` |")
        lines.append("")

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
    # CSV phẳng: mọi hằng số đọc từ literal pool, để đối chiếu bằng spreadsheet
    import csv as _csv
    os.makedirs(os.path.dirname(OUT_CSV) or ".", exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = _csv.writer(fh)
        w.writerow(["class", "method", "value", "via", "va", "addr"])
        for cls, info in sorted(summary.items()):
            for meth, val, va, via in info.get("pool_floats", []):
                w.writerow([cls, meth, val, via, va, ""])

    os.makedirs(os.path.dirname(OUT_MD) or ".", exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("written", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
