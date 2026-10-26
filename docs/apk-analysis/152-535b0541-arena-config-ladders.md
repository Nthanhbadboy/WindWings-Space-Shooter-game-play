# 152 — `ArenaConfig`: mười mùa, hai cái thang ship sẵn, và đơn vị thời gian

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc + dump/metadata đã pin, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Mọi con số ở đây là hằng lúc build; mùa thật dùng thang nào vẫn `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_arena_config_ladders.json.gz` (4743 B, sha256 `cc6bc93a3d83bbe897cf59e6eb321f0527723b8fb6d2ab9e94e6d918c6eb052a`)
**Báo cáo trước:** 139 (`arena_statics` — nơi `ArenaConfig` mới chỉ là danh sách field), 151 (`rewards` — bảng thưởng theo dải), 149/150 (ô metadata).
**Verifier:** `tools/verify/arena_config_ladders.py` (~2,0 s) · **Test:** `tests/test_arena_config_ladders.py` (37 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | § |
|---|---|---|
| `ArenaConfig` có giá trị mặc định nào? | **sáu field, bảy giá trị**: `RankSplit` và `SeasonTime` là hai chuỗi literal, `MaxRoomCount 50` / `MinRoomCount 10` đến từ **một** literal 8 byte, `SummaryTime 60.0f`, `IsOpen false` | §2 |
| `RankSplit` chứa gì? | `20-45;15-45;15-45;10-45;10-45;10-45;10-45;10-45;10-45;10-45` — **10 mùa**, mỗi mùa một cửa sổ `up-down` | §3 |
| `SeasonTime` chứa gì? | `1440;2880;4320;7200;10080;11520;12960;14400;15840;17280` — **10 mùa** | §3 |
| Đơn vị là gì? | **phút** — consumer duy nhất đưa thẳng vào `DateTime.AddMinutes` (rva **34499824**) | §4 |
| Vậy mùa dài bao lâu? | 1, 2, 3, 5, 7, 8, 9, 10, 11, **12 ngày** — tổng **68 ngày** cho 10 mùa | §4 |
| `seasonEnd` là chuỗi ngày tháng? | **không** — là `DateTime.ToBinary()` in ra bằng `Int64.ToString()` | §5 |
| Thang này dùng thế nào? | thăng hạng khi `status <= RankUpIndexs[rank]`, giữ hạng tới `45`, rớt khi `> 45`; hạng kẹp `[0, 9]` | §6 |
| Có gì khớp ngẫu nhiên? | ngưỡng rớt **45** trùng đúng chỗ bảng thưởng của 151 ngừng trả (`46-50`) | §7 |

**Một câu:** cái "lịch mùa" của Arena không phải cấu hình server như các báo cáo trước giả định — nó là hai chuỗi literal mười phần tử trong `ArenaConfig..cctor`, đơn vị **phút** chứng minh được bằng đúng một `bl` tới `DateTime.AddMinutes`, và ngưỡng rớt hạng 45 giải thích luôn vì sao bảng thưởng của 151 có dải `46-50`.

---

## 1. Vì sao cần báo cáo này

139 đọc statics của `ArenaManager` rồi liệt kê `ArenaConfig` như **sáu field static**, nhưng chưa mở `.cctor` của nó: `RankSplit` và `SeasonTime` chỉ được ghi tên, không ghi giá trị. 151 đóng phần *thưởng* và ghi rõ `SeasonTimes` là "int[] do config phục vụ bơm vào", để nguyên đơn vị.

Ba câu hỏi treo:

1. mặc định ship trong binary của lịch mùa là gì?
2. `1440` là phút, giây, hay ngày?
3. ba mảng còn lại (`SeasonTimes`/`RankUpIndexs`/`RankDropIndexs`) được dùng **thế nào**, không chỉ bị ghi?

---

## 2. `ArenaConfig..cctor` — sáu field, bảy giá trị

`ArenaConfig..cctor` (rva **22726640**, 164 B, 41 lệnh) — nhỏ, nên đọc được toàn bộ:

| rva | lệnh | field | giá trị |
|---|---|---|---|
| 22726748 | `str x9, [x8]` | `RankSplit` (+0x00) | literal @ 45978056 (§3) |
| 22726780 | `str x10, [x8, #8]` | `SeasonTime` (+0x08) | literal @ 45977616 (§3) |
| 22726784 | `str d0, [x8, #0x10]` | `MaxRoomCount` (+0x10) | **50** |
| 22726784 | (cùng lệnh) | `MinRoomCount` (+0x14) | **10** |
| 22726788 | `str w9, [x8, #0x18]` | `SummaryTime` (+0x18) | `#0x42700000` = **60.0f** |
| 22726792 | `strb wzr, [x8, #0x1c]` | `IsOpen` (+0x1c) | `false` |

Hai chỗ dễ đọc sai, cả hai đều đã kiểm:

* **50 và 10 đến từ một literal 8 byte**, `320000000a000000` (va **7696928**): `struct.unpack('<2i')` ra `(50, 10)`. Nếu đọc literal đó như `double` thì được `5.3e-313` — vô nghĩa, nên cách đọc hai-int là cách duy nhất đứng được.
* **`SummaryTime` là float, không phải double**: `str w9` ghi 4 byte từ thanh ghi `w`, và `#0x42700000` là bit pattern của `60.0f`. Đây chính là nguồn của `ArenaManager.SeasonSummaryTime` (`+0x10`, double) mà 139 thấy bằng `60.0` — `Board_Arena.GetConfigs` đọc float rồi `fcvt d0, s0` thành double.

---

## 3. Hai cái thang, mỗi cái mười mùa

**`RankSplit`** — cửa sổ hạng của từng mùa, dạng `up-down`:

| mùa | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| text | `20-45` | `15-45` | `15-45` | `10-45` | `10-45` | `10-45` | `10-45` | `10-45` | `10-45` | `10-45` |
| độ rộng | 26 | 31 | 31 | 36 | 36 | 36 | 36 | 36 | 36 | 36 |

**`SeasonTime`** — độ dài từng mùa, đơn vị **phút** (§4):

| mùa | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| phút | 1440 | 2880 | 4320 | 7200 | 10080 | 11520 | 12960 | 14400 | 15840 | 17280 |
| ngày | 1 | 2 | 3 | 5 | 7 | 8 | 9 | 10 | 11 | 12 |

Cả hai đều **đơn điệu**: cửa sổ chỉ mở ra (ngưỡng thăng hạng siết từ 20 xuống 10), mùa chỉ dài thêm (1 → 12 ngày). Không có mùa nào ngắn lại — nên đây là lịch *tăng dần*, không phải bảng tuỳ ý.

---

## 4. Đơn vị là **phút** — bằng chứng nằm ở một `bl`

Consumer duy nhất của `SeasonTimes` là `ArenaManager.<IESetRankSetups>d__41` (rva **22720624**):

```
22721052  ldr  x8, [x8, #0x18]     ; ArenaManager.SeasonTimes
22721060  ldrsw x9, [x19, #0x28]   ; season index
22721080  ldr  w8, [x8, #0x20]     ; SeasonTimes[season]
22721092  scvtf d0, w8             ; int -> double
22721096  bl   #0x20e6cf0          ; DateTime.AddMinutes(double)   <-- rva 34499824
22721128  bl   #0x2104440          ; Int64.ToString()
22721132  stp  x0, xzr, [x21, #0x18]  ; ArenaRankSetup.seasonEnd
```

`0x20e6cf0` = **34499824** = `DateTime.AddMinutes(double)` (đối chiếu trong `dump.cs` đã pin, không đoán từ tên). Nên `1440` là 1440 **phút** = 1 ngày. Nếu là giây thì mùa 1 dài 24 phút; nếu là ngày thì mùa 10 dài 47 năm — cả hai đều vô lý với một game mùa 1–12 ngày.

Chuỗi đầy đủ: `SeasonTimes[season]` (int) → `scvtf` → `AddMinutes` → `ToBinary` → `Int64.ToString()` → `ArenaRankSetup.seasonEnd` (string).

---

## 5. `seasonEnd` là một `ToBinary` long, không phải chuỗi ngày

`ArenaManager.<IEGetTimeSpan>d__19` (rva **22717248**) đọc ngược lại đúng giá trị đó:

```
22717660  ldr  x20, [x8, #0x18]   ; ArenaRankSetup.seasonEnd  (string)
22717688  bl   #0x20c8a6c         ; Convert.ToInt64(string)     rva 34376300
22717732  bl   #0x20e77ac         ; DateTime.FromBinary(long)   rva 34502572
22717760  blr  x9                 ; callback(DateTime)
```

Nên ai đó định "parse ngày" từ `seasonEnd` sẽ thất bại: nó là `DateTime.ToBinary()` (một `long` có cờ kind) in ra bằng `Int64.ToString()`. Điều này cũng cho biết **server không gửi ngày dạng chuỗi ISO** mà gửi đúng giá trị `.NET` mà client sinh ra — tức mùa được tạo bởi client rồi lưu lên, không phải tính lại từ một mốc.

---

## 6. Thang dùng thế nào — `IEResetUserProfileStatus`

`ArenaManager.<IEResetUserProfileStatus>d__37` (rva **22719392**) chấm lại hạng sau mỗi mùa. Ba nhánh, đọc thẳng từ lệnh:

| điều kiện | hiệu ứng | bằng chứng |
|---|---|---|
| `status <= RankUpIndexs[arenaRank]` | `arenaRank = min(arenaRank + 1, 9)` | `cmp` @ 22719888 · `b.le` @ 22719892 · `add w9,w10,#1` @ 22720196 · `cmp w9,#9` @ 22720200 · `csinc` @ 22720208 · `str` @ 22720212 |
| `RankUpIndexs[arenaRank] < status <= RankDropIndexs[arenaRank]` | giữ nguyên hạng | `ldr x10,[x9,#0x30]` @ 22719928 · `cmp` @ 22719960 · `b.le` @ 22719964 |
| `status > RankDropIndexs[arenaRank]` | `arenaRank = max(arenaRank - 1, 0)` | `sub w9,w9,#1` @ 22719968 · `bic w9,w9,w9,asr #31` @ 22719972 |
| luôn luôn | `status = -1`, `roomIndex = -1` | `mov w9,#-1` @ 22720216 · `str w9,[x8,#0x28]` @ 22720220 · `str w9,[x8,#0x20]` @ 22720224 |

Đọc ra tiếng người: **`status` là thứ hạng đạt được, số nhỏ là tốt**. Đứng trong top-20 (mùa 1) thì lên một bậc; tới hạng 45 vẫn giữ; vượt 45 thì rớt. Hạng bị kẹp trong `[0, 9]` — tức **10 bậc**, khớp đúng 10 mùa và 10 dòng của cả hai thang.

Đây là chỗ **đính chính 151**: 151 viết guard của `SetRewards` là *"`status > RankUpIndexs[rank]` thì chặn"* — đúng về lệnh, nhưng dễ đọc thành "status cao thì tốt". Chiều đúng là **status nhỏ = hạng cao**; `SetRewards` chỉ hiện thưởng khi thứ hạng nằm trong ngưỡng thăng hạng (tức `status <= RankUpIndexs[arenaRank]`).

---

## 7. Ngưỡng 45 khớp bảng thưởng — không phải trùng hợp

Bảng thưởng của 151 có sáu dải: `1`, `2`, `3-4`, `5-10`, `11-45`, `46-50`. Ngưỡng rớt ở §6 là **45 trong cả mười mùa**. Nói cách khác: **`46-50` là dải duy nhất vừa có thưởng vừa bị rớt hạng** — nó tồn tại để hiển thị phần thưởng cho người vừa bị đẩy xuống, không phải để thăng tiến. Hai báo cáo độc lập (một đọc bảng thưởng, một đọc bảng chia hạng) cùng chỉ về con số 45.

---

## 8. Ai ghi đè cái gì

`Board_Arena.GetConfigs` (rva **22782048**, 139 đã pin đường ống) đọc `ArenaConfig` rồi ghi vào `ArenaManager`:

| từ `ArenaConfig` | sang `ArenaManager` | kiểu |
|---|---|---|
| `RankSplit` (+0x00) | `RankUpIndexs` (+0x28) / `RankDropIndexs` (+0x30) | `Split(';')` → `Split('-')` → `Int32.Parse` |
| `SeasonTime` (+0x08) | `SeasonTimes` (+0x18) | `Split(';')` → `Int32.Parse` |
| `MaxRoomCount` (+0x10) | `MaxRoomCount` (+0x4) | int |
| `MinRoomCount` (+0x14) | `MinUserCount` (+0x8) | int |
| `SummaryTime` (+0x18) | `SeasonSummaryTime` (+0x10) | `fcvt d0, s0` |
| `IsOpen` (+0x1c) | — | không thấy đọc |

Điểm cần nói rõ vì 151 đã nói ngược lại một nửa: **`ArenaConfig` cũng có mặc định ship sẵn**, nên "server bơm vào" chỉ đúng khi server thực sự gửi config. Nếu không, game vẫn có một lịch mùa hoàn chỉnh (10 mùa, 68 ngày, cửa sổ 20-45 → 10-45) ngay trong binary.

---

## 9. Census tám raw — và một phủ định có biên

Quét đủ **8 slice** (cùng một `libil2cpp` `9cb038e8…`, **2499 method** được dump) bằng cùng con trỏ statics `+0xB8`:

* **9 method** chạm statics của `ArenaManager`; sáu offset bị chạm: `+0x0`, `+0x18`, `+0x20`, `+0x28`, `+0x30`, `+0x38`.
* **`+0x4`, `+0x8`, `+0x10` không method nào chạm** — tức `SeasonSummaryTime` (mặc định 60.0) được ghi hai lần (`.cctor` và `GetConfigs`) mà **không có reader** trong 2499 method đã dump.

Phủ định này **có biên** và phải đọc đúng biên: 2499 method là các *lát cắt* của một build, không phải toàn binary. Nên câu đúng là *"không có reader trong tám lát cắt đã dump"*, **không** phải *"field này không được dùng"*. Ghi vào `open_items` đúng như vậy.

---

## 10. Đính chính & xác nhận

| Nguồn | Nói | 152 |
|---|---|---|
| 139 | `ArenaConfig` sáu field static, `RankSplit`/`SeasonTime` chưa đọc | **đóng** — cả hai là literal 10 phần tử (§3) |
| 139 | `SeasonSummaryTime` mặc định `60.0` | **xác nhận + truy nguồn**: `ArenaConfig.SummaryTime` `60.0f` = `#0x42700000` |
| 151 | "ba mảng kia do config phục vụ bơm vào" | **đính chính một nửa**: `ArenaConfig` cũng ship mặc định, nên lịch mùa có sẵn trong binary (§8) |
| 151 | guard `status > RankUpIndexs[rank]` | **làm rõ chiều**: `status` nhỏ = hạng cao; thăng hạng khi `status <= ngưỡng` (§6) |
| 151 | dải thưởng cuối `46-50` | **giải thích**: đó là dải của người bị rớt, ngưỡng rớt = 45 (§7) |

---

## 11. Còn mở

1. **Mùa thật đã dùng thang nào** — `Board_Arena.GetConfigs` có thể ghi đè cả hai thang bằng config phục vụ. Code chứng minh *thang ship trong binary*, không chứng minh *thang đã chạy*. `MODEL_NOT_MEASURED runtime`.
2. **`SummaryTime` chưa có reader** trong 2499 method đã dump — phủ định có biên, không phải "không dùng".
3. **Mốc bắt đầu mùa** — `seasonStart` là `DateTime.ToBinary()` của một giá trị game tự sinh lúc tạo mùa; binary không ship epoch nào.

---

## 12. Chạy lại

```bash
python3 tools/verify/arena_config_ladders.py             # -> datas/l2_535b0541_arena_config_ladders.json.gz
python3 -m unittest tests.test_arena_config_ladders -q    # 37 test
```

Artifact mang `provenance` (sha256 của `arena-pvp` `3197425a…`, `stringliteral.json` `5e62507e…`, `dump.cs.gz` `e08f23fb…`, `l2_535b0541_arena_rewards.json.gz` `f76d3667…`, `l2_535b0541_arena_statics.json.gz` `261eca3a…`) và **20 check tự khẳng định** khi build: rva/size `.cctor`, sáu offset bảy giá trị, literal đóng gói `(50,10)`, `60.0f`, `IsOpen=false`, 10 mùa mỗi thang, ngưỡng dưới cố định 45, ngưỡng trên siết dần, độ dài là số ngày nguyên, mùa dài dần, đơn vị phút, `seasonEnd` là `ToBinary`, bốn luật thăng/giữ/rớt/reset, hạng kẹp 9, census 8 slice, 9 method chạm statics, `SummaryTime` không có reader, sáu helper resolve đúng class, dải thưởng khớp ngưỡng rớt.
