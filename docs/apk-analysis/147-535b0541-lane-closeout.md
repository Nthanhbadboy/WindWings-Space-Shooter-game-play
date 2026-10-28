# 147 — Đóng lane #29/#30: 20 báo cáo, 21 check chéo, và một chỗ 145 đếm thiếu

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc + 20 artifact cùng lane, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Không lần chạy nào ở đây; mọi giá trị *lưu dưới khoá* / *dịch vụ trả về* / *thiết bị trả lời* vẫn là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_lane_closeout.json.gz` (10669 B, sha256 `3b815fc91d8f21f2191aa4dd558aabac82f67d09adb0f24e3ce54da27a8ecadd`)
**Báo cáo được đóng:** 127 → 146 (20 báo cáo, 20 artifact), tổng **227.107 B** nén, **235** section.
**Verifier:** `tools/verify/lane_closeout.py` (~0,4 s) · **Test:** `tests/test_lane_closeout.py` (18 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | Bằng chứng |
|---|---|---|
| Lane #29/#30 đã đóng chưa? | **20/20 report ↔ 20/20 artifact**, ánh xạ 1:1 cho 127–146 | §1 |
| Các con số có khớp nhau giữa các artifact? | **21/21 check PASS**, 0 lệch | §2 |
| 144 ↔ 145 nói cùng một chuyện? | **184 = 184** lời gọi store; 145 phủ **184**, unknown **0** | §3 |
| Hai không gian khoá có chồng nhau? | **Không**: 143 `GameDatas` 21 khoá ∩ 144 store 25 khoá = **0** | §3 |
| 8 khoá "computed mới" đi đâu? | 26 unknown → **literal 18 + computed 8**; 25 → **28** khoá literal | §3 |
| 145 có đếm thiếu không? | **Có, 6 lời gọi** — 143 tái tạo ra **174**, không phải 170; xem §4 | §4 |
| Còn bao nhiêu việc mở? | **56 mục mở**, trong đó **17 mục runtime** đã dán nhãn `MODEL_NOT_MEASURED runtime` | §5 |
| Có bịa thêm gì trong báo cáo này? | **Không thêm lần disasm nào** — chỉ đọc lại artifact và băm lại nguồn | §6 |

**Một câu:** 20 báo cáo của lane đọc lên khớp nhau và khớp với 40 nguồn đã băm; chỗ duy nhất phải sửa là 145 nói "key-jump thêm 4 lời gọi chưa thấy", trong khi theo đúng luật của 143 thì phần chênh là **10** lời gọi — 4 ở key-jump và **6 ở meta-rewards**.

---

## 1. Inventory: 20 report, 20 artifact, 1:1

Mỗi artifact có `evidence = STATIC_ONLY_ORIGINAL_APK`, `provenance.sources` với sha256 thật, và danh sách `not_decoded` (128 giữ mục mở dưới `gaps` nên đếm ra 0 — xem §5).

| # | Artifact (`datas/l2_535b0541_…`) | B | Mục mở | Report chính |
|---|---|---|---|---|
| 127 | `arena_pvp.json.gz` | 88.881 | 5 | 127 |
| 128 | `meta_rewards.json.gz` | 72.690 | 0 | 128 |
| 129 | `pack_index.json.gz` | 3.101 | 3 | 129 |
| 130 | `box_draw.json.gz` | 3.155 | 3 | 130 |
| 131 | `box_arrays.json.gz` | 2.251 | 2 | 131 |
| 132 | `key_sources.json.gz` | 5.325 | 4 | 132 |
| 133 | `pvp_hunter_reward_table.json.gz` | 2.123 | 3 | 133 |
| 134 | `pvp_manager_rules.json.gz` | 4.597 | 4 | 134 |
| 135 | `max_rank_stars.json.gz` | 2.559 | 3 | 135 |
| 136 | `pvp_rank_api.json.gz` | 3.172 | 3 | 136 |
| 137 | `rank_name.json.gz` | 4.118 | 1 | 137 |
| 138 | `remote_configs.json.gz` | 4.240 | 4 | 138 |
| 139 | `arena_statics.json.gz` | 3.336 | 3 | 139 |
| 140 | `arena_config.json.gz` | 3.690 | 2 | 140 |
| 141 | `game_config_gate.json.gz` | 3.062 | 2 | 141 |
| 142 | `application_cell.json.gz` | 3.669 | 2 | 142 |
| 143 | `economy_keys.json.gz` | 3.993 | 3 | 143 |
| 144 | `game_store_keys.json.gz` | 4.956 | 3 | 144 |
| 145 | `store_key_callers.json.gz` | 3.719 | 3 | 145 |
| 146 | `computed_key_index.json.gz` | 4.470 | 3 | 146 |

Ba artifact được **nhiều** báo cáo trích (135/136/137 → `max_rank_stars`, 128/135 → `meta_rewards`); bảng ánh xạ vì vậy chọn **báo cáo đầu tiên** làm chính và ghi các báo cáo còn lại vào `mentioned_in`, rồi assert rằng tập báo cáo chính đúng bằng `127…146` và có **20** giá trị phân biệt — nếu một báo cáo mới chen vào làm lệch ánh xạ thì check đỏ ngay.

---

## 2. 21 check chéo

| # | id | Kỳ vọng | Đo được |
|---|---|---|---|
| 1 | `store-calls` | 144 và 145 đếm cùng một lượng | **184 / 184** |
| 2 | `store-kinds-before` | tổng kind của 144 | **184** |
| 3 | `store-kinds-after` | 145 phủ hết, unknown = 0 | **[184, 0]** |
| 4 | `resolution-adds-up` | 26 unknown = 18 literal + 8 computed | **18 + 8** |
| 5 | `keys-25-to-28` | 145 thêm 3 khoá literal | **[25, 28, 3]** |
| 6 | `old-keys-unchanged` | 25 khoá cũ giữ nguyên số lời gọi từng khoá | **25/25** |
| 7 | `prefixes-13-to-14` | 145 thêm 1 bucket tiền tố | **[13, 14]** |
| 8 | `computed-records` | 146 = 145 | **51 = 51** |
| 9 | `computed-families` | 14 tiền tố, cùng tập và cùng số | **14 = 14** |
| 10 | `bands` | 3 dải, 12 vị trí | **[12, [100, 200, 300]]** |
| 11 | `sentinel` | 999 · 20 vị trí · 2 họ quest | **[999, 20, Quest_Collect_Index, Quest_Value_Key]** |
| 12 | `economy-reproducible` | áp luật 143 ⇒ 174 và đúng tỉ lệ API | **174** · SetString 32 / GetInt 54 / SetInt 63 / GetString 23 / DeleteKey 2 |
| 13 | `economy-delta` | 184 − 174 = 10, chia theo raw | **10** = key-jump 4 + meta-rewards 6 |
| 14 | `key-spaces-disjoint` | 143 ∩ 144 = 0 | **[0, 21, 25]** |
| 15 | `economy-cross-check` | 143 "setter không khớp prefs" = 144 cross-check | **6 = 6** |
| 16 | `one-slot-per-class` | 142 cell ≠ 141 slot, cách 0x2A8 | **44939488 / 44940168 / 680** |
| 17 | `rank-tiers` | bảng hạng 10 = 10 | **10 / 10** |
| 18 | `pvp-rule-pairs` | hằng luật PvP | **[[3, 1500], [160, 10]]** |
| 19 | `static-only` | mọi artifact cùng một lớp bằng chứng | **20 × `STATIC_ONLY_ORIGINAL_APK`** |
| 20 | `provenance-digests` | băm lại 40 nguồn | **0 thiếu · 0 lệch** |
| 21 | `runtime-is-never-claimed` | không artifact nào tự nhận runtime | **true** |

Bốn check đầu/cuối là check *cấu trúc*: chúng đỏ khi có ai sửa một artifact cũ mà không chạy lại gate — đúng loại lỗi mà một lane 20 báo cáo hay mắc.

---

## 3. Ba chỗ hai artifact phải nói giống nhau

**a) 184 lời gọi store.** 144 census ra **184** lời gọi vào 5 API store (`SetValue` 20912164 · `GetValue` 20912432 · `SetInt` 20912644 · `SetString` 20912660 · `GetInt` 20912668 · `GetString` 20912684 · `DeleteKey` 20912964). 145 phân giải **184/184**, unknown **0**. 26 chỗ 144 để `unknown` được 145 tách thành **18 literal + 8 computed**, và 8 computed đó chính là 51 record mà 146 lập index — 145 và 146 vì vậy phải trùng **51 = 51** trên cùng **14** tiền tố.

**b) Hai không gian khoá rời nhau.** 143 đọc `GameDatas` (**21** khoá int, default 68999 / 500 / 0 / 999999) bằng một cell riêng; 144 đọc store `PlayerPrefs` (**25** khoá tên). Giao = **0**. Nghĩa là hai báo cáo không được trộn số: tiền tệ trong `GameDatas` không đi qua `PlayerPrefs`, và 6 "setter không có prefs" của 143 khớp đúng 6 dòng `cross_check.keys` của 144.

**c) Một slot cho một class.** 142 nhận `UnityEngine.Application` ở cell **44939488**; 141 nhận `GameConfig` ở slot **44940168**. Hai slot cách nhau **680 = 0x2A8** — không trùng, nên chuỗi gate của 140/141 và cell của 142 không thể là cùng một class.

---

## 4. Đính chính 145: phần chênh là 10, không phải 4

145 kết luận: 143 đếm 170 lời gọi store, còn 144 đếm 184, và "key-jump thêm 4 lời gọi mà 145 chưa thấy". Áp **đúng luật của 143** (chỉ đếm lời gọi store nằm trong method có một `slot_ref` kiểu string) lên 4 raw của 143 **cộng** raw key-jump:

| Nhóm | Lời gọi | Chia theo API |
|---|---|---|
| Trong method có `slot_ref` | **174** | SetString 32 · GetInt 54 · SetInt 63 · GetString 23 · DeleteKey 2 |
| key-jump | **4** | GetInt 4 |
| meta-rewards | **6** | GetInt… +4 · SetInt 4 · GetString 2 |
| **Tổng** | **184** | khớp 144 |

* **174**, không phải 170: con số của 145 thiếu 4 lời gọi ngay trong 4 raw của 143 (cùng nhóm key-jump mà 145 đã thấy, nhưng 145 chỉ cộng phần "ngoài").
* **6 lời gọi ở meta-rewards** nằm ngoài luật `slot_ref` — method đọc/ghi key qua tham số chứ không qua slot string, nên luật của 143 không bắt được. 145 chưa từng nhắc tới 6 lời gọi này.

Sửa lại: **10 = 4 (key-jump) + 6 (meta-rewards)**, và tỉ lệ API của phần "trong luật" là **174** — tức bảng chia API của 143 vẫn đúng, chỉ dòng tổng của 145 là thiếu. Correction được ghi trong artifact ở `corrections[0]` với `target: 145` và `evidence.outside_by_raw`.

---

## 5. 56 mục mở, 17 mục runtime

Phân bố theo báo cáo: 1 báo cáo có **5** mục (127), 3 có **4**, 10 có **3**, 4 có **2**, 1 có **1** (137), 1 có **0** (128 — mục mở của nó nằm dưới khoá `gaps`, không phải `not_decoded`, nên bộ đếm trả 0; test ghim đúng ngoại lệ này thay vì nới điều kiện).

**17 mục** có chuỗi `MODEL_NOT_MEASURED runtime` trong `blocking`. Chúng thuộc ba nhóm không thể đóng bằng code:

| Nhóm | Ví dụ | Vì sao chặn |
|---|---|---|
| Thiết bị trả lời | `Application.language` / reachability / company name (142) | APK chỉ có call site |
| Dịch vụ trả lời | `data-leagues` / `arena---datas/is-open` (138) | nằm trong Firebase, không có trong APK |
| Trạng thái máy | giá trị lưu dưới mọi khoá (143/144/145) | chỉ hiện ra khi chạy |

**39 mục còn lại** đều đã ghi đúng bước chặn cụ thể, không có mục nào chỉ ghi "chưa biết". Ba ví dụ đại diện: class sau slot `0x2ADB8E0` (140), literal của 4 slot string tiền tệ (142), và nửa index của 51 khoá computed (145 → 146 giải được cấu trúc dải nhưng độ dài mảng là dữ liệu).

---

## 6. Cái gì không được làm trong báo cáo này

* **Không lần disasm nào.** Verifier chỉ `open`/`decompress` 20 artifact + 20 báo cáo và **băm lại** chúng; con số duy nhất phải tính là kết quả đếm lại trên dữ liệu đã có (bảng §4), và nó tái tạo được từ raw đã pin.
* **Không đụng artifact 143–146.** Không ghi lại file nào trong `datas/` ngoài artifact mới của chính báo cáo này.
* **Không nâng bằng chứng.** 127 vẫn giữ `runtime = MODEL_NOT_MEASURED runtime`; 17 mục runtime vẫn là runtime.
* **Không tuyên bố lane "hoàn thành 100 %"**: 56 mục mở là việc còn lại, trong đó 17 mục không thể đóng STATIC-ONLY.

---

## 7. Chạy lại

```bash
python3 tools/verify/lane_closeout.py          # in bytes/sha + 20 reports / 21 checks / 0 failing
python3 -m unittest tests.test_lane_closeout -q
```

Artifact dựng lại tất định (gzip `mtime=0`, `sort_keys=True`, `separators=(',',':')`) nên sha256 trong test là pin cứng; `test_rebuild_reproduces` gọi lại `build_payload()` và so với file trên đĩa.

---

provenance: static-only close-out over the lane's own artifacts; 40 sources with sha256 in `datas/l2_535b0541_lane_closeout.json.gz` §`provenance` (20 artifacts 127–146 + the 20 reports that cite them). No new disassembly, no emulator, no device. RVAs decimal. Stored values, device answers and served config remain `MODEL_NOT_MEASURED runtime`.
