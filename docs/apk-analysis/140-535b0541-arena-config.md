# 140 — `ArenaConfig`: tầng remote phía trên `ArenaManager` — 10 mùa, đơn vị **phút**, và chuỗi cổng mở bảng

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY; giá trị server ghi đè lúc chạy là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_arena_config.json.gz` (3690 B, sha256 `d3552cea30dfecbef34c325e67e43db382c022238da3f6ad2fa79540985b56dc`)
**Báo cáo trước:** 127 (§Arena), 138 (cổng fail-closed — báo cáo này chỉ ra đúng tầng), 139 (`ArenaManager` statics + cầu `GetConfigs`).
**Verifier:** `tools/verify/arena_config.py` · **Test:** `tests/test_arena_config.py` (36 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | Bằng chứng |
|---|---|---|
| `ArenaConfig` có mấy field? | **6**, `0x0 … 0x1C` | `dump.cs` (TypeDefIndex 402) khớp `..cctor` |
| Bản shipped có sẵn dữ liệu? | **có** — `..cctor` (RVA 22726640, 164 B) điền **cả 6** | §1 |
| `RankSplit`? | `20-45;15-45;15-45;10-45;10-45;10-45;10-45;10-45;10-45;10-45` | literal @22726736 |
| `SeasonTime`? | `1440;2880;4320;7200;10080;11520;12960;14400;15840;17280` | literal @22726760 |
| Đơn vị thời gian? | **phút** — không phải giả định | `DateTime.AddMinutes` RVA **34499824** tại §3 |
| Phòng? | `MaxRoomCount=50`, `MinRoomCount=10` | **một** literal 8 byte `320000000a000000` |
| `SummaryTime`? | `60.0f` (`0x42700000`) | `mov w9,#0x42700000` |
| `IsOpen` shipped? | `false` | `strb wzr` @22726792 |
| Ai ghi `ArenaConfig`? | **1** method (`.cctor`) + 3 chỗ ghi `IsOpen` của 138 | khoá theo slot `0x2AECA98` |
| Ai đọc? | `Board_Arena.GetConfigs` + `Board_Arena.IECheckArenaOpen` | §4 |
| Bảng mùa có từ đâu? | **shipped**, không cần server | 10 mùa × (khung rank, số phút) |

**Một câu:** bảng mùa Arena **nằm sẵn trong APK**: 10 mùa, mỗi mùa một khung rank (`20-45` → `10-45`) và một độ dài **1440 phút (1 ngày) → 17280 phút (12 ngày)**, và đơn vị *phút* là **số đo** chứ không phải suy luận — chính `DateTime.AddMinutes` được gọi trên từng phần tử.

---

## 1. `ArenaConfig..cctor` (RVA 22726640, 164 B) — 6 phép ghi

```asm
22726736  ldr  x9,  [x21]            ; literal "20-45;..."
22726748  str  x9,  [x8]             ; RankSplit      (+0x00)
22726760  ldr  x10, [x19]            ; literal "1440;2880;..."
22726764  ldr  d0,  [x9, #0x220]     ; 8 byte = MaxRoomCount(50) + MinRoomCount(10)
22726776  mov  w9,  #0x42700000      ; 60.0f  (bit pattern, KHÔNG phải địa chỉ)
22726780  str  x10, [x8, #8]         ; SeasonTime     (+0x08)
22726784  str  d0,  [x8, #0x10]      ; MaxRoomCount(+0x10)=50 , MinRoomCount(+0x14)=10
22726788  str  w9,  [x8, #0x18]      ; SummaryTime    (+0x18) = 60.0f
22726792  strb wzr, [x8, #0x1c]      ; IsOpen         (+0x1C) = false
```

| Offset | Field | Kiểu | Giá trị shipped |
|---:|---|---|---|
| `0x00` | `RankSplit` | `string` | `20-45;15-45;15-45;10-45;10-45;10-45;10-45;10-45;10-45;10-45` |
| `0x08` | `SeasonTime` | `string` | `1440;2880;4320;7200;10080;11520;12960;14400;15840;17280` |
| `0x10` | `MaxRoomCount` | `int` | **50** |
| `0x14` | `MinRoomCount` | `int` | **10** |
| `0x18` | `SummaryTime` | `float` | **60.0** |
| `0x1C` | `IsOpen` | `bool` | **false** |

Hai bẫy giống hệt 139 nhưng ở class này: `str d0,[x8,#0x10]` phủ **8 byte** cho **hai** `int` (literal `320000000a000000` = `0x32`/`0x0a`), và `0x42700000` là **bit pattern float** của `60.0`.

---

## 2. Bảng mùa — shipped, không cần server

`Board_Arena.GetConfigs` (139 §4) tách hai chuỗi trên: `Split(';')` cho từng mùa, rồi `Split('-')` cho khung rank. Kết quả:

| mùa | khung rank | phút | ngày |
|---:|---|---:|---:|
| 0 | 20–45 | 1440 | 1 |
| 1 | 15–45 | 2880 | 2 |
| 2 | 15–45 | 4320 | 3 |
| 3 | 10–45 | 7200 | 5 |
| 4 | 10–45 | 10080 | 7 |
| 5 | 10–45 | 11520 | 8 |
| 6 | 10–45 | 12960 | 9 |
| 7 | 10–45 | 14400 | 10 |
| 8 | 10–45 | 15840 | 11 |
| 9 | 10–45 | 17280 | 12 |

Kiểm trong verifier: đúng **10** mục ở **cả hai** chuỗi, mỗi khung có `0 < low ≤ high`, độ dài **tăng dần và phân biệt** (10 giá trị khác nhau), và **mọi** độ dài chia hết cho 1440 (tức tròn ngày). Cột "ngày" chỉ là `minutes / 1440` để đọc cho dễ — **số đo là phút**.

---

## 3. Đơn vị là **phút** — bằng chứng thi hành, không phải quy ước

| Method | RVA | Lệnh | Ý nghĩa |
|---|---:|---:|---|
| `ArenaManager.IESetRankSetups` | 22720624 | 22721052 `ldr x8,[x8,#0x18]` | đọc `SeasonTimes` |
| ↑ | ↑ | 22721092 `scvtf d0, w8` | `int` → `double` |
| ↑ | ↑ | 22721096 `bl 0x20E6CF0` | **`DateTime.AddMinutes(double)`** (RVA **34499824**) |
| `ArenaManager.IECheckUserStatus` | 22707048 | 22708728 `ldr d8,[x9,#0x10]` | đọc `SeasonSummaryTime` |
| ↑ | ↑ | 22708760 `bl 0x20E6CF0` | `AddMinutes` (cùng hàm) |
| ↑ | ↑ | 22708776 `bl 0x20EA03C` | `DateTime.op_GreaterThanOrEqual` (RVA 34512956) |

Tức chuỗi thời gian là: `now.AddMinutes(SeasonTimes[i])` rồi so `>=` với hạn mùa. Nếu đơn vị là giây/giờ thì phải có `AddSeconds`/`AddHours`; ở đây **chỉ** có `AddMinutes` — nên 1440 = 1 ngày là *hệ quả*, không phải giả định.

---

## 4. Chuỗi cổng mở bảng (`Board_Arena.<IECheckArenaOpen>d__55.MoveNext`, RVA 22810128)

```text
22810692  ldrb w8, [statics, #0x1c]   ; ArenaConfig.IsOpen
22810696  cbz  w8                     ; false -> bỏ qua toàn bộ phần nạp
22810700  bl   GetConfigs             ; 22782048 : ArenaConfig -> ArenaManager
22810736  ldrb w9, [statics, #4]      ; class sau slot `0x2ADB8E0` (44939488), field +4
22810796  bl   GetGameConfig          ; 22798808 : GetGameConfig(Action<bool>)
```

Đây là chuỗi đầy đủ mà 138/139 mới có từng mảnh: **`ArenaConfig.IsOpen` là công tắc duy nhất**, mở thì mới copy config và mới đi lấy game config. `ArenaManager.IsOpen` (`+0x0`, chỉ `..cctor` ghi) **không** nằm trên đường này — khớp đính chính của 139.

---

## 5. Ai ghi / ai đọc `ArenaConfig` (khoá theo slot `0x2AECA98`)

| Vai trò | Method | RVA |
|---|---|---:|
| ghi | `ArenaConfig..cctor` (cả 6 field) | 22726640 |
| ghi `IsOpen` | `ArenaManager.LoadRemoteConfigs` (`strb wzr`) | 22691808 |
| ghi `IsOpen` | `ArenaManager.<>c__DisplayClass44_0.<LoadRemoteConfigs>g__OnListCountLoaded` (`= count > 0` / `wzr`) | 22705216 |
| đọc | `Board_Arena.GetConfigs` | 22782048 |
| đọc | `Board_Arena.<IECheckArenaOpen>d__55.MoveNext` | 22810128 |

Nghĩa là **5 field cấu hình còn lại chỉ có đúng một người ghi: `..cctor`** — bảng mùa shipped là *giá trị cuối cùng* trừ khi runtime ghi đè (§7).

### 5.1 Ghi chú phương pháp — vì sao phải khoá theo slot

Lần quét đầu tiên của tôi gán `str x0,[x9,#0x18]` (RVA **22782328**) trong `GetConfigs` cho **`ArenaConfig`**, sai. Nguyên nhân: `x9` từng là statics của `ArenaConfig` ở đầu method, rồi được nạp lại từ khối `ArenaManager` hai lệnh trước store; giữ trạng thái "statics" dính qua lần định nghĩa lại làm field `+0x18` rơi vào class cũ.

Quy tắc đã áp dụng (và có **witness hồi quy** trong artifact):

1. mỗi thanh ghi chỉ có **một** vai: page / slot / klass / statics;
2. mọi lần ghi đè thanh ghi **xoá** vai cũ;
3. kiểm tra "deref slot" **trước** "trang + offset", vì cùng một thanh ghi có thể đang giữ page rồi bị nạp bằng slot.

| Cách đọc | Kết quả tại 22782328 |
|---|---|
| quét dính (sai) | `ArenaConfig` write `+0x18` |
| khoá slot (đúng) | `ArenaManager` write `+0x18` = `SeasonTimes` |

Không có số đo nào thay đổi vì lỗi này (139 vốn đã ghi đúng đích là `ArenaManager`), nhưng danh sách writer của `ArenaConfig` giờ **chính xác tuyệt đối**: một `.cctor` + ba store `IsOpen`.

---

## 6. Kiểm chéo với 139

| Hạng mục | `ArenaConfig` (140) | `ArenaManager` (139) | Khớp |
|---|---|---|---|
| thời lượng mùa | `1440…17280` (chuỗi) | `SeasonTimes` = 10 số nguyên cùng dãy (sau `GetConfigs`) | ✔ |
| tổng kết mùa | `SummaryTime = 60.0f` | `SeasonSummaryTime = 60.0` (double, qua `fcvt`) | ✔ |
| phòng | `MaxRoomCount 50`, `MinRoomCount 10` | `MaxRoomCount 50`, `MinUserCount 10` | ✔ (khác tên, cùng số) |
| mở bảng | `IsOpen` (bị 138 ghi `false`) | `IsOpen` chỉ `..cctor` ghi | ✔ khớp đính chính 139 |

---

## 7. `not_decoded` (2 mục)

| Mục | Bước chặn |
|---|---|
| Class sau slot `0x2ADB8E0` (44939488) | chuỗi cổng đọc field `+4` của class này trước khi gọi `GetGameConfig`, nhưng không symbol nào đã pin đặt tên cho class đó |
| Bản ghi đè từ server | `ArenaConfig` bị loader remote ghi lại lúc chạy; database không nằm trong APK — **`MODEL_NOT_MEASURED runtime`** |

---

## 8. Tái lập

```bash
python3 tools/verify/arena_config.py            # in bytes/sha256 + write/mùa/writer/reader
python3 -m unittest tests.test_arena_config      # 36 test
python3 tools/verify-claims.py --require AB,AO,AP
```

`evidence: STATIC_ONLY_ORIGINAL_APK` · nguồn: `arena-pvp-535b0541/native.json.gz`,
`reverse-engineering/il2cpp/stringliteral.json`, `reverse-engineering/il2cpp/dump.cs.gz`.

---

`provenance:` APK gốc `535b0541` → `libil2cpp.so` → raw `arena-pvp-535b0541` (`ArenaConfig..cctor`, `Board_Arena.GetConfigs`, `IECheckArenaOpen`, `IESetRankSetups`, `IECheckUserStatus`) → `stringliteral.json` (2 chuỗi cấu hình) → `dump.cs` (bố cục + chữ ký callee) → verifier → artifact 3690 B `d3552cea…` → 36 test. Không emulator/probe/device.
