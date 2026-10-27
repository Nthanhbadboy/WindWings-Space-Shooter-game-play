# PHASE C — KẾ HOẠCH TRIỂN KHAI 3 STORE (Microsoft Store · Amazon Appstore · Huawei AppGallery)

> **Cơ sở:** user lần 132 (2026-10-27): *"tự quyết và phân việc; phân tích chỉ để học tập — cần thiết lắm mới đào thêm; không thì triển khai theo kế hoạch."*
> Quyết định D1–D12: `../research/phase-b/DECISIONS_RESOLVED.md`. Nghiên cứu nguồn: `../research/phase-b/` (S1–S73, 2026-10-27).
> **Ràng buộc mandate giữ nguyên:** director + 4 session KHÔNG tự SDK/publish/merge; mọi bước chạm tài khoản/keys/store-upload là **USER-ONLY**. Nhãn bằng chứng 6 loại áp dụng cho mọi số liệu mới.

## Trạng thái 3 kênh (số từ Phase B, có nguồn)

| Kênh | Phí account | Revenue share | Cert/review | Ghi chú |
|---|---|---|---|---|
| Microsoft Store | **$0** (Individual free từ 10/09/2025, Company bỏ $99 từ 07/05/2026) | game **12%** (dev 88%); app 15% | ≤3 business days | Cần **bản Windows** — xem USER-ONLY #3 |
| Amazon Appstore | $0 | 70/30 (SBAP 80/20 khi đủ điều kiện) | — | Kênh Android mobile đã đóng 20/08/2025 → **Fire tablet/TV only** (D1a/D10a) |
| Huawei AppGallery | $0 (individual/enterprise) + identity verification bắt buộc | IAP game **30:70 ngoài TQ** · 50:50 đại lục; paid 30:70 | 3–5 ngày làm việc | APK ≤4GB; AAB ≤150MB (App Signing bắt buộc); 170+ nước (D2a) |

## Phân việc (theo lệnh "phân việc" lần 132)

| Session | Lane mới | Bounded bởi |
|---|---|---|
| **SS 0 (director)** | Tích hợp + sổ cái + board PR12; trình Gate khi đủ | Không implement/SDK/publish; user final authority |
| **AI-4 (535)** | **C2: registry-v4** — sổ ledger cuối best-effort; C1 resolve opportunistic nếu rẻ; xong lane | KHÔNG đào lane mới; số mở không cần = 0 |
| **ef** | **Phase C build/packaging spec** (plan-level): signing flow, versioning, target-API/SDK requirements AppGallery + Amazon, APK/AAB packaging path, MS Windows packaging options | KHÔNG build/SDK/keystore thật; boss-phase×2 → learning-note, chỉ đào nếu triển khai cần |
| **a5** | **Phase C store assets spec**: icon/screenshot/feature-graphic sizes từ 84-file capture + 42 contact sheets (không vẽ art mới); listing copy draft 3 store | Asset thật do Session F planner + user duyệt |
| **Session E** | **Per-store requirement sheets**: rating questionnaire, data-safety/privacy forms, payout/tax setup steps — nguồn chính chủ + ngày tra cứu, UNVERIFIED ghi tại chỗ | Research/plan only |
| **Session F** | Store-art planner theo spec của a5 (asset list, kích thước, số lượng) | Không tự chốt art — user duyệt |
| **AI-3** | Re-review Gate-1 khi registry-v4 về (đơn giản: xác nhận C1–C5 khép) → sau đó verify-lane | Verdict chỉ reviewer nâng |

## User-ONLY checklist (không session nào làm được — Gate chặn tại đây)

1. **D5/pháp lý:** xác nhận individual hay pháp nhân + tình trạng thuế TRƯỚC khi tạo tài khoản (Huawei không đổi quốc gia verify; MS không đổi Individual→Company).
2. **Tạo 3 tài khoản developer** + identity verification (MS $0 · Amazon $0 · Huawei $0) — dùng email/điện thoại của user.
3. **⚠ Unity project source cho bản Windows** — repo chỉ có APK; MS Store cần build Windows. **Câu hỏi cho user:** bạn có project gốc không (tự phát triển/được ủy quyền)? (a) Có → ef viết build-spec là đủ; (b) Không/được ủy quyền phân phối → cần xác nhận **quyền phân phối/IP** trước khi register anywhere; MS leg hoãn tới khi rõ.
4. **Release keystore/signing** — chỉ user giữ và tự sign.
5. **Payout/tax profiles** từng store (ngân hàng, thuế, địa chỉ).
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
- ef: build/packaging spec (không build).
- AI-4: registry-v4 khép Gate-1.
- Mọi thứ chạm tài khoản/keys/source/build thật → dừng ở USER-ONLY checklist.
