# 151 — `ArenaManager.rewards`: mười chuỗi phần thưởng mùa, đọc thẳng từ `.cctor`, và consumer mà 143 để mở

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc + dump/metadata đã pin, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Mười chuỗi dưới đây là **hằng ship sẵn trong build**; ai thắng gì trong một trận thật vẫn `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_arena_rewards.json.gz` (5273 B, sha256 `f76d36671418c9bbd07fdd0ca5be45a7e95973647905f82315ede3e40df7373a`)
**Báo cáo trước:** 139 (`arena_statics` — nơi `rewards` mới chỉ là một cái handle), 148 (danh sách open item, `#11`), 143 (`not_decoded`: "`rewards` consumer").
**Verifier:** `tools/verify/arena_rewards.py` (~0,7 s) · **Test:** `tests/test_arena_rewards.py` (43 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | § |
|---|---|---|
| `ArenaManager.rewards` chứa gì? | **mười chuỗi literal ship sẵn**, mỗi chuỗi là sáu khoảng hạng | §2 |
| Đọc được chúng ở đâu? | `ArenaManager..cctor` (rva **22692372**) cấp phát `new string[10]` rồi `str` mười literal vào `+0x20 + 8*i` | §2 |
| Bảng của 139 có đúng không? | **60/60 dòng khớp** khi parse lại chính mười chuỗi đó | §3 |
| Định dạng do đâu? | mười sáu literal của `Board_Arena.GetRewards` (rva **22795496**) chính là đặc tả: `]`, `#`, `"`, `;`, `[`, `,`, `:`, `Medal`, `Gems`, `-` | §4 |
| **Consumer của `rewards`** (143 để mở) | **`Board_Arena.SetRewards`** (rva **22794144**) — đọc `+0x38` @ **22795328**, lấy `rewards[arenaRank]` đưa cho `GetRewards`; **`Popup_ArenaInfo.SetInfo`** (rva **22784796**) là reader thứ hai | §5 |
| Ai ghi `+0x38`? | chỉ `.cctor` — mọi offset khác của statics đều bị ghi lại từ config | §6 |
| `+0x20 RankMapsIndex` có writer không? | **có** — `ArenaRankSetup.indexMap` (`+0x24`) → `RankMapsIndex` (`+0x20`) | §6 |

**Một câu:** phần thưởng mùa của Arena **không nằm trên server** — nó là mười chuỗi trong binary, một hàm parse bằng `Split` vài ký tự, và một consumer duy nhất đọc mảng đó; 143 để mở đúng chỗ này và nó đóng bằng ba tệp đã pin, không cần binary mới.

---

## 1. Vì sao cần báo cáo này

139 đọc `ArenaManager` statics và dừng ở `rewards` với một câu đúng nhưng hẹp: *"+0x38 là một `string[]`"*. 148 kiểm lại danh sách open và giữ `#11 rewards consumer` là dòng chưa đóng; 143 ghi hẳn `not_decoded: rewards consumer`.

Ba câu hỏi còn treo, và cả ba đều trả lời được **trong phạm vi static**, không cần probe:

1. mười phần tử của mảng là gì — có phải cấu hình server không?
2. ai đọc nó, và đọc bằng quy tắc nào?
3. bảng medal/gems của 139 (suy từ đâu?) có khớp chính văn bản đó không?

---

## 2. Mười chuỗi, và chỗ chúng được ghi

`ArenaManager..cctor` (rva **22692372**, 516 B, 129 lệnh) làm hai việc tách bạch: gán mặc định cho các field vô hướng, rồi dựng mảng `rewards`.

```
22692580  mov w1, #0xa          ; độ dài 10
22692608  bl  #0x110d09c        ; newarr  -> x0 = string[10]
22692624  adrp x9, #0x2aec000
22692628  ldr x9, [x9, #0xad0]  ; ô literal #0
22692632  cmp w8, #1
22692636  ldr x9, [x9]          ; nạp con trỏ chuỗi
22692640  str x9, [x0, #0x20]   ; rewards[0]
        ... (lặp cho +0x28 … +0x68)
22692868  str x0, [x8, #0x38]   ; ArenaManager.rewards = mảng vừa dựng
```

Hai điểm đáng ghi:

* **Chỉ số phần tử suy từ offset ghi**, không từ thứ tự ô: các ô được nạp theo thứ tự `…AD0, …AC0, …AE0, …AE8, …AF0, …AB8, …AB0, …AC8, …AA8, …AD8` — tức **không** tăng dần theo địa chỉ. Đọc "ô thứ n" theo địa chỉ sẽ ra bảng sai thứ tự mùa.
* Mười addend (`45970832, 45970840, 45970768, 45970776, 45970784, 45970792, 45970800, 45970808, 45970816, 45970824`) đều nằm trong `stringliteral.json` đã pin, nên **không có byte nào phải suy diễn**.

Mười chuỗi (index 0 → 9, tức mùa 1 → 10):

| # | dải hạng (medal/gems) | | | | | |
|---|---|---|---|---|---|---|
| 0 | 1: 680/250 | 2: 460/180 | 3-4: 320/120 | 5-10: 200/80 | 11-45: 120/50 | 46-50: 60/20 |
| 1 | 1: 800/300 | 2: 540/220 | 3-4: 380/150 | 5-10: 240/100 | 11-45: 140/60 | 46-50: 70/20 |
| 2 | 1: 1000/350 | 2: 680/250 | 3-4: 470/170 | 5-10: 290/110 | 11-45: 170/70 | 46-50: 90/30 |
| 3 | 1: 1250/400 | 2: 850/290 | 3-4: 490/190 | 5-10: 370/130 | 11-45: 220/80 | 46-50: 110/30 |
| 4 | 1: 1500/500 | 2: 1010/360 | 3-4: 700/240 | 5-10: 440/160 | 11-45: 260/100 | 46-50: 130/40 |
| 5 | 1: 2000/600 | 2: 1350/430 | 3-4: 940/290 | 5-10: 590/190 | 11-45: 350/120 | 46-50: 180/50 |
| 6 | 1: 2500/700 | 2: 1690/500 | 3-4: 1180/330 | 5-10: 740/220 | 11-45: 440/140 | 46-50: 220/60 |
| 7 | 1: 3000/800 | 2: 2030/580 | 3-4: 1410/390 | 5-10: 880/260 | 11-45: 530/160 | 46-50: 270/60 |
| 8 | 1: 4000/900 | 2: 2710/650 | 3-4: 1890/430 | 5-10: 1180/290 | 11-45: 710/180 | 46-50: 360/70 |
| 9 | 1: 5000/1000 | 2: 3380/720 | 3-4: 2350/480 | 5-10: 1470/320 | 11-45: 880/200 | 46-50: 440/80 |

Bảng dày lên theo mùa ở **mọi** dải: hạng 1 từ 680 lên 5000 medal, hạng 46-50 từ 60 lên 440. Gems cũng tăng, nên không có dải nào bị "trả công ngược".

---

## 3. Đối chiếu với 139 — 60/60

`datas/l2_535b0541_arena_statics.json.gz` (sha `261eca3a…`, artifact của 139) có sẵn bảng 10×6. Verifier parse lại **chính mười chuỗi ở trên** rồi so từng bộ ba `(placement, medal, gems)`:

```
rows = 60 · match_139 = true
first_band_by_rank = [680, 800, 1000, 1250, 1500, 2000, 2500, 3000, 4000, 5000]
last_band_by_rank  = [ 60,  70,   90,  110,  130,  180,  220,  270,  360,  440]
```

Đây là kiểm chéo chứ không phải kiểm vòng: 139 suy bảng từ **cấu trúc lệnh** (mười ô + mười lệnh `str`), 151 đọc bảng từ **nội dung chuỗi**, hai đường độc lập gặp nhau ở 60/60.

---

## 4. Định dạng — mười sáu literal của `Board_Arena.GetRewards`

`Board_Arena.GetRewards(string rankSetup, int userRank)` (rva **22795496**, 972 B, 243 lệnh). `slot_refs` của nó cho ra đúng bộ ký tự cần thiết, và các `mov w1, #imm` cho ra dấu phân cách:

| bước | bằng chứng |
|---|---|
| `Replace("]", "")` | literal `]` @ 22795676 · `Replace("#","")` literal `#` @ 22795704 · `Replace('"',"")` literal `"` @ 22795732 |
| `Split(';')` | `mov w1, #0x3b` @ 22795744 → `String.Split` @ 22795768 |
| `Split('[')` | `mov w1, #0x5b` @ 22795828 |
| `Split(',')` | `mov w1, #0x2c` @ 22795872 |
| `Split(':')` | `mov w1, #0x3a` @ 22796000 và @ 22796088 |
| tên field | literal `Medal` @ 22795960 → `ArenaRewards+0x10` (`str w0,[x21,#0x10]` @ 22796044) · literal `Gems` @ 22796052 → `+0x14` @ 22796132 |
| khoảng hay bằng | `Split('-')` — `mov w1, #0x2d` @ 22796252 + `bl` @ 22796264; hai nửa vào `int.TryParse` @ 22796296 / 22796324, rồi so khoảng `low <= userRank <= high` (`cmp ldr w8,[sp,#0xc]` @ 22796332, `ldr w8,[sp,#8]` @ 22796344) |
| nhánh một số | nếu placement không phải khoảng: `int.Parse` @ 22796372 rồi **so bằng** `cmp w0, w19` @ 22796376 |

Nghĩa là: chuỗi `#3-4[Medal:320,Gems:120]` được đọc là *"hạng 3 tới 4 nhận 320 medal và 120 gems"*, và `#2[Medal:460,Gems:180]` là *"hạng 2 nhận 460/180"*. Cả hai cách đọc khớp với §2.

Hai chỗ **không** đóng được từ đây, và không nên giả vờ:

* `int.Parse` được gọi qua `bl 0x2103668` / `bl 0x2103a4c` — helper này là parse **có** kiểm culture; giá trị số trong build là ASCII thuần nên không ảnh hưởng, nhưng đây là suy luận, không phải bằng chứng.
* Chuỗi được lưu dạng `key:value` phẳng, nhưng thứ tự field **không** được kiểm: parser so tên (`Medal`/`Gems`) chứ không theo vị trí, nên nếu server đổi thứ tự thì vẫn parse đúng. Ghi nhận để khỏi ai "sửa" bảng theo vị trí.

---

## 5. Consumer của `rewards` — câu trả lời cho 143

`Board_Arena.SetRewards(ArenaUserProfile userProfile, int count)` (rva **22794144**, 1344 B):

```
22795328  ldr  x8, [x8, #0x38]      ; ArenaManager.rewards   <- đúng ô 143 để mở
22795332  cbz  x8, …                ; null-guard
22795336  ldrsw x9, [x20, #0x1c]    ; userProfile.arenaRank
22795340  ldr  w10, [x8, #0x18]     ; rewards.Length
22795344  cmp  w9, w10
22795348  b.hs …                    ; rank >= Length -> thoát
22795352  add  x8, x8, x9, lsl #3
22795356  ldr  x1, [x8, #0x20]      ; rewards[rank]   (mảng bắt đầu ở +0x20)
22795360  ldr  w2, [x20, #0x28]     ; userProfile.status
22795380  bl   #0x15bd4e8         ; -> rva 22795496 = Board_Arena.GetRewards(string, int)
22795384  str  x0, [x22, #0x20]    ; kết quả ArenaRewards giao lại cho display-class
22795392  str  w8, [x22, #0x28]    ; kèm lại arenaRank
```

Đọc kèm theo nghĩa là: **chuỗi phần thưởng được chọn theo `arenaRank` của người chơi**, còn **hạng đạt được trong mùa** là `status` (`+0x28`) — tức hai con số khác nhau: một cái là "mùa này bạn đang ở bảng nào", cái kia là "bạn xếp thứ mấy". Guard trước đó (rva 22794560–22794608) chặn thêm ba trường hợp: `rewards` null, `rank >= Length`, và `status > RankUpIndexs[rank]` (chỉ số mùa bị vượt cấp).

**Reader thứ hai:** `Popup_ArenaInfo.SetInfo` (rva **22784796**) đọc cùng ô `+0x38` hai lần (@ **22786260** và @ **22786884**) và dùng `Length` để chặn vòng lặp hiển thị. Nó **không** parse chuỗi — chỉ cần biết có bao nhiêu mùa. Nên `rewards` có đúng hai consumer, và chỉ một trong hai đọc nội dung.

---

## 6. Census theo chiều **ghi** — chỗ mà census chỉ-đọc của 139/150 bỏ sót

Walker của 139 chỉ bắt `ldr`, nên bức tranh "offset nào bị chạm" thực ra là "offset nào bị **đọc**". Thêm một nhánh `str`/`strb` cho ra bảng khác hẳn — và giải thích luôn vì sao `.cctor` chỉ ghi **một** mảng:

| offset | field (theo 139) | writers | readers |
|---|---|---|---|
| `+0x0` | `IsOpen` | `ArenaManager..cctor` @ 22692584 | 0 |
| `+0x18` | `SeasonTimes` | `Board_Arena.GetConfigs` @ 22782328 | 4 |
| `+0x20` | `RankMapsIndex` | `.cctor` @ 22692596 · `Board_Arena.<>c__DisplayClass69_0` @ 22807948 | 0 |
| `+0x28` | `RankUpIndexs` | `Board_Arena.GetConfigs` @ 22782576 | 4 |
| `+0x30` | `RankDropIndexs` | `Board_Arena.GetConfigs` @ 22782600 | 5 |
| `+0x38` | `rewards` | `ArenaManager..cctor` @ 22692868 | 3 |

Ba mảng `SeasonTimes`/`RankUpIndexs`/`RankDropIndexs` bị **cấp phát lại mỗi lần load config** (`Board_Arena.GetConfigs`, rva **22782048**, ba `str` trên), còn `rewards` thì ghi **một lần** trong `.cctor`. Đó là lý do cấu trúc: ba mảng kia là dữ liệu server (chuỗi `ArenaConfig.RankSplit` / `SeasonTime` được `Split` rồi parse), còn `rewards` là hằng của build. Nói cách khác: **bảng thưởng không đổi được từ server, chỉ bảng chia hạng thì đổi được.**

**`RankMapsIndex` có writer** — chỗ 148 còn treo. `Board_Arena.<>c__DisplayClass69_0` (rva **22807856**, 120 B) trong callback `<WaitToLoadConfigMaps>b__0(ArenaRankSetup setup)`:

```
22807916  ldr w20, [x20, #0x24]   ; ArenaRankSetup.indexMap
22807948  str w20, [x8,  #0x20]   ; ArenaManager.RankMapsIndex
```

Tức **pool map của Arena là dữ liệu theo-rank ship kèm `ArenaRankSetup`**, không phải một pool cố định trong code. Điều này khớp với #29 (`AllArenaStartMaps`/`AllArenaRandomMaps`) và nói rõ hơn: `RankMapsIndex` chỉ là **con trỏ vào** bốn mảng đó, còn giá trị cụ thể do config của từng rank quyết định. Dòng 148 `#11` đóng ở đây.

**Giới hạn của census này (ghi rõ để không ai đọc quá):** nó chỉ tính `ldr`/`str`/`strb`/`strh` **một thanh ghi** trên nền statics. `.cctor` còn ghi `+0x4`/`+0x8` bằng `stur d0,[x8,#4]` và `stp …,[x8,#0x10]` (`MaxRoomCount`, `MinUserCount`, `SeasonSummaryTime`) — ba cái đó đã pin trong 139 và **không** xuất hiện trong bảng trên, đúng như thiết kế, không phải thiếu dữ liệu.

---

## 7. Đính chính & xác nhận

| Nguồn | Nói | 151 |
|---|---|---|
| 139 | `rewards` = `string[]`, offset `+0x38`, không rõ nội dung | **giữ** offset + độ dài, **bổ sung** toàn bộ nội dung (§2) |
| 139 | bảng 10×6 medal/gems | **xác nhận 60/60** (§3) |
| 139/150 | census statics: chỉ `0x18/0x28/0x30/0x38` bị chạm | **đính chính**: `+0x0` và `+0x20` cũng bị ghi; census cũ chỉ bắt chiều đọc (§6) |
| 148 | `#11 rewards consumer` | **đóng**: `Board_Arena.SetRewards` + `Popup_ArenaInfo.SetInfo` (§5) |
| 143 | `not_decoded: rewards consumer` | **đóng** (§5) |
| 148 | `+0x20 RankMapsIndex` không có writer | **đính chính**: có, từ `ArenaRankSetup.indexMap` (§6) |

---

## 8. Còn mở (và vì sao)

1. **Người chơi thật rơi vào dải nào** — code chứng minh **quy tắc** tra (rank → chuỗi → dải theo `status`), nhưng `status` là kết quả trận đấu. `MODEL_NOT_MEASURED runtime`.
2. **Giá trị `RankUpIndexs` lúc chạy** — mảng này null trong build và được `Board_Arena.GetConfigs` bơm từ chuỗi `RankSplit` phục vụ từ server, nên guard `status > RankUpIndexs[rank]` không tính được bằng static.
3. **`ArenaUserProfile.status` (`+0x28`) được dùng như một vị trí hạng** — tên field là `status` nhưng nó được so với biên dải như thể là thứ hạng. Tên và cách dùng lệch nhau; báo cáo này ghi nhận sự lệch, **không** phán tên nào đúng. Muốn chốt phải có một lần chạy hoặc một bản dump có `[SerializeField]`/attribute bổ sung.
4. **Ngoài lane:** bảng roman-glyph (RVA 21103836) vẫn 0 raw; `LanguageManager.GetText` RVA 21202600 — thuộc 143/148, không đụng ở đây.

---

## 9. Chạy lại

```bash
python3 tools/verify/arena_rewards.py          # -> datas/l2_535b0541_arena_rewards.json.gz
python3 -m unittest tests.test_arena_rewards -q   # 43 test
```

Artifact tự chứa `provenance` (sha256 của `arena-pvp-535b0541/native.json.gz` `3197425a…`, `stringliteral.json` `5e62507e…`, `dump.cs.gz` `e08f23fb…`, `l2_535b0541_arena_statics.json.gz` `261eca3a…`) và **16 check tự khẳng định** trong lúc build: mười phần tử, thứ tự theo offset ghi, mọi literal đều pin được, sáu dải mỗi mùa, khớp 139 60/60, thang đơn điệu, đúng hai consumer, chỉ `.cctor` ghi `+0x38`, sáu offset bị ghi, census phủ đúng sáu field, cầu `indexMap → RankMapsIndex`, reader là `SetRewards`, reader gọi `GetRewards`, đủ năm dấu phân cách, literal có cả `Medal` và `Gems`.
