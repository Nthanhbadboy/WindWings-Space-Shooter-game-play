# 148 — 56 mục mở của lane #29/#30: 17 đã đóng, 2 gỡ chặn, 14 còn mở

> **ERRATA 170 (27/10):** các tổng dưới đây là ảnh chụp tại 147. Báo cáo **170** cho audit
> đọc thêm 168/169 và tổng đổi thành **19 đóng · 6 thu hẹp · 0 gỡ chặn · 20 runtime ·
> 1 ghi chú · 10 còn mở** (28 proof). Đọc 170 trước khi trích số ở đây.


**Trạng thái:** `DECODED_STATIC` (chỉ đọc 20 artifact cùng lane + artifact 147, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Không lần disasm nào trong báo cáo này — mọi "đóng" đều là một vị từ đọc trường của artifact có sẵn, và verifier tính lại.
**Artifact:** `datas/l2_535b0541_open_items_audit.json.gz` (10010 B, sha256 `5416035aca0dbab8090abe64ef16aa191a5cf1e87ba1c26b7bef3a6168ed80ca`)
**Báo cáo trước:** 147 (close-out, 56 mục mở), 146 (index của 51 khoá computed).
**Verifier:** `tools/verify/open_items_audit.py` (~0,2 s) · **Test:** `tests/test_open_items_audit.py` (27 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | Bằng chứng |
|---|---|---|
| 147 đếm 56 mục mở — còn đúng bao nhiêu? | **14** còn mở thật; **17 đã đóng**, **3 thu hẹp**, **2 gỡ chặn**, **19 runtime**, **1 không phải lỗ hổng** | §2, §3 |
| Ai đóng chúng? | báo cáo **sau** trong cùng lane (17/17), không cần đào mới | §3 |
| Vì sao 147 không thấy? | nó **copy nguyên văn** `not_decoded`; lane tự đóng bằng `corrections` / `confirmations` nằm ở artifact khác | §1, §6 |
| Bao nhiêu câu hỏi phân biệt? | **53** — 3 cặp là cùng một câu hỏi | §2 |
| Có mục nào "chết từ lúc sinh"? | **2** — 139 viết mục ToRoman sau khi 138 đã đính chính; 133 viết mục blob sau khi 131 đã giải | §4 |
| Có chỗ nào gỡ chặn mà chưa làm? | **2** — `rewardValues` / `rewardScales` của 133; đường đã có, phép tra chưa chạy | §4, §7 |
| 147 sai chỗ nào? | 3 chỗ: copy nguyên văn, đếm runtime 17 (đúng 19), cắt text ở 220 ký tự và biến `null` thành `"None"` | §6 |

**Một câu:** lane này đã tự đóng **17/56** mục ngay trong lúc chạy, nhưng nó ghi việc đóng vào artifact *của báo cáo sau* chứ không sửa lại danh sách cũ — nên một bản kiểm kê copy nguyên văn sẽ báo động thừa đúng 17 mục.

---

## 1. Vì sao phải kiểm lại (và vì sao copy nguyên văn là sai)

147 lấy `open_items` bằng cách chép `not_decoded` của từng artifact. Cách đó đo được *lịch sử*, không đo được *trạng thái*: mỗi báo cáo chỉ được sửa artifact của chính nó, nên khi báo cáo sau trả lời câu hỏi của báo cáo trước, nó ghi câu trả lời vào **artifact mới** — dưới `corrections` (khi lật lại một khẳng định) hoặc `confirmations` (khi trả lời đúng một mục đã liệt kê).

Lane hiện có **11 bản ghi như vậy**; **5** trong số đó trỏ thẳng vào một trong 56 mục, **6** còn lại đính chính một khẳng định chưa bao giờ được liệt kê là "mục mở". Vì thế một bản chép nguyên văn không thể thấy chúng, còn một bản kiểm lại thì thấy — và còn thấy cả các trường hợp đóng *không* kèm bản ghi, chỉ ngầm hiểu qua nội dung artifact (12 mục):

| Kiểu đóng | Số mục | Ví dụ |
|---|---|---|
| artifact tự khai (`corrections` / `confirmations`) | **5** | 143 khai nó giải 4 khoá tiền tệ của 142 |
| chỉ ngầm qua nội dung | **12** | 131 in ra `[30,30,30]` cho `BoxKeyCost` mà không nhắc 130 |

---

## 2. Sáu kết luận, 56 mục, 53 câu hỏi

| Kết luận | Nghĩa | Số |
|---|---|---|
| `CLOSED` | báo cáo sau trong lane trả lời; có vị từ kiểm lại | **17** |
| `RESTATED` | bị thu hẹp, vẫn mở | **3** |
| `ACTIONABLE` | lý do chặn đã bị gỡ bằng một đường đã chứng minh trong lane; phép decode chưa chạy | **2** |
| `RUNTIME` | trạng thái máy / dịch vụ — `MODEL_NOT_MEASURED runtime` | **19** |
| `OPEN` | vẫn chặn, lý do không đổi | **14** |
| `NOTE` | ghi cho đủ index, không phải lỗ hổng | **1** |

Cộng lại **56**. Trừ 3 cặp trùng (**[3,25]** cùng hỏi slot `0x2ADB8E0`; **[27,54]** cùng hỏi nửa index, 144 và 145; **[34,48]** cùng hỏi level 0 của rank 0, 135 và 136) còn **53 câu hỏi phân biệt**.

Cột `n` trong artifact và trong các bảng dưới là **đúng cột của bảng 147** (§5 của báo cáo đó), để đọc song song hai báo cáo không phải dò lại.

---

## 3. 17 mục đã đóng

Mỗi dòng có một vị từ trong verifier; cột "chứng cứ" là giá trị verifier đọc lại được hôm nay.

| `n` | Report | Mục | Đóng bởi | Chứng cứ (giá trị verifier đọc) |
|---|---|---|---|---|
| 2 | 142 | khoá `PlayerPrefs` của 4 getter tiền tệ | **143** | 4 khoá `GCoins/Gems/StarCount/WingCoins` + đúng 4 cell `44941496/44941512/44941536/44941776` mà 142 nêu |
| 3 | 140 | class sau slot `0x2ADB8E0` (44939488) | **141** | cờ gate nằm sau `44940168` = `GameConfig`; 44939488 là slot **bên cạnh** — câu hỏi dựa trên cell sai |
| 5 | 127 | `ArenaManager.rewards[10]` | **139** | 10 dòng, 6 dải thứ hạng, mỗi dải có medal + gem |
| 6 | 127 | chuỗi `RankSplit` / `SeasonTime` | **140** | hai literal: 10 khoảng hạng và 10 mốc thời gian |
| 7 | 127 | nội dung `PVP_Manager.MaxRankStars` | **135** | 10 array ← 5 blob PID, `data_hex` in ra đủ |
| 8 | 127 | `SeasonTimes` / `RankUpIndexs` / `RankDropIndexs` | **140** | 1440…17280 phút, 10 giá trị |
| 14 | 131 | nơi tăng bộ đếm khoá | **132** | 14 lần cấp trực tiếp / 3 class; 21 class cấp qua pack value |
| 15 | 130 | `BoxKeyCost` / `KeyPrices` / `NumberRewards` | **131** | `[30,30,30]` · `[6,20,100]` · `[5,6,9]` |
| 17 | 130 | lịch nhận khoá | **132** | không có drip: không caller nào cộng gì ngoài đối số reward |
| 22 | 143 | khoá của 174 lời gọi store | **144** | 184 lời gọi; 145 phủ 184/184, unknown 0 |
| 23 | 143 | site `SetString` / `GetString` / `DeleteKey` | **144** | `SetString 32 · GetString 25 · DeleteKey 2` — **lật lại** câu "chỉ có GetInt/SetInt" của 143 |
| 25 | 141 | class của slot `0x2ADB8E0` | **142** | `44939488` = `UnityEngine.Application` |
| 26 | 144 | 26 lời gọi không literal | **145** | 184/184, unknown **0** |
| 31 | 132 | binding khoá `KeyCount0/1/2` | **143** | 3 literal `46011960/46011968/46011976` + 3 slot |
| 33 | 135 | method đọc `MaxRankStars` | **136** | `GetRankNumber` (rva 19884996) đọc statics `+0x18` |
| 42 | 134 | giá trị `MaxRankStars` | **135** | 5 blob in `data_hex`, đủ 10 dòng bảng |
| 46 | 136 | chuỗi hiển thị hạng | **137** | confirmation của 137: 2 slot tiền tố + bảng 10 tier |

Hai dòng đáng đọc kỹ:

* **#23 không phải "đã đóng", mà là "câu hỏi sai".** 143 viết *"chỉ GetInt và SetInt xuất hiện trong 8 raw đã pin"*; 144 census ra `SetString 32`, `GetString 25`, `DeleteKey 2`. Nghĩa là 143 quét thiếu, không phải dữ liệu thiếu. Phần duy nhất còn đúng là **float = 0**, và con số 0 đó chính là câu trả lời.
* **#3 và #25 là hai nửa của cùng một chuyện.** 140 gọi cờ gate là slot `0x2ADB8E0`; 141 đính chính cờ nằm ở `44940168`; 142 đặt tên cho `44939488`. Sau ba bước, cả hai mục đóng, và 147 đã kiểm đúng khoảng cách `680 = 0x2A8` giữa hai cell.

---

## 4. 3 thu hẹp, 2 gỡ chặn

| `n` | Report | Mục | Vì sao chưa đóng |
|---|---|---|---|
| 12 | 139 | bảng glyph `MyLibrary.ToRoman` | 138 đã đính chính: đuôi `GetRankNumber` là `ToRoman`, nên số hạng phải đọc là **số La Mã** (`Herald III`), không phải `Herald 3`. Bảng glyph vẫn không có: 139 quét đủ 8 raw cho rva 21103836 → 0. **Đính chính này có trước mục** — 139 viết mục sau khi 138 đã sửa. |
| 27 | 144 | nửa index của **43** khoá computed | 146 cho cấu trúc (3 dải 100/200/300, 4/14 họ enumerate được) nhưng độ dài mảng là dữ liệu. Con số trong câu hỏi cũng lệch: 43 + 8 = **51**. |
| 54 | 145 | nửa index của **50** khoá computed | cùng câu hỏi với #27, và cũng lệch đếm: 145 và 146 đều mang **51** record / 14 tiền tố. |
| 39 | 133 | `rewardValues` | **gỡ chặn**: 131 đã chỉ đường `InitializeArray handle → PID field → fieldDefaultValues` (bảng 10.493 entry đã pin). 133 dừng một bước trước đó, vẫn ghi handle `0x2ae0010` là chưa phân giải. |
| 40 | 133 | `rewardScales` | cùng dạng, cùng phép tra chưa chạy; field này chỉ là scale icon. |

Cả `39` và `40` là **việc làm được ngay**, không cần chờ ai: đường đã có trong repo, chỉ thiếu lần chạy. Đó là lý do chúng nằm ở `ACTIONABLE` chứ không ở `OPEN`.

---

## 5. 14 mục còn mở, 19 mục runtime, 1 ghi chú

**Còn mở (14)** — mỗi mục vẫn giữ đúng lý do chặn, không mục nào chỉ ghi "chưa biết":

| `n` | Report | Mục |
|---|---|---|
| 9 | 127 | giá/stock shop medal — 146 biết dạng khoá, giá trị nằm trong mảng config |
| 11 | 139 | consumer của `ArenaManager.rewards` (+0x38) — 0 method trong raw arena-pvp |
| 18 | 146 | cận trên của từng dải — `ldr wT, [xConfig, #0x18]` là độ dài lúc chạy |
| 19 | 146 | index do caller truyền — chỉ 20 site literal `999` thấy được |
| 29 | 132 | lượng mỗi pack của 20 clone `SaveDataReward` — đối số `_value` từ dữ liệu pack |
| 30 | 132 | loại/lượng reward theo stage PvP — mảng instance, dispatch chỉ chứng minh `Key2` tới được |
| 32 | 132 | một static store nằm ngoài các class này — hạn chế của **phép quét**, không phải của dữ liệu |
| 34 | 135 | rank 0 có 3 cell nhưng 2 reward level — **chưa giải thích** |
| 44 | 134 | 14 dòng medal được index bằng gì — `[rank][index]`, nghĩa của rank 0..13 không có trong cctor |
| 48 | 136 | level 0 của rank 0 có thật — trùng #34 |
| 49 | 137 | `GetText` với khoá thiếu — **code**, không phải thiết bị: rva 21202600 không có trong 8 raw đã pin |
| 50 | 138 | `get_pathRoot` trả slot `0x2AEC9A0` / `0x2AEC9B0`, không slot nào được dereference |
| 51 | 138 | class config của `PVP_Manager` — slot `0x2AE1000` không phải literal kind 5 |
| 52 | 138 | class sở hữu static field 0 — slot `0x2ADB958` không có symbol nào đặt tên |

**Runtime (19)**: `1, 4, 10, 13, 16, 20, 21, 24, 28, 35, 36, 37, 38, 41, 43, 45, 47, 53, 55` — thiết bị trả lời (Application), Firebase trả lời (config hạng/đấu trường), hoặc trạng thái máy (mọi "stored values"). Không được nâng mục nào trong số này lên mức đọc tĩnh.

**Ghi chú (1)**: `56` — hai lệnh `str` ghi dữ liệu không phải khoá; chúng có mặt trong `statics` chỉ để index đủ, không phải để đòi đóng.

---

## 6. Đính chính 147 (ba chỗ)

| # | 147 đã làm | Đúng ra |
|---|---|---|
| 1 | đếm 56 mục mở rồi để nguyên | **14** còn mở thật; 17 đóng / 3 thu hẹp / 2 gỡ chặn / 19 runtime / 1 ghi chú |
| 2 | `runtime_items = 17` | **19**. 147 đếm trên text đã cắt: khôi phục chỗ cắt được lại tag của 141 (+1 = 18); 129 có hai mục `runtime only` không dùng cụm từ đó (+2 = 20); còn tag của 137 thì sai chiều — `GetText` là code chưa pin, không phải trạng thái máy (−1 = **19**) |
| 3 | lưu `str(blocking)[:220]` | 5 mục có `blocking = null` bị thành chuỗi `"None"` (cả 5 của 127), 4 mục bị cắt đuôi (130, 136, 141, 143). 148 đọc lại **nguyên văn từ artifact gốc** của từng mục, và test ghim điều đó (`test_text_comes_from_the_source_artifact`, `test_no_row_keeps_the_string_none`) |

Ba chỗ này không sửa artifact 147 (sha của nó đã pin trong test và trong HANDOFF): 148 **thay thế** bản kiểm kê, và ghi rõ nó thay thế cái gì.

---

## 7. Việc kế

| Việc | Vì sao | Bước cụ thể |
|---|---|---|
| `rewardValues` / `rewardScales` (133) | đường đã có, chỉ thiếu lần chạy | phân giải 2 handle `0x2ae0010` / `0x2ae0018` thành PID field rồi đọc `reverse-engineering/il2cpp/field-defaults.json` |
| `LanguageManager.GetText` (137) | câu trả lời là **code**, không phải thiết bị | pin raw chứa rva 21202600; trước đó để trống chứ không đoán |
| reader của `ArenaManager.rewards` (139) | 0 consumer trong raw arena-pvp | quét 6 raw còn lại cho `+0x38` trên một statics base `ArenaManager` |

Ba mục còn lại của nhóm "chưa giải thích" (#34/#48 rank 0 level 0, #44 14 dòng medal) không có đường nào trong 8 raw đã pin: chúng cần thêm dữ liệu, không cần thêm cách đọc.

---

## 8. Chạy lại

```bash
python3 tools/verify/open_items_audit.py        # in bytes/sha + 56/53/17/3/2/19/1/14
python3 -m unittest tests.test_open_items_audit -q
```

Artifact dựng lại tất định (gzip `mtime=0`, `sort_keys=True`, `separators=(',',':')`); `test_rebuild_reproduces` gọi lại `build_payload()` và so với file trên đĩa. Mọi dòng "đóng" nằm trong `items[].evidence` với `label` / `expected` / `actual` / `pass_`, nên đọc báo cáo không cần tin lời văn.

---

provenance: static-only re-read of the lane's own artifacts; 21 sources with sha256 in `datas/l2_535b0541_open_items_audit.json.gz` §`provenance` (20 lane artifacts 127–146 + the 147 close-out it supersedes). No disassembly, no emulator, no probe, no device. RVAs decimal. Verdicts are claims about the artifacts, not about the game at run time; device and served state stay `MODEL_NOT_MEASURED runtime`.
