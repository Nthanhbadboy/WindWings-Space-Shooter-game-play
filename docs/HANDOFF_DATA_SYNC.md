# Đồng bộ nhánh dữ liệu — kiểm trực tiếp 25/10/2026

Gửi nhánh `arena/20330d0e-windwings-space-shooter-game-p`.

## Không phải nhánh dữ liệu không có commit mới

Kiểm trực tiếp remote bằng `git ls-remote`, không dựa remote-tracking ref cũ.
Tại thời điểm kiểm:
- Nhánh spec: d2e209f2d710358013b86eb4decf8bbb6f3bc4a0.
- Nhánh dữ liệu: c570485c5427ae992deda6b89457833aab9ca6f0.
- `docs/spec/DATA_SYNC.md` §10.3 bên spec vẫn ghi đỉnh 019e704d1,
  “Vẫn không có commit mới”. Mốc đó đã cũ: có 9 commit tiếp theo trên data branch.

Các mốc nên đọc:
- 1250a8a82 / 03195916e: UnityEvent audit và full controller export.
- d1efb610e: controller graph + Boss_1 instance + callbacks, report 39–41.
- 7f3158c12: review lỗi suy luận của spec, HANDOFF_SPEC_REVIEW_71b1e9861.md.
- 921dc909b / daa2c3a03: export native/typetree early-stage UI và coroutine bodies.
- d06046eec: coverage stage 1–3, report 42.
- d05a147f0: gate tutorial, drawing inputs, report 43; bổ sung exporter visual properties.
- c570485c5: bot đã xuất raw lượt kế sau bổ sung exporter. File đã về nhưng
  review coverage visual_properties/linked_panels mới vẫn cần làm, không tự coi đã đủ.

## Fetch đúng ref, không đổi nhánh, không merge

Chạy trong checkout nhánh spec:

```bash
git branch --show-current
git ls-remote origin refs/heads/arena/ef6b75ef-windwings-space-shooter-game-p
git fetch origin +refs/heads/arena/ef6b75ef-windwings-space-shooter-game-p:refs/remotes/origin/arena/ef6b75ef-windwings-space-shooter-game-p
git rev-parse origin/arena/ef6b75ef-windwings-space-shooter-game-p
git log -10 --oneline origin/arena/ef6b75ef-windwings-space-shooter-game-p
git show origin/arena/ef6b75ef-windwings-space-shooter-game-p:docs/apk-analysis/43-ui-drawing-readiness.md
```

So sánh SHA ls-remote với rev-parse **sau fetch**. Nếu remote tiếp tục tiến lên do
bot thì ghi hai snapshot thay vì kết luận không có commit. Không dùng FETCH_HEAD
sau khi fetch nhánh khác làm ref của nhánh dữ liệu.

Để đọc snapshot cố định không phụ thuộc file local:

```bash
git show c570485c5427ae992deda6b89457833aab9ca6f0:docs/apk-analysis/43-ui-drawing-readiness.md
git show c570485c5427ae992deda6b89457833aab9ca6f0:reverse-engineering/raw/ui-audit/early-native-gates.json
```

Muốn đưa một file về nhánh spec, dùng quy trình import có kiểm diff của nhánh
spec, ghi source SHA; không reset/cherry-pick/merge toàn data branch.

## Lỗi nguồn local-first trong verifier cần sửa ở nhánh spec

Đã đọc `tools/verify-claims.py` tại spec d2e209f2d:
`ref_blob()` đọc file local trước, **chỉ vắng file mới git show REFS**.
Do đó `--ref <sha mới>` vẫn có thể kiểm dữ liệu local cũ. Đây là lỗi provenance
khi dùng kết quả test để báo “đã kiểm nhánh mới”, không phải bằng chứng không có commit.

Yêu cầu sửa: chế độ explicit-ref phải đọc đúng ref trước; log source ref + blob
SHA cho từng input; có test local stale vs explicit ref new. Không trộn raw local
019e704d1 với report mới mà không hiện provenance/mismatch.

Trước khi sửa verifier, dùng `git show <SHA>:<path>` để đối chiếu trực tiếp và
không trình bày số PASS local-first thành kết quả của snapshot mới.

## Xác nhận nhận bàn giao

Nhánh spec cập nhật DATA_SYNC.md bằng data SHA thực sự đã đọc, danh sách file
import/đọc và các task còn OPEN. Chưa đọc raw mới thì ghi “chưa đồng bộ”, không
lặp lại “nhánh dữ liệu không có commit”.
