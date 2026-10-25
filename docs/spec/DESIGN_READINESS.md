# DESIGN_READINESS — đã đủ để bắt tay thiết kế chưa?

> **Câu hỏi:** *"Đã OK để thiết kế game mới chưa?"*
>
> **Trả lời ngắn: ĐỦ — cho phạm vi đã chốt (L1: giống cơ chế, không cần giống số).**
> Và **không** đủ nếu ai đó định làm L2/L3 (khớp số / không phân biệt được).
>
> Tài liệu này đo lại **9 câu blocker** của `DESIGN_QUESTIONS.md` bằng dữ liệu đang có trong repo,
> không chép lại đánh giá cũ. Mỗi dòng đều chạy lại được bằng `tools/verify-claims.py` (nhóm `I`).

---

## 1. Vì sao "đủ" — cái gì đã chốt

`DONE.md` §4.2 đã ghi quyết định phạm vi:

> **L1: giống cơ chế, không cần giống số.**

Đây là điều làm câu trả lời thành **có**. 9 blocker trong `DESIGN_QUESTIONS.md` được viết khi mục
tiêu còn là L2/L3 — *"sao cho giống bản gốc"*. Dưới L1, phần lớn chúng **không còn là blocker**:
chúng là **tham khảo**, không phải điều kiện.

---

## 2. Chín blocker — trạng thái **đo lại hôm nay**

| # | Câu | Trạng thái cũ | **Đo lại 23/10** | Chặn thiết kế L1? |
|---:|---|---|---|---|
| 1 | `StartHp` | đóng (2500) | ✅ **đóng** — `statics_Player_Get_Datas.StartHp = 2500` | **Không** |
| 2 | **A6 — stage ↔ wave** | mở | 🟡 **một phần** — `map_waves_candidate.json`: **250 map**, nhưng chỉ **7** ghép chắc (`immediates`), **243** ghép theo thứ tự blob *"chưa xác thực bằng token"* | **Không** (chỉ cần biết có bao nhiêu màn) |
| 3 | **E2/E3 — hit flash / hit stop** | mở, "chi phí thấp" | 🔴 **vẫn mở, và nay biết là KHÔNG nằm ở `Enemy_Display`** — class đó chỉ có **5 field**: `hpProgressBarRenderer` · `size` · `hitableRenderers` · `appearOff` · `dieOff` | **Có** — xem §4 |
| 4 | **D3 — thứ tự pha boss** | mở, "cần decoder" | ✅ **ĐÓNG** — `event-receivers.json.gz`: **795/795 event use có `time`** | **Không** |
| 5 | **B1 — HP enemy runtime** | mở | 🔴 mở — có hằng số, chưa có thứ tự nhân | **Không** (L1 tự chọn số) |
| 6 | **C4 — vàng/giờ** | mở | 🟡 tính được, **chưa làm** | **Không** |
| 7 | **A7 — mật độ địch** | mở, "làm bằng script" | 🟡 tính được **một nửa** — nhưng vướng #9 (xem dưới) | **Không** |
| 8 | **A5 — độ dài phiên** | mở, "chi phí cao" | 🔴 mở — cần A6 + luật continue | **Không** (tự chọn) |
| 9 | **B3 — đường cong damage** | mở, "chi phí cao" | 🔴 mở | **Không** (tự chọn) |

**Đóng thêm được 1 câu (D3)** so với lần đánh giá trước — không cần decoder nữa, vì nhánh dữ liệu
đã join event với Animator và giữ nguyên `time`.

---

## 3. Một con số sai — sửa luôn

`DESIGN_QUESTIONS.md` ghi **`rate = 0` ở 2.373 spawner**. Đếm lại trên `datas/waves.json`:

```
11.095 spawner · rate = 0 : 2.371 · rate thiếu: 0
phân bố: 1,0 → 7.741 · 0,0 → 2.371 · 0,5 → 532 · 2,0 → 163 · 0,65 → 111 · 6,0 → 58
```

**2.371**, không phải 2.373. Lệch 2, nhưng cùng loại lỗi đã năm lần trong repo này: một con số
không kèm phép đếm. Nay `I3` khoá lại.

Câu hỏi thật vẫn mở và **nó chặn A7**: `rate = 0` nghĩa là **spawn tức thời** hay **mỗi khung
hình**? 2.371/11.095 spawner (21 %) rơi vào trường hợp này, nên mọi phép "địch/giây" đều có sai số
21 % cho tới khi phân xử.

---

## 4. Chỗ **thật sự** sẽ làm đau khi thiết kế — không phải mấy con số trên

Ba blocker còn lại (#3, #5, #9) đều **không chặn L1**, vì L1 cho phép tự chọn số. Nhưng có hai thứ
mà *tự chọn* cũng không cứu được, vì chúng là **cảm giác**, không phải tham số:

### 4.1 Feel — hit flash / hit stop (câu #3)

Đây là thứ người chơi nhận ra ngay, và là thứ **duy nhất trong danh sách mà dữ liệu hiện tại
không có**. Nay biết thêm một điều hữu ích: nó **không** cấu hình trong `Enemy_Display` (5 field,
không có gì liên quan flash/stop). Nghĩa là nó nằm ở **shader / material / code**, không ở prefab.

⇒ Hệ quả cho thiết kế: **đừng chờ dữ liệu**. Tự định nghĩa feel rồi làm prototype 30 giây để cảm
nhận. Đây là chỗ duy nhất nên **bỏ qua** bản gốc và tự quyết ngay từ đầu.

### 4.2 Animation — 0/791 keyframe, và **chưa đo runtime lần nào**

`ANIMATION.md`: biết **tên** 791 clip, **0 %** curve. `ANIMATION_GAPS.md` §2e: endpoint `GET /anim`
đã viết và CI xanh, nhưng **chưa chạy trên máy thật lần nào**.

⇒ Với L1, cái này **không chặn**: tự làm animation theo nhịp mình muốn. Nhưng nếu định "clone y
chuyển động" thì đây là bức tường — và nó chỉ hạ xuống được bằng **một lần cắm điện thoại**, không
phải bằng đọc thêm tài liệu.

---

## 5. Bảng sẵn sàng theo hệ

| Hệ | Đủ để thiết kế? | Cơ sở |
|---|---|---|
| **Vòng lặp / wave / spawn** | ✅ **A** | 109 prefab roster · 282 wave · 11.095 spawner · 22.461 lượt spawn (`waves.json`) |
| **Độ khó / chế độ** | ✅ **A** | `MaxModeIndex = 4` · `levelDelta [1, 2, 3.6, 3.6]` · 3 chế độ mỗi stage |
| **Kinh tế / sao / HP** | ✅ **A** cho hằng số | `StartHp 2500` · `stepCommon 0,18` · `DeltaStarCost 50` · `PercentToCompleteMissions222 [0.2,0.6,0.98]` |
| **Boss** | ✅ **A** cho cấu trúc | 46 boss · 39 prefab `Boss-*` · 3 prefab Spine · 92 `Animator`/36 prefab · 795 event có mốc thời gian |
| **Enemy** | ✅ **A** cho cơ chế | di chuyển procedural theo path 100 % · `Enemy_Appear` = vỏ delegate · `Enemy_Display` 5 field |
| **Animation — *script*** | ✅ **A** cho boss, **B** cho enemy | **33 prefab boss · 793 event có mốc thời gian** · nhịp đòn **0,17/0,33/1,0/5,0 s** · `Boss1_Director` gọi `SetAnimation` · enemy = máy trạng thái 3 nhánh + hit flash 0,05 s — xem **`ANIMATION_SCRIPT.md`** |
| **Animation — *playback / feel*** | 🔴 **D** | 0/791 keyframe · 0 phép đo playback runtime · hành vi 12 handler + tên entry/clip **chưa có** (mức **C**) |
| **UI** | 🟡 chưa đánh giá | 53k file dump có trong nhánh dữ liệu nhưng **chưa kéo về**, chưa phân tích |

---

## 6. Kết luận

**Thiết kế được, ngay bây giờ, cho L1.** Không có blocker nào ở nhóm "cơ chế" còn mở: vòng lặp,
wave, spawn, độ khó, kinh tế, boss, enemy đều **mức A**.

Ba việc nên làm **trước khi** vẽ bảng thiết kế chi tiết, xếp theo giá trị:

| | Việc | Vì sao trước |
|---:|---|---|
| 1 | **Prototype feel 30 giây** (hit flash, hit stop, rung, âm) | thứ duy nhất dữ liệu không có, và nó quyết định cảm giác |
| 2 | **Chốt `rate = 0`** — spawn tức thời hay mỗi frame | 21 % spawner bị ảnh hưởng ⇒ mật độ địch, hiệu năng, độ khó |
| 3 | **A6 stage ↔ wave** | quyết định **số màn**; hiện chỉ 7/250 map chắc chắn |

Và **một việc không nên làm**: đừng chờ dữ liệu animation. Nó chỉ hạ bằng một lần cắm máy, và L1
không cần nó.
