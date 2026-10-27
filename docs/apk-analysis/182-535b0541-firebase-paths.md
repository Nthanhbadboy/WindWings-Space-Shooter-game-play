# 182 — Sơ đồ đường dẫn Firebase của game, đọc tĩnh bằng bảng relocation

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc; không chạy game, không probe)
**Lớp bằng chứng:** STATIC-ONLY. Con số thay vào template và giá trị server trả về vẫn là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_firebase_paths.json.gz` (7371 B, sha256 `3dcbbb832ccf6a0e47817f31834e40b40eec80b24af0f69e361bae19aa1baa16`)
**Verifier:** `tools/verify/firebase_paths.py` · **Test:** `tests/test_firebase_paths.py` (28 test)
**Báo cáo trước:** 181 (ô klass `0x2ADB958` = `FirebaseDatabaseManager` — báo cáo này **đính chính** một mục `not_decoded` của 181), 138 (`get_pathRoot` ba nhánh), 142.

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | Bằng chứng |
|---|---|---|
| Đọc text của ô string bằng gì? | **hai bảng đã có trong workspace**: `native-relocations.json.gz` (288.733 điểm) + `metadata-index.json.gz` (`ScriptString` 15.054) | §1 |
| 181 nói "không có deref nào được ghim" có đúng? | **không** — câu đó quá mạnh; `cell → relocation → ScriptString` là tra bảng, không cần `.so` | §1 |
| Slot `0x2ADB958` là gì, theo bảng relocation? | `FirebaseDatabaseManager_TypeInfo` — **xác nhận độc lập lần thứ 5** cho 181 | §2 |
| Gốc PvP? | **`data-leagues`** (hằng, `PVP_Manager.get_pathRoot` 19859292) | §3 |
| Gốc Arena? | ba nhánh: `arena-test-datas` (`companyName=="Test"`) · `arena--datas` (`VersionControlSystem.PREMIUM`) · `arena---datas` | §3 |
| Năm getter `get_pathOf*` làm gì? | `String.Concat(gốc, literal)` — 5/5 có đúng **một** `Concat` | §3 |
| Bao nhiêu mảnh đường dẫn / template? | **27** mảnh path-ish · **19** template (16 path + 3 log/id) · **179** literal phân biệt trong 34 method | §4 |
| Payload của `SetSummaryDatas` là gì? | `{0}/summary-datas/season-{1}/rank-{2}/rooms/roomList/room-{3}` — **đọc được chữ** | §4 |
| Có gì thú vị ngoài đường dẫn? | pool **108** tên máy ảo PvP (có tên tiếng Việt) trong `IEUploadMachineDatas` | §5 |
| Mục audit 53? | **đối chiếu được tĩnh** nhưng vẫn `RUNTIME` (payload không nằm trong APK) | §6 |

**Một câu:** mọi prefix Firebase của game — `data-leagues` + 5 nhánh, `arena---datas` (và hai biến thể) + `summary-datas`/`rank-datas`/`rank-configs`/`is-open`, cùng các đường cũ `Data-Users/`, `BackupDatas/`, `ban-accounts/` — đều **đọc được chữ** bằng cách tra hai bảng có sẵn, nên 181 đã ghi quá bi quan; báo cáo này thay câu "không đọc được" bằng 27 mảnh đường dẫn và 19 template kèm cell, target và method dùng.

---

## 1. Cách giải: hai bảng, không cần `.so`

Ô string trên các page `0x2ADB000` / `0x2AE0000` / `0x2AEC000` không chứa ký tự; nó chứa **một con trỏ**. Chuỗi giải là:

```
cell VA ──(native-relocations.json.gz: 288.733 điểm)──► target VA
        ──(metadata-index.json.gz: ScriptString 15.054 / ScriptMetadata 10.758)──► text
```

Ví dụ nguyên văn:

| cell (thập phân) | target | kết quả |
|---|---|---|
| `45009312` (`0x2AEC9A0`) | `46051744` | `arena-test-datas` |
| `45009320` (`0x2AEC9A8`) | `46051720` | `arena---datas` |
| `45009328` (`0x2AEC9B0`) | `46051728` | `arena--datas` |
| `44961064` | `45975784` | `/data-users` |
| `45009400` (`0x2AEC9F8`) | `46086200` | `{0}/summary-datas/season-{1}/rank-{2}/rooms/roomList/room-{3}` |

Không có bước nào là suy đoán: cả hai bảng đều là dữ liệu của chính APK (`native_sha256` = `9cb038e8…`), và mỗi dòng trong artifact giữ **cả ba** mốc (cell, target, text) để người đọc đi lại được chuỗi.

### Đính chính 181

181 §7 ghi: *"các getter … đọc **ô string** trên page `0x2AE0000`, không phải string literal — không có deref nào được ghim nên text không đọc ở đây"*. Vế đầu đúng, vế sau **sai**: "chưa ai ghim deref" không đồng nghĩa "không deref được". Bảng relocation chính là phép deref đó, và nó đã nằm trong workspace từ trước. 182 rút lại mục `not_decoded` thứ hai của 181; khối `ERRATUM 182` đã được thêm vào đầu báo cáo 181.

---

## 2. Xác nhận độc lập cho 181

181 định danh `0x2ADB958` bằng bốn phép thử (idiom klass-cell, offset statics `0x0`, `statics+0x0` là `this`, field `Instance` khai báo `// 0x0`). Bảng relocation **không** được dùng ở đó, và nó cho:

| cell | target | `ScriptMetadata` |
|---|---|---|
| `44939608` (`0x2ADB958`) | `45771320` | **`FirebaseDatabaseManager_TypeInfo`** |
| `44939488` (`0x2ADB8E0`) | `45772088` | `UnityEngine.Application_TypeInfo` |

Ô lân cận giải ra đúng class mà 142 đã đọc bằng tay — nên đây là phép thử thứ năm, **độc lập** với bốn phép thử của 181.

---

## 3. Hai gốc

### 3.1 `PVP_Manager.get_pathRoot` (19859292, 64 B) — hằng

`return "data-leagues";` — ô `44960432` (`0x2AE0AB0`), không gọi hàm nào.

Năm getter còn lại chỉ `String.Concat(gốc, literal)` (đúng **1** `Concat` mỗi hàm):

| getter | RVA | literal | kết quả |
|---|---:|---|---|
| `get_pathOfDataUsers` | 19887544 | `44961064` | `data-leagues` + `/data-users` |
| `get_pathOfDataRanks` | 19874728 | `44960752` | `data-leagues` + `/data-ranks` |
| `get_pathOfDataConfigs` | 19915932 | `44961632` | `data-leagues` + `/data-configs` |
| `get_pathOfDataPlayOfUsers` | 19915052 | `44961576` | `data-leagues` + `/data-play/data-play-users` |
| `get_pathOfDataPlayOfMachines` | 19915784 | `44961624` | `data-leagues` + `/data-play/data-play-machines` |

### 3.2 `ArenaManager.get_pathRoot` (22685676, 204 B) — ba nhánh

```
Application.get_companyName() == "Test"   → "arena-test-datas"   (ô 45009312)
VersionControlSystem.get_PREMIUM()        → "arena--datas"       (ô 45009328)
còn lại                                    → "arena---datas"      (ô 45009320)
```

`PREMIUM` là RVA **20068044** (`VersionControlSystem.get_PREMIUM`) — lệnh chọn nhánh là `csel` sau `tst w0, #1`, không có `Concat`. Đây là lần đầu `arena--datas` (hai gạch) và `arena---datas` (ba gạch) được phân biệt **bằng điều kiện**, không chỉ bằng tên.

---

## 4. 27 mảnh đường dẫn và 19 template

Trong 34 method của 181: **179** literal phân biệt đọc được, **27** trong đó là path-ish (chứa `/`), **19** là template. Ba template không phải đường dẫn: `Delete rank-{0:000} season-{1}` (log), `PVP_Machine_{0}_{1}_{2}` và `user#{0}{1}{2}` (id) — artifact ghi `kind` cho từng cái.

| template | method dùng (RVA, API) |
|---|---|
| `{0}/summary-datas/season-{1}/rank-{2}/rooms/roomList/room-{3}` | `ArenaManager` **22687092** (Upload) |
| `{0}/summary-datas/.../room-{3}/listCount` | `ArenaManager.<IECheckUserStatus>d__17` **22707048** (Down/Upload) |
| `{0}/summary-datas/.../room-{3}/listRanks/{4}` | `ArenaManager.<IECheckUserStatus>d__17` **22707048** |
| `{0}/rank-datas/rank-{1}/rooms/roomList/room-{2}` | `ArenaManager` **22687736** (Delete) |
| `{0}/rank-datas/rank-{1}/rooms/roomList/room-{2}/season` | `ArenaManager.<IECheckUserStatus>d__17` **22707048** |
| `{0}/rank-datas/rank-{1}/rooms/roomList/{2}/userList` | `ArenaManager.<IEDownloadRank>d__30` **22714060** (Down) |
| `{0}/rank-configs/rank-{1}` | `ArenaManager.<IELoadRankSetups>d__39` **22717864** (Down); `<IESetRankSetups>d__41` **22720624** (Upload) |
| `/arena---datas/summary-datas/season-{0}/rank-{1:000}` | `ArenaDatabaseCleaner.<Start>d__0` **22673864** (Delete/Down) |
| `/arena---datas/rank-configs/rank-{0}/seasonCount` | `ArenaDatabaseCleaner.<Start>d__0` **22673864** |
| `{0}/data-solos/{1}` | 6 method: 19815216, 19822408, 19858764, 21259384, 21267840, 21271316 |
| `{0}/data-solos` | `Board_RoomPVP` **21258788** (Down) |
| `{0}/rank-{1}/map-{2}` | 19819084, 21274512 (Down) |
| `{0}/rank-{1}/map-{2}/{3}` | `Board_PVP.<IEUploadMachineDatas>d__88` **19831376** (Upload) |
| `{0}/{1}/rank-{2}/map-{3}` | 19819084, 21274512 (Down) |
| `{0}/{1}/rank-{2}/map-{3}/{4}` | `PVP_Endgame.<UploadDatas>d__23` **19911668** (Upload) |
| `{0}/{1}` | 7 method (xem artifact) |

Ba overriding khác cũng đọc được chữ nhưng **không** nằm dưới một gốc: `Data-Users/` (44939952), `BackupDatas/` (44940392), `ban-accounts/` (44940320), `/user-datas/userList/` (44972904), `/is-open` (44950432), `/playerChats`, `/playerScores`, `/profile/pvpDatas`, `/start`.

### Cây đọc được

```
data-leagues
├── /data-users
├── /data-ranks
├── /data-configs
├── /data-play/data-play-users
└── /data-play/data-play-machines

arena---datas | arena--datas (PREMIUM) | arena-test-datas (companyName=="Test")
├── /summary-datas/season-{s}/rank-{r}/rooms/roomList/room-{x}
│   ├── /listCount
│   └── /listRanks/{uid}
├── /rank-datas/rank-{r}/rooms/roomList/room-{x}
│   ├── /season
│   └── /{i}/userList
├── /rank-configs/rank-{r}/seasonCount
└── /is-open
```

Mọi template đều **liên tục từ `{0}`** (16/16 path), nên không có chỗ nào bị đọc thiếu tham số do parse sai.

---

## 5. Ngoài đường dẫn: 108 tên máy ảo PvP

`Board_PVP.<IEUploadMachineDatas>d__88` (**19831376**) dựng id bằng `PVP_Machine_{0}_{1}_{2}` và `user#{0}{1}{2}`, và cùng method đó nạp **108** literal tên: `Anam`, `Aquafine`, `Letto`, `One peach girl`, `Queen Rose`, `Máy sấy`, `Bà ba đi chợ`, `John Lùy`, `Ý Se`, `Do Do  `, …

Đây là pool tên hiển thị cho "máy" (đối thủ không người) ở chế độ PvP. Artifact ghi pool + số lượng + RVA; **chưa** trace từng entry rơi vào field nào — đó là mục `not_decoded` thứ ba.

---

## 6. Mục audit 53: đối chiếu được, vẫn `RUNTIME`

Mục 53 nói: *"`data-leagues/data-configs` và `arena---datas/is-open` sống trong Firebase, không nằm trong APK"*. 182 đối chiếu **tĩnh** cả hai nửa:

- `data-leagues` (ô `44960432`) + `/data-configs` (ô `44961632`);
- `arena---datas` (ô `45009320`) + `/is-open` (ô `44950432`).

Nhưng **verdict không đổi**: cái mục đó thiếu là *payload được phục vụ*, không phải *đường dẫn*. Nên 182 **không** sửa `open_items_audit`; nó chỉ thêm artifact vào phạm vi `audit_drift` (49 → 50) và hai needle (`127` `.md` / `157` `datas/`).

---

## 7. Còn mở

| Mục | Bước chặn |
|---|---|
| Season / rank / room / map thay vào template | đến từ save + server lúc chạy — `MODEL_NOT_MEASURED runtime` |
| Gốc nào đang sống trong một bản build | phụ thuộc `Application.get_companyName()` và `PREMIUM` trên máy |
| Pool 108 tên ↔ field nào | cùng method, nhưng chưa trace entry → field |
| `/playerChats`, `/playerScores`, `/profile/pvpDatas`, `/start` thuộc gốc nào | các ô này không đi qua `get_pathRoot`; cần trace đối số `{0}` của từng call site |

---

## 8. Kiểm chứng

```
python3 tools/verify/firebase_paths.py
  → {"bytes": 7371, "sha256": "3dcbbb83…", "methods": 34, "path_literals": 27,
     "templates": 19, "literals": 179, "identity": "FirebaseDatabaseManager_TypeInfo"}
python3 -m unittest tests.test_firebase_paths
  → 28 test OK
```

`build_payload()` tự khẳng định: 34 method, 179/27/19 literal, 16 template path + 3 template chữ, mọi template liên tục `{0..n}`, gốc Arena đúng ba nhánh kèm điều kiện, 5/5 getter có đúng một `Concat`, `/is-open` đúng ô `44950432`, và ô `0x2ADB958` giải ra đúng class mà 181 đã định danh bằng bốn phép thử khác.

`provenance:` hai bảng dữ liệu + `dump.cs` + 8 `native.json.gz`, mỗi file kèm sha256; `Provenance.test_source_digests_match_workspace` hash lại từ workspace.
