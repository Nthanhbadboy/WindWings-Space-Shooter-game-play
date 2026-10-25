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

---

## 8. Cập nhật sau `6ababbd31` — và một sổ kiểm mới để **không nói mồm**

Nhánh bạn đi tiếp 3 commit (`7c7c9f064 → 6ababbd31`). Mình kéo **đúng 5 file raw** của
`raw/player-loadout/` + `datas/opening_persistence.json` + report 65, rồi **tự kiểm hash**:

| file | sha256 (16 ký tự đầu) | khớp `index.json` |
|---|---|---|
| `Player_Saved_Datas.asm.txt` | `bf90fe4d926e0007` | ✅ |
| `Player_Saved_Datas.json` | `e4c5e1a37f8e07682` | ✅ |
| `Player_Device_Saved_Datas.asm.txt` | `4cd845eca6efa22b` | ✅ |
| `Player_Device_Saved_Datas.json` | `a410ecc45e6956f5` | ✅ |
| `array-blobs.json.gz` | `2ff95f6464eeb0c5` | ✅ |

⇒ Claim **CM5** (5 blob · 49 int · 5/5 sha256). Lần đầu một raw của bạn được kiểm hash **trong repo này**.

**Những gì mình viết lại theo raw mới:**

- Save: 2 key → **8 key family · 2 store · 7 limitation** (claim **CM4**), kèm cảnh báo **getter có side
  effect** (`get_StageTarget` tăng 1 mỗi lần đọc; `get_IndexTutorial` tự ghi 6).
- Blob int `[0,0,0,6500,8500,9500,12500]` = **giá craft** (chưa bind field, mức **B**) — **không** gộp với
  4 mảng **float damage**; **B3 vẫn mở**.
- Trạng thái trong raw được giữ nguyên chữ: `PROVISIONAL_STATIC_PARTIAL_SAVE_CONTRACT_NOT_FULL_SCHEMA`.

**Sổ kiểm mới — trả lời câu \"dựa raw hay nói mồm\" bằng máy:** `docs/spec/RAW_AUDIT.md`
(sinh bằng `python3 tools/raw-audit.py`). Nó phân loại **200 claim**:

| loại | số | nghĩa |
|---|---:|---|
| **RAW** | **170** | hàm đo **mở file** raw ⇒ tái đo được |
| **DOC** | **2** | chỉ đọc `docs/**` |
| **CONST** | **28** | không mở file ⇒ \"đo một lần\" |

Claim **RB1** khoá 4 số đó, nên ai thêm một `lambda: <hằng số>` rồi gọi là bằng chứng thì sổ sẽ lệch ngay.
Danh sách 37 CONST (A*, D*, E*, R*, W4/W5) nằm trong file, kèm luật: *số CONST không được dùng để bác
một kết luận khác*.

**Vẫn chưa kéo:** report **59 · 60 · 61**; 6 chunk `sprite-geometry/objects-*.jsonl.gz`; `raw/ui-audit`
(407) · `raw/il2cpp-consts` (273) · `raw/animation-audit` · `raw/runtime-probe`.

---

## 9. Lượt này mình **chạy code của bạn**, không chỉ đọc report

Trước đây mình chỉ đối chiếu chữ. Lần này chép `tools/verify/opening_persistence.py` + 3 module nó import
+ 2 test vào repo này rồi chạy thật:

```
$ python3 tools/verify/opening_persistence.py
41 methods; 25 checks; 8 key families

$ python3 -m unittest discover -s tests -q
Ran 16 tests in 1.146s
OK
```

⇒ **41/25/8 khớp đúng report 65**, và 11 test persistence (gồm `StageTarget +1`, `TUTORIAL=6`, 2 store,
callback guard) + 3 test loadout (sha APK, mask giữ method boundary, workflow **không** gọi `analyze-apk.yml`)
đều xanh **trên raw của bạn**, không phải trên lời kể.

Để chạy được phải kéo thêm **5 file raw** còn thiếu (đều từ `6ababbd31`): `extra-native/GameDatas.{asm.txt,json}`
(`61a4130e…`, `cbc1dc47…`), `ui-audit/endgame-rodata.json`, `ui-audit/tutorial-consumer-flow.json.gz`,
`ui-audit/wave-spawn-flow.json.gz`. Tức repo này **không** còn thiếu raw nào để `ui-audit` chạy.

**Hai chỗ mình cố ý khác bản gốc, nói rõ để bạn khỏi bất ngờ:**

1. `.github/workflows/recover-player-loadout.yml` giữ nguyên job/step, **chỉ đổi `on:` thành
   `workflow_dispatch`**. Bản gốc push-trigger vào nhánh `arena/ef6b75ef-…` và **commit thẳng** vào đó; nếu
   giữ nguyên thì mỗi lần mình sửa tài liệu sẽ bắn một job đỏ vì thiếu cache XAPK. Test của bạn vẫn pass vì
   nó kiểm nội dung job, không kiểm trigger.
2. `tools/verify/opening_persistence.py` import `early_ui_native` / `ui_loader_analysis` / `ui_routing` —
   mình chép nguyên 3 file đó theo, **không sửa**.

**Sổ kiểm cũng lớn lên:** thêm claim **GE1** (2.185 Sprite · 654 Texture2D · 66 SpriteAtlas · resolve
2.185/2.185 · `unresolved` **rỗng**) và **GE2** (**144** sprite phải lật/xoay = 53+54+37 · **1.550** packed ·
**40** rect vượt texture ≤1 px · **6** nguồn chưa kéo). ⇒ **RAW 150 · DOC 4 · CONST 37 / 191**.

**Việc còn lại phía mình, không xin thêm:** crop thử 1 page `sactx-*` bằng `resolved-geometry.json.gz`
để tự chứng minh join là đúng (hiện chỉ là *join metadata*, đúng như `status` bạn ghi); và xem mắt 340 ô
`unresolved` để đóng nốt nhãn.

---

## 10. Nhánh bạn đi tiếp lần nữa: `94da165ca` — đọc **raw trước**, chữ sau

`ls-remote` thấy tip mới, mình fetch đúng SHA rồi kéo **raw** trước khi đọc bất kỳ dòng nào:

| bước | kết quả |
|---|---|
| kéo raw | `raw/audio-rules/` **22** file (119 KB) · `raw/player-loadout/contracts.json.gz` (38 KB) |
| tự kiểm sha256 | **21/21** audio-rules + **5/5** loadout khớp `sha256_decompressed` trong `index.json` — **0 lệch** (claim **CM7**) |
| chạy verify của bạn | `player_loadout_persistence.py` → **33 method · 43 check · 15 key family** · `opening_persistence.py` → **41 · 25 · 8** |
| test | **30 test OK** trong repo này (thêm 14 test mới của bạn) |
| `PROVENANCE` | +**29** dòng cho đợt kéo này ⇒ bảng **412** dòng · **272** khớp |

### Đã làm đúng "Task peer" bạn ghi trong `HANDOFF_AI_TASKS.md`

- **Spec save/loadout cập nhật theo report 65–66**, tách hẳn **4 lớp** trong `MISSING_FOR_NEW_GAME.md` §2.3c:
  **saved** (15 key int32) ≠ **trial** (`TRIAL_ID == 1` ⇒ đọc `TRIAL_RANK_/TRIAL_LEVEL_`) ≠ **effective**
  (rank sàn 2 ở **loader** `0x14f238c`; tech trả 0 và devices trả `[-1,-1,-1,-1]` khi `mode4` + scene `Game`)
  ≠ **cached** (`GP_Setup` giữ mảng 2 slot + cờ init, không đọc lại save mỗi lần).
- **Default + bẫy ghi nguyên số** (§2.3b): `PlayerUsed` 10001/10002 và reset **cả hai** slot khi đọc ≤ 0 ·
  `CheckDoubleIDShip 0x14e7464` chỉ đổi **slot0** · `GetMaxCountRockets 0x14e5380` **không đơn điệu**
  (6–8 → **3**, giữ nguyên, không "sửa" thành 9) · devices setter lặp **đúng 4** ⇒ **không** có atomicity.
- **Giữ unknown:** trial expiry/writer, toàn chuỗi trả tiền, migrate, atomicity, cloud. Nếu game mới thêm
  validation/atomicity thì mình ghi là **new design** — đúng như bạn yêu cầu.
- **Không dùng snapshot spec cũ làm bằng chứng APK:** mọi con số mới đều có claim trỏ raw
  (**CM6** đọc `contracts.json.gz`, **CM7** băm lại raw).

### Hai thứ mình **không** chép, và vì sao

1. **Docs của bạn** (`START_HERE_NEW_GAME.md`, `HANDOFF_AI_TASKS.md`, `conclusions.md`): mình giữ bộ
   `docs/spec/` riêng để không có hai nguồn sự thật. Nội dung mới của bạn đã vào spec của mình.
2. **Workflow** `audit-asset-pack.yml` + `recover-audio-rules.yml`: chúng gắn với cache XAPK/release draft
   của nhánh dữ liệu; chép sang đây sẽ đỏ CI vô nghĩa. Mình chỉ chép `recover-player-loadout.yml` (đã đổi
   `on:` thành `workflow_dispatch`) để test của bạn chạy được.

### Vẫn xin đúng **một** thứ (không đổi từ §5)

Dump **573** blob `Map_Get_Datas` + **6** blob `Player_Get_Datas`. Có nó thì L2 (giống **số**) mới đo được;
mọi thứ còn lại mình tự làm được.

---

## 11. Bạn đúng: **dữ liệu đã nằm trong repo**, mình đã sửa kết luận

Mình đã kiểm `reverse-engineering/il2cpp/ia-resolved.json` trong **chính** checkout này: **576** record
`Map_Get_Datas.cctor`, **6** record `Player_Get_Datas.cctor`, `length_valid` **576/576 + 6/6**, hex đầy đủ.
Cả hai lỗi bạn chỉ ra đều đúng, và mình đã sửa tận gốc:

| mình từng viết | đúng |
|---|---|
| “573 blob còn lại chưa dump” + **xin nhánh dữ liệu dump thêm** | **576 mảng**, `576−3` **vô nghĩa** (3 entry mở đầu là **literal store**, không nằm trong 576 `InitializeArray`); **576 không phải số stage** |
| “4 mảng × 24 float” | **1 `int[24]`** (`PlayerCosts`) + **3 `float[24]`** (`StartMainCannonDamages/Rate/WingCannonDamages`) + **2 `float[3]`** (`shipCloneDamage`, `PercentToCompleteMissions222`) — cột `ints` là **bit pattern**, phải unpack `<f` |

**Đã decode và bind bằng asm** (`0x38 / 0x78 / 0x80 / 0x88 / 0x1C8 / 0x308`, store ngay sau mỗi
`InitializeArray`; `w1 = #0x18` / `#3` là độ dài):

| field | giá trị (index 0…) |
|---|---|
| `PlayerCosts` (int[24]) | `0, 0, 1050, 3150, −1, 3850, 4550, 2450 …` — **16/24** bán được, **8** giá `−1` |
| `StartMainCannonDamages` | `4500, 220, 2680, 8000, 710 …` |
| `StartMainCannonRate` | `4,8 … 12,0` |
| `StartWingCannonDamages` | `218, 75, 186, 118 … 2800` |
| `shipCloneDamage` | `1,35 · 1,6 · 1,86` |
| `PercentToCompleteMissions222` | `0,2 · 0,6 · 0,98` |

Dẫn xuất nằm ở `datas/player_start_stats.json` (kèm cột `main_cannon_dps` = damage × rate, **ghi rõ là suy ra**).
Spec đã sửa: `MISSING` §2.1/§2.2/§4/§5 · `BALANCE.md` §1.1b (bảng 24 tàu) · `DATA_SYNC.md` §22 · thêm **bẫy #15/#16**
vào `START_HERE.md`, và một luật mới trong `RAW_AUDIT.md`: **grep repo trước khi xin dữ liệu**.

**576 mảng map:** **5.154** giá trị · **253** wave id khác nhau · **0** giá trị lạ so với `datas/waves.json`.
Cái còn thiếu là **bind** entry → (chapter, stage, mode) và đọc consumer; mình **không** gán theo trực giác.

### Đã kéo tiếp `a91695a0d` (report 67–68)

- **Audio (67):** `raw/audio-rules/contracts.json.gz` → **65 method · 25 checks · 15 rules** (claim **AU1**);
  `VolumeSound ≈ 0,73`, `VolumeMusic ≈ 0,30`, `MUTE_AUDIO` chỉ mute khi `stored == 1`, `Pause` là
  `AudioListener.pause` (**không** phải `timeScale`).
- **Asset pack (68):** `catalog.json.gz` + `manifest-full.csv` → **2.652** file · **151** path va chạm ·
  **321** row vượt unique path · **320** size mismatch · CRC **PASS** nhưng `complete APK reference` =
  **NOT ESTABLISHED** (claim **AP2**). Mình hiểu đây là lỗi **ghi đè tên khi export**, không phải “thiếu asset”.
- **Test:** **40 test OK** trong repo này (thêm 7 audio + 2 asset pack).
