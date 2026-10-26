# 142 — Slot `0x2ADB8E0` = ô klass của `UnityEngine.Application`, và bốn API engine game thật sự gọi

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY; mọi giá trị `Application.*` trả về trên máy là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_application_cell.json.gz` (3669 B, sha256 `d618b7401b81dc3119cc11d43687aec3e33707ddabbe56664c993c4bd5518f07`)
**Báo cáo trước:** 141 (`GameConfig` sau slot `0x2ADBB88` — báo cáo này đóng `not_decoded` thứ hai của 141), 138 (`ArenaManager.get_pathRoot` ba nhánh), 128 (`GameDatas` sentinel trong `.cctor`).
**Verifier:** `tools/verify/application_cell.py` · **Test:** `tests/test_application_cell.py` (42 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | Bằng chứng |
|---|---|---|
| Slot `0x2ADB8E0` là gì? | ô **klass của `UnityEngine.Application`** | §1, §2 |
| Vì sao quét statics ra rỗng? | cell **không bao giờ** bị deref tới statics (`klass+0xB8`); nó chỉ dùng để init class | §1 |
| Bao nhiêu method dùng cell? | **47** cặp (raw, method) = **33** method phân biệt, **92** điểm nạp cell | §2 |
| Bao nhiêu method gọi `Application`? | **47/47** | §2 |
| API nào được gọi? | **4**: `internetReachability` (29) · `companyName` (10) · `OpenURL` (6) · `systemLanguage` (2) | §3 |
| Ngôn ngữ được tặng gift code? | **7**: Danish, English, French, German, Japanese, Korean, Norwegian — **tiếng Việt không có** | §4 |
| Tiền tệ khởi tạo khi chưa có save? | coins **68999**, gems **500**, stars **0**, wingCoins **999999** (hoặc 0) | §5 |
| Vì sao là 68999 chứ không phải 7559? | `mov w1,#0xd87` rồi `movk w1,#1,lsl#16` ⇒ `0x10D87` | §5 |
| `slot_refs` có đủ? | **không** — 45/47; thiếu `Board_PVP.CheckInternet` | §6 |

**Một câu:** slot `0x2ADB8E0` **không phải** một class của game — nó là ô klass của **`UnityEngine.Application`**, và toàn bộ 47 method chạm vào nó đều gọi đúng một static của `Application`; đi theo cell đó ra được ba thứ có ích: **bộ ngôn ngữ được gift code** (7 ngôn ngữ, không có tiếng Việt), **giá trị tiền tệ mặc định** của bốn getter `GameDatas` (đọc `PlayerPrefs.GetInt` sau sentinel `-1`), và **bốn callback mở URL** của popup cổng Arena/PvP.

---

## 1. Cell là con trỏ klass — idiom đo được

```asm
20069640  adrp x8,  #0x2adb000
20069644  ldr  x8,  [x8, #0x8e0]    ; cell = 0x2ADB8E0 = 44939488
20069648  ldr  x0,  [x8]            ; *cell  -> Il2CppClass*
20069652  ldr  w8,  [x0, #0xe0]     ; byte "initialized" của klass
20069656  cbnz w8,  ...
20069660  bl   #0x110d12c           ; helper init
```

và dạng nạp sớm:

```asm
20069544  adrp x0,  #0x2adb000
20069548  ldr  x0,  [x0, #0x8e0]
20069552  bl   #0x110d028           ; helper init, nhận klass
```

Đúng hình 141 đã đọc cho cell **`GameConfig`** `0x2ADBB88` (đã chứng minh độc lập bằng bố cục statics + đường `klass+0xB8`). Vì vậy: **`0x2ADB8E0` là một ô klass**, không phải ô statics — và đó là lý do mọi phép quét statics theo slot trả về rỗng (141 ghi nhận; 142 giải thích).

Tổng hợp idiom trên 92 điểm: `class_init(0x110D028)` **47**, `initialized_flag(klass+0xE0)` **38**, `unclassified` **2** (hai method chỉ nạp cell rồi gọi qua tail `b`, cửa sổ 5 lệnh không bắt được cặp deref).

---

## 2. Danh tính: 47/47 method gọi `Application`

| Raw | Method (cặp raw·method) |
|---|---:|
| `arena-pvp-535b0541` | 23 |
| `meta-rewards-535b0541` | 12 |
| `key-grant-535b0541` | 11 |
| `pack-index-535b0541` | 1 |
| **tổng** | **47** (33 method phân biệt, 92 điểm) |

Phép thử: với mỗi method chạm cell, tra **mọi** đích `bl`/`b` trong `dump.cs` rồi xem class khai báo. **47/47** method có ít nhất một static của `UnityEngine.Application`; **không** method nào chạm cell mà chỉ gọi static của class khác. Đó là cơ sở đặt tên — không dựa vào tên field hay đoán từ tên hàm.

Phân bố theo class: `GameDatas` 10 · `Board_PVP` 6 · `Board_PVP.<>c__DisplayClass74_0` 4 · `ArenaManager` 4 · `Board_Arena` 4 · `PVP_Endgame.<>c` 3 · còn lại 1–2.

---

## 3. Bốn API `Application` game thật sự dùng

| API | RVA | Số method | Dùng ở đâu (đo được) |
|---|---:|---:|---|
| `get_internetReachability` | 41274720 | **29** | `ArenaHub.IsNetworkConnected`, `Board_Arena.NoInternet`/`CheckBanStatus`/`Refresh`, `Board_PVP.CheckInternet`, `ArenaManager.LoadRemoteConfigs`, `PVP_Manager.LoadRemoteConfigs`, `Board_EventSeasonPass`, `Popup_WatchVideos`, `Board_ShopEnergy`, `PVP_Endgame.<>c` |
| `get_companyName` | 41274380 | **10** | `ArenaManager.get_pathRoot` (138 §2) + 4 getter tiền tệ `GameDatas` (mỗi cái 2 raw) |
| `OpenURL` | 41274460 | **6** | 4 callback `<IECheckArenaOpen>b__5/b__7` (22807584/22807296) và `<IECheckPvPOpen>b__5/b__7` (19803992/19803704) |
| `get_systemLanguage` | 41274680 | **2** | `GameDatas.IsHasGiftLanguages` (cùng một method ở 2 raw) |

`OpenURL` có đối số đo được: các callback `b__5`/`b__7` gọi `GameHyperlinks.get_LinkRateUs()` (RVA **21099172**) rồi **tail-call** `Application.OpenURL(url)` sau `OnPressedButtonBack()` (Arena 22783988 / PvP 19780904). Tức: nút trong popup đóng bảng và mở **link rate-us**; *popup đó là hộp "cần cập nhật" hay "mời đánh giá" thì chưa decode* (§7).

---

## 4. `GameDatas.IsHasGiftLanguages` (RVA 20071724) — 7 ngôn ngữ, **không có tiếng Việt**

```text
lang = Application.get_systemLanguage()
lang == 10 (English)   -> true      @20071796
lang == 15 (German)    -> true      @20071828
lang == 23 (Korean)    -> true      @20071860
lang == 22 (Japanese)  -> true      @20071892
lang == 26 (Norwegian) -> true      @20071924
lang ==  8 (Danish)    -> true      @20071956   (`cmp #8` + `b.ne`, chiều ngược)
else -> return lang == 14 (French)  @20072004   (`cset w0, eq`)
```

Bảng giá trị lấy **trực tiếp** từ `enum SystemLanguage` trong `dump.cs` (TypeDefIndex 7675), không từ ký ức:

| Giá trị | Tên |
|---:|---|
| 8 | Danish |
| 10 | English |
| 14 | French |
| 15 | German |
| 22 | Japanese |
| 23 | Korean |
| 26 | Norwegian |

**Tiếng Việt = 39, không nằm trong tập** ⇒ người chơi đặt máy tiếng Việt **không** nhận gift code ngôn ngữ. Đây là kết luận từ đúng dãy so sánh, không phải từ tên hàm.

---

## 5. Bốn getter tiền tệ `GameDatas` — `PlayerPrefs.GetInt` sau sentinel `-1`

`PlayerPrefs.GetInt(string key, int defaultValue)` = RVA **41405600**. Mỗi getter có **hai** điểm gọi (nhánh thường và nhánh `companyName == "Test"`):

```text
if (GameDatas.<cache> == -1)                        ; sentinel, 128 §3.5
    GameDatas.<cache> = PlayerPrefs.GetInt(key,
        Application.companyName == "Test" ? <cheat field> : <hằng số>)
return GameDatas.<cache>
```

| Getter | RVA | cache | cheat field | mặc định (nhánh thường) | key cell | điểm gọi |
|---|---:|---:|---:|---:|---:|---|
| `get_Coins` | 20069516 | `0x44` | `cheatCoins 0x14` | **68999** | 44941536 (`0x2ADC0E0`) | 20069720 / 20069800 |
| `get_Gems` | 20068904 | `0x48` | `cheatGems 0x18` | **500** | 44941496 (`0x2ADC0B8`) | 20069104 / 20069184 |
| `get_StarCount` | 20075932 | `0x4C` | `cheatStars 0x1C` | **0** | 44941512 (`0x2ADC0C8`) | 20076132 / 20076212 |
| `get_WingCoins` | 20070312 | `0x5C` | — (không có nhánh cheat) | **999999** / **0** | 44941776 (`0x2ADC1D0`) | 20070532 |

**Bẫy số học:** coins **không phải** 7559. Hai lệnh `mov w1,#0xd87` (3463) và `movk w1,#1,lsl#16` ghép thành `0x10D87` = **68999**; đọc vội `#0xd87` như `0x1D87` là sai 8,6 lần. Tương tự `0x423F` + `0xF<<16` = `0xF423F` = **999999** (wingCoins). Bộ trích trong verifier đọc **cả cặp** `mov`+`movk`, và test khoá đúng con số 68999 để không ai "sửa" về 7559.

Field `0x14/0x18/0x1C` là `cheatCoins/cheatGems/cheatStars` trong `GameDatas` (TypeDefIndex 249) — nên nhánh `companyName == "Test"` là **nhánh bản thử nghiệm**, không phải nhánh người chơi.

---

## 6. Ghi chú bằng chứng: `slot_refs` **không** đầy đủ

| Đo | Số |
|---|---:|
| Method nạp cell (quét instruction: `adrp 0x2ADB000` + `ldr #0x8E0`) | **47** |
| Method có `slot_refs.slot_va == 44939488` | **45** |
| Thiếu | **2** — đều là `Board_PVP.CheckInternet` (RVA 19787760) |

`CheckInternet` nạp cell ở 19787792–19787812 rồi gọi `Application.get_internetReachability` ở 19787868, nhưng raw **không** ghi `slot_ref` cho lần nạp đó. Hệ quả phương pháp: **`slot_refs` là chỉ mục, không phải bằng chứng vắng mặt** — 141 đã dùng đúng nguyên tắc này khi bác slot `0x2ADB8E0`; 142 ghi lại thành số đo thay vì lời.

---

## 7. `not_decoded` (2 mục)

| Mục | Bước chặn |
|---|---|
| `Application.*` trả gì trên máy (ngôn ngữ thiết bị, reachability, companyName) | chỉ đọc lúc chạy; APK chỉ có call site — **`MODEL_NOT_MEASURED runtime`** |
| Chuỗi key `PlayerPrefs` của 4 getter | literal nằm trong các ô string `0x2ADC0B8 / 0x2ADC0C8 / 0x2ADC0E0 / 0x2ADC1D0`, không ô nào có `addend` gắn với một deref đã pin ⇒ chưa đọc được chữ |
| Popup nào chứa 4 callback `OpenURL` | có link rate-us và `OnPressedButtonBack`, nhưng chưa decode chuỗi thông báo của popup ⇒ chưa gọi tên hộp thoại |

---

## 8. Tái lập

```bash
python3 tools/verify/application_cell.py              # in bytes/sha256 + đếm method/API/gift
python3 -m unittest tests.test_application_cell        # 42 test
python3 tools/verify-claims.py --require AB,AO,AP
```

`evidence: STATIC_ONLY_ORIGINAL_APK` · nguồn: 8 raw `reverse-engineering/raw/*/native.json.gz`,
`reverse-engineering/il2cpp/dump.cs.gz` (RVA → class của mọi callee + `enum SystemLanguage`),
`reverse-engineering/il2cpp/stringliteral.json` (chuỗi so sánh).

---

`provenance:` APK gốc `535b0541` → `libil2cpp.so` → 4 raw có cell (`arena-pvp`, `meta-rewards`, `key-grant`, `pack-index`) → `dump.cs` (class của callee + giá trị `SystemLanguage`) → verifier → artifact 3669 B `d618b740…` → 42 test. Không emulator/probe/device.
