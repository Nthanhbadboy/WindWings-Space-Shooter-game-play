# HANDOFF — sửa spec theo review `25c367aca` (nhánh `arena/20330d0e`)

**Ngày:** 25/10. **Nhánh:** `arena/20330d0e-windwings-space-shooter-game-p` (PR #12).
**Đối tượng:** nhánh dữ liệu `arena/ef6b75ef-…` — đọc để **áp dụng lại**, không phải để tin.

Review gốc nằm ở **PR #12 comment `6396779924`** (6 điểm R1–R6, đánh trên snapshot `25c367aca`
+ raw `7e0da2ee3`). Tài liệu này ghi **đã sửa gì, bằng chứng nào, còn gì chưa chứng minh**.
Không có file nào của nhánh dữ liệu bị sửa; mọi thay đổi nằm trên nhánh này.

---

## 1. Sáu điểm và cách sửa

| # | Vấn đề review nêu (trên snapshot) | Đã sửa thành | Bằng chứng / claim |
|---|---|---|---|
| **R1** | `MISSIONS_STARS.md` ghi **fallback = mode 0**; thiếu bảng %; lẫn `savedStars` với kills | fallback là nhánh **`0xb78`** (`csel` mặc định), không rơi về `0xb80`; thêm §2 asm + §7.3 **3 mode × 3 stage**; `IsMissionCompleted` = `savedStars > i`, tách khỏi kills | asm `GetKillPercentMissionComplete` @`0x14e5618`; mẫu số stage2 **262**, stage3 **238**; ngưỡng mode0 **52/117/209** · **47/107/190** |
| **R2** | `ENCOUNTERS.md` khuyên "chia đôi / dedup theo tên trùng" ⇒ gộp nhầm normal với Chapter2 | rút lời khuyên; thêm §1.3 chứng minh **cùng tên GO ≠ cùng resource** (`wave_0164` root `148604` vs `148637`); đếm theo **ident**: `Call_Data` pathID | 14 file wave đã kéo: **0** pathID trùng; `Wave_0164` 42 component = 42 dòng |
| **R3** | "116 sheet chưa tách" thực chất là **116 tên atlas không match** | đổi cách gọi; tách rõ **67 page `sactx` theo tên** vs **56** page có `category=atlas` | `04-asset-manifest.csv` 67 · `sprites-index.csv` 56; claim `AB1` |
| **R4** | classifier có luật **bị che** (R14 che R22 `Coda_`, R18 che R23 `XVideo`); **643 nhãn cũ tự cấp A** | bỏ `Coda_` khỏi R14 (→ `font` R22), bỏ nhánh `XVideo` khỏi R23; `shadowed_rules()` chạy mỗi lần; 643 passthrough có `confidence` **rỗng** + `label_source=category_passthrough` + `reviewed=false` | `tests/test_classify_rules.py` 5 test; claim `AB4` (1.049 = 848 A · 131 B · 70 C) |
| **R5** | `DESIGN_READINESS.md`: D3 vừa "một phần" vừa "đã đóng" | **D3 KHÔNG đóng** — A cho mốc clip, C cho thứ tự/điều kiện/hành vi | mâu thuẫn với bảng §2 đã hết |
| **R6** | verifier biến **lỗi đo** thành SKIP ⇒ exit 0 | `NoSource` là ngoại lệ **duy nhất** được SKIP; mọi lỗi khác = `ERROR` ⇒ **exit 1**; thêm `--no-skip`, `--require` (tiền tố sai = **exit 2**, không im lặng); CI chạy `--require AB,AO,AP` | `python3 tools/verify-claims.py` ⇒ **173 PASS · 0 FAIL · 2 SKIP · 0 ERROR**; `--no-skip` ⇒ **rc=1**; `--require ZZ` ⇒ **rc=2** |

## 2. Một lỗi của **chính bản sửa này** — đơn vị, không phải dữ liệu

Lần đầu tôi "sửa" `ENCOUNTERS.md` từ **23.757 → 11.094** và viết "bảng cũ sai vì export nhân đôi".
**Sai.** Lần hai tôi sửa thành "11.094 dòng = số `Call_Data` component" — **vẫn sai**, và đã sửa lần ba
(25/10, sau khi kéo `class-inventory.csv`):

- **23.757** = `Σ copies` trong `waves.json` **=** số instance `Call_Data` trong `class-inventory.csv`
  ⇒ **đây là số spawner/object**. Hai nguồn khớp, không có "export nhân đôi";
- **11.094** (nay **11.089** ở bản `622b700e5`) = số **dòng cấu hình** — export **gộp object trùng**,
  mỗi dòng mang `copies`. **Không** phải "1 dòng = 1 `Call_Data` component";
- bảng cũ khớp `Σ copies` **9/9 wave** (150 · 331 · 72 · 36 · 54 · **622** · 42 · 84 · 6; `Wave_0163`
  là **621** ở snapshot `8c6da25`, **622** từ `622b700e5`) ⇒ bảng cũ **đúng số, sai nhãn cột**;
- dãy `16.498 / 4.199 / 1.688 / 686 / 686` mà `CROSS_BRANCH_20330d0e.md` §3c ghi cũng là **lượt**.

⇒ Đã in **cả hai cột** (§1.1, §1.4, §1.5, §3) + claim `AQ4`/`AQ5`/`AQ6`/`AQ7` khoá lại.
**Bài học cho nhánh dữ liệu:** (a) nếu bên đó ghi "23.757 spawner" thì **đúng** — đó là object;
(b) nếu bên đó theo bản sửa thứ hai của tôi mà ghi "**11.089 spawner**" thì **sai** — 11.089 là **dòng
cấu hình**; (c) đừng bao giờ kết luận "tổng không đổi ⇒ dữ liệu không đổi": 9 wave + `unknown` đã đổi
trong lúc tổng giữ nguyên (`DATA_SYNC.md` §17.1).

**Chỗ vẫn là suy diễn:** `45.659 "quân"` phụ thuộc `copies`. Raw `Call_Data` đã kéo **không có**
field `copies` (chỉ `number` = 0 và `rate`), nên `copies` do exporter sinh ra — **mức B**, và báo cáo
`54` bên đó cũng viết *"không coi `copies` là số đợt"*.

## 3. Còn **chưa** chứng minh (đừng đọc thành "đã xong")

| Việc | Trạng thái | Cần gì để đóng |
|---|---|---|
| **D3** — clip/điều kiện/hành vi | 🟡 A cho **mốc clip**, C cho thứ tự · điều kiện · hành vi | consumer asm của 793 event (T3/T2 trong `HANDOFF_ANIM_RAW.md`) |
| **340 sprite `unresolved`** | 🟡 kNN gợi ý **89** (`ui` 72 · `bullet` 8 · `enemy` 4 · `bosses` 4 · `parts` 1), LOO **674/781 = 86,3 %** | xem mắt, hoặc `Sprite.m_RD.rect` |
| **4.250 "mảnh"** | 🟡 **cận trên**; chỉ **792** mảnh ≥20×20, **158** ≥64×64; **56 %** mảnh lớn còn góc caro | PNG gốc có alpha + `m_RD.textureRect` |
| **67 vs 56 page `sactx`** | 🟡 11 page bị **luật tên** xếp nhầm `category` | sửa luật sinh `sprites-index.csv` bên nhánh dữ liệu |
| `copies` → 45.659 quân | 🟡 **mức B** | exporter hoặc giải `bytes_base64` của `Call_Data` |

## 4. Cách kiểm lại (phải ra đúng số này)

```bash
python3 -m unittest discover -s tests -q          # 5 test OK
python3 tools/verify-claims.py                    # dòng cuối in PASS/FAIL/SKIP/ERROR — chạy để biết
python3 tools/verify-claims.py --no-skip; echo $?  # 1 (2 SKIP có chủ đích: B9, F4)
python3 tools/data-integrity.py; echo $?          # 0 — 0 file đang sửa trong working tree
```

`data-integrity.py` tách **ba** nhóm: khớp snapshot đã pin · **khớp HEAD nhưng cũ hơn snapshot**
(kéo ở commit ngoài danh sách — **không** phải sửa tay) · **đang sửa** (mới là đỏ).
