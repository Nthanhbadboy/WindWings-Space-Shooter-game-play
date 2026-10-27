# Re-review Gate-1: registry-v4 và C1–C5 — `arena/8141386a`

**Verdict: `APPROVE-BOUNDED` cho hồ sơ L1 theo phạm vi và disposition đã ghi, có
residuals ở §4–5.** Reviewer đề xuất director trình phương án Gate-1 cho user; đây
**không phải user duyệt Gate**, không chứng minh runtime parity, không cấp quyền cho
nhánh này scaffold/SDK/store/publish/merge. `NOT_READY` ở report125 và ở bản review
trước tại cut `1b43…` vẫn đúng **cho các cut lịch sử đó**; không sửa lại chúng.

## 1. Cut, authority và phương pháp

- Producer v4: `cf17c7f22f855c3fb93191e3661fdaaa756a7d80`; registry-v4 SHA-256
  `bcd0e0fd95af375b8841021856209eb701d284bf013966d48f868e9143e21a96`.
- Spec đã đối chiếu: `3179cc81d51836a574070af9eab736c95c817713`; registry-v4
  **trùng byte** producer. Các trạng thái trước `c21b265547df02911e63c06b31cb83a76c5f03f9`
  và `1b43f5dc5069e1b7cccec2dd000d1d107e746277` được pin riêng để thấy supersession.
- Producer mới hơn `afacf4b06bcfff130db4163c5a0400ea5d862ace` thêm report181:
  registry và audit vẫn trùng byte, contract drift vẫn trùng, nhưng artifact-count
  drift tăng 48→49. Report181 là **claim mới của producer**, chưa được independently
  audit; item52 vẫn `CONFLICTING`, không tự đóng (§3).
- Review125/HANDOFF `6440973318`, ACK `6441583848`, 8 findings/5 conditions, source
  cut và receipt cũ là lịch sử `NOT_READY`; tài liệu này là addendum. Không tự ACK.
  Bản `NOT_READY` tại spec `1b43…` được lưu trong Git tại review commit
  `50d135dd93571ecc90d0b85580405137931293a3`; verdict mới này xét cut `3179…`.
- **46 alias/42 archive độc nhất**: `source-manifest.json` ghi commit, đường dẫn,
  Git blob OID, SHA-256 và kích thước nguồn/archive. Archive là gzip của **nguyên
  Git blob**, kể cả khi blob vốn là `.gz`. `--git --fetch` so từng byte với Git ở
  commit đã chọn. `api-captures.json.gz` lưu phản hồi GitHub API có timestamp;
  snapshot API không phải chứng thư GitHub ký, và không thay thế CI của review head.
- Không chạy code verifier của producer; không trích APK, giải thêm binary/metadata,
  chạy emulator/device, sử dụng credentials hay tạo fixture Graph/atlas toàn bộ.
  Original APK vẫn là authority; đây chỉ là đọc lại **hồ sơ đã publish**.

## 2. C1 — tự dựng lại join trong phạm vi static

**STATIC_CONFIRMED, có điều kiện theo convention đã công bố:** constructor
`Board_PVP..ctor` RVA `19796420`, 500 byte, lấy từ slice `key-grant` SHA
`3f43642ab14858f205d99a6b63c93ba5fa601d3ae1318e1f2b3948a729c23ffb`. Tự đọc
6 event, 6 từ lệnh BL và 6 STR trực tiếp từ byte slice; không dùng field_id do 149
cấp làm điểm bắt đầu. Cả 6 BL đi `0x205b07c`; STR X20→[X19,#offset] khớp layout
trong `dump.cs` và offset 408/416/424/520/528/536. Event raw chứa token, **không**
có literal `field_id`; report180 §0–1 đã nói quá mức này.

Theo quy tắc token đã publish: `kind = token >> 29`, `src = token & 0x1fffffff`,
`ordinal = (src−1)/2` với kind 4 và src lẻ. `Board_PVP` TypeDefIndex 852 ở image
`Assembly-CSharp.dll`; PID cùng image TypeDefIndex 2461 có 740 field (kể cả scalar).
Từ ordinal, đọc field theo thứ tự dump, join `field-defaults.json`, unpack 24 byte
little-endian; kết quả dưới đây khớp 149 **và** registry-v4:

| Field | Ordinal → field index | 6 giá trị static |
|---|---:|---|
| `rewardIndexs` | 701 → 17001 | `[23, 0, 14, 1, 15, 18]` |
| `rewardValues` | 688 → 16988 | `[100, 10000, 10, 100, 10, 10]` |
| `rewardScales` | 634 → 16934 | `[1.0, 1.0, 0.6000000238418579, 1.0, 0.6000000238418579, 0.800000011920929]` |
| `allBetCoinValues` | 479 → 16779 | `[500, 2000, 5000, 10000, 20000, 50000]` |
| `allBetGemValues` | 173 → 16473 | `[0, 10, 25, 50, 100, 500]` |
| `allBetMedalValues` | 370 → 16670 | `[0, 30, 50, 100, 200, 1000]` |

Mã lệnh, slot, token, toàn bộ field-id, raw byte và kết quả có trong
`review-results.json:c1`. `rewardIndexs` còn khớp content anchor report133;
export `ia-resolved` có 1 event chồng lấn khớp, nhưng dùng **cùng convention**.
Đây là tái lập nhất quán mạnh trong hồ sơ static, **không** phải decoder token-format
độc lập từ global metadata hoặc bằng chứng constructor thật đã chạy. Disposition
`149` thay `169/177 NOT_BOUND` có cơ sở trong phạm vi đó; không sửa bản cũ.

## 3. C2 — registry, defaults, served và hai loại dữ liệu mới/cũ

**STATIC_CONFIRMED — cấu trúc sổ:** trên cut `cf17…`, 56 audit ID distinct =
23 `CLOSED` + 1 `NOTE` (#56) + 32 ledger ID distinct. 32 label thực tính lại:
20 `runtime-gated→USER`, 7 `served`, 3 `missing-input`, 2 `policy`; contract 33
= 32 ledger + #56. Mỗi row khớp audit/contract về identity, verdict, kind, literal
owner và có step không rỗng. Literal owner chỉ là `owner` (27 row) hoặc `AI-4`
(5 row); không biến chữ `owner` thành danh tính người cụ thể ở mọi row. Sổ 32 row
và step nằm trong `review-results.json:c2`. Đây là **kiểm bookkeeping toàn bộ**,
không phải chứng minh semantics độc lập của cả 32 entry.

- **Item9, corrected reading:** audit còn câu `served, not shipped` trong khi
  report157 §2 cho constructor default `MaxStockCount=10`, `ItemPlayerCost=50`,
  `ItemDroneCost=30`. Report158 §4–5 xuất bản bốn `EventRewards` shop tự dựng:
  stock từ field `MaxStockCount`, player/drone cost/value từ field shop; §7 không
  suy sang event-pass. `GATE1_CLOSURE_NOTES.md:10` tại `3179…` ghi **cách đọc đúng**:
  các đường shop đã xét có default build; giá/stock thực chưa đo; event-pass/served
  cần nguồn riêng, không khẳng định mọi SKU buộc qua server. Dòng `:9` cũ vẫn in
  câu rộng hơn; phải đọc **cùng đính chính :10**, không xem nó là kết luận phổ quát.
  Đường static không chứng minh state/runtime overwrite thật.
- **Items39/40:** audit vẫn chứa `blob unbound` dù `CLOSED`.
  `GATE1_CLOSURE_NOTES.md:11` chỉ rõ đó là quote lịch sử superseded; test producer
  chỉ tìm chuỗi `metadata usage`, không tự kiểm nghĩa tự nhiên. Không sửa audit cũ.
- **Item52 — CONFLICTING giữa hai cut:** registry-v4/138 nói slot `0x2ADB958`
  chưa định danh; report181 §1/artifact mới nói cùng slot là
  `FirebaseDatabaseManager.Instance`, census liệt kê hai parent 138. Report181 §7
  lại nói không đóng audit. `GATE1_CLOSURE_NOTES.md:30–33` ghi cả hai claim, giữ
  #52 trong sổ và gọi claim mới `INFERRED`/chưa đối chứng. Reviewer đồng ý **giữ
  conflicting/open**, không tự tuyên bố report181 proven. #51 cũng vẫn mở; remote
  content không tự biến thành đã đo.
- V4 không pin hash ngược cho drift (tránh chu kỳ); review pin **cả hai drift cut**
  bằng Git blob + SHA riêng. Các step không rỗng không phải giấy phép mở probe.

## 4. C3, C4, C5 — disposition đủ phạm vi, không phải proof

**C3/C5 — INFERRED/design disposition:** `DECISIONS_RESOLVED.md:26–36` ghi director
được user ủy quyền chọn profile `L1 static-complete + runtime-gated residuals có chủ`
và defer boss-phase×2, registry residuals, runtime 20+5. Trên spec `3179…`,
`GATE1_CLOSURE_NOTES.md:35–36` nói rõ các câu tuyệt đối `START_HERE.md:11`,
`DESIGN_READINESS.md` về L2 và mọi việc tĩnh đã đóng **không phải kết luận toàn cục**:
đó là scope L1 đã chọn, residual tiếp tục deferred/UNKNOWN/RUNTIME_UNVERIFIED.
Câu chữ cũ còn trong tài liệu; phải đọc kèm supersession. Điều này chấp nhận được
như một **quyết định phạm vi**, không chứng minh mọi số L2, toàn game static,
consumer, heap, graph, playback hay runtime đã đầy đủ. Bảy row `served` của registry
cũng vẫn mở dù parenthetical tại closure note chỉ nêu 20/3/2.

**C4 — supersession đủ phạm vi:** `DESIGN_READINESS.md:3` supersede **toàn văn**
các summary/tally/absolute, không chỉ ô bảng; `:22` và `:289` sửa thành không thấy
trong mẫu 139 file asm. `COVERAGE_AUDIT.md:49` cũng nêu sample boundary. Một số câu
cũ trong bảng/đoạn `DESIGN_READINESS.md:177–183` vẫn còn, nên phải đọc kèm note
`:3,168`. Zero hit trong mẫu không phải bằng chứng vắng mặt whole-game; bỏ
hit-stop/aim-assist trong Godot là **lựa chọn thiết kế mới**, không chứng minh game
gốc không có. Không cần APK/device mới để thực hiện supersession.

## 5. Điều kiện và việc tiếp theo — không biến verdict thành user approval

| Phạm vi / residual | Chủ hoặc bước đã ghi, giới hạn của review |
|---|---|
| C1 | Chuỗi 6/6 static nhất quán theo convention; token-format và runtime không được nâng mức bằng verdict này. |
| C2 | 32 row vẫn tồn tại ở cut `cf17…`: 20 runtime-gated, 7 served, 3 missing-input, 2 policy; #51 mở, #52 `CONFLICTING`. Đọc closure notes cùng artifact gốc. |
| Runtime/served | `USER` giữ quyền mở runtime lane; dữ liệu payload, giá/stock và state thực `RUNTIME_UNVERIFIED`. Không probe theo verdict này. |
| Missing/served owner `AI-4` | Năm row có literal `AI-4`; lane producer được board báo đã kết thúc. Công việc tiếp chỉ khi director/user phân lại và thực sự cần; không giả định session sẽ tự tiếp tục. |
| Các row literal `owner` | Sổ ghi owner/step nhưng không luôn định danh cá nhân; director điều phối và project owner/user giữ quyền quyết định theo mandate. Không giả vờ mọi policy đã được duyệt. |
| Boss phase ×2 | Defer cho `ef` **chỉ nếu** triển khai cần và được phân công; không suy #27 đầy đủ từ ACK 6/6. |
| Rights/store | Quyền tên/art gốc cần user xác nhận; tuân thủ commerce từng store. Không SDK, publish, merge, close hay force-push theo review này. |

Verdict chỉ nói các **disposition và evidence đã đủ để trình L1 có điều kiện**;
user/director có thể chọn chưa đóng Gate hoặc sửa quyết định. Không sửa historical
baseline, không nhận SDK/merge hay tự giao lane mới. Nghiên cứu thương mại/art có
thể tiếp tục theo phân công riêng, không phải kết luận khoa học của review này.

## 6. Chạy lại và kiểm chứng

```bash
python3 reverse-engineering/raw/geometry-8141386a/gate1-v4-review/verify_review.py --check
python3 reverse-engineering/raw/geometry-8141386a/gate1-v4-review/verify_review.py --check --git --fetch
python3 -m unittest discover -s reverse-engineering/raw/geometry-8141386a/gate1-v4-review -p 'test_review.py' -v
```

Local trên nội dung final được hash trong `local-validation/final-review-validation.json`:
`--check --git --fetch` so **46/46** source alias với Git, **22 test** verifier mới
PASS; kiểm các chuỗi supersession là kiểm locator, không chứng minh semantics/runtime.
Bộ test mới nằm ngoài `tests/` theo ownership hiện hành: **workflow cũ không tự chạy
bộ test này**. Spec `3179…` có docs/bridge/runtime workflow success lần lượt
`40521192778/40521193113/40521192929`; bước `Probe game state` trong runtime bị
**skipped**. CI exact-head của review phải được báo riêng sau push; xanh không chứng
minh semantic mới.

Legacy regression local **không hoàn tất**: monolithic run được chủ động ngắt ở
sampled RSS khoảng 1,16 GB; log giữ trong `local-validation/full-run-interrupted.log.gz`.
Lần chia batch phát hiện 1.710 test: ba batch đầu **600/600 PASS**, batch thứ tư bị
ngắt ở sampled 1.027.384 KiB trước khi hoàn tất (log 04), không tính PASS hay FAIL.
Test đang tới gọi `Recipes.recipe`, tải các section đầy đủ vào cache và không phù hợp
anti-OOM; dừng trước khi hoàn tất, không kết luận có tạo `Graph` hay không, không thử
lại hoặc nới giới hạn. 1.110 test còn lại không được tuyên bố đã chạy xong. Hai lỗi
setup harness giữ tại `local-validation/chunk-runner-setup.txt`, không sửa expected.
Xem `batch-summary.json`, 01–04.log.gz và `validation-summary.json`.

Ở local head trước đó `93e7f25917e4321cbf56970028ced21740266cc7`: README **0 lệch**;
live `APKD1=(130,107)`, `AI1=(139,142136,142,138,42,88)`, `RD1=(41,0)` đều PASS.
Historical-support = **209 PASS evaluations/0 FAIL/2 SKIP** (207 PASS ID distinct;
đây là overlay lịch sử, không phải all-current). Diagnostic unscoped = **163/25/23**,
exit 1; 25 FAIL ID trùng review125, **không có FAIL ID mới**. Log và digest lưu
riêng dưới `local-validation/`, không sửa receipt125 cũ.

**Nhãn:** `STATIC_CONFIRMED` chỉ byte/layout và join theo convention đã chỉ ra;
`RUNTIME_CONFIRMED` = **không có trong re-review này**; `INFERRED` = disposition/claim chưa chứng minh
độc lập; `RUNTIME_UNVERIFIED` = served payload, giá/stock thực, engine/device;
`UNKNOWN` = dữ liệu thiếu, quyền/policy chưa quyết; `CONFLICTING` = #52 và câu cũ
được supersede như đã chỉ ra.
