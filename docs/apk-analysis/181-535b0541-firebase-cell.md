# 181 — Slot `0x2ADB958` là ô klass của `FirebaseDatabaseManager`, và toàn bộ đường Firebase của lane

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc, không chạy game, không probe)
**Lớp bằng chứng:** STATIC-ONLY; mọi thứ Firebase trả về trên máy là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_firebase_cell.json.gz` (4379 B, sha256 `a6d4c430fcdfaa2add5de13c7d7082ee9aab7b64809db802ead3c75c7a1c3cce`)
**Verifier:** `tools/verify/firebase_cell.py` · **Test:** `tests/test_firebase_cell.py` (32 test)
**Báo cáo trước:** 142 (`0x2ADB8E0` = ô klass `UnityEngine.Application`), 178 (census 1788 method), 180 (registry-v4).

---

> **ERRATUM 182** — mục `not_decoded` thứ hai của báo cáo này ("the literal text of the path prefixes … not attached to any pinned dereference") **bị rút lại**.
> Text đọc được **tĩnh**: `reverse-engineering/raw/ui-audit/native-relocations.json.gz` (288.733 điểm) ánh xạ ô → con trỏ, và `metadata-index.json.gz` (`ScriptString`) ánh xạ con trỏ → chữ. Báo cáo 182 làm phép tra đó và in ra 27 mảnh đường dẫn + 19 template, gồm cả format string của `SetSummaryDatas`: `{0}/summary-datas/season-{1}/rank-{2}/rooms/roomList/room-{3}`.
> Bảng relocation cũng xác nhận độc lập danh tính của §1: ô `0x2ADB958` → `FirebaseDatabaseManager_TypeInfo` (xem 182 §2).
> Mục audit 43/44/47/53 **vẫn `RUNTIME`** — cái thiếu là payload server, không phải đường dẫn.

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | Bằng chứng |
|---|---|---|
| Slot `0x2ADB958` là gì? | ô **klass của `FirebaseDatabaseManager`** (TypeDefIndex 1485) | §1 |
| Cách nhận danh tính? | idiom klass-cell + static đọc ở **offset `0x0`** đúng bằng field `Instance` khai báo `// 0x0` trong `dump.cs` | §1 |
| Bao nhiêu method / điểm nạp? | **34** method phân biệt, **54** cặp (raw·method), **141** điểm nạp | §2 |
| API nào được gọi? | **6**: `DownloadDatabase` 27 · `UploadDatabase` 20 · `Query` 6 · `DeleteDatabase` 4 · `DownloadDatabaseQueryRank` 1 · `UploadDatabaseObj` 1 (**59** điểm gọi, tính theo method) | §3 |
| Có method nào chạm cell mà **không** gọi API? | **1**: `Board_Arena.<IESignInOrRestoreYourDatas>d__91` (22814532) — vòng chờ singleton | §4 |
| Payload upload được dựng thế nào? | `String.Format` → `JsonParse.ToJson` → `UploadDatabase(path, json, cb)` | §5 |
| `slot_refs` có đủ? | **đủ** — 54/54 (khác 142: 45/47) | §6 |
| Có đóng mục audit nào? | **không** — mục 43/44/47/53 vẫn `RUNTIME`, vì giá trị phục vụ từ Firebase không nằm trong APK | §7 |

**Một câu:** slot `0x2ADB958` **không phải** một class Arena/PvP nào — nó là ô klass của **`FirebaseDatabaseManager`**, và mọi method trong lane chạm vào nó đều đi qua **một** static duy nhất là `Instance` (offset `0x0`) để gọi **sáu** API instance; 59 điểm gọi đó chính là toàn bộ biên Firebase của game, và chỉ có một method là không gọi gì: coroutine sign-in của `Board_Arena` chờ `Instance` bằng `Object.op_Implicit` với hạn `Time.get_time() + 10s`.

---

## 1. Danh tính: ô klass, không phải ô statics

Idiom đo được (giống 141/142 đã đọc cho `GameConfig` và `Application`):

```asm
22687620  adrp x8,  #0x2adb000
22687624  ldr  x8,  [x8, #0x958]    ; cell = 0x2ADB958 = 44939608
22687640  ldr  x8,  [x8]            ; *cell -> Il2CppClass*
22687648  ldr  x8,  [x8, #0xb8]     ; statics
22687652  ldr  x20, [x8]            ; statics + 0x0 = Instance
...
22687668  mov  x0,  x20             ; this = Instance
22687684  bl   #0x142b86c           ; FirebaseDatabaseManager.UploadDatabase
```

Bốn phép thử độc lập, cả bốn đều dương tính:

| Phép thử | Kết quả |
|---|---|
| idiom klass-cell | `ldr xK,[cell]` + byte `initialized` ở `klass+0xE0` + helper `0x110D028` / `0x110D12C` — **54/54** cặp |
| offset statics được đọc | **chỉ `0x0`** trên 30 cặp có đọc statics; không có offset nào khác |
| `statics+0x0` là `this` | `ldr xT,[statics]` rồi `mov x0, xT` ngay trước `bl` của một method instance `FirebaseDatabaseManager` |
| `dump.cs` | `public static FirebaseDatabaseManager Instance; // 0x0` |

`dump.cs` khai báo **đúng một** static trên class này, và nó nằm ở `0x0` — nên "mọi phép đọc statics đều ở `0x0`" là một phép thử có thể sai, không phải chú thích.

Ô lân cận: `0x2ADB8E0` = `UnityEngine.Application` (142), cách **120 byte** = 15 ô klass.

---

## 2. Census: 34 method, 54 cặp, 141 điểm nạp

| Raw | Cặp |
|---|---:|
| `arena-pvp-535b0541` | 34 |
| `meta-rewards-535b0541` | 12 |
| `key-grant-535b0541` | 8 |
| **tổng** | **54** (34 method phân biệt) |

Phân bố theo class (method phân biệt):

| Class | Method | API |
|---|---:|---|
| `ArenaManager` | 4 | `Upload` · `Download` · `Delete` |
| `Board_PVP` | 2 | `Download` |
| `Board_Arena` | 2 | `Download` |
| `Board_RoomPVP` | 2 | `Download` · `UploadDatabaseObj` |
| `ArenaManager.<IECheckUserStatus>d__17` | 1 | `Download` · `Upload` |
| `Board_PVP.<>c__DisplayClass76_0.<<CheckUserSignInOrRestoreYourDatas>g__IESignInOrRestoreYourDatas|1>d` | 1 | `Download` · `Upload` · `Delete` |
| `Board_PVP.<IEAcceptJoinRoom>d__162` | 1 | `Download` · `Upload` |
| `Board_RoomPVP.<IEJoinRoom>d__12` | 1 | `Download` · `Query` · `Upload` |
| 17 coroutine/`<>c__DisplayClass` còn lại | 17 | 1 API mỗi cái |
| `Board_Arena.<IESignInOrRestoreYourDatas>d__91` | 1 | **không** |
| **tổng** | **34** | |

Tên đầy đủ từng method, RVA (thập phân), `size`, số điểm nạp, API và offset statics nằm ở `census.rows` của artifact.

---

## 3. Sáu API, 59 điểm gọi

| API | RVA (thập phân) | Điểm gọi (method phân biệt) | Method chạm |
|---|---:|---:|---:|
| `DownloadDatabase(string path, Action<DataSnapshot>)` | 21150628 | **27** | 20 |
| `UploadDatabase(string path, string jsonValue, Action<bool>)` | 21149804 | **20** | 14 |
| `Query(string path)` | 21152032 | **6** | 2 |
| `DeleteDatabase(string path, Action<bool>)` | 21149616 | **4** | 4 |
| `DownloadDatabaseQueryRank(path, property, limited, cb)` | 21150980 | **1** | 1 |
| `UploadDatabaseObj(string path, object, Action<bool>)` | 21150216 | **1** | 1 |

Artifact ghi cả hai cách đếm: `calls_per_raw` (93 — một method nằm trong hai raw thì đếm hai lần) và `calls_distinct` (**59** — con số nên trích). Tổng 59 không bằng 34 vì 8 method gọi nhiều hơn một API.

Hai helper chưa định danh được nằm ngay trước mỗi call: `0x18A4388` (25838472, 15 method) và `0x18A5580` (25843072, 23 method) — generic instantiation, **không** có dòng RVA trong `dump.cs`, nên artifact ghi `unresolved@0x18a4388` / `unresolved@0x18a5580` chứ không đoán là `Action<bool>..ctor`.

---

## 4. Method duy nhất không gọi API: vòng chờ `Instance`

`Board_Arena.<IESignInOrRestoreYourDatas>d__91` (22814532, `MoveNext`, 2400 B) nạp cell 4 lần, đọc `Instance` ở 22815084, và:

- gọi `UnityEngine.Object.op_Implicit` (41437640) **3** lần — 22814936 / 22815048 / 22815108, tức phép thử `Instance != null` của Unity;
- gọi `UnityEngine.Time.get_time` (41446848) **2** lần — 22814948 / 22814980;
- có `fmov s1, #10.00000000` ở 22814952 — hạn **+10 giây**.

Đọc theo thứ tự lệnh: coroutine **chờ** singleton Firebase được tạo (tối đa 10 giây) rồi mới đi tiếp, chứ không ghi gì lên Firebase. Đây là lý do method này nằm trong census cell mà không nằm trong census API.

Ba method còn lại của nhóm sign-in dùng `FirebaseAuthManager.SignInWithGooglePlayGames` (21141540) — 2 method, không phải API database.

---

## 5. Một use site đọc trọn: `ArenaManager.SetSummaryDatas`

`ArenaManager.SetSummaryDatas(int season, int rank, int roomIndex, Dictionary<string,object> listRanks, Action<bool> callback)` — RVA **22687092**, 636 B:

1. `String.Format(format, object[])` (RVA **33477820**) dựng chuỗi đường dẫn từ ba số `season` / `rank` / `roomIndex`;
2. `JsonParse.ToJson(object)` (RVA **20888684**) chuyển dictionary thành JSON;
3. `FirebaseDatabaseManager.Instance.UploadDatabase(path = chuỗi (1), jsonValue = chuỗi (2), onComplete = callback)`.

Tức payload của đường "summary" là **dictionary → JSON**, còn đường dẫn là **ba khoá số ghép bằng `String.Format`**. Bản thân format string nằm trong một ô string trên page `0x2AEC000` (`+0x9F0`), không phải string literal, nên **text** của prefix không đọc được ở đây (§7).

---

## 6. `slot_refs` đủ — khác 142

Quét lệnh: **54** cặp. Index `slot_refs` của 8 raw: **54**. Thiếu: **0**.

142 phải ghi nhận `slot_refs` thiếu 2/47 và cảnh báo "index không phải phép đo". Với slot này index khớp hoàn toàn — artifact vẫn ghi phép đo làm chuẩn và chỉ ra rằng lần này index đồng ý, để lần sau không ai đọc sự đồng ý đó thành bảo đảm.

---

## 7. Không đóng mục audit nào

Bốn mục audit nhắc tới Firebase — **43**, **44**, **47**, **53** — đều là *giá trị được phục vụ* (`data-leagues`, `data-configs`, `arena---datas/is-open`, remote config ghi đè default). 181 chỉ định danh **ống dẫn** (cell + API + use site), không đọc được nội dung server:

- payload thật: `MODEL_NOT_MEASURED runtime`;
- text của các prefix đường dẫn: các getter `PVP_Manager.get_pathOfDataUsers` và bốn sibling đọc **ô string** trên page `0x2AE0000`, không phải string literal — không có deref nào được ghim nên text không đọc ở đây.

Vì vậy 181 **không** sửa `open_items_audit`, **không** sửa verdict nào; nó chỉ thêm một artifact vào phạm vi `audit_drift` (48 → 49), và đó là toàn bộ cascade của báo cáo này.

---

## 8. Kiểm chứng

```
python3 tools/verify/firebase_cell.py
  → {"bytes": 4379, "sha256": "a6d4c430…", "pairs": 54, "methods": 34, "sites": 141, "calls": 59}
python3 -m unittest tests.test_firebase_cell
  → 30 test OK
```

Artifact tự khẳng định 8 điều kiện trong `build_payload()` (34 method, 54 cặp, 141 điểm, offset statics chỉ `0x0`, 59 điểm gọi API, census API/helper chính xác, vòng chờ có đủ ba dấu hiệu, field `Instance` ở `0x0`), nên một lần đo sai sẽ làm verifier **dừng**, không làm artifact sai đi.

`provenance:` xapk / libil2cpp / dump.cs + `metadata-slots.json` + 8 `native.json.gz`, mỗi file kèm sha256; test `Provenance.test_source_digests_match_workspace` hash lại từ workspace.
