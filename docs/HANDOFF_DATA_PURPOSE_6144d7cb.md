# Bàn giao nhánh dữ liệu — bổ sung "Mục đích" vào docs bên đó (chủ dự án chốt 25/10, lần 14–16)

> **Tại sao:** chủ dự án đã chốt lại mục đích toàn dự án bên nhánh spec
> (`arena/20330d0e-windwings-space-shooter-game-p`, commits `f60f387528` → `ad7943ce0e` → `6144d7cb70`):
> **dịch ngược để bắt chước bản gốc — không sáng tạo tự do; mọi thứ trừ art đã có bản gốc trả lời,
> không test không hỏi lại; việc thiết kế duy nhất là vẽ lại art; L3 = đối chiếu reference đo được,
> KHÔNG hoãn, KHÔNG cần playtest người thật.** Nhánh dữ liệu cần cùng hướng này trong docs bàn giao
> để AI phía bên đó không đọc lệch thành "còn thiếu quyết định sản phẩm".
>
> **Cách áp dụng:** nhánh dữ liệu tự commit theo quy trình của bên đó (PR riêng `docs(...)`,
> không merge nhánh spec). Base đã đọc: **`ffa9959c9e`** (report 82). Ba chỗ chèn dưới đây là
> **paste-ready**, anchor trích nguyên văn từ tip `ffa9959c9e`.

## 1. `docs/START_HERE_NEW_GAME.md` — chèn khối ngay sau dòng 3

Anchor (giữ nguyên văn, chèn **sau** dòng này):

```
Repo này là **kho dữ liệu reverse-engineering + tài liệu tham khảo**, **chưa phải project game chạy được**. Có đủ dữ liệu để bắt đầu prototype có scope; chưa phải hợp đồng đầy đủ để một agent tự dựng/phát hành cả game mà không hỏi quyết định sản phẩm.
```

Chèn thêm:

```
**Quyết định sản phẩm ĐÃ CÓ (chủ dự án chốt 25/10):** mục đích của repo là đủ thứ để **thiết kế game mới theo cách BẮT CHƯỚC bản gốc** — không sáng tạo cơ chế. Cơ chế · logic · số · animation · nhịp · màu · ánh sáng: **bản gốc đã trả lời hết** — tra reference trong repo là xong, **không test, không hỏi lại**. **Việc thiết kế duy nhất là art**: vẽ lại hình ảnh cho khác (không copy file asset), giữ chuẩn khung/màu/ánh sáng/nhịp theo số đo (`VISUAL_DESIGN.md` nhánh spec: khung 0,4813 · tương phản 0,45–0,80 · accent ≤10 % gameplay/~47 % khung thưởng · chi tiết 13–22 · juice 0,05 s/0,10·20 frame). **Nghiệm thu mức cao nhất = đối chiếu reference đo được bằng máy** (metrics + so ảnh cùng scene + timeline 795 event + audio 15 rules) — **không blind A/B, không playtest người thật**; APK gốc là chuẩn trải nghiệm đã kiểm nghiệm, dự án để học tập thiết kế. Chi tiết: nhánh spec `arena/20330d0e…` — `START_HERE.md` (khối đầu) · `DONE.md` §2 (mức L0–L3, lần 14).
```

Đồng thời sửa vế cuối của dòng 3 cho hết mâu thuẫn:

- Cũ: `chưa phải hợp đồng đầy đủ để một agent tự dựng/phát hành cả game mà không hỏi quyết định sản phẩm.`
- Mới: `quyết định sản phẩm đã có (khối ngay dưới) — làm theo reference, không cần hỏi thêm.`

## 2. `docs/HANDOFF_AI_TASKS.md` — chèn 1 blockquote sau dòng 3

Anchor (chèn **sau**):

```
> **Cửa vào hiện hành (sau report82):** đọc [START_HERE_NEW_GAME.md](START_HERE_NEW_GAME.md) + report81 combat-chain + report82 proof-audit. Review cf27b9755 và các vòng/snapshot cũ dưới đây là lịch sử, chỉ áp dụng finding còn mở; không tự là task hay phán xét hiện hành.
```

Chèn thêm:

```
> **Mục đích (chủ dự án 25/10):** mọi task dưới đây phục vụ việc **bắt chước bản gốc 1:1** — không sáng tạo cơ chế; bản gốc đã trả lời mọi thứ trừ art; **không test, không hỏi lại — có bản gốc trả lời**. Việc thiết kế duy nhất của game mới = **vẽ lại art** (`VISUAL_DESIGN.md` nhánh spec). Nghiệm thu cao nhất = đối chiếu reference đo được, không playtest.
```

## 3. `datas/README.md` — chèn 1 câu sau dòng giới thiệu

Anchor (chèn **sau**):

```
Dữ liệu bóc từ APK **WindWings: Space Shooter 1.3.118**, đã chuẩn hoá thành JSON để dùng cho
bản clone (engine nào cũng đọc được). Sinh tự động bằng:
```

Chèn thêm (trước khối code):

```
Mục đích dùng: **bắt chước bản gốc 1:1** (cơ chế/số/âm/nhịp) — chỉ **art là vẽ lại** theo chuẩn đo được; thắc mắc thông số tra reference trong repo, không test không hỏi lại.
```

## Ghi chú

- Không đụng luật bằng chứng của nhánh dữ liệu (mức A/B/C, `APK fact + raw_ref + scope`, pin SHA) —
  bổ sung này là **mục đích sản phẩm**, không đổi quy trình kiểm chứng.
- Kênh trao đổi: PR #12. Bên spec không push nhánh dữ liệu (khuôn phiên chỉ push nhánh spec).
- Sau khi bên dữ liệu commit, nhắc lại trong report kế: "đã bổ sung mục đích theo `6144d7cb70`".
