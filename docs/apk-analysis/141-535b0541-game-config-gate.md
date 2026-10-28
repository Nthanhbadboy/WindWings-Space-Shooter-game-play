# 141 — `GameConfig`: class sau slot `0x2ADBB88`, và cổng mở Arena/PvP thật sự kiểm gì

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY; giá trị `GameConfig` do server đẩy về lúc chạy là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_game_config_gate.json.gz` (3062 B, sha256 `241dfc87719d1730d4a31af9f2ffe288ff908b700d8f2c503eacd13b70456774`)
**Báo cáo trước:** 140 (chuỗi cổng `Board_Arena.IECheckArenaOpen` — báo cáo này sửa một hằng số của 140), 139 (`ArenaManager` statics), 138 (cổng fail-closed).
**Verifier:** `tools/verify/game_config_gate.py` · **Test:** `tests/test_game_config_gate.py` (39 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | Bằng chứng |
|---|---|---|
| Slot của cổng là gì? | **`0x2ADBB88` = 44940168** (không phải `0x2ADB8E0`) | `slot_ref` @22810712 / 22810728 / 22811040 |
| Class sau slot? | **`GameConfig`** (TypeDefIndex 34) | §2 |
| Có mấy field? | **9**, `0x0 … 0x24` | `dump.cs` |
| Bao nhiêu class có statics trong dump? | **128**; khớp bố cục `int@0 + bool@4 + int@8`: **1** | §2 |
| Ai đọc slot? | **5** method: 2 Arena + 2 PvP + 1 `ArenaHub` | §3 |
| Field `+4` là gì? | **`isEmpty`** — không phải cờ "đang mở" cục bộ | §2, §3 |
| Field `+0` / `+8`? | `versionCode` / `lastestVersionCode` | §2, §4 |
| Luật cập nhật? | **`lastestVersionCode > versionCode`** ⇒ cần update | §4 |
| `isEmpty == true` thì sao? | gọi lại **`GetGameConfig(callback)`** (nạp lại cấu hình) | §5 |
| `isEmpty == false` thì sao? | sang so **cặp version**; nếu không lỗi thời ⇒ `CheckArenaUser` / `CheckPvPUserRequestAccess` | §4, §5 |
| Ai ghi `GameConfig`? | `GameConfig..cctor`, `ConfigStruct.SetupDatas`, `ConfigStruct.ReplaceDatas` — **0/3 body trong raw đã pin** | §6 |
| Giá trị `versionCode`, `isEmpty`, gift code? | **không đọc được** — `MODEL_NOT_MEASURED runtime` | §7 |

**Một câu:** cổng mở Arena/PvP **không** dựa vào một cờ cục bộ nào cả — sau khi `ArenaConfig.IsOpen` (140) qua, nó đòi **`GameConfig.isEmpty == false`** (tức là **đã tải xong cấu hình game từ server**) rồi so **`lastestVersionCode` với `versionCode`**; chỉ khi client không lỗi thời thì mới chạy bước kiểm user (`CheckArenaUser` / `CheckPvPUserRequestAccess`). Và slot thật là **`0x2ADBB88`**, không phải `0x2ADB8E0` như 140 ghi.

---

## 1. Đính chính 140: slot là `0x2ADBB88` (44940168)

140 ghi *"class sau slot `0x2ADB8E0` (44939488)"*. Quét theo slot đó trên **cả 8 raw** trả về **0 hit** — vì **không instruction nào** deref nó. Operand thật trong `Board_Arena.<IECheckArenaOpen>d__55.MoveNext`:

```asm
22810704  adrp x21, #0x2adb000
22810708  ldr  x21, [x21, #0xb88]    ; 0x2ADB000 + 0xB88 = 0x2ADBB88
22810712  ldr  x0,  [x21]            ; slot_ref.slot_va = 44940168
22810716  ldr  w8,  [x0,  #0xe0]     ; byte "đã init class" của klass
22810728  ldr  x0,  [x21]
22810732  ldr  x8,  [x0,  #0xb8]     ; klass -> statics
22810736  ldrb w9,  [x8,  #4]        ; GameConfig.isEmpty
```

Raw ghi `slot_va = 44940168` cho **cả ba** chỗ 22810712, 22810728, 22811040. Nguyên nhân sai: 140 dùng lại hằng `0x2ADB8E0` của 138 thay vì đọc operand của chính instruction mình vừa pin. Hệ quả: `+4` là `isEmpty` (trạng thái cấu hình), **không** phải cờ mở bảng.

> `0x2ADB8E0` vẫn tồn tại và vẫn được hai bảng dùng (ví dụ `slot_ref` @22810480 / 22810756), nhưng nó là **slot khác**; đặt tên cho nó là việc riêng (§7).

---

## 2. Danh tính: `GameConfig` khớp **duy nhất** theo bố cục

`dump.cs` TypeDefIndex 34:

| Offset | Field | Kiểu | Ghi chú |
|---:|---|---|---|
| `0x00` | `versionCode` | `int` | version đang chạy |
| `0x04` | **`isEmpty`** | `bool` | cờ cấu hình rỗng |
| `0x05` | `backupAvailable` | `bool` | |
| `0x06` | `restoreAvailable` | `bool` | |
| `0x08` | `lastestVersionCode` | `int` | version mới nhất server biết |
| `0x10` | `allVersionsAreRequiredToUpdate` | `string` | |
| `0x18` | `allVersionsAreRemindedToUpdate` | `string` | |
| `0x20` | `hasGiftCode` | `bool` | |
| `0x24` | `GemCode` | `int` | |

Phép đo: quét **128** class có field `static` trong `dump.cs`, đòi `int@0`, `bool@4`, `int@8` — **đúng 1** class khớp: `GameConfig`. Không dùng heuristic tên; bố cục là phép thử, và các reader (§3) chỉ chạm đúng `0`, `4`, `8` như bố cục dự đoán.

---

## 3. Năm reader của slot `0x2ADBB88`

| Method | RVA | Size | Truy cập đo được |
|---|---:|---:|---|
| `Board_Arena.<IECheckArenaOpen>d__55.MoveNext` | 22810128 | 1068 | `ldrb +4` @22810736 |
| `Board_Arena.<>c__DisplayClass55_0.<IECheckArenaOpen>b__4` | 22806816 | 480 | `ldrb +4` @22806980 · `+8` @22807152 · `+0` @22807156 |
| `Board_PVP.<IECheckPvPOpen>d__74.MoveNext` | 19817328 | 1068 | `ldrb +4` @19817916 |
| `Board_PVP.<>c__DisplayClass74_0.<IECheckPvPOpen>b__4` | 19803208 | 496 | `ldrb +4` @19803356 · `+8` @19803544 · `+0` @19803548 |
| `ArenaHub.<>c__DisplayClass20_0.<CheckLastestGameVersion>b__0` | 22680000 | 156 | `+8` @22680092 · `+0` @22680096 |

**0 phép ghi** trong cả 5 (artifact `writers.pinned = 0`, `readers` toàn `read`). Hai `MoveNext` chỉ đọc `+4` rồi nhảy sang khối khác — khối version nằm ở nhánh kia của cùng method (§4), nên bộ quét tuyến tính không gán được role qua branch; vì thế §4 dùng phép dò **không phụ thuộc thanh ghi**.

---

## 4. Luật version — đo, không suy từ tên

`ArenaHub.<>c__DisplayClass20_0.<CheckLastestGameVersion>b__0` (RVA 22680000, 156 B):

```asm
22680084  ldr  x0, [x21]
22680088  ldr  x8, [x0, #0xb8]     ; statics
22680092  ldr  w9, [x8, #8]        ; lastestVersionCode
22680096  ldr  w8, [x8]            ; versionCode
22680100  cmp  w9, w8
22680104  cset w1, le              ; kết quả = (lastest <= current)
```

và ba chỗ còn lại dùng đúng cặp đó với `b.le`:

| Method | `+8` | `+0` | `cmp` | nhánh | đích |
|---|---:|---:|---:|---|---:|
| `ArenaHub…b__0` | 22680092 | 22680096 | 22680100 | `cset w1, le` | — |
| `Board_Arena…b__4` | 22807152 | 22807156 | 22807160 | `b.le` | 22807276 |
| `Board_Arena…MoveNext` | 22811048 | 22811052 | 22811056 | `b.le` | 22811180 |
| `Board_PVP…b__4` | 19803544 | 19803548 | 19803552 | `b.le` | 19803684 |
| `Board_PVP…MoveNext` | 19818236 | 19818240 | 19818244 | `b.le` | 19818380 |

`b.le` ⇒ nhảy khi `lastestVersionCode <= versionCode`; **rơi xuống** (fall-through) là `lastest > current` = **cần cập nhật**. Nhánh cập nhật của cả hai bảng đều gọi helper thông báo **RVA 34325296** (`0x20BC330`, chưa có tên trong raw) sau `SetLoading(false)` (RVA 19787504); nhánh "không lỗi thời" của `MoveNext` gọi tiếp bước kiểm user:

* Arena: **`CheckArenaUser` RVA 22782848**
* PvP: **`CheckPvPUserRequestAccess` RVA 19789004**

---

## 5. Cổng `isEmpty` — 4 chỗ, cùng một cực

| Method | đọc `isEmpty` | nhánh | nhảy khi | nhánh rơi xuống (isEmpty = **true**) |
|---|---:|---|---|---|
| `Board_Arena…MoveNext` | 22810736 | `cbz w9` | `isEmpty` = false | `GetGameConfig(Action<bool>)` **RVA 22798808** @22810796 |
| `Board_Arena…b__4` | 22806980 | `cbz w9` | `isEmpty` = false | `0x16F4F54` @22807028 → thông báo |
| `Board_PVP…MoveNext` | 19817916 | `cbz w9` | `isEmpty` = false | `GetGameConfig` **RVA 19787640** @19817980 |
| `Board_PVP…b__4` | 19803356 | `cbz w9` | `isEmpty` = false | `0x16F4F54` @19803420 → thông báo |

Đích của `cbz` trong hai `MoveNext` (22811028 / 19818212) nằm **ngay trên** khối so version của cùng method (cách 228 / 32 byte) — đó là lý do câu "cổng cấu hình rồi mới tới cổng version" là **số đo**, không phải diễn giải.

Hình đầy đủ của `Board_Arena.<IECheckArenaOpen>d__55.MoveNext` (RVA 22810128):

```text
GetConfigs()                                   @22810700
klass GameConfig (slot 0x2ADBB88) -> statics
if (!isEmpty) goto VERSION                     @22810740 (cbz -> 22811028)
else GetGameConfig(callback)                   @22810796   ; cấu hình rỗng -> nạp lại
VERSION:
  if (lastestVersionCode > versionCode)        @22811056 (b.le -> 22811180)
      SetLoading(false) + thông báo 34325296
  else CheckArenaUser()                        @22782848
```

PvP là bản sao cùng hình, thay `CheckArenaUser` bằng `CheckPvPUserRequestAccess`.

> **Đính chính cách đọc của 140:** 140 viết "khi `isEmpty` là false thì luồng dừng". Theo instruction: `cbz` nhảy khi `isEmpty == false` và đích nhảy **là khối so version** (luồng đi tiếp), còn nhánh `isEmpty == true` mới là nhánh nạp lại cấu hình / hiện thông báo. Cả hai đều là "chặn mở bảng", nhưng chiều cờ bị ngược trong ghi chú cũ.

---

## 6. Phía ghi — 3 body, **0** cái nào trong raw đã pin

| Class.Method | RVA | Trong 8 raw? |
|---|---:|:--:|
| `GameConfig..cctor` | 19082168 | ✘ |
| `ConfigStruct.SetupDatas` | 19042256 | ✘ |
| `ConfigStruct.ReplaceDatas` | 19049040 | ✘ |
| `ConfigStruct..ctor` | 19042376 | ✘ |

`ConfigStruct` (TypeDefIndex 35) là bản sao instance của cùng dữ liệu, offset lệch `0x10`:

| `ConfigStruct` | Offset | ứng với `GameConfig` |
|---|---:|---|
| `BackupAvailable` | `0x10` | `backupAvailable` @`0x05` |
| `RestoreAvailable` | `0x14` | `restoreAvailable` @`0x06` |
| `LastestVersionCode` | `0x18` | `lastestVersionCode` @`0x08` |
| `AllVersionsAreRequiredToUpdate` | `0x20` | cùng tên @`0x10` |
| `AllVersionsAreRemindedToUpdate` | `0x28` | cùng tên @`0x18` |

Tức `SetupDatas` là bước copy `ConfigStruct` → `GameConfig`; `isEmpty` không có trong `ConfigStruct`, nên nó do loader đặt (đúng/sai tuỳ có tải được hay không) — phần đó **chưa đo được**.

---

## 7. `not_decoded` (2 mục)

| Mục | Bước chặn |
|---|---|
| Giá trị `GameConfig` (`versionCode`, `lastestVersionCode`, `isEmpty`, 2 chuỗi update, `hasGiftCode`, `GemCode`) | `GameConfig..cctor` RVA **19082168**, `ConfigStruct.SetupDatas` RVA **19042256**, `ConfigStruct.ReplaceDatas` RVA **19049040** không có trong 8 raw đã pin; dữ liệu đến từ JSON server lúc chạy — **`MODEL_NOT_MEASURED runtime`** |
| Class sau slot `0x2ADB8E0` (44939488) | slot hàng xóm, được hai bảng dùng (`slot_ref` @22810480 / 22810756) nhưng không có truy cập nào qua nó được decode ở đây; đặt tên cần một lượt riêng |

---

## 8. Tái lập

```bash
python3 tools/verify/game_config_gate.py            # in bytes/sha256 + reader/version/field
python3 -m unittest tests.test_game_config_gate       # 39 test
python3 tools/verify-claims.py --require AB,AO,AP
```

`evidence: STATIC_ONLY_ORIGINAL_APK` · nguồn: `arena-pvp-535b0541/native.json.gz`,
`reverse-engineering/il2cpp/dump.cs.gz`, `reverse-engineering/il2cpp/stringliteral.json` (đã đối chiếu, không chứa dữ liệu `GameConfig`).

---

`provenance:` APK gốc `535b0541` → `libil2cpp.so` → raw `arena-pvp-535b0541` (`Board_Arena.IECheckArenaOpen`, `Board_PVP.IECheckPvPOpen`, `ArenaHub.CheckLastestGameVersion`) → `dump.cs` (bố cục `GameConfig`/`ConfigStruct` + chữ ký callee) → verifier → artifact 3062 B `241dfc87…` → 39 test. Không emulator/probe/device.
