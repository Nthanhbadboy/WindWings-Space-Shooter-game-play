# Re-review Gate-1: registry-v4 và C1–C5 — `arena/8141386a`

**Trạng thái bản nháp (chưa handoff): `NOT_READY` tại spec cut bên dưới.** Đây là
khuyến nghị review cho hồ sơ/phạm vi đề xuất, không phải user duyệt Gate, không phải
lệnh scaffold/SDK/store/publish/merge và không kết luận runtime parity. Có thể cân nhắc
nâng lên verdict **bounded L1** nếu director ghi rõ các disposition còn thiếu; xem §5.

## 1. Cut, authority và phương pháp

- Producer v4: `cf17c7f22f855c3fb93191e3661fdaaa756a7d80`; registry-v4 SHA-256
  `bcd0e0fd95af375b8841021856209eb701d284bf013966d48f868e9143e21a96`.
- Spec: `1b43f5dc5069e1b7cccec2dd000d1d107e746277`; registry-v4 **trùng byte**
  producer. Cut cũ để so C4: `c21b265547df02911e63c06b31cb83a76c5f03f9`.
- Producer mới hơn: `afacf4b06bcfff130db4163c5a0400ea5d862ace` thêm report181;
  registry và audit vẫn trùng byte, contract drift vẫn trùng, nhưng artifact-count
  drift tăng 48→49. Report181 được xem như **claim mới của producer**, chưa được
  independently audit. Không tự nâng verdict item52 (§3).
- Review125/HANDOFF `6440973318`, ACK `6441583848`, cut cố định và 8 findings/5
  conditions vẫn là lịch sử **`NOT_READY`**; tài liệu này là addendum, không sửa
  báo cáo, receipt, counts hay baseline cũ. Không tự ACK.
- 41 alias nguồn/38 archive độc nhất: `source-manifest.json` ghi commit, đường dẫn,
  Git blob OID, SHA-256, kích thước nguồn và SHA-256 archive. Archive là gzip của
  **nguyên Git blob**, kể cả khi blob vốn là `.gz`. `--git --fetch` so từng byte với
  Git ở commit đã chọn. `api-captures.json.gz` lưu các phản hồi GitHub API đã lấy,
  có timestamp; đây không phải bằng chứng GitHub ký, cũng không thay thế CI của head
  review tương lai.
- Không chạy code verifier của producer; không trích APK, giải thêm binary/metadata,
  chạy emulator/device, sử dụng credentials hay tạo fixture Graph/atlas toàn bộ.
  Original APK vẫn là authority; đây chỉ là đọc lại **hồ sơ đã publish**.

## 2. C1 — tự dựng lại join trong phạm vi static

**STATIC_CONFIRMED, có điều kiện theo convention đã công bố:** constructor
`Board_PVP..ctor` RVA `19796420`, 500 byte, lấy từ slice `key-grant` SHA
`3f43642ab14858f205d99a6b63c93ba5fa601d3ae1318e1f2b3948a729c23ffb`. Tự đọc
6 event, 6 từ lệnh BL và 6 STR trực tiếp từ byte slice; không dùng field_id do 149
cấp làm điểm bắt đầu. Cả 6 BL đi `0x205b07c`; các STR X20→[X19,#offset] khớp
layout trong `dump.cs` và offset 408/416/424/520/528/536. Event raw chứa token,
**không** có literal `field_id`; report180 §0–1 đã nói quá mức này.

Theo quy tắc token đã publish: `kind = token >> 29`, `src = token & 0x1fffffff`,
`ordinal = (src−1)/2` với kind 4 và src lẻ. `Board_PVP` TypeDefIndex 852 ở image
`Assembly-CSharp.dll`; PID cùng image TypeDefIndex 2461 có 740 field (kể cả scalar).
Từ ordinal, đọc đúng field theo thứ tự dump, join `field-defaults.json`, unpack
24 byte little-endian; kết quả dưới đây khớp 149 **và** registry-v4:

| Field | Ordinal → field index | 6 giá trị static |
|---|---:|---|
| `rewardIndexs` | 701 → 17001 | `[23, 0, 14, 1, 15, 18]` |
| `rewardValues` | 688 → 16988 | `[100, 10000, 10, 100, 10, 10]` |
| `rewardScales` | 634 → 16934 | `[1.0, 1.0, 0.6000000238418579, 1.0, 0.6000000238418579, 0.800000011920929]` |
| `allBetCoinValues` | 479 → 16779 | `[500, 2000, 5000, 10000, 20000, 50000]` |
| `allBetGemValues` | 173 → 16473 | `[0, 10, 25, 50, 100, 500]` |
| `allBetMedalValues` | 370 → 16670 | `[0, 30, 50, 100, 200, 1000]` |

Mã lệnh, slot, token, toàn bộ field-id, raw byte và kết quả có trong
`review-results.json:c1`. `rewardIndexs` còn khớp content anchor độc lập report133;
export `ia-resolved` có 1 event chồng lấn khớp, nhưng dùng **cùng convention**. Đây
là tái lập nhất quán mạnh trong hồ sơ static, **không** phải decoder token-format
độc lập từ global metadata hoặc bằng chứng constructor thật đã chạy. Disposition
`149` thay `169/177 NOT_BOUND` có cơ sở trong phạm vi đó; không sửa bản cũ.

## 3. C2 — registry, defaults, served và hai loại dữ liệu mới/cũ

**STATIC_CONFIRMED — cấu trúc sổ:** trên cut `cf17…`, 56 audit ID distinct =
23 `CLOSED` + 1 `NOTE` (#56) + 32 ledger ID distinct. 32 label thực tính lại:
20 `runtime-gated→USER`, 7 `served`, 3 `missing-input`, 2 `policy`; contract 33
= 32 ledger + #56. Mỗi row khớp audit/contract về identity, verdict, kind, literal
owner và có step không rỗng. Literal owner chỉ là `owner` (27 row) hoặc `AI-4`
(5 row); nhãn/user delegation và defer-list vẫn phải được đọc kèm, không biến
chữ `owner` thành danh tính người cụ thể ở mọi row. Sổ 32 row và step nằm trong
`review-results.json:c2`. Đây là **kiểm bookkeeping toàn bộ**, không phải chứng
minh semantics độc lập của cả 32 entry.

- **CONFLICTING — item9:** audit còn nguyên câu `served, not shipped` trong khi
  report157 §2 cho constructor default `MaxStockCount=10`, `ItemPlayerCost=50`,
  `ItemDroneCost=30`. `GATE1_CLOSURE_NOTES.md:7–10` đã công nhận defaults nhưng
  lại khẳng định mọi per-SKU giá/stock thực do `GetConfigs` phục vụ. Report158
  §4–5 xuất bản bốn `EventRewards` shop tự dựng; stock từ `MaxStockCount`,
  player/drone cost/value từ field shop; §7 nói rõ không suy sang event-pass.
  Sửa thành **default build + các đường shop đã xét** so với **giá/stock thực và
  payload event/served chưa đo**, không khẳng định nguồn server phổ quát. Runtime
  hay ghi đè thật vẫn `RUNTIME_UNVERIFIED`.
- **STATIC_CONFIRMED editorial disposition:** các trường `blocking` của audit
  #39/#40 vẫn có `blob unbound` dù `CLOSED`. Spec `GATE1_CLOSURE_NOTES.md:11`
  nói rõ đó là quote lịch sử đã supersede; test producer chỉ tìm chuỗi
  `metadata usage`, không tự kiểm nghĩa tự nhiên. Không sửa byte audit cũ.
- **CONFLICTING — item52 giữa hai cut:** registry-v4/138 nói slot `0x2ADB958`
  chưa định danh; report181 §1 và artifact mới nói cùng slot là
  `FirebaseDatabaseManager.Instance`, census liệt kê cả hai parent 138. 181 §7
  lại nói không đóng audit. Phát biểu mới chưa được reviewer này re-audit; ghi nhận
  discrepancy/claim mới, không tự tuyên bố #52 đã đóng hay 181 đã proven. Xin owner
  203 ghi disposition phù hợp; policy/remote state không tự biến thành đã đo.
  #51 vẫn mở tại cut này.
- Cả 32 owner/step là thông tin có mặt trong sổ, không phải lời hứa dữ liệu runtime
  có thể thu thập hoặc giấy phép mở device/probe. V4 không pin hash ngược cho drift
  (tránh chu kỳ); bản review pin **cả hai drift cut** bằng Git blob + SHA riêng.

## 4. C3, C4, C5 — quyết định phạm vi không phải proof

**C3/C5 — INFERRED/design disposition:** `DECISIONS_RESOLVED.md:26–36` ghi director
được user ủy quyền chọn profile `L1 static-complete + runtime-gated residuals có chủ`
và defer boss-phase×2, registry residuals, runtime 20+5. Đây là quyết định về phạm vi
triển khai, không chứng minh mọi số L2 hay toàn game static đã đầy đủ. Tại `1b43…`,
`START_HERE.md:11` còn “việc thiết kế duy nhất là ART”,
`DESIGN_READINESS.md:297–298` nói L2 không còn thiếu số và `:309` nói mọi việc tĩnh
đã đóng. Chúng chưa được supersede rõ như scope của lựa chọn L1; cần chú thích bao
phủ cả các summary đó. Residual vẫn `UNKNOWN`/`RUNTIME_UNVERIFIED` hoặc design choice;
boss/consumer/layout/playback đầy đủ không được suy ra từ “6/6 review”.

**C4 — CONFLICTING tại cut này:** `DESIGN_READINESS.md:166` đã supersede các ô
trong bảng §4.1b; `COVERAGE_AUDIT.md:49` đổi thành không thấy trong mẫu 139 file.
Nhưng `DESIGN_READINESS.md:20,179–180,287` vẫn dùng ngôn ngữ “game gốc không có” /
“3 mục không tồn tại” **ngoài phạm vi các ô** được supersede rõ. 0 hit trong mẫu
139 asm không phải bằng chứng vắng mặt whole-game. Bỏ hit-stop/aim-assist trong
Godot có thể là quyết định thiết kế mới, không là chứng minh trạng thái game gốc.

## 5. Việc cần trước khi nâng verdict

Owner spec `20330d0e` (không phải reviewer này) cần ghi một lớp supersession/đính
chính đủ rõ cho: (1) C2 item9 đúng đường shop/event, không khẳng định nguồn runtime
phổ quát; (2) C4 toàn bộ summary/tally ngoài bảng; (3) C3/C5 các tuyên bố tuyệt đối
được giới hạn theo profile đã chọn, với residual/owner/next step còn mở; (4) xử lý
claim report181 mới vs item52 mà không viết lại v4 lịch sử. Có thể chỉ cần note bổ
sung, không cần đào APK/device. Policy #51/#52, quyền tên/art gốc, store/SDK và
runtime vẫn chịu decision/permission tương ứng; CI xanh không phải chấp thuận.

Các disposition của director là quyết định theo ủy quyền được báo cáo trên PR12,
không phải reviewer tự ban hành. Nếu những điểm trên được ghi rõ, verdict có thể là
`APPROVE-BOUNDED` / sẵn sàng trình director & user cho **L1 có residuals**, không
phải approval Gate, full fidelity, runtime, licensing hay publication. Nếu không,
`NOT_READY` áp dụng cho cut hiện tại; không phải lệnh dừng nghiên cứu thương mại/art.

## 6. Chạy lại và kiểm chứng

```bash
python3 reverse-engineering/raw/geometry-8141386a/gate1-v4-review/verify_review.py --check
python3 reverse-engineering/raw/geometry-8141386a/gate1-v4-review/verify_review.py --check --git --fetch
python3 -m unittest discover -s reverse-engineering/raw/geometry-8141386a/gate1-v4-review -p 'test_review.py' -v
```

Local: `--check --git` đã so **41/41** source alias với Git; **21 test** verifier mới
PASS. Bộ test mới nằm ngoài `tests/` theo ownership hiện hành: **workflow cũ không
chạy tự động bộ test này**. CI của review head phải được báo cáo riêng bằng đúng
headSha sau khi push; CI cũ trong API snapshot chỉ kiểm workflows tương ứng, không
phải chứng minh semantic mới.

Full legacy regression: lần chạy monolithic được **chủ động ngắt** khi sampled RSS
khoảng 1,16 GB để tuân thủ giới hạn chống OOM; log chưa hoàn tất được giữ trong
`local-validation/full-run-interrupted.log.gz`, không tính PASS hay FAIL. Đang chạy
lại 1.710 test theo các process tối đa 200 test, có giám sát RSS; kết quả sẽ được
bổ sung trước handoff. Hai lỗi setup harness được giữ tại
`local-validation/chunk-runner-setup.txt`, không sửa expected value.

**Nhãn:** `STATIC_CONFIRMED` chỉ dữ liệu/byte đã chỉ ra và phép join theo convention;
`RUNTIME_CONFIRMED` = **không có**; `INFERRED` = disposition/claim chưa chứng minh
độc lập; `RUNTIME_UNVERIFIED` = served payload, giá/stock thực, engine/device;
`UNKNOWN` = dữ liệu thiếu, quyền/policy chưa quyết; `CONFLICTING` = item9/item52 và
các summary C4/C3/C5 như trên.
