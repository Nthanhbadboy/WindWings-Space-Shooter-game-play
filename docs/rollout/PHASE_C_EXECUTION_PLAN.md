# PHASE C — KẾ HOẠCH TRIỂN KHAI 3 STORE (Microsoft Store · Amazon Appstore · Huawei AppGallery)

> **Cơ sở:** user lần 132 (2026-10-27): *"tự quyết và phân việc; phân tích chỉ để học tập — cần thiết lắm mới đào thêm; không thì triển khai theo kế hoạch."*
> Quyết định D1–D12: `../research/phase-b/DECISIONS_RESOLVED.md`. Nghiên cứu nguồn: `../research/phase-b/` (S1–S73, 2026-10-27).
> **Ràng buộc mandate giữ nguyên:** director + 4 session KHÔNG tự SDK/publish/merge; mọi bước chạm tài khoản/keys/store-upload là **USER-ONLY**. Nhãn bằng chứng 6 loại áp dụng cho mọi số liệu mới.

## Trạng thái 3 kênh (số từ Phase B, có nguồn)

| Kênh | Phí account | Revenue share | Cert/review | Ghi chú |
|---|---|---|---|---|
| Microsoft Store | **$0** (Individual free từ 10/09/2025, Company bỏ $99 từ 07/05/2026) | game **12%** (dev 88%); app 15% | ≤3 business days | Cần **bản Windows** — build Godot (engine chốt lần 134, xem §Engine) |
| Amazon Appstore | $0 | 70/30 (SBAP 80/20 khi đủ điều kiện) | — | Kênh Android mobile đã đóng 20/08/2025 → **Fire tablet/TV only** (D1a/D10a) |
| Huawei AppGallery | $0 (individual/enterprise) + identity verification bắt buộc | IAP game **30:70 ngoài TQ** · 50:50 đại lục; paid 30:70 | 3–5 ngày làm việc | APK ≤4GB; AAB ≤150MB (App Signing bắt buộc); 170+ nước (D2a) |

## Phân việc (theo lệnh "phân việc" lần 132)

| Session | Lane mới | Bounded bởi |
|---|---|---|
| **SS 0 (director)** | Tích hợp + sổ cái + board PR12; trình Gate khi đủ | Không implement/SDK/publish; user final authority |
| **AI-4 (535)** | **C2: registry-v4** — sổ ledger cuối best-effort; C1 resolve opportunistic nếu rẻ; xong lane | KHÔNG đào lane mới; số mở không cần = 0 |
| **ef** | **Godot build/packaging spec + port plan** (plan-level): export presets (Windows → MS Store MSIX; Android APK≤4GB / AAB≤150MB qua gradle), versioning, signing flow, target-API AppGallery/Amazon; port-plan: scaffold Godot 4.x + map scene/systems từ spec #29 — chỉ hiện thực hóa khi user ra lệnh scaffold | KHÔNG build/SDK/keystore thật; lanes APK dừng — phân tích chỉ khi triển khai cần |
| **a5** | **Phase C store assets spec**: icon/screenshot/feature-graphic sizes từ 84-file capture + 42 contact sheets (không vẽ art mới); listing copy draft 3 store | Asset thật do Session F planner + user duyệt |
| **Session E** | **Per-store requirement sheets**: rating questionnaire, data-safety/privacy forms, payout/tax setup steps — nguồn chính chủ + ngày tra cứu, UNVERIFIED ghi tại chỗ · **+ research queue kiếm tiền** (bảng dưới — lần 133: đào-tiếp áp dụng cho E/F, KHÔNG phải APK) | Research/plan only |
| **Session F** (`1b836828`, đã xác thực) | **Art planner** — redraw plan 788 đơn vị vẽ (651 dòng planner, L2=149h) — `docs/art-plan/` trên nhánh F | Production art KHÔNG giao F — mở Session H khi Gate-5 (xem `SESSION_CAPABILITY_AUDIT_2026-10-27.md`) |
| **AI-3** | Re-review Gate-1 khi registry-v4 về (đơn giản: xác nhận C1–C5 khép) → sau đó verify-lane | Verdict chỉ reviewer nâng |

## Research queue E/F — đào TIẾP theo lệnh lần 133 ("nghiên cứu của E và F có chỗ nào khúc mắc thì nghiên cứu tiếp — mục đích làm game kiếm tiền")

> Làm rõ scope (lần 133): lệnh dừng-đào chỉ áp dụng cho **APK analysis** (ef/a5/535/AI-3 — boss-phase, C1-reconcile, registry deep-dive, probe). Nghiên cứu **thị trường/store/kiếm tiền** của E và F tiếp tục. Queue lấy từ cột "Thông tin còn thiếu" của `../research/phase-b/DECISIONS_NEEDED.md` — lọc ra các mục tra cứu được từ nguồn công khai:

| Từ D# | Câu hỏi khúc mắc | Giao | Researchable từ nguồn công khai? |
|---|---|---|---|
| D4/D6 | **Giá benchmark remove-ads + premium trong genre shmup** (Sky Force $3,99; 1945; HAWK; Phoenix 2…) → đề xuất bảng giá cụ thể trình user Gate-3 | E | ✓ — giá store công khai |
| D3 | ~~**eCPM/fill-rate rewarded trên Windows**~~ **BỊ HỦY 2026-10-28** — Windows không ads (CHỐT USER) ⇒ không cần benchmark eCPM, không cần hợp đồng Vungle Windows. D3 giờ chỉ còn lane Android/Fire/AppGallery | — | **Không còn việc này** (hủy do D3b chốt) |
| D9 | **Ma trận plugin Godot 4.x cho 3 store**: IAP (Godot Google Play Billing chính chủ · HMS IAP community plugin · Amazon IAP wrapper?) · ads (AdMob Poing-plugin — chú ý Fire thiếu GMS · HMS Ads Kit) · đóng gói MSIX cho MS Store | E | ✓ — docs SDK |
| D11 | **Tương thích analytics/CMP trên Fire + HMS** (GameAnalytics, Firebase fork, Unity Analytics; consent GDPR) | E | ✓ — docs SDK |
| D7 | **Luật gacha/loot-box từng nước cập nhật** (Bỉ/Hà Lan, EU) — thu thập trước Gate-7 | E | ✓ — nguồn pháp lý công khai |
| D2 | Danh sách NPH TQ phù hợp + quy trình 版号 (chỉ cần khi user đổi ý D2) — ưu tiên thấp | E | ✓ — để sẵn |
| D1/D10 | **Quy mô thiết bị Fire** (installed base Amazon thiết bị 2024–2026) + yêu cầu VPKG Vega — định lượng giá trị kênh Amazon | E | ✓ một phần |
| D12 | **Retention/LTV median genre shooting 2025–2026** — làm chuẩn so khi có data thật | E | ✓ — report industry |
| Assets | **Số lượng/kích thước asset từng store + checklist chuyển đổi listing** (CTR thumbnail, A/B screenshot genre) | F | ✓ |
| D5/D3-hop-hợp/D12-ngân-sách | Pháp nhân, thuế, hợp đồng ads, ngân sách UA | — | ✗ USER-ONLY — không research thay được |

## User-ONLY checklist (không session nào làm được — Gate chặn tại đây)

1. **D5/pháp lý — CẬP NHẬT lần 135 (theo user, chưa commit):** MS ✓ đã có tài khoản + khai thuế · Huawei ✓ đã đăng ký · Amazon ✗ chưa làm. Lưu ý: dùng đúng loại tài khoản đã tạo (policy 10.14 — xem MONETIZATION_VERIFICATION).
2. **Tạo tài khoản developer → chỉ còn AMAZON** (MS ✓ Huawei ✓ theo user): register $0 + Tax Identity Interview (Mỹ+Canada) — bữa nào user rảnh làm ~15 phút. Chi tiết: MONETIZATION_VERIFICATION_2026-10-27.md.
3. **Quyền IP/phân phối khi đăng store** (viết lại lần 134 — câu Unity-source hết hiệu lực vì engine = Godot, build mới không cần source gốc): assets/spec đang trích từ APK gốc WindWings — user xác nhận quyền sử dụng art/tên/nội dung game khi đăng 3 store. Bản Windows chỉ chờ mục này (không chờ Unity nữa).
4. **Release keystore/signing — user xác nhận tự thêm** ✓. Nhớ: Huawei AAB bắt buộc App Signing (bật trong console); MS Store tự ký MSIX — không cần keystore riêng.
5. **Payout/tax** — MS ✓ · Huawei ✓ (merchant IAP + Petal Ads, trả tháng, ngưỡng €200) · Amazon pending. **Phát hiện tiền:** VN chưa có thuế-hiệp-định với Mỹ đang hiệu lực ⇒ phần doanh thu khách Mỹ bị withholding 30% (không giảm được); ngoài Mỹ không giữ tại nguồn — tách dòng US/không-US khi báo doanh thu.
6. **Lệnh SDK/publish** khi đến Gate tương ứng (mandate: không tự publish).

## Tiến trình Gate (không vượt silently)

| Gate | Nội dung | Trách nhiệm | Hiện trạng |
|---|---|---|---|
| **Gate-1** Phase A acceptance | C1–C5 khép theo `DECISIONS_RESOLVED.md` §disposition + registry-v4 | AI-4 xuất; AI-3 re-review; user sign-off | **READY-FOR-CLOSE** (chờ registry-v4) |
| **Gate-2** Kênh & phạm vi | D1/D2/D5/D10 đã quyết; user xác nhận D5 + quyền phân phối | USER | Chờ user #1/#3 |
| **Gate-3** Mô hình kiếm tiền | D3/D4/D6/D7/D8 đã quyết; user duyệt bảng giá/SKU | USER duyệt | Cấu hình đã chốt, chờ duyệt giá |
| **Gate-4** Kỹ thuật build | build-spec ef + adapter D9a + analytics D11a; source Windows | USER cung source + lệnh SDK | Chờ #3 |
| **Gate-5** Assets & listing | spec a5 + planner F; user duyệt art | USER duyệt | Bắt đầu được NGAY |
| **Gate-6** Submission kit | requirement sheets E + form đi sẵn (draft) | USER tự tay nộp | Bắt đầu được NGAY |
| **Gate-7** Launch & sau launch | compliance từng nước (D7), UA D12 | USER | Sau khi có build |

## Bắt đầu được NGAY (không cần chờ user) — theo phân việc trên

- a5: asset spec + listing draft (từ dữ liệu có sẵn).
- Session E: requirement sheets 3 store.
- ef: Godot build/packaging spec + port-plan (không build — scaffold chỉ theo lệnh).
- AI-4: registry-v4 khép Gate-1.
- Mọi thứ chạm tài khoản/keys/source/build thật → dừng ở USER-ONLY checklist.
