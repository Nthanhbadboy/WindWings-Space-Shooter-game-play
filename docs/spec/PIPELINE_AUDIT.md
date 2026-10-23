# PIPELINE_AUDIT — nhánh phân tích ngược (`ef6b75ef`) đi đúng hướng không

> Đánh giá **nhánh dữ liệu**, không đánh giá con người. Mọi kết luận dưới đây tính từ
> `git log` + file trong `c52d04e`. Không có chỗ nào là cảm nhận.
>
> Ngày đo: 2026-10-23 00:13 (commit cuối của nhánh dữ liệu).

## 0. Trả lời ngắn

**Đúng hướng 3/4 tuyến — nhưng đang lạc ở tuyến thứ 4, và mù với lỗ hổng lớn nhất.**

| Tuyến | Kết quả | Đánh giá |
|---|---|---|
| Audio · asset · wave | 69/69 WAV · 2.197 asset · wave resolve 100% | ✅ **tốt** |
| Raw typetree (`Enemy_Controller` hub) | 45 class · 24.706 dòng | ✅ **rất tốt** |
| UI layout | 114 màn · 52.936 node · 3.539 file | ✅ **tốt** |
| Spine timeline | 27 rig · 12.274 keyframe | ✅ **tốt** |
| IL2CPP constants | 98 dòng, **60 dòng là rác** | ❌ **lạc** |
| **Lớp hành vi enemy/boss** | **0 trong 4h39** | ⚠ **bỏ quên** |

## 1. Nhịp độ thật — không chậm

| Chỉ số | Số |
|---|---:|
| Tổng commit trên nhánh | **78** |
| Trong đó commit báo cáo tự động (`chore(re) [skip ci]`) | **36 (46%)** |
| **Commit làm việc thật** | **42** |
| Khung thời gian làm việc | **19:34 → 00:13 = 4h39** |
| Nhịp | **≈ 9 commit thật/giờ** |

⇒ "Phân tích lâu" là **cảm giác do 46% commit là rác tự sinh**, không phải do chậm.
Nhìn 78 commit tưởng nhiều; thực chất **42**.

## 2. Đã đóng góp gì cho spec này

6 lần dữ liệu của họ **trực tiếp đổi số** trong `docs/spec/`:

| Commit | Đổi gì trong spec |
|---|---|
| `820f9ad` | bỏ cap `Enemy_Datas` → **800 → 981** dòng |
| `aacc099` | audio **0 → 69/69 WAV** (bác bỏ kết luận "phải vgmstream" của tôi) |
| `20:11` | wave resolve tên prefab + dedupe `copies` → **23.757 khớp `Call_Data`, lệch 0** |
| `61d5385` | raw typetree → **`Enemy_Controller` hub, ghép 981/981 = 100%** |
| `070de92` | **Spine timeline 12.274 keyframe** — lấp lớp animation |
| `ef1a14f` | sửa atlas page → số region đúng |

Đây là **giá trị thật**, không phải hoạt động hình thức.

## 3. Chỗ đang lạc — IL2CPP constants

40 phút cuối (23:33 → 00:13) dồn **4/4 commit** vào tuyến này. Kết quả hiện tại:

**98 dòng "hằng số", trong đó 60 dòng cùng một giá trị `288733`.**

| Method | Đọc ra |
|---|---|
| `ArenaManager.BackUpDatas` | 288733 |
| `GameDatas.IsProVersion` | 288733 |
| `IAP_Manager.BuyProductConsumable` | 288733 |
| `Device_Get_Data.GetStringRank` | 288733 |
| `Droid_Data_Balance.GetBaseDamage` | 288733 |
| … 55 dòng nữa | 288733 |

60 method **không liên quan** trả cùng một số ⇒ đây là **đọc nhầm một ô literal pool dùng chung**,
không phải hằng số thiết kế. Bằng chứng nội tại: commit cuối `c52d04e` **tự viết**
*"metadata ptr tables gave junk"* — tức chính họ đã phát hiện.

Phần **float thì có vẻ thật** (30 giá trị phân biệt: `0.1` · `1.1` · `0.2` · `0.01` · `2.3` · `0.56` …),
nhưng **chưa biết nhân vào đâu** — `conclusions.md` của họ cũng ghi đúng như vậy.

> **Nhận định (mức A):** tuyến này đang **đốt thời gian vào lớp đắt nhất** (method body = **0,44%**
> độ phủ, xem `DATA_SYNC.md` §7.12) trong khi **5 việc rẻ hơn nhiều vẫn chưa làm**.

## 4. Lỗ hổng lớn nhất — và nó **không có trong danh sách của họ**

`docs/conclusions.md` mục *"Những gì chưa bóc được"* liệt kê 7 dòng: IL2CPP constants · công thức ·
ý nghĩa hằng số · layout runtime · particle · PvP server · spine timeScale.

**Không có dòng nào** cho lớp hành vi enemy/boss — trong khi `class-inventory` đếm được:

| Class | Instance | Trong `TARGETS`? |
|---|---:|---|
| **`Enemy_Physics`** | **981** | ❌ |
| `Enemy_Destroy` | 971 | ❌ |
| `Enemy_Burned` | 695 | ❌ |
| `Enemy_Stun` | 140 | ❌ |
| `Enemy_LookAtPlayer` | 391 | ❌ |
| 37 `*_Director` + 3 `AttackPhases` | 68 | ❌ |
| `Call_Point` | **23.757** | ❌ |
| `Transform` | 228.432 object | ❌ |
| `AnimationClip` · `AnimatorController` | 791 · 308 | ❌ |

`TARGETS` trong `unity_data.py` vẫn **45 class**, **không thêm một tên nào** kể từ `61d5385`.

> **Nhận định (mức A):** đây là chỗ đánh giá **sai hướng rõ nhất** — không phải làm sai,
> mà **xếp sai thứ tự**. `Enemy_Physics` là lớp kịch bản chiếm **85,8% entry** mà spec còn trống,
> và PathID của nó **đã nằm sẵn trong `Enemy_Controller.physicsScript`** (`DATA_SYNC.md` §7.7).
> Thêm **1 dòng** vào `TARGETS` là mở.

## 5. Chi phí / lợi ích của 5 việc còn lại

| # | Việc | Chi phí | Mở ra | Nên làm |
|---:|---|---|---|---|
| 1 | Thêm **5 tên** `Enemy_*` vào `TARGETS` | **1 dòng** | 2.787 instance · enemy/boss **58,9% → 100%** · lớp kịch bản #4 **0% → 100%** | **ngay** |
| 2 | Thêm **37 `*_Director` + 3 `AttackPhases`** | 1 dòng | 68 instance · **5 boss 0% đòn → 100%** | **ngay** |
| 3 | Thêm **`Call_Point`** | 1 dòng | **23.757** — có thể chứa phần `Call_Data` bị cap | **ngay** |
| 4 | Export **`Transform`** (`m_Father`) | type mới, 228.432 object | **31,9% object** · mở **5 mắt ghép** (§7.9) | sau #1–3 |
| 5 | Export **`AnimationClip` + `AnimatorController`** | cần reader riêng | 1.099 object · đòn boss còn lại | cuối |
| — | IL2CPP method body | đắt nhất, 0,44% | ý nghĩa hằng số | **dừng lại** |

Ba việc đầu **tổng cộng 3 dòng code**. Chúng mở nhiều hơn 40 phút vừa rồi.

## 6. Cái họ làm **tốt hơn** tôi

Nói công bằng, hai điểm:

1. **`raw/typetrees`** — tôi đọc CSV trong 3 vòng và **không phát hiện CSV làm phẳng list**
   (`PathCreator.points` = `[10]`). Họ xuất raw và nó lưu đủ toạ độ. Cách làm của họ **đúng hơn**.
2. **Spine timeline** — tôi chỉ đếm được số animation; họ xuất **12.274 keyframe** với `t`/`x`/`curve`.
   Đây là bước biến "biết nhịp" thành "dựng lại được".

## 7. Kết luận

| Câu hỏi | Đáp |
|---|---|
| Có đi đúng hướng? | **Phần lớn đúng** — 5/6 tuyến cho dữ liệu thật |
| Có chậm không? | **Không** — 42 commit thật / 4h39 |
| Vì sao thấy lâu? | **46% commit là báo cáo tự sinh** + 40 phút cuối dậm chân |
| Sai ở đâu? | **Thứ tự ưu tiên**: đi vào method body (0,44%) khi 3 dòng cấu hình mở được 100% lớp hành vi |
| Thiếu gì lớn nhất? | **`Enemy_Physics` 981** — PathID đã có, chưa export |
| Cần gì để sửa? | Không cần thêm suy luận — cần **3 dòng `TARGETS`** |

> **Điều kiện lật ngược:** nếu `Enemy_Physics` export ra mà phần lớn field rỗng (như
> `Spawner.dataScript` = 0), thì lớp này **không cứu được** và thứ tự ưu tiên của họ mới đúng.
> Chưa biết trước — nhưng chi phí thử là **1 dòng**, nên không có lý do để không thử.

## 8. Còn thiếu / phải đoán

| # | Thứ | Mức |
|---:|---|---|
| 1 | 5 class `Enemy_*` có field thật hay rỗng như `Spawner.dataScript` | **C** |
| 2 | `Call_Point` có phải bản đầy đủ của `Call_Data` | **C** |
| 3 | 60 dòng `288733` — ô literal pool nào bị đọc nhầm | **B** |
| 4 | Nhánh dữ liệu có tiếp tục sau `c52d04e` không | **C** |
