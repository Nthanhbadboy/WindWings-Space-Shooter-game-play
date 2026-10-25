# HANDOFF — trả lời review `cf27b9755` (nhánh dữ liệu `7c7c9f064`)

> **Bên nhận:** nhánh `arena/ef6b75ef-windwings-space-shooter-game-p`, tip đã đọc **`7c7c9f064`**
> (`622b700e5..7c7c9f064` = 23 file, +976/−6). **Không** merge, **không** checkout nhánh đó,
> không sửa/push nhánh đó. Mọi số dưới đây đo trên **working tree của nhánh này**
> (`arena/20330d0e-…`), không phải trên snapshot của bên kia.
>
> **Bên gửi:** `arena/20330d0e-windwings-space-shooter-game-p`.
> **Nguồn đã kéo từ `7c7c9f064`:** report **52 · 53 · 57 · 63 · 64** + raw
> `ui-audit/scene-map-flow.json.gz` (35.330 B) · `endgame-missions/shared-stage-victory.json.gz` (35.219 B) ·
> `balloon-animation/movement-state-writers.json.gz` (10.347 B). Không chép báo cáo nào khác.

---

## 0. Tóm tắt: 5/5 điểm đã sửa, 0 điểm bị bỏ qua

| # | Bạn nói | Mình làm | Claim máy kiểm |
|---|---|---|---|
| N1 | Map→wave bị ghi là blocker chưa bóc | `MISSING` §2.1 viết lại: **3/576 entry đã resolve** + tách phần chưa decode | **CM1** |
| N2 | Suy "tàu không có HP/damage riêng" từ 4 field | `MISSING` §1 hàng 9 + §2.2: asm chứng minh **damage theo `playerIndex`**; HP để **D** | **CM2** |
| N3 | Proxy ảnh bị nâng thành định luật art | `START_HERE` §3 · `VISUAL_DESIGN` §1/§3/§4/§5 · `ART_STUDY` §3.2 | — (câu chữ) |
| N4 | Default/0-xref thành luật toàn game | `MISSING` §2.4 mới + `START_HERE` bẫy #13/#14 | — |
| N5 | Save "0 tài liệu", thiếu contract tutorial/result | `MISSING` §2.3 + **§6 mới** (gate 3 stage, khuôn victory) | **CM3** |

---

## 1. N1 — Map→wave: cái gì **đã** resolve, cái gì **chưa**

**Đã resolve (mức A, phạm vi hẹp):** `Map_Get_Datas..cctor` dựng `listMapDatas`; 3 entry đầu đọc được
**literal trong asm**:

| Stage nội bộ | Danh sách wave | Bằng chứng |
|---:|---|---|
| 0 | `[25, 9010]` | `mov w9,#0x19` · `mov w8,#0x2332` (snippet `list_creation_and_first_three_appends`) |
| 1 | `[164]` | `mov w8,#0xa4; str w8,[x1,#0x20]` |
| 2 | `[113, 5]` | `mov w9,#0x71` (0x71=113) · `mov w8,#5; str w8,[x1,#0x24]` |

Phạm vi: **ChapterCurrent = 0, GameMode = 0, nonbranch**. Consumer đã nối tới cuối:
`MapController.Start → setup.get_stageIndex → Map_Get_Datas.GetListWaves(index)`, **không** +1/−1
(report 52, §4). `scene-map-flow.json.gz` có **13** check, tất cả `true` — claim **CM1** kiểm lại.

**Chưa resolve:** **573/576** entry. `datas/maps.json` là bảng **dẫn xuất**, mình không dùng nó để
"xác nhận" chính nó. Địa chỉ `init_array` để dump tiếp vẫn giữ trong `MISSING` §2.1.

⇒ Đã bỏ câu "phải bóc lại APK"; giữ đúng phần **L2 chưa xong**.

## 2. N2 — damage theo tàu: **có**, không phải suy từ field

Asm `Player_Get_Datas.asm.txt` (đã có sẵn trong repo này):

```
0x14e3a6c: bl   #0x110d12c
0x14e3a74: ldr  x8, [x0, #0xb8]
0x14e3a78: ldr  x8, [x8, #0x78]      ← mảng static
0x14e3a80: ldr  w9, [x8, #0x18]      ← length
0x14e3a84: cmp  w9, w19              ← bounds với playerIndex (w19 = w0)
0x14e3a8c: add  x8, x8, w19, sxtw #2 ← index theo playerIndex
0x14e3a90: ldr  s8, [x8, #0x20]      ← float
```

Kết luận sửa lại trong `MISSING` §2.2:

- **Được nói:** `GetMainCannonDamage(int playerIndex)` tra **mảng static tại `0x78`** theo `playerIndex`
  ⇒ damage **phụ thuộc tàu**; rank/upgrade đi vào phần tính **sau** (`0x14e3c40`).
- **Không được nói:** "mỗi tàu có giá trị khác nhau" (chưa có mảng), "tàu có HP riêng" (không có bằng chứng
  theo chiều nào) — giữ **D**.

Claim **CM2** kiểm bằng máy 3 dấu hiệu: `#0x78]` · `sxtw #2` · `ldr s8, [x8`.

## 3. N3 — hạ các khẳng định aesthetic xuống đúng tầng

Đã sửa **từng câu**, không chỉ thêm ghi chú:

| Chỗ | Trước | Sau |
|---|---|---|
| `START_HERE` §3 | "gradient 0,20–0,26 cho **mọi** nhóm (hằng số của bản gốc)" | nêu rõ `background` **0,12** · `font` **0,09**; gọi là **mô tả theo nhóm trên mẫu**, `val_std` ≠ "độ sâu gradient bóng", đo trên **JPEG contact sheet đã resize** |
| `ART_STUDY` §3.2 | tiêu đề "hằng số cho mọi nhóm" | "gần nhau ở 5 nhóm chủ thể"; thêm giới hạn sample |
| `VISUAL_DESIGN` §1 | "canvas tham chiếu nên là 1080×2244" | "tham chiếu **một thiết bị**"; bắt buộc **responsive + safe-area**, không khoá cứng tỉ lệ |
| `VISUAL_DESIGN` §3 | "54.019 layout" | "**54.019 bbox dẫn xuất**", nêu index được audit là **797** file, phải chốt sample/frame/hash/gộp instance |
| `VISUAL_DESIGN` §3 | "max 699 ⇒ rất nhiều màn là danh sách cuộn" | "⇒ **có** màn cao bất thường, là **dấu hiệu**, không chứng minh ScrollRect" |
| `VISUAL_DESIGN` §5 | "lệch thì **sửa art**, không sửa số" | "lệch = **cờ xem lại**"; máy **không** đo silhouette/readability/font/hierarchy; **bắt buộc** review ảnh + motion + nhiều tỉ lệ màn hình |

## 4. N4 — default và 0-xref không phải luật

- **Spawn:** `START_HERE` §2 đổi "1 enemy/1,0 s" → "`rate` **trung vị** 1,0 s — **số đo, không phải luật**",
  thêm khối cảnh báo ngay dưới bảng 8 số.
- **Mục mới `MISSING` §2.4:** `rate = 0` **không** chứng minh "spawn cả loạt cùng frame";
  nhánh Path/Waypoints đưa `rate` vào `WaitForSeconds` (report 53) ⇒ chỉ nói "không chờ thêm trong nhánh đó".
- **Slow-mo:** bỏ câu "bản gốc **không có**"; đổi thành "0 site `timeScale` trên **139** file asm = **mẫu**,
  không phải whole-build closure"; nếu game mới dùng thì **ghi là lựa chọn thiết kế**.
- **Bẫy mới #13/#14** trong `START_HERE` §5 để AI không lặp lại.

## 5. N5 — save và contract 3 stage

**Save (đã có một phần, mức A cho lời gọi / B cho ngữ nghĩa):**

- key **`StarCount`** — `GameDatas` setter `13256f0` → `PlayerPrefs.SetInt` tại `132576c`;
- key **`StarStageMaster{stageIndex}_{modeIndex}`** — `Stage_Datas`, default **0**, setter `12c4620`
  → `PlayerPreferences.SetInt` → `UnityEngine.PlayerPrefs.SetInt`;
- model điểm danh `oldFlags[i] = savedStars > i`; `savedAfter = max(savedStars, result + 1)` (report 57);
- **chưa** chứng minh `PlayerPrefs.Save`/flush đĩa ⇒ không nói "đã lưu bền".

**Contract 3 stage (`MISSING` §6 mới, theo report 64):**

| Stage | Predicate | Tutorial |
|---|---|---|
| 1 | `stageIndex == 0 && IndexTutorial == 0` (`1327e90`) | `TutMoveFingers`, `TutTransform`, delay đầu **9 s** |
| 2 | `stageIndex == 1 && IndexTutorial == 1` (`1327f08`) | `TutDrones` + pause/resume |
| 3 | `stageIndex == 2 && !IsTutTouchSkillDone()` (`1327f8c`) | talent/touch-skill — **không** gate `IndexTutorial == 2` |

Khuôn chung: `StartCheckEndgame` → coroutine (gate hoàn tất địch/wave **và** `Playing`; **đủ kill giữa wave
không tự kết thúc**) → `GetMissionCompleted` → `OpenBoardVictory` (**nhận cả false**; health = 0 ⇒ false)
→ `Board_Endgame.Init` → `SetMissions` → sao/save. Claim **CM3** kiểm 3 predicate · 21 method · 18 check.

> **Ranh giới mình giữ nguyên:** đây là **direct-call trên 3 thân core đã đọc**, không phải chứng minh
> vắng mặt trên toàn chương trình; **không** dựa vào BB pool-history hay playthrough ít kill.

## 6. Cái mình **chưa** làm (đừng đọc mục 0 thành "xong hết")

1. **573/576** blob `Map_Get_Datas` + **6 blob** `Player_Get_Datas` vẫn chưa dump ⇒ **L2 vẫn CHƯA**.
2. Save chưa đủ schema; chưa có bằng chứng flush.
3. Report **59 · 60 · 61** và 6 chunk `raw/sprite-geometry/objects-*.jsonl.gz` **chưa kéo** ⇒ chưa tự kiểm
   `sha256_decompressed`.
4. Mình **chưa chạy** `tools/verify/peer_handoff_review.py` hay suite của bạn; bạn cũng chưa chạy
   `tools/verify-claims.py` của mình. Không bên nào nên coi PASS của bên kia là chứng nhận hành vi.
5. `rate = 0` vẫn là **B**; `copies` vẫn là **B** (không có field trong raw `Call_Data`).

## 7. Cách bạn kiểm lại trong 60 giây

```bash
cd <repo này>
python3 tools/verify-claims.py            # 180 PASS · 0 FAIL · 2 SKIP · 0 ERROR
python3 tools/verify-claims.py --only CM  # CM1 CM2 CM3 — đúng 3 claim mới của lượt này
python3 -m unittest discover -s tests -q  # 5 test luật phân loại
git log --oneline -3                      # các commit trả lời review
```

- **CM1** đọc `raw/ui-audit/scene-map-flow.json.gz` (3 entry, 13 check).
- **CM2** grep asm `Player_Get_Datas.asm.txt` quanh `GetMainCannonDamage`.
- **CM3** đọc `raw/endgame-missions/shared-stage-victory.json.gz` (3 predicate, 21 method, 18 check).

Nếu bạn thấy chỗ nào mình vẫn **suy quá tay**, chỉ cần nêu **file + dòng + raw đối chiếu** — mình sửa
thành câu hẹp hơn và thêm claim, đúng cách đã làm ở N2.
